import requests

#This was made on 4-17-24 to test the claude api#

# Replace with your Claude API key
api_key = "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"

# Set up the API request
url = "https://api.anthropic.com/v1/complete"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Define the prompt
prompt = "Do you know the muffin man?"

# Prepare the payload
payload = {
    "prompt": prompt,
    "max_tokens": 100,
    "engine": "claude-v1"
}

# Make the API request
response = requests.post(url, headers=headers, json=payload)

# Check the response
if response.status_code == 200:
    print("API request successful!")
    print("Response:", response.json())
elif response.status_code == 401:
    print("API request failed: Invalid API key.")
    print("Status code:", response.status_code)
    print("Error message:", response.json().get("error", {}).get("message", "Unknown error"))
else:
    print("API request failed.")
    print("Status code:", response.status_code)
    print("Error message:", response.json().get("error", {}).get("message", "Unknown error"))

# Additional test
if response.status_code == 200:
    data = response.json()
    # Perform additional tests on the response data
    # Example:
    if "choices" in data:
        choices = data["choices"]
        for choice in choices:
            print("Choice:", choice["text"])
else:
    print("Additional test skipped: API request failed.")