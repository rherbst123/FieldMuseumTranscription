# DATA ANALYSIS

Many folders in this directory contain their own READMEs and should be consulted for explanation of their respective folders.

Below are the naming conventions employed which are used to associate a run with its various data files.


### Naming Conventions

Run names are a combination of model name and timestamp of when the run was initiated.

run name:

`model-year-month-day-time`, with the timestamp formatted as: `YYYY-mm-DD-HHMM`

output returned from LLM:

`model-year-month-day-time-transcriptions.csv`

comparison of output to ground truth data:

`model-year-month-day-time-comparisons.csv`

errors flagged and saved from comparison:

`model-year-month-day-time-errors.txt`


For example, the files associated with a run done with Claude 3.5 Sonnet at 3:30 p.m. on September 12, 2024 would be:

`claude-3.5-sonnet-2024-10-12-1530-transcriptions.csv`

`claude-3.5-sonnet-2024-10-12-1530-comparisons.csv`

`claude-3.5-sonnet-2024-10-12-1530-errors.txt`

