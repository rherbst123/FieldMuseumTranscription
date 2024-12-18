import logging
import re
from DataAnalysis.AnalysisTools.string_distance import WeightedLevenshtein

class FieldTolerances:
    def __init__(self, config, edit_distance_config):
        self.logger = logging.getLogger('__main__.' + __class__.__name__)
        self.logger.debug(f"{str(config) = }")
        self.logger.debug(f"{str(edit_distance_config) = }")
        self.tols = config["TOLS"]
        self.use_edit_distance_threshold = self.tols["ENABLE_EDIT_DISTANCE_THRESHOLD"]
        self.edit_distance_thresholds = self.tols["EDIT_DISTANCE_THRESHOLDS"]
        self.edit_distance_config = edit_distance_config
        self.defaults = ["both_case", "unstripped_whitespace"]
        self.functions_dict = {"double_space": self.remove_double_spaces_from_observed_val,
                               "missing_abbreviation_point": self.remove_abbreviation_points_from_true_val,
                               "always_true": self.return_true_val,
                               "both_case": self.to_lowercase,
                               "unstripped_whitespace": self.strip_whitespace,
                               "misaligned_spacing": self.collapse_spacing,
                               "mismatching_abbreviation": self.remove_abbreviation_points,
                               "missing_commas": self.remove_commas} 
                              

    def get_edit_distance_interface(self, fieldname):
        return WeightedLevenshtein(self.edit_distance_config, fieldname)

    def get_edit_distance(self, fieldname, observed_val, true_val, scaled):
        if observed_val == "N/A":   # don't bother getting the edit distance when the observed value is "N/A"; just return 1
            return 1 if scaled else len(true_val)       
        edit_distance_interface = self.get_edit_distance_interface(fieldname)        
        return edit_distance_interface.calculate_weighted_difference(observed_val, true_val, scaled)

    def get_thresholds(self, fieldname):
        key = fieldname if fieldname in self.edit_distance_thresholds else "DEFAULT"
        return self.edit_distance_thresholds[key]["SCALED"], self.edit_distance_thresholds[key]["VALUE"]  

    def is_within_threshold(self, fieldname, observed_val, true_val):
        use_scaled_value, threshold_value = self.get_thresholds(fieldname) 
        return self.get_edit_distance(fieldname, observed_val, true_val, use_scaled_value) <= threshold_value    
               
    
    # this method is used for demonstration and testing purposes
    def return_true_val(self, observed_val, true_val):
        return true_val, true_val

    def remove_abbreviation_points(self, observed_val, true_val):
        return re.sub(r"\.", "", observed_val), re.sub(r"\.", "", true_val) 

    def remove_commas(self, observed_val, true_val):
        return re.sub(r",", "", observed_val), re.sub(r",", "", true_val) 

    def collapse_spacing(self, observed_val, true_val):
        return re.sub(" ", "", observed_val), re.sub(" ", "", true_val)    

    def remove_double_spaces_from_observed_val(self, observed_val, true_val):
        return re.sub("  ", " ", observed_val), true_val

    def remove_abbreviation_points_from_true_val(self, observed_val, true_val): 
        return observed_val, re.sub(r"([a-zA-Z]).(\s)", r"\1"+r"\2", true_val)

    def to_lowercase(self, observed_val, true_val):
        return observed_val.lower(), true_val.lower()     

    def strip_whitespace(self, observed_val, true_val):
        return observed_val.strip(), true_val.strip()     

    # exposed method
    def is_within_tolerances(self, fieldname, observed_val, true_val):
        if fieldname not in self.tols:
            return False
        tols = self.tols[fieldname]
        passes_threshold = self.is_within_threshold(fieldname, observed_val, true_val) 
        if passes_threshold:
            self.logger.info(f"{fieldname = }, {observed_val = }, {true_val = }")
        passing_grade = self.use_edit_distance_threshold and passes_threshold
        for tol in tols + self.defaults:
            func_name = self.functions_dict[tol]
            observed_val, true_val = func_name(observed_val, true_val)   
        return observed_val == true_val or passing_grade         

if __name__ == "__main__":
    config = {"TOLERANCES_ALLOWED": True,
            "_EDIT_DISTANCE_THRESHOLD": True,
            "GRADED_MATCH_THRESHOLD": "1.00",
            "TOLS": {"locality": [None, "double_space"],
                    "verbatimLocality": [None, "missing_abbreviation_point", "double_space"],
                    "verbatimCoordinates": []}}
    edit_distance_config =  {
                           "ALL_FIELDS_CUSTOM_COSTS": {
                                              "INSERT_CHAR_COSTS": [[]],  
                                              "DELETE_CHAR_COSTS":  [[]],
                                              "SUBSTITUTION_CHAR_COSTS": [[]],
                                              "TRANSPOSITON_CHAR_COSTS": [[]]

                           },
                           "USE_FIELDNAMES_EXCLUSIVELY": False,
                           "FIELDNAMES_COSTS": {
                                                "": {"INSERT_CHAR_COSTS": [[]],  
                                                    "DELETE_CHAR_COSTS":  [[]],
                                                    "SUBSTITUTION_CHAR_COSTS": [[]],
                                                    "TRANSPOSITON_CHAR_COSTS": [[]]
                                                    }}
    }                
    observed_val = "The Congo"
    true_val = "The. Congo"
    fieldname = "verbatimLocality"
    ft = FieldTolerances(config, edit_distance_config)
    print(ft.is_within_tolerances(fieldname, observed_val, true_val)) 
    observed_val = "S Bolívar Bolivar"    # "bolívar"
    true_val = "S. Bolívar. Bolivar"
    print(ft.is_within_tolerances(fieldname, observed_val, true_val))
    
