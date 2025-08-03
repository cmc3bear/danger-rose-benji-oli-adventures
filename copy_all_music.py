"""
Script to ensure all music files are properly copied to their scene directories
"""

import os
import shutil
from pathlib import Path

# Base paths
DOWNLOADS_PATH = Path("assets/downloads/music")
MUSIC_BASE_PATH = Path("assets/audio/music")

# Music file mappings
MUSIC_MAPPINGS = {
    # Pool scene
    "Splashdown Showdown - pool.mp3": ("pool", "splashdown_showdown.mp3"),
    "Victory Splash Anthem - pool.mp3": ("pool", "victory_splash_anthem.mp3"),
    "Water Balloon Warriors - pool.mp3": ("pool", "water_balloon_warriors.mp3"),
    
    # Ski scene
    "Frostbite Frenzy - ski.mp3": ("ski", "frostbite_frenzy.mp3"),
    "Pixel Peaks Victory - ski.mp3": ("ski", "pixel_peaks_victory.mp3"),
    "Snow Rush Showdown - ski.mp3": ("ski", "snow_rush_showdown.mp3"),
    
    # Vegas scene
    "Battle on the Strip - vegas.mp3": ("vegas", "battle_on_the_strip.mp3"),
    "Las Vegas Lights Up - vegas.mp3": ("vegas", "las_vegas_lights_up.mp3"),
    "Neon Fury - vegas.mp3": ("vegas", "neon_fury.mp3"),
    
    # Hub scene
    "Code Breaker - hub.mp3": ("hub", "code_breaker.mp3"),
    "Debug Mode - hub.mp3": ("hub", "debug_mode.mp3"),
    "Git Push Glory - hub.mp3": ("hub", "git_push_glory.mp3"),
    
    # Hacker Typing scene
    "Dungeon Runners - typingtutor.mp3": ("hacker_typing", "dungeon_runners.mp3"),
    "Pixel Escape - typingtutor.mp3": ("hacker_typing", "pixel_escape.mp3"),
    
    # Easter eggs
    "Banana Beat Drop -easteregg.mp3": ("easter_eggs", "banana_beat_drop.mp3"),
    "Banana Beat Frenzy - easeteregg.mp3": ("easter_eggs", "banana_beat_frenzy.mp3"),
    "Midnight Compiler - eastergg.mp3": ("easter_eggs", "midnight_compiler.mp3"),
}

def copy_music_files():
    """Copy all music files to their proper directories"""
    
    copied = 0
    errors = 0
    
    for source_file, (scene_dir, dest_filename) in MUSIC_MAPPINGS.items():
        source_path = DOWNLOADS_PATH / source_file
        dest_dir = MUSIC_BASE_PATH / scene_dir
        dest_path = dest_dir / dest_filename
        
        # Create directory if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        if source_path.exists():
            try:
                shutil.copy2(source_path, dest_path)
                print(f"[OK] Copied {source_file} -> {scene_dir}/{dest_filename}")
                copied += 1
            except Exception as e:
                print(f"[ERROR] Failed to copy {source_file}: {e}")
                errors += 1
        else:
            print(f"[MISSING] Source file not found: {source_file}")
            errors += 1
    
    return copied, errors

def verify_music_files():
    """Verify all music files are in place"""
    
    print("\nVerifying music files in each scene...")
    
    scenes = ["drive", "pool", "ski", "vegas", "hub", "hacker_typing", "easter_eggs"]
    
    for scene in scenes:
        scene_path = MUSIC_BASE_PATH / scene
        if scene_path.exists():
            music_files = list(scene_path.glob("*.mp3"))
            manifest = scene_path / "music_manifest.json"
            
            print(f"\n{scene.upper()}:")
            print(f"  Music files: {len(music_files)}")
            for music_file in sorted(music_files):
                print(f"    - {music_file.name}")
            
            if manifest.exists():
                print(f"  Manifest: Present")
            else:
                print(f"  Manifest: Missing")
        else:
            print(f"\n{scene.upper()}: Directory not found")

if __name__ == "__main__":
    print("Music File Copy Script")
    print("=" * 50)
    
    # Copy all music files
    copied, errors = copy_music_files()
    
    print(f"\nSummary:")
    print(f"  Files copied: {copied}")
    print(f"  Errors: {errors}")
    
    # Verify installation
    verify_music_files()
    
    print("\nDone!")