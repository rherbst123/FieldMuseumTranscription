import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import re
import csv
import json
import time
from TranscriptionProcessing.edit_distance import WeightedLevenshtein

class Transcript:
    def __init__(self, url: str):
        self.url = url
        self.transcription_folder = "TranscriptionProcessing/SingleTranscriptions/"
        self.versions =  self.load_all_versions()
        self.time_started = self.get_timestamp()

    def load_all_versions(self):
        filename = self.get_legal_json_filename()
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {} 

    def get_timestamp(self):
        return time.strftime("%Y-%m-%d-%H%M-%S")  

    def get_version_name(self, created_by):
        return f"{created_by}-{self.time_started}"                 

    def create_version(self, created_by, content, data, old_version="base"):
        data = self.update_data(data, created_by, old_version)
        new_version_name = self.get_version_name(created_by)
        self.versions[new_version_name] = {"content": content, "data": data}
        self.update_costs(new_version_name)
        self.save_to_json(self.versions)

    def update_data(self, data, created_by, old_version):
        data["created by"] = created_by
        data["url"] = self.url
        data["old version"] = old_version
        time_to_create = time.time() - time.mktime(time.strptime(self.time_started, "%Y-%m-%d-%H%M-%S"))
        data["time to create/edit"] = time_to_create
        return data

    def update_costs(self, current_version_name):
        costs_list = ["input tokens", "output tokens", "input cost $", "output cost $"]
        overall_costs_dict = {f"overall {cost}": 0 for cost in costs_list}
        history = self.get_version_history(self.versions, current_version_name)
        for version_name, version in history[::-1]:
            for cost in costs_list:
                overall_costs_dict[f"overall {cost}"] += version["data"][cost]
            self.versions[version_name]["data"] = self.versions[version_name]["data"] | overall_costs_dict          

    def get_version_history(self, versions, current_version_name: str, up_to="base"):
        history = []
        while current_version_name != up_to:
            history.append((current_version_name, versions[current_version_name]))
            current_version_name = versions[current_version_name]["data"]["old version"]
        return history

    def get_versions_created_by(self, created_by):
        return {version_name: version for version_name, version in self.versions.items() if version["data"]["created by"] == created_by}  

    def get_created_by_history(self, created_by):
        return [version for version_name, version in self.get_versions_created_by(created_by).items()]      

    def get_legal_json_filename(self):
        url = re.sub(r"[\/]", "#", self.url)
        url = re.sub(r"[:]", "$", url)
        filename = f"{self.transcription_folder}{url}.json" 
        return filename   

    def save_to_json(self, versions):
        filename = self.get_legal_json_filename()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(versions, f, ensure_ascii=False, indent=4)            

class Run:
    def __init__(self, run_name, ref_tag):
        self.ref_tag = ref_tag
        self.run_name = run_name
        self.transcripts_folder = "DataAnalysis/Transcriptions/"

    def get_transcripts(self):
        return self.transcripts

    def set_transcripts(self, transcripts):
        self.transcripts = []
        for idx, transcript in enumerate(transcripts):
            url = transcript[self.ref_tag]
            del(transcript[self.ref_tag])
            self.transcripts.append(Transcript(transcript, url, self.ref_tag, idx))

    def set_transcripts_from_csv(self):
        fname = f"{self.run_name}-transcriptions.csv"
        with open(self.transcripts_folder+fname, "r", encoding="utf-8") as f:
            self.set_transcripts(csv.DictReader(f))

class TranscriptComparer:
    def __init__(self, transcriptA, transcriptB, edit_distance_config=None):
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

    def compare_image_transciptions(self):
        for fieldname in self.fieldnames:
            valA = self.transcriptA.get_field(fieldname)   
            valB = self.transcriptB.get_field(fieldname)
            is_a_match = self.is_match(valA, valB)
            graded_match = self.get_graded_match(valA, valB, is_a_match)
            self.update_fieldnames_results_dict(fieldname, is_a_match, graded_match)
        overall_matches, overall_graded_matches = self.tally_results()
        return overall_matches, overall_graded_matches    


class TranscriptAgreement(TranscriptComparer):
    pass                    

if __name__ == "__main__":
    transcript = Transcript("https://fm-digital-assets.fieldmuseum.org/2491/491#C0268520F_p.jpg")
    versions = transcript.get_versions_created_by("claude-3.5-sonnet") 
    #history = transcript.get_version_history_data(sample, "gemini-2", "base")
    print(versions)                           

