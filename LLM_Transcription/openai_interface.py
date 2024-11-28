import openai
import base64
import requests
import os
import json

class OpenAI_Interface:
    def __init__(self, model):
        api_key_filepath = "C:/Users/dancs/OneDrive/Documents/fm/open.txt"
        api_key = self.get_api_key(api_key_filepath)
        self.model = model
        self.headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                       }

    def get_api_key(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            contents = f.read()
        return contents.splitlines()[0].strip() 

    def encode_image_to_base64(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')               

    def format_response(self, image_name, response_data):
        # Check if 'choices' is present and not empty in the response
        if "choices" in response_data and response_data["choices"]:
            content = response_data["choices"][0].get("message", {}).get("content", "")
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
        print("Here is the raw Data Generated",response_data)
        formatted_result = self.format_response(image_name, response_data)
        return formatted_result

           