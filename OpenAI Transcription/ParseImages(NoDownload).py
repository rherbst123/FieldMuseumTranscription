import base64
import requests
import os
import json

# OpenAI API Key
api_key = ""

# FilePath for textfile containing prompt
prompt_file_path = ""

# Filepath for folder holding images
image_folder = ""

# Filepath for textfile 
output_file = ""

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to read the prompt text from a file
def read_prompt_file(prompt_file_path):
    with open(prompt_file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Format the response
def format_response(image_name, response_data):
    if "choices" in response_data and response_data["choices"]:
        content = response_data["choices"][0].get("message", {}).get("content", "")
        formatted_output = f"Image: {image_name}\n\n{content}\n"
    else:
        formatted_output = f"Image: {image_name}\n\nNo data returned from API.\n"
    return formatted_output

# Headers for the request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

prompt_text = read_prompt_file(prompt_file_path)

with open(output_file, "w", encoding="utf-8") as file:
    counter = 0
    # Iterate through each image in the folder
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        
        if os.path.isfile(image_path):
            print(f"Processing entry {counter + 1}: {image_name}")
            base64_image = encode_image(image_path)
           
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_text
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1024
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response_data = response.json()

            # Format and write the result to the file
            formatted_result = format_response(image_name, response_data)
            file.write(formatted_result + "="*50 + "\n")
            print(f"Completed processing: {image_name}")
            print(response_data)
            counter += 1  

print(f"Results saved to {output_file}")
print(f"Total entries processed: {counter}")
print("All Done!")
