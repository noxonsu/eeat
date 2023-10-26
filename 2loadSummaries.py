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


def is_product_or_list(summary):
    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k-0613")
    messages = [
        SystemMessage(content="Determine if the given summary describes a few products of one company or a few products from different companies. If it's a list of products from different companies, extract Names mentioned in the summary in format 'Company_name: product_name' or just 'product_name'. Return a 'list of products: 1.' with number near each product and with the company name near every product's name. In case This summary does not describe a single product or a list of products from different companies return 'Invalid'"),
        HumanMessage(content=summary)
    ]

    try:
        response = chat(messages)
        gpt_response = response.content

        # Check if it's a list of products
        if "nvalid" in gpt_response:
            return "invalid", []
        elif "List of products" in gpt_response:
            # Extract company-product pairs from the response
            product_lines = gpt_response.split("\n")
            company_products = load_products("products.json")

            for line in product_lines:
                if line.strip().startswith(str(len(company_products) + 1) + ". "):
                    # Extract the company and product name from each line
                    parts = line.strip().split(":")
                    if len(parts) >= 2:
                        company_name, product_name = parts[0], parts[1]
                        company_products.append(f"{company_name}: {product_name}")

            return "list of products", company_products
        else:
            return "single product", []

    except Exception as e:
        print(f"An error occurred: {e}")
        return "unknown", []


def extract_links_from_summary(summary):
    soup = BeautifulSoup(summary, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    return links


def main():
    # Load data
    data = load_data_without_nature("data.json")

    # Initialize company_products as an empty list
    company_products = []

    try:
        # Load company_products from "products.json" if it exists
        with open("products.json", "r") as f:
            company_products = json.load(f)
    except FileNotFoundError:
        pass

    # Iterate through the data dictionary
    for domain, domain_data in data.items():
        url = domain_data["url"]
        summary = extract_content(url)

        nature, extracted_links = is_product_or_list(summary)

        # Save the nature into the data dictionary for that domain
        data[domain]["nature"] = nature

        if nature == "list of products":
            print("list of companies saved")
            # Append the new company products to the existing list
            company_products.extend(extracted_links)
        elif nature == "single product":
            # Save the site's summary to an individual JSON file in the 'data/' directory
            file_path = os.path.join("data", f"{domain}.json")
            with open(file_path, "w") as file:
                json.dump({'summary': summary}, file, indent=4)

        # Save modified data.json file after processing all items
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)

        # Save the updated company_products back to "products.json"
        with open("products.json", "w") as f:
            json.dump(company_products, f, indent=4)

if __name__ == "__main__":
    main()