import csv
import json
import re


def get_contents_from_csv(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8', newline='') as csvfile:
        return list(csv.DictReader(csvfile)) 

def save_to_csv(csv_file_path, data):
    fields = list(data[0].keys())
    with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

def remove_csv_extension(fname):
        return re.match("(.+).csv", fname).group(1)



# currently just rounds floats in lists so all numeric values can be seen in spreadsheet column
def format_values(d: dict):
    return {key: [round(v, 1) if type(v)==float else v for v in val]  if type(val)==list else val for key, val in d.items()}
    #return {key: "|".join(val)  if type(val)==list else val for key, val in d.items()}         

def save_errors(txt_filepath, errors: list[dict], spreadsource, record_ref_fieldname, comparison_config, edit_distance_config, tolerances_config):
    errors = list(filter(None, errors))
    temp = {}
    for d in errors:
        record_ref = d["ref"]  
        fieldname = d["fieldname"]
        observed_val = d["observed_val"]
        true_val = d["true_val"]
        gradedFA = round(d["graded_false_app"], 2)
        listing = f"{record_ref}, {gradedFA = }: {observed_val}___{true_val}"
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