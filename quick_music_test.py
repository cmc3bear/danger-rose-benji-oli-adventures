"""
Quick test to check if any of the drive music files work
"""

import pygame
import sys
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

music_files = [
    "assets/audio/music/drive/highway_dreams.mp3",
    "assets/audio/music/drive/sunset_cruise.mp3", 
    "assets/audio/music/drive/turbo_rush.mp3"
]

print("Testing drive music files...")

for music_file in music_files:
    print(f"\nTesting: {music_file}")
    
    if not os.path.exists(music_file):
        print("  File not found!")
        continue
        
    try:
        pygame.mixer.music.load(music_file)
        print("  Loaded successfully!")
        
        pygame.mixer.music.play(0)  # Play once
        print("  Started playing...")
        
        # Let it play for 2 seconds
        pygame.time.wait(2000)
        
        pygame.mixer.music.stop()
        print("  Stopped successfully!")
        
        print(f"  ✅ {os.path.basename(music_file)} works!")
        
    except Exception as e:
        print(f"  ❌ Error with {os.path.basename(music_file)}: {e}")

print("\nMusic test completed!")
pygame.quit()