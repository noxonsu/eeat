import os
import re
import json
from serpapi import GoogleSearch
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from urllib.parse import urlparse

SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not SERPAPI_KEY:
    print("Please set the SERPAPI_KEY environment variable.")
    exit()


def findOfficialDomain(serp, project_name):
    
    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0613")
    messages = [
        SystemMessage(content="Analyse SERP and Identify company-specific domains based on a given Google search query. '"+project_name+"'. we are only looking for a commercial sites, not 'top 10' articles or News or information portals, qurey answer and other information. Return only list of urls if found. Return only urls without quotes etc."),
        HumanMessage(content=f" {serp} \n\n The urls list: ")
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

def save_to_json_file(data):
    """Save the data to data.json."""
    try:
        # Read existing data from the file
        with open('data.json', 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    # Update the data without overriding
    for key, value in data.items():
        if key not in existing_data:
            existing_data[key] = value

    # Save the updated data back to the file
    with open('data.json', 'w') as file:
        json.dump(existing_data, file, indent=4)

def main():
    
    name_project = "KYC providers SaaS or API"
    print(name_project+"\n")
    organic_results = search_google(name_project)
    print(organic_results)
            
    serp=""
    for result in organic_results:
        if "snippet" not in result:
            result["snippet"] = ""
        serp += (str(result["position"]) +". " + result["link"]+" "+result["title"]+" "+result["snippet"])
            
    urls=findOfficialDomain(serp,name_project)

    # Assuming the returned URLs are separated by commas or spaces
    url_list = re.split(r'[,\s]+', urls)

    # Create a dictionary where the domain name is the key
    data = {}
    for url in url_list:
        domain = extract_domain_from_url(url)
        if domain:  # Ensuring domain is not empty
            data[domain] = {'url':url}

    # Save the data to data.json
    save_to_json_file(data)
    print("Data saved to data.json")

if __name__ == '__main__':
    main()