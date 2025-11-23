"""
YouTube Search Panel - Search and download music from YouTube
"""
import customtkinter as ctk
import requests
from io import BytesIO
from PIL import Image
import threading
from config.settings import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY,
    FG_PRIMARY, FG_SECONDARY,
    ACCENT_COLOR, ACCENT_HOVER, ACCENT_LIGHT,
    FONT_FAMILY, FONT_SIZE_NORMAL, FONT_SIZE_SMALL, ICON_SIZE_SMALL
)
from utils.paths import get_icon_path
from utils.tooltip import CTkTooltip
from utils.youtube import search_youtube, download_audio, get_download_folder


class SearchPanel(ctk.CTkToplevel):
    """YouTube search and download panel."""
    
    def __init__(self, parent, on_download_complete: callable):
        super().__init__(parent)
        
        self.on_download_complete = on_download_complete
        self.search_results = []
        self.selected_index = -1
        self.is_downloading = False
        
        self._setup_window()
        self._load_icons()
        self._create_widgets()
        
        # Focus on search entry
        self.search_entry.focus()
    
    def _setup_window(self):
        """Configure the window."""
        self.title("YouTube Search")
        self.geometry("500x520")
        self.configure(fg_color=BG_PRIMARY)
        self.resizable(False, False)
        
        # Center on parent
        self.transient(self.master)
        self.grab_set()
        
        # Position
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 500) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 520) // 2
        self.geometry(f"+{x}+{y}")
    
    def _load_icons(self):
        """Load icons."""
        self.icons = {
            "search": ctk.CTkImage(
                Image.open(get_icon_path("search.png")), size=ICON_SIZE_SMALL),
            "download": ctk.CTkImage(
                Image.open(get_icon_path("download.png")), size=ICON_SIZE_SMALL),
        }
    
    def _create_widgets(self):
        """Create all widgets."""
        
        # ===== Header =====
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 15))
        
        ctk.CTkLabel(
            header,
            text="🎵 YouTube Music Search",
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            text_color=FG_PRIMARY
        ).pack(side="left")
        
        # ===== Search Bar =====
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search for songs, artists...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            height=40,
            corner_radius=20,
            fg_color=BG_TERTIARY,
            border_color=BG_TERTIARY,
            text_color=FG_PRIMARY
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._do_search())
        
        self.search_btn = ctk.CTkButton(
            search_frame,
            text="",
            image=self.icons["search"],
            width=40, height=40,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            corner_radius=20,
            command=self._do_search
        )
        self.search_btn.pack(side="right")
        CTkTooltip(self.search_btn, "Search YouTube")
        
        # ===== Status Label =====
        self.status_label = ctk.CTkLabel(
            self,
            text="Enter a search term to find music",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SMALL),
            text_color=FG_SECONDARY
        )
        self.status_label.pack(pady=(0, 10))
        
        # ===== Results Container =====
        results_container = ctk.CTkFrame(
            self,
            fg_color=BG_SECONDARY,
            corner_radius=10
        )
        results_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        self.results_scroll = ctk.CTkScrollableFrame(
            results_container,
            fg_color="transparent",
            scrollbar_button_color=BG_TERTIARY,
            scrollbar_button_hover_color=ACCENT_COLOR
        )
        self.results_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Empty state
        self.empty_label = ctk.CTkLabel(
            self.results_scroll,
            text="Search results will appear here",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_NORMAL),
            text_color=FG_SECONDARY
        )
        self.empty_label.pack(expand=True, pady=50)
        
        self.result_frames = []
        
        # ===== Progress Bar =====
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            width=350,
            height=8,
            progress_color=ACCENT_COLOR,
            fg_color=BG_TERTIARY
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", padx=(0, 10))
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZE_SMALL),
            text_color=FG_SECONDARY
        )
        self.progress_label.pack(side="left")
        
        # Hide progress initially
        self.progress_frame.pack_forget()
        
        # ===== Download Button =====
        self.download_btn = ctk.CTkButton(
            self,
            text="Download Selected",
            image=self.icons["download"],
            width=200, height=40,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            corner_radius=10,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            command=self._do_download,
            state="disabled"
        )
        self.download_btn.pack(pady=(0, 20))
        
        # ===== Folder Info =====
        folder_label = ctk.CTkLabel(
            self,
            text=f"📁 Downloads: {get_download_folder()}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=FG_SECONDARY
        )
        folder_label.pack(pady=(0, 10))
    
    def _do_search(self):
        """Perform YouTube search."""
        query = self.search_entry.get().strip()
        if not query:
            return
        
        # Update UI
        self.status_label.configure(text="Searching...")
        self.search_btn.configure(state="disabled")
        self._clear_results()
        
        # Search in background
        def search_thread():
            results = search_youtube(query)
            self.after(0, lambda: self._show_results(results))
        
        thread = threading.Thread(target=search_thread, daemon=True)
        thread.start()
    
    def _clear_results(self):
        """Clear search results."""
        for frame in self.result_frames:
            frame.destroy()
        self.result_frames = []
        self.search_results = []
        self.selected_index = -1
        self.download_btn.configure(state="disabled")

    def _refresh_result_thumbnail(self, index):
        """Update the thumbnail inside the correct placeholder label."""
        try:
            thumb = self.search_results[index].get("thumb_image")
            widget = self.search_results[index].get("thumb_widget")

            if thumb and widget:
                widget.configure(image=thumb, text="")
        except Exception:
            pass

    def _create_thumbnail_image(self, index, img_bytes):
        """Create CTkImage and update UI in main thread."""
        try:
            # Check if index is still valid
            if index >= len(self.search_results):
                return
                
            # Convert bytes back to PIL Image - FIXED
            # We need to create a new PIL Image from the bytes, not pass the BytesIO object
            pil_image = Image.open(img_bytes)
            
            # Create the CTkImage - FIXED: pass the PIL Image directly
            thumb_image = ctk.CTkImage(
                light_image=pil_image,  # This should be the PIL Image, not BytesIO
                dark_image=pil_image,   # This should be the PIL Image, not BytesIO
                size=(60, 60)
            )
            
            # Store in results
            self.search_results[index]["thumb_image"] = thumb_image
            
            # Update the thumbnail widget if it exists
            thumb_widget = self.search_results[index].get("thumb_widget")
            if thumb_widget and thumb_widget.winfo_exists():
                thumb_widget.configure(image=thumb_image, text="")

        except Exception:
            pass  # Ignore errors in thumbnail creation

    def _load_thumbnail(self, index, result):
        """Load thumbnail in background thread."""
        try:
            url = result.get("thumbnail")
            if not url:
                return

            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return
                
            img = Image.open(BytesIO(response.content))
            img = img.resize((60, 60), Image.Resampling.LANCZOS)
            
            # Convert to bytes for thread-safe transfer
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Pass the image data to main thread
            self.after(0, lambda: self._create_thumbnail_image(index, img_bytes))
            
        except Exception:
            pass  # Ignore thumbnail loading errors
    
    def _show_results(self, results: list):
        """Display search results."""
        self.search_btn.configure(state="normal")
        self.search_results = results
        
        if not results:
            self.status_label.configure(text="No results found")
            self.empty_label.pack(expand=True, pady=50)
            return
        
        self.status_label.configure(text=f"Found {len(results)} results (Thala for a reason!)")
        self.empty_label.pack_forget()
        
        for i, result in enumerate(results):
            # download thumbnail in background thread
            threading.Thread(
                target=self._load_thumbnail,
                args=(i, result),
                daemon=True
            ).start()
            frame = self._create_result_item(i, result)
            self.result_frames.append(frame)
    
    def _create_result_item(self, index: int, result: dict):
        """Create a single search result item with thumbnail."""
        
        frame = ctk.CTkFrame(
            self.results_scroll,
            fg_color="transparent",
            corner_radius=8,
            height=70
        )
        frame.pack(fill="x", pady=2)
        frame.pack_propagate(False)
        
        inner = ctk.CTkFrame(frame, fg_color="transparent", corner_radius=8)
        inner.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Thumbnail Placeholder
        thumb_frame = ctk.CTkFrame(inner, fg_color="transparent", width=60, height=60)
        thumb_frame.pack(side="left", padx=10)
        thumb_frame.pack_propagate(False)  # Important: prevent size changes
        
        # Create placeholder with loading text
        thumb_label = ctk.CTkLabel(
            thumb_frame,
            text="📁",  # Placeholder icon
            width=60,
            height=60,
            fg_color=BG_TERTIARY,
            corner_radius=6,
            font=ctk.CTkFont(size=20)
        )
        thumb_label.pack()
        
        # Store widget reference immediately
        result["thumb_widget"] = thumb_label
        
        # Start loading thumbnail
        threading.Thread(
            target=self._load_thumbnail,
            args=(index, result),
            daemon=True
        ).start()
        
        # Rest of your existing _create_result_item code...
        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=5)
        
        # Title (truncate long titles)
        title = result.get("title", "")
        if len(title) > 45:
            title = title[:45] + "..."
        
        title_label = ctk.CTkLabel(
            info_frame,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=FG_PRIMARY,
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # Channel + Duration
        meta_text = f"{result.get('channel', '')} • {result.get('duration', '')}"
        meta_label = ctk.CTkLabel(
            info_frame,
            text=meta_text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=FG_SECONDARY,
            anchor="w"
        )
        meta_label.pack(anchor="w")
        
        # Bind click/hover events
        clickable_widgets = [frame, inner, thumb_label, info_frame, title_label, meta_label]

        for widget in clickable_widgets:
            widget.bind("<Button-1>", lambda e, i=index: self._on_select(i))
            widget.bind("<Enter>", lambda e, f=inner: f.configure(fg_color=BG_TERTIARY))
            widget.bind(
                "<Leave>",
                lambda e, f=inner, i=index:
                    f.configure(
                        fg_color=ACCENT_COLOR if i == self.selected_index else "transparent"
                    )
            )
        
        return frame

    def _on_select(self, index: int):
        """Handle result selection."""
        # Deselect previous
        if 0 <= self.selected_index < len(self.result_frames):
            # Reset previous frame color
            for child in self.result_frames[self.selected_index].winfo_children():
                child.configure(fg_color="transparent")
        
        # Select new
        self.selected_index = index
        if 0 <= index < len(self.result_frames):
            for child in self.result_frames[index].winfo_children():
                child.configure(fg_color=ACCENT_COLOR)
            self.download_btn.configure(state="normal")
    
    def _do_download(self):
        """Download selected video."""
        if self.selected_index < 0 or self.is_downloading:
            return
        
        result = self.search_results[self.selected_index]
        
        # Show progress
        self.is_downloading = True
        self.progress_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        self.progress_label.configure(text="Starting...")
        self.download_btn.configure(state="disabled", text="Downloading...")
        
        def on_progress(percent, status):
            self.after(0, lambda: self._update_progress(percent, status))
        
        def on_complete(filepath):
            self.after(0, lambda: self._download_complete(filepath))
        
        def on_error(error):
            self.after(0, lambda: self._download_error(error))
        
        download_audio(
            url=result['url'],
            title=result['title'],
            on_progress=on_progress,
            on_complete=on_complete,
            on_error=on_error
        )
    
    def _update_progress(self, percent: float, status: str):
        """Update progress bar."""
        self.progress_bar.set(percent / 100)
        self.progress_label.configure(text=status)
    
    def _download_complete(self, filepath: str):
        """Handle download completion."""
        self.is_downloading = False
        self.progress_label.configure(text="✓ Download complete!")
        self.download_btn.configure(state="normal", text="Download Selected")
        
        # Notify parent to add to playlist
        if self.on_download_complete:
            self.on_download_complete(filepath)
        
        # Reset after delay
        self.after(2000, self._reset_progress)
    
    def _download_error(self, error: str):
        """Handle download error."""
        self.is_downloading = False
        self.progress_label.configure(text=f"✗ Error: {error[:50]}")
        self.download_btn.configure(state="normal", text="Download Selected")
        
        # Reset after delay
        self.after(3000, self._reset_progress)
    
    def _reset_progress(self):
        """Reset progress bar."""
        self.progress_bar.set(0)
        self.progress_label.configure(text="")
        self.progress_frame.pack_forget()