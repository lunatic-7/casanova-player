# 🎵 Casanova Player

<div align="center">

![Casanova Player](https://github.com/user-attachments/assets/cc22af82-3f9b-485d-aa9e-5e83b9cb0299)

**Your Music, Everywhere**

A modern, feature-rich music player built with Python, CustomTkinter, and Pygame.

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/lunatic-7/casanova-player/releases)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Building](#-building-from-source) • [Contributing](#-contributing)

</div>

---

## ✨ Features

### 🎧 Core Playback
- **Multi-format support**: MP3, FLAC, WAV, OGG, M4A, AAC
- **Real-time waveform visualization**
- **ID3 tag reading** with album art display
- **Gapless playback** with instant track switching
- **Volume control** with mute toggle

### 📋 Playlist Management
- **Drag-free reordering** with ↑/↓ buttons
- **Shuffle mode** for random playback
- **Persistent playlist** across sessions
- **Batch import** from folders
- **Double-click to play**

### 🔴 YouTube Integration
- **Built-in YouTube search** - no browser needed
- **Direct MP3 download** at 192kbps quality
- **Auto-add to playlist** after download
- **Progress tracking** with status updates

### ⌨️ Keyboard Shortcuts
- `Space` - Play / Pause
- `←` / `→` - Seek backward/forward (5 seconds)
- Mouse wheel - Volume control (coming soon)

### 🎨 Modern UI
- **Dark theme** inspired by GitHub's design
- **Smooth animations** and transitions
- **Responsive controls** with hover effects
- **Marquee scrolling** for long titles
- **Tooltip hints** on all buttons

---

## 📸 Screenshots

<div align="center">

| Main Interface | YouTube Search | Playlist View |
|:--------------:|:--------------:|:-------------:|
| ![Main](https://github.com/user-attachments/assets/ba63ea18-d887-430a-8b36-7c18d85545c5) | ![Search](https://github.com/user-attachments/assets/b7be9b3a-d907-496c-a39b-e6ae5d1ca334) | ![Playlist](https://github.com/user-attachments/assets/8877c448-5181-4f0d-b451-ce9daf97f143) |

</div>

---

## 🚀 Installation

### Option 1: Windows Installer (Recommended)

1. Download the latest `CasanovaPlayer_Setup_v1.0.exe` from [Releases](https://github.com/lunatic-7/casanova-player/releases)
2. Run the installer
3. Launch from Start Menu or Desktop shortcut

### Option 2: Run from Source

```bash
# Clone the repository
git clone https://github.com/lunatic-7/casanova-player.git
cd casanova-player

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

---

## 📖 Usage

### Getting Started

1. **Add Music**
   - Click `+` to add local audio files
   - Click `📁` to load from `~/Music/playlist` folder
   - Click `🔴` to search and download from YouTube

2. **Playback Controls**
   - Click `▶️` to play, `⏸️` to pause
   - Use `⏮️` / `⏭️` for previous/next track
   - Drag the seek bar to jump to any position

3. **Organize Playlist**
   - Select a track and use `↑` / `↓` to reorder
   - Click `🔀` to shuffle
   - Use `Remove` / `Clear` buttons to manage tracks

### Folder Locations

| Purpose | Path | Auto-created? |
|---------|------|---------------|
| Default Playlist | `~/Music/playlist` | ✅ Yes |
| YouTube Downloads | `~/Music/playlist` | ✅ Yes |

---

## 🏗️ Project Structure

```
casanova_player/
│
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── casanova.spec              # PyInstaller configuration
├── installer.iss              # Inno Setup script
│
├── config/
│   └── settings.py            # App configuration & constants
│
├── core/
│   ├── player.py              # Audio playback engine (pygame)
│   └── playlist.py            # Playlist management logic
│
├── ui/
│   ├── app.py                 # Main application window
│   ├── left_panel.py          # Player controls & waveform
│   ├── right_panel.py         # Playlist panel
│   └── search_panel.py        # YouTube search dialog
│
├── utils/
│   ├── paths.py               # Resource path handling
│   ├── waveform.py            # Waveform computation
│   ├── metadata.py            # ID3 tag extraction
│   ├── youtube.py             # YouTube search & download
│   ├── tooltip.py             # Custom tooltips
│   └── windows_patch.py       # Windows console hiding
│
└── assets/
    ├── icons/                 # App icons (PNG/ICO)
    └── ffmpeg/                # FFmpeg binaries
```

---

## 🛠️ Building from Source

### Prerequisites

- Python 3.10 or higher
- pip package manager
- FFmpeg (included in `assets/ffmpeg/`)

### Build Windows Installer

```bash
# Install build tools
pip install pyinstaller

# Build executable
pyinstaller casanova.spec

# Install Inno Setup from https://jrsoftware.org/isdl.php

# Compile installer using installer.iss
# Output: installer_output/CasanovaPlayer_Setup_v1.0.exe
```

---

## 🎨 Tech Stack

| Component | Technology |
|-----------|-----------|
| **UI Framework** | CustomTkinter |
| **Audio Playback** | Pygame (mixer) |
| **Audio Processing** | pydub, mutagen |
| **Waveform** | NumPy |
| **YouTube** | yt-dlp |
| **Packaging** | PyInstaller, Inno Setup |

---

## 📦 Dependencies

```txt
customtkinter>=5.2.0    # Modern UI components
pygame>=2.5.0           # Audio playback
Pillow>=10.0.0          # Image processing
mutagen>=1.47.0         # Audio metadata
pydub>=0.25.1           # Audio manipulation
numpy>=1.24.0           # Waveform computation
yt-dlp>=2024.0.0        # YouTube downloading
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🐛 **Report bugs** - Open an issue with details
2. 💡 **Suggest features** - Share your ideas
3. 🔧 **Submit PRs** - Fork, code, and create a pull request
4. 📖 **Improve docs** - Help make the README better

### Development Setup

```bash
# Fork the repo and clone your fork
git clone https://github.com/lunatic-7/casanova-player.git

# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes and commit
git commit -m "Add amazing feature"

# Push and create a PR
git push origin feature/amazing-feature
```

---

## 🐛 Known Issues

- Seek precision limited by pygame mixer capabilities
- YouTube download requires internet connection
- Waveform generation may be slow for very large files (>100MB)

---

## 📝 Roadmap

- [ ] Playlist import/export (M3U, JSON)
- [ ] Equalizer with presets
- [ ] Lyrics display (synced LRC)
- [ ] Last.fm scrobbling
- [ ] Spotify integration
- [ ] Linux/macOS support
- [ ] Mini player mode
- [ ] System media controls integration
- [ ] MoodAI friend

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **CustomTkinter** - Modern UI framework
- **yt-dlp** - YouTube downloading
- **FFmpeg** - Audio processing
- Icon designs inspired by modern music players

---

## 📧 Contact

**Your Name** - [@wasifnadeem7](https://www.linkedin.com/in/wasifnadeem7/)

Project Link: [https://github.com/lunatic-7/casanova-player](https://github.com/lunatic-7/casanova-player)

---

<div align="center">

Made with ❤️ and Python

⭐ Star this repo if you like it!

</div>
