#data from 1companies.json 
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


# Configuration and Initialization
INDUSTRY_KEYWORD = os.getenv('INDUSTRY_KEYWORD')
WHOISJSONAPI = os.getenv('WHOISJSONAPI')
COMPAREPRICES = os.getenv('COMPAREPRICES')
SERP_PRICES_EXT = os.getenv('SERP_PRICES_EXT') or exit("SERP_PRICES_EXT is not defined. Please define it in .env file if you want to use this script.")
DATA_FOLDER = f"data/{INDUSTRY_KEYWORD}"


def find_link_to_plans(serp_content,domain_data):
    """ Use GPT to find the link to the plans page from SERP content. """
    from langchain.chat_models import ChatOpenAI

    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    messages = [
        SystemMessage(content="Find the link to the page with prices and plans for "+INDUSTRY_KEYWORD+" (not sms). Return JSON with link and cached_page_link, or return 'Not found' if not found."),
        HumanMessage(content=serp_content)
    ]
    print(serp_content)
    try:
        response = chat(messages)
        return response.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Not found'


def process_domain_data(domain, domain_data):
    """ Process the data for a single domain. """
    query = f"site:{domain} {SERP_PRICES_EXT}"
    
    organic_results = search_companies_on_google(query, 10)
    serp_content = "".join([
        f"{result.get('position', 'N/A')}. link: {result.get('link', '')}, "
        f"text: {result.get('title', '')}, cached_page_link: {result.get('cached_page_link', '')}, "
        f"snippet: {result.get('snippet', '')}"
        for result in organic_results
    ])

    # Determine the plans URL based on the number of search results
    plans_url, plans_url_cached = ('Not found', 'Not found')
    if organic_results:
        plans_url = organic_results[0]['link']
        if ('cached_page_link' in organic_results[0]):
            plans_url_cached = organic_results[0]['cached_page_link']
        else:
            plans_url_cached = 'Not found'
        if len(organic_results) > 1:
            details = load_from_json_file(f"{domain}.json", DATA_FOLDER)
            plans_url_json = find_link_to_plans(details['links'],domain_data)
            if 'ot found' not in plans_url_json and "I'm sorry" not in plans_url_json:
                plans_url_info = json.loads(plans_url_json)
                plans_url = plans_url_info['link']
                plans_url_cached = plans_url_info['cached_page_link']

    return plans_url, plans_url_cached


def main():
    # Load data
    data = load_from_json_file("1companies.json", DATA_FOLDER)
    # Filter only data with nature=single project and not yet crawled
    data = {k: v for k, v in data.items() if v['nature'] == 'single project' and 'priceAndPlansCrawled' not in v}

    print(len(data), "domains to process.")

    for domain, domain_data in data.items():
        print(f"\n\nProcessing prices {domain}...")
        plans_url, plans_url_cached = process_domain_data(domain, domain_data)

        # Handle found plans URL
        if plans_url != 'Not found':
            plans_url = correct_url(plans_url)
            domain_data["priceAndPlansCrawled"] = plans_url
            domain_data["priceAndPlansCached"] = plans_url_cached
            print(f"Crawling {plans_url}...")
            summary = extract_content(plans_url)
            details = load_from_json_file(f"{domain}.json", DATA_FOLDER)
            details["priceAndPlans"] = summary['text_content']
            save_to_json_file(details, f"{domain}.json", DATA_FOLDER)
        else:
            domain_data["priceAndPlansCrawled"] = plans_url

        save_to_json_file(data, "1companies.json", DATA_FOLDER)

    print("Processing complete. Next step: 5")


if __name__ == "__main__":
    main()