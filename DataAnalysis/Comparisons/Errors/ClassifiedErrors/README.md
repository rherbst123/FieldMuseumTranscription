## Classified Errors

This is the folder where the results of `error_classification.py` are saved.

`error_classification.py` creates an `ErrorClassifier` object which creates sets of errors to be flagged--punctuation, diacritic, typographic related and more.

The above script then compares each mismatch between an LLM transcription value and a ground truth value and sees if those mismatches can be attributed to a set of errors. The strings being compared will be manipulated until they match by editing out errors, or until all sets of errors have been tested and no match results. Since more than one error may contribute to a mismatch, mismatch tallies will track sets of errors.

Mismatch data is aggregated for fieldnames, along with the number of mismatches that can a given set of errors can FULLY account for.

Individual mismatches are recorded in the below form:

`{mismatch number}. {error set}: {original transcription value}____{original ground truth value}`

`                                { edited transcription value }____{edited ground truth value}`

For example:

`1. spacing, comma: KIUSHIU Miyazaki Minaminaka Obi___Kiushiu, Miyazaki, Minaminaka, Obi`

`                   KIUSHIUMiyazakiMinaminakaObi___KiushiuMiyazakiMinaminakaObi`
  

The below is an example of all the mismatches accounted for in a field:

firstPoliticalUnit

    percentage mismatches accounted for: 18.8

    total mismatches: 16

    spacing: 1

    vowel diacritic: 2

    1. spacing: Veracruz___Vera Cruz

                Veracruz___VeraCruz

    2. vowel diacritic: Bolivar___Bolívar

                        Bolivar___Bolivar

    3. vowel diacritic: Bolivar___Bolívar
    
                        Bolivar___Bolivar