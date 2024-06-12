import base64
import requests
import os
import json
import re
import csv
import time

# OpenAI API Key
api_key = "ENTER API KEY"

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

            # Extract image name from URL and save it
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
image_urls = download_images('CHANGE TO INPUT TEXT FILE OF URLS', 
                             'CHANGE TO WHERE IMAGES GO ')

user_confirmation = input("Proceed with parsing the images? (yes/no): ").strip().lower()
if user_confirmation != "yes":
    print("Parsing cancelled by the user.")
    quit()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your folder containing images
folder_path = "CHANGE TO THE SAME LOCATION AS LINE 44 FOR WHERE IMAGES GO"

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

# File to store the output
output_file = "CHANGE TO OUTPUT FILE FOR TEXT (MUST END IN A TEXTFILE FOR CREATION)"

# Open the file for writing
with open(output_file, "w", encoding="utf-8") as file:
    counter = 0
    # Iterate through each image in the folder
    for image_name, url in zip(os.listdir(folder_path), image_urls):
        image_path = os.path.join(folder_path, image_name)
        
        # Check if it's a file
        if os.path.isfile(image_path):
            print(f"Processing entry {counter + 1}: {image_name}")
            start_time = time.time()
            base64_image = encode_image(image_path)
           
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text":  "Please transcribe and expand all details from this herbarium specimen label  Include the full expansion of any abbreviations present. For all entries do not shorten Units of measurement always print out full units. Do not Incluide any Full stops in Entries.If the output includes any words or phrases not in English, Translate them to English. For Titles do not us All caps, only capitalize names and locations and do not abbreviate any names or locations. I require information on the following categories:  I want the list to output in the following order, Title, Collected by(The First Collector),Secondary Collectors(These are collecors listed after the first) Scientific name, Associated Taxon (if any special symbols are present you delete those), Date collected (Date collected Verbatum (As you see on label)(If in Roman Numerals Convert to Arabic Numbers)),Formatted Date Collected [Formatted to Day/Month/Year (If date is only in verbatum convert to a formatted date)],Determined By (This can be found using Det if present on the sheet.), Determined Date (also can be found in a field that contains Det), Country(Spell Out Whole country if abreviated), First Political Unit [State/Provience/district], Second Political Unit [County if co. Use County],City(May be included in Detailed Locality, if so remove from there and put into city), Detailed Locality(Verbatum: This is how it apprears ion the label) [Anything below the country and political unit providing specific information about the location. If you see mi, Mi. Spell this out to miles. If you see Natl, this is national, if you see ft. this is feet, If you see M this is meters, Also, tease out habiatat from loacality and remove elevation from locality but keep it in its own elevation Also do this for Habitat and exclusively put that information in habitiat], Habitat (Example: Substrate, If not present use N/A), Elevation [if M is present it is Meters. If Ft is present it is Feet. If nothing is present put N/A], Collection name [WIll be anything if you see an institution in the label. If not use N/A], Collection Number [if Not present put N/A], Lattitude, Longitude, Addional Notes (if blank just put N/A), Raw format of the sheet with no changes and or categories"

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
                "max_tokens": 300
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response_data = response.json()
            print("Here is the raw Data Generated",response_data)

            
            
            # Format and write the result to the file
            formatted_result = format_response(image_name, response_data)
            file.write(formatted_result)
        
            file.write(f"URL: {url}\n" + "="*50 + "\n")
            print(f"Completed processing: {image_name}")
            end_time = time.time()  # End the timer
            elapsed_time = end_time - start_time  # Calculate the elapsed time
            print(f"Completed processing entry {counter + 1} in {elapsed_time:.2f} seconds")

            counter += 1  # Increment the counter

print(f"Results saved to {output_file}")
print(f"Total entries processed: {counter}")

# Function to parse the text data
def parse_data(text, urls):
    # Split the text into sections for each specimen
    specimens = text.split("=" * 50)
    
    # List to hold all specimen data
    all_data = []

    # Regular expression patterns for each field
    patterns = {
       'Image': r"Image: (.+?)\n",
        'Title': r"Title: (.+?)\n",
        'Collected by': r"Collected by: (.+?)\n",
        'Secondary Collectors': r"Secondary Collectors: (.+?)\n",
        'Scientific name': r"Scientific name: (.+?)\n",
        'Associated Taxon': r"Associated Taxon: (.+?)\n",
        'Date collected Verbatum': r"Date collected Verbatum: (.+?)\n",
        'Formatted Date Collected': r"Formatted Date Collected: (.+?)\n",
        'Determined By': r"Determined By: (.+?)\n",
        'Determined Date': r"Determined Date: (.+?)\n",
        'Country': r"Country: (.+?)\n",
        'First Political Unit': r"First Political Unit: (.+?)\n",
        'Second Political Unit': r"Second Political Unit: (.+?)\n",
        'City': r"City: (.+?)\n",
        'Detailed Locality': r"Detailed Locality: (.+?)\n",
        'Elevation': r"Elevation: (.+?)\n",
        'Collection name': r"Collection name: (.+?)\n",
        'Collection Number': r"Collection Number: (.+?)\n",
        'Latitude': r"Latitude: (.+?)\n",
        'Longitude': r"Longitude: (.+?)\n",
        'Additional Notes': r"Additional Notes: (.+?)\n"
    }

    # Process each specimen
    for i, specimen in enumerate(specimens):
        if specimen.strip():  # Check if the specimen section is not empty
            data = {"URL": urls[i].strip()}  # Add URL to data
            for key, pattern in patterns.items():
                match = re.search(pattern, specimen)
                data[key] = match.group(1) if match else 'N/A'
            all_data.append(data)

    return all_data

# Function to write data to CSV
def write_to_csv(data, filename):
    if data:
        keys = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)

# Read the text from a file
with open('CMAKE THE SAME AS LINE 76 THIS IS FOR CSV PROCESSING', 'r', encoding='utf-8') as file:
    text_content = file.read()

# Parse the data with URLs
parsed_data = parse_data(text_content, image_urls)

# Write data to CSV
print("All Done!")
write_to_csv(parsed_data, 'MAKE THE OUTPUT A CSV FILE')
