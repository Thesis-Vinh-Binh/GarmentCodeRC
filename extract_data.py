import os 
from os import path
import cv2


root = './runs/s_sketch'

postfix = [
    'cg_baseline',
    'cg_cot',
    'cg_blip',
    # 'cg_retrieval',
    # 'blip',
    # 'ref',
    # 'retrieval'
]

# root = './runs/d2g_close'
# postfix = [
#     'model',
#     'caption'
# ]

folders = [f'{root}_{p}/vis_new/' for p in postfix]
output_folder = f'./data/{path.basename(root)}'
os.makedirs(output_folder, exist_ok=True)

# assert not path.exists(folders[0])

file_names = [f for f in os.listdir(folders[0]) if path.isdir(path.join(folders[0], f))]
print(len(file_names), file_names[:10])

for file_name in file_names:
    # read image
    # initial_image = cv2.imread(path.join(folders[0], file_name, 'gt_image.png'))
    initial_image = cv2.imread(path.join(folders[0], file_name, 'gt_image.png'))
    for folder in folders:
        folder_path = path.join(folder, file_name)
        name = postfix[folders.index(folder)]
        if not os.path.exists(folder_path):
            print(f'{folder_path} does not exist')
            continue
        current_garments = [g for g in os.listdir(folder_path) if g.startswith('valid_garment')]
        garment_images = []
        for garment in current_garments:
            path_to_garment = path.join(folder_path, f'{garment}/{garment}/{garment}_render_front.png')
            if path.exists(path_to_garment):
                garment_image = cv2.imread(path_to_garment)
                garment_images.append(garment_image)
            else: 
                break
        
        if len(current_garments) == 0 or len(garment_images) == 0:
            print(f'no garment found for {file_name} in {folder}')
            continue
        
            
        if len(current_garments) > 1:
            # concat the images by placing them up and down
            if current_garments[0] == 'valid_garment_upper':
                garment_images[0] = cv2.vconcat([garment_images[0], garment_images[1]])
            else:
                garment_images[0] = cv2.vconcat([garment_images[1], garment_images[0]])
        
        cv2.putText(garment_images[0], name, (0, garment_images[0].shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        
        new_height = initial_image.shape[0]
        new_width = int(new_height * garment_images[0].shape[1] / garment_images[0].shape[0])
        garment_images[0] = cv2.resize(garment_images[0], (new_width, new_height))
        initial_image = cv2.hconcat([initial_image, garment_images[0]])
        
    path_to_save = path.join(output_folder, f'{file_name}.png')
    cv2.imwrite(path_to_save, initial_image)
    print(f'saved to {path_to_save}')
    
    
