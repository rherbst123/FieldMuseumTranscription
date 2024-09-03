import re
from string_distance import WeightedLevenshtein

class FieldTolerances:
    def __init__(self, config, edit_distance_config):
        self.tols = config["TOLS"]
        self.use_graded_match_threshold = config["USE_GRADED_MATCH_THRESHOLD"] == "True"
        self.graded_match_threshold = float(config["GRADED_MATCH_THRESHOLD"])
        self.edit_distance_config = edit_distance_config
        self.defaults = ["both_case", "unstripped_whitespace"]
        self.functions_dict = {"double_space": self.remove_double_spaces_from_observed_val,
                               "missing_abbreviation_point": self.remove_abbreviation_points_from_true_val,
                               "always_true": self.return_true_val,
                               "both_case": self.to_lowercase,
                               "unstripped_whitespace": self.strip_whitespace} 
                              

    def get_edit_distance_interface(self, fieldname):
        return WeightedLevenshtein(self.edit_distance_config, fieldname)
    
    def get_graded_difference(self, fieldname, observed_val, true_val):
        if observed_val == "N/A":   # don't bother getting the edit distance when the observed value is "N/A"; just return 1
            return 1       
        edit_distance_interface = self.get_edit_distance_interface(fieldname)        
        return edit_distance_interface.calculate_weighted_difference(observed_val, true_val)

    def get_graded_match(self, fieldname, observed_val, true_val):
        return 1 - self.get_graded_difference(fieldname, observed_val, true_val)    
    
    # this method is used for demonstration and testing purposes
    def return_true_val(self, observed_val, true_val):
        return true_val, true_val 

    def remove_double_spaces_from_observed_val(self, observed_val, true_val):
        return re.sub("  ", " ", observed_val), true_val

    def remove_abbreviation_points_from_true_val(self, observed_val, true_val): 
        return observed_val, re.sub(r"[a-zA-Z]\.", "", true_val)

    def to_lowercase(self, observed_val, true_val):
        return observed_val.lower(), true_val.lower()     

    def strip_whitespace(self, observed_val, true_val):
        return observed_val.strip(), true_val.strip()     

    # exposed method
    def is_within_tolerances(self, fieldname, observed_val, true_val):
        graded_match = self.get_graded_match(fieldname, observed_val, true_val) 
        passing_grade = self.use_graded_match_threshold and graded_match > self.graded_match_threshold
        tols = self.tols[fieldname]
        for tol in tols + self.defaults:
            func_name = self.functions_dict[tol]
            observed_val, true_val = func_name(observed_val, true_val)
        return observed_val == true_val or passing_grade         

if __name__ == "__main__":
    config = {"TOLERANCES_ALLOWED": "True",
            "USE_GRADED_MATCH_THRESHOLD": "True",
            "GRADED_MATCH_THRESHOLD": "0.80",
            "TOLS": {"locality": ["double_space"],
                    "verbatimLocality": ["missing_abbreviation_point", "double_space"]}}
    edit_distance_config =  {
                           "ALL_FIELDS_CUSTOM_COSTS": {
                                              "INSERT_CHAR_COSTS": [[]],  
                                              "DELETE_CHAR_COSTS":  [[]],
                                              "SUBSTITUTION_CHAR_COSTS": [[]],
                                              "TRANSPOSITON_CHAR_COSTS": [[]]

                           },
                           "USE_FIELDNAMES_EXCLUSIVELY": "False",
                           "FIELDNAMES_COSTS": {
                                                "": {"INSERT_CHAR_COSTS": [[]],  
                                                    "DELETE_CHAR_COSTS":  [[]],
                                                    "SUBSTITUTION_CHAR_COSTS": [[]],
                                                    "TRANSPOSITON_CHAR_COSTS": [[]]
                                                    }}
    }                
    observed_val = "The  Congo"
    true_val = "The. congo"
    fieldname = "verbatimLocality"
    ft = FieldTolerances(config, edit_distance_config)
    print(ft.is_within_tolerances(fieldname, observed_val, true_val)) 
    
