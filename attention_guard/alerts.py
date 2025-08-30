import threading
import time
try:
    import pygame
    PYGAME_OK = True
except Exception:
    PYGAME_OK = False

class AlertManager:
    def __init__(self, play_audio: bool = True):
        self.play_audio = play_audio and PYGAME_OK
        self._lock = threading.Lock()
        self._muted = False
        if self.play_audio:
            pygame.mixer.init()
    
    def set_muted(self, muted: bool):
        with self._lock:
            self._muted = muted
    
    def is_muted(self) -> bool:
        with self._lock:
            return self._muted
    
    def play(self, wav_path: str):
        if not self.play_audio: 
            return
        if self.is_muted():
            return
        try:
            snd = pygame.mixer.Sound(wav_path)
            snd.play()
        except Exception:
            # Swallow audio errors
            pass
