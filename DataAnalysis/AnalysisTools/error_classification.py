# for details, see DataAnalysis/Comparisons/Errors/ClassifiedErrors/README.md

import re
from itertools import combinations
from Utilities import utility

class ErrorClassifier:
    def __init__(self, fieldnames):
        self.fieldnames = fieldnames
        self.errors = ["spacing", "period", "positive polarity sign", "vowel diacritic", "comma", "dash"]
        error_combos: list[list[tuple]] = [list(combinations(self.errors, k)) for k in range(1,len(self.errors)+1)]
        self.error_combos: list[tuple] = self.flatten(error_combos)
        self.error_func_pairs = {"spacing": self.remove_whitespace, "period": self.remove_periods, "positive polarity sign": self.remove_polarity_signs, "vowel diacritic": self.to_english_alpha_vowels, "comma": self.remove_commas, "dash": self.remove_dashes}
        self.setup_tallies_dict()

    def setup_tallies_dict(self):
        self.tallies_dict = {fieldname: {elem: 0 for elem in [("total mismatches",)]+self.error_combos} for fieldname in self.fieldnames}

    def setup_comparison_dicts(self, transcription_filepath, ground_truth_filepath):
        self.transcriptions_dicts = utility.get_contents_from_csv(transcription_filepath)
        self.ground_truth_dicts = utility.get_contents_from_csv(ground_truth_filepath)

    def flatten(self, lists):
        return [elem for inner_list in lists for elem in inner_list]

    def extract_run_name_from_filepath(self, filepath):
        timestamp_pattern = r"\d\d\d\d-\d\d-\d\d-\d\d\d\d"
        mtch = re.search(fr".*/(.+-{timestamp_pattern})-.+", filepath)
        return mtch.group(1)

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
        self.tallies_dict[fieldname][("total mismatches",)] += 1
        for error_set in self.error_combos:
            temp_tran_val, temp_gt_val = transcription_val, ground_truth_val
            iterated_errors = []
            for error in error_set:
                iterated_errors += [error]
                func_name = self.error_func_pairs[error]
                temp_tran_val, temp_gt_val = func_name(temp_tran_val, temp_gt_val)
                if self.is_match(temp_tran_val, temp_gt_val):
                    self.tallies_dict[fieldname][tuple(iterated_errors)] += 1
                    self.tallies_dict[fieldname][(temp_tran_val,)] = f"{transcription_val}___{ground_truth_val}  ({', '.join(iterated_errors)})"
                    return

    def is_match(self, val1, val2):
        return val1.lower().strip() == val2.lower().strip()

    def compare(self, transcription_val, ground_truth_val, fieldname):
        if self.is_match(transcription_val, ground_truth_val):
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
            percentage =  round(100*(accounted_for_mismatches/total_mismatches), 1) if accounted_for_mismatches else "No mismatches to account for" if not total_mismatches else "No error combinations can account for mismatches!" 
            self.tallies_dict[fieldname] = {("percentage mismatches accounted for",): percentage} | self.tallies_dict[fieldname]
            
    def run(self, transcription_filepath, ground_truth_filepath):
        self.setup_comparison_dicts(transcription_filepath, ground_truth_filepath)
        self.iterate()
        self.calculate_percentages()
        self.save_to_txt(transcription_filepath)

    def __str__(self):
        tallies_dict = dict(sorted(self.tallies_dict.items()))
        return "\n".join([fieldname + "\n"+"\n".join([f"    {', '.join(error_set)}: {tally}" for error_set, tally in d.items() if tally]) for fieldname, d in tallies_dict.items()])                
    
    def save_to_txt(self, transcription_filepath):
        run_name = self.extract_run_name_from_filepath(transcription_filepath)
        errors_filepath = f"DataAnalysis/Comparisons/Errors/ClassifiedErrors/{run_name}-errors-classifications.txt"
        with open(errors_filepath, "w", encoding="utf-8") as f:
            f.write(str(self))

    @staticmethod
    def get_fieldnames_from_saved_data(filepath, skip_list):
        saved_dicts = utility.get_contents_from_csv(filepath)
        return  [key for key in saved_dicts[0].keys() if key not in skip_list] 


if __name__ == "__main__":
    # Enter the names of the files to be compared below.
    # No other modifications are necessary to run this script.
    transcription_filename = ""
    ground_truth_filename = ""
               ##########################
    transcription_folder = "DataAnalysis/Transcriptions/"
    transcriptions_filepath = transcription_folder+transcription_filename
    ground_truth_folder = "DataAnalysis/GroundTruths/"
    ground_truth_filepath = ground_truth_folder+ground_truth_filename
    skip_list = ["Image Name", "catalogNumber", "Dataset Source", "accessURI", "Label only?", "modifiedBy", "verifiedBy" , "substrate", "URL", "Image"]
    fieldnames = ErrorClassifier.get_fieldnames_from_saved_data(ground_truth_filepath, skip_list) 
    ec = ErrorClassifier(fieldnames)
    ec.run(transcriptions_filepath, ground_truth_filepath)
    