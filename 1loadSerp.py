import os
import re
import json

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from utils import *

SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD')
KEYWORD_FOR_SERP = os.environ.get('KEYWORD_FOR_SERP')


if not SERPAPI_KEY:
    print("Please set the SERPAPI_KEY environment variable.")
    exit()

def extract_company_urls_from_serp(serp_content, industry_query):
    
    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    messages = [
        SystemMessage(content="Analyse SERP and Identify sites based on a given Google search query. '"+industry_query+"'. Return only list of urls if found. Return only urls without quotes etc."),
        HumanMessage(content=f" {serp_content} \n\n The urls list: ")
    ]

    try:
        response = chat(messages)
        gpttitle = response.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Not found"

    # Remove the quotation marks from the start and end of the generated title
    if gpttitle[0] == '"':
        gpttitle = gpttitle[1:]
    if gpttitle[-1] == '"':
        gpttitle = gpttitle[:-1]
    
    return gpttitle



def main():
    industry_query = INDUSTRY_KEYWORD
    
    organic_results = search_companies_on_google(KEYWORD_FOR_SERP,40)
    print(organic_results)
    
    # Setting the folder based on the industry keyword
   
    
    serp_content = ""
    for result in organic_results:
        if "snippet" not in result:
            result["snippet"] = ""
        serp_content += (str(result["position"]) + ". " + result["link"] + " " + result["title"] + " " + result["snippet"])
            
    company_urls = extract_company_urls_from_serp(serp_content, industry_query)

    # Assuming the returned URLs are separated by commas or spaces
    url_list = re.split(r'[,\s]+', company_urls)

    company_domains = {}
    for url in url_list:
        domain = extract_domain_from_url(url)
        if domain:  # Ensuring domain is not empty
            company_domains[domain] = {'url': url}
    directory_name = os.path.join('data', INDUSTRY_KEYWORD)
    save_to_json_file(company_domains, '1companies.json', directory_name)
    print(f"Company data saved to {directory_name}/1companies.json")

if __name__ == '__main__':
    main()