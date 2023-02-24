import json


if __name__ == "__main__":
    DICTS_TO_COMBINE = []
    COMBINED_OUT = "final_supplemental_dict.json"
    
    combined_dict = {}

    for dict_path in DICTS_TO_COMBINE:
        loaded_dict = {}

        with open(dict_path, 'r') as json_in:
            loaded_dict = json.load(json_in)

        combined_dict |= loaded_dict  # Fancy python3.10+ syntax

    with open(, 'w') as json_out:
        json.dump(combined_dict, json_out)
