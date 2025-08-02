#!/usr/bin/env python3
"""Convert and setup the Drive minigame MP3 files."""

import os
import shutil
import json
from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).parent.parent

# Source MP3 files
MP3_FILES = [
    {
        "source": "Highway Dreams (Main Theme).mp3",
        "target": "highway_dreams.mp3",
        "id": "highway_dreams",
        "title": "Highway Dreams",
        "bpm": 125,
        "key": "C major",
        "mood": "energetic",
        "description": "Main racing theme"
    },
    {
        "source": "Sunset Cruise.mp3",
        "target": "sunset_cruise.mp3",
        "id": "sunset_cruise",
        "title": "Sunset Cruise",
        "bpm": 108,
        "key": "G major",
        "mood": "relaxed",
        "description": "Peaceful cruising music"
    },
    {
        "source": "Turbo Rush.mp3",
        "target": "turbo_rush.mp3",
        "id": "turbo_rush",
        "title": "Turbo Rush",
        "bpm": 140,
        "key": "A minor",
        "mood": "intense",
        "description": "High-energy racing"
    }
]

# Output directory
OUTPUT_DIR = ROOT_DIR / "assets" / "audio" / "music" / "drive"

def main():
    """Convert MP3s and set up Drive music."""
    print("Setting up Drive minigame music...")
    print("=" * 50)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Remove old placeholder WAV files
    print("\nRemoving old placeholder files...")
    for wav_file in OUTPUT_DIR.glob("*.wav"):
        wav_file.unlink()
        print(f"  Removed: {wav_file.name}")
    
    # Process each MP3
    success_count = 0
    manifest = {"tracks": []}
    
    for track_info in MP3_FILES:
        source_path = ROOT_DIR / track_info["source"]
        target_path = OUTPUT_DIR / track_info["target"]
        
        print(f"\nProcessing: {track_info['source']}")
        
        if source_path.exists():
            # Copy MP3 to target location
            shutil.copy2(source_path, target_path)
            print(f"  [OK] Copied to: {target_path.name}")
            
            # Add to manifest
            manifest_entry = {
                "id": track_info["id"],
                "title": track_info["title"],
                "filename": track_info["target"],
                "bpm": track_info["bpm"],
                "key": track_info["key"],
                "mood": track_info["mood"],
                "description": track_info["description"]
            }
            manifest["tracks"].append(manifest_entry)
            success_count += 1
        else:
            print(f"  [ERROR] Source file not found: {source_path}")
    
    # Update manifest
    manifest_path = OUTPUT_DIR / "music_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nManifest updated: {manifest_path}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"SETUP COMPLETE: {success_count}/{len(MP3_FILES)} tracks processed")
    
    if success_count == len(MP3_FILES):
        print("\n[OK] All tracks successfully set up!")
        print("\nThe Drive minigame is now using your custom MP3 files.")
        print("You can test it with: make run-drive")
    else:
        print("\n[WARNING] Some tracks failed to process.")
        print("Check the error messages above.")

if __name__ == "__main__":
    main()