#4analyseProduct.py
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

import json


import os

def load_summaries_from_data_folder(folder_path="data"):
    """Loads summaries from all JSON files in the specified folder."""
    summaries = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r") as f:
                content = json.load(f)
                if "summary" in content:
                    domain_name = filename.rstrip(".json")  # Extract domain name from filename
                    summaries[domain_name] = content["summary"]
    return summaries

def get_company_details(summary):
    """Extract details of the company using ChatOpenAI."""
    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")

    response = chat(messages=[
        SystemMessage(content="Extract a list of services provided by the company, their prices, and the features they're proud of. Also, check if they have an API. Provide the results in JSON format."),
        HumanMessage(content=summary)
    ])

    gpt_response = response.content
    try:
        # Try to convert the response to a JSON object
        return json.loads(gpt_response)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for response: {gpt_response}")
        return None

def load_existing_company_details(filename="company_details.json"):
    """Loads existing company details from the specified JSON file."""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}
def create_comparison_table():
    """Creates a comparative table for companies using ChatOpenAI."""
    
    # Load the company details
    with open('company_details.json', 'r') as f:
        company_details = json.load(f)

    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")

    # Create the request to get a comparative table
    request_content = json.dumps(company_details, indent=4)
    response = chat(messages=[
        SystemMessage(content="make a feature comparison table (features one per letter, companies are columns). Return markdown"),
        HumanMessage(content=request_content)
    ])

    gpt_response = response.content

    # Save or process the response as needed, for instance, saving to a new file:
    with open('comparison_table.md', 'w', encoding='utf-8') as f:
        f.write(gpt_response)

    return gpt_response

def main():
    # Load the summaries from the /data folder
    summaries = load_summaries_from_data_folder()
    
    # Load existing company details
    existing_company_details = load_existing_company_details()
    company_details = existing_company_details.copy()  # Start with existing details

    # Iterate through the summaries to get details for each company
    for company, summary in summaries.items():
        if company not in existing_company_details:  # Only fetch details if not already present
            print(f"Fetching details for company: {company}")
            details = get_company_details(summary)
            if details:
                company_details[company] = details

    # Save the updated company details to the JSON file
    with open('company_details.json', 'w') as f:
        json.dump(company_details, f, indent=4)

    print(create_comparison_table())
if __name__ == "__main__":
    main()

