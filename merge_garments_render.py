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


def load_obj_mesh(obj_path):
    """Load OBJ mesh and return vertices and faces."""
    if not os.path.exists(obj_path):
        raise FileNotFoundError(f"OBJ file not found: {obj_path}")
    
    mesh = trimesh.load_mesh(str(obj_path))
    return mesh.vertices, mesh.faces


def merge_garment_meshes(upper_vertices, upper_faces, lower_vertices, lower_faces):
    """
    Merge upper and lower garment meshes.
    
    Args:
        upper_vertices: Upper garment vertices (N, 3)
        upper_faces: Upper garment faces (M, 3)
        lower_vertices: Lower garment vertices (P, 3)
        lower_faces: Lower garment faces (Q, 3)
    
    Returns:
        merged_vertices: Combined vertices
        merged_faces: Combined faces with adjusted indices
    """
    # Combine vertices
    merged_vertices = np.vstack([upper_vertices, lower_vertices])
    
    # Adjust face indices for lower garment (add offset)
    lower_faces_adjusted = lower_faces + len(upper_vertices)
    
    # Combine faces
    merged_faces = np.vstack([upper_faces, lower_faces_adjusted])
    
    return merged_vertices, merged_faces


def create_merged_mesh(upper_vertices, upper_faces, lower_vertices, lower_faces):
    """Create a trimesh object from merged vertices and faces."""
    merged_vertices, merged_faces = merge_garment_meshes(
        upper_vertices, upper_faces, lower_vertices, lower_faces
    )
    
    # Create trimesh object
    merged_mesh = trimesh.Trimesh(vertices=merged_vertices, faces=merged_faces)
    
    # Scale vertices to meters (divide by 100 as done in the original code)
    merged_mesh.vertices = merged_mesh.vertices / 100
    
    return merged_mesh


def load_body_mesh(body_path):
    """Load the body mesh (mean_all.obj)."""
    if not os.path.exists(body_path):
        raise FileNotFoundError(f"Body mesh not found: {body_path}")
    
    body_mesh = trimesh.load_mesh(str(body_path))
    # Scale body vertices to meters
    body_mesh.vertices = body_mesh.vertices / 100
    
    return body_mesh


def create_pyrender_meshes(merged_garment_mesh, body_mesh):
    """Create pyrender mesh objects for rendering using the same approach as existing code."""
    # Create body material with skin color
    body_material = pyrender.MetallicRoughnessMaterial(
        baseColorFactor=(0.9, 0.6, 0.4, 1.0),  # Lighter gray for better visibility
        metallicFactor=0.3,  # Less metallic for better visibility
        roughnessFactor=0.7  # More rough for better visibility
    )
    
    # Create garment material - similar to existing code but simplified
    garment_material = pyrender.MetallicRoughnessMaterial(
        baseColorFactor=(0.7, 0.7, 0.7, 1.0),  # Medium gray instead of light gray
        metallicFactor=0.0,
        roughnessFactor=0.8,
        doubleSided=True
    )
    
    # Debug: Print original mesh information
    print(f"Original body mesh vertices: {len(body_mesh.vertices)}")
    print(f"Original body mesh bounds: {body_mesh.bounds}")
    print(f"Original garment mesh vertices: {len(merged_garment_mesh.vertices)}")
    print(f"Original garment mesh bounds: {merged_garment_mesh.bounds}")
    
    # Create pyrender meshes
    pyrender_body_mesh = pyrender.Mesh.from_trimesh(body_mesh, material=body_material)
    pyrender_garment_mesh = pyrender.Mesh.from_trimesh(merged_garment_mesh, material=garment_material, smooth=True)
    
    # Debug: Print pyrender mesh information
    print(f"Pyrender body mesh created: {pyrender_body_mesh}")
    print(f"Pyrender garment mesh created: {pyrender_garment_mesh}")
    
    # Check if meshes were created successfully
    if pyrender_body_mesh is None:
        print("WARNING: Pyrender body mesh creation failed!")
    if pyrender_garment_mesh is None:
        print("WARNING: Pyrender garment mesh creation failed!")
    
    return pyrender_garment_mesh, pyrender_body_mesh


def create_test_cube():
    """Create a simple test cube mesh for debugging."""
    # Create a simple cube
    vertices = np.array([
        [-0.5, -0.5, -0.5],
        [0.5, -0.5, -0.5],
        [0.5, 0.5, -0.5],
        [-0.5, 0.5, -0.5],
        [-0.5, -0.5, 0.5],
        [0.5, -0.5, 0.5],
        [0.5, 0.5, 0.5],
        [-0.5, 0.5, 0.5]
    ])
    
    faces = np.array([
        [0, 1, 2], [2, 3, 0],  # front
        [1, 5, 6], [6, 2, 1],  # right
        [5, 4, 7], [7, 6, 5],  # back
        [4, 0, 3], [3, 7, 4],  # left
        [3, 2, 6], [6, 7, 3],  # top
        [4, 5, 1], [1, 0, 4]   # bottom
    ])
    
    cube_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    return cube_mesh


