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

from utils import *

INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD')


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
        SystemMessagePromptTemplate.from_template("""Instructions for Assistant to Analyze [INDUSTRY_KEYWORD]

Objective: To determine the critical characteristics or features of the chosen [INDUSTRY_KEYWORD] that may be important to consumers.

Preparation:
Familiarize yourself with the content from the main pages of the companies provided.
Get a broad understanding of [INDUSTRY_KEYWORD] and its implications in the industry.

Collate findings in a structured manner. For each service, list down how they fare in each of the criteria.

In additional detrmine such information
1. Call to action - talk to a manager like 'book a demo', 'talk to team', sign up etc.
2. Determine their business model (how they earn) and prices
3. Their usecases (use the same name for similar suecases of all companies)  
4. Their solutions (use the same name for similar solutions of all companies)
5. Key features
6. Brief summary 2-3 sentencies
7. Is this project realy one of the [INDUSTRY_KEYWORD]?
                                                                
Summarize your findings in a concise manner. The goal is to provide an objective view of each [INDUSTRY_KEYWORD] offerings, highlighting both strengths and potential areas for improvement. Provide the results in JSON format."""
),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ]
)

# Initialize the ConversationBufferMemory and LLMChain
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=5000, return_messages=True,extra_variables=["INDUSTRY_KEYWORD"])
conversation = ConversationChain(llm=llm, prompt=prompt,memory=memory)


def get_company_details(company):
    """Extract details of the company using the LLMChain."""
    summary=load_from_json_file(company+".json","data/"+INDUSTRY_KEYWORD)
    question_content = 'INDUSTRY_KEYWORD: '+INDUSTRY_KEYWORD+"\n\n"+summary['summary']
    question_content = question_content[:50000]
    response = conversation({ "input": question_content })
    
    gpt_response = response['response']
    try:
        return json.loads(gpt_response)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for response: {gpt_response}")
        return None
    

def main():
    
    summaries = load_from_json_file("companies.json", "data/" + INDUSTRY_KEYWORD)
    
    # Filter the summaries to get only those with nature "single project"
    filtered_summaries = {k: v for k, v in summaries.items() if v.get('nature') == "single project"}
   
    # Load existing company details
    existing_company_details = load_from_json_file("companies_details.json", "data/" + INDUSTRY_KEYWORD)
    company_details = existing_company_details.copy()  # Start with existing details
    
    # Iterate through the filtered summaries to get details for each company
    for company, compdata in filtered_summaries.items():
        if company not in existing_company_details:  # Only fetch details if not already present
            print(f"Fetching details for company: {company}")
            details = get_company_details(company)
            if details:
                company_details[company] = details
                save_to_json_file(company_details, "companies_details.json", "data/" + INDUSTRY_KEYWORD)

if __name__ == "__main__":
    main()

