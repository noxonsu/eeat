import json


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_extraction_chain
from langchain.schema import SystemMessage, HumanMessage
from langchain.chat_models import ChatOpenAI

import re

from utils import *


INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD')

data_folder = f"data/{INDUSTRY_KEYWORD}"
companies_file = "1companies.json"
products_file = "2products.json"
companies_names_file = "companies_names.json"

def load_data_without_nature(filename):
    return {domain: info for domain, info in load_from_json_file(filename,data_folder).items() if ("nature" not in info or "DDOS" in info['nature'])}

def load_products(filename):
    return load_from_json_file(filename)



def is_product_or_list(summary, company_products):
    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    messages = [
        SystemMessage(content="Given a text input, identify the products, services, or solutions of companies mentioned in the text. If the products or services is associated with the one company, provide the output as 'All products/services mentioned belong to the one company [Company_name]'. If there a list of products services or projects are from different companies (or it's a 'TOP') in the text say 'Yes, this list of products belongs to different companies.'. If input looks like invalid or DDOS protection screen or explain article/blog return 'Invalid:[reason]'"),
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
            return gpt_response, []
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
    
    
    
    # Load data
    data = load_data_without_nature(companies_file)
    total = len(data)
    company_products = set(load_from_json_file(products_file,data_folder))
    companies = set(load_from_json_file(companies_names_file,data_folder))

    # Iterate through the data dictionary
    i=0
    for domain, domain_data in data.items():
        i=i+1
        url = domain_data["url"]
        print(i/total*100)
        print ("\n\nHarvest "+domain)
        summary = extract_content(url)
        print ("Analyse "+domain)

        # save to tmp.html
        with open("tmp.html", "w") as f:
           f.write(summary['text_content'])
            
        nature, extracted_links = is_product_or_list(summary['text_content'], list(company_products))
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
            # To use:
            internal_links = extract_links_with_text_from_html(summary['html_content'],url)

            save_to_json_file({'summary': summary['text_content'],'links':internal_links}, f"{domain}.json", data_folder)
            # Add the domain (which presumably is the company name) to the companies set
            companies.add(domain)
            

        print(nature)
        save_to_json_file(data, companies_file,data_folder)
        if company_products is not None: save_to_json_file(list(company_products), products_file, data_folder)
        save_to_json_file(list(companies), companies_names_file, data_folder)

if __name__ == "__main__":
    main()
    print("next: 4searchProducts.py ")