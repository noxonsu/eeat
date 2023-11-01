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

from utils import *

INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD')
WHOISJSONAPI= os.environ.get('WHOISJSONAPI')
# Load the data
data_folder = f"data/{INDUSTRY_KEYWORD}"
companies_file = "5companies_details.json"


llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")

# Create the ChatPromptTemplate
prompt = ChatPromptTemplate(
    messages=[
            SystemMessagePromptTemplate.from_template("Remove elements which are not related to the topic [topic]. Clusterize the key features. Return as json "),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ]
    )

# Initialize the ConversationBufferMemory and LLMChain
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=5000, return_messages=True,extra_variables=["INDUSTRY_KEYWORD"])
conversation = ConversationChain(llm=llm, prompt=prompt,memory=memory)

def clusterize_key_features(key_features):
    print(key_features)
    #key_features = key_features[:10000]
    response = conversation({ "input": key_features })
    
    gpt_response = response['response']
    try:
        return json.loads(gpt_response)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for response: {gpt_response}")
        return None
    


def optimize_cluster(text):
    prompt2 = """Optimization of Product Feature List

Objective: Improve the product feature list by eliminating irrelevant and uninformative content.

Define Criteria: Determine what is considered "fluff" or irrelevant information for your list.
Analyze the List: Go through each item and check its alignment with the set criteria.
Remove Unnecessary Items: Delete items that don't meet the criteria.
Gather Feedback: Consult with a colleague or expert for an additional review.
Evaluate Effectiveness: Test your updated list among a small group of consumers.
Document Changes: Keeping a record of why certain items were removed can be useful for future references.
Use this framework for a thorough optimization of your product feature list. After optimization, present the result in the form of a list and a brief introduction, mentioning what this list represents, how many companies were analyzed, and the total number of features gathered."""
    #text = text[:10000]
    llm = ChatOpenAI(temperature=0, model_name="gpt-4")

    conversation2 = ConversationChain(llm=llm, prompt=prompt2,memory=memory)
    response = conversation2({ "input": text })
    
    gpt_response = response['response']
    try:
        return json.loads(gpt_response)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for response: {gpt_response}")
        return None

def main():
    
    details = load_from_json_file(companies_file, "data/" + INDUSTRY_KEYWORD)

    #load all 'key_features' 
    key_features=[]
    for k,v in details.items():
        if 'key_features' in v:
            key_features.extend(v['key_features'])
    key_features=list(set(key_features))

    #how many companies analysed?
    total_companies=len(details)

    print("Clusterizing the Key Features")
    if (
    ret = clusterize_key_features("topic: "+INDUSTRY_KEYWORD+"\n\n"+json.dumps(key_features))
    print(ret)
    print("Optimizing the Product Feature List")
    ret = optimize_cluster(json.dumps(ret))
    print(ret)
    save_to_json_file(ret, "key_features_clusterized.json", INDUSTRY_KEYWORD)


if __name__ == "__main__":
    main()