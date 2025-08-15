#!/usr/bin/env python3
"""
Merge simulated upper and lower garments and render the front view.

This script takes simulated garment OBJ files from the runs directory structure
and merges them into a single mesh, then renders the front view using the
existing rendering infrastructure.

Usage:
    python merge_garments_render.py --garment_path "runs/close_image_scan_cg_baseline/vis_new/valid_garment_10001_1923"
"""
import os
import argparse
import numpy as np
from pathlib import Path
import trimesh
import pyrender
from PIL import Image

eval_dict = {
    "close_image_scan": {
        "cg_baseline": [],
        "cg_cot": [],
        "cg_blip": [],
        "cg_retrieval": []
    },
    "s_sketch": {
        "cg_baseline": [],
        "cg_cot": [],
        "cg_blip": [],
    },
    "example_data": {
        "cg_retrieval": [],
        "cg_cot": [],
        "cg_blip": []
    }
}

def load_obj_mesh(obj_path):
    """Load OBJ mesh and return vertices and faces."""
    if not os.path.exists(obj_path):
        raise FileNotFoundError(f"OBJ file not found: {obj_path}")
    
    mesh = trimesh.load_mesh(str(obj_path))
    return mesh.vertices, mesh.faces


def load_body_mesh(body_path = "assets/bodies/mean_all.obj"):
    """Load the body mesh (mean_all.obj)."""
    if not os.path.exists(body_path):
        raise FileNotFoundError(f"Body mesh not found: {body_path}")
    
    body_mesh = trimesh.load_mesh(str(body_path))
    # Scale body vertices to meters
    body_mesh.vertices = body_mesh.vertices / 100
    
    return body_mesh


def create_pyrender_meshes(body_mesh, upper_mesh, lower_mesh = None):
    """Create pyrender mesh objects for rendering using the same approach as existing code."""
    # Create body material with skin color
    body_material = pyrender.MetallicRoughnessMaterial(
        baseColorFactor=(0.9, 0.6, 0.4, 1.0),  # Lighter gray for better visibility
        metallicFactor=0.3,  # Less metallic for better visibility
        roughnessFactor=0.7  # More rough for better visibility
    )
    
    # upper white
    upper_color = "5 10 2"
    upper_color = upper_color.split(' ')
    upper_color = [int(i) / 10 for i in upper_color]
    upper_material = pyrender.MetallicRoughnessMaterial(
        baseColorFactor=(upper_color[0], upper_color[1], upper_color[2], 1.0),  # Medium gray instead of light gray
        metallicFactor=0.0,
        roughnessFactor=0.8,
        doubleSided=True
    )
    
    if lower_mesh:
        lower_color = "6 0 1"
        lower_color = lower_color.split(' ')
        lower_color = [int(i) / 10 for i in lower_color]
        lower_material = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=(lower_color[0], lower_color[1], lower_color[2], 1.0),  # Medium gray instead of light gray
            metallicFactor=0.0,
            roughnessFactor=0.8,
            doubleSided=True
        )
    
    # Create pyrender meshes
    pyrender_body_mesh = pyrender.Mesh.from_trimesh(body_mesh, material=body_material)
    pyrender_upper_mesh = pyrender.Mesh.from_trimesh(upper_mesh, material=upper_material, smooth=True)
    pyrender_lower_mesh = None
    if lower_mesh:
        pyrender_lower_mesh = pyrender.Mesh.from_trimesh(lower_mesh, material=lower_material, smooth=True)
    
    
    # Check if meshes were created successfully
    if pyrender_body_mesh is None:
        print("WARNING: Pyrender body mesh creation failed!")
    if pyrender_upper_mesh is None:
        print("WARNING: Pyrender upper garment mesh creation failed!")
    if pyrender_lower_mesh is None:
        print("WARNING: Pyrender lower garment mesh creation failed!")
    
    return pyrender_body_mesh, pyrender_upper_mesh, pyrender_lower_mesh


