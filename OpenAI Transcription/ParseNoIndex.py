import base64
import requests
import os
import json
import re
import csv
import time



#THIS ITERATION WAS MADE ON 2-27-24#
#Put all filepaths in double quotes
# OpenAI API Key
api_key = "APiKeyHere"

#FilePath for textfile containing prompt
prompt_file_path = "prompt.txt"

#Filepath for Textfile containing url's
url_text = "url.txt"

#Filepath for folder holding images
image_folder = "Image Folder"

#Filepath for textfile 
output_file = "output.txt"




def download_images(file_path, save_folder):
    # Ensure save folder exists
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Read URLs from file and store them in a list
    with open(file_path, 'r') as file:
        urls = file.readlines()

    # Download each image
    for url in urls:
        url = url.strip()  # Remove any extra whitespace
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful

            # Extract image name from URL
            image_name = os.path.basename(url)
            save_path = os.path.join(save_folder, image_name)

            with open(save_path, 'wb') as img_file:
                img_file.write(response.content)
            print(f"Downloaded: {image_name}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")

    # Return the list of URLs
    return urls

# Download images and collect URLs
image_urls = download_images(url_text, 
                             image_folder)

user_confirmation = input("Proceed with parsing the images? (yes/no): ").strip().lower()
if user_confirmation != "yes":
    print("Parsing cancelled by the user.")
    quit()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your folder containing images
folder_path = image_folder

# Headers for the request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Function to format the response
def format_response(image_name, response_data):
    # Check if 'choices' is present and not empty in the response
    if "choices" in response_data and response_data["choices"]:
        content = response_data["choices"][0].get("message", {}).get("content", "")
        formatted_output = f"Image: {image_name}\n\n{content}\n"
    else:
        # If 'choices' is empty or not present, set a default message
        formatted_output = f"Image: {image_name}\n\nNo data returned from API.\n" 
    return formatted_output


def read_prompt_file(prompt_file_path):
    with open(prompt_file_path, 'r', encoding='utf-8') as file:
        return file.read()
    

# Open the file for writing

prompt_text = read_prompt_file(prompt_file_path)
with open(output_file, "w", encoding="utf-8") as file:
    counter = 0
    # Iterate through each image in the folder
    for image_name, url in zip(os.listdir(folder_path), image_urls):
        image_path = os.path.join(folder_path, image_name)
        
        
        if os.path.isfile(image_path):
            print(f"Processing entry {counter + 1}: {image_name}")
            start_time = time.time()
            total_time = time.time()
            base64_image = encode_image(image_path)
            
            payload = {
                       "model": "gpt-4-turbo",
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
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "auto"
                    }
                }
            ]
        }
    ],
                  "max_tokens": 3000,
                  "temperature": 0,  # Add temperature parameter
                  "seed": 42  # Add seed parameter
}


            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response_data = response.json()
            print("Here is the raw Data Generated",response_data)

            
            
            # Format and write the result to the file
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
finalend_time = time.time()
final_time = finalend_time - total_time
#print(f"Final time: {final_time:.2f} seconds")
print("All Done!")



