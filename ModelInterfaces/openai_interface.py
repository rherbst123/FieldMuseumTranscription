import openai
import base64
import requests
import os
import json
from dotenv import load_dotenv

class OpenAI_Interface:
    def __init__(self, model):
        load_dotenv()  # take environment variables from .env.
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        self.headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
        }
        self.input_tokens = 0
        self.output_tokens = 0
        self.set_token_costs_per_mil()

    def set_token_costs_per_mil(self):
        if "gpt-4o" in self.model:
            self.input_cost_per_mil = 2.50
            self.output_cost_per_mil = 10.00

    def get_token_costs(self):
        return {
            "input tokens": self.input_tokens,
            "output tokens": self.output_tokens,
            "input cost $": round((self.input_tokens / 1_000_000) * self.input_cost_per_mil, 2),
            "output cost $": round((self.output_tokens / 1_000_000) * self.output_cost_per_mil, 2)
        }         


    def encode_image_to_base64(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def update_usage(self, response_data):
        if "usage" in response_data:
            usage = response_data["usage"]
            self.input_tokens += int(usage.get("prompt_tokens", 0))
            self.output_tokens += int(usage.get("completion_tokens", 0))                       

    def format_response(self, image_name, response_data):
        # Check if 'choices' is present and not empty in the response
        if "choices" in response_data and response_data["choices"]:
            content = response_data["choices"][0].get("message", {}).get("content", "")
            usage = response_data["usage"]
            formatted_output = f"Image: {image_name}\n\n{content}\n"
        else:
            # If 'choices' is empty or not present, set a default message
            formatted_output = f"Image: {image_name}\n\nNo data returned from API.\n" 
        return formatted_output

    def get_response(self, prompt_text, image_name, image_path):
        base64_image = self.encode_image_to_base64(image_path)
        payload = {
                    "model": self.model,
                    "messages": [
                    {
                        "role": "user",
                        "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                        }
                                ]
                    }
                                ],
                    "max_tokens": 2048,
                    "temperature": 0,  #Change this value to adjust the randomness of the output (We want less randomness)
                    "seed": 42  
                }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)
        response_data = response.json()
        self.update_usage(response_data)
        formatted_result = self.format_response(image_name, response_data)
        return formatted_result

if __name__ == "__main__":
    interface = OpenAI_Interface("gpt") 
    print(interface.api_key)       

           