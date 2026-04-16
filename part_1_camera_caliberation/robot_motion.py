import math
import select
import sys
import termios
import time
import tty

import numpy as np
import pydobot


PORT = "/dev/ttyACM0"
POLL_INTERVAL_S = 0.2


def move_to_home(device):
    print("Homing the robot...")
    # Safe home pose used in your other scripts
    device.move_to(x=240, y=0, z=150, r=45)


def get_current_pose(device):
    """Return (x, y, z, r) or None if pose read fails."""
    try:
        x, y, z, r, j1, j2, j3, j4 = device.pose()
    except Exception as e:
        print(f"Warning: failed to read pose: {e}")
        return None

    for v in (x, y, z, r):
        if not isinstance(v, (int, float)) or not math.isfinite(v):
            print(f"Warning: received non-finite pose value: {(x, y, z, r)}")
            return None
        if abs(v) > 1e7:
            print(f"Warning: received out-of-range pose value: {(x, y, z, r)}")
            return None

    return (float(x), float(y), float(z), float(r))


def print_copy_block_for_affine(saved_positions):
    """Print copy/paste-ready rob_xy block for Affine_transform.py."""
    rob_xy = np.array([[p[0], p[1]] for p in saved_positions], dtype=np.float64)
    print("\n--- Copy into Affine_transform.py ---")
    print("rob_xy = np.array([")
    for x, y in rob_xy.tolist():
        print(f"    [{x}, {y}],")
    print("], dtype=np.float64)")
    print("--- End copy ---\n")


def main():
    device = pydobot.Dobot(port=PORT)

    saved_positions = []
    old_term_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())

        move_to_home(device)
        print("\nPress 'a' to save/print the current pose. Ctrl-C to finish.\n")

        while True:
            pose = get_current_pose(device)
            if pose is None:
                time.sleep(POLL_INTERVAL_S)
                continue

            dr, _, _ = select.select([sys.stdin], [], [], 0)
            if dr:
                ch = sys.stdin.read(1)
                if ch == "a":
                    x, y, z, r = pose
                    print(f"pose: {(x, y, z, r)}")
                    saved_positions.append([x, y, z, r])
                    print(f"Saved position: {[x, y, z, r]}")

            time.sleep(POLL_INTERVAL_S)

    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_term_settings)
        except Exception:
            pass

        print("\nCollected positions:")
        for i, p in enumerate(saved_positions):
            print(f"{i}: {p}")

        if saved_positions:
            print_copy_block_for_affine(saved_positions)

        try:
            move_to_home(device)
        except Exception:
            pass
        device.close()


if __name__ == "__main__":
    main()
