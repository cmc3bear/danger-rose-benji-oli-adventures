"""
Quick test to verify hub music works
"""

import pygame
import json
from pathlib import Path

pygame.init()
pygame.mixer.init()

# Test hub music
hub_path = Path("assets/audio/music/hub")
manifest_path = hub_path / "music_manifest.json"

print("Testing Hub Music")
print("=" * 40)

# Load manifest
with open(manifest_path, 'r') as f:
    manifest = json.load(f)

print(f"Found {len(manifest['tracks'])} tracks in hub manifest:")

# Test each track
for track in manifest['tracks']:
    music_file = hub_path / track['filename']
    print(f"\nTesting: {track['display_name']}")
    print(f"  File: {track['filename']}")
    
    try:
        pygame.mixer.music.load(str(music_file))
        print("  [OK] Loaded successfully!")
        
        # Play for 1 second
        pygame.mixer.music.play(0)
        pygame.time.wait(1000)
        pygame.mixer.music.stop()
        
    except Exception as e:
        print(f"  [ERROR] {e}")

print("\nHub music test complete!")
pygame.quit()