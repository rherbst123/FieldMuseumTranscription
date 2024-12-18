################################################################################
# Information for this script can be found in `LLM_Transcription-README.md`
################################################################################

import os
import requests
import base64
import time
from ModelInterfaces.Utilities import utility, update_spreadsheet
from ModelInterfaces.gemini_interface import GeminiInterface
from ModelInterfaces.claude_interface import ClaudeInterface
from ModelInterfaces.openai_interface import OpenAI_Interface
from DataAnalysis.AnalysisTools import end_to_end_comparison_and_accuracy


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
        self.llm_interface = self.get_llm_interface()
        
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
                print(f"Downloaded: {image_name_with_index}")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {url}: {e}")
        return urls

    def transcribe(self, image_urls, prompt_text):
        total_time = time.time()
        counter = 0
        with open(self.text_transcriptions_filepath, 'w', encoding='utf-8') as file:
            image_files = sorted(os.listdir(self.images_folder))  # Ensure consistent order
            for image_name, url in zip(image_files, image_urls):
                image_path = os.path.join(self.images_folder, image_name)
                if os.path.isfile(image_path):
                    print(f"Processing entry {counter + 1}: {image_name}")
                    start_time = time.time()
                    formatted_result = self.llm_interface.get_response(prompt_text, image_name, image_path)
                    try:
                        file.write(formatted_result)
                        file.write(f"\nURL: {url}\n")
                        print(formatted_result)
                    except TypeError as e:
                        print(f"TypeError encountered: {e}")
                        file.write(f"Image: {image_name}\nResponse: {response_data}\n")
                        file.write(f"\nURL: {url}\n")
                        print(f"Image: {image_name}\nResponse: {response_data}\n")
                    file.write("=" * 50 + "\n")
                    print(f"Completed processing: {image_name}")
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    print(f"Completed processing entry {counter + 1} in {elapsed_time:.2f} seconds")
                    counter += 1
        self.log_info["#images processed"] = str(counter)
        total_elapsed_time = time.time() - total_time
        self.log_info["run time"] = f"{total_elapsed_time:.2f} seconds"           
        print(f"results saved to: {self.text_transcriptions_filepath}")

    def log_run_to_csv(self):
        update_spreadsheet.append_to_csv(self.log_for_runs_filepath, [self.log_info])
    
    def ask_to_proceed_or_cancel(self, msg):
        if input(f"{msg} (yes/no): ").strip().lower() != "yes":
            print("Processing cancelled by the user.")
            quit()

    def offer_to_transcribe(self, image_urls):
        self.ask_to_proceed_or_cancel(msg="Proceed with transcribing the images?")
        prompt_text = self.read_prompt_from_file()
        self.transcribe(image_urls, prompt_text)
        self.log_run_to_csv()         

    def offer_to_process_and_compare(self):
        self.ask_to_proceed_or_cancel(msg="Proceed with processing and comparing to ground truth?")
        end_to_end_comparison_and_accuracy.process_and_compare(self.run_name, self.ground_truth_filename)    
                
    def offer_to_classify_errors(self):
        self.ask_to_proceed_or_cancel(msg="Proceed with classifying errors?")
        end_to_end_comparison_and_accuracy.classify_errors(self.run_name, self.ground_truth_filename)        

    def run(self):
        image_urls = self.download_images()
        self.offer_to_transcribe(image_urls)
        self.offer_to_process_and_compare()
        self.offer_to_classify_errors()      

if __name__ == "__main__":
    gemini_config = {
                    "prompt filename": "Prompt 1.5.2.txt",
                    "dataset urls filename": "5-bryophytes-typed-testing-urls.txt",
                    "ground_truth_filename": "5-bryophytes-typed-testing.csv",
                    "modelname": "gemini-1.5-pro",
                    "model": "gemini-1.5-pro-latest",
                    "reason for run": "test end-to-end processing",
                    "run by": "DS"
                    }

    sonnet_config = {
                    "prompt filename": "Prompt 1.5.2.txt",
                    "dataset urls filename": "5-bryophytes-typed-testing-urls.txt",
                    "ground_truth_filename": "5-bryophytes-typed-testing.csv",
                    "modelname": "claude-3.5-sonnet",
                    "model": "claude-3-5-sonnet-20240620",
                    "reason for run": "test end-to-end processing",
                    "run by": "DS"
                    }

    gpt_config = {
                    "prompt filename": "Prompt 1.5.2.txt",
                    "dataset urls filename": "5-bryophytes-typed-testing-urls.txt",
                    "ground_truth_filename": "5-bryophytes-typed-testing.csv",
                    "modelname": "gpt-4o",
                    "model": "gpt-4o-2024-08-06",
                    "reason for run": "test end-to-end processing",
                    "run by": "DS"
                    }

    ############################################                
    # Complete and/or modify one of the above configurations and
    # enter the name of the configuration to be run below.
    llm_configuration = None   # replace None
    # This is all that is needed to run this script
    #############################################
    transcriber = Transcriber(llm_configuration)
    transcriber.run()        
