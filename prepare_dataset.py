import pandas as pd
import numpy as np
import yaml
import json

paths = [
    'assets/design_params/ao_dai_nu.yaml',
    'assets/design_params/ao_dai/tay lo.yaml',
    'assets/design_params/ao_dai/khong tay.yaml',
    'assets/design_params/ao_dai/tay phong.yaml',
]


def convert_yaml_to_pair_output(path) -> tuple[dict, list]:
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    float_list = []
    
    def recursive_loop(content: dict):
        if not isinstance(content, dict):
            return content
        
        if content.pop('range', None):
            type = content.pop('type')
            value = content.pop('v')
            if not type.startswith('select') and type != 'bool':
                float_list.append(value)
                return '[SEG]'
                
            return value
        
        for key, _ in content.items():
            content[key] = recursive_loop(content[key])
        return content
    
    data = recursive_loop(data)
    # rename the key
    data['wholebody_garment'] = data.pop('design')
    
    return data, float_list


if __name__ == '__main__':
    # df = pd.DataFrame(columns=['image_path', 'conversation', 'all_floats'])
    # for path in paths:
    #     data, float_list = convert_yaml_to_pair_output(path)
    #     # use json to print the data
    #     df.loc[len(df)] = [path, json.dumps(data), float_list]
    # df.to_csv('dataset.csv', index=False)
    data_path = 'data/aodai_Apose'
    import os 
    data_dir = os.listdir(data_path)
    for i, file in enumerate(data_dir):
        # rename to aodai_Apose_00000.png
        os.rename(os.path.join(data_path, file), os.path.join(data_path, f'aodai_{i:05d}.png'))
    