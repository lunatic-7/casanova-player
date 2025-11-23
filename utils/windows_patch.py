"""
Windows-specific patches to hide console windows for ffmpeg/ffprobe
"""
import subprocess
import platform
import sys

# Store original Popen
_original_popen = subprocess.Popen

def apply_windows_patch():
    """
    Monkey patch subprocess.Popen to hide console windows on Windows.
    Must be called BEFORE importing pydub or any audio libraries.
    """
    if platform.system() != "Windows":
        return
    
    # Create startup info to hide window
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    
    # Patch Popen class
    class HiddenPopen(subprocess.Popen):
        def __init__(self, *args, **kwargs):
            # Force hide console on Windows
            if 'startupinfo' not in kwargs or kwargs['startupinfo'] is None:
                kwargs['startupinfo'] = startupinfo
            
            # Also set creation flags to hide window
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = (
                    subprocess.CREATE_NO_WINDOW | 
                    subprocess.DETACHED_PROCESS
                )
            
            # Redirect stderr to prevent console output
            if 'stderr' not in kwargs:
                kwargs['stderr'] = subprocess.DEVNULL
            
            super().__init__(*args, **kwargs)
    
    # Apply the patch
    subprocess.Popen = HiddenPopen
    
    # Also patch os.system if used
    import os
    _original_system = os.system
    
    def hidden_system(command):
        subprocess.run(
            command, 
            shell=True, 
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return 0
    
    os.system = hidden_system


def configure_pydub():
    """Configure pydub with correct ffmpeg paths."""
    from pydub import AudioSegment
    from pydub.utils import get_player_name, get_prober_name
    from utils.paths import get_ffmpeg_path, get_ffprobe_path
    
    # Set converter and prober paths
    AudioSegment.converter = get_ffmpeg_path()
    AudioSegment.ffprobe = get_ffprobe_path()
    
    # Also patch pydub's subprocess calls
    if platform.system() == "Windows":
        import pydub.utils
        
        _original_mediainfo = getattr(pydub.utils, 'mediainfo_json', None)
        
        if _original_mediainfo:
            def patched_mediainfo(filepath):
                """Patched mediainfo to hide console."""
                import json
                
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                prober = get_ffprobe_path()
                
                command = [
                    prober,
                    '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_format',
                    '-show_streams',
                    filepath
                ]
                
                try:
                    result = subprocess.run(
                        command,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        capture_output=True,
                        text=True
                    )
                    return json.loads(result.stdout)
                except Exception:
                    return {}
            
            pydub.utils.mediainfo_json = patched_mediainfo