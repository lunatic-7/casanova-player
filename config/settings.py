"""
Configuration constants for Casanova Player
"""
import os

# Window settings
WINDOW_TITLE = "Casanova Player"
WINDOW_WIDTH = 920
WINDOW_HEIGHT = 520
WINDOW_RESIZABLE = False

# Theme
APPEARANCE_MODE = "dark"
COLOR_THEME = "green"

# Colors - Modern dark theme
BG_PRIMARY = "#0d1117"       # GitHub dark background
BG_SECONDARY = "#161b22"     # Slightly lighter
BG_TERTIARY = "#21262d"      # Card/panel background
FG_PRIMARY = "#e6edf3"       # Main text
FG_SECONDARY = "#8b949e"     # Muted text
FG_ACCENT = "#58a6ff"        # Blue accent
ACCENT_COLOR = "#238636"     # Green primary
ACCENT_HOVER = "#2ea043"     # Green hover
ACCENT_LIGHT = "#3fb950"     # Light green
BORDER_COLOR = "#30363d"     # Subtle borders
SELECTION_BG = "#1f6feb"     # Selection highlight
WAVEFORM_COLOR = "#3fb950"   # Waveform bars
WAVEFORM_BG = "#0d1117"      # Waveform background

# Slider colors
SLIDER_PROGRESS = "#238636"
SLIDER_FG = "#21262d"
SLIDER_BUTTON = "#e6edf3"

# Waveform settings
WAVEFORM_WIDTH = 480
WAVEFORM_HEIGHT = 100

# Playback settings
SEEK_STEP = 5
UPDATE_INTERVAL_MS = 250
DEFAULT_VOLUME = 0.7

# Icon sizes
ICON_SIZE_CONTROL = (28, 28)
ICON_SIZE_PLAY = (32, 32)
ICON_SIZE_VOLUME = (20, 20)
ICON_SIZE_SMALL = (18, 18)

# Album art
ALBUM_ART_SIZE = (120, 130)

# Supported audio formats
AUDIO_FILETYPES = [
    ("Audio files", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
    ("All files", "*.*")
]

# Font settings
FONT_FAMILY = "Segoe UI"
FONT_SIZE_TITLE = 15
FONT_SIZE_NORMAL = 12
FONT_SIZE_SMALL = 11

# Download to playlist folder so they auto-load
DEFAULT_PLAYLIST_FOLDER = os.path.join(os.path.expanduser("~"), "Music", "playlist")
MUSIC_DOWNLOAD_FOLDER = DEFAULT_PLAYLIST_FOLDER  # Same as playlist folder
MAX_SEARCH_RESULTS = 7  # (Thala for a reason)

# Supported audio extensions
AUDIO_EXTENSIONS = (".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac")