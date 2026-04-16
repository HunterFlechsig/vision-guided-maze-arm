#!/usr/bin/env bash
set -euo pipefail

CAM_INDEX="${CAM_INDEX:-0}"

usage() {
  cat <<'EOF'
Run Part 2 maze pipeline (01 -> 05) in succession.

Usage:
  ./run_part2_all.sh --cam-index 3

Options:
  --cam-index N   Camera index for 01_capture_image.py (default: 0, or env CAM_INDEX)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cam-index)
      CAM_INDEX="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "=== Running Part 2 pipeline ==="
echo "Camera index: $CAM_INDEX"

# Home robot first so it starts from a known pose.
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

python part_2_maze_solution/01_capture_image.py --cam-index "$CAM_INDEX"
python part_2_maze_solution/02_maze_warp_from_json.py
python part_2_maze_solution/03_maze_circles_and_grid.py
python part_2_maze_solution/04_solve_maze.py
python part_2_maze_solution/05_unwrap_and_overlay_path.py
echo "[Robot] Executing Maze_Motion with unwarped path..."
python part_1_camera_caliberation/Maze_Motion.py --path-json part_2_maze_solution/solution_path_points_unwarped.json

echo
echo "Done."

