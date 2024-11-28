import google.generativeai as genai
import os
import time

class GeminiInterface:
    def __init__(self, model):
        api_key_filepath = "C:/Users/dancs/OneDrive/Documents/fm/google.txt"
        self.api_key = self.get_api_key(api_key_filepath)
        self.model = model
        self.client = genai.GenerativeModel(model_name=self.model)
        
    def get_api_key(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            contents = f.read()
        return contents.splitlines()[0].strip()

    def get_response(self, prompt_text, image_name, image_path):
        temperature = 0.0
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            # Upload the local file
            genai.configure(api_key=self.api_key)
            sample_file = genai.upload_file(path=image_path, display_name=image_name)
            response = self.client.generate_content([sample_file, prompt_text])
            # Pause to avoid overwhelming the API
            time.sleep(10)
            return response.text
            