"""
Left panel UI - Controls, waveform, and playback info
"""
import customtkinter as ctk
from tkinter import Canvas, ROUND
from PIL import Image
from config.settings import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BORDER_COLOR,
    FG_PRIMARY, FG_SECONDARY, FG_ACCENT,
    WAVEFORM_WIDTH, WAVEFORM_HEIGHT, WAVEFORM_COLOR, WAVEFORM_BG,
    ICON_SIZE_CONTROL, ICON_SIZE_PLAY, ICON_SIZE_VOLUME, DEFAULT_VOLUME,
    ACCENT_COLOR, ACCENT_HOVER, ACCENT_LIGHT,
    SLIDER_PROGRESS, SLIDER_FG, SLIDER_BUTTON,
    FONT_FAMILY, FONT_SIZE_TITLE, FONT_SIZE_NORMAL, FONT_SIZE_SMALL,
    ALBUM_ART_SIZE
)
from utils.paths import get_icon_path
from utils.tooltip import CTkTooltip

class MarqueeLabel(ctk.CTkFrame):
    """A label that scrolls text if it's too long."""
    
    def __init__(self, parent, text="", font=None, text_color=None, max_width=280, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.max_width = max_width
        self.full_text = text
        self.text_color = text_color or FG_PRIMARY
        self.font = font or ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_TITLE, weight="bold")
        
        self.scroll_pos = 0.0  # Float for smooth scrolling
        self.is_scrolling = False
        self.scroll_delay = 30  # Faster refresh for smoother animation
        self.scroll_speed = 0.8  # Pixels per frame (slower = smoother)
        self.pause_at_start = 2500
        self.scroll_id = None

        # Container to clip text
        self.configure(width=max_width, height=25)
        self.pack_propagate(False)
        
        # Canvas for smooth pixel-based scrolling
        self.canvas = Canvas(
            self,
            width=max_width,
            height=25,
            bg=BG_SECONDARY,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(anchor="w", side="left")
        
        # Create text on canvas
        self.text_id = self.canvas.create_text(
            0, 12,
            text=text,
            font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"),
            fill=self.text_color,
            anchor="w"
        )
        
        self._check_scroll_needed()
    
    def _check_scroll_needed(self):
        """Check if scrolling is needed based on text width."""
        self.update_idletasks()
        
        # Get actual text width from canvas
        bbox = self.canvas.bbox(self.text_id)
        if bbox:
            text_width = bbox[2] - bbox[0]
        else:
            text_width = len(self.full_text) * 9
        
        if text_width > self.max_width:
            self.is_scrolling = True
            # Create duplicated text for seamless loop
            self.canvas.itemconfig(
                self.text_id,
                text=self.full_text + "    ●    " + self.full_text
            )
            self.after(self.pause_at_start, self._start_scroll)
        else:
            self.is_scrolling = False
            self.canvas.itemconfig(self.text_id, text=self.full_text)
    
    def _start_scroll(self):
        """Start the scrolling animation."""
        if not self.is_scrolling:
            return
        self._scroll_step()
    
    def _scroll_step(self):
        """Perform smooth pixel-based scroll step."""
        if not self.is_scrolling or not self.winfo_exists():
            return
        
        # Move by pixels (smooth)
        self.scroll_pos += self.scroll_speed
        
        # Get text width for reset
        bbox = self.canvas.bbox(self.text_id)
        if bbox:
            text_width = bbox[2] - bbox[0]
            
            # Reset when scrolled past first copy
            # Divide by 2 because we have duplicated text
            if self.scroll_pos >= text_width / 2:
                self.scroll_pos = 0
        
        # Update position (negative for left scroll)
        self.canvas.coords(self.text_id, -self.scroll_pos, 12)
        
        self.scroll_id = self.after(self.scroll_delay, self._scroll_step)
    
    def set_text(self, text: str):
        """Update the label text."""
        if self.scroll_id:
            self.after_cancel(self.scroll_id)
            self.scroll_id = None
        
        self.full_text = text
        self.scroll_pos = 0.0
        self.is_scrolling = False
        self.canvas.itemconfig(self.text_id, text=text)
        self.canvas.coords(self.text_id, 0, 12)
        self._check_scroll_needed()
    
    def stop_scroll(self):
        """Stop scrolling."""
        self.is_scrolling = False
        if self.scroll_id:
            self.after_cancel(self.scroll_id)

class LeftPanel(ctk.CTkFrame):
    """Left side panel containing playback controls and waveform."""
    
    def __init__(self, parent, callbacks: dict):
        super().__init__(
            parent, 
            width=560, 
            height=420,
            fg_color=BG_PRIMARY,
            corner_radius=0
        )
        self.callbacks = callbacks
        self._load_icons()
        self._create_widgets()
    
    def _load_icons(self):
        """Load all icon images."""
        self.icons = {
            "prev": ctk.CTkImage(
                Image.open(get_icon_path("previous.png")), size=ICON_SIZE_CONTROL),
            "play": ctk.CTkImage(
                Image.open(get_icon_path("play.png")), size=ICON_SIZE_PLAY),
            "pause": ctk.CTkImage(
                Image.open(get_icon_path("pause.png")), size=ICON_SIZE_PLAY),
            "next": ctk.CTkImage(
                Image.open(get_icon_path("next.png")), size=ICON_SIZE_CONTROL),
            "audio": ctk.CTkImage(
                Image.open(get_icon_path("audio.png")), size=ICON_SIZE_VOLUME),
            "mute": ctk.CTkImage(
                Image.open(get_icon_path("mute.png")), size=ICON_SIZE_VOLUME),
            "info": ctk.CTkImage(
                Image.open(get_icon_path("info.png")), size=(18, 18)),
        }
    
    def _create_widgets(self):
        """Create all widgets for the left panel."""

        # ===== Header with App Name & Info =====
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))
        
        # App name and tagline
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="🎧 Casanova Player",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=ACCENT_LIGHT
        ).pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="  •  Your Music, Everywhere",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=FG_SECONDARY
        ).pack(side="left")

        
        # Info button
        info_btn = ctk.CTkButton(
            header, text="", image=self.icons["info"],
            width=28, height=28,
            fg_color="transparent",
            hover_color=BG_TERTIARY,
            corner_radius=14
        )
        info_btn.pack(side="right")

        ctk.CTkLabel(
            header,
            text="v1.0",
            font=ctk.CTkFont(family=FONT_FAMILY, size=9),
            text_color=FG_SECONDARY
        ).pack(side="right", padx=(0, 8))
        
        # Rich tooltip for info
        info_text = """━━━━━━━━━━━━━━━━━━━━━━━━━━
        🎵 Casanova Player
        ━━━━━━━━━━━━━━━━━━━━━━━━━━

        📁  Load Folder
            Auto-loads songs from ~/Music/playlist

        ➕  Add Files  
            Add local audio files (MP3, FLAC, WAV, OGG)

        🔴  YouTube Search
            Search & download songs as MP3

        🎮  Keyboard Shortcuts
            Space ─── Play/Pause
            ← / → ─── Seek 5 seconds

        📋  Playlist Controls
            ↑ / ↓ ─── Reorder tracks
            🔀 ─── Shuffle playlist
            Double-click ─── Play track

        💾  Downloads: ~/Music/playlist

        ━━━━━━━━━━━━━━━━━━━━━━━━━━
            Made with ❤️ in Python
        ━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        CTkTooltip(info_btn, info_text, delay=200)
        
        # ===== Now Playing Section =====
        now_playing_frame = ctk.CTkFrame(self, fg_color=BG_SECONDARY, corner_radius=12)
        now_playing_frame.pack(fill="x", padx=15, pady=(5, 8))
        
        # Inner content
        content = ctk.CTkFrame(now_playing_frame, fg_color="transparent")
        content.pack(fill="x", padx=12, pady=12)
        
        # Album art with rounded corners
        self.album_frame = ctk.CTkFrame(
            content, 
            width=ALBUM_ART_SIZE[0], 
            height=ALBUM_ART_SIZE[1],
            fg_color=BG_TERTIARY,
            corner_radius=10
        )
        self.album_frame.pack(side="left", padx=(0, 12))
        self.album_frame.pack_propagate(False)
        
        self.album_art_label = ctk.CTkLabel(
            self.album_frame, 
            text="♪",
            font=ctk.CTkFont(size=36),
            text_color=FG_SECONDARY
        )
        self.album_art_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Track info - FIXED WIDTH
        info_frame = ctk.CTkFrame(content, fg_color="transparent", width=280)
        info_frame.pack(side="left", fill="y")
        info_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            info_frame,
            text="NOW PLAYING",
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            text_color=ACCENT_LIGHT
        ).pack(anchor="w")
        
        # Marquee title
        self.title_label = MarqueeLabel(
            info_frame,
            text="No track loaded",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_TITLE, weight="bold"),
            text_color=FG_PRIMARY,
            max_width=270
        )
        self.title_label.pack(anchor="w", pady=(2, 0))
        
        # Artist (subtitle)
        self.artist_label = ctk.CTkLabel(
            info_frame,
            text="Select a track to play",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SMALL),
            text_color=FG_SECONDARY,
            anchor="w",
            width=270
        )
        self.artist_label.pack(anchor="w", pady=(2, 0))
        
        # ===== Controls Section =====
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(pady=(3, 6))
        
        # Previous button
        self.prev_btn = ctk.CTkButton(
            controls_frame, text="", image=self.icons["prev"],
            width=44, height=44, 
            fg_color="transparent",
            hover_color=BG_TERTIARY,
            corner_radius=22,
            command=self.callbacks["prev"]
        )
        self.prev_btn.grid(row=0, column=0, padx=6)
        CTkTooltip(self.prev_btn, "Previous (←)")
        
        # Play/Pause button - larger and prominent
        self.play_button = ctk.CTkButton(
            controls_frame, text="", image=self.icons["play"],
            width=50, height=50,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            corner_radius=25,
            command=self.callbacks["play_pause"]
        )
        self.play_button.grid(row=0, column=1, padx=10)
        CTkTooltip(self.play_button, "Play / Pause (Space)")
        
        # Next button
        self.next_btn = ctk.CTkButton(
            controls_frame, text="", image=self.icons["next"],
            width=44, height=44,
            fg_color="transparent",
            hover_color=BG_TERTIARY,
            corner_radius=22,
            command=self.callbacks["next"]
        )
        self.next_btn.grid(row=0, column=2, padx=6)
        CTkTooltip(self.next_btn, "Next (→)")
        
        # ===== Progress Section =====
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=(0, 0))
        
        # Time labels
        time_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        time_frame.pack(fill="x")
        
        self.current_time_label = ctk.CTkLabel(
            time_frame, text="0:00",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SMALL),
            text_color=FG_SECONDARY,
            width=40
        )
        self.current_time_label.pack(side="left")
        
        self.total_time_label = ctk.CTkLabel(
            time_frame, text="0:00",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SMALL),
            text_color=FG_SECONDARY,
            width=40
        )
        self.total_time_label.pack(side="right")
        
        # Seek slider
        self.seek_var = ctk.DoubleVar(value=0)
        self.seek_slider = ctk.CTkSlider(
            progress_frame,
            from_=0, to=100,
            variable=self.seek_var,
            width=480, height=16,
            progress_color=ACCENT_COLOR,
            button_color=FG_PRIMARY,
            button_hover_color=ACCENT_LIGHT,
            fg_color=BG_TERTIARY,
            command=self._on_seek_change
        )
        self.seek_slider.pack(fill="x", pady=(2, 0))
        self.seek_slider.bind("<ButtonPress-1>", lambda e: self.callbacks["start_drag"]())
        self.seek_slider.bind("<ButtonRelease-1>", lambda e: self.callbacks["end_drag"]())
        
        # ===== Waveform Section =====
        wave_frame = ctk.CTkFrame(self, fg_color="transparent")
        wave_frame.pack(fill="x", padx=20, pady=(2, 0))
        
        self.wave_canvas = Canvas(
            wave_frame,
            width=WAVEFORM_WIDTH,
            height=WAVEFORM_HEIGHT,
            bg=BG_SECONDARY,
            bd=0,
            highlightthickness=0
        )
        self.wave_canvas.pack(fill="x")
        
        # ===== Volume Section =====
        vol_frame = ctk.CTkFrame(self, fg_color="transparent")
        vol_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        # Mute button
        self.mute_button = ctk.CTkButton(
            vol_frame, text="", image=self.icons["audio"],
            width=32, height=32,
            fg_color="transparent",
            hover_color=BG_TERTIARY,
            corner_radius=16,
            command=self.callbacks["toggle_mute"]
        )
        self.mute_button.pack(side="left", padx=(0, 10))
        CTkTooltip(self.mute_button, "Mute / Unmute")
        
        # Volume slider
        self.volume_var = ctk.DoubleVar(value=DEFAULT_VOLUME)
        self.volume_slider = ctk.CTkSlider(
            vol_frame,
            from_=0, to=1,
            variable=self.volume_var,
            width=140, height=12,
            progress_color=FG_ACCENT,
            button_color=FG_PRIMARY,
            button_hover_color=FG_ACCENT,
            fg_color=BG_TERTIARY,
            command=self._on_volume_change
        )
        self.volume_slider.pack(side="left")
        
        # Volume percentage
        self.volume_label = ctk.CTkLabel(
            vol_frame,
            text="70%",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SMALL),
            text_color=FG_SECONDARY,
            width=35
        )
        self.volume_label.pack(side="left", padx=(8, 0))
    
    def _on_seek_change(self, value):
        """Handle seek slider changes."""
        if self.callbacks.get("on_seek_drag"):
            self.callbacks["on_seek_drag"](value)
    
    def _on_volume_change(self, value):
        """Handle volume slider changes."""
        self.volume_label.configure(text=f"{int(value * 100)}%")
        if self.callbacks.get("set_volume"):
            self.callbacks["set_volume"](value)
    
    def set_title(self, title: str, artist: str = ""):
        """Update the track title and artist display."""
        self.title_label.set_text(text=title if title else "No track loaded")
        self.artist_label.configure(text=artist if artist else "Unknown artist")
    
    def set_album_art(self, image):
        """Update album art display."""
        self.album_img = image
        self.album_art_label.configure(image=self.album_img, text="")
    
    def set_time(self, current: int, total: int):
        """Update time display."""
        cur_m, cur_s = divmod(max(0, current), 60)
        tot_m, tot_s = divmod(total, 60)
        self.current_time_label.configure(text=f"{cur_m}:{cur_s:02d}")
        self.total_time_label.configure(text=f"{tot_m}:{tot_s:02d}")
    
    def set_seek_position(self, percentage: float):
        """Update seek bar position (0-100)."""
        self.seek_var.set(percentage)
    
    def get_seek_position(self) -> float:
        """Get current seek bar position (0-100)."""
        return self.seek_var.get()
    
    def set_playing(self, is_playing: bool):
        """Update play button icon."""
        icon = self.icons["pause"] if is_playing else self.icons["play"]
        self.play_button.configure(image=icon)
    
    def set_muted(self, is_muted: bool):
        """Update mute button icon."""
        icon = self.icons["mute"] if is_muted else self.icons["audio"]
        self.mute_button.configure(image=icon)
    
    def draw_waveform(self, heights: list):
        """Draw waveform visualization."""
        self.wave_canvas.delete("all")
        mid = WAVEFORM_HEIGHT // 2
        bar_width = max(2, WAVEFORM_WIDTH // len(heights))
        gap = 1
        
        for i, val in enumerate(heights):
            x = i * (bar_width + gap)
            y = int(val)
            if y > 0:
                # Draw rounded bars
                self.wave_canvas.create_line(
                    x, mid - y, x, mid + y,
                    width=bar_width,
                    fill=WAVEFORM_COLOR,
                    capstyle=ROUND
                )
    
    def clear_waveform(self):
        """Clear the waveform display."""
        self.wave_canvas.delete("all")