import json
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_extraction_chain
from langchain.schema import SystemMessage, HumanMessage
from langchain.chat_models import ChatOpenAI
import requests
import re

from utils import *


INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD')
WHOISJSONAPI= os.environ.get('WHOISJSONAPI')
data_folder = f"data/{INDUSTRY_KEYWORD}"
companies_file = "1companies.json"

targetField="priceAndPlans"

def load_data_without(filename):
    return {domain: info for domain, info in load_from_json_file(filename,data_folder).items()}


def finde_link_toplans(links):
    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    messages = [
        SystemMessage(content="Find the link to page with prices and plans. Return only url starts with 'https://' or 'Not found'"),
        HumanMessage(content=''.join(links))
    ]

    try:
        response = chat(messages)
        return response.content
        

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Define paths and filenames
    
    
    
    # Load data
    data = load_data_without(companies_file)
    print(len(data))
    # Iterate through the data dictionary
    for domain, domain_data in data.items():
        
        data = load_from_json_file(domain+".json",data_folder)
        print("\n\n"+domain)
        if ("links" not in data): 
            print("no links in file "+data_folder+"/"+domain+".json")
            continue
        if ("{targetField}" in data):
            print("prices crawled. skip ")
            continue

        print("searching link to prices")
        plans_url = finde_link_toplans(data['links'])
        
        if "Not found" in plans_url:
            data[targetField] = 'Not found'
        elif "https://" in plans_url:
            print ("Crawl "+plans_url)
            plans_url=correct_url(plans_url)
            summary = extract_content(plans_url)

        data[targetField] = summary['text_content']
        save_to_json_file(data, domain+".json",data_folder)
        

if __name__ == "__main__":
    main()
    print("next:  5")