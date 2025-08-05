import os
import sys
import argparse
import json
from pathlib import Path
import shutil

# from llava.garment_utils_v2 import run_simultion_warp
from assets.garment_programs.meta_garment import MetaGarment
from assets.bodies.body_params import BodyParameters

from pygarment.meshgen.boxmeshgen import BoxMesh
from pygarment.meshgen.simulation import run_sim
import pygarment.data_config as data_config
from pygarment.meshgen.sim_config import PathCofig

def get_command_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_list", '-j', type=str, required=True, help="path to the save resules shapenet dataset")
    args = parser.parse_args()
    return args

def run_simultion_warp(pattern_spec, props, output_path):
    spec_path = Path(pattern_spec)
    garment_name, _, _ = spec_path.stem.rpartition('_')  # assuming ending in '_specification'

    paths = PathCofig(
        in_element_path=spec_path.parent,  
        out_path=output_path, 
        in_name=garment_name,
        body_name='mean_all',    # 'f_smpl_average_A40'
        smpl_body=False,   # NOTE: depends on chosen body model
        add_timestamp=False,
        system_path='./system.json'
    )

    garment_box_mesh = BoxMesh(paths.in_g_spec, props['sim']['config']['resolution_scale'])
    garment_box_mesh.load()
    garment_box_mesh.serialize(
        paths, store_panels=False, uv_config=props['render']['config']['uv_texture'])

    props.serialize(paths.element_sim_props)

    run_sim(
        garment_box_mesh.name, 
        props, 
        paths,
        save_v_norms=False,
        store_usd=False,  # NOTE: False for fast simulation!
        optimize_storage=False,   # props['sim']['config']['optimize_storage'],
        verbose=False
    )
    
    props.serialize(paths.element_sim_props)

if __name__ == "__main__":  
    args = get_command_args()

    props = data_config.Properties('assets/Sim_props/default_sim_props.yaml') 
    props.set_section_stats('sim', fails={}, sim_time={}, spf={}, fin_frame={}, body_collisions={}, self_collisions={})
    props.set_section_stats('render', render_time={})

    with open(args.json_list) as f:
        garment_json = json.load(f)

    print("total files: ", len(garment_json))
    processed_files = []
    # assert False

    for json_spec_file in garment_json:
        json_spec_file = json_spec_file.replace('validate_garment', 'valid_garment')
        saved_folder = os.path.dirname(json_spec_file) 
        # if os.path.exists(os.path.join(saved_folder, os.path.basename(saved_folder))):
        #     print(f'Skip ', json_spec_file)
        #     processed_files.append(json_spec_file)
        #     continue
        print(f'Handle ', json_spec_file)
        try:
            run_simultion_warp(
                    json_spec_file,
                    props,
                    saved_folder
                )
        except Exception as e:
            print('Error in running simulation for ', json_spec_file)
            continue
        processed_files.append(json_spec_file)
    
    from datetime import datetime
    os.makedirs('processed_files', exist_ok=True)
    with open(f'processed_files/processed_files_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
        json.dump(processed_files, f)