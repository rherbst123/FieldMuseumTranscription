import utility

def format_result(image_dict):
    return "\n".join([f"{key}: {val}" for key, val in image_dict.items()])
 
def find_image(image_ref, results):
    for res_dict in results:
        if "accessURI" in res_dict and res_dict["accessURI"] == image_ref or "Image" in res_dict and res_dict["Image"] == image_ref:
            return res_dict

def main(fname, image_ref):
    results = utility.get_contents_from_csv(fname)
    image_dict = find_image(image_ref, results)
    formatted = format_result(image_dict)
    print(formatted)

if __name__ == "__main__":
    fname = "AutomaticAnalysis/SourcesForPaper/First100BryophytesTyped.csv"
    image_ref1 = "C0341263F.jpg"
    image_ref2 = "https://fm-digital-assets.fieldmuseum.org/2307/750/C0341263F.jpg"
    main(fname, image_ref2)
    
    