def front_view_render(output_path, body_mesh, upper_pyrender_mesh, lower_pyrender_mesh = None):
    """
    Simple test render to debug the issue.
    """
    print("Creating simple test render...")
    
    # Create a simple scene with white background
    scene = pyrender.Scene(bg_color=(1., 1., 1., 1.))
    
    # Add meshes
    scene.add(upper_pyrender_mesh)
    if lower_pyrender_mesh:
        scene.add(lower_pyrender_mesh)
    scene.add(body_mesh)
    
    # Create a simple camera with better positioning
    camera = pyrender.PerspectiveCamera(yfov=np.pi/4)

    fov = 50  # Set your desired field of view in degrees 

    # # Calculate the bounding box center of the mesh
    bounding_box_center = body_mesh.bounds.mean(axis=0)

    # Calculate the diagonal length of the bounding box
    diagonal_length = np.linalg.norm(body_mesh.bounds[1] - body_mesh.bounds[0])

    # Calculate the distance of the camera from the object based on the diagonal length
    distance = 1.5 * diagonal_length / (2 * np.tan(np.radians(fov / 2)))

    camera_location = bounding_box_center
    camera_location[-1] += distance

    # Calculate the camera pose
    camera_pose = np.array([
        [1.0, 0.0, 0.0, camera_location[0]],
        [0.0, 1.0, 0.0, camera_location[1]],
        [0.0, 0.0, 1.0, camera_location[2] - 1],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    print(f"Test render camera position: {camera_pose[:3, 3]}")
    scene.add(camera, pose=camera_pose)
    
    # Add a simple light
    light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=2.0)
    light_pose = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1]
    ])
    scene.add(light, pose=light_pose)
    
    # Render
    renderer = pyrender.OffscreenRenderer(viewport_width=1080, viewport_height=1080)
    color, _ = renderer.render(scene, flags=pyrender.RenderFlags.RGBA)
    
    # Save
    image = Image.fromarray(color)
    image.save(output_path, "PNG")
    print(f"Simple test render saved to: {output_path}")

json_list = []

def main(args):
    
    # Validate paths
    garment_path = Path(args["garment_path"])
    if not garment_path.exists():
        print(f"Error: Garment path does not exist: {garment_path}")
        return
    
    # Create output directory
    output_dir = Path(args["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define paths for upper and lower garments
    upper_path = garment_path / "valid_garment_upper" / "valid_garment_upper" / "valid_garment_upper_sim.obj"
    lower_path = garment_path / "valid_garment_lower" / "valid_garment_lower" / "valid_garment_lower_sim.obj"
    wholebody_path = garment_path / "valid_wholebody" / "valid_wholebody" / "valid_wholebody_sim.obj"
    
    body_mesh = load_body_mesh()
    body_mesh.vertices = body_mesh.vertices * 100
    
    # Check if both garment files exist
    if wholebody_path.exists():
        wholebody_mesh = load_body_mesh(wholebody_path)
        
        print("Creating pyrender meshes...")
        rendered_body_mesh, rendered_upper_mesh, rendered_lower_mesh = create_pyrender_meshes(body_mesh, wholebody_mesh)
    
    elif upper_path.exists() and lower_path.exists():
        upper_mesh = load_body_mesh(upper_path)
        lower_mesh = load_body_mesh(lower_path)
        # Create pyrender meshes
        print("Creating pyrender meshes...")
        rendered_body_mesh, rendered_upper_mesh, rendered_lower_mesh = create_pyrender_meshes(body_mesh, upper_mesh, lower_mesh)
        # Render front view
        
    else: 
        return
        
    garment_name = garment_path.name
    output_path = output_dir / f"{garment_name}.png"
    
    print(f"Rendering front view...")
    front_view_render(
        output_path, 
        rendered_body_mesh, 
        rendered_upper_mesh, 
        rendered_lower_mesh
    )
    
    json_list.append(output_path)
    print("Success! Merged garment rendering completed.")
            
def get_all_sub_dirs(path):
    dir_list = os.listdir(path)
    sub_dirs = []
    # dir_names = []
    for file in dir_list:
        sub_path = os.path.join(path, file)
        if os.path.isdir(sub_path):
            sub_dirs.append(sub_path)
            # dir_names.append(file)
    return sub_dirs #, dir_names    

if __name__ == "__main__":
    for data, methods in eval_dict.items():
        for method, _ in methods.items():
            print(f"Processing {data}_{method}...")
            garment_path = f"runs/{data}_{method}/vis_new"
            garment_paths = get_all_sub_dirs(garment_path)
            args = {
                "output_dir": f"./simulation/{data}_{method}",
            }
            os.makedirs(args["output_dir"], exist_ok=True)
            for garment_path in garment_paths:
                args["garment_path"] = garment_path
                main(args)
    
    
