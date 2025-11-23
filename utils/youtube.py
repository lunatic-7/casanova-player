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

            # Store metadata for writing later
            video_info = None
            
            def progress_hook(d):
                nonlocal video_info

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
                # Get video info for metadata
                video_info = ydl.extract_info(url, download=False)
                # Download
                ydl.download([url])
            
            # Final path will have .mp3 extension
            final_path = output_path + '.mp3'
            
            if os.path.exists(final_path):
                # Write metadata to MP3 file
                if on_progress:
                    on_progress(95, "Adding metadata...") 
                    _write_metadata(final_path, video_info, output_path)
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

def _write_metadata(filepath: str, video_info: dict, base_path: str = None):
    """
    Write ID3 metadata to downloaded MP3 file including album art.
    
    Args:
        filepath: Path to MP3 file
        video_info: Video information from yt-dlp
        base_path: Base path for finding thumbnail file
    """
    try:
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TPE2, COMM, APIC
        from PIL import Image
        import io
        
        # Load or create ID3 tags
        try:
            audio = MP3(filepath, ID3=ID3)
            audio.add_tags()
        except:
            audio = MP3(filepath)
        
        if video_info:
            # Title
            if 'title' in video_info:
                audio['TIT2'] = TIT2(encoding=3, text=video_info['title'])
            
            # Artist (uploader/channel)
            if 'uploader' in video_info:
                audio['TPE1'] = TPE1(encoding=3, text=video_info['uploader'])
                audio['TPE2'] = TPE2(encoding=3, text=video_info['uploader'])
            
            # Album (set as "YouTube Downloads")
            audio['TALB'] = TALB(encoding=3, text="YouTube Downloads")
            
            # Year (upload date)
            if 'upload_date' in video_info:
                upload_date = video_info['upload_date']
                year = upload_date[:4] if len(upload_date) >= 4 else None
                if year:
                    audio['TDRC'] = TDRC(encoding=3, text=year)
            
            # Comment (source URL)
            if 'webpage_url' in video_info:
                audio['COMM'] = COMM(
                    encoding=3,
                    lang='eng',
                    desc='Source',
                    text=video_info['webpage_url']
                )
            
            # Album Art (thumbnail)
            thumbnail_data = _get_thumbnail(video_info, base_path)
            if thumbnail_data:
                audio['APIC'] = APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=thumbnail_data
                )
        
        # Save tags
        audio.save()
        
    except Exception:
        pass  # Ignore metadata writing errors


def _get_thumbnail(video_info: dict, base_path: str = None) -> bytes:
    """
    Get and process thumbnail image for album art.
    
    Args:
        video_info: Video information from yt-dlp
        base_path: Base path where thumbnail might be saved
        
    Returns:
        Thumbnail image data as bytes, or None if not available
    """
    try:
        from PIL import Image
        import io
        
        # Try to find downloaded thumbnail file
        if base_path:
            # yt-dlp saves thumbnails with various extensions
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                thumb_path = base_path + ext
                if os.path.exists(thumb_path):
                    # Load and convert image
                    img = Image.open(thumb_path)
                    
                    # Resize to reasonable size (500x500 max)
                    img.thumbnail((500, 500), Image.Resampling.LANCZOS)
                    
                    # Convert to JPEG
                    output = io.BytesIO()
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Convert transparent images to RGB
                        img = img.convert('RGB')
                    img.save(output, format='JPEG', quality=85)
                    
                    # Clean up thumbnail file
                    try:
                        os.remove(thumb_path)
                    except:
                        pass
                    
                    return output.getvalue()
        
        # Fallback: download thumbnail from URL
        if 'thumbnail' in video_info and video_info['thumbnail']:
            import urllib.request
            
            thumb_url = video_info['thumbnail']
            
            # Download thumbnail
            with urllib.request.urlopen(thumb_url, timeout=10) as response:
                thumb_data = response.read()
            
            # Load and process
            img = Image.open(io.BytesIO(thumb_data))
            img.thumbnail((500, 500), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.save(output, format='JPEG', quality=85)
            
            return output.getvalue()
        
        return None
        
    except Exception:
        return None



def get_download_folder() -> str:
    """Return the download folder path."""
    return MUSIC_DOWNLOAD_FOLDER