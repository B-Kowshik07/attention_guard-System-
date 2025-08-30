<<<<<<< HEAD
# attention_guard-System
=======
# Stay Focused, Stay Safe — 2‑in‑1 Gaze Tracking & Drowsiness Detection

A unified attention‑monitoring assistant that combines **8‑way gaze tracking** with **blink/drowsiness detection** (EAR) in real‑time. It raises visual/audio alerts and **logs attention time** to generate per‑session focus reports.

https://github.com —> Create a repo and drop these files there to share easily.

## Features
- **8‑way gaze**: CENTER, LEFT/RIGHT/UP/DOWN + diagonals
- **Blink & drowsiness** via Eye Aspect Ratio (EAR)
- **Attention states**: _Attentive_ (green), _Distracted_ (amber), _Drowsy_ (red)
- **Audio alert** (pygame) + mute toggle (`m`)
- **Time logging** every second → CSV **session report** on exit
- **Threaded logger** to avoid blocking
- **Modular**: `gaze.py`, `drowsiness.py`, `alerts.py`, `logger.py`

## Quick Start
```bash
# 1) Create venv (recommended)
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run
python main.py
```

> If the camera doesn’t open, change `camera_index` in `config.py` to 1 or 2.

## Controls
- `q` → quit and write the session report
- `m` → mute/unmute audio
- `d` → toggle face mesh landmark drawing (debug)

## Outputs
- `logs/session_YYYYMMDD_HHMMSS.csv` — raw per‑second state log
- `reports/report_YYYYMMDD_HHMMSS.csv` — summary of attentive/distracted/drowsy time

## Tuning
Edit `config.py`:
- `THRESH.EAR_DROWSY`: lower = more sensitive drowsiness
- `THRESH.DROWSY_CONSEC_FRAMES`: frames below threshold to mark as _Drowsy_
- `GAZE.CENTER_TOLERANCE_X/Y`: deadzone around center (smaller = stricter)
- `GAZE.DISTRACTION_GRACE_SECS`: delay before labeling as _Distracted_

## How it works
- **Face & Iris**: MediaPipe Face Mesh (`refine_landmarks=True`) yields iris landmarks.
- **Gaze**: We normalize the iris center inside the eye box to `[-1, 1]` then bucket to 8 directions.
- **EAR**: From 6 eye landmarks per eye → `EAR=(||p2-p6||+||p3-p5||)/(2*||p1-p4||)`.
- **Attention logic**: Drowsy overrides Distracted; Distracted uses a short grace period.
- **Alerts**: Red border + audio on _Drowsy_; amber on _Distracted_; green on _Attentive_.

## Notes & Tips
- Good lighting improves stability.
- Glasses may reduce iris accuracy; increase `CENTER_TOLERANCE_*` if needed.
- For multi‑camera laptops, try indices 0,1,2.
- The included alarm tone is a simple generated sine wave. Replace with your own in `sounds/alarm.wav` if you want.

## License
MIT
>>>>>>> 9f6f762 (Initial commit - attention monitoring system)
