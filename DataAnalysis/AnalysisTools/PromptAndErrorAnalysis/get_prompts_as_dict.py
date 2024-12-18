import re
import utility

def get_contents_from_txt(filepath):
    return utility.get_contents_from_txt(filepath)

def remove_preamble(text):
    preamble = "Please transcribe and expand all details from this herbarium label. Do not Include any Full stops. If there is no information present for a field insert N/A. If in a language other than English, do not translate. If unsure at all, state “unsure and check”. I require information on the following categories and to output in the following order(Make sure the fields are exactly as typed)."
    return re.sub(preamble, "", text)           

def get_field_dict(prompt_filename):
    prompt_folder = "Prompts/"
    prompt_path = prompt_folder+prompt_filename
    raw_prompt = get_contents_from_txt(prompt_path)   
    cleaned_prompt = remove_preamble(raw_prompt)
    lines = cleaned_prompt.splitlines()
    instructions = []
    for line in lines:
        mtch = re.match(r"(.+?):\s?(.+)", line)
        if mtch:
            instructions += [(mtch.group(1), mtch.group(2))]
    return dict(instructions)

if __name__ == "__main__":
    prompt_filename = "Prompt 1.5.2.txt"
    d = get_field_dict(prompt_filename)
    print(d)
