import base64
import requests
import os
import json
import re
import csv
import time



#THIS ITERATION WAS MADE ON 2-27-24 AND HAS DARWINCORE FIELDS#

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
image_urls = download_images('CHANGE TO FILE PATH OF .txt FILE CONTAINING URLS', 
                             'CHANGE TO FILEPATH OF FOLDER WHERE PHOTOGRAPHS ARE GOING TO GO')

user_confirmation = input("Proceed with parsing the images? (yes/no): ").strip().lower()
if user_confirmation != "yes":
    print("Parsing cancelled by the user.")

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your folder containing images
folder_path = "CHANGE TO SAME PATH AS LINE 48 FOR PHOTOS"

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
output_file = "CHANGE TO FILEPATH OF OUTPUT .txt FILE OF PARSED INFORMATION"

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
                                "text":  "Please transcribe and expand all details from this herbarium label. Include full expansion of any abbreviations present. For all entries do not shorted units of measurement and always print out full units(mi to miles, m to meters, ft to feet). Do not Include any Full stops in Entries. If the output includes any words or phrases not in English, translate them to English. For Titles do not use All Capitals, only capitalize names and locations and do not abbreviate any names or locations. fields are using DarwinCore formatting. I require information on the following categories and to output in the following order. Title, recordedBy (A list (concatenated and separated) of names of people, groups, or organizations responsible for recording the original The primary collector or observer, especially one who applies a personal identifier should be listed first.), secondaryRecordedBy, scientificName (The full scientific name, with authorship and date information if known. When forming part of a dwc:Identification, this should be the name in lowest level taxonomic rank that can be determined. This term should not contain identification qualifications), accociatedTaxa (A list (concatenated and separated) of identifiers or names of dwc:Taxon records and the associations of this dwc:Occurrence to each of them.), varbatimEventDate (The verbatim original representation of the date and time information), eventDate (representation of the data and time information in a format of Day/Month/Year separated by a / Have Month spelled out fully), country, firstPoliticalUnit (State/Province/district), secondPoliticalUnit (County if Co. Use County), city (May be included in Detailed Locality, if so remove from there and put into city), verbatimLocality (The original textual description of the place.), locality (The specific description of the place.), habitat (a category describing the habitat in which the event occurred.), verbatimElevation (the original textual description of the elevation), collectionCode (the identifier for the collection or dataset from which the record was derived), catalogNumber (an identifier for the record within the dataset or collection), decimalLatitude, decimalLongitude, occuranceRemarks, Raw format of the sheet with no changes and or categories that is a verbatim transcription as seen on label"

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
    'recordedBy': r"recordedBy: (.+?)\n",
    'scientificName': r"scientificName: (.+?)\n",
    'associatedTaxa': r"associatedTaxa: (.+?)\n",
    'verbatimEventDate': r"verbatimEventDate: (.+?)\n",
    'eventDate': r"eventDate: (.+?)\n",
    'country': r"country: (.+?)\n",
    'firstPoliticalUnit': r"firstPoliticalUnit: (.+?)\n",
    'secondPoliticalUnit': r"secondPoliticalUnit: (.+?)\n",
    'city': r"city: (.+?)\n",
    'verbatimLocality': r"verbatimLocality: (.+?)\n",
    'locality': r"locality: (.+?)\n",
    'verbatimElevation': r"verbatimElevation: (.+?)\n",
    'collectionCode': r"collectionCode: (.+?)\n",
    'decimalLatitude': r"decimalLatitude: (.+?)\n",
    'decimalLongitude': r"decimalLongitude: (.+?)\n",
    'occuranceRemarks': r"occuranceRemarks: (.+?)\n",
    'rawformat': r"rawformat: (.+?)\n",

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
with open('FOR CSV PARSING: CHANGE TO SAME FILEPATH AS LINE 80', 'r', encoding='utf-8') as file:
    text_content = file.read()

# Parse the data with URLs
parsed_data = parse_data(text_content, image_urls)

# Write data to CSV
print("All Done!")
write_to_csv(parsed_data, 'CHANGE TO FILEPATH OF .csv ')
