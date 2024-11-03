
import utility

SOURCE_PATH = "AutomaticAnalysis/SourcesForPaper/"
RESULTS_PATH = "AutomaticAnalysis/ResultsForPaper/"
FILENAMES =  [
              ["Spread_6_11_1050.csv", "Spread_6_11_1110.csv",],
              ["Spread_6_12_1404.csv", "Spread_6_12_1440.csv",],
              ["SpreadJun.20.24.0153.csv", "SpreadJun.26.24.1108.csv",],
              ["SpreadJun.21.24.1043.csv", "SpreadJun.26.24.1050.csv"]]
GROUND_TRUTH_FILENAME = "First100BryophytesTyped.csv"
RESULTS_FILENAME = "100_bryophytes_variability_verification.csv"
SKIP_LIST = ["Image Name", "catalogNumber", "Dataset Source", "accessURI", "Label only?", "modifiedBy", "verifiedBy" , "substrate", "URL", "Image"]

def save_results(fname, results: list[dict]):
    utility.save_to_csv(fname, results) 

def calculate_variability(matchValid, matchNonValid, nonMatchValid, nonMatchNonValid):
    return  1 - matchValid / (matchValid+nonMatchValid+nonMatchNonValid)       

def is_match(s1, s2):
    return s1.strip().lower() == s2.strip().lower()

def is_valid(s1):
    return s1.strip().lower() == "N/A".strip().lower()    

def compare_differences(transcriptionsA, transcriptionsB, true_value_dicts):
    matchValid, matchNonValid, nonMatchValid, nonMatchNonValid = 0,0,0,0
    for transcriptA, transcriptB, true_value_dict in zip(transcriptionsA, transcriptionsB, true_value_dicts):

        for fieldname, valA in transcriptA.items():
            valB = transcriptB[fieldname]
            true_val = true_value_dict[fieldname]
            is_valid_target = is_valid(true_val)
            is_a_match = is_match(valA, valB)
            matchValid += is_valid_target and is_a_match 
            matchNonValid += not is_valid_target and is_a_match 
            nonMatchValid += is_valid_target and not is_a_match
            nonMatchNonValid += not is_valid_target and not is_a_match
            
    return calculate_variability(matchValid, matchNonValid, nonMatchValid, nonMatchNonValid)    

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
    transcriptionsA, transcriptionsB, true_value_dicts = get_results_to_be_compared(filenameA, filenameB)
    variability = compare_differences(transcriptionsA, transcriptionsB, true_value_dicts)
    formatted = {"runA": filenameA, "runB": filenameB, "variability": variability}
    return formatted

def main(logger):
    all_results = []
    for filelist in FILENAMES:
        for idx, filenameA in enumerate(filelist):
            for filenameB in filelist[idx+1:]:
                all_results += [process(filenameA, filenameB)]            
    save_results(RESULTS_PATH+RESULTS_FILENAME, all_results)
    print(f"Yay!!! {RESULTS_FILENAME} saved!")         

if __name__ == "__main__":
    logger = utility.get_logger()
    main(logger)
    