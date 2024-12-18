import csv
import re

#-----------------------------------------------------------#
#THIS PROGRAM IS IN TANDOM WITH THE PARSING INTO TEXT SCRIPT
#GO TO LINE 63 AND 65 FOR FILE PATH CHANGES
#WRITTEN BY RILEY HERBST
#updated for stripped prompt 3/19/2024 by Jeff Gwilliam
#-----------------------------------------------------------#


def extract_info_from_text(text):
    
    #Seeing which categories we want. Looking at txt file
    regex_patterns = {
    'Image': r"Image: (.+?)\n",
    'verbatimCollectors': r"verbatimCollectors: (.+?)\n",
    'collectedBy': r"collectedBy: (.+?)\n",
    'secondaryCollectors': r"secondaryCollectors: (.+?)\n",
    'recordNumber': r"recordNumber: (.+?)\n",
    'verbatimEventDate': r"verbatimEventDate: (.+?)\n",
    'minimumEventDate': r"minimumEventDate: (.+?)\n",
    'maximumEventDate': r"maximumEventDate: (.+?)\n",
    'verbatimIdentification': r"verbatimIdentification: (.+?)\n",
    'latestScientificName': r"latestScientificName: (.+?)\n",
    'identifiedBy': r"identifiedBy: (.+?)\n",
    'verbatimDateIdentified': r"verbatimDateIdentified: (.+?)\n",
    'associatedTaxa': r"associatedTaxa: (.+?)\n",
    'country': r"country: (.+?)\n",
    'firstPoliticalUnit': r"firstPoliticalUnit: (.+?)\n",
    'secondPoliticalUnit': r"secondPoliticalUnit: (.+?)\n",
    'municipality': r"municipality: (.+?)\n",
    'verbatimLocality': r"verbatimLocality: (.+?)\n",
    'locality': r"locality: (.+?)\n",
    'habitat': r"habitat: (.+?)\n",
#    'substrate': r"substrate: (.+?)\n",
    'verbatimElevation': r"verbatimElevation: (.+?)\n",
    'verbatimCoordinates': r"verbatimCoordinates: (.+?)\n",
    'otherCatalogNumbers': r"otherCatalogNumbers: (.+?)\n",
    'originalMethod': r"originalMethod: (.+?)\n",
    'typeStatus': r"typeStatus: (.+?)\n",
     
    }

    result = {}
    
    #For each of the Categories. Match the ones in the txt file to the ones created in the csv
    for key, pattern in regex_patterns.items():
        match = re.search(pattern, text)
        result[key] = match.group(1) if match else ''

    return result

#Open file
def process_file(file_path):
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            contents = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []

    entries = re.split(r'Image: ', contents)[1:]  # Split entries based on the image marker

    data = []
    for entry in entries:
        entry_info = extract_info_from_text('Image: ' + entry)
        data.append(entry_info)

    return data

def export_to_csv(data, csv_file_path):
    fields = list(data[0].keys())

    with open(csv_file_path, 'w', encoding="utf-8", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

def main(input_file_path, output_csv_file_path):
    extracted_data = process_file(input_file_path)
    if extracted_data:
        export_to_csv(extracted_data, output_csv_file_path)
        print(f"Data exported to '{output_csv_file_path}'.")
        print(f"All Done!")
        

if __name__ == "__main__":
    #CHANGE INPUT TO DESIRED .TXT FILE
    input_file_path = "/Users/jeff/ChatGPT/Output_4_23_1306.txt"
    #CHANGE OUTPUT TO DESIRED LOCATION TO .CSV FILE
    output_csv_file_path = "/Users/jeff/ChatGPT/Spread_4_23_1306.csv"
    main(input_file_path, output_csv_file_path)
