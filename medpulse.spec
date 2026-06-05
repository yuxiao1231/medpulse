# -*- mode: python ; coding: utf-8 -*-
import os

# Filter out Android and Renderer files from being collected as datas
py_datas = []
for root, dirs, files in os.walk('medpulse'):
    dirs[:] = [d for d in dirs if d != '__pycache__' and d != 'android']
    for f in files:
        if f.endswith('.py') or f.endswith('.json') or f.endswith('.ttf') or f.endswith('.ttc'):
            if f == 'renderer.py':
                continue
            src = os.path.join(root, f)
            py_datas.append((src, root))

datas = py_datas + [
    ('pill.ico', '.')
]

# Only include lightweight standard libraries and tkinter.
# Exclude matplotlib, PIL, kivy, android.
hidden = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'ctypes',
    'math',
    'decimal',
    'traceback',
    'json',
    'glob'
]

# Explicitly tell PyInstaller to exclude these massive packages
excludes = [
    'matplotlib',
    'PIL',
    'kivy',
    'scipy',
    'numpy',
    'medpulse.ui.android'
]

block_cipher = None

a = Analysis(
    ['medpulse/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

icon_path = os.path.abspath('pill.ico') if os.path.exists('pill.ico') else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="MedPulse",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=icon_path,
)
