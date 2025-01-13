# Documentation for llm_transcription.py

## Overview

`llm_transcription.py` allows a user to select an llm and have it transcribe a set of images and save that output to a .txt file.

It additionally offers to 1) convert that output to a .csv file, 2) compare that data to ground truth data, and 3) classify mismatches due to formatting, punctuation or typographic errors or any combination of those errors.

## Steps to run llm_transcription.py

1) Set up environment: run `setup.py`

The packages in `requirements.txt` must be installed and the api key to run a particular llm must be set in the `.env` file.

Running `setup.py` will install `requirements.txt`and create the `.env` file and facilitate adding api keys to the `.env` file.

The `.env` file is created only on the user's machine and is excluded from the repository via the `gitignore`, to ensure that api keys are not shared accidentally.

If the user does not have an api key for a particular llm handy when `setup.py` prompts them for it, `None` can be entered, and the user can add that api key to the `.env` file later if they need to.

To access GPT models, the user needs to obtain an api key from openai.com:

https://platform.openai.com/docs/api-reference/authentication

To access Gemini models, the user needs to obtain and api key from ai.google

https://ai.google.dev/gemini-api/docs/api-key

To access Claude models, the user needs to obtain and api key from anthropic.com

https://support.anthropic.com/en/articles/8114521-how-can-i-access-the-anthropic-api

2) Choose a configuration

`llm_transcription.py` provides individual configurations for each llm which can be run. The configurations are already filled out, but should be modified by the user according to their needs. A sample configuration with descriptions:


gemini_config = {
                    "prompt filename": "Prompt 1.5.2.txt",   `<--the filename of the prompt to be used in the Prompts folder`

                    "dataset urls filename": "5-bryophytes-typed-testing-urls.txt",   `<--the name of the file in the DataAnalysis/DataSets folder containing the urls to be downloaded`

                    "ground_truth_filename": "5-bryophytes-typed-testing.csv",  `<--the ground truth filename in the DataAnalysis/GroundTruths folder` 

                    "modelname": "gemini-1.5-pro", `<--the name of model which will be used for naming files`

                    "model": "gemini-1.5-pro-latest", `<--the specific model which should be used by the API`

                    "reason for run": "test script functionality", `<--the reason for the run which will be added to the runs log`

                    "run by": "DS" `<--the name of the user conducting the run`
                    }

3) Assign selected configuration

Near the end of the file, assign the name of the configuration to be used to the variable `llm_configuration`, as shown below.

############################################  

    # Complete and/or modify one of the above configurations and

    # enter the name of the configuration to be run below.

    llm_configuration = gemini_config  `<--the name of the configuration to be run`

    # This is all that is needed to run this script

#############################################

The script is ready to run!!!

### What it does

1) Download the images to be transcribed, using the urls provided.

2) Have the selected llm transcribe those images and save those results to a .txt file in the `DataAnalysis/Transcriptions/TextTranscriptions` folder.

3) Ask the user if they would like to save the results to a .csv file and compare the results to ground truth data. Comparsions will be saved to the `DataAnalysis/Comparisons/SingleComparisons` folder.

4) Ask the user if they would like to classify mismatches due to formatting, punctuation or typographic errors (or any combination of those errors). Classified errors will be saved to the `DataAnalysis/Comparisons/Errors/ClassifiedErrors` folder.

5) Log information pertaining to the run to a .csv file. See below.


### Logs

Information pertaining to a run will be saved to a .csv file in the `Logs` folder.

The name of the file will be: `log_for_runs-user-{username}.csv`

If a log is already associated with a username, the run information will be appended to that file.
