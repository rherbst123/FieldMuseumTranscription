import anthropic
import base64

# Replace with your API key
API_KEY = "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"

# Initialize the client with your API key
client = anthropic.Anthropic(api_key=API_KEY)

# Open the image file and read its contents
with open('c:\\\\Users\\\\riley\\\\Desktop\\\\Portal\\\\Code\\\\Python\\\\Outputs\\\\Images\\\\0000_V0573776F.jpg', 'rb') as f:
    image_data = f.read()

# Encode the image data as base64
image_data_base64 = base64.b64encode(image_data).decode('utf-8')

message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",  # Change this if your image is a different format
                        "data": image_data_base64,
                    },
                },
                {
                    "type": "text",
                    "text": "Describe this image."
                }
            ],
        }
    ]
)

print(message)