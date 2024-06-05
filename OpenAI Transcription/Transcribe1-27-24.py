import base64
import requests
import os
import json
import re
import csv
import time



#THIS ITERATION WAS MADE ON 2-7-24 AND HAS DARWINCORE FIELDS#

# OpenAI API Key
api_key = "CHANGE TO API KEY"

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
image_urls = download_images('FILE PATH TO .TXT FILE OF URLS', 
                             'OUTPUT TO FOLDER FOR IMAGES')

user_confirmation = input("Proceed with parsing the images? (yes/no): ").strip().lower()
if user_confirmation != "yes":
    print("Parsing cancelled by the user.")
    exit()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your folder containing images
folder_path = "CHANGE TO FOLDER FOR IMAGES"

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
output_file = "FILE PATH OF OUTPUT TEXT FILE"

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
                                "text":  "Please transcribe and expand all details from this herbarium label. Include full expansion of any abbreviations present. For all entries do not shorten units of measurement and always print out full units(mi to miles, m to meters, ft to feet). Do not Include any Full stops in Entries. If the output includes any words or phrases not in English, translate them to English. For Titles do not use All Capitals, only capitalize names and locations and do not abbreviate any names or locations. fields are using DarwinCore formatting. If there is no information present for a field present a N/A I require information on the following categories and to output in the following order(Make sure the fields are exactly as typed). title: (A name given to the resource), recordedBy: (A list of names of people, groups, or organizations responsible for recording the original occurrence. The primary collector or observer, especially one who applies a personal identifier, should be listed first), secondaryRecordedBy: (Additional collectors or observers contributing to the recording of the occurrence. This is every name listed after the first name of collectors), acceptedScientificName: (The full scientific name, according to the latest taxonomic treatment (acceptance), of the organism referred to in the occurrence record), phylum ((Division): The phylum or division in which the taxon is classified, family: The family in which the taxon is classified), genus:( The genus in which the taxon is classified), specificEpithet:( The specific epithet of the scientific name; in binomial nomenclature, the second part of the name), infraspecificEpithet(: The infraspecific epithet of the scientific name; in trinomial nomenclature, the third part of the name), scientificNameAuthorship:( The authorship information for the scientific name formatted according to the conventions of the applicable nomenclatural code), identifiedBy:( A list of names of people, groups, or organizations who assigned the Taxon to the subject), dateIdentified: T(he date on which the subject was identified as representing the Taxon), otherScientificName: (Alternative scientific names that have been applied to the specimen), associatedTaxa:( A list of identifiers or names of taxa and their associations with the occurrence), verbatimEventDate:( The original verbatim text of the date and time information for the occurrence), eventDate:( The date-time or interval during which an event occurred, in an ISO 8601 date format), country:( The name of the country or major administrative unit in which the event occurred), countryCode:( The standard code for the country in which the event occurred), firstPoliticalUnit:( The name of the first-order administrative division in which the event occurred (e.g., state or province)), secondPoliticalUnit:( The name of the second-order administrative division in which the event occurred (e.g., county)), city: (The city or locality in which the event occurred), verbatimLocality(: The original textual description of the place where the occurrence was recorded), locality:( The specific description of the place. Less specific than verbatimLocality), habitat:( A category or description of the habitat in which the event occurred), substrate:( The underlying material or surface on which an organism lives or grows), verbatimElevation:( The original verbatim text of the elevation (altitude, depth) of the occurrence), maximumElevationInMeters:( The upper limit of elevation (in meters) for the occurrence), minimumElevationInMeters:( The lower limit of elevation (in meters) for the occurrence), verbatimCoordinates:( The original verbatim text of the coordinates), decimalLatitude: (The latitude of the location from which the occurrence was recorded, expressed in decimal degrees), decimalLongitude:( The longitude of the location from which the occurrence was recorded, expressed in decimal degrees), occurrenceRemarks: (Comments or notes about the occurrence), collectionCode:( The identifier for the collection or dataset from which the record was derived.), recordNumber:( An identifier given to the occurrence at the time it was recorded), catalogNumber:( An identifier for the record within the dataset or collection), language:( The language of the resource), languageRemarks: (Comments or notes about the language of the resource), originalMethod ((Handwritten, Typed, Printed): The method by which the original data was recorded), generalNotes: (Additional comments or notes about the occurrence or record), rawFormat:( A verbatim transcription of the label or record as it is represented in the physical or digital format Do not Indent this information and leave it as one line.)"

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
    'title': r"title: (.+?)\n",
    'recordedBy': r"recordedBy: (.+?)\n",
    'secondaryRecordedBy': r"secondaryRecordedBy: (.+?)\n",
    'phylum': r"phylum: (.+?)\n",
    'family': r"family: (.+?)\n",
    'genus': r"genus: (.+?)\n",
    'specificEpithet': r"specificEpithet: (.+?)\n",
    'infraspecificEpithet': r"infraspecificEpithet: (.+?)\n",
    'scientificNameAuthorship': r"scientificNameAuthorship: (.+?)\n",
    'identifiedBy': r"identifiedBy: (.+?)\n",
    'dateIdentified': r"dateIdentified: (.+?)\n",
    'otherScientificName': r"otherScientificName: (.+?)\n",
    'scientificName': r"scientificName: (.+?)\n",
    'associatedTaxa': r"associatedTaxa: (.+?)\n",
    'verbatimEventDate': r"verbatimEventDate: (.+?)\n",
    'eventDate': r"eventDate: (.+?)\n",
    'country': r"country: (.+?)\n",
    'countryCode': r"countryCode: (.+?)\n",
    'firstPoliticalUnit': r"firstPoliticalUnit: (.+?)\n",
    'secondPoliticalUnit': r"secondPoliticalUnit: (.+?)\n",
    'city': r"city: (.+?)\n",
    'verbatimLocality': r"verbatimLocality: (.+?)\n",
    'locality': r"locality: (.+?)\n",
    'Habitat': r"Habitat: (.+?)\n",
    'substrate': r"substrate: (.+?)\n",
    'verbatimElevation': r"verbatimElevation: (.+?)\n",
    'maximumElevationInMeters': r"maximumElevationInMeters: (.+?)\n",
    'minimumElevationInMeters': r"minimumElevationInMeters: (.+?)\n",
    'verbatimCoordinates': r"verbatimCoordinates: (.+?)\n",
    'decimalLatitude': r"decimalLatitude: (.+?)\n",
    'decimalLongitude': r"decimalLongitude: (.+?)\n",
    'collectionCode': r"collectionCode: (.+?)\n",
    'recordNumber': r"recordNumber: (.+?)\n",
    'catalogNumber': r"catalogNumber: (.+?)\n",
    'language': r"language: (.+?)\n",
    'languageRemarks': r"languageRemarks: (.+?)\n",
    'originalMethod': r"originalMethod: (.+?)\n",
    'generalNotes': r"generalNotes: (.+?)\n",
    'occuranceRemarks': r"occuranceRemarks: (.+?)\n",
    'rawFormat': r"rawFormat: (.+?)\n",
   


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
with open('OUTPUT TEXT FILE FILE PATH SAME AS LINE 80', 'r', encoding='utf-8') as file:
    text_content = file.read()

# Parse the data with URLs
parsed_data = parse_data(text_content, image_urls)

# Write data to CSV
print("All Done!")
write_to_csv(parsed_data, '.CSV FILE PATH EXPORT')
