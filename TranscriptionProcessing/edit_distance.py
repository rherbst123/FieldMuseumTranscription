import logging
import numpy as np
from weighted_levenshtein import levenshtein

class WeightedLevenshtein:
    def __init__(self, config=None):
        self.available_ascii_range = list(range(128))
        self.char_value_pairs = {}
        self.INSERT_COSTS = np.ones(128, dtype=np.float64)  # make an array of all 1's of size 128, the number of ASCII characters
        self.DELETE_COSTS = np.ones(128, dtype=np.float64)
        self.SUBSTITUTE_COSTS = np.ones((128, 128), dtype=np.float64)  # make a 2D array of 1's
        if config:
            self.update_costs(config)
        
    def update_costs(self, config):
        custom_insert_char_costs = config["INSERT_CHAR_COSTS"]
        custom_delete_char_costs = config["DELETE_CHAR_COSTS"] 
        custom_substitution_char_costs = config["SUBSTITUTION_CHAR_COSTS"]  
        self.update_insert_delete_costs(custom_insert_char_costs, self.INSERT_COSTS)
        self.update_insert_delete_costs(custom_delete_char_costs, self.DELETE_COSTS)
        self.update_substition_costs(custom_substitution_char_costs, self.SUBSTITUTE_COSTS)   

    def update_insert_delete_costs(self, custom_char_costs: list[list], costs_list):
        if not custom_char_costs[0] or not custom_char_costs[0][0]:
            return
        for char, cost in custom_char_costs:
            value = self.get_char_value(char)
            costs_list[value] = cost

    def update_substition_costs(self, custom_char_costs: list[list], costs_lists):
        if not custom_char_costs[0] or not custom_char_costs[0][0]:
            return
        for substitution, target, cost in custom_char_costs:
            substitution_value = self.get_char_value(substitution)
            target_value = self.get_char_value(target)
            costs_lists[(substitution_value, target_value)] = cost  

    def get_char_value(self, char):
        if char in self.char_value_pairs:
            return self.char_value_pairs[char]
        else:
            self.char_value_pairs[char] = self.available_ascii_range.pop()
            return self.char_value_pairs[char]           

    def get_modified_str(self, s):
        return "".join([chr(self.get_char_value(char)) for char in s])               
    
    def get_edit_distance(self, s1, s2):
        s1, s2 = self.get_modified_str(s1), self.get_modified_str(s2)
        edit_distance = levenshtein(s1, s2, insert_costs=self.INSERT_COSTS, delete_costs=self.DELETE_COSTS, substitute_costs=self.SUBSTITUTE_COSTS)
        return edit_distance

    # exposed method
    def calculate_weighted_difference(self, s1, s2, scaled=True):
        edit_distance = self.get_edit_distance(s1, s2)
        return self.scale(edit_distance, minimum=0, maximum=max(len(s1), len(s2))) if scaled else edit_distance

    def scale(self, val, minimum, maximum):
        return (val-minimum) / (maximum-minimum)       

if __name__ == "__main__":
    # a test of the calculate_weighted_distance method
    config = {
                    "INSERT_CHAR_COSTS": [[]],
                    "DELETE_CHAR_COSTS":  [[]],
                    "SUBSTITUTION_CHAR_COSTS": [["A", "a", 0.5], ["i", "í", 0.01],  ["í", "i", 0.01], ["é", "e", 500], ["e", "é", 500]],
                    "TRANSPOSITON_CHAR_COSTS": [[]]
                }
    wl = WeightedLevenshtein(config)
    s1 = 'bolivar' 
    s2 = 'bolívar'
    dist = wl.calculate_weighted_difference(s1, s2, scaled=False)
    print(f"{s1 = }, {s2 = }, {dist = }")
    s1 = 'bolivAr' 
    s2 = 'bolivar'
    dist = wl.calculate_weighted_difference(s1, s2, scaled=False)
    print(f"{s1 = }, {s2 = }, {dist = }")
    s1 = 'bolívar' 
    s2 = 'bolívar'
    dist = wl.calculate_weighted_difference(s1, s2, scaled=False)
    print(f"{s1 = }, {s2 = }, {dist = }")
    s1 = 'bolvar' 
    s2 = 'bolívar'
    dist = wl.calculate_weighted_difference(s1, s2)
    print(f"{s1 = }, {s2 = }, {dist = }")