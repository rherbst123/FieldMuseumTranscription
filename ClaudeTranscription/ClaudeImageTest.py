import anthropic
import base64
import requests
import os
import json
import re
import csv
import time

# Replace with your API key
API_KEY = "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"

image_folder = "c:\\Users\\riley\\Desktop\\Portal\\Code\\Python\\Outputs\\Images"

url_text = "c:\\Users\\riley\\Desktop\\Portal\\Code\\Python\\Inputs\\10test.txt"

output_file = "c:\\Users\\riley\\Desktop\\Portal\\Code\\Python\\Outputs\\Text\\OutputApr24.0758.txt"


def format_response(image_name, response_data):
    # Check if 'choices' is present and not empty in the response
    if "choices" in response_data and response_data["choices"]:
        content = response_data["choices"][0].get("message", {}).get("content", "")
        formatted_output = f"Image: {image_name}\n\n{content}\n"
    else:
        # If 'choices' is empty or not present, set a default message
        formatted_output = f"Image: {image_name}\n\nNo data returned from API.\n"
        print(formatted_output)
    return formatted_output



def download_images(file_path, save_folder):
    # Ensure save folder exists
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Read URLs from file and store them in a list
    with open(file_path, 'r') as file:
        urls = file.readlines()

    # Download each image, appending an index to maintain order
    for index, url in enumerate(urls):
        url = url.strip()  # Remove any extra whitespace
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful

            # Extract image name from URL
            image_name = os.path.basename(url)
            # Modify image name to include index for ordering
            image_name_with_index = f"{index:04d}_{image_name}"  # Prefix index, ensuring it's zero-padded
            save_path = os.path.join(save_folder, image_name_with_index)

            with open(save_path, 'wb') as img_file:
                img_file.write(response.content)
            print(f"Downloaded: {image_name_with_index}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")

    # Return the list of URLs
    return urls



def parse_images(image_urls):
    # Initialize the client with your API key
    client = anthropic.Anthropic(api_key=API_KEY)

    # Read the prompt from a .txt file
    with open('c:\\Users\\riley\\Desktop\\Portal\\Code\\Python\\Inputs\\1.4StrippedPrompt.txt', 'r', encoding='utf-8') as prompt_file:
        lines = prompt_file.readlines()
        prompt = ''.join(lines)

    # Parse each image
    for index, url in enumerate(image_urls):
        url = url.strip()  # Remove any extra whitespace
        try:
            # Extract image name from URL
            image_name = os.path.basename(url)
            # Modify image name to include index for ordering
            image_name_with_index = f"{index:04d}_{image_name}"  # Prefix index, ensuring it's zero-padded
            image_path = os.path.join(image_folder, image_name_with_index)

            # Make API call for each image
            response_data = encode_and_api_call(client, image_path, prompt)

            # Format the response and write to the output file
            formatted_output = format_response(image_name_with_index, response_data)
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(formatted_output + "\n" + "-" * 50 + "\n")

        except Exception as e:
            print(f"Error parsing {url}: {e}")

def encode_and_api_call(client, image_path, prompt):
    # Open the image file and read its contents
    with open(image_path, 'rb') as f:
        image_data = f.read()

    # Encode the image data as base64
    image_data_base64 = base64.b64encode(image_data).decode('utf-8')

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",  # Change this if your image is a different format
                            "data": image_data_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt  # Use the prompt read from the .txt file
                    }
                ],
            }
        ]
        
    )
    return(message)
    # Write the result to the output file with a line of 50 hyphens between each entry
    separator = "-" * 50 + "\n"
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(str(message) + "\n" + separator)


# Download images and collect URLs
image_urls = download_images(url_text, image_folder)



# Parse the downloaded images
parse_images(image_urls)


 # Format and write the result to the file
        
