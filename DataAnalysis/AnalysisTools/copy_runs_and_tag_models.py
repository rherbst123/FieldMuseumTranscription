import utility
SOURCES_PATH = "AutomaticAnalysis/SourcesForPaper/"
SOURCE_FILENAMES_MODELNAMES = [("GPT-4", "Spread_5_30_1139.csv", "Spread_5_30_1025.csv"),
                                ("GPT-4o", "Spread_6_11_1050.csv", "Spread_6_11_1110.csv"),
                                ("Opus", "Spread_6_12_1404.csv", "Spread_6_12_1440.csv"),
                                ("Gemini", "SpreadJun.20.24.0153.csv", "SpreadJun.26.24.1108.csv"),
                                ("Sonnet", "SpreadJun.21.24.1043.csv", "SpreadJun.26.24.1050.csv")]

def add_modelname(modelname, transcription_dicts):
    revised_dicts = []
    for transcription_dict in transcription_dicts:
        d = {"modelname": modelname} | transcription_dict
        revised_dicts.append(d)
    return revised_dicts    
        

def main():
    for tup in SOURCE_FILENAMES_MODELNAMES:
        modelname, *filenames = tup
        for fname in filenames:
            transcription_dicts = utility.get_contents_from_csv(SOURCES_PATH+fname)
            updated_dicts = add_modelname(modelname, transcription_dicts)
            new_fname = f"{modelname}_{fname}"
            utility.save_to_csv(SOURCES_PATH+new_fname, updated_dicts)
            print(f"updated results saved to {new_fname} !!!!")


if __name__ == "__main__":
    main()