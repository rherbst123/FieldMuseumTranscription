import anthropic
import base64
import os
import time
import json

#business as usual 
api_key = "api key"
prompt_file_path = "prompt.txt"  
image_path_folder = "image folder"  
output_file_path = "output.txt"  


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def read_prompt_from_file(prompt_file_path):
    with open(prompt_file_path, "r", encoding="utf-8") as prompt_file:
        return prompt_file.read().strip() #just a warning for myself. please always encode your files in utf-8.

def format_response(image_name, response_data):
    formatted_result = f"Image: {image_name}\nResponse: {json.dumps(response_data, indent=2)}\n"
    return formatted_result

client = anthropic.Anthropic(api_key=api_key) 


prompt_text = read_prompt_from_file(prompt_file_path)


total_time = time.time()
counter = 0 

with open(output_file_path, 'w', encoding='utf-8') as file:
    for image_name in os.listdir(image_path_folder):
        image_path = os.path.join(image_path_folder, image_name)
        if os.path.isfile(image_path):
            print(f"Processing entry {counter + 1}: {image_name}")
            start_time = time.time()
            base64_image = encode_image_to_base64(image_path)

          #This was the issue. Dont know why or when this was a change to be made but its changed now. But if i had the old payload it broke it
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2500,
                temperature=0,
                system="You are an assistant that has a job to extract text from an image and parse it out.", #system prompt. Something anthropic actually has decent documentation for. 
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

         
            formatted_result = format_response(image_name, response_data)
            file.write(formatted_result)
            file.write("="*50 + "\n")
            print(f"Completed processing: {image_name}")
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Completed processing entry {counter + 1} in {elapsed_time:.2f} seconds")

            counter += 1

finalend_time = time.time()
final_time = finalend_time - total_time
print(f"Total entries processed: {counter}")
print(f"Total processing time: {final_time:.2f} seconds")
print("All Done!")
print(f"Results saved to {output_file_path}")

