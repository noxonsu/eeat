import json
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_extraction_chain
from langchain.schema import SystemMessage, HumanMessage
from langchain.chat_models import ChatOpenAI
from bs4 import BeautifulSoup
import re

from utils import *


INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD')
data_folder = f"data/{INDUSTRY_KEYWORD}"

def load_data_without_prices(filename):
    return {domain: info for domain, info in load_from_json_file(filename,data_folder).items() if "prices" not in info}

def load_products(filename):
    return load_from_json_file(filename)

def extract_content(site):
    loader = AsyncChromiumLoader([site])
    docs = loader.load()
    html2text = Html2TextTransformer({'ignore_links': False})
    text_content = html2text.transform_documents(docs)
    if not text_content:
        return f"Failed to extract content for site {site}"
    return text_content[0].page_content

def is_product_or_list(summary, company_products):
    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    messages = [
        SystemMessage(content="Given a text input, identify the products, services, or solutions of companies mentioned in the text. If the products or services is associated with the one company, provide the output as 'All products/services mentioned belong to the one company [Company_name]'. IF there a list of products services or projects are from different companies in the text say 'Yes, this list of products belongs to different companies.'. If input looks like invalid or DDOS protection screen return 'Invalid'"),
        HumanMessage(content=summary)
    ]

    try:
        response = chat(messages)
        gpt_response = response.content

        if "belongs to different companies" in gpt_response or "belong to the respective companies" in gpt_response:
            response2 = chat(messages = [
                SystemMessage(content="Extract the company-product pairs in the format 'Company_name: product_name' each project at new line and provide output as 'List of projects:'. Exclude any duplicates or redundancies. Remove special characters from company's name like '-' and spaces"),
                HumanMessage(content=gpt_response+summary)
            ])
            gpt_response = response2.content
        else:
            response2 = chat(messages = [
                SystemMessage(content="is this list of products of the one company and which name of this company? "),
                HumanMessage(content=gpt_response)
            ])

            if "Yes" in response2.content:
                gpt_response = response2.content
        
        # Check if it's a list of products
        if "nvalid" in gpt_response:
            return "invalid", []
        elif "List of projects" in gpt_response:
            # Extract company-product pairs from the response
            product_lines = gpt_response.split("\n")

            for line in product_lines:
                parts = line.strip().split(":")
                if len(parts) >= 2:
                    company_name, product_name = parts[0], parts[1]
                    company_products.append(f"{company_name}: {product_name}")

            return "list of projects", company_products
        else:
            return "single project", []

    except Exception as e:
        print(f"An error occurred: {e}")
        return "unknown", []

def main():
    # Define paths and filenames
    
    companies_file = "companies.json"
    products_file = "products.json"
    companies_names_file = "companies_names.json"
    
    # Load data
    data = load_data_without_nature("companies.json")
    company_products = set(load_from_json_file(products_file,data_folder))
    companies = set(load_from_json_file(companies_names_file,data_folder))

    # Iterate through the data dictionary
    for domain, domain_data in data.items():
        url = domain_data["url"]
        summary = extract_content(url)

        nature, extracted_links = is_product_or_list(summary, list(company_products))
        data[domain]["nature"] = nature

        if nature == "list of projects":
            print("list of companies to be saved")
            # Check if the company already exists
            for company_product in extracted_links:
                company_product = re.sub(r'^\d+\.\s*', '', company_product)
                company_name = company_product.split(":")[0].strip()
                company_name = re.sub(r'^\d+\.\s*', '', company_name)

                if company_name not in companies:
                    companies.add(company_name)
                    company_products.add(company_product)
        elif nature == "single project":
            # Save the site's summary to an individual JSON file in the 'data/' directory

            save_to_json_file({'summary': summary}, f"{domain}.json", data_folder)
            # Add the domain (which presumably is the company name) to the companies set
            companies.add(domain)

        save_to_json_file(data, companies_file,data_folder)
        if company_products is not None: save_to_json_file(list(company_products), products_file, data_folder)
        save_to_json_file(list(companies), companies_names_file, data_folder)

if __name__ == "__main__":
    main()