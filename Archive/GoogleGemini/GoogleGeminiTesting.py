import google.generativeai as genai


#Test your api key here to see if it works
API_KEY = 'API_KEY'
genai.configure(api_key=API_KEY)
geminiModel=genai.GenerativeModel("gemini-pro")
#Ask me a question
response=geminiModel.generate_content("Tell me about the field museum in chicago.")
print(response.text)