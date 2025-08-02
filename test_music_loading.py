#!/usr/bin/env python3
"""Test music loading directly."""

import pygame
from pathlib import Path

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Test paths
music_dir = Path("assets/audio/music/drive")
print(f"Music directory: {music_dir.absolute()}")
print(f"Directory exists: {music_dir.exists()}")
print()

# List MP3 files
print("MP3 files found:")
for mp3 in music_dir.glob("*.mp3"):
    print(f"  - {mp3.name} ({mp3.stat().st_size / 1024:.1f} KB)")
print()

# Test loading each file
print("Testing music loading:")
for mp3 in music_dir.glob("*.mp3"):
    try:
        print(f"\n{mp3.name}:")
        
        # Test loading
        pygame.mixer.music.load(str(mp3))
        print("  [OK] Loaded successfully")
        
        # Test playing
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(0)
        print("  [OK] Play command sent")
        
        # Wait a moment
        pygame.time.wait(500)
        
        if pygame.mixer.music.get_busy():
            print("  [OK] Music is playing")
        else:
            print("  [ERROR] Music is NOT playing")
            
        pygame.mixer.music.stop()
        
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

print("\n" + "="*50)

# Test the exact path the game would use
print("\nTesting game paths:")
test_filename = "highway_dreams.mp3"
game_path = Path(__file__).parent / "assets" / "audio" / "music" / "drive" / test_filename
print(f"Game would look for: {game_path}")
print(f"File exists: {game_path.exists()}")

# Test volume
print(f"\nCurrent music volume: {pygame.mixer.music.get_volume()}")

pygame.quit()