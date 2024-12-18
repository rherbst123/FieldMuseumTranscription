import anthropic
import json
import base64
import os
from dotenv import load_dotenv

class ClaudeInterface:
    def __init__(self, model):
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

    def encode_image_to_base64(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')               

    def format_response(self, image_name, response_data):
        # Extract the text from the response data
        text_block = response_data[0].text
        lines = text_block.split('\n')
        formatted_result = f"Image: {image_name}\n\n\n"
        formatted_result += "\n".join(lines)
        return formatted_result    

    def get_response(self, prompt_text, image_name, image_path):
        base64_image = self.encode_image_to_base64(image_path)
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2500,
            temperature=0,
            system="You are an assistant that has a job to extract text from an image and parse it out.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }
            ]
        )
        response_data = message.content
        print("This is response_data: ", response_data)
        formatted_result = self.format_response(image_name, response_data)
        return formatted_result
