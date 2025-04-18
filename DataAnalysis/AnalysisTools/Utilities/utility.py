import csv
import json
import re
import yaml
import logging
import time

def striplines(text):
    return [s.strip() for s in text.splitlines()]
    

def get_fieldnames_from_prompt(prompt_text):
    prompt_text = "\n".join(striplines(prompt_text))
    fieldnames = re.findall(r"(^\w+):", prompt_text, flags=re.MULTILINE)
    return fieldnames

def get_contents_from_csv(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8', newline='') as csvfile:
        return list(csv.DictReader(csvfile)) 

def save_to_csv(csv_file_path, data):
    fields = list(data[0].keys())
    with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

def get_contents_from_txt(txt_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        return f.read() 

def save_to_txt(text_file_path, data):
    with open(text_file_path, 'w', encoding='utf-8') as f:
        f.write(data)       

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def remove_csv_extension(fname):
    return re.match("(.+).csv", fname).group(1)

def load_yaml(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.SafeLoader) 

def get_logger():
        logger = logging.getLogger()
        logging.basicConfig(filename="DataAnalysis/AnalysisTools/Logs/analysis.log", format='%(asctime)s %(name)s %(funcName)s %(levelname)s: %(message)s',level=logging.DEBUG, encoding = "UTF-8")
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        console_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(funcName)s - %(message)s'))
        return logger                   



# currently just rounds floats in lists so all numeric values can be seen in spreadsheet column
def format_values(d: dict):
    if not d:
        return {}
    return {key: [round(v, 1) if type(v)==float else v for v in val]  if type(val)==list else val for key, val in d.items()}
    #return {key: "|".join(val)  if type(val)==list else val for key, val in d.items()}         

def save_errors(txt_filepath, errors: list[dict], spreadsource, record_ref_fieldname, comparison_config, edit_distance_config, tolerances_config):
    errors = list(filter(None, errors))
    temp = {}
    for d in errors:
        record_ref = d["ref"]  
        fieldname = d["fieldname"]
        transcription_val = d["transcription_val"]
        target_val = d["target_val"]
        gradedNoMatchValid = round(d["gradedNoMatchValid"], 2)
        listing = f"{record_ref}, {gradedNoMatchValid = }: {transcription_val}___{target_val}"
        if fieldname in temp:
            temp[fieldname] += [listing]
        else:
            temp[fieldname] = [listing]    
    out = f"{spreadsource = }\n\n"
    for fieldname, val in temp.items():
        out += f"{fieldname}: {len(val)}\n\n"  
        out += "\n".join(val) + "\n\n" 
    out += 50*"-" + "\n\n"
    try:
        with open(txt_filepath, "r", encoding="utf-8") as f:
            prior = f.read()
    except FileNotFoundError:
        prior = ""
    with open(txt_filepath, "w", encoding="utf-8") as f:
        f.write(f"{prior}\n{comparison_config = }\n{edit_distance_config = }\n{tolerances_config = }\n\n\n{out}")  

def get_timestamp():
    return time.strftime("%Y-%m-%d-%H%M") 

def get_run_name(modelname):
    return f"{modelname}-{get_timestamp()}"

def extract_run_name_from_filepath(filepath):
        timestamp_pattern = r"\d\d\d\d-\d\d-\d\d-\d\d\d\d"
        mtch = re.search(fr".*/(.+-{timestamp_pattern})-.+", filepath)
        return mtch.group(1)        

                                    