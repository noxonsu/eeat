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
import requests
def extract_content(site):
    loader = AsyncChromiumLoader([site])
    docs = loader.load()
    html2text = Html2TextTransformer({'ignore_links': False})
    text_content = html2text.transform_documents(docs)
    if not text_content:
        return f"Failed to extract content for site {site}"
    return text_content[0].page_content

def extract_links_from_html(html_content, base_url):
    """Extract all internal links from the given HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()

    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        # Only add internal links to the set
        if base_url in link:
            links.add(link)
        elif link.startswith('/'):
            links.add(base_url + link)

    return list(links)

def scrape_website(base_url):
    """Scrape the given website for all its internal links and 
    compile the contents of all the pages into a single JSON document."""

    # Get the main page content
    response = requests.get(base_url)
    html_content = response.text

    # Extract links from the main page
    internal_links = extract_links_from_html(html_content, base_url)

    # Compile all contents into a dictionary
    all_contents = {}
    for link in internal_links:
        content = extract_content(link)
        all_contents[link] = content

    # Convert dictionary to JSON
    json_content = json.dumps(all_contents)

    return json_content

# To use:
base_url = "https://onout.org/"
json_document = scrape_website(base_url)
print(json_document)
