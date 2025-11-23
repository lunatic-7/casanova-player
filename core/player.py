"""
Audio playback engine using pygame mixer
"""
import time
from pygame import mixer
from config.settings import DEFAULT_VOLUME

class AudioPlayer:
    """Handles audio playback, seeking, and volume control."""
    
    def __init__(self):
        mixer.init()
        mixer.music.set_volume(DEFAULT_VOLUME)
        
        self.current_file = None
        self.length = 0
        self.is_playing = False
        self.is_paused = False
        self.start_time = 0.0
        self.paused_time = 0.0

        # Mute state
        self.is_muted = False
        self.volume_before_mute = DEFAULT_VOLUME
    
    def load(self, filepath: str, length: int):
        """Load an audio file for playback."""
        self.current_file = filepath
        self.length = length
        self.is_playing = False
        self.is_paused = False
        self.start_time = 0.0
        self.paused_time = 0.0
    
    def play(self) -> bool:
        """Start playback. Returns True on success."""
        if not self.current_file:
            return False
        try:
            mixer.music.load(self.current_file)
            mixer.music.play()
            self.start_time = time.time()
            self.is_playing = True
            self.is_paused = False
            return True
        except Exception:
            return False
    
    def pause(self):
        """Pause playback."""
        if self.is_playing:
            mixer.music.pause()
            self.paused_time = time.time() - self.start_time
            self.is_playing = False
            self.is_paused = True
    
    def unpause(self):
        """Resume playback."""
        if self.is_paused:
            mixer.music.unpause()
            self.start_time = time.time() - self.paused_time
            self.is_playing = True
            self.is_paused = False
    
    def stop(self):
        """Stop playback completely."""
        mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
    
    def seek(self, seconds: int) -> bool:
        """Seek to position in seconds. Returns True on success."""
        if not self.current_file or self.length == 0:
            return False
        try:
            mixer.music.play(start=seconds)
            self.start_time = time.time() - seconds
            self.is_playing = True
            self.is_paused = False
            return True
        except Exception:
            return False
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)."""
        vol = max(0.0, min(1.0, volume))
        mixer.music.set_volume(vol)
        # If user adjusts volume, unmute
        if vol > 0 and self.is_muted:
            self.is_muted = False
        self.volume_before_mute = vol
    
    def toggle_mute(self) -> bool:
        """Toggle mute state. Returns new mute state."""
        if self.is_muted:
            # Unmute - restore previous volume
            mixer.music.set_volume(self.volume_before_mute)
            self.is_muted = False
        else:
            # Mute - save current volume and set to 0
            self.volume_before_mute = mixer.music.get_volume()
            mixer.music.set_volume(0.0)
            self.is_muted = True
        return self.is_muted
    
    def get_elapsed(self) -> int:
        """Get current playback position in seconds."""
        if self.is_playing:
            return int(time.time() - self.start_time)
        elif self.is_paused:
            return int(self.paused_time)
        return 0
    
    def is_track_ended(self) -> bool:
        """Check if current track has finished playing."""
        if self.is_playing and self.length > 0:
            return self.get_elapsed() >= self.length
        return False
    
    def reset(self):
        """Fully reset the audio player state after clearing the playlist."""
        try:
            mixer.music.stop()
        except Exception:
            pass

        self.current_file = None
        self.is_playing = False
        self.is_paused = False
        self.length = 0
        self.start_time = 0.0
        self.paused_time = 0.0
