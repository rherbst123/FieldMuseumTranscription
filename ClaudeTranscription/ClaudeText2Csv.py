import csv
import re

def extract_info_from_text(text):
    regex_patterns = {
        'Image Name': r"Image Name:\s*(.+?)\n",
        'verbatimCollectors': r"verbatimCollectors\s*:\s*(.+?)\n",
        'collectedBy': r"collectedBy\s*:\s*(.+?)\n",
        'secondaryCollectors': r"secondaryCollectors\s*:\s*(.+?)\n",
        'recordNumber': r"recordNumber\s*:\s*(.+?)\n",
        'verbatimEventDate': r"verbatimEventDate\s*:\s*(.+?)\n",
        'minimumEventDate': r"minimumEventDate\s*:\s*(.+?)\n",
        'maximumEventDate': r"maximumEventDate\s*:\s*(.+?)\n",
        'verbatimIdentification': r"verbatimIdentification\s*:\s*(.+?)\n",
        'latestScientificName': r"latestScientificName\s*:\s*(.+?)\n",
        'identifiedBy': r"identifiedBy\s*:\s*(.+?)\n",
        'verbatimDateIdentified': r"verbatimDateIdentified\s*:\s*(.+?)\n",
        'associatedTaxa': r"associatedTaxa\s*:\s*(.+?)\n",
        'country': r"country\s*:\s*(.+?)\n",
        'firstPoliticalUnit': r"firstPoliticalUnit\s*:\s*(.+?)\n",
        'secondPoliticalUnit': r"secondPoliticalUnit\s*:\s*(.+?)\n",
        'municipality': r"municipality\s*:\s*(.+?)\n",
        'verbatimLocality': r"verbatimLocality\s*:\s*(.+?)\n",
        'locality': r"locality\s*:\s*(.+?)\n",
        'habitat': r"habitat\s*:\s*(.+?)\n",
        'substrate': r"substrate\s*:\s*(.+?)\n",
        'verbatimElevation': r"verbatimElevation\s*:\s*(.+?)\n",
        'verbatimCoordinates': r"verbatimCoordinates\s*:\s*(.+?)\n",
        'otherCatalogNumbers': r"otherCatalogNumbers\s*:\s*(.+?)\n",
        'originalMethod': r"originalMethod\s*:\s*(.+?)\n",
        'typeStatus': r"typeStatus\s*:\s*(.+?)\n",
        'URL': r"URL:\s*(.+?)\n",
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

    entries = re.split(r'Image Name: ', contents)[1:]

    data = []
    for entry in entries:
        entry_info = extract_info_from_text('Image Name: ' + entry)
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
    input_file_path = "input.txt"
    output_csv_file_path = "output.csv"

    extracted_data = process_file(input_file_path)
    if extracted_data:
        export_to_csv(extracted_data, output_csv_file_path)
        print(f"Data exported to '{output_csv_file_path}'.")
        print("All Done!")
