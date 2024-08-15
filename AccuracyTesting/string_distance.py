'''
install these packages:
pip install weighted-levenshtein
https://pypi.org/project/weighted-levenshtein/

pip install nltk
https://www.nltk.org/api/nltk.metrics.distance.html

academic paper on minimum edit distance by Jurafsky
https://web.stanford.edu/class/cs124/lec/med.pdf
'''



import math
from nltk.metrics.distance import edit_distance as nltk_edit_distance 
from nltk.metrics.distance import edit_distance_align as nltk_edit_distance_align 
import numpy as np
from weighted_levenshtein import lev, osa, dam_lev

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
        return [str(s).lower().strip() for s in strings]         


class NLTKDistance(StringDistance):

# future home of Mr Levenshtein and his REGEX regulars
    def calculate_weighted_difference(self, s1, s2):
        s1, s2 = self.clean(s1, s2)
        edit_distance = nltk_edit_distance(s1.strip().lower(), s2.strip().lower(), substitution_cost=1)
        #return normalized_edit_similarity(min(len(s1), len(s2)), weighted_distance)
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

    def update_substition_transposition_costs(self, char_costs: list[tuple], costs_lists):
        if not char_costs[0] or not char_costs[0][0]:
            return
        for substitution, target, cost in char_costs:
            costs_lists[ord(substitution), ord(target)] = cost

    def assign_temp_ascii_values(self, s1, s2):
        temp1, temp2 = "", ""
        unused_ascii_range = list(range(32))
        d = {}
        def assign_temp_val(char: str, d, unused: list):  
            if char in d:
                return chr(d[char])
            else:
                d[char] = unused.pop()
                return chr(d[char]) 
        temp1 = "".join(char if ord(char) < 128 else assign_temp_val(char, d, unused_ascii_range) for char in s1)
        temp2 = "".join(char if ord(char) < 128 else assign_temp_val(char, d, unused_ascii_range) for char in s1)
        return temp1, temp2


    def calculate_weighted_difference(self, s1, s2):
        s1, s2 = self.clean(s1, s2)
        try:
            edit_distance = lev(s1, s2, insert_costs=self.INSERT_COSTS, delete_costs=self.DELETE_COSTS, substitute_costs=self.SUBSTITUTE_COSTS)
        except UnicodeEncodeError:
            print(f"UNICODE ERROR: {s1 = }, {s2 = }")
            s1, s2 = self.assign_temp_ascii_values(s1, s2)
            edit_distance = lev(s1, s2, insert_costs=self.INSERT_COSTS, delete_costs=self.DELETE_COSTS, substitute_costs=self.SUBSTITUTE_COSTS)
            #edit_distance = nltk_edit_distance(s1.strip().lower(), s2.strip().lower(), substitution_cost=1)
        #return normalized_edit_similarity(min(len(s1), len(s2)), weighted_distance)
        return self.scale(edit_distance, minimum=0, maximum=max(len(s1), len(s2)))


if __name__ == "__main__":
    config = {"INSERT_CHAR_COSTS": [[".", 0.5], [" ", 0.5]],
             "DELETE_CHAR_COSTS":  [[".", 0.5], [" ", 0.5]],
            "SUBSTITUTION_CHAR_COSTS": [["A", "a", 0.00001]],
            "TRANSPOSITON_CHAR_COSTS": [[]]
                                }
    wl = WeightedLevenshtein()