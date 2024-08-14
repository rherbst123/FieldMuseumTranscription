import utility
import string_distance
import re


class Comparison:
    def __init__(self, config: dict):
        self.config = config
        self.RUN_SPREADNAMES = config["LLM_SPREAD_SOURCES"]
        self.SOURCE_PATH = config["SOURCE_PATH"]
        self.GROUND_TRUTH_FILENAME = config["GROUND_TRUTH_FILENAME"]
        self.SKIP_LIST = config["SKIP_LIST"]
        self.CORE_FIELDS_LIST = config["CORE_FIELDS_LIST"]
        self.RESULTS_PATH = config["RESULTS_PATH"]
        self.RESULT_FILENAME = config["RESULT_FILENAME"]
        self.ERRORS_FILENAME = config["ERRORS_FILENAME"]
        self.CORE_FIELDS_ONLY = config["USE_CORE_FIELDS"] == "True"
        edit_distance_class = config["EDIT_DISTANCE_CLASS"]
        self.edit_distance_interface = self.setup_edit_distance_interface(edit_distance_class, config["EDIT_DISTANCE_CONFIG"])

    def setup_edit_distance_interface(self, edit_distance_class, edit_distance_config):
        if edit_distance_class == "WeightedLevenshtein":
            from string_distance import WeightedLevenshtein
            return WeightedLevenshtein(edit_distance_config)
        elif edit_distance_class == "NLTKDistance":
            from string_distance import NLTKDistance
            return NLTKDistance(edit_distance_config)   
    
    # accuracy calculated only for those valid ground truth targets (i.e., not an "N/A")
    def calculate_accuracy_valid_targets(self, master_results_dict, num_errors, val_weighted_errors, num_valid_targets):
        master_results_dict["number errors"] = num_errors
        master_results_dict["weighted errors"] = val_weighted_errors
        master_results_dict["number valid targets"] = num_valid_targets
        master_results_dict["accuracy: UNWEIGHTED"] = (num_valid_targets-num_errors) / num_valid_targets
        master_results_dict["accuracy: WEIGHTED"] = (num_valid_targets-val_weighted_errors) / num_valid_targets
        return master_results_dict  

    def update_comparison_fields(self, d, master_comparison_dict):
        fieldname = d["fieldname"]
        master_comparison_dict[fieldname][0] += d["is_an_error"]
        master_comparison_dict[fieldname][1] += d["weighted_error"]
        master_comparison_dict[fieldname][2] += d["is_a_valid_target"]
        return master_comparison_dict

    def update_tallies(self, num_errors, val_weighted_errors, num_valid_targets, d, master_comparison_dict):
        num_errors += d["is_an_error"]
        num_valid_targets += d["is_a_valid_target"]
        d["weighted_error"] = self.get_weighted_difference(d)
        val_weighted_errors += d["weighted_error"]
        master_comparison_dict = self.update_comparison_fields(d, master_comparison_dict)    
        return num_errors, val_weighted_errors, num_valid_targets, master_comparison_dict    

    def get_errors(self, d):
        if d["is_an_error"]:
           return {"fieldname": d["fieldname"], "observed_val": d["observed_val"], "true_val": d["true_val"], "weighted_error": d["weighted_error"]}
        return None   
             
    def get_weighted_difference(self, d):
        if not d["is_an_error"]:
            return 0
        elif self.is_invalid_observation(d["observed_val"], d["true_val"]):
            # don't get the weighted distance when the true value is "N/A" and the observed value isn't "N/A"; just return 1
            return 1
        elif d["observed_val"] == "N/A":
            return 1       
        else:
            return self.edit_distance_interface.calculate_weighted_difference(d["observed_val"], d["true_val"])      

    def is_different(self, val1, val2):
        return val1.strip().lower() != val2.strip().lower()

    # an observation is invalid when the true value is "N/A" and the observed value is not "N/A"
       # currently, this counts as an error
    def is_invalid_observation(self, observed_val, true_val):
        return not self.is_a_valid_target(true_val) and observed_val != "N/A"

    def is_an_error(self, observed_val, true_val):
        return self.is_a_valid_target(true_val) and self.is_different(observed_val, true_val) or self.is_invalid_observation(observed_val, true_val)    

    def is_a_valid_target(self, true_val):
        return true_val != "N/A"

    def compare(self, observed_val, true_val):
        return self.is_a_valid_target(true_val), self.is_an_error(observed_val, true_val)
    
    def compare_and_tally(self, observed_values_dicts, true_values_dicts, master_comparison_dict):
        num_errors = 0
        val_weighted_errors = 0
        num_valid_targets = 0
        run_errors = []
        for observed_values_dict, true_values_dict in zip(observed_values_dicts, true_values_dicts):
            for fieldname, observed_val in observed_values_dict.items():
                if observed_val == "PASS":
                    continue
                true_val = true_values_dict[fieldname]
                is_a_valid_target, is_an_error = self.compare(observed_val, true_val)
                field_comparison_dict = {"fieldname": fieldname, "observed_val": observed_val, "true_val": true_val, "is_a_valid_target": is_a_valid_target, "is_an_error": is_an_error}
                num_errors, val_weighted_errors, num_valid_targets, master_comparison_dict = self.update_tallies(num_errors, val_weighted_errors, num_valid_targets, field_comparison_dict, master_comparison_dict)
                run_errors += [self.get_errors(field_comparison_dict)]
        return master_comparison_dict, num_errors, val_weighted_errors, num_valid_targets, run_errors 

    def process(self, run_spreadname, true_values_dicts, blank_results_dict):
        saved_results: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+run_spreadname)
        observed_values_dicts = [self.get_fields_to_be_compared(d) for d in saved_results]
        tallied_results_dict, num_errors, val_weighted_errors, num_targets, run_errors = self.compare_and_tally(observed_values_dicts, true_values_dicts, blank_results_dict)  
        return run_errors, self.calculate_accuracy_valid_targets(tallied_results_dict, num_errors, val_weighted_errors, num_targets) 

    def get_blank_results_dict(self, spreadname, true_values_dict):
        return   {"run": spreadname, "ground truth filename": self.GROUND_TRUTH_FILENAME, "skipped fields": self.SKIP_LIST, "core fields": self.CORE_FIELDS_LIST}  |   \
                 {fieldname: [0,0,0] for fieldname in true_values_dict if fieldname not in self.SKIP_LIST}        
    
    # remove fields before comparison
    def remove_skipped_fields(self, d: dict):
        return {key: val for key, val in d.items() if key not in self.SKIP_LIST} 

    # use only core fields for comparison
    def get_core_fields_only(self, d: dict):
        return {key: val for key, val in d.items() if key in self.CORE_FIELDS_LIST}

    # this method determines whether to use core fields or just skip select fields
    def get_fields_to_be_compared(self, d: dict):
        return self.remove_skipped_fields(d) if not self.CORE_FIELDS_ONLY else  self.get_core_fields_only(d) 

    def run(self):
        reference_dicts: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+self.GROUND_TRUTH_FILENAME)
        true_values_dicts: list[dict] = [self.get_fields_to_be_compared(d) for d in reference_dicts]
        master_results = []                    
        for spreadname in self.RUN_SPREADNAMES: 
            blank_results_dict = self.get_blank_results_dict(spreadname, true_values_dicts[0]) 
            run_errors, results = self.process(spreadname, true_values_dicts, blank_results_dict)  
            master_results += [results]
            utility.save_errors(self.RESULTS_PATH+self.ERRORS_FILENAME, run_errors, spreadname, self.config)
            print(f"Errors saved to {self.RESULTS_PATH+self.ERRORS_FILENAME}!!!!")  
        formatted_results = [utility.format_values(d) for d in master_results]    
        utility.save_to_csv(self.RESULTS_PATH+self.RESULT_FILENAME, formatted_results)
        print(f"Comaparisons saved to {self.RESULTS_PATH+self.RESULT_FILENAME}!!!!")   
    
if __name__ == "__main__":
    config_filename = "AccuracyTesting/transcription_config.json" 
    config_name = "gpt4o and sonnet3.5 repeats"
    config = utility.load_json(config_filename)[config_name]
    accuracy_run = Comparison(config)
    accuracy_run.run()