import os
import re
import json
from serpapi import GoogleSearch
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from urllib.parse import urlparse

from utils import *

SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD')
data_folder = f"data/{INDUSTRY_KEYWORD}"

if not SERPAPI_KEY:
    print("Please set the SERPAPI_KEY environment variable.")
    exit()

def findOfficialDomain(serp, project_name):
    
    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0613")
    messages = [
        SystemMessage(content="Analyse SERP and find the official domain URL of the project named '"+project_name+"'. Return only one URL if found starts with https://. Return only URL without quotes etc."),
        HumanMessage(content=f" {serp} \n\n The official domain is: ")
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

def search_google(nameOfProject):
    params = {
        "engine": "google",
        "q": nameOfProject,
        'gl': 'us',
        'hl': 'en',
        'num': 20,
        "api_key": SERPAPI_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    # Error handling for missing key
    if "organic_results" in results:
        return results["organic_results"]
    else:
        print("Error: 'organic_results' not found in the results!")
        print(results)  # This will print the structure of results to inspect it
        return []

def extract_domain_from_url(url):
    """Extract the domain from a given URL."""
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return domain



def is_valid_domain(domain):
    # A simple regex to validate domain names
    pattern = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$")
    return bool(pattern.match(domain))

def main():
    # Try to load existing data from 'data.json'
    companies = load_from_json_file("1companies.json",data_folder)
    product_names = load_from_json_file("2products.json",data_folder)
    
    for name_project in product_names:
        print(name_project)

        if any(company_data.get('sourcekeyword') == name_project for company_data in companies.values()):
            print('exists. ')
            continue

        organic_results = search_google(name_project)
        print(organic_results)

        serp = ""
        for result in organic_results:
            if "snippet" not in result:
                result["snippet"] = ""
            serp += (str(result["position"]) + ". " + result["link"] + "\n" + result["title"] + "\n" + result["snippet"] + "\n\n")
        
        url = findOfficialDomain(serp, name_project)

        if (is_valid_domain(url)):
            domain = url
        else:
            domain = extract_domain_from_url(url)

        if domain != "not found" and is_valid_domain(domain):
            if domain not in companies:  # Check if domain is not already in data
                companies[domain] = {'url': url,'sourcekeyword': name_project}
            else:
                companies[domain]['url'] = url
                companies[domain]['sourcekeyword'] = name_project

        # Save the data to data.json
        save_to_json_file(companies,"1companies.json",data_folder)
        print("Data saved to companies.json. Run 5..py")

if __name__ == '__main__':
    main()

