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

COMPAREPRICES= os.environ.get('COMPAREPRICES')
SERP_PRICES_EXT = os.environ.get('SERP_PRICES_EXT')

#SERP_PRICES_EXT Check if this exists or exit with debug message
if SERP_PRICES_EXT is None:
    print("SERP_PRICES_EXT is not defined. Please define it in .env file if you want to use this script")
    exit()
    

data_folder = f"data/{INDUSTRY_KEYWORD}"


def load_data_without(filename):
    return {domain: info for domain, info in load_from_json_file(filename,data_folder).items()}


def finde_link_toplans(serp):


    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    messages = [
        SystemMessage(content="Find the link to page with prices and plans. Return JSON with link and cached_page_link. Or 'Not found' if not found"),
        HumanMessage(content=serp)
    ]

    try:
        response = chat(messages)
        return response.content
        

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Define paths and filenames
    
    
    
    # Load data

    data = load_from_json_file("1companies.json","data/"+INDUSTRY_KEYWORD)
    #filter only data with nature=single project
    data = {k:v for k,v in data.items() if v['nature']=='single project' and 'priceAndPlansCrawled' not in v}


    print(len(data))
    # Iterate through the data dictionary
    for domain, domain_data in data.items():
         
        print("\n\n"+domain)
        q="site:"+domain+' '+SERP_PRICES_EXT
        organic_results = search_companies_on_google(q, 10)
        
        serp_content = ""
        for result in organic_results:
            if "snippet" not in result:
                result["snippet"] = ""
            if "cached_page_link" not in result:
                result["cached_page_link"] = ""    
            serp_content += (str(result["position"]) + ". link: " +  result["link"]+ " , text: " + result["title"] + ", cached_page_link " +result['cached_page_link']+" , snipptet: "+ result["snippet"])
        
        if (len(organic_results) == 1):
            plans_url = organic_results[0]['link']
            plans_url_cached = organic_results[0]['cached_page_link']
        elif (len(organic_results) > 1):
            #ask gpt
            plans_url_json = finde_link_toplans(serp_content)
            if plans_url_json != 'Not found':
                plans_url = json.loads(plans_url_json)['link']
                plans_url_cached = json.loads(plans_url_json)['cached_page_link']
            else:
                plans_url = 'Not found'
                plans_url_cached = 'Not found'
        else:
            plans_url = 'Not found'
        
        
        if plans_url != 'Not found':
            
            plans_url=correct_url(plans_url)
            data[domain]["priceAndPlansCrawled"] = plans_url
            data[domain]["priceAndPlansCached"] = plans_url_cached
            print ("Crawl "+plans_url)
            summary = extract_content(plans_url)
            details = load_from_json_file(domain+".json",data_folder)
            details["priceAndPlans"] = summary['text_content']
            save_to_json_file(details, domain+".json",data_folder)
        else:
            data[domain]["priceAndPlansCrawled"] = plans_url
        save_to_json_file(data, "1companies.json",data_folder)

        
        
        

if __name__ == "__main__":
    main()
    print("next:  5")