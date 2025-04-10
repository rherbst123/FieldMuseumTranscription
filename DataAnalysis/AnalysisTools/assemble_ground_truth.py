import re
import csv

def get_contents_from_csv(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8', newline='') as csvfile:
        return list(csv.DictReader(csvfile)) 

def save_to_csv(csv_file_path, data):
    fields = list(data[0].keys())
    with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def get_image_name_from_url(url):
    image_name = url.split('/')[-1].split('.')[0].split('_')[0]
    #print(f"image_name: {image_name}")
    return image_name      

def find_matching_dict(dict_list, image_url):
    url_image_name = get_image_name_from_url(image_url)
    for d in dict_list:
        gt_image_name = get_image_name_from_url(d['accessURI'])
        url_image_name = get_image_name_from_url(image_url)
        if d['accessURI'] == image_url or gt_image_name == url_image_name:
            return d, None
    return None, url_image_name 


def get_contents_from_txt(txt_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        return f.read()     

def assemble_ground_truth(ground_truth_file_path, images_file_path):
    ground_truth_dicts = get_contents_from_csv(ground_truth_file_path)
    raw_images = get_contents_from_txt(images_file_path)
    images_list = [l.strip() for l in raw_images.splitlines()]
    new_ground_truth_dicts = []
    for image_url in images_list:
        matching_dict, not_found_image_name = find_matching_dict(ground_truth_dicts, image_url)
        if matching_dict:
            new_ground_truth_dicts.append(matching_dict)
        else:
            print(f"No match found for URL: {image_url} or the image name {not_found_image_name}")
    return new_ground_truth_dicts

def run(ground_truth_file_path, images_file_path, output_file_path):
    new_ground_truth_dicts = assemble_ground_truth(ground_truth_file_path, images_file_path)
    save_to_csv(output_file_path, new_ground_truth_dicts)   

if __name__ == "__main__":
    ground_truth_file_path = 'DataAnalysis/GroundTruths/300-mixed_families-202-fully_typed-20-label_only.csv'
    images_file_path = 'DataAnalysis/DataSets/trillo-dataset.txt'
    output_file_path = 'DataAnalysis/GroundTruths/20-mixed-trillo.csv'
    run(ground_truth_file_path, images_file_path, output_file_path)                 