
# Field Museum Transcription Project

This repository contains Python scripts designed to transcribe and categorize images from herbarium specimens at the Field Museum. Using the latest AI tools, specifically OpenAI's GPT-4 and Anthropic's Claude 3, this project facilitates the automated extraction and organization of text from herbarium images.

## Created and Contributed By:

- Dan Stille
- Matt Von Konrat
- Jeff Gwilliam
- Riley Herbst

## Installation

### Prerequisites
- Python 3.8 or higher
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
To access GPT-4 and Claude 3 for transcription, obtain API keys from the following:
- [OpenAI](https://platform.openai.com/docs/introduction)
- [Claude (Anthropic)](https://support.anthropic.com/en/collections/5370014-claude-api)

## Project Structure

- **AutomaticAnalysis/**: Contains automated analysis scripts for organizing transcription results.
- **ClaudeTranscription/**: Scripts and functions that interact with the Claude API for text extraction.
- **DataAnalysis/**: Tools and scripts for further data processing and analysis.
- **GoogleGemini/**: Experimental code using Google Gemini for transcription tasks.
- **OpenAI Transcription/**: Scripts and functions for integrating with OpenAI's GPT API.
- **Outputs/**: Folder for storing transcription outputs.
- **Prompts/**: Predefined prompts used for various transcription tasks.
- **TextBlob/**: Utilities leveraging TextBlob for natural language processing.

## Special Thanks

Acknowledgments to Matt Von Konrat, Jeff Gwilliam, Dan Stille, Rick Ree, Felix Grewe, Grangier Bioinformatics Center, and the Field Museum.

## License

This project is licensed under the MIT License.
