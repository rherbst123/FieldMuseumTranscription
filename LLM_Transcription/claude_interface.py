import anthropic
import json
import base64

class ClaudeInterface:
    def __init__(self, model):
        api_key_filepath = "C:/Users/dancs/OneDrive/Documents/fm/ant.txt"
        api_key = self.get_api_key(api_key_filepath)
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

    def get_api_key(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            contents = f.read()
        return contents.splitlines()[0].strip() 

    def encode_image_to_base64(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')               

    def format_response(self, image_name, response_data):
        # Extract the text from the response data
        text_block = response_data[0].text

        # Split the text into lines
        lines = text_block.split('\n')

        # Create a formatted result string
        formatted_result = f"Image Name: {image_name}\n\n"
        formatted_result += "\n"
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
