# This script gets the accuracy of runs without all the bells and whistles of comparison_and_accuracy.py
# It is intended to verify the results of that script

from Utilities import utility
import re

SOURCE_PATH = "AutomaticAnalysis/SourcesForPaper/"
RESULTS_PATH = "AutomaticAnalysis/ResultsForPaper/"
RUN_FILENAMES1 = [
    #("SpreadMar12.0427.csv", "3.2", "GPT-4", "15_7_2024_Bryophytes_Typed - Stripped Ground Truth Batch 300.csv"),
   # ("SpreadMar27.1128.csv", "3.2", "GPT-4", "15_7_2024_Bryophytes_Typed - Stripped Ground Truth Batch 300.csv"),
    ("Spread_4_4(1.4StrippedPrompt).csv", "3.2", "GPT-4", "15_7_2024_Bryophytes_Typed - Stripped Ground Truth Batch 300.csv"),
    ("Spread_4_10_1334.csv", "3.3", "GPT-4", "Batch202.csv"),
    ("Spread_5_7_1356.csv", "3.4", "GPT-4", "78BryophytesTyped.csv"),
    ("Spread_5_7_1952.csv", "3.4", "GPT-4", "78BryophytesTyped.csv"),
   # ("SpreadJun.5.100Test.COLORIMAGES.csv", "3.5", "GPT4o", "7.5.2024 Jeff's Updated Copy of Batch 300 Testing chat gpt status, results and ground truth - GT100ImageEnhanceTest.csv"),
 #("SpreadJun.4.BWIMAGES.csv", "3.5", "GPT4o", "7.5.2024 Jeff's Updated Copy of Batch 300 Testing chat gpt status, results and ground truth - GT100ImageEnhanceTest.csv"),
    ("Spread_5_30_1139.csv", "3.6", "GPT-4", "First100BryophytesTyped.csv"),
 ("Spread_5_30_1025.csv", "3.6", "GPT-4", "First100BryophytesTyped.csv"),
  ("Spread_6_11_1050.csv", "3.7", "GPT4o", "First100BryophytesTyped.csv"),
   ("Spread_6_11_1110.csv", "3.7", "GPT4o", "First100BryophytesTyped.csv"),
    ("Spread_6_12_1404.csv", "3.8", "Opus", "First100BryophytesTyped.csv"),
     ("Spread_6_12_1440.csv", "3.8", "Opus", "First100BryophytesTyped.csv"),
      ("SpreadJun.20.24.0153.csv", "3.9", "Gemini", "First100BryophytesTyped.csv"),
       ("SpreadJun.26.24.1108.csv", "3.9", "Gemini", "First100BryophytesTyped.csv"),
        ("SpreadJun.21.24.1043.csv", "3.10", "Sonnet", "First100BryophytesTyped.csv"),
         ("SpreadJun.26.24.1050.csv", "3.10", "Sonnet", "First100BryophytesTyped.csv")]
RUN_FILENAMES2 = [ ("Spread_6_11_1050.csv", "3.11", "GPT4o", "First100BryophytesTyped.csv"),
   ("Spread_6_11_1110.csv", "3.11", "GPT4o", "First100BryophytesTyped.csv")]
RUN_FILENAMES3 = [ ("Spread_6_11_1050.csv", "3.11", "GPT4o", "First100BryophytesTyped.csv"),
   ("Spread_6_11_1110.csv", "3.11", "GPT4o", "First100BryophytesTyped.csv")]
RUN_FILENAMES4 = [("revSpreadMar12.0427_REVISED.csv", "3.2", "GPT-4", "15_7_2024_Bryophytes_Typed - Stripped Ground Truth Batch 300.csv"),
                    ("OutputJun.5.100Test.COLORIMAGES.csv", "3.5", "GPT4o", "100TestEnhancedImages.csv"),
                        ("OutputJun.5.100Test.BWIMAGES.csv", "3.5", "GPT4o", "100TestEnhancedImages.csv")]    
         
RESULT_FILENAME = "accuracy_method2_no_typeStatus.csv"
SKIP_LIST = ['PROV LARECAJA', "Image Name", "catalogNumber", "Dataset Source", "accessURI", "Label only?", "modifiedBy", "verifiedBy" , "substrate", "URL", "Image", "typeStatus"] 
CRITICAL_FIELDS = ["collectedBy", "secondaryCollectors", "collectionNumber", "minimumEventDate", "verbatimIdentification", "latestScientificName", "identifiedBy", "verbatimDateIdentified", "country", "firstPoliticalUnit", "secondPoliticalUnit", "municipality", "locality", "habitat", "verbatimElevation", "verbatimCoordinates", "otherCatalogNumbers"]
SKELETON_FIELDS = ["collectedBy", "collectionNumber", "minimumEventDate", "latestScientificName", "country"]

def format_results(spreadname, ref, model, results):
    return {"spreadname": spreadname, "ref": ref, "model": model} | results

