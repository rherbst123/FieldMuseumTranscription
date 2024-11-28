## Classified Errors

This is the folder where the results of `error_classification.py` are saved.

`error_classification.py` creates an `ErrorClassifier` object which creates sets of errors to be flagged--currently punctuation, diacritic and typographic related.

The above script then compares each mismatch between an LLM transcription value and a ground truth value and sees if those mismatches can be attributed to a set of errors. The strings being compared will be manipulated until they match by editing out errors, or until all sets of errors have been tested and no match results. Since more than one error may contribute to a mismatch, mismatch tallies will track sets of errors.

Mismatch data is aggregated for fieldnames, along with the number of mismatches that can a given set of errors can FULLY account for.

Further, individual mismatches are recorded in the below form:

`edited transcription value: original transcription value____original ground truth value  (error set)`