from typing import Tuple, Dict
import numpy as np

# MediaPipe FaceMesh landmark indices for eyes (with iris when refined_landmarks=True)
# Eye bounds (outer corners): Left 33-133, Right 362-263 (corners 33/133 and 362/263)
LEFT_EYE_CORNERS = (33, 133)
RIGHT_EYE_CORNERS = (362, 263)

# Eyelids for vertical reference (midpoints approximations)
LEFT_UPPER_LID = 159
LEFT_LOWER_LID = 145
RIGHT_UPPER_LID = 386
RIGHT_LOWER_LID = 374

# Iris landmarks
LEFT_IRIS = [468, 469, 470, 471]
RIGHT_IRIS = [473, 474, 475, 476]

def eye_box_and_center(landmarks: np.ndarray, left: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    if left:
        c1, c2 = LEFT_EYE_CORNERS
        upper, lower = LEFT_UPPER_LID, LEFT_LOWER_LID
        iris_ids = LEFT_IRIS
    else:
        c1, c2 = RIGHT_EYE_CORNERS
        upper, lower = RIGHT_UPPER_LID, RIGHT_LOWER_LID
        iris_ids = RIGHT_IRIS

    p1 = landmarks[c1][:2]
    p2 = landmarks[c2][:2]
    top = landmarks[upper][:2]
    bottom = landmarks[lower][:2]
    eye_center = (top + bottom) / 2.0
    eye_width = np.linalg.norm(p2 - p1)
    eye_height = np.linalg.norm(top - bottom)

    iris_pts = landmarks[iris_ids][:, :2]
    iris_center = iris_pts.mean(axis=0)

    # Build an axis-aligned eye box from the four references
    left_x, right_x = (p1[0], p2[0]) if p1[0] < p2[0] else (p2[0], p1[0])
    top_y, bot_y = (top[1], bottom[1]) if top[1] < bottom[1] else (bottom[1], top[1])
    eye_box = np.array([[left_x, top_y], [right_x, bot_y]], dtype=float)  # [[x_min,y_min],[x_max,y_max]]
    return eye_box, iris_center, eye_center

def relative_gaze(landmarks: np.ndarray) -> Dict[str, float]:
    """Return normalized iris offsets for left & right eyes in [-1,1] range.
    0 means centered; negative x is left, negative y is up (image coords: y down).
    """
    out = {}
    for name, is_left in [("left", True), ("right", False)]:
        box, iris_c, _ = eye_box_and_center(landmarks, left=is_left)
        (x0, y0), (x1, y1) = box
        w = x1 - x0 + 1e-6
        h = y1 - y0 + 1e-6
        # Normalize iris center inside eye box to [-1,1]
        nx = ((iris_c[0] - x0) / w) * 2 - 1
        ny = ((iris_c[1] - y0) / h) * 2 - 1
        # Map to conventional screen coords: up negative
        out[f"{name}_nx"] = float(nx)
        out[f"{name}_ny"] = float(ny)
    # Average both eyes for stability
    out["x"] = float((out["left_nx"] + out["right_nx"]) / 2.0)
    out["y"] = float((out["left_ny"] + out["right_ny"]) / 2.0)
    return out

def eight_way_bucket(x: float, y: float, tol_x: float, tol_y: float) -> str:
    # Center deadzone
    if abs(x) <= tol_x and abs(y) <= tol_y:
        return "CENTER"
    # Cardinal vs diagonals
    if abs(x) > tol_x and abs(y) > tol_y:
        if x < 0 and y < 0:
            return "UP_LEFT"
        if x > 0 and y < 0:
            return "UP_RIGHT"
        if x < 0 and y > 0:
            return "DOWN_LEFT"
        if x > 0 and y > 0:
            return "DOWN_RIGHT"
    # Cardinals
    if abs(x) > abs(y):
        return "LEFT" if x < 0 else "RIGHT"
    else:
        return "UP" if y < 0 else "DOWN"
