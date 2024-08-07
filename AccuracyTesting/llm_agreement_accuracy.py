import csv

SKIP_LIST = ['catalogNumber', 'Dataset Source', 'accessURI', 'Label only?', 'modifiedBy', 'verifiedBy' , 'substrate', 'Image']
PATH_WRAPPER = "Output/%s.csv"


def get_contents(fname):
    with open(fname, 'r', encoding='utf-8', newline='') as csvfile:
        return list(csv.DictReader(csvfile)) 

def save_to_csv(csv_file_path, data):
    fields = list(data[0].keys())
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)                  

def image_agreement_dict(img_results1, img_results2):
    d = {}
    for res1, res2 in zip(img_results1.items(), img_results2.items()):
        if res1[0] not in SKIP_LIST and res1[1].lower().strip() == res2[1].lower().strip():
            d[res1[0]] = res1[1]
    return d

def tally(master_list, ground_truth_dicts, master_agree_dict):
    matches = 0
    num_targets = 0
    not_applicable_tally = 0
    na_matches = 0
    for results_dict, ground_truth_dict in zip(master_list, ground_truth_dicts):
        num_targets += len(results_dict)
        for key, val in results_dict.items():
            master_agree_dict[key][1] += 1
            if val.strip() == "N/A":
                not_applicable_tally += 1
            if ground_truth_dict[key].lower().strip() == val.lower().strip():
                master_agree_dict[key][0] += 1 
                matches +=1
                if val.strip() == "N/A":
                    na_matches += 1
    master_agree_dict["number targets"] = num_targets
    master_agree_dict["matches"] = matches
    master_agree_dict["accuracy: all values"] = matches/num_targets
    master_agree_dict["num N/A targets"] = not_applicable_tally
    master_agree_dict["N/A matches"] = na_matches
    master_agree_dict["accuracy: without N/As"] = (matches-na_matches) / (num_targets-not_applicable_tally)            
    return master_agree_dict            


def main(model1, model2, ground_truth_dicts, master_agree_dict):
    all_results1, all_results2 = get_contents(PATH_WRAPPER%model1), get_contents(PATH_WRAPPER%model2)
    master_list = [image_agreement_dict(img_results1, img_results2) for img_results1, img_results2 in zip(all_results1, all_results2)]
    master_agree_dict = tally(master_list, ground_truth_dicts, master_agree_dict)  
    return master_agree_dict
    
if __name__ == "__main__":
    gpt1, gpt2 = "Spread_6_11_1050", "Spread_6_11_1110"
    sonnet1, sonnet2 = "Spread_6_12_1404", "Spread_6_12_1440"
    ground_truth_dicts = get_contents("Output/First100BryophytesTyped.csv")
    master_results = []                    
    for gpt in [gpt1, gpt2]: 
        for sonnet in [sonnet1, sonnet2]:
            master_agree_dict = {"runs": f"{gpt}VS.{sonnet}"} | \
                        {fieldName: [0,0] for fieldName in ground_truth_dicts[0] if fieldName not in SKIP_LIST}
            master_results += [main(gpt, sonnet, ground_truth_dicts, master_agree_dict)]
    save_to_csv(PATH_WRAPPER%"First100BryophytesTypedGPT4oSonnet3.5", master_results)