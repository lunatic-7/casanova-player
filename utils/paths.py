"""
Path utilities for PyInstaller compatibility
"""
import os
import sys

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource.
    Works for both PyInstaller bundled apps and development.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_icon_path(icon_name: str) -> str:
    """Get path to an icon file."""
    return resource_path(f"assets/icons/{icon_name}")

def get_ffmpeg_path() -> str:
    """Get path to ffmpeg executable."""
    return resource_path("assets/ffmpeg/ffmpeg.exe")

def get_ffprobe_path() -> str:
    """Get path to ffprobe executable."""
    return resource_path("assets/ffmpeg/ffprobe.exe")