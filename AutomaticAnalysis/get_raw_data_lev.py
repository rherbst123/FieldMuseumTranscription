import utility
from string_distance import WeightedLevenshtein
WL = WeightedLevenshtein({"INSERT_CHAR_COSTS": [[]], "DELETE_CHAR_COSTS": [[]], "SUBSTITUTION_CHAR_COSTS": [[]]})

SOURCE_PATH = "AccuracyTesting/AccuracyTestingSources/"
RESULTS_PATH = "AccuracyTesting/AccuracyTestingResults/"

FILENAMES = ["Spread_6_11_1050.csv", "Spread_6_11_1110.csv", "Spread_6_12_1404.csv", "Spread_6_12_1440.csv"]
GROUND_TRUTH_FILENAME = "First100BryophytesTyped.csv"

# Enter below the filename to which results should be saved. The file will be saved to the RESULTS_PATH directory listed above
RESULTS_FILENAME = "spread_for_correct_field_identification.csv"
SKIP_LIST = ["Image Name", "catalogNumber", "Dataset Source", "accessURI", "Label only?", "modifiedBy", "verifiedBy" , "substrate", "URL", "Image"]

RECORD_REF_FIELDNAME = "accessURI"

def save_results(fname, results: list[dict]):
    utility.save_to_csv(fname, results) 

def get_edit_distance(false_pos, false_neg, observed_val, true_val):
        if observed_val == "N/A" or false_neg:   # don't bother getting the edit distance when the observed value is "N/A"; just return 1
            return max([len(observed_val), len(true_val)]), 1       
        else:
            return WL.get_edit_distance(observed_val, true_val), WL.calculate_weighted_difference(observed_val, true_val)

def istrue(observed_val, true_val):
        return observed_val.lower() == true_val.lower()

def is_positive(val):
        return val != "N/A"

def get_comparisons(fieldname, observed_val, true_val, record_ref):
    is_pos = is_positive(true_val)
    is_true = istrue(observed_val, true_val)
    true_pos = is_pos and is_true
    true_neg = not is_pos and is_true
    false_pos = is_pos and not is_true
    false_neg = not is_pos and not is_true
    if true_pos or true_neg:
        return None
    edit_distance, edit_distance_scaled = get_edit_distance(false_pos, false_neg, observed_val, true_val)
    return {"record_ref": record_ref, "fieldname": fieldname, "observed_val": observed_val, "true_val": true_val, "edit_distance": edit_distance, "edit_distance_scaled": edit_distance_scaled}

def compare_and_compile(observed_values_dicts, true_values_dicts, record_refs):
    all_field_comparisons = []
    for record_ref, observed_values_dict, true_values_dict in zip(record_refs, observed_values_dicts, true_values_dicts):
        for fieldname, observed_val in observed_values_dict.items():
            if observed_val == "PASS" or observed_val.lower().strip() == "unsure and check":
                continue  # Just in case the LLM doesn't hazard a guess,
                                # or there are gaps in some of the fields of observed values.
                                # This is used when runs are compared for agreement
                                    #  and only agreed values are to be compared against true values
            true_val = true_values_dict[fieldname]
            field_comparison_dict = get_comparisons(fieldname, observed_val, true_val, record_ref) 
            if field_comparison_dict:
                all_field_comparisons += [field_comparison_dict  | {"is this field": "     "} ]
    return all_field_comparisons

def get_fields_to_be_compared(d):
    return {key: val for key, val in d.items() if key not in SKIP_LIST}

def get_record_refs(reference_dicts):
    return [ref_dict[RECORD_REF_FIELDNAME] for ref_dict in reference_dicts]     

def get_results_to_be_compared(filename): 
    run: list[dict] = utility.get_contents_from_csv(SOURCE_PATH+filename)
    reference_dicts: list[dict] = utility.get_contents_from_csv(SOURCE_PATH+GROUND_TRUTH_FILENAME)
    record_refs = get_record_refs(reference_dicts)
    observed_values_dicts = [get_fields_to_be_compared(transcription) for transcription in run]
    true_value_dicts = [get_fields_to_be_compared(d) for d in reference_dicts]
    return observed_values_dicts, true_value_dicts, record_refs 

def process(filename):
    observed_values_dicts, true_value_dicts, record_refs = get_results_to_be_compared(filename) 
    all_fields_dict = compare_and_compile(observed_values_dicts, true_value_dicts, record_refs) 
    return all_fields_dict

def remove_edit_distance(all_results):
    for r in all_results:
        r.pop("edit_distance")
        r.pop("edit_distance_scaled")    
    return all_results   

def main():
    all_results = []
    for filename in FILENAMES:
        all_results += process(filename)     
    save_results(RESULTS_PATH+RESULTS_FILENAME, all_results)
    print(f"Yay!!! {RESULTS_FILENAME} saved!")
    FILENAME = "fillable_" + RESULTS_FILENAME
    mod_results = remove_edit_distance(all_results)
    save_results(RESULTS_PATH+FILENAME, mod_results)
    print(f"Yay!!! {FILENAME} saved!")




if __name__ == "__main__":
    main()