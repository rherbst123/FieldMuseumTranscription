import logging
from Utilities import utility
import string_distance
import re
from comparison_and_accuracy import Comparison
from tolerances import FieldTolerances
from string_distance import WeightedLevenshtein

class PostProcessor(Comparison):
        
    def get_field_methods(self):
        return {"verbatimCollectors": self.clean_verbatim_collectors,
                "collectedBy": self.format_names,
                "identifiedBy": self.format_names,
                "verbatimCoordinates": self.clean_verbatim_coordinates}

    def remove_abbreviation_points(self, val):
        return re.sub(r"\.", "", val)

    def remove_commas(self, val):
        return re.sub(r",", "", val)

    def collapse_spacing(self, val):
        return re.sub(r" ", "", val)                    

    def remove_extra_spaces(self, val):
        return re.sub(r"\s+", " ", val)

    def abbreviate_name(self, w):
        w = w.strip()
        if re.match(r"^[a-z]", w) or w in ["De", "Von"]:
            return w+" "
        else:
            return w[0]+". "    
    
    def format_names(self, val):
        *unformatted, final = val.split()
        formatted = ""
        for w in unformatted:
            formatted += self.abbreviate_name(w)
        return formatted + " " + final

    def clean_verbatim_collectors(self, val):
        words = val.split()
        return " ".join([w.strip() for w in words if w.strip() not in ["coll.", "Coll.", "leg.", "Leg."]]) 

    def clean_verbatim_coordinates(self, val):
        val = self.collapse_spacing(val)
        val = self.remove_abbreviation_points(val)   
        val = self.remove_commas(val)  
        return val
            
    def check_fields(self, fieldname, val):
        
        field_methods = self.get_field_methods()
        if fieldname in field_methods:
            val = field_methods[fieldname](val)
        val = self.remove_extra_spaces(val)    
        return val


    def post_process(self, results):
        post_results = []
        print("woo hoo")
        for image in results:
            d = {}
            for fieldname, val in image.items():
                val = self.check_fields(fieldname, val)
                d[fieldname] = val  
            post_results += [d]    
        return post_results

    def post(self):
        master_runs = []                    
        for spreadname in self.RUN_SPREADNAMES:
            saved_results: list[dict] = utility.get_contents_from_csv(self.SOURCE_PATH+spreadname)
            post_processed_results = self.post_process(saved_results)
            post_name = f"post_{spreadname}"
            utility.save_to_csv(self.SOURCE_PATH+post_name, post_processed_results)
            master_runs += [spreadname, post_name]
        self.RUN_SPREADNAMES = master_runs
        self.run()
       
    
if __name__ == "__main__":
    CONFIG_PATH = "DataAnalysis/Configurations/"
    # copy in the name of the configuration file to be used below
    config_filename = "" 

    post_process_run = PostProcessor(CONFIG_PATH, config_filename)
    post_process_run.post()