#!/usr/bin/env python3
"""Create placeholder music files for the Drive minigame to prevent crashes."""

import os
from pathlib import Path

def create_placeholder_music():
    """Create empty placeholder music files for missing Drive game tracks."""
    
    # Get the music directory
    project_root = Path(__file__).parent.parent
    music_dir = project_root / "assets" / "audio" / "music" / "drive"
    
    # Ensure directory exists
    music_dir.mkdir(parents=True, exist_ok=True)
    
    # List of required music files
    required_files = [
        "highway_dreams.mp3",
        "sunset_cruise.mp3", 
        "turbo_rush.mp3"
    ]
    
    # Create placeholder files
    for filename in required_files:
        filepath = music_dir / filename
        if not filepath.exists():
            print(f"Creating placeholder: {filepath}")
            # Create an empty file
            filepath.touch()
        else:
            print(f"File already exists: {filepath}")
    
    # Also create placeholder stinger files
    sfx_dir = project_root / "assets" / "audio" / "sfx" / "drive" / "stingers"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    
    stinger_files = [
        "stinger_crash.ogg",
        "stinger_boost.ogg",
        "stinger_victory.ogg",
        "stinger_final_lap.ogg",
        "stinger_position_up.ogg",
        "stinger_position_down.ogg"
    ]
    
    for filename in stinger_files:
        filepath = sfx_dir / filename
        if not filepath.exists():
            print(f"Creating placeholder: {filepath}")
            filepath.touch()
        else:
            print(f"File already exists: {filepath}")
    
    print("\nPlaceholder music files created successfully!")
    print("Note: These are empty files to prevent crashes.")
    print("Replace with actual music files when available.")

if __name__ == "__main__":
    create_placeholder_music()