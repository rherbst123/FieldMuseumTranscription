import utility
import copy
SOURCEFILE_AVERAGES1 = "multi_agreement_gpt_sonnet_gemini.csv"
SOURCEFILE_AVERAGES2 = "tagged_model_repeats.csv"

SOURCEFILE_RUNS1 = ["GPT-4o_Spread_6_11_1050.csv", 
                    "Sonnet_SpreadJun.21.24.1043.csv", 
                    "Gemini_SpreadJun.20.24.0153.csv", 
                    "agreement_GPT-4o_Spread_6_11_1050_Sonnet_SpreadJun.21.24.1043.csv",
                    "agreement_GPT-4o_Spread_6_11_1050_Gemini_SpreadJun.20.24.0153.csv",
                    "agreement_Sonnet_SpreadJun.21.24.1043_Gemini_SpreadJun.20.24.0153.csv",
                    "agreement_GPT-4o_Spread_6_11_1050_Sonnet_SpreadJun.21.24.1043_Gemini_SpreadJun.20.24.0153.csv"]

SOURCEFILE_RUNS2 = ["GPT-4o_Spread_6_11_1110.csv", #
                    "Sonnet_SpreadJun.26.24.1050.csv", #
                    "Gemini_SpreadJun.26.24.1108.csv", #
                    "agreement_GPT-4o_Spread_6_11_1110_Sonnet_SpreadJun.26.24.1050.csv",  #
                    "agreement_GPT-4o_Spread_6_11_1110_Gemini_SpreadJun.26.24.1108.csv",   #
                    "agreement_Sonnet_SpreadJun.26.24.1050_Gemini_SpreadJun.26.24.1108.csv",  #
                    "agreement_GPT-4o_Spread_6_11_1110_Sonnet_SpreadJun.26.24.1050_Gemini_SpreadJun.26.24.1108.csv"] #


RESULTS_FILENAME = "completed_agreement_gpt_sonnet_gemini2.csv"
SOURCE_PATH = "AutomaticAnalysis/SourcesForPaper/"
RESULTS_PATH = "AutomaticAnalysis/ResultsForPaper/"
SKIP_LIST = []

def get_average(field_value: str):
    # [65, 85.5, 100]
    raw = field_value.split(",")
    hits, num_targets = int(raw[0][1:]), int(raw[2][:-1])
    return hits/num_targets

def rank_models_for_fieldname(averages_list: list[dict], fieldname):
    return sorted(averages_list, key=lambda d: get_average(d[fieldname]))[::-1]

def get_field_value_for_model(modelname, fieldname, runs, image_idx):
    for run in runs:
        if run[image_idx]["modelname"] == modelname:
            return run[image_idx][fieldname]
    return "Error!!!!"        




def get_result_for_field(fieldname, averages_list, runs, image_idx):
    ranked_averages = rank_models_for_fieldname(averages_list, fieldname)
    if fieldname == "verbatimCollectors":
        for avg in ranked_averages:
            print(f"{avg['run'] = }")
        print(3*"\n")
    for ranked_avg in ranked_averages:
        modelname = ranked_avg["modelname"]
        field_value = get_field_value_for_model(modelname, fieldname, runs, image_idx)
        if field_value != "PASS":
            return field_value

def get_image_result(fieldnames, averages_list, runs, image_idx):
    return {"modelname": "mixed gpt4o sonnet gemini"} | {fieldname: get_result_for_field(fieldname, averages_list, runs, image_idx) for fieldname in fieldnames}            

def main():
    avg1 = utility.get_contents_from_csv(RESULTS_PATH+SOURCEFILE_AVERAGES1)
    avg2 = utility.get_contents_from_csv(RESULTS_PATH+SOURCEFILE_AVERAGES2)
    averages = avg1+avg2
    runs = [utility.get_contents_from_csv(SOURCE_PATH+sourcefile) for sourcefile in SOURCEFILE_RUNS2]
    fieldnames = ["verbatimCollectors","collectedBy","secondaryCollectors","recordNumber","verbatimEventDate","minimumEventDate","maximumEventDate","verbatimIdentification","latestScientificName","identifiedBy","verbatimDateIdentified","associatedTaxa","country","firstPoliticalUnit","secondPoliticalUnit","municipality","verbatimLocality","locality","habitat","verbatimElevation","verbatimCoordinates","otherCatalogNumbers","originalMethod","typeStatus"]
    results = []
    for image_idx, image in enumerate(runs[0]):
        results += [get_image_result(fieldnames, averages, runs, image_idx)]
    utility.save_to_csv(SOURCE_PATH+RESULTS_FILENAME, results) 
    print(f"results saved to {RESULTS_FILENAME} !!!")   



if __name__ == "__main__":
    main()