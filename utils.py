from urllib.parse import urlparse
import os
import re
import json
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import Html2TextTransformer
from urllib.parse import urljoin
from bs4 import BeautifulSoup

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



def extract_links_with_text_from_html(html_content, base_url):
    """Extract all internal links with their text from the given HTML content and return as JSON."""
    soup = BeautifulSoup(html_content, 'html.parser')
    links_with_text = []

    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        text = a_tag.string if a_tag.string else ""
        # Only add internal links to the list
        if base_url in link:
            links_with_text.append({"link": link, "text": text})
        elif link.startswith('/'):
            full_url = urljoin(base_url, link)
            links_with_text.append({"link": full_url, "text": text})

    return json.dumps(links_with_text, ensure_ascii=False)


def correct_url(url):
    """Corrects a URL that has double slashes by using the domain as the base URL and trims everything after ':' (excluding the 'https://' or 'http://')."""
    parsed_url = urlparse(url)
    
    # Combine path and params to get the full path
    full_path = parsed_url.path
    if parsed_url.params:
        full_path += f":{parsed_url.params}"
    
    # If '//' is found in the full path, correct it
    if '//' in full_path:
        # Extract the part after the '//' 
        corrected_path = full_path.split('//')[-1]
        
        # Construct the corrected URL using the domain as the base
        corrected_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{corrected_path}"
    else:
        # If no '//' in the full path, return the original URL
        corrected_url = url
    
    # Trim everything after ':' (excluding the 'https://' or 'http://')
    if "://" in corrected_url:
        scheme, rest_of_url = corrected_url.split("://", 1)
        rest_of_url = rest_of_url.split(":", 1)[0]
        corrected_url = f"{scheme}://{rest_of_url}"
    
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

def search_companies_on_google(industry_query,limt):
    SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
    params = {
        "engine": "google",
        "q": industry_query,
        'num': limt,
        "api_key": SERPAPI_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    # Error handling for missing key
    if "organic_results" in results:
        return results["organic_results"]
    else:
        print("Error: 'organic_results' not found in the results!")
        print(results)  # This will print the structure of results to inspect it
        return []
    
def get_wayback_url(input_url):
    base_url = "https://archive.org/wayback/available?url="
    full_url = base_url + input_url

    try:
        response = requests.get(full_url)
        response.raise_for_status()
        result = response.json()
        
        # Check if "archived_snapshots" is available in the response
        if "archived_snapshots" in result:
            closest_snapshot = result["archived_snapshots"]["closest"]
            if closest_snapshot.get("available") and closest_snapshot.get("url"):
                return closest_snapshot["url"]
        
        return None  # Return None if no valid URL is found

    except requests.exceptions.RequestException as e:
        print("Error making the request:", e)
        return None