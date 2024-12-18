# Prompt Analysis and Error Analysis

## Prompt Analysis

The following are the scripts that can be run to analyze prompts.

The script `compare_prompt_field_descriptions.py` takes a list of prompts and iterates through the fileds of each pair of successive prompts. The description for each field of those two prompts are displayed to the console and also saved to a .txt file.

The script `change_tracker.py` iterates through a list of fieldnames and notes changes in accuracy and edit distance along with changes in field descriptions.

Results are saved to a .csv file in the `DataAnalysis/Comparisons/BatchComparisons` directory.

## Error Analysis

The script `error_classification.py` creates an `ErrorClassifier` object which creates sets of errors to be flagged--punctuation, diacritic, typographic related and more.

The above script then compares each mismatch between an LLM transcription value and a ground truth value and sees if those mismatches can be attributed to a set of errors. The strings being compared will be manipulated until they match by editing out errors, or until all sets of errors have been tested and no match results. Since more than one error may contribute to a mismatch, mismatch tallies will track sets of errors.

Mismatch data is aggregated for fieldnames, along with the number of mismatches that can a given set of errors can FULLY account for.

Results are saved to a .txt file in the `DataAnalysis/Comparisons/Errors/ClassifiedErrors` folder. See `DataAnalysis/Comparisons/Errors/ClassifiedErrors/README.md` for an explanation of how results are formatted. 

Since `ErrorCLassifier` is a class, an instance can be created and used by `comparison_and_accuracy.py` to integrate error classification into comparisons, rather than running `error_classification.py` separately later.

Also, it is possible to classify all the runs listed on a spreadsheet: `classify_errors_for_runs_on_spreadsheet.py`


