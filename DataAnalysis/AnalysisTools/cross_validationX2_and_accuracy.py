# This script takes a list of runs and compares each pair of runs to each other for agreed values.
# Only the agreed values are stored and saved (if there is no agreement in a field, a "PASS" is stored).abs
# The this script calls the parent class of Agreement, i.e., Comparison, to do a complete run against the ground truth.


from comparison_and_accuracy import Comparison
from Utilities import utility
import re
import copy

class CrossValidationX2(Comparison):

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
    
    def remove_timestamp_and_extension(self, fname):
        return re.match(r"(.+?)-2024|5.+", fname).group(1)

    def shorten_filename(self, fname):
        return re.sub("-transcriptions.csv", "", fname)
    
        
    def gather_data(self):
        saved_filenames = []
        for spreadname1 in self.RUN_SPREADNAMES[0]:
            for spreadname2 in self.RUN_SPREADNAMES[1]:
                for spreadname3 in self.RUN_SPREADNAMES[2]:
                    saved_results1: list[dict] = utility.get_contents_from_csv(self.TRANSCRIPTIONS_PATH+spreadname1)
                    saved_results2: list[dict] = utility.get_contents_from_csv(self.TRANSCRIPTIONS_PATH+spreadname2)
                    saved_results3: list[dict] = utility.get_contents_from_csv(self.TRANSCRIPTIONS_PATH+spreadname3)
                    self.set_fields_to_be_compared()
                    model1 = "sonnet-3.5"#self.remove_timestamp_and_extension(spreadname1)
                    model2 = "gpt-4o-cropped"#self.remove_timestamp_and_extension(spreadname2)
                    model3 = "gpt-4o-collage"#self.remove_timestamp_and_extension(spreadname3)
                    modelname = f"{model1}_{model2}_{model3}"
                    print(f"{modelname = }")    
                    agreement_values1 = [self.get_image_agreement_dict(d1, d2) for d1, d2 in zip(saved_results1, saved_results2)]
                    agreement_values2 = [self.get_image_agreement_dict(d1, d2) for d1, d2 in zip(agreement_values1, saved_results3)] 
                    agreement_values2 = [{"modelname": modelname} | d for d in agreement_values2]
                    bare_spreadname1 = self.shorten_filename(spreadname1)
                    bare_spreadname2 = self.shorten_filename(spreadname2)
                    bare_spreadname3 =  self.shorten_filename(spreadname3)
                    fname = f"{bare_spreadname1}_{bare_spreadname2}_{bare_spreadname3}-transcriptions.csv"
                    print(f"saving: {fname = }")
                    utility.save_to_csv(self.TRANSCRIPTIONS_PATH+fname, agreement_values2)
                    print(f"prelimary results saved to {fname}")
                    saved_filenames += [fname]
        return saved_filenames       
    
if __name__ == "__main__":
    CONFIG_PATH = "DataAnalysis/AnalysisTools/Configurations/"
    # copy in the name of the configuration file to be used below
    config_filename = "multi_agreement_image_manipulation.yaml" 
    configuration = Comparison.read_configuration_from_yaml(CONFIG_PATH, config_filename)
    cv = CrossValidationX2(configuration, config_filename)
    saved_filenames = cv.gather_data()
    cv.RUN_SPREADNAMES = saved_filenames
    cv.run()