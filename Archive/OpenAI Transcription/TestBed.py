import base64
import requests
import os

# OpenAI API Key
api_key = ""

# FilePath for the prompt file
prompt_file_path = ""

# FilePath for the file containing image URLs
image_urls_file_path = ""

# Headers for the API request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Function to read the image URLs from a file
def read_image_urls(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

# Function to read the prompt from a file
def read_prompt_file(prompt_file_path):
    with open(prompt_file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to format the response
def format_response(response_data):
    if "choices" in response_data and response_data["choices"]:
        content = response_data["choices"][0].get("message", {}).get("content", "")
        return f"Response:\n{content}\n"
    else:
        return "No data returned from API."

# Read the image URLs and prompt
image_urls = read_image_urls(image_urls_file_path)
prompt_text = read_prompt_file(prompt_file_path)

# Loop through each image URL and make API call
for image_url in image_urls:
    # Create the payload for the API request
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        "max_tokens": 2048,
        "temperature": 0,
        "seed": 42
    }

    # Make the API call
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()

    # Format and print the response
    formatted_result = format_response(response_data)
    print(f"Response for image {image_url}:\n{formatted_result}")