def calculate_accuracy(tallies):
    mv = tallies["matchValid"]
    nmv = tallies["noMatchValid"]
    mnv = tallies["matchNotValid"]
    nmnv = tallies["noMatchNotValid"]
    all_targets = (mv+mnv) / (mv+nmv+mnv+nmnv)
    valid_targets = mv / (mv+nmv+nmnv)
    return {"accuracyValidTargets": valid_targets}

def update_tallies(tallies, is_valid_target, is_a_match):
    tallies["matchValid"] += is_a_match and is_valid_target
    tallies["noMatchValid"] += not is_a_match and is_valid_target
    tallies["matchNotValid"] += is_a_match and not is_valid_target
    tallies["noMatchNotValid"] += not is_a_match and not is_valid_target
    return tallies
    

def is_match(val1, val2):
    return val1.strip().lower() == val2.strip().lower()

def is_valid(val):
    return val.strip().lower() != "N/A".strip().lower()

def compare_and_tally(transcription_dicts, ground_truth_dicts):
    tallies = {"matchValid": 0, "noMatchValid": 0, "matchNotValid": 0, "noMatchNotValid": 0}
    for transcription_dict, ground_truth_dict in zip(transcription_dicts, ground_truth_dicts):
        for fieldname, ground_truth_val in ground_truth_dict.items():
            transcription_val = transcription_dict[fieldname]
            if transcription_val == "unsure and check":
                continue
            is_valid_target = is_valid(ground_truth_val)
            is_a_match = is_match(transcription_val, ground_truth_val)
            tallies = update_tallies(tallies, is_valid_target, is_a_match)
    return tallies        


def process(run_spreadname, ground_truth_dicts):
    saved_results: list[dict] = utility.get_contents_from_csv(SOURCE_PATH+run_spreadname)
    transcription_dicts = [remove_skipped_fields(d) for d in saved_results]
    tallies = compare_and_tally(transcription_dicts, ground_truth_dicts)  
    return calculate_accuracy(tallies)

def process2(run_spreadname, ground_truth_dicts, transcription_dicts): 
    print(f"{len(ground_truth_dicts[0]) = }, {len(transcription_dicts[0]) = }")
    tallies = compare_and_tally(transcription_dicts, ground_truth_dicts)  
    return calculate_accuracy(tallies)   

def intersecting_fields(d1, d2):
    return {key: val for key, val in d1.items() if key in d2}      

def critical_fields_only(d: dict):
    return {key: val for key, val in d.items() if key in CRITICAL_FIELDS}

def skeleton_fields_only(d: dict):
    return {key: val for key, val in d.items() if key in SKELETON_FIELDS}    

# remove fields before comparison
def remove_skipped_fields(d: dict):
    return {key: val for key, val in d.items() if key not in SKIP_LIST} 

def run():
    
    master_results = []                    
    for tup in RUN_FILENAMES1:
        print(tup) 
        spreadname, ref, model, ground_truth_filename = tup
        reference_dicts: list[dict] = utility.get_contents_from_csv(SOURCE_PATH+ground_truth_filename)
        ground_truth_dicts: list[dict] = [remove_skipped_fields(d) for d in reference_dicts]
        results = process(spreadname, ground_truth_dicts)  
        master_results += [format_results(spreadname, ref, model, results)] 
    for tup in RUN_FILENAMES2:
        print(tup) 
        spreadname, ref, model, ground_truth_filename = tup
        reference_dicts: list[dict] = utility.get_contents_from_csv(SOURCE_PATH+ground_truth_filename)
        ground_truth_dicts: list[dict] = [critical_fields_only(d) for d in reference_dicts]
        results = process(spreadname, ground_truth_dicts)  
        master_results += [format_results(spreadname, ref, model, results)]
    for tup in RUN_FILENAMES3:
        print(tup) 
        spreadname, ref, model, ground_truth_filename = tup
        reference_dicts: list[dict] = utility.get_contents_from_csv(SOURCE_PATH+ground_truth_filename)
        ground_truth_dicts: list[dict] = [skeleton_fields_only(d) for d in reference_dicts]
        results = process(spreadname, ground_truth_dicts)  
        master_results += [format_results(spreadname, ref, model, results)]   
    for tup in RUN_FILENAMES4:
        print(tup) 
        spreadname, ref, model, ground_truth_filename = tup
        reference_dicts: list[dict] = utility.get_contents_from_csv(SOURCE_PATH+ground_truth_filename)
        saved_results: list[dict] = utility.get_contents_from_csv(SOURCE_PATH+spreadname)
        
        ground_truth_dicts: list[dict] = [intersecting_fields(d, saved_results[0]) for d in reference_dicts]
        transcription_dicts = [intersecting_fields(d, reference_dicts[0]) for d in saved_results]
        fields = {key for key in ground_truth_dicts[0]}
        print(f"{fields = }")
        results = process2(spreadname, ground_truth_dicts, transcription_dicts)  
        master_results += [format_results(spreadname, ref, model, results)]              
    utility.save_to_csv(RESULTS_PATH+RESULT_FILENAME, master_results)
    print(f"Comparisons saved to {RESULTS_PATH+RESULT_FILENAME}!!!!")   

if __name__ == "__main__":
    run()
