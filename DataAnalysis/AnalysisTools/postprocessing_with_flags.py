# This script is like postprocessing.py, 
### but it also flags when post-processing "undoes" or "miscorrects" 
##### matches between transcriptions and ground truth

import logging
from Utilities import utility
import string_distance
import re
from comparison_and_accuracy import Comparison
from tolerances import FieldTolerances
from string_distance import WeightedLevenshtein

class PostProcessor(Comparison):
        
    def get_field_methods(self):
        return {"verbatimCollectors": self.remove_name_identifiers,
                "secondaryCollectors": self.name_compliance,
                "collectedBy": self.name_compliance,
                "identifiedBy": self.name_compliance,
                "locality": self.remove_additional_comments,
                "verbatimElevation": self.remove_altitude_identifiers}

    def check_for_correction(self, original_val, post_val, target_val):
        field_method = self.field_method.__name__
        if original_val == target_val and post_val != target_val:
            print(f"MISCORRECTION!!! {self.current_image_ref = }, {field_method = }, {target_val = }, {original_val = }, {post_val = }")
        elif post_val == target_val and original_val != target_val:
            pass
            #print("YAY!!!") 
            #print(f"corrected!!! {field_method = }, {target_val = }, {original_val = }, {post_val = }")  

    def abbreviation_point_compliance(self, val, target_val):
        temp_val = re.sub(r"([A-Z]?\.)([A-Z])", r"\1 \2", val)
        temp_val = re.sub(r"([A-Z])( )", r"\1. ",temp_val)
        self.check_for_correction(val, temp_val, target_val)
        return temp_val

    def name_compliance(self, val, target_val):
        temp_val = self.remove_name_identifiers(val, target_val)
        temp_val = self.abbreviation_point_compliance(temp_val, target_val)
        self.check_for_correction(val, temp_val, target_val) 
        return temp_val   
    
    def remove_additional_comments(self, val, target_val):
        temp_val =  re.sub(r"(.+) ?\[.+\]", r"\1", val)  
        self.check_for_correction(val, temp_val, target_val)
        return temp_val
                  
    def remove_name_identifiers(self, val, target_val):
        words = val.split()
        temp_val =  " ".join([w.strip() for w in words if w.strip().lower() not in ["coll.", "coll", "leg.", "leg", "det.", "det"]])
        self.check_for_correction(val, temp_val, target_val)
        return temp_val

    def remove_altitude_identifiers(self, val, target_val):
        words = val.split()
        temp_val =  " ".join([w.strip() for w in words if w.strip() not in ["alt.", "alt", "Alt.", "Alt"]]) 
        self.check_for_correction(val, temp_val, target_val)
        return temp_val    

    def check_fields(self, fieldname, val, target_val):
        field_methods = self.get_field_methods()
        if fieldname in field_methods and fieldname in self.POST_PROCESSING_CONFIG:
            self.field_method = field_methods[fieldname]
            val = self.field_method(val, target_val)  
        return val

    def post_process(self, results):
        self.set_fields_to_be_compared()
        post_results = []
        for image, target_values_dict in zip(results, self.target_values_dicts):
            d = {}
            self.current_image_ref = image[self.RECORD_REF_FIELDNAME] if self.RECORD_REF_FIELDNAME in image else image["Image"]
            for fieldname in self.fieldnames:
                transcription_val = image[fieldname]
                target_val = target_values_dict[fieldname]
                if transcription_val not in ["N/A", "unsure and check", "PASS"]:
                    transcription_val = self.check_fields(fieldname, transcription_val, target_val)
                d[fieldname] = transcription_val  
            post_results += [d]    
        return post_results

    def post(self):
        self.load_data()
        master_runs = []                   
        for spreadname, transcription_values_dicts in self.master_transcription_values_dicts.items():
            post_processed_results = self.post_process(transcription_values_dicts)
            post_name = f"post_{spreadname}"
            utility.save_to_csv(self.TRANSCRIPTIONS_PATH+post_name, post_processed_results)
            print(f"saved {self.TRANSCRIPTIONS_PATH+post_name = }")
            master_runs += [spreadname, post_name]
        self.RUN_SPREADNAMES = master_runs
        self.run()
       
    
if __name__ == "__main__":
    CONFIG_PATH = "DataAnalysis/AnalysisTools/Configurations/"

    ##############################################################
    # copy in the name of the configuration file to be used below
    config_filename = "post_processing_image_manipulation.yaml"
    ##############################################################
    
    config = PostProcessor.read_configuration_from_yaml(CONFIG_PATH, config_filename)
    post_process_run = PostProcessor(config, config_filename)
    post_process_run.post()
    