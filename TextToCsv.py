import csv
import re

#-----------------------------------------------------------#
#THIS PROGRAM IS IN TANDOM WITH THE PARSING INTO TEXT SCRIPT
#GO TO LINE 63 AND 65 FOR FILE PATH CHANGES
#WRITTEN BY RILEY HERBST
#-----------------------------------------------------------#


def extract_info_from_text(text):
    
    #Seeing which categories we want. Looking at txt file
    regex_patterns = {
    'Image': r"Image: (.+?)\n",
    'title': r"title: (.+?)\n",
    'collectedBy': r"collectedBy: (.+?)\n",
    'secondaryCollectors': r"secondaryCollectors: (.+?)\n",
    'phylum': r"phylum: (.+?)\n",
    'family': r"family: (.+?)\n",
    'genus': r"genus: (.+?)\n",
    'specificEpithet': r"specificEpithet: (.+?)\n",
    'infraspecificEpithet': r"infraspecificEpithet: (.+?)\n",
    'scientificNameAuthorship': r"scientificNameAuthorship: (.+?)\n",
    'identifiedBy': r"identifiedBy: (.+?)\n",
    'dateIdentified': r"dateIdentified: (.+?)\n",
    'acceptedScientificName': r"acceptedScientificName: (.+?)\n",
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
    'habitat': r"habitat: (.+?)\n",
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
    'typeStatus': r"typeStatus: (.+?)\n",
    'occuranceRemarks': r"occuranceRemarks: (.+?)\n",
    'sex': r"sex: (.+?)\n",
    'reproductiveCondition': r"reproductiveCondition: (.+?)\n",
    'generalNotes': r"generalNotes: (.+?)\n",
    'expeditionFundedBy': r"expeditionFundedBy: (.+?)\n",
    'generalInformationAboutThePlantSpecimenItself': r"generalInformationAboutThePlantSpecimenItself: (.+?)\n",
    'rawFormat': r"rawFormat: (.+?)\n",
   
    }

    result = {}
    
    #For each of the Categories. Match the ones in the txt file to the ones created int he csv
    for key, pattern in regex_patterns.items():
        match = re.search(pattern, text)
        result[key] = match.group(1) if match else ''

    return result

#Open file
def process_file(file_path):
    try:
        with open(file_path, 'r') as file:
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

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    #CHANGE INPUT TO DESIRED .TXT FILE
    input_file_path = "C:\\Users\\riley\\OneDrive\\Desktop\\CodeForMe\\python\\Outputs\\Output2.29.1147.txt"
    #CHANGE OUTPUT TO DESIRED LOCATION TO .CSV FILE
    output_csv_file_path = "C:\\Users\\riley\\OneDrive\\Desktop\\CodeForMe\\python\\Outputs\\Spread2.29.1232.csv"

    extracted_data = process_file(input_file_path)
    if extracted_data:
        export_to_csv(extracted_data, output_csv_file_path)
        print(f"Data exported to '{output_csv_file_path}'.")
        print(f"All Done!")
