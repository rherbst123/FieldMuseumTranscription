################################################################################
# Information for this script can be found in `LLM_Transcription-README.md`
################################################################################

import os
import requests
import base64
import time
import re
from ModelInterfaces.Utilities import utility, update_spreadsheet
from ModelInterfaces.gemini_interface import GeminiInterface
from ModelInterfaces.claude_interface import ClaudeInterface
from ModelInterfaces.openai_interface import OpenAI_Interface
from TranscriptionProcessing.image import Transcript, Run


class Transcriber:
    def __init__(self, config):
        self.modelname = config["modelname"]
        self.model = config["model"]
        self.run_name = utility.get_run_name(self.modelname)
        self.user = config["run by"] if config["run by"] else "undeclared"
        self.log_info = {"run name": self.run_name} | config
        self.prompt_filename = config["prompt filename"]
        self.dataset_urls_filename = config["dataset urls filename"]
        self.ground_truth_filename = config["ground_truth_filename"]
        self.prompt_folder = "Prompts/"
        self.dataset_urls_folder = "DataAnalysis/DataSets/"
        self.images_folder = "Images/"
        self.text_transcriptions_folder = "DataAnalysis/Transcriptions/TextTranscriptions/"
        self.logs_folder = "Logs/"
        self.setup_paths()
        #self.llm_interface = self.get_llm_interface()
        
    def setup_paths(self):
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
        if not os.path.exists(self.logs_folder):
            os.makedirs(self.logs_folder)    
        self.prompt_file_path = os.path.normpath(self.prompt_folder+self.prompt_filename)
        self.dataset_urls_filepath = os.path.normpath(self.dataset_urls_folder+self.dataset_urls_filename)
        self.text_transcriptions_filepath = os.path.normpath(self.text_transcriptions_folder+self.get_transcription_filename())
        log_for_runs_filename = f"log_for_runs-user-{self.user}.csv"
        self.log_for_runs_filepath = os.path.normpath(self.logs_folder+log_for_runs_filename)

    def get_llm_interface(self):
        if "claude" in self.modelname:
            return ClaudeInterface(self.model)
        if "gpt" in self.modelname:
            return OpenAI_Interface(self.model) 
        if "gemini" in self.modelname:
            return GeminiInterface(self.model)   
    
    def get_transcription_filename(self):
        return f"{self.run_name}-transcriptions.txt"

    def read_prompt_from_file(self):
        with open(self.prompt_file_path, "r", encoding="utf-8") as prompt_file:
            return prompt_file.read().strip()
    
    def download_images(self):
        with open(self.dataset_urls_filepath, 'r') as file:
            urls = [url.strip() for url in file.readlines()]
        for index, url in enumerate(urls):
            try:
                response = requests.get(url)
                response.raise_for_status()  # Check if the request was successful
                # prepend an index to the image name to maintain order 
                image_name_with_index = f"{index:04d}_{os.path.basename(url)}"
                image_path = os.path.join(self.images_folder, image_name_with_index)
                with open(image_path, 'wb') as img_file:
                    img_file.write(response.content)
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {url}: {e}")
        return urls

    def get_transcript_processing_data(self, llm_interface, time_elapsed):
        return {
                "created by": self.user
                } | llm_interface.get_token_costs() 

    def transcribe(self, image_urls, prompt_text):
        total_time = time.time()
        counter = 0
        image_files = sorted(os.listdir(self.images_folder))  # Ensure consistent order
        for image_name, url in zip(image_files, image_urls):
            image_path = os.path.join(self.images_folder, image_name)
            if os.path.isfile(image_path):
                start_time = time.time()
                llm_interface = self.get_llm_interface()
                formatted_transcription = llm_interface.get_response(prompt_text, image_name, image_path)
                transcription_dict = self.extract_info_from_text(formatted_transcription)
                transcript_obj = Transcript(url)
                end_time = time.time()
                elapsed_time = end_time - start_time
                transcript_processing_data = self.get_transcript_processing_data(llm_interface, elapsed_time)
                transcript_obj.create_version(created_by=self.modelname, content=transcription_dict, data=transcript_processing_data)
                counter += 1
        total_elapsed_time = time.time() - total_time

    def extract_info_from_text(self, formatted_transcription):
        regex_patterns = {
        'Image': r"Image: (.+?)\n",
        'verbatimCollectors': r"verbatimCollectors: (.+?)\n",
        'collectedBy': r"collectedBy: (.+?)\n",
        'secondaryCollectors': r"secondaryCollectors: (.+?)\n",
        'recordNumber': r"recordNumber: (.+?)\n",
        'verbatimEventDate': r"verbatimEventDate: (.+?)\n",
        'minimumEventDate': r"minimumEventDate: (.+?)\n",
        'maximumEventDate': r"maximumEventDate: (.+?)\n",
        'verbatimIdentification': r"verbatimIdentification: (.+?)\n",
        'latestScientificName': r"latestScientificName: (.+?)\n",
        'identifiedBy': r"identifiedBy: (.+?)\n",
        'verbatimDateIdentified': r"verbatimDateIdentified: (.+?)\n",
        'associatedTaxa': r"associatedTaxa: (.+?)\n",
        'country': r"country: (.+?)\n",
        'firstPoliticalUnit': r"firstPoliticalUnit: (.+?)\n",
        'secondPoliticalUnit': r"secondPoliticalUnit: (.+?)\n",
        'municipality': r"municipality: (.+?)\n",
        'verbatimLocality': r"verbatimLocality: (.+?)\n",
        'locality': r"locality: (.+?)\n",
        'habitat': r"habitat: (.+?)\n",
        'verbatimElevation': r"verbatimElevation: (.+?)\n",
        'verbatimCoordinates': r"verbatimCoordinates: (.+?)\n",
        'otherCatalogNumbers': r"otherCatalogNumbers: (.+?)\n",
        'originalMethod': r"originalMethod: (.+?)\n",
        'typeStatus': r"typeStatus: (.+?)\n",
        }
        result = {}
        for key, pattern in regex_patterns.items():
            match = re.search(pattern, formatted_transcription)
            result[key] = match.group(1) if match else ''
        return result    

    def log_run_to_csv(self):
        update_spreadsheet.append_to_csv(self.log_for_runs_filepath, [self.log_info])
    
    def run(self):
        image_urls = self.download_images()
        prompt_text = self.read_prompt_from_file()
        self.transcribe(image_urls, prompt_text)
        self.log_run_to_csv()     

