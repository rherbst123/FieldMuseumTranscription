## CONFIGURATION

Follow the below comments to fill out your configuration

```
{
    # enter the name you want to give your configuration
    "CONFIGURATION_NAME": "",


    "COMPARISON_CONFIG": {
                         # this is the field used for identifying what image the error refers to
                        "RECORD_REF_FIELDNAME": "accessURI",

                        "SKIP_LIST": ["Image Name", "catalogNumber", "Dataset Source", "accessURI", "Label only?", "modifiedBy", "verifiedBy" , "substrate", "URL", "Image"], 

                        # if you want to use only certain fields, add them to "CORE_FIELDS_LIST"
                            # and set "USE_CORE_FIELDS" to "True"
                        "CORE_FIELDS_LIST": [],
                        "USE_CORE_FIELDS": "False",

                        # list all the names of the .csv files you want to run in "LLM_SPREAD_SOURCES"
                            # do not set the SOURCE directory here
                        "LLM_SPREAD_SOURCES": [""],

                        # insert the name of the ground truth file you are going to use below
                        "GROUND_TRUTH_FILENAME": "",

                        # insert the name of the file you want to create for your spreadsheet/csv
                            # this file, if it already exists, will be overwritten
                        "RESULT_FILENAME": "",

                        # insert the name of the text file you want transcription errors logged to
                            # this file, if it already exists, will be appended
                        "ERRORS_FILENAME": "",

                        # the SOURCE directory/folder can be modified below
                        "SOURCE_PATH": "AutomaticAnalysis/Sources/",

                        # the RESULTS directory/folder can be modified below
                        "RESULTS_PATH": "AutomaticAnalysis/Results/"
                    },
    
    "EDIT_DISTANCE_CONFIG": {
                             "comment1": "COSTS are lists of lists.",
                             "comment2": "For INSERT_CHAR and DELETE_CHAR, the order of the two elements of the inner list is char, cost.",
                             "comment3": "For SUBSTITUTION_CHAR and TRANSPOSITION_CHAR, the order of the three elements of the inner list is char to substitute in, target char to be substuted out, cost.",
                             "ALL_FIELDS_CUSTOM_COSTS": {
                                                "INSERT_CHAR_COSTS": [[]],  
                                                "DELETE_CHAR_COSTS":  [[]],
                                                "SUBSTITUTION_CHAR_COSTS": [[]],
                                                "TRANSPOSITON_CHAR_COSTS": [[]]

                             },

                             # enter "True" below to use ONLY the fieldnames declared in FIELDNAMES_COSTS
                                # entering "False" below will have the edit_distance module first look among the fieldnames for costs
                                  #  and then use the costs above if the fieldname is not specified
                             "USE_FIELDNAMES_EXCLUSIVELY": "",

                             # FIELDNAMES COSTS take precedence over ALL_FIELDS_CUSTOM_COSTS
                             "FIELDNAMES_COSTS": {
                                                  "": {"INSERT_CHAR_COSTS": [[]],  
                                                                       "DELETE_CHAR_COSTS":  [[]],
                                                                       "SUBSTITUTION_CHAR_COSTS": [[]],
                                                                       "TRANSPOSITON_CHAR_COSTS": [[]]
                                                                       }
                        }
                            },

    "TOLERANCES_CONFIG": {
                          # enter "True" enable tolerances for comparisons
                          "TOLERANCES_ALLOWED": "",

                          # enter "True" to allow using a graded match among the tolerances
                             # graded_matches are derived from edit distances (Levenshtein distances)
                                # essentially: graded_match = 1 - scaled Levenshtein distance 
                          "USE_GRADED_MATCH_THRESHOLD": "",

                          # modify that thresheold below; it should be a value between 0.0 and 1.0
                          "GRADED_MATCH_THRESHOLD": "0.99999",

                          # TOLS are dictionary of fieldnames and tolerances pairs, where the tolerances are 
                            # listed as strings in a list (see options in tolerances.py)
                               # for example: {"identifiedBy": ["missing_abbreviation_point", "double_space"]}
                          "TOLS": {}

    }
    
    
}
