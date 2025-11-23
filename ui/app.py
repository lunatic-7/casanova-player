"""
Main application window - orchestrates all components
"""
import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import ImageTk

from config.settings import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_RESIZABLE,
    BG_PRIMARY, BG_SECONDARY, SEEK_STEP, UPDATE_INTERVAL_MS, AUDIO_FILETYPES,
    AUDIO_EXTENSIONS, DEFAULT_PLAYLIST_FOLDER
)
from utils.paths import get_icon_path
from utils.metadata import get_track_metadata, extract_album_art
from utils.waveform import compute_waveform
from ui.left_panel import LeftPanel
from ui.right_panel import RightPanel
from core.player import AudioPlayer
from core.playlist import Playlist

class MusicPlayerApp(ctk.CTk):
    """Main application class using CustomTkinter."""
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._init_components()
        self._bind_shortcuts()
        self._start_updater()
    
    def _setup_window(self):
        """Configure main window."""
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(fg_color=BG_PRIMARY)
        self.resizable(WINDOW_RESIZABLE, WINDOW_RESIZABLE)

        # Set window icon (works for taskbar and window)
        self.iconbitmap(get_icon_path("app.ico"))

        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    
    def _init_components(self):
        """Initialize all application components."""
        self.player = AudioPlayer()
        self.playlist = Playlist()
        self.is_dragging = False
        
        # Left panel callbacks
        left_callbacks = {
            "prev": self.prev_track,
            "next": self.next_track,
            "play_pause": self.play_pause_toggle,
            "on_seek_drag": self._on_seek_drag,
            "start_drag": self._start_drag,
            "end_drag": self._end_drag,
            "set_volume": self._set_volume,
            "toggle_mute": self._toggle_mute,
        }
        self.left_panel = LeftPanel(self, left_callbacks)
        self.left_panel.place(x=0, y=0)
        
        # Right panel callbacks
        right_callbacks = {
            "add": self.add_files,
            "remove": self.remove_selected,
            "clear": self.clear_playlist,
            "play_selected": self.play_selected,
            "reorder": self._on_reorder,
            "shuffle": self._on_shuffle,
            "youtube_search": self._open_youtube_search,
            "load_default_folder": self.load_default_folder,
        }
        self.right_panel = RightPanel(self, right_callbacks)
        self.right_panel.place(x=565, y=10)

        # Search panel reference
        self.search_panel = None
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.bind("<space>", lambda e: self.play_pause_toggle())
        self.bind("<Left>", lambda e: self.seek_relative(-SEEK_STEP))
        self.bind("<Right>", lambda e: self.seek_relative(SEEK_STEP))
    
    # --- Playlist Actions ---
    def add_files(self):
        """Open file dialog to add tracks."""
        files = filedialog.askopenfilenames(filetypes=AUDIO_FILETYPES)
        if not files:
            return
        
        for f in files:
            self.playlist.add(f)
            self.right_panel.add_item(self.playlist.get_display_names()[-1])
        
        if len(self.playlist) == len(files):
            self._load_current_track()

    def remove_selected(self):
        """Remove selected track from playlist."""
        idx = self.right_panel.get_selection()
        if idx < 0:
            return
        
        self.right_panel.remove_item(idx)
        current_changed = self.playlist.remove(idx)
        
        if current_changed:
            self.player.stop()
            if not self.playlist.is_empty():
                self._load_current_track()
    
    def clear_playlist(self):
        """Clear entire playlist."""
        self.player.stop()
        self.player.reset()
        self.playlist.clear()
        self.right_panel.clear()
        self.left_panel.set_title("No track loaded", "Select a track to play")
        self.left_panel.clear_waveform()
        self.left_panel.set_playing(False)

        # RESET timestamp + slider
        self.left_panel.set_time(0, 0)
        self.left_panel.set_seek_position(0)

    def _on_reorder(self, from_idx: int, to_idx: int):
        """Handle track reordering."""
        # Swap in playlist
        tracks = self.playlist.tracks
        tracks[from_idx], tracks[to_idx] = tracks[to_idx], tracks[from_idx]
        
        # Update current index if affected
        if self.playlist.current_index == from_idx:
            self.playlist.current_index = to_idx
        elif self.playlist.current_index == to_idx:
            self.playlist.current_index = from_idx
    
    def _on_shuffle(self, new_order: list):
        """Handle playlist shuffle."""
        # Create mapping from display names to file paths
        name_to_path = {}
        for path in self.playlist.tracks:
            name = os.path.basename(path)
            name_to_path[name] = path
        
        # Rebuild playlist in new order
        new_tracks = []
        for name in new_order:
            if name in name_to_path:
                new_tracks.append(name_to_path[name])
        
        self.playlist.tracks = new_tracks
        self.playlist.current_index = -1  # Reset current track

    # --- YouTube Search ---
    def _open_youtube_search(self):
        """Open YouTube search panel."""
        if self.search_panel is not None and self.search_panel.winfo_exists():
            self.search_panel.focus()
            return
        
        from ui.search_panel import SearchPanel
        self.search_panel = SearchPanel(self, self._on_youtube_download)
    
    def _on_youtube_download(self, filepath: str):
        """Handle downloaded file from YouTube."""
        # Add to playlist
        self.playlist.add(filepath)
        self.right_panel.add_item(os.path.basename(filepath))
        
        # If first track, load it
        if len(self.playlist) == 1:
            self._load_current_track()

    def load_default_folder(self):
        """Load all audio files from default playlist folder."""
        if not os.path.exists(DEFAULT_PLAYLIST_FOLDER):
            try:
                os.makedirs(DEFAULT_PLAYLIST_FOLDER, exist_ok=True)
                messagebox.showinfo(
                    "Folder Created",
                    f"Created playlist folder at:\n{DEFAULT_PLAYLIST_FOLDER}\n\n"
                    "Add your music files there and click 📁 again!"
                )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Could not create folder:\n{e}"
                )
            return
        
        audio_files = []
        for root, _, files in os.walk(DEFAULT_PLAYLIST_FOLDER):
            for fname in files:
                if fname.lower().endswith(AUDIO_EXTENSIONS):
                    audio_files.append(os.path.join(root, fname))
        
        if not audio_files:
            messagebox.showinfo("Empty Playlist", "No audio files found in folder.")
            return
        
        # Add to playlist
        for f in audio_files:
            self.playlist.add(f)
            self.right_panel.add_item(os.path.basename(f))
        
        # Load first track if playlist was empty before
        if len(self.playlist) == len(audio_files):
            self._load_current_track()
        
        messagebox.showinfo(
            "Loaded", 
            f"Loaded {len(audio_files)} songs from playlist folder."
        )
    
    def play_selected(self):
        """Play the selected track."""
        idx = self.right_panel.get_selection()
        if idx < 0:
            return
        self.playlist.set_current(idx)
        self._load_current_track()
        self._play()
    
    # --- Playback Actions ---
    def play_pause_toggle(self):
        """Toggle play/pause state."""
        if self.player.is_playing:
            self.player.pause()
            self.left_panel.set_playing(False)
        elif self.player.is_paused:
            self.player.unpause()
            self.left_panel.set_playing(True)
        else:
            if not self.player.current_file and not self.playlist.is_empty():
                self.playlist.set_current(0)
                self._load_current_track()
            self._play()
    
    def prev_track(self):
        """Play previous track."""
        if self.playlist.previous():
            self._load_current_track()
            self._play()
    
    def next_track(self):
        """Play next track."""
        if self.playlist.next():
            self._load_current_track()
            self._play()
    
    def _play(self):
        """Start playback of current track."""
        if self.player.play():
            self.left_panel.set_playing(True)
             # Highlight current track in playlist
            self.right_panel.set_playing_index(self.playlist.current_index)
        else:
            messagebox.showerror("Playback error", "Couldn't play file, Maybe try adding some songs to the playlist 😁")
    
    # --- Track Loading ---
    def _load_current_track(self):
        """Load the current playlist track."""
        filepath = self.playlist.get_current()
        if not filepath:
            return
        
        # Quick load - just get title and length for immediate playback
        filename = os.path.basename(filepath)
        title = os.path.splitext(filename)[0]
        
        # Set basic info immediately
        self.left_panel.set_title(title, "Loading...")
        
        # Get length quickly for player
        try:
            from mutagen.mp3 import MP3
            audio = MP3(filepath)
            length = int(audio.info.length)
        except:
            length = 0
        
        # Load into player immediately
        self.player.load(filepath, length)
        self.left_panel.set_time(0, length)
        self.left_panel.set_seek_position(0)
        
        # Highlight in playlist
        self.right_panel.set_playing_index(self.playlist.current_index)
        
        # Load metadata, album art, and waveform in background
        thread = threading.Thread(
            target=self._load_track_details,
            args=(filepath,),
            daemon=True
        )
        thread.start()

    def _load_track_details(self, filepath: str):
        """Load track details in background thread."""
        try:
            # Get full metadata
            meta = get_track_metadata(filepath)
            
            # Update UI from main thread
            self.after(0, lambda: self.left_panel.set_title(
                meta["title"], meta["artist"]
            ))
            
            # Load album art
            art = extract_album_art(filepath)
            album_img = ImageTk.PhotoImage(art)
            self.after(0, lambda: self._set_album_art(album_img))
            
            # Compute waveform (slowest operation)
            try:
                heights = compute_waveform(filepath)
                self.after(0, lambda: self.left_panel.draw_waveform(heights))
            except Exception:
                self.after(0, lambda: self.left_panel.clear_waveform())
                
        except Exception as e:
            print(f"Error loading track details: {e}")
    
    def _set_album_art(self, image):
        """Set album art (called from main thread)."""
        self.album_img = image  # Keep reference
        self.left_panel.set_album_art(self.album_img)

    # --- Seek Controls ---
    def _start_drag(self):
        self.is_dragging = True
    
    def _end_drag(self):
        self.is_dragging = False
        self._commit_seek()
    
    def _on_seek_drag(self, val):
        """Update time display while dragging."""
        if self.player.length:
            secs = int((float(val) / 100.0) * self.player.length)
            self.left_panel.set_time(secs, self.player.length)
    
    def _commit_seek(self):
        """Seek to the current slider position."""
        if not self.player.current_file or self.player.length == 0:
            return
        pct = self.left_panel.get_seek_position()
        seconds = int((pct / 100.0) * self.player.length)
        if not self.player.seek(seconds):
            messagebox.showwarning("Seek", "Seek not supported on this format")
        self.left_panel.set_playing(True)
    
    def seek_relative(self, delta: int):
        """Seek forward or backward by delta seconds."""
        if not self.player.current_file or self.player.length == 0:
            return
        elapsed = self.player.get_elapsed()
        new_pos = max(0, min(self.player.length, elapsed + delta))
        pct = (new_pos / self.player.length) * 100
        self.left_panel.set_seek_position(pct)
        self._commit_seek()
    
    # --- Volume ---
    def _set_volume(self, val):
        self.player.set_volume(float(val))
        self.left_panel.set_muted(self.player.is_muted)
    
    def _toggle_mute(self):
        is_muted = self.player.toggle_mute()
        self.left_panel.set_muted(is_muted)
    
    # --- UI Update Loop ---
    def _start_updater(self):
        """Start the periodic UI update loop."""
        self._update()
    
    def _update(self):
        """Periodic UI update."""
        if self.player.current_file:
            if self.player.is_track_ended():
                self.next_track()
            elif self.player.is_playing and not self.is_dragging:
                elapsed = self.player.get_elapsed()
                self.left_panel.set_time(elapsed, self.player.length)
                if self.player.length:
                    pct = (elapsed / self.player.length) * 100
                    self.left_panel.set_seek_position(pct)
        
        self.after(UPDATE_INTERVAL_MS, self._update)