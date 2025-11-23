"""
Modern tooltip utility for CustomTkinter
"""
import customtkinter as ctk

class CTkTooltip:
    """
    Modern tooltip for CustomTkinter widgets.
    Matches the CTk aesthetic with rounded corners and smooth appearance.
    
    Usage:
        button = ctk.CTkButton(parent, text="Play")
        CTkTooltip(button, "Play or pause the current track")
    """
    
    def __init__(self, widget, text: str, delay: int = 400, 
                 bg_color: str = "#1a1a2e", text_color: str = "#e6eef8",
                 corner_radius: int = 8, padding: int = 8):
        """
        Args:
            widget: The widget to attach tooltip to
            text: Tooltip text to display
            delay: Milliseconds before showing (default 400ms)
            bg_color: Background color
            text_color: Text color
            corner_radius: Corner radius for rounded look
            padding: Internal padding
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.bg_color = bg_color
        self.text_color = text_color
        self.corner_radius = corner_radius
        self.padding = padding
        
        self.tooltip_window = None
        self.scheduled_id = None
        
        # Bind events
        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<ButtonPress>", self._on_leave, add="+")
    
    def _on_enter(self, event=None):
        """Schedule tooltip to appear after delay."""
        self._cancel_scheduled()
        self.scheduled_id = self.widget.after(self.delay, self._show)
    
    def _on_leave(self, event=None):
        """Hide tooltip and cancel any scheduled show."""
        self._cancel_scheduled()
        self._hide()
    
    def _cancel_scheduled(self):
        """Cancel any scheduled tooltip display."""
        if self.scheduled_id:
            self.widget.after_cancel(self.scheduled_id)
            self.scheduled_id = None
    
    def _show(self):
        """Display the tooltip."""
        if self.tooltip_window:
            return
        
        # Get widget position
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        
        # Create tooltip window
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Remove window shadow/decoration
        self.tooltip_window.configure(fg_color=self.bg_color)
        
        # Make it transparent initially for fade effect
        self.tooltip_window.attributes("-alpha", 0.0)
        
        # Tooltip frame with rounded corners
        frame = ctk.CTkFrame(
            self.tooltip_window,
            fg_color=self.bg_color,
            corner_radius=self.corner_radius,
            border_width=1,
            border_color="#2a2a4e"
        )
        frame.pack(padx=2, pady=2)
        
        # Tooltip label
        label = ctk.CTkLabel(
            frame,
            text=self.text,
            text_color=self.text_color,
            font=ctk.CTkFont(size=11),
            padx=self.padding,
            pady=self.padding // 2
        )
        label.pack()
        
        # Update to get actual size
        self.tooltip_window.update_idletasks()
        
        # Reposition to center under widget
        tip_width = self.tooltip_window.winfo_width()
        x = self.widget.winfo_rootx() + (self.widget.winfo_width() - tip_width) // 2
        
        # Keep tooltip on screen
        screen_width = self.widget.winfo_screenwidth()
        if x + tip_width > screen_width - 10:
            x = screen_width - tip_width - 10
        if x < 10:
            x = 10
            
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Fade in effect
        self._fade_in(0.0)
    
    def _fade_in(self, alpha):
        """Animate fade in."""
        if self.tooltip_window and alpha < 0.95:
            alpha += 0.15
            self.tooltip_window.attributes("-alpha", alpha)
            self.tooltip_window.after(20, lambda: self._fade_in(alpha))
        elif self.tooltip_window:
            self.tooltip_window.attributes("-alpha", 0.95)
    
    def _hide(self):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def add_tooltip(widget, text: str, **kwargs):
    """Convenience function to add tooltip to a widget."""
    return CTkTooltip(widget, text, **kwargs)