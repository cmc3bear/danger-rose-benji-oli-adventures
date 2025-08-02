#!/usr/bin/env python3
"""Check if all required game assets exist."""

import os
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"

# Required assets by category
REQUIRED_ASSETS = {
    "images/characters": [
        "danger.png",
        "rose.png",
        "dad_kenney.png",
        "danger_kenney.png",
        "rose_kenney.png",
    ],
    "images/icons": [
        "arrow_left.png",
        "arrow_right.png",
        "button_blue.png",
        "button_green.png",
    ],
    "images/tilesets": [
        "living_room.png",
    ],
    "images/tilesets/ski": [
        "tree.png",
        "rock.png",
        "snowball.png",
        "winter_tileset.png",
    ],
    "images/tilesets/pool": [
        "water_balloon.png",
        "water_splash_sheet.png",
        "splash_01.png",
        "splash_02.png",
    ],
    "images/tilesets/vegas": [
        "slot_machine_frame.png",
        "cherries.png",
        "bell.png",
        "lucky7.png",
        "chip_bronze.png",
        "chip_gold.png",
        "chip_silver.png",
    ],
    "audio/music": [
        "title_theme.ogg",
        "hub_theme.ogg",
        "ski_theme.ogg",
        "pool_theme.ogg",
        "vegas_theme.ogg",
    ],
    "audio/sfx": [
        "menu_move.ogg",
        "menu_select.ogg",
        "jump.ogg",
        "attack.ogg",
        "collision.ogg",
    ],
}


def check_assets() -> tuple[list[str], list[str]]:
    """Check for missing and extra assets."""
    missing = []
    found = []

    # Check required assets
    for category, files in REQUIRED_ASSETS.items():
        category_path = ASSETS_DIR / category
        for filename in files:
            file_path = category_path / filename
            if file_path.exists():
                found.append(str(file_path.relative_to(PROJECT_ROOT)))
            else:
                missing.append(str(file_path.relative_to(PROJECT_ROOT)))

    return missing, found


def main():
    """Run asset check and report results."""
    print("Checking game assets...")
    print(f"Assets directory: {ASSETS_DIR}")
    print()

    missing, found = check_assets()

    # Report found assets
    if found:
        print(f"[OK] Found {len(found)} required assets:")
        for asset in sorted(found):
            print(f"   - {asset}")

    print()

    # Report missing assets
    if missing:
        print(f"[MISSING] Missing {len(missing)} required assets:")
        for asset in sorted(missing):
            print(f"   - {asset}")
        print()
        print("Tip: Missing assets will use placeholders during development")
        sys.exit(1)
    else:
        print("[SUCCESS] All required assets found!")

    # Check for extra assets (informational only)
    all_assets = []
    for root, dirs, files in os.walk(ASSETS_DIR):
        for file in files:
            if file.endswith((".png", ".ogg", ".mp3", ".wav")):
                path = Path(root) / file
                all_assets.append(str(path.relative_to(PROJECT_ROOT)))

    extra = set(all_assets) - set(found)
    if extra:
        print()
        print(f"[INFO] Found {len(extra)} additional assets (not required):")
        for asset in sorted(extra):
            print(f"   - {asset}")


if __name__ == "__main__":
    main()
