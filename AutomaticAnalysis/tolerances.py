import re
from string_distance import WeightedLevenshtein

class FieldTolerances:
    def __init__(self, config, edit_distance_config):
        self.tols = config["TOLS"]
        self.use_graded_match_threshold = config["USE_GRADED_MATCH_THRESHOLD"] == "True"
        self.graded_match_threshold = float(config["GRADED_MATCH_THRESHOLD"])
        self.edit_distance_config = edit_distance_config
        self.functions_dict = {"double_space": self.remove_double_spaces_from_observed_val, "missing_abbreviation_point": self.remove_abbreviation_points_from_true_val, "always_true": self.return_true_val}

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
        return observed_val, re.sub(r"\.", "", true_val)  

    # exposed method
    def is_within_tolerances(self, fieldname, observed_val, true_val):
        tols = self.tols[fieldname]
        for tol in tols:
            func_name = self.functions_dict[tol]
            observed_val, true_val = func_name(observed_val, true_val)
        graded_match = self.get_graded_match(fieldname, observed_val, true_val) 
        passing_grade = self.use_graded_match_threshold and graded_match > self.graded_match_threshold
        return observed_val == true_val or passing_grade         

if __name__ == "__main__":
    tols = {"verbatimLocality": ["double_space", "missing_abbreviation_point"], "locality": ["double_space"]}
    observed_val = "The  Congo"
    true_val = "The. Congo"
    fieldname = "verbatimLocality"
    ft = FieldTolerances(tols)
    print(ft.is_within_tolerances(fieldname, observed_val, true_val)) 
    
