import csv, os, time, threading, datetime as dt
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Counters:
    attentive: float = 0.0
    distracted: float = 0.0
    drowsy: float = 0.0

class SessionLogger:
    def __init__(self, base_dir: str, interval_secs: float = 1.0):
        self.base_dir = base_dir
        os.makedirs(os.path.join(base_dir, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(base_dir, 'reports'), exist_ok=True)
        self.interval = interval_secs
        self._stop = threading.Event()
        self._thread = None
        self.state = "attentive"
        self.counters = Counters()
        self.last_tick = time.time()
        self.session_id = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_path = os.path.join(base_dir, 'logs', f'session_{self.session_id}.csv')
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'state'])
    
    def set_state(self, state: str):
        now = time.time()
        dt_s = now - self.last_tick
        if self.state == 'attentive':
            self.counters.attentive += dt_s
        elif self.state == 'distracted':
            self.counters.distracted += dt_s
        else:
            self.counters.drowsy += dt_s
        self.last_tick = now
        self.state = state
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([dt.datetime.now().isoformat(timespec='seconds'), state])
    
    def start(self):
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        # finalize last segment
        self.set_state(self.state)
        # write report
        report_path = os.path.join(self.base_dir, 'reports', f'report_{self.session_id}.csv')
        with open(report_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            total = self.counters.attentive + self.counters.distracted + self.counters.drowsy
            w.writerow(['metric','seconds','percent'])
            for name, secs in [('attentive', self.counters.attentive), ('distracted', self.counters.distracted), ('drowsy', self.counters.drowsy)]:
                pct = (secs / total * 100.0) if total > 0 else 0.0
                w.writerow([name, round(secs, 1), f"{pct:.1f}%"])        
        return report_path
    
    def _run(self):
        while not self._stop.wait(self.interval):
            # periodic tick to accumulate time even if state unchanged
            self.set_state(self.state)
