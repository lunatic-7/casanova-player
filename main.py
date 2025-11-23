"""
Casanova Player - Entry Point
A modern music player built with CustomTkinter and Pygame
"""

# ============================================
# CRITICAL: Apply patches BEFORE any imports!
# ============================================
import subprocess
import platform
import sys

# Hide console windows on Windows (for ffmpeg/ffprobe)
if platform.system() == "Windows":
    _startupinfo = subprocess.STARTUPINFO()
    _startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    _startupinfo.wShowWindow = subprocess.SW_HIDE
    
    _original_popen_init = subprocess.Popen.__init__
    
    def _patched_popen_init(self, *args, **kwargs):
        if 'startupinfo' not in kwargs or kwargs['startupinfo'] is None:
            kwargs['startupinfo'] = _startupinfo
        if 'creationflags' not in kwargs:
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        _original_popen_init(self, *args, **kwargs)
    
    subprocess.Popen.__init__ = _patched_popen_init

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Hide pygame welcome message
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

# ============================================
# Now import everything else
# ============================================
import customtkinter as ctk
from config.settings import APPEARANCE_MODE, COLOR_THEME


def main():
    # Additional Windows patches for pydub
    from utils.windows_patch import apply_windows_patch, configure_pydub
    apply_windows_patch()
    
    # Configure CustomTkinter
    ctk.set_appearance_mode(APPEARANCE_MODE)
    ctk.set_default_color_theme(COLOR_THEME)
    
    # Configure pydub paths
    configure_pydub()
    
    # Import app here (after all patches applied)
    from ui.app import MusicPlayerApp
    
    # Create and run app
    app = MusicPlayerApp()
    app.mainloop()


if __name__ == "__main__":
    main()