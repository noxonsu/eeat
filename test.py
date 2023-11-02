
from utils import * 
import os

INDUSTRY_KEYWORD = os.environ.get('INDUSTRY_KEYWORD', 'Vector databases')

data = load_from_json_file("1companies.json", "data/"+INDUSTRY_KEYWORD)

# Function to check if the "nature" field contains invalid data
def is_invalid_nature(nature_data):
    # Define your condition for invalid nature data here
    # For example, if "nature" should not contain the word "invalid":
    return 'invalid' in nature_data.lower()

# Function to remove the "nature" field if it contains invalid data
def remove_invalid_nature(json_data):
    for key, value in json_data.items():
        if 'nature' not in value and 'sourcekeyword' not in value:
            value['nature'] = "invalid no sourcekeyword"

# Remove the "nature" field if it contains invalid data
remove_invalid_nature(data)

save_to_json_file(data, "1companies.json", "data/"+INDUSTRY_KEYWORD)
