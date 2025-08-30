import time
from collections import deque

class FPSCounter:
    def __init__(self, maxlen=60):
        self.times = deque(maxlen=maxlen)
    
    def tick(self):
        now = time.time()
        self.times.append(now)
    
    def fps(self):
        if len(self.times) < 2:
            return 0.0
        elapsed = self.times[-1] - self.times[0]
        return (len(self.times) - 1) / elapsed if elapsed > 0 else 0.0

def clamp(v, lo, hi):
    return max(lo, min(hi, v))
