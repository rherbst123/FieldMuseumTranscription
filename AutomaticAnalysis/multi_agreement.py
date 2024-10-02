# This script takes a list of runs and compares each pair of runs to each other for agreed values.
# Only the agreed values are stored and saved (if there is no agreement in a field, a "PASS" is stored).abs
# The this script calls the parent class of Agreement, i.e., Comparison, to do a complete run against the ground truth.


from comparison_and_accuracy import Comparison
import utility
import re
import copy

class Agreement(Comparison):

    def is_same(self, s1, s2):
        return s1.strip().lower()==s2.strip().lower()
    
    def get_image_agreement_dict(self, img_results1, img_results2):
        d = {}
        for img1, img2 in zip(img_results1.items(), img_results2.items()):
            fieldname1, observed_val1 = img1
            fieldname2, observed_val2 = img2
            if self.is_same(fieldname1, fieldname2) and self.is_same(observed_val1, observed_val2):
                d[fieldname1] = observed_val1
            else:
                d[fieldname1] = "PASS"    
        return d
    
    
        
    def gather_data(self):
        saved_filenames = []
        for spreadname1 in self.RUN_SPREADNAMES[0]:
            for spreadname2 in self.RUN_SPREADNAMES[1]:
                for spreadname3 in self.RUN_SPREADNAMES[2]:
                    saved_results1: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname1)
                    saved_results2: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname2)
                    saved_results3: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname3)
                    observed_values_dicts1 = [self.get_fields_to_be_compared(d) for d in saved_results1]  
                    observed_values_dicts2 = [self.get_fields_to_be_compared(d) for d in saved_results2] 
                    observed_values_dicts3 = [self.get_fields_to_be_compared(d) for d in saved_results3] 
                    agreement_values1 = [self.get_image_agreement_dict(d1, d2) for d1, d2 in zip(observed_values_dicts1, observed_values_dicts2)]
                    agreement_values2 = [self.get_image_agreement_dict(d1, d2) for d1, d2 in zip(agreement_values1, observed_values_dicts3)] 
                    bare_spreadname1 = utility.remove_csv_extension(spreadname1)
                    bare_spreadname2 = utility.remove_csv_extension(spreadname2)
                    bare_spreadname3 =  utility.remove_csv_extension(spreadname3)
                    fname = f"{bare_spreadname1}_{bare_spreadname2}_{bare_spreadname3}_agreed_values.csv"
                    utility.save_to_csv(self.SOURCE_PATH+fname, agreement_values2)
                    print(f"prelimary results saved to {fname}")
                    saved_filenames += [fname]
        return saved_filenames       
    
if __name__ == "__main__":
    CONFIG_PATH = "AutomaticAnalysis/Configurations/"
    # copy in the name of the configuration file to be used below
    config_filename = "" 
    
    agreement = Agreement(CONFIG_PATH+config_filename)
    saved_filenames = agreement.gather_data()
    agreement.RUN_SPREADNAMES = saved_filenames
    agreement.run()