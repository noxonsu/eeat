import os
import re
import json

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from utils import *

SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD')
KEYWORD_FOR_SERP = os.environ.get('KEYWORD_FOR_SERP',INDUSTRY_KEYWORD)


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

def read_existing_domains(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}

def save_to_json_file(data, filename, directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    file_path = os.path.join(directory_name, filename)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def main():
    industry_query = INDUSTRY_KEYWORD
    
    organic_results = search_companies_on_google(KEYWORD_FOR_SERP, 40)
    
    serp_content = ""
    for result in organic_results:
        if "snippet" not in result:
            result["snippet"] = ""
        serp_content += (str(result["position"]) + ". " + result["link"] + " " + result["title"] + " " + result["snippet"])
            
    company_urls = extract_company_urls_from_serp(serp_content, industry_query)

    # Assuming the returned URLs are separated by commas or spaces
    url_list = re.split(r'[,\s]+', company_urls)

    # Читаем уже существующие домены
    directory_name = os.path.join('data', INDUSTRY_KEYWORD)
    file_path = os.path.join(directory_name, '1companies.json')
    existing_domains = read_existing_domains(file_path)

    # Обновляем список компаний, если домен не существует
    for url in url_list:
        domain = extract_domain_from_url(url)
        if domain and domain not in existing_domains:  # Проверяем, что домен не существует
            existing_domains[domain] = {'url': url}
        else:
            print(domain+" exists")

    # Сохраняем обновленные данные
    save_to_json_file(existing_domains, '1companies.json', directory_name)
    print(f"Company data saved to {directory_name}/1companies.json")

if __name__ == '__main__':
    main()