def front_view_render(garment_mesh, body_mesh, output_path, resolution=(1080, 1080)):
    """
    Simple test render to debug the issue.
    """
    print("Creating simple test render...")
    
    # Create a simple scene with white background
    scene = pyrender.Scene(bg_color=(1., 1., 1., 1.))
    
    # Add meshes
    scene.add(garment_mesh)
    scene.add(body_mesh)
    
    # Create a simple camera with better positioning
    camera = pyrender.PerspectiveCamera(yfov=np.pi/4)
    
    # Calculate camera position based on mesh bounds
    all_vertices = []
    if hasattr(garment_mesh, 'vertices'):
        all_vertices.extend(garment_mesh.vertices)
    if hasattr(body_mesh, 'vertices'):
        all_vertices.extend(body_mesh.vertices)
    
    # if all_vertices:
    #     all_vertices = np.array(all_vertices)
    #     center = np.mean(all_vertices, axis=0)
    #     max_distance = np.max(np.linalg.norm(all_vertices - center, axis=1))
    #     camera_distance = max_distance * 3.0  # Position camera at 3x the max distance
        
    #     camera_pose = np.array([
    #         [1, 0, 0, center[0]],
    #         [0, 1, 0, center[1]],
    #         [0, 0, 1, center[2] + camera_distance],  # Move camera back
    #         [0, 0, 0, 1]
    #     ])
    # else:
    #     # Move camera to forward, 
    #     camera_pose = np.array([
    #         [1, 0, 0, 0],
    #         [0, 1, 0, 0],
    #         [0, 0, 1, 5],  
    #         [0, 0, 0, 1]
    #     ])
    
    # Evaluate w.r.t. body

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
    renderer = pyrender.OffscreenRenderer(viewport_width=resolution[0], viewport_height=resolution[1])
    color, _ = renderer.render(scene, flags=pyrender.RenderFlags.RGBA)
    
    # Save
    image = Image.fromarray(color)
    image.save(output_path, "PNG")
    print(f"Simple test render saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Merge simulated garments and render front view")
    parser.add_argument("--garment_path", "-g", type=str, required=True,
                       help="Path to garment directory (e.g., runs/close_image_scan_cg_baseline/vis_new/valid_garment_10001_1923)")
    parser.add_argument("--output_dir", "-o", type=str, default="./merged_renders",
                       help="Output directory for merged renders")
    parser.add_argument("--resolution", "-r", type=int, nargs=2, default=[1080, 1080],
                       help="Render resolution (width height)")
    parser.add_argument("--body_mesh", "-b", type=str, default="assets/bodies/mean_all.obj",
                       help="Path to body mesh file")
    
    args = parser.parse_args()
    
    # Validate paths
    garment_path = Path(args.garment_path)
    if not garment_path.exists():
        print(f"Error: Garment path does not exist: {garment_path}")
        return
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define paths for upper and lower garments
    upper_path = garment_path / "valid_garment_upper" / "valid_garment_upper" / "valid_garment_upper_sim.obj"
    lower_path = garment_path / "valid_garment_lower" / "valid_garment_lower" / "valid_garment_lower_sim.obj"
    
    # Check if both garment files exist
    if not upper_path.exists():
        print(f"Error: Upper garment not found: {upper_path}")
        return
    
    if not lower_path.exists():
        print(f"Error: Lower garment not found: {lower_path}")
        return
    
    # Check if body mesh exists
    body_mesh_path = Path(args.body_mesh)
    if not body_mesh_path.exists():
        print(f"Error: Body mesh not found: {body_mesh_path}")
        return
    
    try:
        print(f"Loading upper garment: {upper_path}")
        upper_vertices, upper_faces = load_obj_mesh(upper_path)
        print(f"Upper garment: {len(upper_vertices)} vertices, {len(upper_faces)} faces")
        
        print(f"Loading lower garment: {lower_path}")
        lower_vertices, lower_faces = load_obj_mesh(lower_path)
        print(f"Lower garment: {len(lower_vertices)} vertices, {len(lower_faces)} faces")
        
        print(f"Loading body mesh: {body_mesh_path}")
        body_mesh = load_body_mesh(body_mesh_path)
        body_mesh.vertices = body_mesh.vertices * 100
        print(f"Body mesh: {len(body_mesh.vertices)} vertices, {len(body_mesh.faces)} faces")
        
        # Merge garments
        print("Merging garment meshes...")
        merged_garment_mesh = create_merged_mesh(upper_vertices, upper_faces, lower_vertices, lower_faces)
        print(f"Merged garment: {len(merged_garment_mesh.vertices)} vertices, {len(merged_garment_mesh.faces)} faces")
        
        # Create pyrender meshes
        print("Creating pyrender meshes...")
        pyrender_garment_mesh, pyrender_body_mesh = create_pyrender_meshes(merged_garment_mesh, body_mesh)
        
        # Check if meshes are valid
        if pyrender_garment_mesh is None or pyrender_body_mesh is None:
            print("ERROR: One or both meshes failed to create. Cannot render.")
            return
        
        # Render front view
        garment_name = garment_path.name
        output_path = output_dir / f"{garment_name}_merged_front.png"
        
        print(f"Rendering front view...")
        front_view_render(
            pyrender_garment_mesh, 
            pyrender_body_mesh, 
            output_path, 
            resolution=tuple(args.resolution)
        )
        
        # Save merged mesh as OBJ for inspection
        merged_obj_path = output_dir / f"{garment_name}_merged.obj"
        merged_garment_mesh.export(str(merged_obj_path))
        print(f"Merged mesh saved to: {merged_obj_path}")
        
        print("Success! Merged garment rendering completed.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return
    

if __name__ == "__main__":
    main()
