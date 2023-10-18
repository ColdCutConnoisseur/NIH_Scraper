"""This script is a one-off for combining multiple output csvs into one sigular file"""

import sys
import csv
import json



def combine_files_and_show_duplicates(files_list, out_path, aggregate_list=[], out_path_final=None):
    """aggregate_list --> If run already, provide list of names to aggregate data for"""
    duplicate_dict = {} # Find names appearing multiple times across differing files

    aggregated_data_dict = {}

    header_row = None

    all_combined_rows = []

    PL_INDEX = 3

    for file_path in files_list:

        with open(file_path, 'r') as csv_in:
            csv_reader = csv.reader(csv_in)

            for ct, row in enumerate(csv_reader):

                # Set header
                if ct == 0:
                    header_row = row

                else:
                    if row == header_row:
                        print("Duplicate 'header' row found.  Skipping...")

                    else:
                        # Increment Counter Dict for Project Leader
                        name = row[PL_INDEX]

                        if name in duplicate_dict.keys():
                            duplicate_dict[name] += 1

                            if len(aggregate_list) > 0:
                                if name in aggregate_list:

                                    # Check Agg Dict
                                    if name in aggregated_data_dict.keys():

                                        # Check if differing project name otherwise skip
                                        print(aggregated_data_dict[name]['data_dict'])

                                        existing_project_titles = []

                                        # Run Aggregating Stuff
                                        additional_grant_sums = int(row[11])
                                        additional_grant_totals = float(row[12])
                                        additional_p_types = row[13].split(',')
                                        additional_data_dict = json.loads(row[14])

                                        for key, project_data in aggregated_data_dict[name]['data_dict'].items():
                                            new_proj_title = project_data['Project_title']
                                            existing_project_titles.append(new_proj_title)

                                        new_projects_being_added = additional_data_dict
                                        print(f"new_projs: {additional_data_dict}")

                                        # Iterate through new dict
                                        existing_proj_dict_keys = list(aggregated_data_dict[name]['data_dict'].keys())
                                        existing_proj_dict_len = len(existing_proj_dict_keys)

                                        new_dict_project_keys = list(additional_data_dict.keys())

                                        for ct, k in enumerate(new_dict_project_keys):
                                            new_proj_title = additional_data_dict[k]['Project_title']

                                            if new_proj_title in existing_project_titles:
                                                print("Project already in existing dict!")
                                                continue

                                            else:
                                                print("New Project!")

                                                # Update grant_sums
                                                print(f"Original grant sums: {aggregated_data_dict[name]['grant_sums']}")
                                                #print(f"Added: {additional_grant_sums}")
                                                aggregated_data_dict[name]['grant_sums'] += 1
                                                print(f"New Grant Sums: {aggregated_data_dict[name]['grant_sums']}")

                                                # Update grant_totals
                                                print(f"Original Grant Totals: {aggregated_data_dict[name]['grant_totals']}")
                                                #print(f"Added: {additional_grant_totals}")
                                                grant_amount_this_project = additional_data_dict[k]['FY_total_cost']
                                                raw_grant_amount = grant_amount_this_project.replace('$', '')
                                                raw_grant_amount = raw_grant_amount.replace(',', '')
                                                as_float = float(raw_grant_amount)
                                                aggregated_data_dict[name]['grant_totals'] += as_float
                                                print(f"New Grant Totals: {aggregated_data_dict[name]['grant_totals']}")

                                                # Update ptypes
                                                print(f"Original PTypes: {aggregated_data_dict[name]['ptypes']}")
                                                new_code = additional_p_types[ct]
                                                print(f"Added: {new_code}")

                                                aggregated_data_dict[name]['ptypes'].append(new_code)

                                                # Make list of set to remove dupes
                                                as_list_set = list(set(aggregated_data_dict[name]['ptypes']))
                                                aggregated_data_dict[name]['ptypes'] = as_list_set
                                                print(f"New PTypes: {aggregated_data_dict[name]['ptypes']}")

                                                # Update Projects Data Dict
                                                print(f"Original Data Dict: {aggregated_data_dict[name]['data_dict']}")
                                                new_key = str(existing_proj_dict_len + ct + 1)
                                                print(new_key)
                                                aggregated_data_dict[name]['data_dict'][new_key] = additional_data_dict[k]
                                                print(f"New Data Dict: {aggregated_data_dict[name]['data_dict']}")

                                    else:
                                        try:
                                            new_data_dict = {'row_constants' : row[0:11],
                                                                        'grant_sums' : int(row[11]),
                                                                        'grant_totals' : float(row[12]),
                                                                        'ptypes': row[13].split(','),
                                                                        'data_dict' : json.loads(row[14])}
                                            
                                            aggregated_data_dict[name] = new_data_dict

                                        except ValueError:
                                            print(row)
                                            sys.exit(0)


                            else:
                                all_combined_rows.append(row)

                        else:
                            duplicate_dict[name] = 1
                            all_combined_rows.append(row)

    # Write to final CSV
    with open(out_path_final, 'w') as final_out:
        csv_writer = csv.writer(final_out)
        csv_writer.writerow(header_row)
        csv_writer.writerows(all_combined_rows)

        # Then build and write combined rows
        if len(aggregated_data_dict.keys()) > 0:
            for k, v in aggregated_data_dict.items():
                new_row = v['row_constants']
                new_row.append(v['grant_sums'])
                new_row.append(v['grant_totals'])
                new_row.append(", ".join(v['ptypes']))
                new_row.append(v['data_dict'])

                # Write new row
                csv_writer.writerow(new_row)

                # FOR REFERENCE
                #{'row_constants' : row[0:11],
                #                                                        'grant_sums' : int(row[11]),
                #                                                        'grant_totals' : float(row[12]),
                #                                                        'ptypes': row[13].split(','),
                #                                                        'data_dict' : json.loads(row[14])}


    print("Combined CSV written!")

    print("\n")

    print("Here are the dupes: \n")

    agg_list_for_next_run = []

    for key, value in duplicate_dict.items():
        if value > 1:
            print(f"{key} : {value}")
            agg_list_for_next_run.append(key)

    print(agg_list_for_next_run)

        




