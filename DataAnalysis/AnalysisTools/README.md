# AUTOMATIC ANALYSIS

This folder contains the scripts and other files to compare transcripiton runs to ground truth values and calculate the accuracy of a run.
The goal is to be able to process batches of runs, compare them to the ground truth under different configurations, and save them to a spreadsheet. 

`comparison_and_accuracy.py`:
This script takes a list of files and compares them all against the Ground Truth.
Field matches can be done by strict equality or can be done within tolerances (see below configuration and `tolerances.py`)
For each file, errors and weighted errors per field are added up and fed into an accuracy formula.
All accumulated numbers are recorded as a row in a csv file.
When all files have been compared, a single csv is created with the results.
Individuals errors are stored as strings and written alongside Ground Truth targets to a separate text file.  

`llm_agreement_and_accuracy.py`
This script takes a list of files and compares each pair of files against eachother for agreed upon transcriptions.
Agreed fields are stored as is, and when there is not agreement, "PASS" is stored for later comparison to the Ground Truth.
These results are saved as separate csv s, and then the script calls `comparison_and_accuracy.py`,
where comparison against the Ground Truth takes place.

`post_processing.py`
This script takes a list of files and performs post-processing operations to those fields indicated in the configuration file.
For example, if the fieldname `verbatimCollectors` is listed, `coll.`, `Coll.`, `leg.` and  `Leg.` are removed from the field transcription and saved with the filename `post_` + original_filename.
Then `comparison_and_accuracy.py` is run to compare both original values and post-processed values to the Ground Truth and saved.

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

After everything has been installed the next step is to define and/or select a configuration for `comparison_and_accuracy.py`, `llm_agreement_and_accuracy.py` or `post_processing.py`:
Go to the `Configurations` folder and copy the file `configuration_template.yaml` into a new file in the same folder. Fill out the configuration, the instructions for which are in the comments in the file.
Copy the name of that configuration into the `config_name` variable found at the bottom of the script you are going to run. For example `config_name = "gpt4o and sonnet3.5 repeats"`.
A completed sample configuration can be found in `example.yaml` and also run.
Your script is ready to run!!!
