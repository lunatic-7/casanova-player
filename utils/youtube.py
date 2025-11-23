"""
YouTube search and download utilities using yt-dlp
"""
import os
import threading
import re
from typing import Callable, Optional
import yt_dlp

from utils.paths import get_ffmpeg_path
from config.settings import MUSIC_DOWNLOAD_FOLDER, MAX_SEARCH_RESULTS


# Ensure download folder exists
os.makedirs(MUSIC_DOWNLOAD_FOLDER, exist_ok=True)


def search_youtube(query: str, max_results: int = MAX_SEARCH_RESULTS) -> list:
    """
    Search YouTube for videos.
    Returns list of dicts with: id, title, duration, channel, thumbnail
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Keep it fast
        'default_search': 'ytsearch',
    }
    
    results = []
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(
                f"ytsearch{max_results}:{query}", 
                download=False
            )
            
            if search_results and 'entries' in search_results:
                for entry in search_results['entries']:
                    if entry:
                        # Format duration
                        duration = entry.get('duration', 0) or 0
                        mins, secs = divmod(int(duration), 60)
                        
                        # Construct thumbnail URL from video ID
                        video_id = entry.get('id', '')
                        thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else ""
                        
                        results.append({
                            'id': video_id,
                            'title': entry.get('title', 'Unknown'),
                            'duration': f"{mins}:{secs:02d}",
                            'duration_seconds': duration,
                            'channel': entry.get('channel', entry.get('uploader', 'Unknown')),
                            'url': f"https://www.youtube.com/watch?v={video_id}",
                            'thumbnail': thumbnail,
                        })
    except Exception:
        pass  # On error, return empty list
        
    
    return results


def sanitize_filename(title: str) -> str:
    """Remove invalid characters from filename."""
    # Remove invalid chars
    sanitized = re.sub(r'[<>:"/\\|?*]', '', title)
    # Remove extra spaces
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    # Limit length
    return sanitized[:100] if len(sanitized) > 100 else sanitized


def download_audio(
    url: str,
    title: str,
    on_progress: Optional[Callable[[float, str], None]] = None,
    on_complete: Optional[Callable[[str], None]] = None,
    on_error: Optional[Callable[[str], None]] = None
) -> None:
    """
    Download YouTube video as MP3.
    Runs in background thread.
    
    Args:
        url: YouTube video URL
        title: Video title for filename
        on_progress: Callback(percent, status) for progress updates
        on_complete: Callback(filepath) when download completes
        on_error: Callback(error_message) on error
    """
    
    def _download():
        try:
            filename = sanitize_filename(title)
            output_path = os.path.join(MUSIC_DOWNLOAD_FOLDER, filename)
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    # Calculate percentage
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    if total > 0:
                        percent = (downloaded / total) * 100
                        if on_progress:
                            on_progress(percent, "Downloading...")
                
                elif d['status'] == 'finished':
                    if on_progress:
                        on_progress(90, "Converting to MP3...")
            
            # Use my local ffmpeg
            ffmpeg_path = get_ffmpeg_path()

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook],

                # Bug Fix
                'ffmpeg_location': ffmpeg_path,
            }

            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Final path will have .mp3 extension
            final_path = output_path + '.mp3'
            
            if os.path.exists(final_path):
                if on_progress:
                    on_progress(100, "Complete!")
                if on_complete:
                    on_complete(final_path)
            else:
                # Sometimes yt-dlp doesn't add extension
                if os.path.exists(output_path):
                    os.rename(output_path, final_path)
                    if on_progress:
                        on_progress(100, "Complete!")
                    if on_complete:
                        on_complete(final_path)
                else:
                    raise FileNotFoundError("Downloaded file not found")
                    
        except Exception as e:
            if on_error:
                on_error(str(e))
    
    # Run in background thread
    thread = threading.Thread(target=_download, daemon=True)
    thread.start()


def get_download_folder() -> str:
    """Return the download folder path."""
    return MUSIC_DOWNLOAD_FOLDER