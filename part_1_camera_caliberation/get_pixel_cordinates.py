# filename: click_coords_camera.py
import cv2
import os

WINDOW_NAME = "Camera (click to get pixel coords)"

# global state for drawing
click_points = []  # list of (x, y) tuples

OUT_IMG = os.path.join(os.path.dirname(__file__), "calibration_pixels_overlay.png")


def print_points_for_affine(points):
    print("img_pts = np.array([")
    for x, y in points:
        print(f"    [{x}, {y}],")
    print("], dtype=np.float64)")


def draw_points_overlay(frame, points):
    """
    Draw points with index labels in click order, plus a connecting polyline.
    """
    out = frame.copy()
    if not points:
        return out

    # Draw connecting lines to show the order.
    for i in range(1, len(points)):
        cv2.line(out, points[i - 1], points[i], (0, 255, 255), 2, cv2.LINE_AA)

    for i, (x, y) in enumerate(points, start=1):
        # point marker
        cv2.circle(out, (x, y), 7, (0, 255, 0), thickness=-1)
        cv2.circle(out, (x, y), 10, (0, 0, 0), thickness=2)

        # label with outline for readability
        label = str(i)
        org = (x + 12, y - 12)
        cv2.putText(out, label, org, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(out, label, org, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    return out


def on_mouse(event, x, y, flags, param):
    global click_points
    if event == cv2.EVENT_LBUTTONDOWN:
        click_points.append((x, y))
        print(f"Clicked at: x={x}, y={y}")
    elif event == cv2.EVENT_RBUTTONDOWN:
        # right-click to clear points
        click_points = []
        print("Cleared points")

def main():
    cap = cv2.VideoCapture(1)  # change to 1/2 if you have multiple cameras
    if not cap.isOpened():
        raise RuntimeError("Could not open camera. Try a different index (1, 2) or check permissions.")

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    print("Instructions:")
    print(" • Left-click on the video to print/overlay pixel coordinates (x, y)")
    print(" • Right-click to clear overlays")
    print(" • Press 'q' to quit")

    last_frame = None
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read frame from camera.")
            break
        last_frame = frame.copy()

        # draw markers for all click points
        for (x, y) in click_points:
            cv2.circle(frame, (x, y), 5, (0, 255, 0), thickness=-1)   # filled dot
            cv2.putText(frame, f"({x}, {y})", (x + 8, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    print_points_for_affine(click_points)

    # Save an annotated overlay so you can see the order you clicked.
    if last_frame is not None and click_points:
        overlay = draw_points_overlay(last_frame, click_points)
        cv2.imwrite(OUT_IMG, overlay)
        print(f"Saved overlay image: {OUT_IMG}")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
