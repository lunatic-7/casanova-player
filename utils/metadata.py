"""
Audio metadata extraction utilities
"""
import os
import io
from PIL import Image
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from config.settings import ALBUM_ART_SIZE

def get_track_metadata(filepath: str) -> dict:
    """
    Extract metadata from audio file.
    Returns dict with title, artist, and length.
    """
    filename = os.path.basename(filepath)
    # Remove extension for default title
    title = os.path.splitext(filename)[0]
    artist = "Unknown artist"
    length = 0
    
    try:
        meta = MutagenFile(filepath, easy=True)
        if meta:
            title = meta.get("title", [title])[0]
            artist = meta.get("artist", ["Unknown artist"])[0]
    except Exception:
        pass
    
    # Get track length
    try:
        audio = MP3(filepath)
        length = int(audio.info.length)
    except Exception:
        try:
            from pydub import AudioSegment
            seg = AudioSegment.from_file(filepath)
            length = int(seg.duration_seconds)
        except Exception:
            length = 0
    
    return {
        "title": title,
        "artist": artist,
        "length": length,
        "display_title": f"{title} — {artist}" if artist != "Unknown artist" else title
    }

def extract_album_art(filepath: str) -> Image.Image:
    """
    Extract album art from audio file.
    Returns PIL Image or placeholder if not found.
    """
    img = None
    
    try:
        f = MutagenFile(filepath)
        if hasattr(f, "tags") and f.tags:
            # Try MP3 APIC frames
            for tag_k in f.tags.keys():
                if tag_k.startswith("APIC"):
                    img_data = f.tags[tag_k].data
                    img = Image.open(io.BytesIO(img_data))
                    break
            # FLAC/MP4 coverart
            if img is None and hasattr(f, "pictures") and getattr(f, "pictures"):
                img_data = f.pictures[0].data
                img = Image.open(io.BytesIO(img_data))
    except Exception:
        img = None
    
    if img is None:
        # Create placeholder
        img = Image.new("RGB", ALBUM_ART_SIZE, color=(18, 24, 28))
    
    return img.resize(ALBUM_ART_SIZE, Image.LANCZOS)