import anthropic
import base64
import os
import time
import json
import requests

# Business as usual
api_key = "api_key_here"

prompt_file_path = "prompt.txt"
url_text = "url.txt"
image_folder = "imagefolder"
output_file = "output.txt"

prompt_file_path = os.path.normpath(prompt_file_path)
url_text = os.path.normpath(url_text)
image_folder = os.path.normpath(image_folder)
output_file = os.path.normpath(output_file)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def read_prompt_from_file(prompt_file_path):
    with open(prompt_file_path, "r", encoding="utf-8") as prompt_file:
        return prompt_file.read().strip()

def format_response(image_name, response_data):
    # Extract the text from the response data
    text_block = response_data[0].text

    # Split the text into lines
    lines = text_block.split('\n')

    # Create a formatted result string
    formatted_result = f"Image Name: {image_name}\n\n"
    formatted_result += "\n"
    formatted_result += "\n".join(lines)

    return formatted_result
    

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

# Download images and collect URLs
image_urls = download_images(url_text, image_folder)

user_confirmation = input("Proceed with parsing the images? (yes/no): ").strip().lower()
if user_confirmation != "yes":
    print("Parsing cancelled by the user.")
    quit()
    

client = anthropic.Anthropic(api_key=api_key)
prompt_text = read_prompt_from_file(prompt_file_path)

total_time = time.time()
counter = 0

with open(output_file, 'w', encoding='utf-8') as file:
    image_files = sorted(os.listdir(image_folder))  # Ensure consistent order
    for image_name, url in zip(image_files, image_urls):
        image_path = os.path.join(image_folder, image_name)
        if os.path.isfile(image_path):
            print(f"Processing entry {counter + 1}: {image_name}")
            start_time = time.time()
            base64_image = encode_image_to_base64(image_path)

            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2500,
                temperature=0,
                system="You are an assistant that has a job to extract text from an image and parse it out.",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_text
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            )

            response_data = message.content
            print("This is response_data: ", response_data)

            try:
                formatted_result = format_response(image_name, response_data)
                file.write(formatted_result)
                file.write(f"\nURL: {url}\n")
                print(formatted_result)
            except TypeError as e:
                print(f"TypeError encountered: {e}")
                file.write(f"Image: {image_name}\nResponse: {response_data}\n")
                file.write(f"\nURL: {url}\n")
                print(f"Image: {image_name}\nResponse: {response_data}\n")

            file.write("=" * 50 + "\n")
            print(f"Completed processing: {image_name}")
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Completed processing entry {counter + 1} in {elapsed_time:.2f} seconds")

            counter += 1

finalend_time = time.time()
final_time = finalend_time - total_time
print(f"Total entries processed: {counter}")
print(f"Total processing time: {final_time:.2f} seconds")
print("All Done!")
print(f"Results saved to {output_file}")