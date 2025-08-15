import os

BIG_DIR = "C:/Users/nguye/Documents/Thesis/ForkedRepo/GarmentCodeRC/runs"
# FOLDER = "s_sketch_cg_baseline"
FOLDER = "close_image_scan_cg_blip"

directory = os.path.join(BIG_DIR, FOLDER, "vis_new")

folders = []

for folder in os.listdir(directory):
    path = os.path.join(directory, folder)
    if os.path.isdir(path):
        folders.append(path)

def validate_garment_generation(folder):
    for subfile in os.listdir(folder):
        path = os.path.join(folder, subfile)
        if os.path.isdir(path):
            if os.path.exists(os.path.join(path, subfile, f'{subfile}_sim.obj')):
                pass 
            else: 
                return False 
    return True 
failed_folders = []
for folder in folders:
    if validate_garment_generation(folder):
        pass        
    else:
        failed_folders.append(folder)
        print(f"Evaluation failed at: {folder}")

print(f'Total failed folders: {len(failed_folders)}')
