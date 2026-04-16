import numpy as np
import cv2  
import time
import pydobot
import json
from pathlib import Path
from camera_utilities import apply_affine, fit_affine, apply_homography, fit_homography
from robot_utilities import move_to_home, move_to_specific_position, get_current_pose

M = np.array([
    [0.0184314522612, -0.451829120989, 365.497289163],
    [-0.455148448965, -0.00927368289792, 117.119113829],
], dtype=np.float64)

H = np.array([
    [-2.44594058e-02, -4.75669460e-01,  3.67247188e+02],
    [-4.34041615e-01,  5.08065338e-03,  1.20901686e+02],
    [-5.98330506e-05 ,-7.62411614e-05 , 1.00000000e+00]]
    , dtype=np.float64)

def move_robot_point(device,M,u,v):
    Xa, Ya = apply_affine(M, u, v) # Using Affine
    # Xa, Ya = apply_homography(H, u, v) # Using Homography
    print(f"Affine:  pixel({u:.3f}, {v:.3f}) -> robot({Xa:.6f}, {Ya:.6f})")
    move_to_specific_position(device, x=Xa, y=Ya, z=-35)

def main():
    # Optional: pull path points from unwarped_path_pixels JSON instead of hardcoding
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--path-json",
        default="part_2_maze_solution/solution_path_points_unwarped.json",
        help="JSON file containing unwarped_path_pixels to follow",
    )
    ap.add_argument(
        "--z",
        type=float,
        default=-35.0,
        help="Z height to use when moving to each point",
    )
    args = ap.parse_args()

    device = pydobot.Dobot(port="/dev/ttyACM0")
    device.speed(50, 50)
    move_to_home(device)
    time.sleep(2)

    # Load path points if provided
    path = Path(args.path_json)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            pixel_coords = data.get("unwarped_path_pixels", [])
        except Exception:
            pixel_coords = []
    else:
        pixel_coords = []

    if not pixel_coords:
        print("Warning: no unwarped_path_pixels found; using empty list.")

    for (u, v) in pixel_coords:
        move_robot_point(device, M, float(u), float(v))

    device.close() 
    
if __name__ == "__main__":
    main()
