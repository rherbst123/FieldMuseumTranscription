# for details, see DataAnalysis/Comparisons/Errors/ClassifiedErrors/README.md

import re
import os
from itertools import combinations
import csv
#from Utilities import utility

class ErrorClassifier:
    def __init__(self, run_name, fieldnames):
        self.run_name = run_name
        self.fieldnames = fieldnames
        self.errors = ["spacing", "period", "positive polarity sign", "vowel diacritic", "comma", "dash", "extraneous preface"]
        error_combos: list[list[tuple]] = [list(combinations(self.errors, k)) for k in range(1,len(self.errors)+1)]
        self.error_combos: list[tuple] = self.flatten(error_combos)
        self.error_func_pairs = {"spacing": self.remove_whitespace, "period": self.remove_periods, "positive polarity sign": self.remove_polarity_signs, "vowel diacritic": self.to_english_alpha_vowels, "comma": self.remove_commas, "dash": self.remove_dashes, "extraneous preface": self.remove_prefaces_from_transcription}
        self.setup_tallies_dict()
        self.numbering = {fieldname: iter(range(1,1000)) for fieldname in fieldnames}

    def setup_paths(self, ground_truth_filename):
        transcription_filename = f"{self.run_name}-transcriptions.csv"           
        transcription_folder = "DataAnalysis/Transcriptions/"
        self.transcription_filepath = os.path.normpath(transcription_folder+transcription_filename)
        ground_truth_folder = "DataAnalysis/GroundTruths/"
        self.ground_truth_filepath = os.path.normpath(ground_truth_folder+ground_truth_filename)    

    def setup_tallies_dict(self):
        self.grand_totals = {"grand total mismatches": 0, "grand total mismatches accounted for": 0}
        self.tallies_dict = {fieldname: {elem: 0 for elem in [("total mismatches",)]+self.error_combos} for fieldname in self.fieldnames}

    def setup_comparison_dicts(self):
        self.transcriptions_dicts = ErrorClassifier.get_contents_from_csv(self.transcription_filepath)
        self.ground_truth_dicts = ErrorClassifier.get_contents_from_csv(self.ground_truth_filepath)

    def flatten(self, lists):
        return [elem for inner_list in lists for elem in inner_list]

    def extract_run_name_from_filepath(self, filepath):
        timestamp_pattern = r"\d\d\d\d-\d\d-\d\d-\d\d\d\d"
        mtch = re.search(fr".*/(.+-{timestamp_pattern})-.+", filepath)
        return mtch.group(1)

    def get_prefaces(self):
        return ["coll", "leg", "det", "collected by", "alt", "ca"]   

    def remove_prefaces_from_transcription(self, tran_val, gt_val):
        temp_tran_val = tran_val
        prefaces = self.get_prefaces()
        for preface in prefaces:
            temp_tran_val = re.sub(fr"{preface}\.?", "", temp_tran_val, flags=re.IGNORECASE)
        return temp_tran_val, gt_val     

    def remove_dashes(self, tran_val, gt_val):
        return re.sub("-", "", tran_val), re.sub("-", "", gt_val)  

    def remove_commas(self, tran_val, gt_val):
        return re.sub(r",\s?", "", tran_val), re.sub(r",\s?", "", gt_val)

    def get_vowel_pairs(self):  
        return {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú"}

    def to_english_alpha_vowels(self, tran_val, gt_val):
        vowel_pairs = self.get_vowel_pairs()
        temp_tran_val, temp_gt_val = tran_val, gt_val
        for en_vowel, non_en_vowel in vowel_pairs.items():
            temp_tran_val = re.sub(non_en_vowel, en_vowel, temp_tran_val)
            temp_gt_val = re.sub(non_en_vowel, en_vowel, temp_gt_val)
        return temp_tran_val, temp_gt_val    

    def remove_polarity_signs(self, tran_val, gt_val):
        plus_minus_symbol = u"\u00B1"
        tran_val = re.sub(plus_minus_symbol, "", tran_val)
        gt_val = re.sub(plus_minus_symbol, "", gt_val)
        return re.sub(r"\+", "", tran_val), re.sub(r"\+", "", gt_val)  

    def remove_periods(self, tran_val, gt_val):
        return re.sub("\.", "", tran_val), re.sub("\.", "", gt_val)  

    def remove_whitespace(self, tran_val, gt_val):
        return re.sub(r" ", "", tran_val), re.sub(r" ", "", gt_val)    

    def classify(self, transcription_val, ground_truth_val, fieldname):
        self.grand_totals["grand total mismatches"] += 1
        self.tallies_dict[fieldname][("total mismatches",)] += 1
        for error_set in self.error_combos:
            temp_tran_val, temp_gt_val = transcription_val, ground_truth_val
            iterated_errors = []
            for error in error_set:
                iterated_errors += [error]
                func_name = self.error_func_pairs[error]
                temp_tran_val, temp_gt_val = func_name(temp_tran_val, temp_gt_val)
                if self.is_match(temp_tran_val, temp_gt_val):
                    self.grand_totals["grand total mismatches accounted for"] += 1
                    self.tallies_dict[fieldname][tuple(iterated_errors)] += 1
                    mismatch_accounted_for_number = f"{next(self.numbering[fieldname])}. "
                    str_error_set = ', '.join(iterated_errors)
                    spaces = (6+len(mismatch_accounted_for_number)+len(str_error_set)) * " "
                    self.tallies_dict[fieldname][(f"{mismatch_accounted_for_number}{str_error_set}",)] = f"{transcription_val}___{ground_truth_val}\n{spaces}{temp_tran_val}___{temp_gt_val}"
                    
                    return

    def is_match(self, val1, val2):
        return val1.lower().strip() == val2.lower().strip()

    def compare(self, transcription_val, ground_truth_val, fieldname):
        if self.is_match(transcription_val, ground_truth_val) or transcription_val == "PASS":
            return
        self.classify(transcription_val, ground_truth_val, fieldname)    

    def iterate(self):
        for transcription_dict, ground_truth_dict in zip(self.transcriptions_dicts, self.ground_truth_dicts):
            for fieldname in self.fieldnames:
                transcription_val = transcription_dict[fieldname]
                ground_truth_val = ground_truth_dict[fieldname]
                self.compare(transcription_val, ground_truth_val, fieldname)

    def calculate_percentages(self):
        for fieldname in self.tallies_dict:
            accounted_for_mismatches = sum([self.tallies_dict[fieldname][error_set] for error_set in self.error_combos])
            total_mismatches = self.tallies_dict[fieldname][("total mismatches",)]
            field_percentage =  round(100*(accounted_for_mismatches/total_mismatches), 1) if accounted_for_mismatches else "No mismatches to account for" if not total_mismatches else "No error combinations can account for mismatches!" 
            self.tallies_dict[fieldname] = {("percentage mismatches accounted for",): field_percentage} | self.tallies_dict[fieldname]
            
    def run(self, run_name, ground_truth_filename):
        self.setup_paths(ground_truth_filename)
        self.setup_comparison_dicts()
        self.iterate()
        self.calculate_percentages()
        self.save_to_txt(run_name)

    def __str__(self):
        overall_percentage = round(100*(self.grand_totals["grand total mismatches accounted for"]/self.grand_totals["grand total mismatches"]), 1)
        self.grand_totals["overall percentage mismatches accounted for"] = overall_percentage
        grand_totals = "\n".join([f"{key}: {val}" for key, val in self.grand_totals.items()]) + "\n"
        tallies_dict = dict(sorted(self.tallies_dict.items()))
        return grand_totals + "\n".join([fieldname + "\n"+"\n".join([f"    {', '.join(error_set)}: {tally}" for error_set, tally in d.items() if tally]) for fieldname, d in tallies_dict.items()])                
    
    def save_to_txt(self, run_name):
        errors_filepath = f"DataAnalysis/Comparisons/Errors/ClassifiedErrors/{run_name}-errors-classifications.txt"
        with open(errors_filepath, "w", encoding="utf-8") as f:
            f.write(str(self))

    @staticmethod
    def get_contents_from_csv(csv_file_path):
        with open(csv_file_path, 'r', encoding='utf-8', newline='') as csvfile:
            return list(csv.DictReader(csvfile))           

    @staticmethod
    def get_fieldnames_from_saved_data(filepath):
        skip_list = ["Image Name", "catalogNumber", "Dataset Source", "accessURI", "Label only?", "modifiedBy", "verifiedBy" , "substrate", "URL", "Image"]
        saved_dicts = ErrorClassifier.get_contents_from_csv(filepath)
        return  [key for key in saved_dicts[0].keys() if key not in skip_list] 


if __name__ == "__main__":
    # Enter the names of the files to be compared below.
    # No other modifications are necessary to run this script.
    run_name = "claude-3.5-sonnet-v2-2024-10-28-1111" #"claude-3.5-sonnet-2024-06-21-1043" "gpt-4o-2024-06-11-1110"
    ground_truth_filename = "100-bryophytes-typed.csv"
               ##########################
    
    
    fieldnames = ErrorClassifier.get_fieldnames_from_saved_data(transcriptions_filepath) 
    ec = ErrorClassifier(fieldnames)
    ec.run(run_name, ground_truth_filename)
    