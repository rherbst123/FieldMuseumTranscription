import google.generativeai as genai
import os
import requests
import time

prompt_file_path = "C:\\Users\\riley\\OneDrive\\Desktop\\CodeForMe\\python\\Input\\1.5Stripped.txt"
url_text = "C:\\Users\\riley\\OneDrive\\Desktop\\CodeForMe\\python\\Input\\100Test.txt"
image_folder = "C:\\Users\\riley\\OneDrive\\Desktop\\CodeForMe\\python\\Input\\Images"
output_file_path = "C:\\Users\\riley\\OneDrive\\Desktop\\CodeForMe\\python\\Output\\OutputJun.20.24.0153.txt"

prompt_file_path = os.path.normpath(prompt_file_path)
url_text = os.path.normpath(url_text)
image_folder = os.path.normpath(image_folder)
output_file_path = os.path.normpath(output_file_path)

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

image_urls = download_images(url_text, image_folder)

user_confirmation = input("Proceed with parsing the images? (yes/no): ").strip().lower()
if user_confirmation != "yes":
    print("Parsing cancelled by the user.")
    quit()

def read_prompt_from_file(prompt_file_path):
    with open(prompt_file_path, "r", encoding="utf-8") as prompt_file:
        return prompt_file.read().strip()

prompt_text = read_prompt_from_file(prompt_file_path)

GOOGLE_API_KEY = 'APIKEY'  # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)

# Ensure the output directory exists
output_directory = os.path.dirname(output_file_path)
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Choose a Gemini API model.
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
temperature = 0.0

# Open the output file for writing
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    # Process each image in the image folder
    for image_name in os.listdir(image_folder):
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            local_image_path = os.path.join(image_folder, image_name)
            
            # Upload the local file
            sample_file = genai.upload_file(path=local_image_path, display_name=image_name)
            
            # Prompt the model with text and the previously uploaded image.
            response = model.generate_content([sample_file, prompt_text])
            
            # Write the response to the output file
            output_file.write(f"Image: {image_name}:\n{response.text}\n")
            output_file.write("=" * 50 + "\n\n")
            
            # Pause to avoid overwhelming the API
            time.sleep(20)
            
            print(f"Image: {image_name}:\n{response.text}\n")
            print("=" * 50 + "\n\n")

print(f"Output written to {output_file_path}")
