import anthropic
import base64
from pathlib import Path


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def read_prompt_from_file(prompt_file_path):
    with open(prompt_file_path, "r", encoding="utf-8") as prompt_file:
        return prompt_file.read().strip()

# Initialize the Anthropic client
client = anthropic.Anthropic(
    api_key="API KEY",
)

# Path to the image file (replace with the actual file path)
image_path = "IMAGEPATH"  # Update this path to your actual image file path
encoded_image = encode_image_to_base64(image_path)

# Path to the prompt text file (replace with the actual file path)
prompt_file_path = "PROMPT"  # Update this path to your actual prompt file path
prompt = read_prompt_from_file(prompt_file_path)

# Create the message with the image and prompt
message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=2500,
    temperature=0,
    system="You are an assistant that has a job to extract text from an image and parse it out.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": encoded_image
                    }
                }
            ]
        }
    ]
)

print(message.content)
