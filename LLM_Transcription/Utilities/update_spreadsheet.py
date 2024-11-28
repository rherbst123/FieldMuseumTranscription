import csv
import requests
import shutil
import tempfile
import urllib.request
import re
import sys

URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1eWkG6EW7PPWfCq6QGE7O5-m2p5VrMHQS1BOUMemqdCeM0RJHVe1c2su2Y1O7WKmEJdm_R0E1uNGR/pub?output=csv"

def get_contents_from_csv(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8', newline='') as csvfile:
        return list(csv.DictReader(csvfile)) 

def save_to_csv(csv_file_path, data, fields):
    print(f"{csv_file_path = }")
    print(f"{fields = }")
    print(f"{data = }")
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
        saved_data: list[dict] = download_csv_contents(URL)
        fields = get_fieldnames_union(saved_data+data)
        print(f"{saved_data = }\n\n")
        print(f"{data =}\n\n")
        save_to_csv(csv_file_path, saved_data + data, fields)
    except FileNotFoundError:
        fields = list(data[0].keys())
        save_to_csv(csv_file_path, data, fields)

def download_csv_contents(url):
    with urllib.request.urlopen(url) as response:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            shutil.copyfileobj(response, tmp_file)
    with open(tmp_file.name, encoding = 'utf-8',newline='') as csvfile:
            return list(csv.DictReader(csvfile)) 
