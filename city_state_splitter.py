import csv
import project_config as pc

new_headers = []
new_data = []


with open(pc.PRE_SPLIT_FINAL_FILE_NAME, 'r') as in_file:

    csv_reader = csv.reader(in_file)

    for ct, line in enumerate(csv_reader):

        if ct == 0:
            new_headers = line[:]
            new_headers.remove('Organization - City & State')
            new_headers.insert(7, 'Organization - City')
            new_headers.insert(8, 'Organization - State')

        else:
            existing_line = line[:]
            city_state = existing_line[7]
            c_s_split = city_state.split(", ")
            city = c_s_split[0]
            state = c_s_split[1]
            existing_line[7] = city
            existing_line.insert(8, state)
            
            new_data.append(existing_line)


# Write
with open(pc.POST_SPLIT_FINAL_FILE_NAME, 'w') as out_file:
    csv_writer = csv.writer(out_file)
    csv_writer.writerow(new_headers)
    csv_writer.writerows(new_data)

        





