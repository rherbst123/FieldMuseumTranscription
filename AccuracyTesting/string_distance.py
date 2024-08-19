'''
install these packages:
pip install weighted-levenshtein
https://pypi.org/project/weighted-levenshtein/

pip install nltk
https://www.nltk.org/api/nltk.metrics.distance.html

lecture presentation text on minimum edit distance by Jurafsky
https://web.stanford.edu/class/cs124/lec/med.pdf
'''



import math
from nltk.metrics.distance import edit_distance as nltk_edit_distance 
from nltk.metrics.distance import edit_distance_align as nltk_edit_distance_align 
import numpy as np
from weighted_levenshtein import levenshtein, optimal_string_alignment, damerau_levenshtein

class StringDistance:
    def __init__(self, config):
        self.config = config
        
    def scale(self, val, minimum, maximum):
        return (val-minimum) / (maximum-minimum)

    # based on this paper: https://www.cse.lehigh.edu/~lopresti/Publications/1996/sdair96.pdf
    # not working though, borrowed from here: https://stackoverflow.com/questions/64113621/how-to-normalize-levenshtein-distance-between-0-to-1
    def normalized_edit_similarity(self, m, d):
        # d : edit distance between the two strings
        # m : length of the shorter string
        return ( 1.0 / math.exp( d / (m - d) ) ) if m != d else self.scale(d, 0, m) 

    def clean(self, *strings):
        return [s.lower().strip() for s in strings]         


class NLTKDistance(StringDistance):

    # exposed method
    def calculate_weighted_difference(self, s1, s2):
        s1, s2 = self.clean(s1, s2)
        edit_distance = nltk_edit_distance(s1, s2, substitution_cost=1)
        return self.scale(edit_distance, minimum=0, maximum=max(len(s1), len(s2)))

  

class WeightedLevenshtein(StringDistance):
    def __init__(self, config):
        self.INSERT_COSTS = np.ones(128, dtype=np.float64)  # make an array of all 1's of size 128, the number of ASCII characters
        self.DELETE_COSTS = np.ones(128, dtype=np.float64)
        self.SUBSTITUTE_COSTS = np.ones((128, 128), dtype=np.float64)  # make a 2D array of 1's
        self.TRANSPOSITION_COSTS = np.ones((128, 128), dtype=np.float64)
        self.setup_costs(config)

    def setup_costs(self, config):
        insert_char_costs = config["INSERT_CHAR_COSTS"]
        delete_char_costs = config["DELETE_CHAR_COSTS"] 
        substitution_char_costs = config["SUBSTITUTION_CHAR_COSTS"]  
        self.update_insert_delete_costs(insert_char_costs, self.INSERT_COSTS)
        self.update_insert_delete_costs(delete_char_costs, self.DELETE_COSTS)
        self.update_substition_transposition_costs(substitution_char_costs, self.SUBSTITUTE_COSTS)   

    def update_insert_delete_costs(self, char_costs: list[tuple], costs_list):
        if not char_costs[0] or not char_costs[0][0]:
            return
        for char, cost in char_costs:
            costs_list[ord(char)] = cost

    # transposition costs only used with optimal_string_alignment
    def update_substition_transposition_costs(self, char_costs: list[tuple], costs_lists):
        if not char_costs[0] or not char_costs[0][0]:
            return
        for substitution, target, cost in char_costs:
            costs_lists[ord(substitution), ord(target)] = cost

    def assign_temp_ascii_values(self, s1, s2):
    # The functions from the weighted_levenshtein module only work on characters with unicode values < 128.
    # This is due to the datatypes and libraries used for speed.
    # Many non-English words contain characters whose unicode values are >= 128.
    # It so happens that unicode 0-32 are used for non-printable characters, i.e., 
    #    they would never appear as single characters in a text.
    # This lowest unicode range is used in this method to represent the the characters >= 128 on a temporary basis,
    #     i.e., a sort of translation applied the same way to both strings, just for one comparison
        unused_ascii_range = list(range(32))
        d = {}
        def assign_temp_val(char: str, d, unused: list):  
            if char in d:
                return chr(d[char])
            else:
                d[char] = unused.pop()
                return chr(d[char]) 
        temp1 = "".join(char if ord(char) < 128 else assign_temp_val(char, d, unused_ascii_range) for char in s1)
        temp2 = "".join(char if ord(char) < 128 else assign_temp_val(char, d, unused_ascii_range) for char in s2)
        return temp1, temp2

    # exposed method
    def calculate_weighted_difference(self, s1, s2):
        s1, s2 = self.clean(s1, s2)
        try:
            edit_distance = levenshtein(s1, s2, insert_costs=self.INSERT_COSTS, delete_costs=self.DELETE_COSTS, substitute_costs=self.SUBSTITUTE_COSTS)
        except UnicodeEncodeError:
            # see explanation in assign_temp_ascii_values method comments
            s1, s2 = self.assign_temp_ascii_values(s1, s2)
            edit_distance = levenshtein(s1, s2, insert_costs=self.INSERT_COSTS, delete_costs=self.DELETE_COSTS, substitute_costs=self.SUBSTITUTE_COSTS)
        return self.scale(edit_distance, minimum=0, maximum=max(len(s1), len(s2)))


if __name__ == "__main__":
    # a test of the calculate_weighted_distance method
    config = {"INSERT_CHAR_COSTS": [[".", 0.5], [" ", 0.5]],
             "DELETE_CHAR_COSTS":  [[".", 0.5], [" ", 0.5]],
            "SUBSTITUTION_CHAR_COSTS": [["A", "a", 0.00001]],
            "TRANSPOSITON_CHAR_COSTS": [[]]
                                }
    
    wl = WeightedLevenshtein(config)
    s1 = 'bolivar' 
    s2 = 'bolívar'
    dist = wl.calculate_weighted_difference(s1, s2)
    print(f"{s1 = }, {s2 = }, {dist = }")
    s1 = 'bolivar' 
    s2 = 'bolivar'
    dist = wl.calculate_weighted_difference(s1, s2)
    print(f"{s1 = }, {s2 = }, {dist = }")
    s1 = 'bolívar' 
    s2 = 'bolívar'
    dist = wl.calculate_weighted_difference(s1, s2)
    print(f"{s1 = }, {s2 = }, {dist = }")
    s1 = 'bolvar' 
    s2 = 'bolívar'
    dist = wl.calculate_weighted_difference(s1, s2)
    print(f"{s1 = }, {s2 = }, {dist = }")