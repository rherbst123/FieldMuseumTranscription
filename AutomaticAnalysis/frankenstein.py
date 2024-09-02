# This script takes a list of runs and compares each pair of runs to each other for agreed values.
# Only the agreed values are stored and saved (if there is no agreement in a field, a "PASS" is stored).abs
# The this script calls the parent class of Agreement, i.e., Comparison, to do a complete run against the ground truth.


from comparison_and_accuracy import Comparison
import utility
import re

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
    
    def get_full_dict(self, img_results1, img_results2, obsd1, obsd2):
        d = {}
        for img1, img2, obs1, obs2 in zip(img_results1.items(), img_results2.items(), obsd1.items(), obsd2.items()):
            fieldname1, observed_val1 = img1
            fieldname2, observed_val2 = img2
            f3, gpt_val1 = obs1
            f4, gpt_val2 = obs2
            if fieldname1 != fieldname2 or fieldname1 != f3 or fieldname1 != f4:
                print("oh oh")
            if observed_val1 == "PASS" and observed_val2 == "PASS":
                d[fieldname1] = gpt_val1
            elif observed_val1 == "PASS":
                d[fieldname1] = gpt_val1
            elif observed_val2 == "PASS":
                d[fieldname1] = gpt_val1
            elif self.is_same(observed_val1, observed_val2):
                d[fieldname1] = observed_val1    
            else:
                print(f"that's a pickle: {observed_val1 = }, {observed_val2 = }")  
                print(f"going with: {gpt_val1 = }") 
                d[fieldname1] = gpt_val1       
        return d

    def get_field_accuracy_average(self, fieldname, model_dict):
        #print(f"{model_dict[fieldname] = }")
        #model_dict[fieldname] = '[42, 77.8, 100]'
        mtch = re.search(r"\[(\d+), (.+?), (\d+)\]", model_dict[fieldname])
        correct = int(mtch.group(1)) 
        edit_distance = float(mtch.group(2)) 
        out_of = int(mtch.group(3))
        #print(f"{correct = }, {out_of = }") 
        #return edit_distance / out_of
        return correct / out_of 

    def get_complete_dict(self, agreement_dict, model1_scores, model2_scores, model1_alt_dict, model2_alt_dict):
        print(f"{model1_scores = }")
        print(f"{model2_scores = }")
        d = {}
        for fieldname, observed_val in agreement_dict.items():
            if observed_val != "PASS":
                d[fieldname] = observed_val
            elif self.get_field_accuracy_average(fieldname, model1_scores) > self.get_field_accuracy_average(fieldname, model2_scores):
                d[fieldname] = model1_alt_dict[fieldname]
                self.gpt_is_better += 1
            elif self.get_field_accuracy_average(fieldname, model1_scores) < self.get_field_accuracy_average(fieldname, model2_scores):
                d[fieldname] = model1_alt_dict[fieldname]
                self.sonnet_is_better +=1
            else:
                d[fieldname] = model1_alt_dict[fieldname]
                self.its_a_tie += 1

        #return agreement_dict
        return d        

    
        
    def gather_data(self):
        saved_filenames = []
        spreadname1, *spreadnames = self.RUN_SPREADNAMES
        for idx, spreadname2 in enumerate(spreadnames):
                saved_results1: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname1)
                saved_results2: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname2)
                observed_values_dicts1 = [self.get_fields_to_be_compared(d) for d in saved_results1]  
                observed_values_dicts2 = [self.get_fields_to_be_compared(d) for d in saved_results2]  
                agreement_values = [self.get_image_agreement_dict(d1, d2) for d1, d2 in zip(observed_values_dicts1, observed_values_dicts2)] 
                bare_spreadname1 = utility.remove_csv_extension(spreadname1)
                bare_spreadname2 = utility.remove_csv_extension(spreadname2)
                fname = f"{idx}.csv"
                utility.save_to_csv(self.SOURCE_PATH+fname, agreement_values)
                saved_filenames += [fname]
                spreadname1 = fname
        return saved_filenames

    def cross_validate_then_complete(self):
        f1, f2, f3, f4 = self.RUN_SPREADNAMES
        agreed_results = []
        for pair in [(f1,f3),(f2,f4)]:
            spreadname1, spreadname2 = pair
            saved_results1: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname1)
            saved_results2: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname2)
            observed_values_dicts1 = [self.get_fields_to_be_compared(d) for d in saved_results1]  
            observed_values_dicts2 = [self.get_fields_to_be_compared(d) for d in saved_results2] 
            agreement_values = [self.get_image_agreement_dict(d1, d2) for d1, d2 in zip(observed_values_dicts1, observed_values_dicts2)]
            agreed_results += [agreement_values]
        agr1, agr2 = agreed_results
        saved_results1: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+f1)
        saved_results2: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+f2)
        obs1 = [self.get_fields_to_be_compared(d) for d in saved_results1]  
        obs2 = [self.get_fields_to_be_compared(d) for d in saved_results2]  
        complete_dict =  [self.get_full_dict(d1, d2, obsd1, obsd2) for d1, d2, obsd1, obsd2 in zip(agr1, agr2, obs1, obs2)] 
        bare_spreadname1 = utility.remove_csv_extension(f1)
        bare_spreadname2 = utility.remove_csv_extension(f2)
        bare_spreadname3 = utility.remove_csv_extension(f3)
        bare_spreadname4 = utility.remove_csv_extension(f4)
        fname = f"{bare_spreadname1}_{bare_spreadname2}_{bare_spreadname3}_{bare_spreadname4}_complete.csv"
        utility.save_to_csv(self.SOURCE_PATH+fname, complete_dict)
      
        return [fname]

    def cross_validate_then_complete_fields_algorithmically(self):
        self.sonnet_is_better,  self.gpt_is_better, self.its_a_tie = 0,0,0
        source_model1, alt_source_model1, source_model2, alt_source_model2 = self.RUN_SPREADNAMES
        saved_run1: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+source_model1)
        saved_run2: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+source_model2)
        saved_run_alt1: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+alt_source_model1)
        saved_run_alt2: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+alt_source_model2)
        observed_values_dicts1 = [self.get_fields_to_be_compared(d) for d in saved_run1]  
        observed_values_dicts2 = [self.get_fields_to_be_compared(d) for d in saved_run2] 
        alt_observed_values_dicts1 = [self.get_fields_to_be_compared(d) for d in saved_run_alt1]  
        alt_observed_values_dicts2 = [self.get_fields_to_be_compared(d) for d in saved_run_alt2] 
        agreement_values = [self.get_image_agreement_dict(d1, d2) for d1, d2 in zip(observed_values_dicts1, observed_values_dicts2)]
        #print(f"{agreement_values = }")
        saved_scored_results: list[dict] = utility.get_contents_from_csv(self.RESULTS_PATH+"gpt4o_and_sonnet3.5_repeats.csv")
        scored_model = [self.get_fields_to_be_compared(d) for d in saved_scored_results] 
        #print(f"{scored_model = }") 
        complete_dict =  [self.get_complete_dict(agreement_dict, scored_model[1], scored_model[3], alt_model1_dict, alt_model2_dict) for agreement_dict, alt_model1_dict, alt_model2_dict in zip(agreement_values, alt_observed_values_dicts1, alt_observed_values_dicts2)] 
        fname = "gpt_sonnet_agree_then_complete.csv"
        #print(f"{complete_dict = }")
        print(f"{self.sonnet_is_better = }, {self.gpt_is_better = }, {self.its_a_tie = }")
        utility.save_to_csv(self.SOURCE_PATH+fname, complete_dict)
      
        return [fname]



    def fill_out_the_blanks(self):
        f1, f2, f3, f4 = self.RUN_SPREADNAMES
        all_results = []
        for spreadname1, spreadname2, spreadname3 in [(f1,f3,f2),(f2,f4,f1), (f1, f3, f4), (f2, f4, f3)]:
            saved_results1: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname1)
            saved_results2: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname2)
            saved_results3: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname3)
            observed_values_dicts1 = [self.get_fields_to_be_compared(d) for d in saved_results1]  
            observed_values_dicts2 = [self.get_fields_to_be_compared(d) for d in saved_results2] 
            observed_values_dicts3 = [self.get_fields_to_be_compared(d) for d in saved_results3]  
            agreement_values = [self.get_image_agreement_dict(d1, d2) for d1, d2 in zip(observed_values_dicts1, observed_values_dicts2)] 
            complete_dict =  [self.get_full_dict(d1, d2) for d1, d2 in zip(observed_values_dicts3, agreement_values)] 
            bare_spreadname1 = utility.remove_csv_extension(spreadname1)
            bare_spreadname2 = utility.remove_csv_extension(spreadname2)
            bare_spreadname3 = utility.remove_csv_extension(spreadname3)
            
            fname = f"{bare_spreadname1}_{bare_spreadname2}_{bare_spreadname3}_complete.csv"
            utility.save_to_csv(self.SOURCE_PATH+fname, complete_dict)
            all_results += [fname]
        return all_results
                 
    
if __name__ == "__main__":
    # copy in the name of the configuration file to be used below
    config_filename = "" 
    
    agreement = Agreement(config_filename)
    saved_filenames = agreement.cross_validate_then_complete_fields_algorithmically()
    agreement.RUN_SPREADNAMES = saved_filenames
    agreement.run()