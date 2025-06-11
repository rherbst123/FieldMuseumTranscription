import csv
import re

def read_dicts_from_csv(fname):
    with open(fname, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def save_to_csv(csv_file_path, data):
    #clean_data(data)
    print(f"{len(data) = }")
    fields = list(data[0].keys())
    with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)        

def get_image_name_from_url(url):
    return url.split("/")[-1]          

def reorder_dicts_by_key(sorted_dicts, unsorted_dicts):
    print(f"{len(sorted_dicts) = }, {len(unsorted_dicts) = }")
    reordered_dicts = []
    images_to_account_for = []
    accounted_for_images = []
    begins_with_C = []
    begins_with_V = []
    for ud in unsorted_dicts:
        if ud["docName"].startswith("C"):
                begins_with_C.append(ud["docName"])
        elif ud["docName"].startswith("V"):
            begins_with_V.append(ud["docName"])  
    for sd in sorted_dicts:
        image_name = sd["imageName"]
        images_to_account_for.append(image_name)
        for ud in unsorted_dicts:  
            if ud["docName"].startswith("V") and image_name in ud["docName"]:
                reordered_dicts.append(ud)
                accounted_for_images.append(image_name)
                break
    print(f"{len(accounted_for_images) = }, {len(images_to_account_for) = }, {len(begins_with_C) = }, {len(begins_with_V) = }")
    print(f"{accounted_for_images = }")
    print(f"{images_to_account_for = }")
    print(f"{begins_with_C = }")
    print(f"{begins_with_V = }")

    for image_name in images_to_account_for:
        if image_name not in accounted_for_images:
            print(f"missing: {image_name = }")
    return reordered_dicts
        
def sort_dict_by_fieldnames(d, fieldnames):
    return {fieldname: d[fieldname] for fieldname in fieldnames}    

def sort_rows(sorted_fname, unsorted_fname, save_fname):
    sorted_dicts = read_dicts_from_csv(sorted_fname)
    sorted_dicts = clean_data(sorted_dicts)
    print(f"{len(sorted_dicts) = }")
    print(f"{sorted_dicts[1] = }")
    unsorted_dicts = read_dicts_from_csv(unsorted_fname)
    reordered_dicts = reorder_dicts_by_key(sorted_dicts, unsorted_dicts)
    save_to_csv(save_fname, reordered_dicts)
    save_to_csv("DataAnalysis/GroundTruths/12-trillo-flowering.csv", sorted_dicts)

def clean_data(data):
    out = []
    for idx, d in enumerate(data):
        #print(f"{idx = }")
        #print(f"{d = }\n\n")
        for key, val in d.items():
            print(f"{key = }, {val = }")
            if val=="":
                print(f"empty value for {key = }")
                d[key] = "N/A"
            elif type(val) == str:
                d[key] = re.sub(r"[\n\r\t]", " ", val)
        out.append(d)
    return out              

def sort_columns():
    pass 

def edit_spreadsheet():
    fname = "DataAnalysis/Trillo/Transcriptions/30-trillo-reformatted-transcriptions.csv"
    dicts = read_dicts_from_csv(fname)
    print(f"{len(dicts) = }")
    save_name = "DataAnalysis/Trillo/Transcriptions/33-trillo-reformatted-transcriptions.csv" 
    save_to_csv(save_name, dicts)  

def main():
    sorted_fname = "DataAnalysis/GroundTruths/12-trillo-flowering.csv"
    unsorted_fname = "DataAnalysis/Trillo/Transcriptions/30-trillo-reformatted-transcriptions.csv"
    save_fname = "DataAnalysis/Trillo/Transcriptions/12-trillo-flowering-transcriptions.csv"
    sort_rows(sorted_fname, unsorted_fname, save_fname) 

if __name__ == "__main__":
    main() 
    #edit_spreadsheet()                         