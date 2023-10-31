#5visual.py.py
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



OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD', 'Vector databases')

llm = ChatOpenAI(temperature=0, model_name="gpt-4")

#old Write a final SEO optimized article about [INDUSTRY_KEYWORD] using the data. Compare all the elements and find the best one project.  Need an article with tables, etc. Return as Markdown with Title, Meta keywords, Meta description, Text fields (without ")
prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template("""Need to create a comparsion article across the [INDUSTRY_KEYWORD] list. 
                                                  Analyse every product, then add given information to main article. 
                                                  What prices they have? What should i do to start using? Compare key features, uscases and solutions. do not include information that is too general (such as "complete solution", "best on the market", etc.) .
                                                  Return only main article every time we send you new project. Use tables and other markdown syntaxis. """
        #SystemMessagePromptTemplate.from_template("""I will send you websites, just add them to your list and return only 10 of them in every answer""" 
                                                  ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ]
)

# Initialize the ConversationBufferMemory and LLMChain
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=3000, return_messages=True)
conversation = ConversationChain(llm=llm, prompt=prompt,memory=memory)



if __name__ == "__main__":
    # Загрузите данные из /data папки
    all_sites_data = load_from_json_file("companies_details.json","data/"+INDUSTRY_KEYWORD)
    
    # Получить список всех сайтов
    sites = list(all_sites_data.keys())
    
    i = 1
    prev=" We do deep analysis of many {INDUSTRY_KEYWORD}. Here is the reuslt:"
    while i < len(sites) - 1:
        first_site = sites[i]
        second_site = sites[i + 1]

         # Access the first provider for each site
        first_site_data = all_sites_data[first_site]
        second_site_data = all_sites_data[second_site]
        

        question_content = 'INDUSTRY_KEYWORD: ' + INDUSTRY_KEYWORD + "\n\n" 
        question_content += json.dumps(first_site_data)
      
        question_content += "Main article (need to be rewrited with new data): "+prev

        #response = conversation({ "input": question_content })
        #response['response']
        print(question_content)
        response = input("gpt answer") #ask user
        prev = response
        with open(INDUSTRY_KEYWORD+".md", 'w') as file:
            file.write(response)

        print("added "+first_site+" to article")
        i += 1


        # Далее можно обработать question_content по вашему усмотрению