if __name__ == "__main__":
    gemini_config = {
                    "prompt filename": "Prompt 1.5.2.txt",
                    "dataset urls filename": "5-bryophytes-typed-testing-urls.txt",
                    "ground_truth_filename": "5-bryophytes-typed-testing.csv",
                    "modelname": "gemini-1.5-pro",
                    "model": "gemini-1.5-pro-latest",
                    "reason for run": "test transcript object",
                    "run by": "DanS"
                    }

    sonnet_config = {
                    "prompt filename": "Prompt 1.5.2.txt",
                    "dataset urls filename": "5-bryophytes-typed-testing-urls.txt",
                    "ground_truth_filename": "5-bryophytes-typed-testing.csv",
                    "modelname": "claude-3.5-sonnet",
                    "model": "claude-3-5-sonnet-20240620",
                    "reason for run": "test transcript object",
                    "run by": "DanS"
                    }

    gpt_config = {
                    "prompt filename": "Prompt 1.5.2.txt",
                    "dataset urls filename": "5-bryophytes-typed-testing-urls.txt",
                    "ground_truth_filename": "5-bryophytes-typed-testing.csv",
                    "modelname": "gpt-4o",
                    "model": "gpt-4o-2024-08-06",
                    "reason for run": "test transcript object",
                    "run by": "DanS"
                    }

    ############################################                
    # Complete and/or modify one of the above configurations and
    # enter the name of the configuration to be run below.
    llm_configuration = gpt_config   # replace None
    # This is all that is needed to run this script
    #############################################
    transcriber = Transcriber(llm_configuration)
    transcriber.run()        
