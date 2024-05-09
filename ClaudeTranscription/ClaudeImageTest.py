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
    print(f"API Response for {image_name}:")
    print(json.dumps(response_data, indent=2))

    # Check if 'choices' is present and not empty in the response
    if "choices" in response_data and response_data["choices"]:
        content = response_data["choices"][0].get("message", {}).get("content", "")
        formatted_output = f"Image: {image_name}\n\n{content}\n"
    else:
        # If 'choices' is empty or not present, set a default message
        formatted_output = f"Image: {image_name}\n\nNo data returned from API.\n"
        print(formatted_output)
    return formatted_output


def parse_images(image_paths):
    # Initialize the client with your API key
    client = anthropic.Anthropic(api_key=API_KEY)

    # Read the prompt from a .txt file
    with open('c:\\Users\\riley\\Desktop\\Portal\\Code\\Python\\Inputs\\1.4StrippedPrompt.txt', 'r', encoding='utf-8') as prompt_file:
        lines = prompt_file.readlines()
        prompt = ''.join(lines)

    # Parse each image
    for image_path in image_paths:
        try:
            # Extract image name from the file path
            image_name = os.path.basename(image_path)

            # Load the image data from the file
            with open(image_path, 'rb') as img_file:
                image_data = img_file.read()

            # Make API call for each image
            response_data = encode_and_api_call(client, image_data, prompt)

            # Format the response and write to the output file
            formatted_output = format_response(image_name, response_data)
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(formatted_output + "\n" + "-" * 50 + "\n")

        except Exception as e:
            print(f"Error parsing {image_path}: {e}")

def encode_and_api_call(client, image_data, prompt):
    try:
        # Encode the image data as base64
        image_data_base64 = base64.b64encode(image_data).decode('utf-8')

        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
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
        return message.dict()  # Return the JSON data instead of the message object
    except Exception as e:
        print(f"Error in API call: {e}")
        return None


# Get the list of downloaded image paths
image_paths = [os.path.join(image_folder, filename) for filename in os.listdir(image_folder)]

# Parse the downloaded images
parse_images(image_paths)