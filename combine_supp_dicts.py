import json


if __name__ == "__main__":
    DICTS_TO_COMBINE = ["candidate_supplemental_info1.json", "candidate_supplemental_info2.json", "candidate_supplemental_info3.json"]
    COMBINED_OUT = "final_supplemental_dict.json"
    
    combined_dict = {}

    for dict_path in DICTS_TO_COMBINE:
        loaded_dict = {}

        with open(dict_path, 'r') as json_in:
            loaded_dict = json.load(json_in)

        combined_dict |= loaded_dict  # Fancy python3.10+ syntax

    with open(COMBINED_OUT, 'w') as json_out:
        json.dump(combined_dict, json_out)
