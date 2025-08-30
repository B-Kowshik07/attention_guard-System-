import cv2
import numpy as np
import time
from dataclasses import dataclass
import mediapipe as mp

from config import THRESH, GAZE, APP
from gaze import relative_gaze, eight_way_bucket
from drowsiness import eye_aspect_ratio
from alerts import AlertManager
from logger import SessionLogger
from utils import FPSCounter, clamp

@dataclass
class State:
    attentive: bool = True
    distracted: bool = False
    drowsy: bool = False
    last_distract_time: float = 0.0
    consecutive_drowsy_frames: int = 0
    muted: bool = False

def draw_status(frame, msg: str, color):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0,0), (w,40), color, -1)
    cv2.putText(frame, msg, (10,28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, cv2.LINE_AA)
    # border
    cv2.rectangle(frame, (0,0), (w,h), color, 6)

def main():
    cap = cv2.VideoCapture(APP.camera_index)
    if not cap.isOpened():
        raise SystemExit("Cannot open camera. Change camera_index in config.py")
    
    face_mesh = mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,   # enables iris landmarks
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    alert = AlertManager(play_audio=APP.play_audio)
    logger = SessionLogger(base_dir='.', interval_secs=APP.log_interval_secs)
    logger.start()
    fps = FPSCounter()
    st = State()
    
    # optional alarm path
    alarm_path = 'sounds/alarm.wav'

    win = APP.window_title
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)  # selfie view
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = face_mesh.process(rgb)

        status_msg = "Initializing..."
        color = (128,128,128)

        if res.multi_face_landmarks:
            mesh = res.multi_face_landmarks[0]
            landmarks = np.array([[lm.x, lm.y, lm.z] for lm in mesh.landmark], dtype=np.float32)
            h, w = frame.shape[:2]
            landmarks[:,0] *= w
            landmarks[:,1] *= h

            # EAR for drowsiness
            ear, l_ear, r_ear = eye_aspect_ratio(landmarks)

            # Gaze direction
            g = relative_gaze(landmarks)
            bucket = eight_way_bucket(g['x'], g['y'], GAZE.CENTER_TOLERANCE_X, GAZE.CENTER_TOLERANCE_Y)

            # Decide states
            now = time.time()
            is_blink = ear < THRESH.EAR_BLINK
            is_drowsy_frame = ear < THRESH.EAR_DROWSY

            if is_drowsy_frame:
                st.consecutive_drowsy_frames += 1
            else:
                st.consecutive_drowsy_frames = 0

            st.drowsy = st.consecutive_drowsy_frames >= THRESH.DROWSY_CONSEC_FRAMES
            st.distracted = (bucket != 'CENTER')

            # Apply grace period for distraction
            if st.distracted:
                if st.last_distract_time == 0.0:
                    st.last_distract_time = now
            else:
                st.last_distract_time = 0.0

            distracted_effective = st.distracted and (st.last_distract_time != 0.0) and ((now - st.last_distract_time) >= GAZE.DISTRACTION_GRACE_SECS)

            st.attentive = not st.drowsy and not distracted_effective

            # choose UI + logging state
            if st.drowsy:
                status_msg = f"DROWSY | EAR={ear:.2f} | {bucket}"
                color = (0, 0, 255)
                alert.play(alarm_path)
                logger.set_state('drowsy')
            elif distracted_effective:
                status_msg = f"DISTRACTED | {bucket}"
                color = (0, 215, 255)
                logger.set_state('distracted')
            else:
                status_msg = f"ATTENTIVE | EAR={ear:.2f} | {bucket}"
                color = (0, 200, 0)
                logger.set_state('attentive')

            # Draw debug overlays
            if APP.draw_mesh:
                for pt in landmarks.astype(int):
                    cv2.circle(frame, (int(pt[0]), int(pt[1])), 1, (255, 255, 255), -1)
            # Draw gaze arrow from eye center
            cx = int(w * 0.5)
            cy = int(h * 0.5)
            gx = int(cx + g['x'] * 100)
            gy = int(cy + g['y'] * 60)
            cv2.arrowedLine(frame, (cx, cy), (gx, gy), (255,255,255), 2, tipLength=0.2)
            cv2.putText(frame, bucket, (gx+10, gy), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)

        else:
            logger.set_state('distracted')
            status_msg = "No face detected"
            color = (0, 215, 255)

        # Status bar
        draw_status(frame, status_msg + (" | MUTE" if alert.is_muted() else ""), color)

        # FPS
        fps.tick()
        cv2.putText(frame, f"FPS: {fps.fps():.1f}", (10, frame.shape[0]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)

        cv2.imshow(win, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('m'):
            alert.set_muted(not alert.is_muted())
        if key == ord('d'):
            from config import APP as _APP
            _APP.draw_mesh = not _APP.draw_mesh

    cap.release()
    cv2.destroyAllWindows()
    report = logger.stop()
    print("Session report saved:", report)

if __name__ == "__main__":
    main()
