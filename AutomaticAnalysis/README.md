# ACCURACY TESTING

This folder contains the scripts and other files to compare transcripiton runs to ground truth values and calculate the accuracy of a run.
The goal is to be able to process batches of runs, compare them to the ground truth under different configurations, and save them to a spreadsheet. 

`comparison_and_accuracy.py`:
This script takes a list of files and compares them all against the Ground Truth.
For each file, errors and weighted errors per field are added up and fed into an accuracy formula.
All accumulated numbers are recorded as a row in a csv file.
When all files have been compared, a single csv is created with the results.
Individuals errors are stored as strings and written alongside Ground Truth targets to a separate text file.  

`llm_agreement_and_accuracy.py`
This script takes a list of files and compares each pair of files against eachother for agreed upon transcriptions.
Agreed fields are stored as is, and when there is not agreement, "PASS" is stored for later comparison to the Ground Truth.
These results are saved as separate csv s, and then the script calls `comparison_and_accuracy.py`,
where comparison against the Ground Truth takes place.

`run_variability.py`
This script determines the run-to-run variability of a given model (each run presumably using the same prompt and configuration). Variability is done for a field to field and overall basis (the sum of field differences / the sum of targets).
This script does not access the configuration file, so all files must be listed in the script itself.
Istructions for doing so are in the file.


# INSTRUCTIONS

The following details what to install, how to configure, how to use a configuration in a script and some notes on configuration options.

## SETUP
There are two packages related to string edit distance that need to be installed
These two packages have been added to requirements.txt, which can be run as:

`pip install -r requirements.txt`

But if you already have this project installed, you may want to use just:

`pip install nltk weighted-levenshtein`

After everything has been installed the next step is to define and/or select a configuration for `comparison_and_accuracy.py` or `llm_agreement_and_accuracy.py`:
Go to the file `transcription_config.py` and fill out one of the blank configurations, the instructions for which are in the next section.
Copy the name of that configuration into `config_name` variable found at the bottom of the script you are going to run. For example `config_name = "gpt4o and sonnet3.5 repeats"`.
Your script is ready to run!!!


## CONFIGURATION

Follow the below comments to fill out your configuration

```
# replace "blank1" with the name you want to give your configuration
"blank1": {
        # this is the field used for identifying what image the error refers to
        "RECORD_REF_FIELDNAME": "accessURI",

        "SKIP_LIST": ["Image Name", "catalogNumber", "Dataset Source", "accessURI", "Label only?", "modifiedBy", "verifiedBy" , "substrate", "URL", "Image"], 

        # if you want to use only certain fields, add them to "CORE_FIELDS_LIST"
           # and set "USE_CORE_FIELDS" to "True"
        "CORE_FIELDS_LIST": [],
        "USE_CORE_FIELDS": "False",

        # select the EDIT_DISTANCE_CLASS you want to use from `string_distance.py`
           # the options here are "NLTKDistance" and "WeightedLevenshtein"
              # "WeightedLevenshtein" allows for the customization of costs for string edit operations
                # and is configured below by following the included comments
                   # if you are using "NLTKDistance", the "EDIT_DISTANCE_CONFIG" can be left blank
        "EDIT_DISTANCE_CLASS": "",
        "EDIT_DISTANCE_CONFIG": {"comment1": "COSTS are lists of lists.",
                                 "comment2": "For INSERT_CHAR and DELETE_CHAR, the order of the two elements of the inner list is char, cost.",
                                 "comment3": "For SUBSTITUTION_CHAR and TRANSPOSITION_CHAR, the order of the three elements of the inner list is char to substitute in, target char to be substuted out, cost.",
                                 "INSERT_CHAR_COSTS": [[]],  
                                 "DELETE_CHAR_COSTS":  [[]],
                                 "SUBSTITUTION_CHAR_COSTS": [[]],
                                 "TRANSPOSITON_CHAR_COSTS": [[]]
                                },
        
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
        "SOURCE_PATH": "AccuracyTesting/AccuracyTestingSources/",

        # the RESULTS directory/folder can be modified below
        "RESULTS_PATH": "AccuracyTesting/AccuracyTestingSources/"
    },
```

