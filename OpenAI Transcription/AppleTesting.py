import base64
import requests
import os
import json
import re
import csv
import time

# Set your inputs here
api_key = "YOUR_API_KEY"
prompt_file_path = "path/to/your/prompt_file.txt"
url_text = "path/to/your/url_text.txt"
image_folder = "path/to/your/image_folder"
output_file = "path/to/your/output_file.txt"

# Ensure all file paths are normalized
prompt_file_path = os.path.normpath(prompt_file_path)
url_text = os.path.normpath(url_text)
image_folder = os.path.normpath(image_folder)
output_file = os.path.normpath(output_file)

def download_images(file_path, save_folder):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    with open(file_path, 'r') as file:
        urls = file.readlines()

    for index, url in enumerate(urls):
        url = url.strip()
        try:
            response = requests.get(url)
            response.raise_for_status()
            image_name = os.path.basename(url)
            image_name_with_index = f"{index:04d}_{image_name}"
            save_path = os.path.join(save_folder, image_name_with_index)
            with open(save_path, 'wb') as img_file:
                img_file.write(response.content)
            print(f"Downloaded: {image_name_with_index}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")

    return urls

def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def format_response(image_name, response_data):
    # Extract the relevant information from the response
    message = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    # Create a formatted result string
    formatted_result = f"Image: {image_name}\nResponse:\n{message}\n\n"
    return formatted_result

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

with open(prompt_file_path, 'r') as file:
    prompt_text = file.read()

image_urls = download_images(url_text, image_folder)

user_confirmation = input("Proceed with parsing the images? (yes/no): ").strip().lower()
if user_confirmation != "yes":
    print("Parsing cancelled by the user.")
    exit()

counter = 0
with open(output_file, 'w') as file:
    for url in image_urls:
        url = url.strip()
        image_name = os.path.basename(url)
        image_path = os.path.join(image_folder, f"{counter:04d}_{image_name}")
        if os.path.isfile(image_path):
            print(f"Processing entry {counter + 1}: {image_name}")
            start_time = time.time()
            base64_image = encode_image(image_path)
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0,
                "seed": 42
            }
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response_data = response.json()
            print("Here is the raw Data Generated", response_data)
            formatted_result = format_response(image_name, response_data)
            file.write(formatted_result)
            file.write(f"URL: {url}\n" + "="*50 + "\n")
            print(f"Completed processing: {image_name}")
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Completed processing entry {counter + 1} in {elapsed_time:.2f} seconds")
            counter += 1

print(f"Results saved to {output_file}")
print(f"Total entries processed: {counter}")
