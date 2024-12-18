import re
import utility

GROUND_TRUTH_FOLDER = "DataAnalysis/GroundTruths/"
SINGLE_COMPARISONS_FOLDER = "DataAnalysis/Comparisons/SingleComparisons/"
BATCH_COMPARISONS_FOLDER = "DataAnalysis/Comparisons/BatchComparisons/"
FIELDNAMES = ["verbatimCollectors", "collectedBy", "secondaryCollectors", "recordNumber", "verbatimEventDate", "minimumEventDate", "maximumEventDate", "verbatimIdentification", "latestScientificName", "identifiedBy", "verbatimDateIdentified", "associatedTaxa", "country", "firstPoliticalUnit", "secondPoliticalUnit", "municipality", "verbatimLocality", "locality", "habitat", "verbatimElevation", "verbatimCoordinates", "otherCatalogNumbers", "originalMethod", "typeStatus"]

def extract_data(string_data):
    return re.findall(r"[0-9.]+", string_data) 

def calculate_accuracy(numerator, denominator):
    return round(100*(numerator/denominator), 1) if denominator != 0 else "NaN"
    
def get_fields_accuracy(results_dict, fieldnames):
    d = {}
    for fieldname in fieldnames:
        data = extract_data(results_dict[fieldname])
        matchesValid, gradedMatchValid, numTargets = [int(float(datum)) for datum in data]
        d[fieldname] = calculate_accuracy(matchesValid, numTargets)
        d[f"{fieldname}GRD"] = calculate_accuracy(gradedMatchValid, numTargets)
    return d 

def get_fields_accuracy_batch_runs(batch_comparisons_filename):
    fieldnames = FIELDNAMES
    results_dicts = utility.get_contents_from_csv(BATCH_COMPARISONS_FOLDER+batch_comparisons_filename)
    field_accuracy_dicts = [get_fields_accuracy(results_dict, fieldnames) for results_dict in results_dicts]
    return field_accuracy_dicts          
                
def get_fields_accuracy_as_dict(run_name):
    fieldnames = FIELDNAMES
    comparsions_filename = f"{run_name}-comparisons.csv"
    results_dict = utility.get_contents_from_csv(SINGLE_COMPARISONS_FOLDER+comparsions_filename)[0]
    field_accuracy_dict = get_fields_accuracy(results_dict, fieldnames)
    return field_accuracy_dict
    
if __name__ == "__main__":
    batch_comparisons_filename = "claude-3.5-sonnet-various_prompts-comparisons.csv"
    r = get_fields_accuracy_batch_runs(batch_comparisons_filename)
    print(r)            
