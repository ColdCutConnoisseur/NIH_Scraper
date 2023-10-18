import json


def create_sub_files_list(base_file_directory, project_title, start_index, end_index):
    out_files = []

    for i in range(start_index, end_index + 1):
        file_name = base_file_directory + project_title + \
                "_candidate_supplemental_info" + str(i) + ".json"
        out_files.append(file_name)

    return out_files


if __name__ == "__main__":
    import project_config

    SUPP_INFO_DIRECTORY = "./supp_info/"

    DICTS_TO_COMBINE = create_sub_files_list(SUPP_INFO_DIRECTORY, project_config.SCRAPE_TITLE, 1, 1)


    test_list = [
        SUPP_INFO_DIRECTORY + f"{project_config.SCRAPE_TITLE}_candidate_supplemental_info1.json"
    ]


    assert DICTS_TO_COMBINE == test_list, "Lists do not match!"
        

    COMBINED_OUT = project_config.FULL_SUPP_DICT_PATH
    
    combined_dict = {}

    for dict_path in DICTS_TO_COMBINE:
        loaded_dict = {}

        with open(dict_path, 'r') as json_in:
            loaded_dict = json.load(json_in)

        combined_dict |= loaded_dict  # Fancy python3.10+ syntax

    with open(COMBINED_OUT, 'w') as json_out:
        json.dump(combined_dict, json_out)

    print(combined_dict)
