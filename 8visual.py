#5visual.py.py
import json
import time
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


# Function to check if existing domains are included in the output
def check_domains_in_output(existedDomainList, output, article_index):
    for existedDomain in existedDomainList:
        if existedDomain.lower().replace("www.","") not in output.lower():
            print(f"{existedDomain} not in output of this file article{article_index}.md")
            exit()


# Environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD', 'Vector databases')

# Load clusterized features list
cfl = load_from_json_file("7key_features_optimized.json", "data/" + INDUSTRY_KEYWORD)
if cfl:
    clusterized_features_list_f = json.dumps(cfl)
else:
    clusterized_features_list_f = ""

with open(f"data/{INDUSTRY_KEYWORD}/article_pricing.md", "r") as f:
    prices_article = f.read()

if __name__ == "__main__":
    input = clusterized_features_list_f+" \n\n "+prices_article
    
    messages = [
        SystemMessage(content="""Create research article of features and prices in """+INDUSTRY_KEYWORD+""" . Keep numbers!  Kepp all project names. If possible add tables and lists. Return markdown. The title must included "KYC providers 2023". Compile Conclusion, Resume and Introduction to one short part and place to the start of article. Add that We removed from comparsion companies witout prices and sign up functionality. Keep list of industry features """),
        HumanMessage(content=input)
    ]

    start = time.time()
    try:
        chat = ChatOpenAI(model_name="gpt-4-1106-preview")
        response = chat(messages)
        print("gpt-4-1106-preview 4k")
    except:
        print(".16k")
        chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
        response = chat(messages)
        
    
    end = time.time()

    print("Time to get response1: "+str(end - start))

    
    with open(f"data/{INDUSTRY_KEYWORD}/article.md", "w") as f:
                f.write(response.content)
    with open(f"data/{INDUSTRY_KEYWORD}/article_inpout.md", "w") as f:
                f.write(json.dumps(input))



