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
import markdown

# Function to check if existing domains are included in the output
def check_domains_in_output(existedDomainList, output, article_index):
    for existedDomain in existedDomainList:
        if existedDomain.lower().replace("www.","") not in output.lower():
            print(f"{existedDomain} not in output of this file article{article_index}.md")
            exit()

def read_markdown_file(file):
    with open(file, "r") as f:
        return f.read()

def generate_html_from_markdown(mark,title,keys,desc):
    #markdown to html with tables
    #mark = mark.replace("- ","<Br>- ")
    html = markdown.markdown(mark,extensions=['markdown.extensions.tables'])
    html = html.replace("- ","<Br>- ")
    return """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="keywords" content="{meta_keywords}">
        <meta name="description" content="{meta_description}">
        <title>{title}</title>
    </head>
    <body>
        <article>
        {text}
        </article>
        
    </body>
    </html>""".format(text=html,title=title,meta_keywords=keys,meta_description=desc)


# Environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD', 'Vector databases')
TITLE_ARTICLE = os.environ.get('TITLE_ARTICLE', 'Vector databases')

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
        SystemMessage(content="""Create research article of features and prices in """+INDUSTRY_KEYWORD+""" . Keep numbers!  Kepp all project names. If possible add tables and lists. Return markdown. The title must included """+TITLE_ARTICLE+""". Compile Conclusion, Resume and Introduction to one short part and place it to the start of the article. Keep list of industry features. Don't add conclution (place important info into the start of article) """),
        HumanMessage(content=input)
    ]
    gen=True
    if (gen == True):
        start = time.time()
        try:
            mod = "gpt-4-1106-preview" #gpt-4-1106-preview
            chat = ChatOpenAI(model_name=mod)
            response = chat(messages)
            print(mod)
        except:
            print(".16k")
            chat = ChatOpenAI(temperature=0, model_name="gpt-4-1106-preview")
            response = chat(messages)
            
        
        end = time.time()

        print("Time to get response1: "+str(end - start))

        
        with open(f"data/{INDUSTRY_KEYWORD}/article.md", "w") as f:
                    f.write(response.content)
        with open(f"data/{INDUSTRY_KEYWORD}/article_inpout.md", "w") as f:
                    f.write(json.dumps(input))


    file = "data/"+INDUSTRY_KEYWORD+"/article.md"


    mark=read_markdown_file(file)

    html=generate_html_from_markdown(mark,TITLE_ARTICLE,INDUSTRY_KEYWORD,INDUSTRY_KEYWORD)

    #save html to file
    def save_html_to_file(html):
        with open("data/"+INDUSTRY_KEYWORD+"/article.html", "w") as f:
            f.write(html)

    save_html_to_file(html)



