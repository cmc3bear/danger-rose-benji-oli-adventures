"""
Clean up duplicate music files and ensure proper naming
"""

import os
from pathlib import Path

MUSIC_BASE_PATH = Path("assets/audio/music")

# Define which files to keep and which to remove
CLEANUP_RULES = {
    "pool": {
        "keep": ["splashdown_showdown.mp3", "victory_splash_anthem.mp3", "water_balloon_warriors.mp3"],
        "remove": ["Splashdown Showdown.mp3", "Victory Splash Anthem.mp3", "Water Balloon Warriors.mp3"]
    },
    "ski": {
        "keep": ["frostbite_frenzy.mp3", "pixel_peaks_victory.mp3", "snow_rush_showdown.mp3"],
        "remove": ["Frostbite Frenzy.mp3", "Pixel Peaks Victory.mp3", "Snow Rush Showdown.mp3"]
    },
    "vegas": {
        "keep": ["battle_on_the_strip.mp3", "las_vegas_lights_up.mp3", "neon_fury.mp3"],
        "remove": ["Battle on the Strip.mp3", "Neon Fury.mp3"]
    },
    "hub": {
        "keep": ["code_breaker.mp3", "debug_mode.mp3", "git_push_glory.mp3"],
        "remove": ["Code Breaker.mp3", "Debug Mode.mp3", "Debug Mode Redux.mp3"]
    },
    "easter_eggs": {
        "keep": ["banana_beat_drop.mp3", "banana_beat_frenzy.mp3", "midnight_compiler.mp3"],
        "remove": ["banana_beat_drop_-easteregg.mp3"]
    }
}

def cleanup_duplicates():
    """Remove duplicate music files"""
    
    removed_count = 0
    
    for scene, rules in CLEANUP_RULES.items():
        scene_path = MUSIC_BASE_PATH / scene
        
        if not scene_path.exists():
            continue
            
        print(f"\nCleaning {scene.upper()}:")
        
        # Remove duplicates
        for file_to_remove in rules["remove"]:
            file_path = scene_path / file_to_remove
            if file_path.exists():
                try:
                    os.remove(file_path)
                    print(f"  [REMOVED] {file_to_remove}")
                    removed_count += 1
                except Exception as e:
                    print(f"  [ERROR] Could not remove {file_to_remove}: {e}")
        
        # Verify kept files exist
        for file_to_keep in rules["keep"]:
            file_path = scene_path / file_to_keep
            if file_path.exists():
                print(f"  [OK] {file_to_keep}")
            else:
                print(f"  [MISSING] {file_to_keep}")
    
    return removed_count

def verify_final_state():
    """Show final state of music directories"""
    
    print("\n" + "=" * 50)
    print("FINAL MUSIC FILE STATE:")
    print("=" * 50)
    
    scenes = ["drive", "pool", "ski", "vegas", "hub", "hacker_typing", "easter_eggs"]
    
    total_files = 0
    
    for scene in scenes:
        scene_path = MUSIC_BASE_PATH / scene
        if scene_path.exists():
            music_files = list(scene_path.glob("*.mp3"))
            manifest = scene_path / "music_manifest.json"
            
            print(f"\n{scene.upper()} ({len(music_files)} tracks):")
            for music_file in sorted(music_files):
                print(f"  ✓ {music_file.name}")
                total_files += 1
            
            if not manifest.exists():
                print(f"  ⚠ Missing manifest!")
        else:
            print(f"\n{scene.upper()}: ✗ Directory not found")
    
    print(f"\nTotal music files: {total_files}")

if __name__ == "__main__":
    print("Music Duplicate Cleanup")
    print("=" * 50)
    
    # Clean up duplicates
    removed = cleanup_duplicates()
    
    print(f"\nRemoved {removed} duplicate files")
    
    # Show final state
    verify_final_state()