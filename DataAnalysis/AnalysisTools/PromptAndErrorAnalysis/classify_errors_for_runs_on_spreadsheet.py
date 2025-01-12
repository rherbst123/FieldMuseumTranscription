import utility
from error_classification import ErrorClassifier


def main(associated_files_dicts):
    transcription_folder = "DataAnalysis/Transcriptions/"
    for associated_files_dict in associated_files_dicts:
        run_name = associated_files_dict["Run Name"]
        ground_truth_filename = associated_files_dict["Ground Truth"]
        transcription_filename = f"{run_name}-transcriptions.csv"
        print(f"{transcription_filename = }")
        transcriptions_filepath = transcription_folder+transcription_filename
        try:
            fieldnames = ErrorClassifier.get_fieldnames_from_saved_data(transcriptions_filepath)
        except FileNotFoundError:
            print("File Not Found: "+transcriptions_filepath) 
            continue    
        ec = ErrorClassifier(run_name, fieldnames)
        ec.run(run_name, ground_truth_filename)     

if __name__ == "__main__":
    spread_filepath = "DataAnalysis/associated_files_for_paper.csv"
    associated_files_dicts = utility.get_contents_from_csv(spread_filepath)
    main(associated_files_dicts)
    