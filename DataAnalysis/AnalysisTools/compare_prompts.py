import re

def get_contents_from_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def get_fieldnames(d):
    return list(d.keys())

def get_field_instruction(d, fieldname):
    return d.get(fieldname, "Field not present in this prompt")

def pair_and_print_field_instructions(d1, d2, fieldname):
    print(f"{d1['prompt_name']}\n{fieldname}: {get_field_instruction(d1, fieldname)}") 
    print(f"{d2['prompt_name']}\n{fieldname}: {get_field_instruction(d2, fieldname)}") 
    print(50*"=")

def remove_preamble(text):
    preamble = "Please transcribe and expand all details from this herbarium label. Do not Include any Full stops. If there is no information present for a field insert N/A. If in a language other than English, do not translate. If unsure at all, state “unsure and check”. I require information on the following categories and to output in the following order(Make sure the fields are exactly as typed)."
    return re.sub(preamble, "", text)    

def get_field_dict(path_prompt, prompt_name):
    raw_prompt = get_contents_from_txt(path_prompt)   
    cleaned_prompt = remove_preamble(raw_prompt)
    lines = cleaned_prompt.splitlines()
    instructions = []
    for line in lines:
        mtch = re.match(r"(.+?):\s?(.+)", line)
        if mtch:
            instructions += [(mtch.group(1), mtch.group(2))]
    return {"prompt_name": prompt_name} | dict(instructions)

def get_fieldname_union(dictA, dictB):
    return list(dictA.keys() | dictB.keys())  

def compare_prompts(prompt_nameA, path_promptA, prompt_nameB, path_promptB):
    dict_A = get_field_dict(path_promptA, prompt_nameA)
    dict_B = get_field_dict(path_promptB, prompt_nameB)
    all_fieldnames = get_fieldname_union(dict_A, dict_B)
    for fieldname in all_fieldnames:
        pair_and_print_field_instructions(dict_A, dict_B, fieldname)

def compare_all_prompts():
    all_prompts: list(tuple) = [("prompt1.0", "Prompts/Prompt 1.0.txt"),
                                ("prompt1.1", "Prompts/Prompt 1.1.txt"),
                                ("prompt1.2", "Prompts/Prompt 1.2.txt"),
                                ("prompt1.3", "Prompts/Prompt 1.3.txt"),
                                ("prompt1.4", "Prompts/Prompt 1.4.txt"),
                                ("prompt1.5.2", "Prompts/Prompt 1.5.2.txt")]
    for idx in range(len(all_prompts)-1):
        prompt_nameA, path_promptA = all_prompts[idx]
        prompt_nameB, path_promptB = all_prompts[idx+1]
        compare_prompts(prompt_nameA, path_promptA, prompt_nameB, path_promptB)
        print(f"\n\n\n{50*'*'}\n\n\n")



    
if __name__ == "__main__":
    compare_all_prompts()