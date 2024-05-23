import csv
import re

def extract_info_from_text(text):
    regex_patterns = {
        'Image': r"Image: (.+?)\n",
        'verbatimCollectors': r"verbatimCollectors\s+: (.+?)\n",
        'collectedBy': r"collectedBy\s+: (.+?)\n",
        'secondaryCollectors': r"secondaryCollectors\s+: (.+?)\n",
        'recordNumber': r"recordNumber\s+: (.+?)\n",
        'verbatimEventDate': r"verbatimEventDate\s+: (.+?)\n",
        'minimumEventDate': r"minimumEventDate\s+: (.+?)\n",
        'maximumEventDate': r"maximumEventDate\s+: (.+?)\n",
        'verbatimIdentification': r"verbatimIdentification\s+: (.+?)\n",
        'latestScientificName': r"latestScientificName\s+: (.+?)\n",
        'identifiedBy': r"identifiedBy\s+: (.+?)\n",
        'verbatimDateIdentified': r"verbatimDateIdentified\s+: (.+?)\n",
        'associatedTaxa': r"associatedTaxa\s+: (.+?)\n",
        'country': r"country\s+: (.+?)\n",
        'firstPoliticalUnit': r"firstPoliticalUnit\s+: (.+?)\n",
        'secondPoliticalUnit': r"secondPoliticalUnit\s+: (.+?)\n",
        'municipality': r"municipality\s+: (.+?)\n",
        'verbatimLocality': r"verbatimLocality\s+: (.+?)\n",
        'locality': r"locality\s+: (.+?)\n",
        'habitat': r"habitat\s+: (.+?)\n",
        'substrate': r"substrate\s+: (.+?)\n",
        'verbatimElevation': r"verbatimElevation\s+: (.+?)\n",
        'verbatimCoordinates': r"verbatimCoordinates\s+: (.+?)\n",
        'otherCatalogNumbers': r"otherCatalogNumbers\s+: (.+?)\n",
        'originalMethod': r"originalMethod\s+: (.+?)\n",
        'typeStatus': r"typeStatus\s+: (.+?)\n",
    }

    result = {}
    for key, pattern in regex_patterns.items():
        match = re.search(pattern, text)
        result[key] = match.group(1) if match else ''

    return result

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []

    entries = re.split(r'Image: ', contents)[1:]

    data = []
    for entry in entries:
        entry_info = extract_info_from_text('Image: ' + entry)
        data.append(entry_info)

    return data

def export_to_csv(data, csv_file_path):
    if not data:
        print("No data to write to CSV.")
        return

    fields = list(data[0].keys())
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    input_file_path = "c:\\Users\\Riley\\Desktop\\Portal\\Code\\Python\\Outputs\\Text\\OutputMay5.0758.txt"
    output_csv_file_path = "C:\\Users\\Riley\\Desktop\\Portal\\Code\\Python\\Outputs\\SpreadMay5.0758.csv"

    extracted_data = process_file(input_file_path)
    if extracted_data:
        export_to_csv(extracted_data, output_csv_file_path)
        print(f"Data exported to '{output_csv_file_path}'.")
        print("All Done!")
