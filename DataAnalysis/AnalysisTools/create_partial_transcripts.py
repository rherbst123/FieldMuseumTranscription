import csv
import re
from Utilities import text_to_dict_via_prompt

def read_csv(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8', newline='') as csvfile:
        return list(csv.DictReader(csvfile)) 

def save_to_csv(csv_file_path, data):
    fields = list(data[0].keys())
    with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

def read_from_txt(txt_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        return f.read()             

def is_missing_row(row, fieldnames):
    return not any(row[field] for field in fieldnames)

def create_partial_transcripts(trillo_data, gpt_data, ground_truth_data, fieldnames):
    partial_trillo_data = []
    partial_gpt_data = []
    partial_ground_truth_data = []
    num_missing_rows = 0
    for trillo_row, gpt_row, ground_truth_row in zip(trillo_data, gpt_data, ground_truth_data):
        if is_missing_row(trillo_row, fieldnames) or is_missing_row(gpt_row, fieldnames):
            print(f"missing row: {trillo_row = }, {gpt_row = }")
            num_missing_rows += 1
            continue
        partial_trillo_data.append(trillo_row)
        partial_gpt_data.append(gpt_row)
        partial_ground_truth_data.append(ground_truth_row)
    print(f"num missing rows: {num_missing_rows}")     
    return partial_trillo_data, partial_gpt_data, partial_ground_truth_data       

def save_partial_transcripts(partial_trillo_data, partial_gpt_data, partial_ground_truth_data):
    save_to_csv("DataAnalysis/Trillo/Transcriptions/partial-18-mixed-trillo-transcriptions.csv", partial_trillo_data)
    save_to_csv("DataAnalysis/Trillo/Transcriptions/partial-gpt-4o-2025-04-18-2319-transcriptions.csv", partial_gpt_data)
    save_to_csv("DataAnalysis/GroundTruths/partial-18-mixed-trillo.csv", partial_ground_truth_data)

def main(prompt_filename, trillo_filename, gpt_filename, ground_truth_filename):
    trillo_data = read_csv(trillo_filename)
    gpt_data = read_csv(gpt_filename)
    ground_truth_data = read_csv(ground_truth_filename)
    prompt_text = read_from_txt(prompt_filename)
    fieldnames = text_to_dict_via_prompt.get_fieldnames_from_prompt(prompt_text) 
    partial_trillo_data, partial_gpt_data, partial_ground_truth_data = create_partial_transcripts(trillo_data, gpt_data, ground_truth_data, fieldnames)
    save_partial_transcripts(partial_trillo_data, partial_gpt_data, partial_ground_truth_data)

if __name__ == "__main__":
    prompt_filename = "Prompts/Prompt 1.5.4.txt" 
    trillo_filename = "DataAnalysis/Trillo/Transcriptions/18-mixed-trillo-transcriptions.csv"
    gpt_filename = "DataAnalysis/Trillo/Transcriptions/gpt-4o-2025-04-18-2319-transcriptions.csv"
    ground_truth_filename = "DataAnalysis/GroundTruths/18-mixed-trillo.csv"
    main(prompt_filename, trillo_filename, gpt_filename, ground_truth_filename)
