# This script iterates through a list of .csv files
   # and compares each run to Ground Truth data.

# A configuration file template can be copied and saved to configure how run data is compared to
   # Ground Truth data.   (see the Configurations/README.md for details) 
     
# Each field of each image is categorized as valid or nonValid 
   # according to whether there is transcribed string data or "N\A" recorded for that field of that image in the Ground Truth,
     # and is compared for a match against the llm data for that field of that image.

# This yields a True value for one of the following:
   #  matchValid, matchNonValid, noMatchValid or noMatchNonValid (MV, MNV, NMV, NMNV)

# The breakdown of the three numbers in each field is explained in Comparisons/README.md  
# Accuracy breakdowns are explained in the calculate_accuracy method
# Errors are appended to the error file designated in the configuration file, if it already exists.
   # Results .csv s are NOT appended. They will be overwritten if they already exist.


import logging
import re
from Utilities import utility
from tolerances import FieldTolerances
from string_distance import WeightedLevenshtein

class Comparison:
    def __init__(self, config, config_source=None):
        self.config_source = config_source
        self.config = config["COMPARISON_CONFIG"]
        self.setup_paths()
        self.RECORD_REF_FIELDNAME = self.config["RECORD_REF_FIELDNAME"]
        self.RECORD_REFS = []
        self.SKIP_LIST = self.config["SKIP_LIST"]
        self.SELECTED_FIELDS_LIST = self.config["SELECTED_FIELDS_LIST"]
        self.USE_SELECTED_FIELDS_ONLY = self.config["USE_SELECTED_FIELDS_ONLY"]
        self.setup_other_configs(config)

    @staticmethod
    def read_configuration_from_yaml(config_folder, config_filename):
        return utility.load_yaml(config_folder+config_filename)

    def setup_paths(self):
        self.TRANSCRIPTIONS_PATH = self.config["TRANSCRIPTIONS_PATH"]
        self.GROUND_TRUTH_FILENAME = self.config["GROUND_TRUTH_FILENAME"]
        self.GROUND_TRUTH_PATH = "DataAnalysis/GroundTruths/"
        self.PROMPTS_PATH = self.config["PROMPTS_PATH"]
        self.PROMPT_FILENAME = self.config["PROMPT_FILENAME"]
        self.PROMPT_PATH = self.PROMPTS_PATH + self.PROMPT_FILENAME
        if self.config["COMPARISON_TYPE"] == "single_run":
            self.setup_single_run()
        elif self.config["COMPARISON_TYPE"] == "batch_run":
            self.setup_batch_run() 
        else:
            print('CONFIGURATION ERROR !!! COMPARISON_TYPE must be "single_run" or "batch_run"!!')      

    def setup_single_run(self):
        run_name = self.config["RUN_NAME"]
        comparison_name = self.config["COMPARISON_NAME"]
        results_name = f"{run_name}-{comparison_name}" if comparison_name else run_name 
        self.RUN_SPREADNAMES = [f"{run_name}-transcriptions.csv"] 
        self.COMPARISONS_PATH = self.config["COMPARISONS_PATH"] + "SingleComparisons/"
        self.COMPARISONS_FILENAME = f"{results_name}-comparisons.csv"
        self.ERRORS_PATH = self.config["COMPARISONS_PATH"] + "Errors/"
        self.ERRORS_FILENAME = f"{results_name}-errors.txt"

    def setup_batch_run(self):
        batch_name = self.config["BATCH_NAME"]
        comparison_name = self.config["COMPARISON_NAME"]
        results_name = f"{batch_name}-{comparison_name}" if comparison_name else batch_name
        self.RUN_NAMES = self.config["RUN_NAMES"]
        if type (self.RUN_NAMES[0]) == list:
            self.RUN_SPREADNAMES = self.get_run_names_for_2D_batch_run()
        else:    
            self.RUN_SPREADNAMES = [f"{run_name}-transcriptions.csv" for run_name in self.config["RUN_NAMES"]] 
        self.COMPARISONS_PATH = self.config["COMPARISONS_PATH"] + "BatchComparisons/"
        self.COMPARISONS_FILENAME = f"{results_name}-comparisons.csv"
        self.ERRORS_PATH = self.config["COMPARISONS_PATH"] + "Errors/"
        self.ERRORS_FILENAME = f"{results_name}-errors.txt"

    def get_run_names_for_2D_batch_run(self):
        return [[f"{run_name}-transcriptions.csv" for run_name in batch_list] for batch_list in self.config["RUN_NAMES"]]        


    def setup_other_configs(self, config):
        self.logger = utility.get_logger()
        self.edit_distance_config = config["EDIT_DISTANCE_CONFIG"]
        self.USE_FIELDNAMES_EXCLUSIVELY = self.edit_distance_config["USE_FIELDNAMES_EXCLUSIVELY"]
        self.tolerances_config = config["TOLERANCES_CONFIG"] 
        self.TOLERANCES_ALLOWED = self.tolerances_config["TOLERANCES_ALLOWED"]
        self.TOLS = self.tolerances_config["TOLS"] if self.TOLERANCES_ALLOWED else {}
        self.field_tolerances = FieldTolerances(self.tolerances_config, self.edit_distance_config)
        self.POST_PROCESSING_CONFIG = config["POST_PROCESSING_CONFIG"]

    def get_edit_distance_interface(self, fieldname):
        return WeightedLevenshtein(self.edit_distance_config, fieldname)
    
    def calculate_accuracy(self, master_results_dict, tallies):
        for key, val in tallies.items():
            master_results_dict[key] = val
        matchValid, matchNonValid, noMatchValid, noMatchNonValid = tallies["matchValid"], tallies["matchNonValid"], tallies["noMatchValid"], tallies["noMatchNonValid"]
        master_results_dict["Correct:matchValid+matchNonValid"] = matchValid + matchNonValid
        master_results_dict["Errors:noMatchValid+noMatchNonValid"] = noMatchValid + noMatchNonValid

        # accuracy = the sum of all matches divided by the sum of all targets, valid or nonValid
        master_results_dict["MV+MNV/MV+MNV+NMV+NMNV"] = f"{matchValid}+{matchNonValid}/{matchValid}+{matchNonValid}+{noMatchValid}+{noMatchNonValid}"
        master_results_dict["all targets:accuracy"] = (matchValid+matchNonValid)/(matchValid+matchNonValid+noMatchValid+noMatchNonValid)

        # accuracy = the sum of matches on valid targets divided by the sum of matches on valid targets plus all noMatches, valid or nonValid
        master_results_dict["MV/MV+NMV+NMNV"] = f"{matchValid}/{matchValid}+{noMatchValid}+{noMatchNonValid}"
        master_results_dict["valid targets:accuracy"] = matchValid/(matchValid+noMatchValid+noMatchNonValid)
        print(master_results_dict["valid targets:accuracy"])
        return master_results_dict  

    def update_comparison_fields(self, d, master_comparison_dict):
        fieldname = d["fieldname"]
        master_comparison_dict[fieldname][0] += d["matchValid"] 
        master_comparison_dict[fieldname][1] += d["gradedMatchValid"]
        master_comparison_dict[fieldname][2] += d["matchValid"] or d["noMatchValid"] or d["noMatchNonValid"]
        return master_comparison_dict

    def update_tallies(self, tallies, field_comparison_dict, master_comparison_dict):
        tallies["matchValid"] += field_comparison_dict["matchValid"]
        tallies["matchNonValid"] += field_comparison_dict["matchNonValid"]
        tallies["noMatchValid"] += field_comparison_dict["noMatchValid"]
        tallies["noMatchNonValid"] += field_comparison_dict["noMatchNonValid"]
        tallies["gradedMatchValid"] += field_comparison_dict["gradedMatchValid"]
        tallies["gradedNoMatchValid"] += field_comparison_dict["gradedNoMatchValid"]
        master_comparison_dict = self.update_comparison_fields(field_comparison_dict, master_comparison_dict)    
        return tallies, master_comparison_dict    

    def get_errors(self, d):
        if d["noMatchValid"] or d["noMatchNonValid"]:
           return {"ref": d["record_ref"], "fieldname": d["fieldname"], "transcription_val": d["transcription_val"], "target_val": d["target_val"], "gradedMatchValid": d["gradedMatchValid"], "gradedNoMatchValid": d["gradedNoMatchValid"]}
        return None   

    # this method is used to take false applicable values and determine by an edit distance algorithm
    # how far the observed value is to the true value and then grade that distance
    # that grade is used to "split" false applicable values into grades of "true" and grades of "false"         
    def get_graded_difference(self, transcription_val, target_val, fieldname):
        if transcription_val == "N/A":   # don't bother getting the edit distance when the observed value is "N/A"; just return 1
            return 1       
        elif self.USE_FIELDNAMES_EXCLUSIVELY and fieldname not in self.edit_distance_config["FIELDNAMES_COSTS"]: 
            return 1
        edit_distance_interface = self.get_edit_distance_interface(fieldname)        
        return edit_distance_interface.calculate_weighted_difference(transcription_val, target_val)

    def grade(self, matchValid, noMatchValid, transcription_val, target_val, fieldname):
        if noMatchValid:
            graded_error = self.get_graded_difference(transcription_val, target_val, fieldname)
            gradedMatchValid = 1 - graded_error
            gradedNoMatchValid = graded_error
            return gradedMatchValid, gradedNoMatchValid
        else:
            return matchValid, noMatchValid 

    def is_within_tolerances(self, fieldname, observed_val, true_val):
        return self.field_tolerances.is_within_tolerances(fieldname, observed_val, true_val) 

    def is_match(self, val1, val2):
        return val1.strip().lower() == val2.strip().lower()

    def is_valid(self, val):
        return val != "N/A"

    def get_comparisons(self, fieldname, transcription_val, target_val, record_ref):
        is_valid = self.is_valid(target_val)
        is_a_match = self.is_match(transcription_val, target_val) or self.is_within_tolerances(fieldname, transcription_val, target_val) #and fieldname in self.TOLS
        matchValid = is_valid and is_a_match
        matchNonValid = not is_valid and is_a_match
        noMatchValid = is_valid and not is_a_match
        noMatchNonValid = not is_valid and not is_a_match
        gradedMatchValid, gradedNoMatchValid = self.grade(matchValid, noMatchValid, transcription_val, target_val, fieldname)
        return {"fieldname": fieldname, "transcription_val": transcription_val, "target_val": target_val, "matchValid": matchValid, "matchNonValid": matchNonValid, "noMatchValid": noMatchValid, "noMatchNonValid": noMatchNonValid, "gradedMatchValid": gradedMatchValid, "gradedNoMatchValid": gradedNoMatchValid, "record_ref": record_ref}    
    
    def compare_and_tally(self, transcription_values_dicts, master_comparison_dict):
        tallies = {"matchValid": 0, "matchNonValid": 0, "noMatchValid": 0, "noMatchNonValid": 0, "gradedMatchValid": 0, "gradedNoMatchValid": 0}
        run_errors = []
        for record_ref, transcription_values_dict, target_values_dict in zip(self.RECORD_REFS, transcription_values_dicts, self.target_values_dicts):
            for fieldname in self.fieldnames:
                target_val = target_values_dict[fieldname]
                transcription_val = transcription_values_dict[fieldname]
                if transcription_val.strip() in ["PASS", "unsure and check", "[precise locality unknown]"]:
                    continue  # Just in case the LLM doesn't hazard a guess,
                                 # or there are gaps in some of the fields of observed values.
                                   # This is used when runs are compared for agreement
                                     #  and only agreed values are to be compared against true values
                
                field_comparison_dict = self.get_comparisons(fieldname, transcription_val, target_val, record_ref)
                tallies, master_comparison_dict = self.update_tallies(tallies, field_comparison_dict, master_comparison_dict)
                run_errors += [self.get_errors(field_comparison_dict)]
        return master_comparison_dict, tallies, run_errors 

    def get_blank_results_dict(self, spreadname):
        return   {"run": spreadname, "ground truth source": self.GROUND_TRUTH_FILENAME, "prompt name": self.PROMPT_FILENAME, "configuration source": self.config_source}  |   \
                 {fieldname: [0,0,0] for fieldname in self.fieldnames}        

    def get_fieldnames(self):
        prompt_text = utility.get_contents_from_txt(self.PROMPT_PATH)
        fieldnames = utility.get_fieldnames_from_prompt(prompt_text)
        return [fieldname for fieldname in fieldnames if fieldname not in self.SKIP_LIST]       

    def set_fields_to_be_compared(self):
        self.fieldnames = self.SELECTED_FIELDS_LIST if self.USE_SELECTED_FIELDS_ONLY else self.get_fieldnames()
        self.fieldnames.sort()

    def process(self, run_spreadname, transcription_values_dicts):
        self.set_fields_to_be_compared()
        blank_results_dict = self.get_blank_results_dict(run_spreadname)
        results_dict, tallies, run_errors = self.compare_and_tally(transcription_values_dicts, blank_results_dict)  
        return run_errors, self.calculate_accuracy(results_dict, tallies) 
    
    def set_record_refs(self, reference_dicts):
        if self.RECORD_REF_FIELDNAME in reference_dicts[0]:
            self.RECORD_REFS = [ref_dict[self.RECORD_REF_FIELDNAME] for ref_dict in reference_dicts] 
        else:
            self.RECORD_REFS = [ref_dict["catalogNumber"] for ref_dict in reference_dicts]         

    def load_data(self):
        self.target_values_dicts: list[dict] = utility.get_contents_from_csv(self.GROUND_TRUTH_PATH+self.GROUND_TRUTH_FILENAME)
        self.set_record_refs(self.target_values_dicts)
        self.master_transcription_values_dicts = {run_spreadname: utility.get_contents_from_csv(self.TRANSCRIPTIONS_PATH+run_spreadname) for run_spreadname in self.RUN_SPREADNAMES}    
        
    def run(self):
        self.load_data()
        master_results = []                   
        for spreadname, transcription_values_dicts in self.master_transcription_values_dicts.items():
            run_errors, results = self.process(spreadname, transcription_values_dicts)  
            master_results += [results]
            utility.save_errors(self.ERRORS_PATH+self.ERRORS_FILENAME, run_errors, spreadname, self.RECORD_REF_FIELDNAME, self.config, self.edit_distance_config, self.tolerances_config)
            print(f"Errors saved to {self.ERRORS_PATH+self.ERRORS_FILENAME}!!!!")  
        formatted_results = [utility.format_values(d) for d in master_results]
        print(f"{len(formatted_results) = }")    
        utility.save_to_csv(self.COMPARISONS_PATH+self.COMPARISONS_FILENAME, formatted_results)
        print(f"Comparisons saved to {self.COMPARISONS_PATH+self.COMPARISONS_FILENAME}!!!!")   
    
if __name__ == "__main__":
    
    ###########################################################
    # copy in the name of the configuration file to be used below
    config_filename = "nova_repeats.yaml" 
    ###########################################################
    CONFIG_PATH = "DataAnalysis/AnalysisTools/Configurations/"
    configuration = Comparison.read_configuration_from_yaml(CONFIG_PATH, config_filename)
    accuracy_run = Comparison(configuration, config_source=config_filename)
    accuracy_run.run()