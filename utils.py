from urllib.parse import urlparse
import os
import re
import json

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

    # Update the data without overriding
    for key, value in data.items():
        if key not in existing_data:
            existing_data[key] = value

    # Save the updated data back to the file
    with open(file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)

def load_from_json_file(filename, folder_name):
    """Load data from a JSON file within a specified folder."""
    
    file_path = os.path.join(folder_name, filename)

    try:
        # Read data from the file
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error: Could not load data from {file_path}")
        return {}

