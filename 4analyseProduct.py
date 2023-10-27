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
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
import json
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.memory import ConversationSummaryBufferMemory

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


llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")

# Create the ChatPromptTemplate
prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template("""Instructions for Assistant to Analyze KYC API Service Providers

Objective: To determine the critical characteristics or features of the chosen KYC API service providers that may be important to consumers.

Preparation:

Familiarize yourself with the content from the main pages of the 10 companies provided.
Get a broad understanding of KYC (Know Your Customer) and its implications in the industry.

Use the provided content and conduct additional research if necessary.
Collate findings in a structured manner. For each provider, list down how they fare in each of the criteria.
Use ChatGPT for assistance in understanding technical jargon or for any questions related to the topic.
Presentation:

Summarize your findings in a concise manner.
Create a comparison chart or table to visually represent how each service provider measures up against the set criteria.
Final Note: Always ensure unbiased analysis. The goal is to provide an objective view of each KYC API service provider's offerings, highlighting both strengths and potential areas for improvement.  Provide the results in JSON format."""
                                                  ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ]
)

# Initialize the ConversationBufferMemory and LLMChain
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=5000, return_messages=True)

conversation = ConversationChain(llm=llm, prompt=prompt, memory=memory)


def get_company_details(summary):
    """Extract details of the company using the LLMChain."""
    
    question_content = summary

    response = conversation({ "input": question_content})
    
    gpt_response = response['response']
    try:
        return json.loads(gpt_response)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for response: {gpt_response}")
        return None
    
def create_comparison_table():
    """Creates a comparative table for companies using the LLMChain."""
    
    with open('company_details.json', 'r') as f:
        company_details = json.load(f)

    request_content = json.dumps(company_details, indent=4)
    response = conversation({"question": request_content})

    gpt_response = response.content
    with open('comparison_table.md', 'w', encoding='utf-8') as f:
        f.write(gpt_response)

    return gpt_response

def load_existing_company_details(filename="company_details.json"):
    """Loads existing company details from the specified JSON file."""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}


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

if __name__ == "__main__":
    main()

