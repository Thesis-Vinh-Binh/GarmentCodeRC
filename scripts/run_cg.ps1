# Activate conda environment
conda activate garmentcode

# ------------------------------- TO RUN THIS SCRIPT --------------------------------------------

# powershell -ExecutionPolicy Bypass -File ./scripts/run_cg.ps1

# Unzip archives
# Expand-Archive -Force ./runs/close_image_scan_cg_blip.zip -DestinationPath ./runs/
###!!!!!! REMEMBER to fix the all_json_spec_files before moving forward
# find all
(Get-Content ./runs/close_image_scan_cg_blip/vis_new/all_json_spec_files.json) -replace '/try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final', '' | Set-Content ./runs/close_image_scan_cg_blip/vis_new/all_json_spec_files.json

python test_garment_sim_index.py -j ./runs/close_image_scan_cg_blip/vis_new/all_json_spec_files.json

# Zip simulation folders
Compress-Archive -Force -Path ./runs/close_image_scan_cg_blip -DestinationPath ./runs/close_image_scan_cg_blip_simulation.zip

# Cd to rclone
cd C:/Users/nguye/Downloads/rclone-v1.70.3-windows-amd64/rclone-v1.70.3-windows-amd64

# Upload to remote
rclone copy C:/Users/nguye/Documents/Thesis/ForkedRepo/GarmentCodeRC/runs/close_image_scan_cg_blip_simulation.zip remote:thesis-data-here/simulation/
