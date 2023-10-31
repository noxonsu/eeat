from urllib.parse import urlparse
import os
import re
import json
from bs4 import BeautifulSoup
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import Html2TextTransformer
from urllib.parse import urljoin

def extract_domain_from_url(url):
    """Extract the domain from a given URL."""
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return domain

def ensure_directory_exists(directory):
    """Ensure the specified directory exists. If not, create it."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_to_json_file(data, filename, folder_name):
    """Save the data to data.json within a specified folder."""
    
    # Ensure the directory exists
    ensure_directory_exists(folder_name)

    file_path = os.path.join(folder_name, filename)

    try:
        # Read existing data from the file
        with open(file_path, 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    if isinstance(data, dict):
        # Update the data without overriding
        for key, value in data.items():
                existing_data[key] = value
        data_to_write = existing_data
    elif isinstance(data, list):
        data_to_write = data
    else:
        raise ValueError("Unsupported data type for saving to JSON. Expected dict or list.")

    # Save the updated data back to the file
    with open(file_path, 'w') as file:
        json.dump(data_to_write, file, indent=4)


def load_from_json_file(filename, folder_name):
    """Load data from a JSON file within a specified folder."""
    
    file_path = os.path.join(folder_name, filename)

    try:
        # Read data from the file
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError):
        return {}
    except (json.JSONDecodeError):
        print(f"Error: Could not load data from {file_path}")
        return {}



def generate_html_from_json(json_data):
    """
    Generate an HTML page from the provided JSON structure.

    :param json_data: A dictionary containing the JSON structure.
    :return: A string containing the HTML representation.
    """
    
    # Basic HTML structure with placeholders for our content.
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="keywords" content="{meta_keywords}">
        <meta name="description" content="{meta_description}">
        <title>{title}</title>
    </head>
    <body>
        {text}
    </body>
    </html>
    """
    
    # Inserting the content from the JSON into our HTML template.
    html_content = html_template.format(
        title=json_data.get('title', ''),
        meta_keywords=json_data.get('meta_keywords', ''),
        meta_description=json_data.get('meta_description', ''),
        text=json_data.get('text', '')
    )
    
    return html_content

from bs4 import BeautifulSoup

def extract_links_with_text_from_html(html_content, base_url):
    """Extract all internal links with their text from the given HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    links_with_text = set()

    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        text = a_tag.string if a_tag.string else ""
        # Only add internal links to the set
        if base_url in link:
            links_with_text.add(f"{link}:{text}")
        elif link.startswith('/'):
            full_url = urljoin(base_url, link)
            links_with_text.add(f"{full_url}:{text}")

    return list(links_with_text)

def correct_url(url):
    """Corrects a URL that has double slashes by using the domain as the base URL."""
    parsed_url = urlparse(url)
    
    # If '//' is found in the path, correct it
    if '//' in parsed_url.path:
        # Extract the part after the '//' 
        corrected_path = parsed_url.path.split('//')[-1]
        
        # Construct the corrected URL using the domain as the base
        corrected_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{corrected_path}"
    else:
        # If no '//' in the path, return the original URL
        corrected_url = url
    
    return corrected_url

def extract_content(site):
    loader = AsyncChromiumLoader([site])
    docs = loader.load()
    
    # Проверка на наличие документов
    if not docs:
        return {
            "error": f"Failed to load the site {site}",
            "text_content": None,
            "html_content": None
        }

    # Извлечение HTML содержимого
    

    html_content = docs[0].page_content

    # Преобразование HTML в текст
    html2text = Html2TextTransformer({'ignore_links': False})
    text_content = html2text.transform_documents(docs)

    if not text_content:
        return {
            "error": f"Failed to extract content for site {site}",
            "text_content": None,
            "html_content": html_content
        }

    return {
        "error": None,
        "text_content": text_content[0].page_content,
        "html_content": html_content
    }