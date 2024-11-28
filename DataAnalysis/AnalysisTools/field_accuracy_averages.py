import re
from Utilities import utility

GROUND_TRUTH_FILENAME = "First100BryophytesTyped.csv"
ACCURACY_RESULTS_FILENAME = "multi_agreement_gpt_sonnet_gemini.csv"
AVERAGES_RESULTS_FILENAME = "gpt_sonnet_gemini_field_averages.csv"
SOURCE_PATH = "AutomaticAnalysis/SourcesForPaper/"
RESULTS_PATH = "AutomaticAnalysis/ResultsForSCSE/"
FIELDS = []

def set_fields_from_ground_truth(results_sample):
    ground_truth_sample = utility.get_contents_from_csv(SOURCE_PATH+GROUND_TRUTH_FILENAME)[0]
    for fieldname in results_sample:
        if fieldname in ground_truth_sample:
            FIELDS.append(fieldname)

def extract_data(string_data):
    return re.findall(r"[0-9.]+", string_data) 

def calculate_averages(d):
    return {fieldname: data[0]/data[1] if data[1] != 0 else "N/A" for fieldname, data in d.items()}          

def get_averages(results_dicts):
    d = {fieldname: [0,0] for fieldname in FIELDS}
    for run in results_dicts:
        for fieldname in FIELDS:
            data = extract_data(run[fieldname])
            num_true_applicable, __, num_applicable_targets = data
            d[fieldname][0] += int(num_true_applicable)
            d[fieldname][1] += int(num_applicable_targets)
    return calculate_averages(d)        
                


def main():
    results_dicts = utility.get_contents_from_csv(RESULTS_PATH+ACCURACY_RESULTS_FILENAME)
    set_fields_from_ground_truth(results_dicts[0])
    averages_dict = get_averages(results_dicts)
    utility.save_to_csv(RESULTS_PATH+AVERAGES_RESULTS_FILENAME, [averages_dict])


if __name__ == "__main__":
    main()            
