# Changelog

All notable changes to Casanova Player will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- 🎵 Multi-format audio playback (MP3, FLAC, WAV, OGG, M4A, AAC)
- 📊 Real-time waveform visualization
- 🎨 Modern dark UI with GitHub-inspired theme
- 🔴 YouTube search and download integration
- 📋 Playlist management with reordering (↑/↓ buttons)
- 🔀 Shuffle mode
- 🖼️ Album art display from ID3 tags
- ⌨️ Keyboard shortcuts (Space, ←, →)
- 📁 Auto-load from ~/Music/playlist folder
- 🎯 Marquee scrolling for long titles
- 💡 Helpful tooltips on all buttons
- 📦 Windows installer with Inno Setup
- 🎼 Track metadata display (title, artist, duration)
- 🔊 Volume control with mute toggle
- ⏯️ Instant track switching with background loading

### Technical
- Built with CustomTkinter for modern UI
- Pygame mixer for audio playback
- yt-dlp for YouTube downloading
- NumPy for efficient waveform computation
- Mutagen for ID3 tag reading
- Threading for non-blocking operations

### Known Issues
- Seek precision limited by pygame mixer capabilities
- Waveform generation may be slow for very large files (>100MB)
- YouTube download requires active internet connection

---

## [Unreleased]

### Planned Features
- Playlist import/export (M3U, JSON formats)
- Equalizer with presets
- Lyrics display with LRC sync
- Last.fm scrobbling
- Mini player mode
- System media controls integration
- Cross-platform support (Linux, macOS)

---

## Release Notes Template (for future releases)

## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements

---

[1.0.0]: https://github.com/yourusername/casanova-player/releases/tag/v1.0.0
[Unreleased]: https://github.com/yourusername/casanova-player/compare/v1.0.0...HEAD
