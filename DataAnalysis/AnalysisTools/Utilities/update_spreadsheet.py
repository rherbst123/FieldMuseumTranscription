import csv

def get_contents_from_csv(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8', newline='') as csvfile:
        return list(csv.DictReader(csvfile)) 

def save_to_csv(csv_file_path, data, fields):
    with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

def get_fieldnames_union(dicts_in: list[dict]):
    fields = []
    for d in dicts_in:
        fields += [key for key in d.keys() if key not in fields]
    return fields            

def append_to_csv(csv_file_path, data):
    try:
        saved_data: list[dict] = get_contents_from_csv(csv_file_path)
        fields = get_fieldnames_union(saved_data+data)
        save_to_csv(csv_file_path, saved_data + data, fields)
    except FileNotFoundError:
        fields = list(data[0].keys())
        save_to_csv(csv_file_path, data, fields)    

