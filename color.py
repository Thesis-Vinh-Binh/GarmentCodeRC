import os
import json
from PIL import Image

data_path = './dataset'

files = [
    # 'close_image_scan',
    's_sketch',
    'example_data'
]

for data in files:
    content = json.load(open(os.path.join(data_path, f'{data}_color.json')))
    for key in content.keys():
        image = Image.open(os.path.join(data_path, data, key))
        image = image.resize((224, 224))
        image.show()
        print(f"Please input upper: ")
        upper = input()
        print(f"Please input lower: ")
        lower = input()
        print(f"Please input skin: ")
        skin = input()
        content[key] = [upper, lower, skin]
        break
    
    with open(os.path.join(data_path, f'{data}_color.json'), 'w') as f:
        json.dump(content, f, indent=4)

# for data in files:
#     color = {}
#     path = os.path.join(data_path, data)
#     for file in os.listdir(path):
#         if file.endswith('.png'):
#             color[file] = []
            
#     with open(os.path.join(data_path, f'{data}_color.json'), 'w') as f:
#         json.dump(color, f, indent=4)