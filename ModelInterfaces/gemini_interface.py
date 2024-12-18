import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

class GeminiInterface:
    def __init__(self, model):
        load_dotenv()  # take environment variables from .env.
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = model
        self.client = genai.GenerativeModel(model_name=self.model)

    def get_response(self, prompt_text, image_name, image_path):
        temperature = 0.0
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            # Upload the local file
            genai.configure(api_key=self.api_key)
            sample_file = genai.upload_file(path=image_path, display_name=image_name)
            response = self.client.generate_content([sample_file, prompt_text])
            # Pause to avoid overwhelming the API
            time.sleep(15)
            return f"Image: {image_name}\n\n\n" + response.text
            