from comparison_and_accuracy import Comparison
import utility
import re

class Agreement(Comparison):
    
    def get_image_agreement_dict(self, img_results1, img_results2):
        d = {}
        for img1, img2 in zip(img_results1.items(), img_results2.items()):
            fieldname1, observed_val1 = img1
            fieldname2, observed_val2 = img2
            if not self.is_different(fieldname1, fieldname2) and not self.is_different(observed_val1, observed_val2):
                d[fieldname1] = observed_val1
            else:
                d[fieldname1] = "PASS"    
        return d
    
    
        
    def gather_data(self):
        saved_filenames = []
        for idx, spreadname1 in enumerate(self.RUN_SPREADNAMES):
            for spreadname2 in self.RUN_SPREADNAMES[idx+1:]:
                saved_results1: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname1)
                saved_results2: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname2)
                observed_values_dicts1 = [self.get_fields_to_be_compared(d) for d in saved_results1]  
                observed_values_dicts2 = [self.get_fields_to_be_compared(d) for d in saved_results2]  
                agreement_values = [self.get_image_agreement_dict(d1, d2) for d1, d2 in zip(observed_values_dicts1, observed_values_dicts2)] 
                bare_spreadname1 = utility.remove_extension(spreadname1)
                bare_spreadname2 = utility.remove_extension(spreadname2)
                fname = f"{bare_spreadname1}_{bare_spreadname2}_agreed_values.csv"
                utility.save_to_csv(self.SOURCE_PATH+fname, agreement_values)
                saved_filenames += [fname]
        return saved_filenames       
    
if __name__ == "__main__":
    config_filename = "AccuracyTesting/transcription_config.json" 
    config_name = "gpt4o and sonnet3.5 agreement"
    config = utility.load_json(config_filename)[config_name]
    accuracy_run = Agreement(config)
    saved_filenames = accuracy_run.gather_data()
    accuracy_run.RUN_SPREADNAMES = saved_filenames
    accuracy_run.run()