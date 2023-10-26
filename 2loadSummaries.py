import json
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_extraction_chain
from langchain.schema import SystemMessage, HumanMessage
import os
from langchain.chat_models import ChatOpenAI
from bs4 import BeautifulSoup
import re


def load_data_without_nature(filename):
    with open(filename, "r") as f:
        all_data = json.load(f)
    # Filter out items that already have a "nature" field
    return {domain: info for domain, info in all_data.items() if "nature" not in info}

def load_products(filename):
    with open(filename, "r") as f:
        all_data = json.load(f)
    # Filter out items that already have a "nature" field
    return all_data

def extract_content(site):
    loader = AsyncChromiumLoader([site])
    docs = loader.load()
    html2text = Html2TextTransformer({'ignore_links': False})
    text_content = html2text.transform_documents(docs)
    if not text_content:
        return f"Failed to extract content for site {site}"
    return text_content[0].page_content


def is_product_or_list(summary,company_products):
    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    messages = [
        SystemMessage(content="Given a text input, identify the products, services, or solutions of companies mentioned in the text. If the products or services is associated with the one company, provide the output as 'All products/services mentioned belong to [Company_name]'. IF there a list of products services or projects are from different companies in the text say 'Yes, this list of products belongs to different companies.'"),
        HumanMessage(content=summary)
    ]

    try:
        response = chat(messages)
        gpt_response = response.content

        if "belongs to different companies" in gpt_response:
            response2 = chat(messages = [
                SystemMessage(content="Extract the company-product pairs in the format 'Company_name: product_name' each project at new line with number and provide output as 'List of projects:'. Exclude any duplicates or redundancies. Exclude projects which not in category 'KYC API SaaS'"),
                HumanMessage(content=gpt_response)
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
        if "invalid" in gpt_response:
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
    # Load data
    data = load_data_without_nature("data.json")

    # Initialize company_products as an empty set and companies as an empty set
    company_products = set()
    companies = set()

    try:
        # Load company_products from "products.json" if it exists
        with open("products.json", "r") as f:
            company_products = set(json.load(f))
    except FileNotFoundError:
        pass

    try:
        # Load companies from "companies.json" if it exists
        with open("companies.json", "r") as f:
            companies = set(json.load(f))
    except FileNotFoundError:
        pass

    # Iterate through the data dictionary
    for domain, domain_data in data.items():
        url = domain_data["url"]
        summary = extract_content(url)

        nature, extracted_links = is_product_or_list(summary, list(company_products))

        # Save the nature into the data dictionary for that domain
        data[domain]["nature"] = nature

        if nature == "list of projects":
            print("list of companies saved")
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
            file_path = os.path.join("data", f"{domain}.json")
            with open(file_path, "w") as file:
                json.dump({'summary': summary}, file, indent=4)
            # Add the domain (which presumably is the company name) to the companies set
            companies.add(domain)


        # Load the current content of data.json
        with open("data.json", "r") as f:
            current_data = json.load(f)

        # Update the current_data with new information
        current_data[domain] = data[domain]

        # Save the updated data back to data.json
        with open("data.json", "w") as f:
            json.dump(current_data, f, indent=4)


        # Load the current content of products.json
        with open("products.json", "r") as f:
            current_products = set(json.load(f))

        # Update the current_products with new products
        current_products.update(company_products)

        # Save the updated products back to products.json
        with open("products.json", "w") as f:
            json.dump(list(current_products), f, indent=4)


        # Load the current content of companies.json
        with open("companies.json", "r") as f:
            current_companies = set(json.load(f))

        # Update the current_companies with new companies
        current_companies.update(companies)

        # Save the updated companies back to companies.json
        with open("companies.json", "w") as f:
            json.dump(list(current_companies), f, indent=4)


if __name__ == "__main__":
    main()