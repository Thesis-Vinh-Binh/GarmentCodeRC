# Activate conda environment
conda activate garmentcode

# Optional: Check conda environment
# if ($env:CONDA_DEFAULT_ENV -ne "C:/Users/nguye/.conda/envs/garmentcode") {
#     Write-Host "Current conda env is not garmentcode, please activate it"
#     exit 1
# }

# Remove directories if they exist
Remove-Item -Recurse -Force ./runs/d2g_close_caption/, ./runs/d2g_close/ -ErrorAction SilentlyContinue

# Unzip archives
Expand-Archive -Force ./runs/d2g_close_caption.zip -DestinationPath ./runs/
Expand-Archive -Force ./runs/d2g_close.zip -DestinationPath ./runs/

# Run Python scripts
python export_json_total.py -i ./runs/d2g_close_caption/
python export_json_total.py -i ./runs/d2g_close/

python test_garment_sim_index.py -j ./runs/d2g_close_caption/all_json_spec_files.json
python test_garment_sim_index.py -j ./runs/d2g_close/all_json_spec_files.json

# Zip simulation folders
Compress-Archive -Force -Path ./runs/d2g_close_caption/simulation/* -DestinationPath ./runs/d2g_close_caption_simulation.zip
Compress-Archive -Force -Path ./runs/d2g_close/simulation/* -DestinationPath ./runs/d2g_close_simulation.zip

# 
cd C:/Users/nguye/Downloads/rclone-v1.70.3-windows-amd64/rclone-v1.70.3-windows-amd64

# Upload to remote
rclone copy ./runs/d2g_close_caption_simulation.zip remote:thesis-data-here/simulation/
rclone copy ./runs/d2g_close_simulation.zip remote:thesis-data-here/simulation/
