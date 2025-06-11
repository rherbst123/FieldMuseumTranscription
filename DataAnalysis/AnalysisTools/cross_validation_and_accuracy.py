# This script takes a list of runs and compares each pair of runs to each other for agreed values.
# Only the agreed values are stored and saved (if there is no agreement in a field, a "PASS" is stored).abs
# The this script calls the parent class of Agreement, i.e., Comparison, to do a complete run against the ground truth.


# A few methods have been added that override the parent class in order to give breakdowns on
# 1) the percentage of valid targets that were skipped during comparison with ground truth,
#       as there was no agreement between the two runs and we are looking strictly at cross-validation accuracy
# 2) the percentage of all targets that were skipped during comparision with ground truth.

from comparison_and_accuracy import Comparison
from Utilities import utility
import re

class CrossValidation(Comparison):

    def calculate_accuracy(self, master_results_dict, tallies):
        for key, val in tallies.items():
            master_results_dict[key] = val
        matchValid, matchNonValid, noMatchValid, noMatchNonValid = tallies["matchValid"], tallies["matchNonValid"], tallies["noMatchValid"], tallies["noMatchNonValid"]
        numSkippedValid, numSkippedNonValid = tallies["skippedValid"], tallies["skippedNonValid"]
        master_results_dict["NumValidTargets"] = matchValid + noMatchValid + numSkippedValid
        master_results_dict["NumAllTargets"] = matchValid + noMatchValid + noMatchNonValid + matchNonValid + numSkippedValid + numSkippedNonValid
        master_results_dict["PercentSkippedValidTargets"] = numSkippedValid/(matchValid + noMatchValid + numSkippedValid)
        master_results_dict["PercentSkippedAllTargets"] = (numSkippedValid + numSkippedNonValid) /(matchValid + noMatchValid + noMatchNonValid + matchNonValid + numSkippedValid + numSkippedNonValid)
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

    def compare_and_tally(self, transcription_values_dicts, master_comparison_dict):
        tallies = {"matchValid": 0, "matchNonValid": 0, "noMatchValid": 0, "noMatchNonValid": 0, "gradedMatchValid": 0, "gradedNoMatchValid": 0, "skippedValid": 0, "skippedNonValid": 0}
        run_errors = []
        for record_ref, transcription_values_dict, target_values_dict in zip(self.RECORD_REFS, transcription_values_dicts, self.target_values_dicts):
            for fieldname in self.fieldnames:
                target_val = target_values_dict[fieldname]
                transcription_val = transcription_values_dict[fieldname]
                if transcription_val.strip() in ["PASS", "unsure and check", "[precise locality unknown]"]:
                    is_valid = self.is_valid(target_val)
                    tallies["skippedValid"] += is_valid
                    tallies["skippedNonValid"] += not is_valid
                    continue  # Just in case the LLM doesn't hazard a guess,
                                 # or there are gaps in some of the fields of observed values.
                                   # This is used when runs are compared for agreement
                                     #  and only agreed values are to be compared against true values
                field_comparison_dict = self.get_comparisons(fieldname, transcription_val, target_val, record_ref)
                tallies, master_comparison_dict = self.update_tallies(tallies, field_comparison_dict, master_comparison_dict)
                run_errors += [self.get_errors(field_comparison_dict)]
        return master_comparison_dict, tallies, run_errors     

    def is_same(self, s1, s2):
        return s1.strip().lower()==s2.strip().lower()
    
    def get_image_agreement_dict(self, img_results1, img_results2):
        d = {}
        for fieldname in self.fieldnames:
            observed_val1 = img_results1[fieldname]
            observed_val2 = img_results2[fieldname]
            if self.is_same(observed_val1, observed_val2):
                d[fieldname] = observed_val1
            else:
                d[fieldname] = "PASS"    
        return d

    def gather_data(self):
        self.load_data()
        saved_filenames = []
        print(f"{self.RUN_SPREADNAMES = }")
        for idx, spreadname1 in enumerate(self.RUN_SPREADNAMES):
            for spreadname2 in self.RUN_SPREADNAMES[idx+1:]:
                print(f"{spreadname1 = }, {spreadname2 = }")
                observed_values_dicts1 = self.master_transcription_values_dicts[spreadname1]  
                observed_values_dicts2 = self.master_transcription_values_dicts[spreadname2]
                self.set_fields_to_be_compared() 
                agreement_values = [self.get_image_agreement_dict(d1, d2) for d1, d2 in zip(observed_values_dicts1, observed_values_dicts2)] 
                bare_spreadname1 = re.sub(r"-transcriptions.csv", "", spreadname1)
                bare_spreadname2 = re.sub(r"-transcriptions.csv", "", spreadname2 )
                fname = f"{bare_spreadname1}-{bare_spreadname2}-cross-validated_values-transcriptions.csv"
                utility.save_to_csv(self.TRANSCRIPTIONS_PATH+fname, agreement_values)
                print(f"prelimary results saved to {fname}")
                saved_filenames += [fname]
        return saved_filenames           
    
if __name__ == "__main__":
    CONFIG_PATH = "DataAnalysis/AnalysisTools/Configurations/"
    # copy in the name of the configuration file to be used below
    config_filename = "nova_cross_validation.yaml" 
     
    config = CrossValidation.read_configuration_from_yaml(CONFIG_PATH, config_filename)
    cv = CrossValidation(config, config_filename)
    saved_filenames = cv.gather_data()
    cv.RUN_SPREADNAMES = saved_filenames
    cv.run()