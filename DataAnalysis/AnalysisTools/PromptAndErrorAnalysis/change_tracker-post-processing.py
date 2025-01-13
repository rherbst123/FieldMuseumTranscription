import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import utility
import re
import get_prompts_as_dict
import field_accuracy
from postprocessing2 import PostProcessor
from error_classification import ErrorClassifier
import field_classified_errors
from copy import deepcopy

class ChangeTracker:
    def __init__(self, field_methods, error_data: dict[dict], accuracy_data: dict[dict], fieldnames, run_names):
        
        self.error_data = error_data
        self.accuracy_data = accuracy_data
        self.fieldnames = fieldnames
        self.methods_applied = field_methods | {f"all {len(fieldnames)} fields": "all methods"}
        self.run_names = run_names
        self.set_master_error_combos_used()

    def set_master_error_combos_used(self):
        self.master_error_combos_used = []
        for run, data in self.error_data.items():
            self.update_error_combos_used(data["error_combos_used"])


    def update_error_combos_used(self, error_combos_used):
        for error_combo in error_combos_used:
            if error_combo not in self.master_error_combos_used:
                self.master_error_combos_used += [error_combo]    
        
    def get_changes(self):
        lines = []
        for fieldname in sorted(self.fieldnames) + [f"all {len(self.fieldnames)} fields"]:
            for run_name in self.run_names:
                last_accuracy, last_graded_match, last_error_set, last_num_mismatches = "N/A", "N/A", [], 0
                for __ in range(2):
                    accuracy_data = self.accuracy_data[run_name]
                    error_data = self.error_data[run_name]
                    d, last_accuracy, last_graded_match, last_error_set, last_num_mismatches = self.associate_changes(fieldname, accuracy_data, last_accuracy, last_graded_match, error_data, last_error_set, last_num_mismatches, run_name)
                    lines.append(self.format_values(d))
                    run_name = f"post_{run_name}"
                lines.append({})    
            lines.append({})
            lines.append({})
        return lines    

    def format_values(self, d):
        return {field: "" if val == "N/A" else val for field, val in d.items()} 
                           
    def associate_changes(self, fieldname, accuracy_data, last_accuracy, last_graded_match, error_data, last_error_set, last_num_mismatches, run_name):#(self, fieldname, error_datum, accuracy_datum, last_accuracy, last_graded_match, last_field_method, last_error_sets):
            d = {}
            field_method = self.methods_applied[fieldname]
            d["run name"] = run_name
            d["fieldname"] = fieldname
            d["method"] = field_method
            error_set = error_data.get(fieldname, {})
            num_mismatches = self.count_mismatches(error_set)
            accuracy, graded_match = accuracy_data.get(fieldname, "N/A"), accuracy_data.get(f"{fieldname}GRD", "N/A")
            d = self.get_data_changes(d, accuracy, last_accuracy, graded_match, last_graded_match, num_mismatches, last_num_mismatches)
            d = d | self.get_error_changes(error_set, last_error_set)
            return d, accuracy, graded_match, error_set, num_mismatches

    def get_error_changes(self, error_set, last_error_set):
        total = {"sum": sum([len(key)*val for key, val in error_set.items()])}
        return {"   ": "", "itemized": "", "errors": "", "  ------>": ""} | {",".join(error_combo): error_set[error_combo] if error_combo in error_set else 0 for error_combo in self.master_error_combos_used} | total

                       

    def get_diff(self, val1, val2):
        return "N/A" if "N/A" in [val1, val2] or "NaN" in [val1, val2] else val2 - val1

    def count_mismatches(self, error_sets):
        if not error_sets:
            return 0
        return sum([val for key, val in error_sets.items()])                     

    def get_data_changes(self, d, accuracy, last_accuracy, gradedMatch, last_graded_match, num_mismatches, last_num_mismatches):
        d["gradedMatch"] = gradedMatch
        d["diff gradedMatch"] = self.get_diff(last_graded_match, gradedMatch)
        d["accuracy"] = accuracy
        d["diff accuracy"] = self.get_diff(last_accuracy, accuracy)
        d["num mismatches"] = num_mismatches
        d["diff mismatches"] = last_num_mismatches - num_mismatches if last_num_mismatches else "N/A"
        return d    

