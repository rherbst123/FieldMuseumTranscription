#    CONFIGURATIONS

There are a few configuration templates available in this folder. Make a copy of whichever template suits your needs and fill out the necessary fields. The necessary fields are described below. Instructions for additonal options appear in the templates themselves. Rename the copy and enter that into the line `config_filename = "" ` located towards the bottom of the comparsion script you wish to run.


##  BASIC CONFIGURATION TYPES

Basic configurations come in two flavors: `single_run` and `batch_run`

### SINGLE RUN

`single_run` configurations are set up to process just one LLM transcription.

All that needs to be entered by a user into a `single_run` configuration is the name of the run.

A `RUN_NAME` takes the form: `model-year-month-day-time`, with the timestamp formatted as:

`YYYY-mm-DD-HHMM`

Whichever script is used will locate the transcription for that run in the designated `Transcriptions` folder.

Though files in the `Transcriptions` folder are expected to have `-transcriptions` in their name,

DO NOT include `-transcriptions` in the `RUN_NAME`. The script will add that, as it will add

`-comparisons` and `-errors` to comparison output.

### BATCH RUN

`batch_run` configurations are set up to process multiple LLM transcriptions.

The user needs to enter two things into a `batch_run` configuration: 

1) the names of each run, following the above naming conventions, and 

2) the `BATCH_NAME`, which will be used in the filename to which comparisons are saved.

A `batch_run` saves comparison values to a single spreadsheet, with each run a row in the spreadsheet.

## ADDITIONAL ELEMENTS

There are comments in the configuration templates to help guide the use of additional/optional elements. Here are some general notes.

### COMPARISON NAME

There is an option to provide a `COMPARISON_NAME`, which will be appended to the comparison filename after the `RUN_NAME` or `BATCH_NAME`. This can be useful when using only certain fields or when enabling `TOLERANCES`.

### TOLERANCES

Tolerances can be used for comparisons, but tolerances must first be enabled in the configuration file and individual tolerances must be listed as defaults or according to field. See `tolerances.py` for tolerance options.

### EDIT DISTANCE / LEVENSHTEIN DISTANCE

Edit distance is one available tolerance that needs to be enabled among the tolerances, along with an edit distance threshold.

There is a separate section for customizing edit distance costs, for all fields and for specific fields.

See instructions in the configuration file for more description.