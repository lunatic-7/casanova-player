# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Casanova Player
Build command: pyinstaller casanova.spec
"""

import os
import sys

# Get customtkinter path for including themes
import customtkinter
ctk_path = os.path.dirname(customtkinter.__file__)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # App assets
        ('assets/icons', 'assets/icons'),
        ('assets/ffmpeg', 'assets/ffmpeg'),
        # CustomTkinter themes (required!)
        (ctk_path, 'customtkinter'),
    ],
    hiddenimports=[
        # HTTP
        'requests',
        # Tkinter
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        # CustomTkinter
        'customtkinter',
        # Audio libraries
        'pygame',
        'pygame.mixer',
        'mutagen',
        'mutagen.mp3',
        'mutagen.id3',
        'mutagen.id3._frames',
        'mutagen.id3._specs',
        'mutagen.flac',
        'mutagen.oggvorbis',
        'mutagen.mp4',
        'mutagen.easyid3',
        'mutagen.easymp4',
        'pydub',
        'pydub.audio_segment',
        'pydub.utils',
        'pydub.effects',
        'pydub.playback',
        # YouTube downloader
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.downloader',
        # NumPy (critical for waveform!)
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'numpy.fft',
        'numpy.random',
        # PIL/Pillow
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        # Standard library
        'threading',
        'queue',
        'json',
        'urllib',
        'urllib.request',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'notebook',
        'jupyter',
        'IPython',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CasanovaPlayer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CasanovaPlayer',
)