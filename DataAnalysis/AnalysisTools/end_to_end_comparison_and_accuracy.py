# this script takes an LLM .txt file output and first converts it a .csv file, 
# and then performs a comparison run

from comparison_and_accuracy import Comparison
import logging
from Utilities import utility
import string_distance
import re
from tolerances import FieldTolerances
from string_distance import WeightedLevenshtein
from Utilities import text2csv_stripped

class CompareFromText(Comparison):
    
    def convert_text_output_to_csv(self):
        run_name = self.config["RUN_NAME"]
        text_filename = f"TextTranscriptions/{run_name}-transcriptions.txt"
        csv_filename = f"{run_name}-transcriptions.csv"
        text2csv_stripped.main(self.COMPARISONS_PATH+text_filename, self.COMPARISONS_PATH+csv_filename)

if __name__ == "__main__":
    CONFIG_PATH = "DataAnalysis/AnalysisTools/Configurations/"

    # copy in the name of the configuration file to be used below
    config_filename = "template_single_runs.yaml" 

    accuracy_run = CompareFromText(CONFIG_PATH, config_filename)
    accuracy_run.convert_text_output_to_csv()
    accuracy_run.run()