class TrackFieldAccuracy:
    def __init__(self, config_filename, batch_comparisons_filename):
        self.setup(config_filename)
        self.batch_comparisons_folder = "DataAnalysis/Comparisons/BatchComparisons/"
        self.batch_comparisons_filepath = self.batch_comparisons_folder+batch_comparisons_filename

    def setup(self, config_filename):
        config_folder = "DataAnalysis/AnalysisTools/Configurations/"
        config = utility.load_yaml(config_folder+config_filename)
        self.post = PostProcessor(config, config_filename)
        self.run_names = self.post.RUN_NAMES
        self.fieldnames = self.post.POST_PROCESSING_CONFIG
        self.ground_truth_filename = self.post.GROUND_TRUTH_FILENAME
        self.run_names = self.post.RUN_NAMES
        methods = self.post.get_field_methods()
        self.field_methods = {fieldname: method_name.__name__ for fieldname, method_name in methods.items()}
        
        

    def get_classified_errors_dict(self):
        classified_errors_dict = {}
        for run_name in self.run_names:
            orig = field_classified_errors.get_fields_classified_errors(run_name, self.fieldnames, self.ground_truth_filename)
            classified_errors_dict[run_name] = orig
            post = field_classified_errors.get_fields_classified_errors(f"post_{run_name}", self.fieldnames, self.ground_truth_filename)
            classified_errors_dict[f"post_{run_name}"] = post
        return classified_errors_dict 

    def extract_run_name_from_transcriptions_filename(self, filename):
        timestamp_pattern = r"\d\d\d\d-\d\d-\d\d-\d\d\d\d"
        mtch = re.search(fr"(.+-{timestamp_pattern})-transcriptions.csv", filename)
        return mtch.group(1)           

    def get_field_accuracy_dict_from_batch_file(self):
        results = utility.get_contents_from_csv(self.batch_comparisons_filepath)
        field_accuracy_dict = {}
        for idx in range(0,len(results),2):
            orig = field_accuracy.get_fields_accuracy(results[idx], self.fieldnames)
            orig_run_name = self.extract_run_name_from_transcriptions_filename(results[idx]["run"])
            field_accuracy_dict[orig_run_name] = orig
            post = field_accuracy.get_fields_accuracy(results[idx+1], self.fieldnames)
            post_run_name = self.extract_run_name_from_transcriptions_filename(results[idx+1]["run"])
            field_accuracy_dict[post_run_name] = post
        return field_accuracy_dict  

    def save_to_csv(self, data):
        run_name = "post_processing"
        filepath = f"{self.batch_comparisons_folder}{run_name}-changes.csv"
        utility.save_to_csv(filepath, data)
        print(f"saved to {filepath} !!!")       

    def run(self):
        field_accuracy_dict = self.get_field_accuracy_dict_from_batch_file()
        classified_error_dict = self.get_classified_errors_dict()
        ct = ChangeTracker(self.field_methods, classified_error_dict, field_accuracy_dict, self.fieldnames, self.run_names)
        changes = ct.get_changes()
        self.save_to_csv(changes)

if __name__ == "__main__":
    batch_comparisons_filename = "prompt1.5.2-postprocessed-comparisons.csv"
    config_filename = "latest_prompt_runs.yaml"
    tfa = TrackFieldAccuracy(config_filename, batch_comparisons_filename)
    tfa.run()
    #r = tfa.get_classified_errors_dicts()
    #print(r)
    #r2 = tfa.get_field_accuracy_dicts()
    #print(r2)
