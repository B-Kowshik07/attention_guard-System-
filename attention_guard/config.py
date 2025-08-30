from dataclasses import dataclass

@dataclass
class Thresholds:
    # Eye Aspect Ratio thresholds
    EAR_DROWSY: float = 0.21       # below -> drowsy
    EAR_BLINK: float = 0.20        # momentary blink threshold
    DROWSY_CONSEC_FRAMES: int = 15 # ~0.5s if 30 FPS (tune per device)

@dataclass
class GazeParams:
    CENTER_TOLERANCE_X: float = 0.20  # fraction of eye width
    CENTER_TOLERANCE_Y: float = 0.25  # fraction of eye height
    DISTRACTION_GRACE_SECS: float = 1.0  # seconds before "Distracted" alert

@dataclass
class AppConfig:
    camera_index: int = 0
    draw_mesh: bool = False
    play_audio: bool = True
    log_interval_secs: float = 1.0
    window_title: str = "Attention Guard - Focus & Drowsiness Monitor"

THRESH = Thresholds()
GAZE = GazeParams()
APP = AppConfig()
