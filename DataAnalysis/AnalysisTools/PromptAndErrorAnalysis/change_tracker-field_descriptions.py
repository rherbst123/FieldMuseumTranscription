import utility
import re
import get_prompts_as_dict
import field_accuracy

class ChangeTracker:
    def __init__(self, inputs: list[dict], data: list[dict]):
        self.inputs = inputs
        self.data = data
        self.fieldnames =  ["verbatimCollectors", "collectedBy", "secondaryCollectors", "recordNumber", "verbatimEventDate", "minimumEventDate", "maximumEventDate", "verbatimIdentification", "latestScientificName", "identifiedBy", "verbatimDateIdentified", "associatedTaxa", "country", "firstPoliticalUnit", "secondPoliticalUnit", "municipality", "verbatimLocality", "locality", "habitat", "verbatimElevation", "verbatimCoordinates", "otherCatalogNumbers", "originalMethod", "typeStatus"]

    def extract_run_name_from_comparisons_filepath(self, filepath):
        timestamp_pattern = r"\d\d\d\d-\d\d-\d\d-\d\d\d\d"
        mtch = re.search(fr".*/(.+-{timestamp_pattern}.*?)-comparisons.csv", filepath)
        return mtch.group(1)    

    def get_changes(self):
        lines = []
        for fieldname in sorted(self.fieldnames):
            last_accuracy, last_graded_match, last_field_description, last_prompt_name = "N/A", "N/A", "", ""
            for prompt, datum in zip(self.inputs, self.data):
                d, last_accuracy, last_graded_match, last_field_description, last_prompt_name = self.track_changes(fieldname, prompt, datum, last_accuracy, last_graded_match, last_field_description, last_prompt_name)
                lines.append(d)
            lines.append({})
        return lines

    def format_values(self, d):
        return {field: "      "+val if val in ["N/A", "NaN"] else val for field, val in d.items()} 

    def track_changes(self, fieldname, prompt, datum, last_accuracy, last_graded_match, last_field_description, last_prompt_name):
            d = {}
            prompt_name, field_descriptions = prompt
            field_description = field_descriptions[fieldname]
            d["fieldname"], d["prompt"]  = fieldname, prompt_name
            accuracy, gradedMatch = datum.get(fieldname, "N/A"), datum.get(f"{fieldname}GRD", "N/A")
            d = self.associate_data_changes_with_inputs(d, accuracy, last_accuracy, gradedMatch, last_graded_match, field_description, last_field_description, last_prompt_name)
            formatted_d = self.format_values(d)        
            return formatted_d, accuracy, gradedMatch, field_description, prompt_name 
                       

    def get_diff(self, val1, val2):
        return "N/A" if "N/A" in [val1, val2] or "NaN" in [val1, val2] else val2 - val1                 

    def associate_data_changes_with_inputs(self, d, accuracy, last_accuracy, gradedMatch, last_graded_match, field_description, last_field_description, last_prompt_name):
        d["accuracy"] = accuracy
        d["gradedMatch"] = gradedMatch
        d["diff accuracy"] = self.get_diff(last_accuracy, accuracy)
        d["diff gradedMatch"] = self.get_diff(last_graded_match, gradedMatch)
        if last_field_description and last_field_description in field_description:
            d["description"] = field_description.replace(last_field_description, f" <--same as {last_prompt_name}--> ")
        else:
            d["description"] = field_description
        return d    

class TrackFieldAccuracy:
    def __init__(self, prompt_filenames, batch_comparisons_filename):
        self.prompt_folder = "Prompts/"
        self.prompt_filenames = prompt_filenames
        self.comparisons_folder = "DataAnalysis/Comparisons/BatchComparisons/"
        self.batch_comparisons_filename = batch_comparisons_filename

    def get_prompt_dicts(self):
        return [(fname, get_prompts_as_dict.get_field_dict(fname)) for fname in self.prompt_filenames]

    def get_field_accuracy_dicts(self):
        return field_accuracy.get_fields_accuracy_batch_runs(self.batch_comparisons_filename)

    def save_to_csv(self, data):
        #run_name = self.extract_run_name_from_comparisons_filepath(batch_comparisons_filepath)
        run_name = "claude-3.5-sonnet-various_prompts"
        filepath = f"{self.comparisons_folder}{run_name}-changes.csv"
        utility.save_to_csv(filepath, data)       

    def run(self):
        field_accuracy_dicts = self.get_field_accuracy_dicts()
        prompt_dicts = self.get_prompt_dicts()
        ct = ChangeTracker(prompt_dicts, field_accuracy_dicts)
        changes = ct.get_changes()
        self.save_to_csv(changes)

if __name__ == "__main__":
    prompt_filenames = ["Prompt 1.1.1.txt", "Prompt 1.2.txt", "Prompt 1.3.txt", "Prompt 1.4.txt", "Prompt 1.5.2.txt"]
    batch_comparisons_filename = "claude-3.5-sonnet-various_prompts-comparisons.csv"
    tfa = TrackFieldAccuracy(prompt_filenames, batch_comparisons_filename)
    tfa.run()