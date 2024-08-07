import csv
import re

SKIP_LIST = ['Image Name', 'catalogNumber', 'Dataset Source', 'accessURI', 'Label only?', 'modifiedBy', 'verifiedBy', 'substrate']

def get_csv_contents(fname):
    with open(fname, 'r', encoding='utf-8', newline='') as csvfile:
        return list(csv.DictReader(csvfile)) 

def filter_out_skips(d: dict):
    return {fieldname: val for fieldname, val in d.items() if fieldname not in SKIP_LIST}

def get_counts_regex(data, string_in):
    return len(re.findall(string_in.strip(), str(data)))

def get_counts_iterate(data: list[dict], string_in):
    count = 0
    for d in data:
        for elem in d.values():
            if elem.strip()==string_in.strip():
                count += 1
    return count  


def main(ground_truth_filepath, llm_output_filepath):
    ground_truth_data: list[dict] = get_csv_contents(ground_truth_filepath)
    ground_truth_data_filtered = [filter_out_skips(l) for l in ground_truth_data]
    llm_run_data: list[dict] = get_csv_contents(llm_output_filepath)
    llm_run_data_filtered = [filter_out_skips(l) for l in llm_run_data]
    s = "N/A"
    gtruth_counts_regex = get_counts_regex(ground_truth_data, s)
    gtruth_counts_iterated = get_counts_iterate(ground_truth_data, s)
    llm_run_counts_regex = get_counts_regex(llm_run_data, s)
    llm_run_counts_iterated = get_counts_iterate(llm_run_data, s)
    print(f"{gtruth_counts_regex = }, {gtruth_counts_iterated = }")
    print(f"{llm_run_counts_regex = }, {llm_run_counts_iterated = }")
    filtered_gtruth_counts_regex = get_counts_regex(ground_truth_data_filtered, s)
    filtered_gtruth_counts_iterated = get_counts_iterate(ground_truth_data_filtered, s)
    filtered_llm_run_counts_regex = get_counts_regex(llm_run_data_filtered, s)
    filtered_llm_run_counts_iterated = get_counts_iterate(llm_run_data_filtered, s)
    print(f"{filtered_gtruth_counts_regex = }, {filtered_gtruth_counts_iterated = }")
    print(f"{filtered_llm_run_counts_regex = }, {filtered_llm_run_counts_iterated = }")



if __name__ == "__main__":
    ground_truth_filepath = "AccuracyTesting/AccuracyTestingSources/First100BryophytesTyped.csv"
    llm_output_filepath = "AccuracyTesting/AccuracyTestingSources/Spread_6_12_1404.csv"
    main(ground_truth_filepath, llm_output_filepath)