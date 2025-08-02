#!/usr/bin/env python3
"""Test audio in game context."""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import game components
from src.managers.sound_manager import SoundManager
from pathlib import Path

# Initialize sound manager
sound_manager = SoundManager()

print("=== Game Audio Test ===")
print(f"Master volume: {sound_manager.master_volume}")
print(f"Music volume: {sound_manager.music_volume}")
print(f"SFX volume: {sound_manager.sfx_volume}")
print()

# Test playing music directly
music_path = Path("assets/audio/music/drive/highway_dreams.mp3")
print(f"Testing: {music_path}")
print(f"File exists: {music_path.exists()}")

try:
    # Set volume
    sound_manager.set_music_volume(0.7)
    print(f"Set music volume to: {sound_manager.music_volume}")
    
    # Play music
    sound_manager.play_music(str(music_path), loops=-1)
    print("Music command sent")
    
    # Check if playing
    import pygame
    import time
    time.sleep(0.5)
    
    if pygame.mixer.music.get_busy():
        print("[OK] Music is playing!")
        print(f"Mixer volume: {pygame.mixer.music.get_volume()}")
    else:
        print("[ERROR] Music is NOT playing")
        
    # Let it play for a bit
    print("\nLetting music play for 3 seconds...")
    time.sleep(3)
    
    sound_manager.stop_music()
    print("Music stopped")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()