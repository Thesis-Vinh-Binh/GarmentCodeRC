import os
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--input_dir", '-i', type=str, required=True)
args = parser.parse_args()

if __name__ == "__main__":
    input_dir = args.input_dir
    json_list = []
    for file in os.listdir(input_dir):
        for sub_file in os.listdir(os.path.join(input_dir, file)):
            if sub_file.endswith(".json") and not sub_file.startswith("caption"):
                # rename by adding posfix _specification
                new_name = sub_file.replace(".json", "_specification.json")
                new_dir = os.path.join(input_dir, file, new_name)
                json_list.append(new_dir)
                os.rename(os.path.join(input_dir, file, sub_file), new_dir)
    with open(os.path.join(input_dir, "all_json_spec_files.json"), "w") as f:
        json.dump(json_list, f)
    