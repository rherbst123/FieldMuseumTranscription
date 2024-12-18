import utility
from error_classification import ErrorClassifier


def main(associated_files_dicts, skip_list):
    transcription_folder = "DataAnalysis/Transcriptions/"
    ground_truth_folder = "DataAnalysis/GroundTruths/"
    for associated_files_dict in associated_files_dicts:
        run_name = associated_files_dict["Run Name"]
        ground_truth_filename = associated_files_dict["Ground Truth"]
        transcription_filename = f"{run_name}-transcriptions.csv"
        print(f"{transcription_filename = }")
        transcriptions_filepath = transcription_folder+transcription_filename
        ground_truth_filepath = ground_truth_folder+ground_truth_filename
        try:
            fieldnames = ErrorClassifier.get_fieldnames_from_saved_data(transcriptions_filepath, skip_list)
        except FileNotFoundError:
            print("File Not Found: "+transcriptions_filepath) 
            continue    
        ec = ErrorClassifier(fieldnames)
        ec.run(transcriptions_filepath, ground_truth_filepath, run_name)     

if __name__ == "__main__":
    spread_filepath = "DataAnalysis/associated_files_for_paper.csv"
    associated_files_dicts = utility.get_contents_from_csv(spread_filepath)
    skip_list = ["Image Name", "catalogNumber", "Dataset Source", "accessURI", "Label only?", "modifiedBy", "verifiedBy" , "URL", "Image", "PROV LARECAJA"]
    main(associated_files_dicts, skip_list)
    