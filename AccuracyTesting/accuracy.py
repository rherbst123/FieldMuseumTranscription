import csv
import re

SKIP_LIST = ['Image Name', 'catalogNumber', 'Dataset Source', 'accessURI', 'Label only?', 'modifiedBy', 'verifiedBy' , 'substrate', 'URL']
CORE_FIELDS_LIST = []


### SUBSTITUTE YOUR FILENAMES BELOW
# sources and filenames should be bare; no folder name and no extension name
LLM_SPREAD_SOURCES = []#  "spread08.02.1600.1.1Stripped", "spread08.02.1600.1.2Stripped", "spread08.02.1600.1.3Stripped", "spread08.02.1600.1.4StrippedPrompt", "spread08.02.1600.1.5Stripped", "Spread08.06.1000.1.5Stripped"# "Spread_6_11_1050", "Spread_6_11_1110", "Spread_6_12_1404", "Spread_6_12_1440"#
GROUND_TRUTH_FILENAME = "" # First100BryophytesTyped # First25BryophytesTyped
RESULT_FILENAME = ""
# path wrappers are used to add folder location and add extension names
# data can be read or saved to a diffeent folder by changing the wrapper
SOURCE_PATH_WRAPPER = "Outputs/%s.csv"    # AccuracyTesting/AccuracyTestingSources/
RESULTS_PATH_WRAPPER = "AccuracyTesting/AccuracyTestingResults/%s.csv"


def get_contents_from_csv(fname):
    with open(fname, 'r', encoding='utf-8', newline='') as csvfile:
        return list(csv.DictReader(csvfile)) 

def save_to_csv(csv_file_path, data):
    fields = list(data[0].keys())
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data) 

# remove fields before comparison
def remove_skipped_fields(d: dict):
    return {key: val for key, val in d.items() if key not in SKIP_LIST} 

# use only core fields for comparison
def get_core_fields_only(d: dict):
    return {key: val for key, val in d.items() if key in CORE_FIELDS_LIST}

# this function determines whether to use core fields or just skip select fields
# core fields and skipped fields are set at the top
def get_fields_to_be_compared(d:dict):
    return remove_skipped_fields(d)   
    # return get_core_fields_only(d)      

# future home of Mr Levenshtein and his REGEX regulars
def get_weight(s1, s2):
    return 0

# returns 1 if there is a match
# returns the value of the get_weight() function if there is no match 
def is_match(val1, val2):
    return val1.strip().lower() == val2.strip().lower() or get_weight(val1, val2)

# accuracy calculated only for those valid ground truth targets (i.e., not an "N/A")
def calculate_accuracy_valid_targets(master_results_dict, num_valid_targets, num_matches):
    master_results_dict["number valid targets"] = num_valid_targets
    master_results_dict["matches"] = num_matches
    master_results_dict["accuracy: valid fields"] = num_matches/num_valid_targets
    return master_results_dict                                 

def compare_and_tally(transcription_dicts, ground_truth_dicts, comparison_results_dict):
    num_matches = 0
    num_targets = 0
    for tr_dict, gr_truth_dict in zip(transcription_dicts, ground_truth_dicts):
        for fieldname, grtruth_val in gr_truth_dict.items():
            if not is_match(grtruth_val, "N/A"):
                # increment the number of overall valid ground truth targets
                num_targets += 1
                # increment the "out of" for the given field in the results dictionary
                comparison_results_dict[fieldname][1] += 1 
                if is_match(tr_dict[fieldname], grtruth_val):
                    # increment the number of overall matches to valid ground truth targets  
                    num_matches +=1
                    # increment the number of "hits" to given filed in the results dictionary
                    comparison_results_dict[fieldname][0] += 1
            elif is_match(tr_dict[fieldname], "N/A"):
                # just in case there is not a valid target (i.e., "N/A" in the ground truth)
                   # and the llm still transcribes "N/A", the number of overall targets will still be incremented.
                     # for this reason, the number of targets does depend on the llm run
                #num_targets += 1    # uncommenting this will significantly increase the number of targets
                pass              
    return comparison_results_dict                   

def process(run_spreadname, ground_truth_dicts, blank_results_dict):
    saved_results: list[dict] = get_contents_from_csv(SOURCE_PATH_WRAPPER%run_spreadname)
    transcription_dicts = [get_fields_to_be_compared(d) for d in saved_results]
    tallied_results_dict = compare_and_tally(transcription_dicts, ground_truth_dicts, blank_results_dict)  
    return calculate_accuracy_valid_targets(tallied_results_dict, num_targets, num_matches) 

def main(run_spreadnames=LLM_SPREAD_SOURCES): 
    reference_dicts: list[dict] = get_contents_from_csv(SOURCE_PATH_WRAPPER%GROUND_TRUTH_FILENAME)
    ground_truth_dicts: list[dict] = [get_fields_to_be_compared(d) for d in reference_dicts]
    master_results = []                    
    for spreadname in run_spreadnames:
        blank_results_dict =           \
            {"run": spreadname} | {fieldname: [0,0] for fieldname in ground_truth_dicts[0] if fieldname not in SKIP_LIST}
        master_results += [process(spreadname, ground_truth_dicts, blank_results_dict)]
    save_to_csv(RESULTS_PATH_WRAPPER%RESULT_FILENAME, master_results)   
    
if __name__ == "__main__":
    main()