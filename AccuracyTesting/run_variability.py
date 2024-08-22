import utility
import statistics

SOURCE_PATH = "AccuracyTesting/AccuracyTestingSources/"
RESULTS_PATH = "AccuracyTesting/AccuracyTestingResults/"

FILENAMES = [["Spread_6_11_1050.csv", "Spread_6_11_1110.csv"], ["Spread_6_12_1404.csv", "Spread_6_12_1440.csv"],  ["Spread_6_11_1050_Spread_6_12_1404_agreed_values.csv", "Spread_6_11_1050_Spread_6_12_1440_agreed_values.csv", "Spread_6_11_1110_Spread_6_12_1404_agreed_values.csv", "Spread_6_11_1110_Spread_6_12_1440_agreed_values.csv"]]
GROUND_TRUTH_FILENAME = "First100BryophytesTyped.csv"
RESULTS_FILENAME = "variation.csv"

SKIP_LIST = ["Image Name", "catalogNumber", "Dataset Source", "accessURI", "Label only?", "modifiedBy", "verifiedBy" , "substrate", "URL", "Image"]

def save_results(fname, results: list[dict]):
    utility.save_to_csv(fname, results)    

def calculate_variability(field_counts_dict, sum_dict):
    var_dict = {"ratio diff:all": sum_dict["sum differences(A,B)"] / sum_dict["sum all"], 
                "ratio diff:non-N/A": sum_dict["sum differences(A,B)"] / sum_dict["sum non-N/A"]}
    return field_counts_dict | sum_dict | var_dict

def sum_differences_and_targets(d):
    return {"sum differences(A,B)": sum([val[0] for val in d.values()]), 
            "sum all": sum([val[1] for val in d.values()]), 
            "sum non-N/A": sum([val[2] for val in d.values()])}     

def is_different(s1, s2):
    return s1.strip().lower() != s2.strip().lower()

def compare_differences(transcriptionA, transcriptionB, field_counts_dict, true_value_dicts):
    for itemsA, itemsB, tr_val_items in zip(transcriptionA.items(), transcriptionB.items(), true_value_dicts.items()):
        fieldnameA, valA, fieldnameB, valB, fieldname, true_val = *itemsA, *itemsB, *tr_val_items
        if valA=="PASS" and valB=="PASS":
            continue
        field_counts_dict[fieldname][0] += is_different(valA, valB)
        field_counts_dict[fieldname][1] += fieldnameA==fieldnameB
        field_counts_dict[fieldname][2] += fieldnameB==fieldnameB and true_val != "N/A"
    return field_counts_dict    

def get_blank_counts_dict(result_sample):
    return {key: [0,0,0] for key in result_sample}

def get_fields_to_be_compared(d):
    return {key: val for key, val in d.items() if key not in SKIP_LIST}

def get_results_to_be_compared(filenameA, filenameB): 
    runA: list[dict] = utility.get_contents_from_csv(SOURCE_PATH+filenameA)
    runB: list[dict] = utility.get_contents_from_csv(SOURCE_PATH+filenameB)
    reference_dicts: list[dict] = utility.get_contents_from_csv(SOURCE_PATH+GROUND_TRUTH_FILENAME)

    resultsA = [get_fields_to_be_compared(transcription) for transcription in runA]
    resultsB = [get_fields_to_be_compared(transcription) for transcription in runB]
    true_value_dicts = [get_fields_to_be_compared(d) for d in reference_dicts]
    return resultsA, resultsB, true_value_dicts   

def process(filenameA, filenameB):
    resultsA, resultsB, true_value_dicts = get_results_to_be_compared(filenameA, filenameB)
    field_counts_dict = get_blank_counts_dict(resultsA[0]) 
    for transcriptionA, transcriptionB, tr_val_dict in zip(resultsA, resultsB, true_value_dicts):
        field_counts_dict = compare_differences(transcriptionA, transcriptionB, field_counts_dict, tr_val_dict)
    sum_dict = sum_differences_and_targets(field_counts_dict) 
    master_differences_dict = calculate_variability(field_counts_dict, sum_dict)
    result = {"run A": filenameA, "run B": filenameB} | master_differences_dict
    return result

def main():
    all_results = []
    for filelist in FILENAMES:
        for idx, filenameA in enumerate(filelist):
            for filenameB in filelist[idx+1:]:
                all_results += [process(filenameA, filenameB)]  
    save_results(RESULTS_PATH+RESULTS_FILENAME, all_results)
    print(f"Yay!!! {RESULTS_FILENAME} saved!")         

if __name__ == "__main__":
    main()
    