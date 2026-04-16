import pydobot
import time

def move_to_home(device):
    print("Homing the robot...")
    # You have to specific the home position.
    device.move_to(x = 240, y = 0 , z = 150 , r= 45)  # Move to position (x=250, y=0, z=50) with r=0

def move_to_specific_position(device,x,y,z,r = 0.0, delay = 1):
    device.move_to(x = x, y = y , z = z , r= 45) 
    time.sleep(delay)
    
def get_current_pose(device):
    time.sleep(1)
    print("current pose")
    x, y, z, r, j1, j2, j3, j4 = device.pose()  # Get the current position and joint angles
    print(f"pose: {(x, y, z, r)}")
    return (x, y, z, r)