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
companies_file = ""



def clusterize_key_features(key_features):

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")

    # Create the ChatPromptTemplate
    prompt = ChatPromptTemplate(
        messages=[
                SystemMessagePromptTemplate.from_template("Remove elements which are not related to the topic [topic]. Clusterize the key features Create a Topic Title per Cluster. Return as json "),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}")
            ]
        )

    # Initialize the ConversationBufferMemory and LLMChain
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=1000, return_messages=True)
    conversation = ConversationChain(llm=llm, prompt=prompt,memory=memory)
    #print(key_features)
    #key_features = key_features[:10000]

    response = conversation({ "input": key_features })
    
    gpt_response = response['response']
    try:
        return json.loads(gpt_response)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for response: {gpt_response}")
        return None
    


def optimize_cluster(text,x,y):
    prompt = """You're an expert analytic. this are "features" list of """+INDUSTRY_KEYWORD+""". Group features (reutrned must be "features").  We analysed """+str(x)+""" sites and """+str(y)+""" features.

Then Improve the product feature list by eliminating irrelevant and uninformative content.

1. Define Criteria: Determine what is considered "fluff" or irrelevant information for your list. 
2. Analyze the List: Go through each item and check its alignment with the set criteria.
3. Remove Unnecessary Items: Delete items that don't meet the criteria. Remove unclear. 
Document Changes: Keeping a record of why certain items were removed can be useful for future references.
Use this framework for a thorough optimization of your product feature list. After optimization, present the result in the form of a list and a brief introduction, mentioning what this list represents, how many companies were analyzed, and the total number of features gathered. Return as json with fields: title, intro, resume, features (with subcategories)

 """
    mod = "gpt-4-1106-preview" #gpt-3.5-turbo-16k
    chat = ChatOpenAI(temperature=0, model_name=mod)
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=text)
    ]
    response = chat(messages)
    response.content = re.sub(r'```', '', response.content)
    response.content = re.sub(r'json', '', response.content)
    gpt_response = response.content
    
    try:
        return json.loads(gpt_response)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for response: {gpt_response}")
        return None

def main():
    
    details = load_from_json_file("5companies_details.json", "data/" + INDUSTRY_KEYWORD)

    #load all 'key_features' 
    key_features=[]
    for k,v in details.items():
        if 'key_features' in v:
            key_features.extend(v['key_features'])
    key_features=list(set(key_features))

    #how many companies analysed?
    total_companies=len(details)

    




    print("Clusterizing the Key Features total "+str(len(key_features)))

    print("Optimizing the Product Feature List")
    ret = optimize_cluster(json.dumps(key_features),total_companies,len(key_features))
    print(ret)
    save_to_json_file(ret, "7key_features_optimized.json", "data/"+INDUSTRY_KEYWORD)


if __name__ == "__main__":
    main()