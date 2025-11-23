"""
Right panel UI - Playlist management
"""
import customtkinter as ctk
import random
from PIL import Image
from config.settings import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BORDER_COLOR,
    FG_PRIMARY, FG_SECONDARY, SELECTION_BG,
    ICON_SIZE_SMALL, ACCENT_COLOR, ACCENT_HOVER, ACCENT_LIGHT,
    FONT_FAMILY, FONT_SIZE_TITLE, FONT_SIZE_NORMAL, FONT_SIZE_SMALL
)
from utils.paths import get_icon_path
from utils.tooltip import CTkTooltip


class RightPanel(ctk.CTkFrame):
    """Right side panel containing playlist."""
    
    def __init__(self, parent, callbacks: dict):
        super().__init__(
            parent, 
            width=345, 
            height=420,
            fg_color=BG_SECONDARY,
            corner_radius=12
        )
        self.pack_propagate(False)
        self.callbacks = callbacks
        self.selected_index = -1
        self.items = []
        
        self._load_icons()
        self._create_widgets()
    
    def _load_icons(self):
        """Load all icon images."""
        self.icons = {
            "clear": ctk.CTkImage(
                Image.open(get_icon_path("clear.png")), size=(18, 18)),
            "remove": ctk.CTkImage(
                Image.open(get_icon_path("remove.png")), size=(18, 18)),
            "add": ctk.CTkImage(
                Image.open(get_icon_path("add_list.png")), size=(18, 18)),
            "shuffle": ctk.CTkImage(
                Image.open(get_icon_path("shuffle.png")), size=(16, 16)),
            "up": ctk.CTkImage(
                Image.open(get_icon_path("up.png")), size=(14, 14)),
            "down": ctk.CTkImage(
                Image.open(get_icon_path("down.png")), size=(14, 14)),
            "youtube": ctk.CTkImage(
                Image.open(get_icon_path("youtube.png")), size=(18, 18)),
            "folder": ctk.CTkImage(
                Image.open(get_icon_path("music_folder.png")), size=(18, 18)),
        }
    
    def _create_widgets(self):
        """Create all widgets for the right panel."""
        
        # ===== Header Row =====
        header = ctk.CTkFrame(self, fg_color="transparent", height=35)
        header.pack(fill="x", padx=12, pady=(10, 6))
        header.pack_propagate(False)
        
        # Title
        ctk.CTkLabel(
            header,
            text="📋 Playlist",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=FG_PRIMARY
        ).pack(side="left")
        
        # Track count
        self.count_label = ctk.CTkLabel(
            header,
            text="0 tracks",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=FG_SECONDARY
        )
        self.count_label.pack(side="right")
        
        # ===== Action Buttons Row =====
        actions = ctk.CTkFrame(self, fg_color="transparent", height=32)
        actions.pack(fill="x", padx=12, pady=(0, 6))
        actions.pack_propagate(False)
        
        # Left side - reorder buttons
        left_actions = ctk.CTkFrame(actions, fg_color="transparent")
        left_actions.pack(side="left")
        
        self.up_btn = ctk.CTkButton(
            left_actions, text="", image=self.icons["up"],
            width=28, height=26, fg_color=BG_TERTIARY,
            hover_color="#3d4248", corner_radius=5,
            command=self._move_up
        )
        self.up_btn.pack(side="left", padx=(0, 3))
        CTkTooltip(self.up_btn, "Move up")
        
        self.down_btn = ctk.CTkButton(
            left_actions, text="", image=self.icons["down"],
            width=28, height=26, fg_color=BG_TERTIARY,
            hover_color="#3d4248", corner_radius=5,
            command=self._move_down
        )
        self.down_btn.pack(side="left", padx=(0, 3))
        CTkTooltip(self.down_btn, "Move down")
        
        shuffle_btn = ctk.CTkButton(
            left_actions, text="", image=self.icons["shuffle"],
            width=28, height=26, fg_color=BG_TERTIARY,
            hover_color="#3d4248", corner_radius=5,
            command=self._shuffle_playlist
        )
        shuffle_btn.pack(side="left")
        CTkTooltip(shuffle_btn, "Shuffle")
        
        # Right side - add buttons
        right_actions = ctk.CTkFrame(actions, fg_color="transparent")
        right_actions.pack(side="right")
        
        # Folder button
        folder_btn = ctk.CTkButton(
            right_actions, text="", image=self.icons["folder"],
            width=28, height=26, fg_color=BG_TERTIARY,
            hover_color="#3d4248", corner_radius=5,
            command=self.callbacks.get("load_default_folder", lambda: None)
        )
        folder_btn.pack(side="left", padx=(0, 3))
        CTkTooltip(folder_btn, "Load from ~/Music/playlist")
        
        # YouTube button
        yt_btn = ctk.CTkButton(
            right_actions, text="", image=self.icons["youtube"],
            width=28, height=26, fg_color="#cc0000",
            hover_color="#aa0000", corner_radius=5,
            command=self.callbacks.get("youtube_search", lambda: None)
        )
        yt_btn.pack(side="left", padx=(0, 3))
        CTkTooltip(yt_btn, "YouTube search")
        
        # Add files button
        add_btn = ctk.CTkButton(
            right_actions, text="", image=self.icons["add"],
            width=28, height=26, fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER, corner_radius=5,
            command=self.callbacks["add"]
        )
        add_btn.pack(side="left")
        CTkTooltip(add_btn, "Add local files")
        
        # ===== Playlist Container - MAXIMIZED =====
        list_container = ctk.CTkFrame(
            self, fg_color=BG_TERTIARY, corner_radius=8
        )
        list_container.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        
        # Scrollable frame
        self.playlist_scroll = ctk.CTkScrollableFrame(
            list_container,
            fg_color="transparent",
            scrollbar_button_color=BG_SECONDARY,
            scrollbar_button_hover_color=ACCENT_COLOR
        )
        self.playlist_scroll.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Empty state
        self.empty_label = ctk.CTkLabel(
            self.playlist_scroll,
            text="No tracks added\n\nUse + to add files\nor 📁 to load folder",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=FG_SECONDARY,
            justify="center"
        )
        self.empty_label.pack(expand=True, pady=30)
        
        self.track_frames = []
        
        # ===== Bottom Controls - COMPACT =====
        bottom = ctk.CTkFrame(self, fg_color="transparent", height=32)
        bottom.pack(fill="x", padx=12, pady=(0, 10))
        bottom.pack_propagate(False)
        
        # Remove button
        remove_btn = ctk.CTkButton(
            bottom, text="Remove", image=self.icons["remove"],
            width=75, height=28, fg_color=BG_TERTIARY,
            hover_color="#3d4248", corner_radius=6,
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            command=self.callbacks["remove"]
        )
        remove_btn.pack(side="left", padx=(0, 4))
        CTkTooltip(remove_btn, "Remove selected")
        
        # Clear button
        clear_btn = ctk.CTkButton(
            bottom, text="Clear", image=self.icons["clear"],
            width=65, height=28, fg_color=BG_TERTIARY,
            hover_color="#3d4248", corner_radius=6,
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            command=self.callbacks["clear"]
        )
        clear_btn.pack(side="left")
        CTkTooltip(clear_btn, "Clear playlist")
    
    def _create_track_item(self, index: int, name: str):
        """Create a single track item - COMPACT."""
        frame = ctk.CTkFrame(
            self.playlist_scroll,
            fg_color="transparent",
            corner_radius=4,
            height=24  # Compact height
        )
        frame.pack(fill="x", pady=0)  # No vertical padding
        frame.pack_propagate(False)
        
        inner = ctk.CTkFrame(frame, fg_color="transparent", corner_radius=4)
        inner.pack(fill="both", expand=True)
        
        # Track number
        num_label = ctk.CTkLabel(
            inner,
            text=f"{index + 1:02d}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=FG_SECONDARY,
            width=22
        )
        num_label.pack(side="left", padx=(6, 3))
        
        # Track name - compact
        display_name = name[:38] + "..." if len(name) > 38 else name
        name_label = ctk.CTkLabel(
            inner,
            text=display_name,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=FG_PRIMARY,
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True, padx=2)
        
        # Bind events
        for widget in [frame, inner, num_label, name_label]:
            widget.bind("<Button-1>", lambda e, i=index: self._on_select(i))
            widget.bind("<Double-Button-1>", lambda e: self.callbacks["play_selected"]())
            widget.bind("<Enter>", lambda e, f=inner: f.configure(fg_color=BG_SECONDARY))
            widget.bind("<Leave>", lambda e, f=inner, i=index: 
                       f.configure(fg_color=ACCENT_COLOR if i == self.selected_index else "transparent"))
        
        return frame, inner, name_label
    
    def _on_select(self, index: int):
        """Handle track selection."""
        if 0 <= self.selected_index < len(self.track_frames):
            self.track_frames[self.selected_index][1].configure(fg_color="transparent")
        
        self.selected_index = index
        if 0 <= index < len(self.track_frames):
            self.track_frames[index][1].configure(fg_color=ACCENT_COLOR)
    
    def set_playing_index(self, index: int):
        """Highlight the currently playing track."""
        self._on_select(index)
    
    def _move_up(self):
        """Move selected track up."""
        if self.selected_index <= 0 or self.selected_index >= len(self.items):
            return
        
        idx = self.selected_index
        self.items[idx], self.items[idx - 1] = self.items[idx - 1], self.items[idx]
        
        if self.callbacks.get("reorder"):
            self.callbacks["reorder"](idx, idx - 1)
        
        self._rebuild_list()
        self._on_select(idx - 1)
    
    def _move_down(self):
        """Move selected track down."""
        if self.selected_index < 0 or self.selected_index >= len(self.items) - 1:
            return
        
        idx = self.selected_index
        self.items[idx], self.items[idx + 1] = self.items[idx + 1], self.items[idx]
        
        if self.callbacks.get("reorder"):
            self.callbacks["reorder"](idx, idx + 1)
        
        self._rebuild_list()
        self._on_select(idx + 1)
    
    def _shuffle_playlist(self):
        """Shuffle all tracks randomly."""
        if len(self.items) < 2:
            return
        
        random.shuffle(self.items)
        
        if self.callbacks.get("shuffle"):
            self.callbacks["shuffle"](self.items)
        
        self._rebuild_list()
        self.selected_index = -1
    
    def _rebuild_list(self):
        """Rebuild the entire track list display."""
        for frame, _, _ in self.track_frames:
            frame.destroy()
        self.track_frames = []
        
        for i, name in enumerate(self.items):
            frame_data = self._create_track_item(i, name)
            self.track_frames.append(frame_data)
    
    def get_selection(self) -> int:
        return self.selected_index
    
    def refresh(self, items: list):
        self.clear()
        for item in items:
            self.add_item(item)
    
    def add_item(self, name: str):
        self.empty_label.pack_forget()
        
        index = len(self.track_frames)
        frame_data = self._create_track_item(index, name)
        self.track_frames.append(frame_data)
        self.items.append(name)
        
        self._update_count()
    
    def remove_item(self, index: int):
        if 0 <= index < len(self.track_frames):
            self.track_frames[index][0].destroy()
            del self.track_frames[index]
            del self.items[index]
            
            if self.selected_index == index:
                self.selected_index = -1
            elif self.selected_index > index:
                self.selected_index -= 1
            
            self._rebuild_list()
            self._update_count()
            
            if self.selected_index >= 0:
                self._on_select(self.selected_index)
            
            if not self.track_frames:
                self.empty_label.pack(expand=True, pady=30)
    
    def _update_count(self):
        count = len(self.track_frames)
        self.count_label.configure(text=f"{count} track{'s' if count != 1 else ''}")
    
    def clear(self):
        for frame, _, _ in self.track_frames:
            frame.destroy()
        self.track_frames = []
        self.items = []
        self.selected_index = -1
        self._update_count()
        self.empty_label.pack(expand=True, pady=30)
    
    def get_items(self) -> list:
        return self.items.copy()