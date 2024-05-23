import anthropic
import base64
import os
import json
import logging

# Configure logging (UNCOMMENT FOR DEBUGGING)
#logging.basicConfig(level=logging.INFO)

# Replace with your API key
API_KEY = "API_KEY"

# Configurable paths
image_folder = "IMAGE_FOLDER"
prompt_file_path = 'PROMPT.txt'
output_file = "OUTPUT.txt"

def format_response(image_name, response_data):
    #UNCOMMENT FOR DEBUGGING
    #logging.info(f"API Response for {image_name}:")
    #logging.info(json.dumps(response_data, indent=2))

    if "content" in response_data:
        content_list = response_data["content"]
        if content_list:
            content = content_list[0].get("text", "")
            
            # Extract key-value pairs from the content
            data_lines = content.split('\n')
            formatted_content = ""
            for line in data_lines:
                if line.strip():
                    key, value = line.split(':', 1) if ':' in line else (line, "")
                    formatted_content += f"{key.strip():<25}: {value.strip()}\n"

            formatted_output = f"Image: {image_name}\n\n{formatted_content}\n"
            print(formatted_output)
            print("-" * 50)
        else:
            formatted_output = f"Image: {image_name}\n\nNo data returned from API.\n"
            logging.warning(f"No data returned from API for {image_name}")
    else:
        formatted_output = f"Image: {image_name}\n\nNo data returned from API.\n"
        logging.warning(f"No data returned from API for {image_name}")
    return formatted_output
  

def parse_images(image_paths):
    client = anthropic.Anthropic(api_key=API_KEY)

    with open(prompt_file_path, 'r', encoding='utf-8') as prompt_file:
        prompt = prompt_file.read()

    for image_path in image_paths:
        try:
            image_name = os.path.basename(image_path)

            with open(image_path, 'rb') as img_file:
                image_data = img_file.read()

            response_data = encode_and_api_call(client, image_data, prompt)

            formatted_output = format_response(image_name, response_data)
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(formatted_output + "\n" + "=" * 50 + "\n")

        except Exception as e:
            logging.error(f"Error parsing {image_path}: {e}")

def encode_and_api_call(client, image_data, prompt):
    try:
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
                                "media_type": "image/jpeg",
                                "data": image_data_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ]
        )
        return message.dict()
    except Exception as e:
        logging.error(f"Error in API call: {e}")
        return None

image_paths = [os.path.join(image_folder, filename) for filename in os.listdir(image_folder) if filename.endswith(('.png', '.jpg', '.jpeg'))]

parse_images(image_paths)
