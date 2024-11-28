import os
import requests
import base64
import time
from Utilities import utility, update_spreadsheet
from gemini_interface import GeminiInterface
from claude_interface import ClaudeInterface
from openai_interface import OpenAI_Interface

class Transcriber:
    def __init__(self, config):
        self.modelname = config["modelname"]
        self.model = config["model"]
        self.run_name = utility.get_run_name(self.modelname)
        self.log_info = {"run name": self.run_name} | config
        self.prompt_filename = config["prompt filename"]
        self.dataset_urls_filename = config["dataset urls filename"]
        self.prompt_folder = "Prompts/"
        self.dataset_urls_folder = "DataAnalysis/DataSets/"
        self.images_folder = "Images/"
        self.text_transcriptions_folder = "DataAnalysis/Transcriptions/TextTranscriptions/"
        self.setup_paths()
        self.llm_interface = self.get_llm_interface()
        self.log_filepath = "Outputs/log_runs.csv"

    def setup_paths(self):
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
        self.prompt_file_path = os.path.normpath(self.prompt_folder+self.prompt_filename)
        self.dataset_urls_filepath = os.path.normpath(self.dataset_urls_folder+self.dataset_urls_filename)
        self.text_transcriptions_filepath = os.path.normpath(self.text_transcriptions_folder+self.get_transcription_filename())

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
        # Read URLs from file and store them in a list
        with open(self.dataset_urls_filepath, 'r') as file:
            urls = file.readlines()

        # Download each image, appending an index to maintain order
        for index, url in enumerate(urls):
            url = url.strip()  # Remove any extra whitespace
            try:
                response = requests.get(url)
                response.raise_for_status()  # Check if the request was successful

                # Extract image name from URL
                image_name = os.path.basename(url)
                # Modify image name to include index for ordering
                image_name_with_index = f"{index:04d}_{image_name}"  # Prefix index, ensuring it's zero-padded
                image_path = os.path.join(self.images_folder, image_name_with_index)

                with open(image_path, 'wb') as img_file:
                    img_file.write(response.content)
                print(f"Downloaded: {image_name_with_index}")

            except requests.exceptions.RequestException as e:
                print(f"Error downloading {url}: {e}")

        # Return the list of URLs
        return urls

# Download images and collect URLs

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
        update_spreadsheet.append_to_csv(self.log_filepath, [self.log_info])

    
    def get_user_confirmation(self):
        user_confirmation = input("Proceed with parsing the images? (yes/no): ").strip().lower()
        if user_confirmation != "yes":
            print("Parsing cancelled by the user.")
            quit()
            

    def run(self):
        image_urls = self.download_images()
        self.get_user_confirmation()
        prompt_text = self.read_prompt_from_file()
        self.transcribe(image_urls, prompt_text)
        self.log_run_to_csv()       




if __name__ == "__main__":
    gemini_config = {
                    "prompt filename": "Prompt 1.5.2.txt",
                    "dataset urls filename": "5-bryophytes-typed-testing-urls.txt",
                    "modelname": "gemini-1.5-pro",
                    "model": "gemini-1.5-pro-latest",
                    "reason for run": "test published logging",
                    "run by": "DS"
                    }

    sonnet_config = {
                    "prompt filename": "Prompt 1.5.2.txt",
                    "dataset urls filename": "5-bryophytes-typed-testing-urls.txt",
                    "modelname": "claude-3.5-sonnet",
                    "model": "claude-3-5-sonnet-20240620",
                    "reason for run": "test published logging",
                    "run by": "DS"
                    }

    gpt_config = {
                    "prompt filename": "Prompt 1.5.2.txt",
                    "dataset urls filename": "5-bryophytes-typed-testing-urls.txt",
                    "modelname": "gpt-4o",
                    "model": "gpt-4o-2024-08-06",
                    "reason for run": "test run logging",
                    "run by": "DS"
                    }

                    

    transcriber = Transcriber(gemini_config)
    transcriber.run()        
