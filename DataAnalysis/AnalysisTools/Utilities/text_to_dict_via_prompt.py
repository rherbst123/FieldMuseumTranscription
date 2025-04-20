import re
import csv

def save_to_csv(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def striplines(text):
    return [s.strip() for s in text.splitlines()]
    
def get_fieldnames_from_prompt(prompt_text):
    prompt_text = "\n".join(striplines(prompt_text))
    fieldnames = re.findall(r"(^\w+):", prompt_text, flags=re.MULTILINE)
    return fieldnames

def get_contents(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def convert_text_to_dict(text, fieldnames):
    mtch = re.search(r"(http.+?)\n", text)
    image_ref = mtch.group(1) if mtch else "Not found"
    result = {"accessURI": image_ref} | {fieldname: "" for fieldname in fieldnames}
    lines = striplines(text)
    
    for line in lines:
        for fieldname in fieldnames:
            if line.startswith(fieldname):
                result[fieldname] = line.split(":", 1)[1].strip()
    return result if any(result.values()) else {"error": text}        

def extract_info_from_text(text, prompt_name):
    print(f"{text = }")
    prompt_text = get_contents(f"Prompts/{prompt_name}")
    fieldnames = get_fieldnames_from_prompt(prompt_text)
    texts = re.split(r"==================================================", text)
    dict_list = [convert_text_to_dict(text, fieldnames) for text in texts]
    return dict_list

def dict_to_string(dictionary):
    result = ""
    for key, value in dictionary.items():
        result += f"{key}: {value}\n"
    return result.strip() 

def text_to_csv(text_fname, csv_filename, prompt_name="Prompt 1.5.4.txt"):
    contents = get_contents(text_fname)
    data = extract_info_from_text(contents, prompt_name)
    print(f"{data = }")
    save_to_csv(csv_filename, data)    

if __name__ == "__main__":
    text = "Here is the transcription and expansion of details from the herbarium label:\n\nverbatimCollectors: leg H Fleischer nr 3-2734\ncollectedBy: Fleischer\nsecondaryCollectors: N/A\nrecordNumber: 3-2734\nverbatimEventDate: 25 9 1903\nminimumEventDate: 1903-09-25\nmaximumEventDate: 1903-09-25\nverbatimIdentification: Macromitrium\nlatestScientificName: Macromitrium austraLieni\nidentifiedBy: N/A\nverbatimDateIdentified: N/A\nassociatedTaxa: N/A\ncountry: Australia\nfirstPoliticalUnit: Queensland\nsecondPoliticalUnit: N/A\nmunicipality: N/A\nverbatimLocality: Eumundi (ca 100 km nordlich Brisbane) Urwald\nlocality: Eumundi, about 100 km north of Brisbane\nhabitat: Urwald (primeval forest)\nsubstrate: N/A\nverbatimElevation: N/A\nverbatimCoordinates: N/A\notherCatalogNumbers: 1076713, 1044984\noriginalMethod: Typed\ntypeStatus: no type status"
    prompt_name = "Prompt 1.5.4.txt" 
    d = extract_info_from_text(text, prompt_name)
    print(d)      