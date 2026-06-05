# -*- mode: python ; coding: utf-8 -*-

datas = [
    ('medpulse/data/*', 'medpulse/data'),
    ('medpulse/data/checklists/*', 'medpulse/data/checklists'),
    ('medpulse/data/drugs/*', 'medpulse/data/drugs'),
    ('medpulse/data/scores/*', 'medpulse/data/scores'),
    ('medpulse/locales/*', 'medpulse/locales'),
    ('medpulse/ui/windows/assets/*', 'medpulse/ui/windows/assets'),
    ('pill.ico', '.')
]

block_cipher = None

a = Analysis(
    ["medpulse/__main__.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['medpulse.locales', 'medpulse.data', 'medpulse.data.scores', 'medpulse.data.checklists', 'medpulse.data.drugs'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

import os
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
