#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "=== Calibration workflow (interactive) ==="
echo
echo "This script runs your calibration steps in order and PAUSES when you need to copy/paste values."
echo

echo "[0/6] Home robot (non-interactive)"
python - <<'PY'
import time
import pydobot

PORT = "/dev/ttyACM0"

device = pydobot.Dobot(port=PORT)
try:
    print("Homing robot...")
    device.move_to(x=240, y=0, z=150, r=0)
    time.sleep(2)
finally:
    device.close()
PY

echo "[1/6] Open camera preview"
echo " - Script: part_1_camera_caliberation/open_camera.py"
echo " - Tip: if the wrong camera opens, edit cam_index inside that file."
python part_1_camera_caliberation/open_camera.py

echo
echo "[2/6] Click pixel coordinates"
echo " - Script: part_1_camera_caliberation/get_pixel_cordinates.py"
echo " - Left click points (aim for ~10), press 'q' to finish."
python part_1_camera_caliberation/get_pixel_cordinates.py

echo
echo "[PAUSE] Copy pixel coordinates into robot_motion"
echo " - Open: part_1_camera_caliberation/robot_motion.py"
echo " - Paste the printed img_pts / pixel list where your script expects it."
read -r -p "Press Enter when done editing robot_motion.py..."

echo
echo "[3/6] Run robot_motion to collect robot poses for those pixel points"
echo " - Script: part_1_camera_caliberation/robot_motion.py"
python part_1_camera_caliberation/robot_motion.py

echo
echo "[PAUSE] Copy pixel coords + robot poses into Affine_transform"
echo " - Open: part_1_camera_caliberation/Affine_transform.py"
echo " - Paste:"
echo "   - img_pts = np.array([...])"
echo "   - rob_xy  = np.array([...])"
read -r -p "Press Enter when done editing Affine_transform.py..."

echo
echo "[4/6] Compute calibration matrices"
echo " - Script: part_1_camera_caliberation/Affine_transform.py"
python part_1_camera_caliberation/Affine_transform.py

echo
echo "[PAUSE] Copy M matrix (and any needed coords) into Maze_Motion"
echo " - Open: part_1_camera_caliberation/Maze_Motion.py"
echo " - Paste the printed M = np.array([...]) into the M block."
echo " - Also paste/update the pixel coordinate path list if Maze_Motion uses it."
read -r -p "Press Enter when done editing Maze_Motion.py..."

echo
echo "[5/6] Run Maze_Motion (robot executes path)"
echo " - Script: part_1_camera_caliberation/Maze_Motion.py"
python part_1_camera_caliberation/Maze_Motion.py

echo
echo "Done."

