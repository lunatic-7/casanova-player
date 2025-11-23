"""
Playlist management
"""
import os
from typing import Optional, List

class Playlist:
    """Manages the list of audio tracks."""
    
    def __init__(self):
        self.tracks: List[str] = []
        self.current_index: int = -1
    
    def add(self, filepath: str):
        """Add a track to the playlist."""
        self.tracks.append(filepath)
        if self.current_index == -1:
            self.current_index = 0
    
    def add_multiple(self, filepaths: List[str]):
        """Add multiple tracks to the playlist."""
        for f in filepaths:
            self.add(f)
    
    def remove(self, index: int) -> bool:
        """Remove track at index. Returns True if current track changed."""
        if index < 0 or index >= len(self.tracks):
            return False
        
        del self.tracks[index]
        current_changed = False
        
        if index == self.current_index:
            current_changed = True
            if self.tracks:
                self.current_index = min(index, len(self.tracks) - 1)
            else:
                self.current_index = -1
        elif index < self.current_index:
            self.current_index -= 1
        
        return current_changed
    
    def clear(self):
        """Clear all tracks."""
        self.tracks = []
        self.current_index = -1
    
    def get_current(self) -> Optional[str]:
        """Get current track filepath."""
        if 0 <= self.current_index < len(self.tracks):
            return self.tracks[self.current_index]
        return None
    
    def get_current_name(self) -> str:
        """Get current track filename."""
        current = self.get_current()
        return os.path.basename(current) if current else ""
    
    def set_current(self, index: int) -> bool:
        """Set current track by index. Returns True if valid."""
        if 0 <= index < len(self.tracks):
            self.current_index = index
            return True
        return False
    
    def next(self) -> bool:
        """Move to next track. Returns True if playlist not empty."""
        if not self.tracks:
            return False
        self.current_index = (self.current_index + 1) % len(self.tracks)
        return True
    
    def previous(self) -> bool:
        """Move to previous track. Returns True if playlist not empty."""
        if not self.tracks:
            return False
        self.current_index = (self.current_index - 1) % len(self.tracks)
        return True
    
    def get_display_names(self) -> List[str]:
        """Get list of track filenames for display."""
        return [os.path.basename(f) for f in self.tracks]
    
    def is_empty(self) -> bool:
        """Check if playlist is empty."""
        return len(self.tracks) == 0
    
    def __len__(self) -> int:
        return len(self.tracks)