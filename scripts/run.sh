#!/bin/bash
conda activate garmentcode

# echo "Current conda env: $CONDA_DEFAULT_ENV"
# if [ "$CONDA_DEFAULT_ENV" != "C:/Users/nguye/.conda/envs/garmentcode" ]; then
#     echo "Current conda env is not garmentcode, please activate it"
#     exit 1
# fi

# remove if exist
rm -rf ./runs/d2g_close_caption/ ./runs/d2g_close/
unzip -o ./runs/d2g_close_caption.zip -d ./runs/
unzip -o ./runs/d2g_close.zip -d ./runs/

python export_json_total.py -i ./runs/d2g_close_caption/
python export_json_total.py -i ./runs/d2g_close/

python test_garment_sim_index.py -j ./runs/d2g_close_caption/all_json_spec_files.json
python test_garment_sim_index.py -j ./runs/d2g_close/all_json_spec_files.json

zip -r ./runs/d2g_close_caption_simulation.zip ./runs/d2g_close_caption/simulation/
zip -r ./runs/d2g_close_simulation.zip ./runs/d2g_close/simulation/

rclone copy ./runs/d2g_close_caption_simulation.zip remote:thesis-data-here/simulation/
rclone copy ./runs/d2g_close_simulation.zip remote:thesis-data-here/simulation/