import os
import requests

def publish_to_medium(title, content, tags, integration_token):
    # Medium API URL for creating posts
    api_url = 'https://api.medium.com/v1/me/posts'

    # Formatting the tags into a list
    tags_list = tags.split(",") if tags else []

    # Post data
    post_data = {
        'title': title,
        'contentFormat': 'markdown',  # Assuming content is in markdown format
        'content': content,
        'publishStatus': 'draft',  # Change to 'public' to publish immediately
        'tags': tags_list,
    }

    # Headers including the authentication token
    headers = {
        'Authorization': f'Bearer {integration_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Charset': 'utf-8'
    }

    # Sending post request to Medium
    response = requests.post(api_url, json=post_data, headers=headers)

    # Handling the response
    if response.ok:
        print("Post created successfully!")
        print(response.json())  # The response includes the URL of the new post
    else:
        print("Failed to create post")
        print(response.text)

# Validate Environment Variables
required_env_vars = ['MEDIUM_INTEGRATION_TOKEN', 'MEDIUM_TITLE', 'MEDIUM_TEXT', 'MEDIUM_TAGS']
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Getting environment variables
integration_token = os.environ['MEDIUM_INTEGRATION_TOKEN']
medium_title = os.environ['MEDIUM_TITLE']
medium_text = os.environ['MEDIUM_TEXT']
medium_tags = os.environ['MEDIUM_TAGS']

# Publishing to Medium
publish_to_medium(medium_title, medium_text, medium_tags, integration_token)
