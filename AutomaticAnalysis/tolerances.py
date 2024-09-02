import re

class FieldTolerances:
    def __init__(self, config):
        self.tols = config["TOLS"]
        self.patterns = {"double_space": self.remove_double_spaces_from_observed_val, "missing_abbreviation_point": self.remove_abbreviation_points_from_true_val, "always_true": self.return_true_val}

    def is_within_tolerances(self, fieldname, observed_val, true_val):
        tols = self.tols[fieldname]
        for tol in tols:
            func_name = self.patterns[tol]
            observed_val, true_val = func_name(observed_val, true_val)
        return observed_val == true_val    

    def remove_double_spaces_from_observed_val(self, observed_val, true_val):
        return re.sub("  ", " ", observed_val), true_val

    def remove_abbreviation_points_from_true_val(self, observed_val, true_val): 
        return observed_val, re.sub(r"\.", "", true_val)  

    # this method is used for demonstration and testing purposes
    def return_true_val(self, observed_val, true_val):
        return true_val, true_val    

if __name__ == "__main__":
    tols = {"verbatimLocality": ["double_space", "missing_abbreviation_point"], "locality": ["double_space"]}
    observed_val = "The  Congo"
    true_val = "The. Congo"
    fieldname = "verbatimLocality"
    ft = FieldTolerances(tols)
    print(ft.is_within_tolerances(fieldname, observed_val, true_val)) 
    