if __name__ == "__main__":
    import os

    BASE_PATH = os.path.abspath(".")
    FILE_PARENT_FOLDER = "/rural_project_remainder/"
    FULL_PATH = BASE_PATH + FILE_PARENT_FOLDER

    FILES_LIST = ["." + FILE_PARENT_FOLDER + file for file in os.listdir(FULL_PATH) if os.path.isfile(file) and "split.csv" in file]

    print(f"Found {len(FILES_LIST)} files!")

    OUT_PATH = "./acmed_10_12_23_combined.csv"


    OUT_PATH_F = "./acmed_10_12_23_combined_final.csv"
    prev_dupe_list = ['RHODES, SCOTT D', 'WATTS-TAFFE, SUSAN', 'ADAMS, ALEXANDRA K.', 'BRUCE, MARTHA L', 'MAHONEY, JANE E', 'BEARDEN, JAMES D', 'BUCHWALD, DEDRA S', 'PEDERSEN, MAJA', 'KARLINER, LEAH S', 'HOWARTH, MARILYN', 'JAYADEV, SUMAN', 'MCEVOY, LINDA KATHLEEN', 'ELK, RONIT', 'JARAMILLO, ELISE TROTT', 'JAMES, KATHERINE A', 'LIN, SHAO', 'ROBERSON, ERIK D', 'GOINS, R. TURNER', 'WARRY, WAYNE RICHARD', 'HOLSTEIN, SARAH A', 'DENNY, ANDREA', 'COOK, ROBERT L', 'JANEVIC, MARY ROSE', 'LU, QUAN', 'ROBERTS, SCOTT', 'TANG, FENGYAN', 'LEWIS, JORDAN PAUL', 'GLUCK, MARK A']



    combine_files_and_show_duplicates(FILES_LIST, OUT_PATH, aggregate_list=prev_dupe_list, out_path_final=OUT_PATH_F)