
import csv
import json


import project_config as pc





INSPECT_FILE = pc.POST_SPLIT_FINAL_FILE_NAME

# Constant
PROJECT_DATA_INDEX = 14



project_count = 0
unique_candidates = 0

with open(INSPECT_FILE, 'r') as csv_in:
    csv_reader = csv.reader(csv_in)

    for ct, row in enumerate(csv_reader):
        if ct == 0:
            continue

        else:
            unique_candidates += 1

            project_json = json.loads(row[14])

            unique_projects = len(list(project_json.keys()))

            project_count += unique_projects


print(f"Unique candidate count: {unique_candidates}")
print(f"Project count: {project_count}")







