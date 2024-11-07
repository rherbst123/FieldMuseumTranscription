# ANALYSIS TOOLS

This folder contains the scripts and other files to compare transcripiton runs to ground truth values and calculate the accuracy of a run.
The goal is to be able to process a single run or batches of runs, compare them to the ground truth for a set of images under different configurations, and save them to a spreadsheet. 



## GENERAL INSTRUCTIONS

The following details what to install and how to select a configuration for a script. For information on configurations, see `Configurations/README.md` 

## SETUP
There are a few packages related to string edit distance that need to be installed
These packages have been added to requirements.txt, which can be run in your command line interface as:

`pip install -r requirements.txt`

Alternatively, if you want to use just the scripts in this folder, you can enter the following into your command line interface:

`pip install nltk weighted-levenshtein numpy`

After everything has been installed the next step is to define and/or select a configuration for `comparison_and_accuracy.py`, `cross_validation_and_accuracy.py`, `cross_validationX2_and_accuracy.py` or `post_processing.py`. (These scripts are explained in the following sections.)

Go to the `Configurations` folder and copy the contents of `configuration_template.yaml` into a new file in the same folder. Fill out the configuration, the instructions for which are in the comments in the file.

Copy the name of that configuration into the `config_filename` variable found at the bottom of the script you are going to run. For example `config_filename = "basic_single_run.yaml"`.


A completed sample configuration can be found in `example.yaml` and also run.
Your script is ready to run!!!



## COMPARISON AND ACCURACY

`comparison_and_accuracy.py`:

This script takes a file or list of files and compares them all against the Ground Truth for that set of images.

Field matches can be done by equality or can be done within tolerances (see `Configurations/README.md`, `tolerances.py` and `string_distance.py`).

For each file, ground truth target values are classified as `valid` (non-"N/A") or `nonValid` and LLM transcription values are rated for each target value as `match` or `noMatch` (through string equality, ignoring case differences and ignoring leading and trailing whitespace differences).

#`matchValid`, #`matchNonValid`, #`noMatchValid` and #`noMatchNonValid` are processed into one or more accuracy formulas.

Also, a list of three values is determined for each fieldname: 

`[#matchValid, #gradedMatchValid, #targets]`

`#matchValid`: the number of transcription matches to non-"N/A" ground truth targets

`#gradedMatchValid`: the number of `#matchValid` plus the quantity of graded matches to valid ground truth targets, determined as `1 - Normalized Levenshtein distance`

`#targets`: the number of valid ground truth targets plus the number of LLM transcriptions that had data, rather than "N/A" for non-valid ground truth targets. 

`#targets` is the same as `#matchValid+#noMatchValid+#noMatchNonValid`

When all files have been compared, a single csv is created with the results. 

Individuals errors are stored as strings and written alongside Ground Truth targets to a separate text file.

For more information, see `DataAnalysis/Comparisons/README.md`.


## CROSS VALIDATION AND ACCURACY

`cross_validation_and_accuracy.py`:

This script takes a list of files and compares each pair of files against eachother for agreed upon transcription values.

For each pair of transcriptions, a third transcription is created. In the new transcription, agreed fields are considered cross-validated and copied in. 

When there is not agreement, "PASS" is stored as a flag to ignore this field in that image transcription during later comparison to the Ground Truth.

These results are saved as separate `csv`s, and then the script calls `comparison_and_accuracy.py`,
where comparison against the Ground Truth takes place.

## CROSS VALIDATIONx2

`cross_validationX2_and_accuracy.py`:

The same as `cross_validation_and_accuracy.py`, but looking for agreed upon values between three runs (cross-validated twice).

## POST-PROCEESSING

`post_processing.py`:

This script takes a list of files and performs post-processing operations to those fields indicated in the configuration file.

For example, if the fieldname `verbatimCollectors` is listed, `coll.`, `Coll.`, `leg.` and  `Leg.` are removed from the field transcription and saved with the filename `post_` + original_filename.

Then `comparison_and_accuracy.py` is run to compare both original values and post-processed values to the Ground Truth and saved.


## RUN VARIABILITY

`run_variability.py`:

This script determines the run-to-run variability of a given model (each run presumably done by the same LLM using the same prompt and configuration). Variability is done for a field to field and overall basis (the sum of field differences / the sum of targets).

This script does not access the configuration file, so all files must be listed in the script itself.
Istructions for doing so are in the file.

## EXPERIMENTAL SCRIPTS

There are other scripts that are used experimentally to complete cross-validated transcripts, which are by their nature only partial. Some of this work involves tracking performance over runs on individual cross-validated fields and selecting the most accurate model or model combination to use to complete a transcription. `frankenstein.py` and `cobble.py` are more or less my laboratories (DS).
