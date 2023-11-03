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



OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD', 'Vector databases')

cfl = load_from_json_file("7key_features_optimized.json","data/"+INDUSTRY_KEYWORD)
# Check if exists.
if cfl:
    clusterized_features_list_f = "features list for projects (detect which aplyable to the project): "+cfl['title']+": \n "+cfl['intro']+json.dumps(cfl['features'])
else:
    clusterized_features_list_f = ""



#old Write a final SEO optimized article about [INDUSTRY_KEYWORD] using the data. Compare all the elements and find the best one project.  Need an article with tables, etc. Return as Markdown with Title, Meta keywords, Meta description, Text fields (without ")
prompt = ChatPromptTemplate(
    messages=[
        SystemMessage(content="""Act like an analytic. Need to create a comparsion article across the [INDUSTRY_KEYWORD] list. 
                                                  I will send you projects one by one. Analyse every product, then add given information to main article. 
                                                  What prices they have? What should i do to start using? Focus on differencies between porojects. Compare key features, uscases and solutions. do not include information that is too general (such as "complete solution", "best on the market", etc.) .
                                                  Return only main article every time we send you new project. Use tables and other markdown syntaxis.
                                                  If project has prices or plans move them upper than other projects.
                                                     """
                                                  .replace("[INDUSTRY_KEYWORD]", INDUSTRY_KEYWORD)),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ]
)

# Initialize the ConversationBufferMemory and LLMChain
llm1 = ChatOpenAI(temperature=0, max_tokens=3600, model_name="gpt-4")
memory1 = ConversationSummaryBufferMemory(llm=llm1, max_token_limit=3000, return_messages=True)
conversation1 = ConversationChain(llm=llm1, prompt=prompt,memory=memory1)

llm2 = ChatOpenAI(temperature=0, max_tokens=3600, model_name="gpt-3.5-turbo-16k")
memory2 = ConversationSummaryBufferMemory(llm=llm2, max_token_limit=3000, return_messages=True)
conversation2 = ConversationChain(llm=llm2, prompt=prompt,memory=memory2)

if __name__ == "__main__":
    # Загрузите данные из /data папки
    all_sites_data = load_from_json_file("5companies_details.json","data/"+INDUSTRY_KEYWORD)
    sites = list(all_sites_data.keys())
    existedDomainList = []

    for i, domain in enumerate(sites):
        if os.path.isfile(f"data/{INDUSTRY_KEYWORD}/article{i}.md"):
            print(f" data/{INDUSTRY_KEYWORD}/article{i}.md exists <- "+domain)
            existedDomainList.append(domain)
            if os.path.isfile(f"data/{INDUSTRY_KEYWORD}/article{i}_input.md"):
                with open(f"data/{INDUSTRY_KEYWORD}/article{i}_input.md", "r") as f:
                    input = f.read()
            else:
                input = ""
            with open(f"data/{INDUSTRY_KEYWORD}/article{i}.md", "r") as f:
                output = f.read()
                for existedDomain in existedDomainList:
                    if existedDomain.lower() not in output.lower():
                        print(f"{existedDomain} not in output of this file")
                        exit() 
            memory1.save_context({"input": input}, {"output": output})
            memory2.save_context({"input": input}, {"output": output})
            continue

        datatoAdd = all_sites_data[domain]
       
        question_content = """Add this project to comparsion """+domain+""" . 
    The string """+domain+""", """+",".join(existedDomainList)+""" must be included in your answer. 
    You can rewrite and optimize entire article.
            \n\n"""
        question_content += json.dumps(datatoAdd)
        

        print(domain)
        start = time.time()

        try:
            
            response = conversation1({ "input": question_content })
            gpt_response = response['response']
            memory2.save_context({"input": input}, {"output": output}) #save context to brother memory (1->2 and 2->1)
            print("gpt 4 ")
        except:
            response = conversation2({ "input": question_content })
            gpt_response = response['response']
            print("gpt .16k")
            memory1.save_context({"input": input}, {"output": output})
        try:
            
            with open(f"data/{INDUSTRY_KEYWORD}/article{i}.md", "w") as f:
                f.write(gpt_response)
            with open(f"data/{INDUSTRY_KEYWORD}/article{i}_input.md", "w") as f:
                f.write(question_content)
            if existedDomain.lower() not in output.lower():
                if existedDomain not in gpt_response:
                    print(f"{existedDomain} not in gpt_response")
                    exit() 
            existedDomainList.append(domain)
        except Exception as e:
            print(f"An error response = chat(messages) : {e}")
        end = time.time()
        print("Time to get response: "+str(end - start))
        print("added "+domain+" to article")



