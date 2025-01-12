BLANK_CONFIG =                 \
{
"COMPARISON_CONFIG":
    {
    "COMPARISON_TYPE": "single_run",
    "RUN_NAME": "TBD",
    "COMPARISON_NAME": "",
    "RECORD_REF_FIELDNAME": "accessURI",  
    "SKIP_LIST": [], 
    "SELECTED_FIELDS_LIST": [],                      
    "USE_SELECTED_FIELDS_ONLY": False,
    "GROUND_TRUTH_FILENAME": "TBD",
    "TRANSCRIPTIONS_PATH": "DataAnalysis/Transcriptions/",
    "COMPARISONS_PATH": "DataAnalysis/Comparisons/",
    },



"EDIT_DISTANCE_CONFIG":
    {
    "USE_FIELDNAMES_EXCLUSIVELY": False,  
    "FIELDNAMES_COSTS": {},
    "DEFAULT_FIELDS_CUSTOM_COSTS":
        {
        "INSERT_CHAR_COSTS": [[]], 
        "DELETE_CHAR_COSTS":  [[]],
        "SUBSTITUTION_CHAR_COSTS": [[]],
        "TRANSPOSITON_CHAR_COSTS": [[]]
        }
    },

"TOLERANCES_CONFIG": 
    {
     "TOLERANCES_ALLOWED": False,
     "TOLS":
        { 
        "ENABLE_EDIT_DISTANCE_THRESHOLD": False,  
        "EDIT_DISTANCE_THRESHOLDS": 
            {                                                   
            "DEFAULT":
                {
                "SCALED": None,         
                "VALUE": None              
                }
            }
        }
    },

"POST_PROCESSING_CONFIG": {}
}

from Utilities import utility
from comparison_and_accuracy import Comparison


def main(associated_files_dicts):
    transcription_folder = "DataAnalysis/Transcriptions/"
    for associated_files_dict in associated_files_dicts:
        run_name = associated_files_dict["Run Name"]
        ground_truth_filename = associated_files_dict["Ground Truth"]
        BLANK_CONFIG["COMPARISON_CONFIG"]["RUN_NAME"] = run_name
        BLANK_CONFIG["COMPARISON_CONFIG"]["GROUND_TRUTH_FILENAME"] = ground_truth_filename
        try:
            acc = Comparison(BLANK_CONFIG)
            acc.run()     
        except FileNotFoundError:
            print("Run Not Found: "+run_name) 
            continue    
        

if __name__ == "__main__":
    spread_filepath = "DataAnalysis/associated_files_for_paper.csv"
    associated_files_dicts = utility.get_contents_from_csv(spread_filepath)
    main(associated_files_dicts)
    