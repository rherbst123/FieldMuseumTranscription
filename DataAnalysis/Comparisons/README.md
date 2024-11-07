### COMPARISONS

This folder contains CSVs of LLM transcriptions compared to the Ground Truth for the set images transcribed.

Comparisons are done the `Comparison` class in the file `comparison_and_accuracy.py`

The comparison results are listed broken down by field name and run accuracy is calculated.

Fields: the result for each field is entered as a list of three elements. Field accuracy should be calculated as the first element divided by the third element:

`[#matchValid, #gradedMatchValid, #targets]`

`#matchValid`: the number of transcription matches to non-"N/A" ground truth targets

`#gradedMatchValid`: the number of `#matchValid` plus the quantity of graded matches to valid ground truth targets, determined as `1 - Normalized Levenshtein distance`

`#targets`: the number of valid ground truth targets plus the number of LLM transcriptions that had data, rather than "N/A" for non-valid ground truth targets. 

`#targets` is the same as `#matchValid+#noMatchValid+#noMatchNonValid`

`SingleComparisons/` contains comparisons of just one LLM run against the Ground Truth. As such, each CSV will have just one row.

`BatchComparisons/` contains comparisons of multiple LLM runs against the Ground Truth. As such, each CSV will have multiple rows. This is useful for ease of comparison between repeat runs.

`Errors` contains text files structured for looking at errors on a field by field basis. `BatchComparisons` save to one errors file.

The top of the file contains LLM transcription sourcefile information and configuration data used for comparison. Configuration objects are copied in full into the file.

It is important to first check 




