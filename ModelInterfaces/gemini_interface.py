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
        self.input_tokens = 0
        self.output_tokens = 0
        self.set_token_costs_per_mil()

    def set_token_costs_per_mil(self):
        if "gemini-1.5-pro" in self.model:
            self.input_cost_per_mil = 0.00
            self.output_cost_per_mil = 0.00

    def get_token_costs(self):
        return {
            "input tokens": self.input_tokens,
            "output tokens": self.output_tokens,
            "input cost $": round((self.input_tokens / 1_000_000) * self.input_cost_per_mil, 2),
            "output cost $": round((self.output_tokens / 1_000_000) * self.output_cost_per_mil, 2)
        }         


    def update_usage(self, response):
        usage = response.usage_metadata
        self.input_tokens += usage.prompt_token_count 
        self.output_tokens += usage.candidates_token_count

    def get_response(self, prompt_text, image_name, image_path):
        temperature = 0.0
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            # Upload the local file
            genai.configure(api_key=self.api_key)
            sample_file = genai.upload_file(path=image_path, display_name=image_name)
            response = self.client.generate_content([sample_file, prompt_text])
            self.update_usage(response)
            # Pause to avoid overwhelming the API
            time.sleep(15)
            return f"Image: {image_name}\n\n\n" + response.text
            