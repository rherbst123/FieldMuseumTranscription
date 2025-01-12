import re
import utility
from error_classification import ErrorClassifier

GROUND_TRUTH_FOLDER = "DataAnalysis/GroundTruths/"
SINGLE_COMPARISONS_FOLDER = "DataAnalysis/Comparisons/SingleComparisons/"
BATCH_COMPARISONS_FOLDER = "DataAnalysis/Comparisons/BatchComparisons/"
TRANSCRIPTIONS_FOLDER = "DataAnalysis/Transcriptions/"

def extract_data(string_data):
    return re.findall(r"[0-9.]+", string_data) 

def calculate_accuracy(numerator, denominator):
    return round(100*(numerator/denominator), 1) if denominator != 0 else "NaN"

def get_field_classified_errors_as_dict(fieldname, tallies_dict, error_combos_used):
    d = {}
    field_tallies = tallies_dict[fieldname]
    for key, val in field_tallies.items():
        if key in error_combos_used:
            d[key] = val        
    return d

    
def get_fields_classified_errors(run_name, fieldnames, ground_truth_filename):
    ec = ErrorClassifier(run_name, fieldnames)
    error_combos = ec.error_combos
    ec.setup_paths(ground_truth_filename)
    ec.setup_comparison_dicts()
    ec.iterate()
    tallies_dict = ec.tallies_dict
    error_combos_used = ec.error_combos_used
    all_fields_dict = {combo: 0 for combo in error_combos_used}
    run_dict = {}
    for fieldname in fieldnames:
        d = get_field_classified_errors_as_dict(fieldname, tallies_dict, error_combos_used)
        run_dict[fieldname] = d
        for combo, val in d.items():
            all_fields_dict[combo] += val 
    run_dict[f"all {len(fieldnames)} fields"] = all_fields_dict        
    run_dict["error_combos_used"] = error_combos_used    
    return run_dict 
    

def get_fields_classified_errors_batch_runs(run_names, fieldnames, ground_truth_filename):
    field_classified_errors_dicts = [get_fields_classified_errors(run_name, fieldnames, ground_truth_filename) for run_name in run_names]
    return field_classified_errors_dicts          
    
if __name__ == "__main__":
    run_name = "claude-3.5-sonnet-2024-08-02-1700-prompt1.5.2"
    fieldnames = ["collectedBy", "identifiedBy", "verbatimCollectors", "secondaryCollectors", "locality", "verbatimElevation"]
    ground_truth_filename = "100-bryophytes-typed.csv"
    r = get_fields_classified_errors(run_name, fieldnames, ground_truth_filename) 
    print(r)           
