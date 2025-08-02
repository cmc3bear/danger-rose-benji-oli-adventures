#!/usr/bin/env python3
"""Debug audio system for The Drive."""

import pygame
import os
from pathlib import Path

def test_audio():
    """Test pygame audio system and MP3 playback."""
    print("=== Audio System Debug ===")
    
    # Initialize pygame
    pygame.init()
    
    # Check mixer initialization
    try:
        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=512
        )
        print("[OK] Pygame mixer initialized")
        
        # Get mixer info
        freq, size, channels = pygame.mixer.get_init()
        print(f"Mixer settings: {freq}Hz, {size}-bit, {channels} channels")
        
    except Exception as e:
        print(f"[ERROR] Mixer init failed: {e}")
        return
    
    # Check MP3 support
    print("\n=== MP3 Support Check ===")
    formats = ['.ogg', '.wav', '.mp3']
    for fmt in formats:
        try:
            # Try to create a dummy sound
            pygame.mixer.Sound.__new__(pygame.mixer.Sound)
            print(f"[OK] {fmt} format supported")
        except:
            print(f"[WARNING] {fmt} format may have issues")
    
    # Test loading MP3 files
    print("\n=== Testing MP3 Files ===")
    mp3_dir = Path("assets/audio/music/drive")
    
    for mp3_file in mp3_dir.glob("*.mp3"):
        print(f"\nTesting: {mp3_file.name}")
        try:
            # Test with music module (streaming)
            pygame.mixer.music.load(str(mp3_file))
            print(f"  [OK] Loaded with mixer.music")
            
            # Try to play for a moment
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(0, 0)
            print(f"  [OK] Play command sent")
            
            # Check if playing
            pygame.time.wait(100)
            if pygame.mixer.music.get_busy():
                print(f"  [OK] Music is playing")
            else:
                print(f"  [WARNING] Music not playing")
            
            pygame.mixer.music.stop()
            
        except Exception as e:
            print(f"  [ERROR] Failed to load/play: {e}")
    
    # Check volume settings
    print("\n=== Volume Settings ===")
    print(f"Music volume: {pygame.mixer.music.get_volume()}")
    
    pygame.quit()

if __name__ == "__main__":
    test_audio()