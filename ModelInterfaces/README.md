## Model Interfaces

This folder supports the script, `llm_transcriptions.py`, located in the root directory. At the end of that script, a selection of configurations are available for different LLMs.

`llm_transcriptions.py` will call whichever llm interface is associated with the selected configuration and that interface will access that llm through its api and format the response returned from the llm.

For security sake, api keys are not hard-coded into the interfaces, but read from a file.

The user will need to save their api key to a .txt file and enter the filepath into the indicated variable for the interface they are using.

Results will be saved to a .txt file named according to the convention

`model_name-timestamp-transcriptions.csv`,

and saved to the `DataAnalysis/Transcriptions/TextTranscriptions` folder.


