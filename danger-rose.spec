# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path('.').absolute()

a = Analysis(
    ['src/main.py'],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        # Bundle all game assets
        ('assets', 'assets'),
        # Include any config files needed
        ('src/config', 'src/config'),
    ],
    hiddenimports=[
        'pygame',
        'pygame_ce',
        'pygame.locals',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude development tools
        'pytest',
        'black',
        'ruff',
        'pre_commit',
        'augint_github',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DangerRose',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for the game
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/icons/icon.ico' if os.path.exists('assets/images/icons/icon.ico') else None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DangerRose',
)
