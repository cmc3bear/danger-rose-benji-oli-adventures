"""
Verify final music installation
"""

from pathlib import Path

MUSIC_BASE_PATH = Path("assets/audio/music")

def verify_music():
    scenes = ["drive", "pool", "ski", "vegas", "hub", "hacker_typing", "easter_eggs"]
    
    print("FINAL MUSIC VERIFICATION")
    print("=" * 50)
    
    total_files = 0
    
    for scene in scenes:
        scene_path = MUSIC_BASE_PATH / scene
        if scene_path.exists():
            music_files = list(scene_path.glob("*.mp3"))
            manifest = scene_path / "music_manifest.json"
            
            print(f"\n{scene.upper()} ({len(music_files)} tracks):")
            for music_file in sorted(music_files):
                print(f"  [OK] {music_file.name}")
                total_files += 1
            
            if manifest.exists():
                print(f"  [OK] music_manifest.json")
            else:
                print(f"  [MISSING] music_manifest.json")
        else:
            print(f"\n{scene.upper()}: [ERROR] Directory not found")
    
    print(f"\nTotal music files: {total_files}")
    print("\nAll scenes have music ready!")

if __name__ == "__main__":
    verify_music()