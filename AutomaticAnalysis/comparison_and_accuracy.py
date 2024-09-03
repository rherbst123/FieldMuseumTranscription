# This script iterates through a list of .csv files
   # and compares each run to Ground Truth data.
# The configuration file template.json can be copied and saved to configure how run data is compared to
   # Ground Truth data (see the README in this folder for details)   
# Each field of each image is categorized as A or NA (applicable or non-applicable) 
   # according to whether or not "N\A" is recorded for that field and image in the Ground Truth,
     # and is compared to the llm data (observed value)
# This yields a True value for one of the following:
   #  TA, TNA, FA, FNA (true applicable, true non-applicable, false applicable or false non-applicable)
# In the spreadsheet, the breakdown of the three numbers in each field is: 
   # 1) number true (TA+TNA), 2) sum graded matches and number true negative (grdTA+TNA) , 3) sum of all values (TA+TNA+FA+FNA) 
# Accuracy breakdowns are explained in the calculate_accuracy method
# Errors are appended to the error file designated in the configuration file, if it already exists.
   # Results .csv s are NOT appended. They will be overwritten if they already exist.


import utility
import string_distance
import re
from tolerances import FieldTolerances
from string_distance import WeightedLevenshtein

class Comparison:
    def __init__(self, config_filename):
        config = utility.load_json(config_filename)
        self.config = config["COMPARISON_CONFIG"]
        self.config_name = config["CONFIGURATION_NAME"]
        self.SOURCE_PATH = self.config["SOURCE_PATH"]
        self.GROUND_TRUTH_FILENAME = self.config["GROUND_TRUTH_FILENAME"]
        self.RUN_SPREADNAMES = self.config["LLM_SPREAD_SOURCES"] 
        self.RESULTS_PATH = self.config["RESULTS_PATH"]
        self.RESULT_FILENAME = self.config["RESULT_FILENAME"]
        self.ERRORS_FILENAME = self.config["ERRORS_FILENAME"]
        self.RECORD_REF_FIELDNAME = self.config["RECORD_REF_FIELDNAME"]
        self.RECORD_REFS = []
        self.SKIP_LIST = self.config["SKIP_LIST"]
        self.SELECTED_FIELDS_LIST = self.config["SELECTED_FIELDS_LIST"]
        self.USE_SELECTED_FIELDS_ONLY = self.config["USE_SELECTED_FIELDS_ONLY"] == "True"
        self.setup(config)
        

    def setup(self, config):
        self.edit_distance_config = config["EDIT_DISTANCE_CONFIG"]
        self.USE_FIELDNAMES_EXCLUSIVELY = self.edit_distance_config["USE_FIELDNAMES_EXCLUSIVELY"] == "True"
        self.tolerances_config = config["TOLERANCES_CONFIG"] 
        self.TOLERANCES_ALLOWED = self.tolerances_config["TOLERANCES_ALLOWED"] == "True"
        self.TOLS = self.tolerances_config["TOLS"] if self.TOLERANCES_ALLOWED else {}
        self.field_tolerances = FieldTolerances(self.tolerances_config, self.edit_distance_config)

    def get_edit_distance_interface(self, fieldname):
        return WeightedLevenshtein(self.edit_distance_config, fieldname)
    
    def calculate_accuracy(self, master_results_dict, tallies):
        for key, val in tallies.items():
            master_results_dict[key] = val
        ta, tna, fa, fna = tallies["TrueApplicable"], tallies["TrueN/A"], tallies["FalseApplicable"], tallies["FalseN/A"]
        grdta, grdfa = int(tallies["GradedTA"]), int(tallies["GradedFA"])
        master_results_dict["Correct:TA+TN/A"] = ta+tna
        master_results_dict["Errors:FA+FN/A"] = fa+fna

        # Accuracy1 is the sum of all true values divided by the sum of all values, true or false
        master_results_dict["TA+TNA/TA+TNA+FA+FNA"] = f"{ta}+{tna}/{ta}+{tna}+{fa}+{fna}"
        master_results_dict["acc1:TA+TNA/TA+TNA+FA+FNA"] = (ta+tna)/(ta+tna+fa+fna)

        # Accuracy2 substitutes graded matches and graded non-matches for TrueApplicable and FalseApplicable
        master_results_dict["grdTA+TNA/grdTA+TNA+grdFA+FNA"] = f"{grdta}+{tna}/{grdta}+{tna}+{grdfa}+{fna}"
        master_results_dict["acc2:grdTP+TN/grdTP+TN+grdFP+FN"] = (grdta+tna)/(grdta+tna+grdfa+fna)

        # Accuracy3 leaves out TrueN/A, i.e., the true value is "N/A"
        master_results_dict["TA/TA+FA+FNA"] = f"{ta}/{ta}+{fa}+{fna}"
        master_results_dict["acc3:TA/TA+FA+FNA"] = ta/(ta+fa+fna)

         # Accuracy4 is like Accuracy3, but substituting graded matches and graded non-matches
        master_results_dict["grdTA/grdTA+grdFA+FNA"] = f"{grdta}/{grdta}+{grdfa}+{fna}"
        master_results_dict["acc4:grdTA/grdTA+grdFA+FNA"] = grdta/(grdta+grdfa+fna)
        return master_results_dict  

    def update_comparison_fields(self, d, master_comparison_dict):
        fieldname = d["fieldname"]
        master_comparison_dict[fieldname][0] += d["is_true_app"] or d["is_true_n/a"]
        master_comparison_dict[fieldname][1] += d["is_true_n/a"] or d["graded_true_app"]
        master_comparison_dict[fieldname][2] += d["is_true_app"] or d["is_true_n/a"] or d["is_false_app"] or d["is_false_n/a"]
        return master_comparison_dict

    def update_tallies(self, tallies, field_comparison_dict, master_comparison_dict):
        tallies["TrueApplicable"] += field_comparison_dict["is_true_app"]
        tallies["TrueN/A"] += field_comparison_dict["is_true_n/a"]
        tallies["FalseApplicable"] += field_comparison_dict["is_false_app"]
        tallies["FalseN/A"] += field_comparison_dict["is_false_n/a"]
        tallies["GradedTA"] += field_comparison_dict["graded_true_app"]
        tallies["GradedFA"] += field_comparison_dict["graded_false_app"]
        master_comparison_dict = self.update_comparison_fields(field_comparison_dict, master_comparison_dict)    
        return tallies, master_comparison_dict    

    def get_errors(self, d):
        if d["is_false_app"] or d["is_false_n/a"]:
           return {"ref": d["record_ref"], "fieldname": d["fieldname"], "observed_val": d["observed_val"], "true_val": d["true_val"], "graded_true_app": d["graded_true_app"], "graded_false_app": d["graded_false_app"]}
        return None   

    # this method is used to take false applicable values and determine by an edit distance algorithm
    # how far the observed value is to the true value and then grade that distance
    # that grade is used to "split" false applicable values into grades of "true" and grades of "false"         
    def get_graded_difference(self, observed_val, true_val, fieldname):
        if observed_val == "N/A":   # don't bother getting the edit distance when the observed value is "N/A"; just return 1
            return 1       
        elif self.USE_FIELDNAMES_EXCLUSIVELY and fieldname not in self.edit_distance_config["FIELDNAMES_COSTS"]: 
            return 1
        edit_distance_interface = self.get_edit_distance_interface(fieldname)        
        return edit_distance_interface.calculate_weighted_difference(observed_val, true_val)

    def grade(self, is_true_app, is_false_app, observed_val, true_val, fieldname):
        if is_false_app:
            graded_error = self.get_graded_difference(observed_val, true_val, fieldname)
            graded_true_app = 1 - graded_error
            graded_false_app = graded_error
            return graded_true_app, graded_false_app
        else:
            return is_true_app, is_false_app 

    def is_within_tolerances(self, fieldname, observed_val, true_val):
        return self.field_tolerances.is_within_tolerances(fieldname, observed_val, true_val) 


    def is_true(self, observed_val, true_val):
        return observed_val.strip().lower() == true_val.strip().lower()

    def is_applicable(self, val):
        return val != "N/A"

    def get_comparisons(self, fieldname, observed_val, true_val, record_ref):
        is_applicable = self.is_applicable(true_val)
        is_true = self.is_true(observed_val, true_val) or fieldname in self.TOLS and self.is_within_tolerances(fieldname, observed_val, true_val)
        true_app = is_applicable and is_true
        true_non_app = not is_applicable and is_true
        false_app = is_applicable and not is_true
        false_non_app = not is_applicable and not is_true
        graded_true_app, graded_false_app = self.grade(true_app, false_app, observed_val, true_val, fieldname)
        return {"fieldname": fieldname, "observed_val": observed_val, "true_val": true_val, "is_true_app": true_app, "is_true_n/a": true_non_app, "is_false_app": false_app, "is_false_n/a": false_non_app, "graded_true_app": graded_true_app, "graded_false_app": graded_false_app, "record_ref": record_ref}    
    
    def compare_and_tally(self, observed_values_dicts, true_values_dicts, master_comparison_dict):
        tallies = {"TrueApplicable": 0, "TrueN/A": 0, "FalseApplicable": 0, "FalseN/A": 0, "GradedTA": 0, "GradedFA": 0}
        run_errors = []
        for record_ref, observed_values_dict, true_values_dict in zip(self.RECORD_REFS, observed_values_dicts, true_values_dicts):
            for fieldname, observed_val in observed_values_dict.items():
                if observed_val == "PASS" or observed_val.lower().strip() == "unsure and check":
                    continue  # Just in case the LLM doesn't hazard a guess,
                                 # or there are gaps in some of the fields of observed values.
                                   # This is used when runs are compared for agreement
                                     #  and only agreed values are to be compared against true values
                true_val = true_values_dict[fieldname]
                field_comparison_dict = self.get_comparisons(fieldname, observed_val, true_val, record_ref)
                tallies, master_comparison_dict = self.update_tallies(tallies, field_comparison_dict, master_comparison_dict)
                run_errors += [self.get_errors(field_comparison_dict)]
        return master_comparison_dict, tallies, run_errors 

    def process(self, run_spreadname, true_values_dicts, blank_results_dict):
        saved_results: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+run_spreadname)
        observed_values_dicts = [self.get_fields_to_be_compared(d) for d in saved_results]
        results_dict, tallies, run_errors = self.compare_and_tally(observed_values_dicts, true_values_dicts, blank_results_dict)  
        return run_errors, self.calculate_accuracy(results_dict, tallies) 

    def get_blank_results_dict(self, spreadname, true_values_dict):
        return   {"run": spreadname, "ground truth filename": self.GROUND_TRUTH_FILENAME, "configuration name": self.config_name, "errors filename": self.ERRORS_FILENAME}  |   \
                 {fieldname: [0,0,0] for fieldname in true_values_dict}        
    
    # remove fields before comparison
    def remove_skipped_fields(self, d: dict):
        return {key: val for key, val in d.items() if key not in self.SKIP_LIST} 

    # use only selected fields for comparison
    def get_selected_fields_only(self, d: dict):
        return {key: val for key, val in d.items() if key in self.SELECTED_FIELDS_LIST}

    # this method determines whether to use core fields or just skip select fields
    def get_fields_to_be_compared(self, d: dict):
        return self.remove_skipped_fields(d) if not self.USE_SELECTED_FIELDS_ONLY else  self.get_selected_fields_only(d)

    def set_record_refs(self, reference_dicts):
        self.RECORD_REFS = [ref_dict[self.RECORD_REF_FIELDNAME] for ref_dict in reference_dicts]     

    def run(self):
        reference_dicts: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+self.GROUND_TRUTH_FILENAME)
        self.set_record_refs(reference_dicts) 
        true_values_dicts: list[dict] = [self.get_fields_to_be_compared(d) for d in reference_dicts]
        master_results = []                    
        for spreadname in self.RUN_SPREADNAMES:
            blank_results_dict = self.get_blank_results_dict(spreadname, true_values_dicts[0]) 
            run_errors, results = self.process(spreadname, true_values_dicts, blank_results_dict)  
            master_results += [results]
            utility.save_errors(self.RESULTS_PATH+self.ERRORS_FILENAME, run_errors, spreadname, self.RECORD_REF_FIELDNAME, self.config, self.edit_distance_config, self.tolerances_config)
            print(f"Errors saved to {self.RESULTS_PATH+self.ERRORS_FILENAME}!!!!")  
        formatted_results = [utility.format_values(d) for d in master_results]    
        utility.save_to_csv(self.RESULTS_PATH+self.RESULT_FILENAME, formatted_results)
        print(f"Comaparisons saved to {self.RESULTS_PATH+self.RESULT_FILENAME}!!!!")   
    
if __name__ == "__main__":
    

    # copy in the name of the configuration file to be used below
    config_filename = "AutomaticAnalysis/Configurations/demo.json" 

    accuracy_run = Comparison(config_filename)
    accuracy_run.run()