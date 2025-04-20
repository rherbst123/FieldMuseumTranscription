# this script takes an LLM .txt file output and first converts it a .csv file, 
# and then performs a comparison run

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
    "PROMPT_FILENAME": "TBD",
    "TRANSCRIPTIONS_PATH": "DataAnalysis/Transcriptions/",
    "COMPARISONS_PATH": "DataAnalysis/Comparisons/",
    "PROMPTS_PATH": "Prompts/"
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

import logging
import re
from DataAnalysis.AnalysisTools.comparison_and_accuracy import Comparison
from DataAnalysis.AnalysisTools.Utilities import utility
from DataAnalysis.AnalysisTools.Utilities import text_to_dict_via_prompt
from DataAnalysis.AnalysisTools.PromptAndErrorAnalysis.error_classification import ErrorClassifier

class CompareFromText(Comparison):
    
    def convert_text_output_to_csv(self):
        run_name = self.config["RUN_NAME"]
        text_filename = f"TextTranscriptions/{run_name}-transcriptions.txt"
        csv_filename = f"{run_name}-transcriptions.csv"
        text_to_dict_via_prompt.text_to_csv(self.TRANSCRIPTIONS_PATH+text_filename, self.TRANSCRIPTIONS_PATH+csv_filename)
        print(f"transcriptions saved to {self.TRANSCRIPTIONS_PATH+csv_filename} !!!")


def process_and_compare(run_name, ground_truth_filename):
    BLANK_CONFIG["COMPARISON_CONFIG"]["RUN_NAME"] = run_name
    BLANK_CONFIG["COMPARISON_CONFIG"]["GROUND_TRUTH_FILENAME"] = ground_truth_filename
    BLANK_CONFIG["COMPARISON_CONFIG"]["PROMPT_FILENAME"] = "Prompt 1.5.4.txt"
    accuracy_run = CompareFromText(BLANK_CONFIG)
    accuracy_run.convert_text_output_to_csv()
    accuracy_run.run()

def classify_errors(run_name, ground_truth_filename):
    transcriptions_filename = f"{run_name}-transcriptions.csv"
    transcriptions_filepath = "DataAnalysis/Transcriptions/"+transcriptions_filename
    fieldnames = ErrorClassifier.get_fieldnames_from_saved_data(transcriptions_filepath) 
    ec = ErrorClassifier(run_name, fieldnames)
    ec.run(run_name, ground_truth_filename)    
    

if __name__ == "__main__":
    
    ###########################################################
    # copy in the name of the configuration file to be used below
    config_filename = "template_single_runs.yaml" 
    ###########################################################
    CONFIG_PATH = "DataAnalysis/AnalysisTools/Configurations/"
    configuration = Comparison.read_configuration_from_yaml(CONFIG_PATH, config_filename)
    accuracy_run = CompareFromText(configuration, config_source=config_filename)
    accuracy_run.convert_text_output_to_csv()
    accuracy_run.run()