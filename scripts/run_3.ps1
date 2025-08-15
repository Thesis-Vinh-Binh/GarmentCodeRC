param(
    [string]$run_name1 = "close_image_scan_cg_blip",
    [string]$run_name2 = "close_image_scan_cg_baseline"
)

# print out run name
Write-Host "Run name: $run_name1"
Write-Host "Run name: $run_name2"

# to call this use
# powershell -ExecutionPolicy Bypass -File ./scripts/run_3.ps1

# Activate conda environment
conda activate garmentcode

# Unzip archives (if needed manually before running)
# Expand-Archive -Force "./runs/$run_name1.zip" -DestinationPath ./runs/
# Expand-Archive -Force "./runs/$run_name2.zip" -DestinationPath ./runs/

# Fix all_json_spec_files.json by removing specific path
(Get-Content "./runs/$run_name1/vis_new/all_json_spec_files.json") -replace '/try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final', '' | Set-Content "./runs/$run_name1/vis_new/all_json_spec_files.json"
(Get-Content "./runs/$run_name2/vis_new/all_json_spec_files.json") -replace '/try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final', '' | Set-Content "./runs/$run_name2/vis_new/all_json_spec_files.json"

# Run simulation test
python test_garment_sim_index.py -j "./runs/$run_name1/vis_new/all_json_spec_files.json"
python test_garment_sim_index.py -j "./runs/$run_name2/vis_new/all_json_spec_files.json"

# Zip simulation folder
Compress-Archive -Force -Path "./runs/$run_name1" -DestinationPath "./runs/${run_name1}_simulation.zip"
Compress-Archive -Force -Path "./runs/$run_name2" -DestinationPath "./runs/${run_name2}_simulation.zip"

# Cd to rclone
cd C:/Users/nguye/Downloads/rclone-v1.70.3-windows-amd64/rclone-v1.70.3-windows-amd64

# Upload to remote
rclone copy "C:/Users/nguye/Documents/Thesis/ForkedRepo/GarmentCodeRC/runs/${run_name1}_simulation.zip" ntnbinh:Thesis/simulation
rclone copy "C:/Users/nguye/Documents/Thesis/ForkedRepo/GarmentCodeRC/runs/${run_name2}_simulation.zip" ntnbinh:Thesis/simulation
