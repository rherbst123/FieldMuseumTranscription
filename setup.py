import os

def install_requirements():
    os.system("pip install -r requirements.txt")

def save_to_env(contents):
    with open(".env", "w", encoding="utf-8") as f:
        f.write(contents)    

def convert_dict_to_string(d):
    return "\n".join([f"{key} = {val}" for key, val in d.items()]) 

def request_variables():
    d = {}
    print("\nYou have the option to save your api keys now.")
    print("If you do not set your api keys now, enter 'None' when prompted")
    print("The .env file will be created with the values you provide, which you can add or modify later.\n")
    for key in ["OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"]:
        val = input(f"Enter the value for {key} or enter 'None': ")
        d[key] = val or "None"
    return d    
              
def create_dotenv_file():
    d = request_variables()
    contents = convert_dict_to_string(d)
    save_to_env(contents)     
    
def main():
    create_dotenv_file()
    install_requirements()

if __name__ == "__main__":
    main()