import re

def save_to_txt(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def get_contents_from_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def get_fieldnames(d):
    return list(d.keys())

def get_field_instruction(d, fieldname):
    return d.get(fieldname, "Field not present in this prompt")

def pair_field_instructions(d1, d2, fieldname):
    i1 = f"{d1['prompt_name']}\n{fieldname}: {get_field_instruction(d1, fieldname)}\n" 
    i2 = f"{d2['prompt_name']}\n{fieldname}: {get_field_instruction(d2, fieldname)}\n" 
    return i1 + i2 + 75*"=" + "\n"

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
    pairings = ""
    for fieldname in all_fieldnames:
        pairings += pair_field_instructions(dict_A, dict_B, fieldname) if fieldname != "prompt_name" else ""
    return pairings    

def compare_all_prompts():
    all_prompts: list(tuple) = [("prompt1.0", "Prompts/Prompt 1.0.txt"),
                                ("prompt1.1", "Prompts/Prompt 1.1.txt"),
                                ("prompt1.2", "Prompts/Prompt 1.2.txt"),
                                ("prompt1.3", "Prompts/Prompt 1.3.txt"),
                                ("prompt1.4", "Prompts/Prompt 1.4.txt"),
                                ("prompt1.5.2", "Prompts/Prompt 1.5.2.txt")]
    all_comparisons = []                            
    for idx in range(len(all_prompts)-1):
        prompt_nameA, path_promptA = all_prompts[idx]
        prompt_nameB, path_promptB = all_prompts[idx+1]
        prompt_comparison = compare_prompts(prompt_nameA, path_promptA, prompt_nameB, path_promptB)
        all_comparisons += [f"{prompt_comparison}\n\n\n{75*'*'}\n\n\n"]
    output = "".join(all_comparisons)    
    print(output)
    return output    



    
if __name__ == "__main__":
    output_filepath = "Prompts/prompts1.0-1.5.2-field_comparisons.txt"
    all_comparsions = compare_all_prompts()
    save_to_txt(output_filepath, all_comparsions)