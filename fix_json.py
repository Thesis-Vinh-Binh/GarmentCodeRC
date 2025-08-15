import os
import json

path = './runs/'

filename = 'close_image_scan_cg_baseline'
# filename = 's_sketch_cg_baseline'
filepath = os.path.join(path, filename, 'vis_new')
json_path = os.path.join(filepath, 'all_json_spec_files.json')

with open(json_path, 'r') as f:
    data = json.load(f)

json_list = []

for file in os.listdir(filepath):
    file_path = os.path.join(filepath, file)
    if os.path.isdir(file_path):
        for sub_file in os.listdir(file_path):
            sub_file_path = os.path.join(file_path, sub_file)
            if os.path.isdir(sub_file_path):
                json_list.append(os.path.join(sub_file_path, f'{sub_file}_specification.json'))
                
if len(json_list) != len(data):
    print("Overwrite json list, old length: ", len(data), "new length: ", len(json_list))
    with open(json_path, 'w') as f:
        json.dump(json_list, f)
else:
    print("No need to overwrite json list")

print('Done')