from typing import Tuple
import numpy as np

# MediaPipe mesh indices commonly used for EAR (Eye Aspect Ratio)
# Using 6 points per eye (approx): p1-horizontal outer, p4-horizontal inner, p2/p6 upper/lower, p3/p5 upper/lower
LEFT = [33, 160, 158, 133, 153, 144]   # (p1, p2, p3, p4, p5, p6)
RIGHT = [362, 387, 385, 263, 380, 373] # (p1, p2, p3, p4, p5, p6)

def _ear_for_indices(landmarks: np.ndarray, idxs) -> float:
    pts = landmarks[idxs][:, :2]
    p1, p2, p3, p4, p5, p6 = pts
    # EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    vert1 = np.linalg.norm(p2 - p6)
    vert2 = np.linalg.norm(p3 - p5)
    horiz = np.linalg.norm(p1 - p4) + 1e-6
    return float((vert1 + vert2) / (2.0 * horiz))

def eye_aspect_ratio(landmarks: np.ndarray) -> Tuple[float, float, float]:
    left_ear = _ear_for_indices(landmarks, LEFT)
    right_ear = _ear_for_indices(landmarks, RIGHT)
    mean_ear = (left_ear + right_ear) / 2.0
    return mean_ear, left_ear, right_ear
