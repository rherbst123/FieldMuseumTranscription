# In the spreadsheet, the breakdown of the three numbers in each field is: 
   # 1) number true (TP+TN), 2) sum graded matches and number true negative (grdTP+TN) , 3) sum of all values (TP+TN+FP+FN) 
# Accuracy breakdowns are explained in the calculate_accuracy method
# Errors are appended to the error file designated in the configuration file, if it already exists.
   # Results .csv s are NOT appended. They will be overwritten if they already exist.

import utility
import string_distance
import re

class Comparison:
    def __init__(self, config_filename, config_name):
        self.config_name = config_name
        config = utility.load_json(config_filename)[config_name]
        self.config = config
        self.RUN_SPREADNAMES = config["LLM_SPREAD_SOURCES"]
        self.SOURCE_PATH = config["SOURCE_PATH"]
        self.GROUND_TRUTH_FILENAME = config["GROUND_TRUTH_FILENAME"]
        self.RECORD_REF_FIELDNAME = config["RECORD_REF_FIELDNAME"]
        self.RECORD_REFS = []
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
    
    def calculate_accuracy(self, master_results_dict, tallies):
        for key, val in tallies.items():
            master_results_dict[key] = val
        tp, tn, fp, fn = tallies["TPs"], tallies["TNs"], tallies["FPs"], tallies["FNs"]
        grdtp, grdfp = int(tallies["gradedTPs"]), int(tallies["gradedFPs"])
        master_results_dict["Correct:TP+TN"] = tp+tn
        master_results_dict["Errors:FP+FN"] = fp+fn

        # Accuracy1 is the sum of all true values divided by the sum of all values, true or false
        master_results_dict["TP+TN/TP+TN+FP+FN"] = f"{tp}+{tn}/{tp}+{tn}+{fp}+{fn}"
        master_results_dict["acc1:TP+TN/TP+TN+FP+FN"] = (tp+tn)/(tp+tn+fp+fn)

        # Accuracy2 substitutes graded matches and graded non-matches for TP and FP
        master_results_dict["grdTP+TN/grdTP+TN+grdFP+FN"] = f"{grdtp}+{tn}/{grdtp}+{tn}+{grdfp}+{fn}"
        master_results_dict["acc2:grdTP+TN/grdTP+TN+grdFP+FN"] = (grdtp+tn)/(grdtp+tn+grdfp+fn)

        # Accuracy3 leaves out true negatives, i.e., the true value is "N/A"
        master_results_dict["TP/TP+FP+FN"] = f"{tp}/{tp}+{fp}+{fn}"
        master_results_dict["acc3:TP/TP+FP+FN"] = tp/(tp+fp+fn)

         # Accuracy4 is like Accuracy3, but substituting graded matches and graded non-matches
        master_results_dict["grdTP/grdTP+grdFP+FN"] = f"{grdtp}/{grdtp}+{grdfp}+{fn}"
        master_results_dict["acc4:grdTP+TN/grdTP+TN+grdFP+FN"] = grdtp/(grdtp+grdfp+fn)
        return master_results_dict  

    def update_comparison_fields(self, d, master_comparison_dict):
        fieldname = d["fieldname"]
        master_comparison_dict[fieldname][0] += d["is_true_pos"] or d["is_true_neg"]
        master_comparison_dict[fieldname][1] += d["is_true_neg"] or d["gradedTP"]
        master_comparison_dict[fieldname][2] += d["is_true_pos"] or d["is_true_neg"] or d["is_false_pos"] or d["is_false_neg"]
        return master_comparison_dict

    def update_tallies(self, tallies, field_comparison_dict, master_comparison_dict):
        tallies["TPs"] += field_comparison_dict["is_true_pos"]
        tallies["TNs"] += field_comparison_dict["is_true_neg"]
        tallies["FPs"] += field_comparison_dict["is_false_pos"]
        tallies["FNs"] += field_comparison_dict["is_false_neg"]
        tallies["gradedTPs"] += field_comparison_dict["gradedTP"]
        tallies["gradedFPs"] += field_comparison_dict["gradedFP"]
        master_comparison_dict = self.update_comparison_fields(field_comparison_dict, master_comparison_dict)    
        return tallies, master_comparison_dict    

    def get_errors(self, d):
        if d["is_false_pos"] or d["is_false_neg"]:
           return {f"{self.RECORD_REF_FIELDNAME}": d["record_ref"], "fieldname": d["fieldname"], "observed_val": d["observed_val"], "true_val": d["true_val"], "gradedTP": d["gradedTP"], "gradedFP": d["gradedFP"]}
        return None   
             
    def get_graded_difference(self, observed_val, true_val):
        if observed_val == "N/A":   # don't bother getting the edit distance when the observed value is "N/A"; just return 1
            return 1       
        else:
            return self.edit_distance_interface.calculate_weighted_difference(observed_val, true_val)

    def grade(self, is_true_pos, is_false_pos, observed_val, true_val):
        if is_false_pos:
            graded_error = self.get_graded_difference(observed_val, true_val)
            gradedTP = 1 - graded_error
            gradedFP = graded_error
            return gradedTP, gradedFP
        else:
            return is_true_pos, is_false_pos   

    def is_true(self, observed_val, true_val):
        return observed_val.lower() == true_val.lower()

    def is_positive(self, val):
        return val != "N/A"

    def get_comparisons(self, fieldname, observed_val, true_val, record_ref):
        is_positive = self.is_positive(true_val)
        is_true = self.is_true(observed_val, true_val)
        true_pos = is_positive and is_true
        true_neg = not is_positive and is_true
        false_pos = is_positive and not is_true
        false_neg = not is_positive and not is_true
        gradedTP, gradedFP = self.grade(true_pos, false_pos, observed_val, true_val)
        return {"fieldname": fieldname, "observed_val": observed_val, "true_val": true_val, "is_true_pos": true_pos, "is_true_neg": true_neg, "is_false_pos": false_pos, "is_false_neg": false_neg, "gradedTP": gradedTP, "gradedFP": gradedFP, "record_ref": record_ref}    
    
    def compare_and_tally(self, observed_values_dicts, true_values_dicts, master_comparison_dict):
        tallies = {"TPs": 0, "TNs": 0, "FPs": 0, "FNs": 0, "gradedTPs": 0, "gradedFPs": 0}
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

    # use only core fields for comparison
    def get_core_fields_only(self, d: dict):
        return {key: val for key, val in d.items() if key in self.CORE_FIELDS_LIST}

    # this method determines whether to use core fields or just skip select fields
    def get_fields_to_be_compared(self, d: dict):
        return self.remove_skipped_fields(d) if not self.CORE_FIELDS_ONLY else  self.get_core_fields_only(d)

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
            utility.save_errors(self.RESULTS_PATH+self.ERRORS_FILENAME, run_errors, spreadname, self.config, self.RECORD_REF_FIELDNAME)
            print(f"Errors saved to {self.RESULTS_PATH+self.ERRORS_FILENAME}!!!!")  
        formatted_results = [utility.format_values(d) for d in master_results]    
        utility.save_to_csv(self.RESULTS_PATH+self.RESULT_FILENAME, formatted_results)
        print(f"Comaparisons saved to {self.RESULTS_PATH+self.RESULT_FILENAME}!!!!")   
    
if __name__ == "__main__":
    config_filename = "AccuracyTesting/transcription_config.json" 

    # copy in the name of the configuration to be used below
    config_name = ""

    accuracy_run = Comparison(config_filename, config_name)
    accuracy_run.run()