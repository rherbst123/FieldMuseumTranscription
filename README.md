
# Field Museum Transcription Project

This project contains Python scripts designed to transcribe and categorize images from herbarium specimens at the Field Museum. Using assorted LLM's specifically OpenAI's GPT-4 and Anthropic's Claude 3 and 3.5, this project facilitates the automated extraction and organization of text from herbarium images.

## Created and Contributed By:

- Dan Stille
- Matt Von Konrat
- Jeff Gwilliam
- Riley Herbst

## Installation

### Prerequisites
- Python 3.9 or higher
- `pip` (Python package installer)

### Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/rherbst123/FieldMuseumTranscription
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### API Keys
To access GPT and Claude  for transcription, obtain API keys from the following:
- [OpenAI](https://platform.openai.com/docs/introduction)
- [Claude (Anthropic)](https://support.anthropic.com/en/collections/5370014-claude-api)

## Project Directory

- **ClaudeTranscription**: Scripts and functions that interact with the Claude API for text extraction.
- **DataAnalysis**: Data, tools and scripts for further data processing and analysis.
    - **/AnalysisTools**: Contains automated analysis scripts for organizing transcription results.
- **GoogleGemini**: Experimental code using Google Gemini for transcription tasks.
- **OpenAI Transcription**: Scripts and functions for integrating with OpenAI's GPT API.
- **Outputs**: Folder for storing transcription outputs.
- **llm_transcription.py**: single script that can be configured to transcribe from various LLMs.
- **Prompts**: Predefined prompts used for various transcription tasks.


## Special Thanks

Acknowledgments to Matt Von Konrat, Jeff Gwilliam, Dan Stille, Rick Ree, Felix Grewe, Grangier Bioinformatics Center, and the Field Museum.

## License

This project is licensed under the MIT License.
