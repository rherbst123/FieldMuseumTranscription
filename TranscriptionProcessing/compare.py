import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import re
import csv
import json
import time
import math
from TranscriptionProcessing.edit_distance import WeightedLevenshtein

class TranscriptComparer:
    def __init__(self, transcriptA, transcriptB, edit_distance_config=None):
        return
        self.transcriptA = transcriptA
        self.transcriptB = transcriptB
        self.fieldnames = self.get_fieldnames_intersection()
        self.fieldnames_results_dict = self.get_blank_fieldnames_results_dict()
        self.wl = WeightedLevenshtein(edit_distance_config)

    def get_fieldnames_intersection(self):
        return [fieldname for fieldname in self.transcriptA.fieldnames if fieldname in self.transcriptB.fieldnames]

    def get_blank_fieldnames_results_dict(self):
        results = {"num_matches": 0, "graded_matches": 0}
        return {fieldname: results for fieldname in self.fieldnames}

    def tally_results(self):
        overall_matches = sum([self.fieldnames_results_dict[fieldname]["num_matches"] for fieldname in self.fieldnames])
        overall_graded_matches = sum([self.fieldnames_results_dict[fieldname]["graded_matches"] for fieldname in self.fieldnames])
        return overall_matches, overall_graded_matches

    def update_fieldnames_results_dict(self, fieldname, is_a_match, graded_match):
        self.fieldnames_results_dict[fieldname]["num_matches"] = is_a_match
        self.fieldnames_results_dict[fieldname]["graded_matches"] = graded_match 

    def is_match(self, valA, valB):
        return valA.strip().lower() == valB.strip().lower() 

    def get_graded_match(self, valA, valB, is_a_match):
        if not is_a_match and (valA=="N/A" or valB=="N/A"):
            return 0
        return is_a_match or 1 - self.wl.calculate_weighted_difference(valA, valB, scaled=True)

    def tally(self, d: dict, use_graded_match=False):
        return sum([val if use_graded_match else math.floor(val) for val in d.values()])             

    def compare_image_transciptions(self):
        for fieldname in self.fieldnames:
            valA = self.transcriptA.get_field(fieldname)   
            valB = self.transcriptB.get_field(fieldname)
            is_a_match = self.is_match(valA, valB)
            graded_match = self.get_graded_match(valA, valB, is_a_match)
            self.update_fieldnames_results_dict(fieldname, is_a_match, graded_match)
        overall_matches, overall_graded_matches = self.tally_results()
        return overall_matches, overall_graded_matches

if __name__ == "__main__":
    tc = TranscriptComparer(0,0,0)  
    d = {1:True, 2:0.5, 3:True, 4:0.25} 
    score = tc.tally(d, use_graded_match=True)
    print(f"{score = }")         
