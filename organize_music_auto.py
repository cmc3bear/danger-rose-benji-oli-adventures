"""
Automatic music file organization script
"""

import os
import shutil
import json
from pathlib import Path
import pygame

# Initialize pygame for testing
pygame.init()
pygame.mixer.init()

# Base paths
DOWNLOADS_PATH = Path("assets/downloads/music")
MUSIC_BASE_PATH = Path("assets/audio/music")

# Create scene mappings based on file naming
SCENE_MAPPINGS = {
    "thedrive": "drive",
    "the drive": "drive",
    "pool": "pool",
    "ski": "ski",
    "vegas": "vegas",
    "hub": "hub",
    "typingtutor": "hacker_typing",
    "easteregg": "easter_eggs",
    "easeteregg": "easter_eggs",  # typo in filename
    "eastergg": "easter_eggs",
    "-easteregg": "easter_eggs"  # handle dash prefix
}

def clean_filename(filename):
    """Clean up filename for consistency"""
    # Remove scene suffix and clean up
    name = filename.replace(".mp3", "")
    
    # Extract title and scene
    parts = name.split(" - ")
    if len(parts) == 2:
        title, scene = parts
        return title.strip(), scene.strip().lower()
    return name, "unknown"

def test_music_file(filepath):
    """Test if a music file can be loaded and played"""
    try:
        pygame.mixer.music.load(str(filepath))
        return True
    except Exception as e:
        print(f"  [ERROR] {filepath.name} - Error: {e}")
        return False

def organize_music_files():
    """Organize music files into proper directories"""
    
    if not DOWNLOADS_PATH.exists():
        print(f"Downloads path not found: {DOWNLOADS_PATH}")
        return
    
    # Get all MP3 files
    music_files = list(DOWNLOADS_PATH.glob("*.mp3"))
    print(f"Found {len(music_files)} music files to organize\n")
    
    # Test all files first
    print("Validating music files...")
    valid_files = []
    for music_file in music_files:
        if test_music_file(music_file):
            valid_files.append(music_file)
            print(f"  [OK] {music_file.name}")
    
    print(f"\n{len(valid_files)} out of {len(music_files)} files are valid\n")
    
    # Organize files by scene
    organized = {}
    skipped = []
    
    for music_file in valid_files:
        title, scene_tag = clean_filename(music_file.name)
        
        # Map to proper scene directory
        scene_dir = SCENE_MAPPINGS.get(scene_tag, scene_tag)
        if scene_dir == "unknown":
            # Try to fix the Banana Beat Drop issue
            if "easteregg" in music_file.name.lower():
                scene_dir = "easter_eggs"
                title = music_file.name.split(".mp3")[0].strip()
            else:
                skipped.append(music_file.name)
                continue
            
        if scene_dir not in organized:
            organized[scene_dir] = []
        
        organized[scene_dir].append({
            "file": music_file,
            "title": title,
            "scene": scene_dir,
            "original_name": music_file.name
        })
    
    if skipped:
        print("Skipped files (unknown scene):")
        for name in skipped:
            print(f"  - {name}")
        print()
    
    # Execute the organization
    print("Copying files to scene directories...")
    copied_count = 0
    
    for scene, files in organized.items():
        scene_path = MUSIC_BASE_PATH / scene
        
        # Create directory if it doesn't exist
        scene_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{scene.upper()} -> {scene_path}")
        
        for file_info in files:
            source = file_info["file"]
            # Clean up filename - remove parentheses and special chars
            clean_title = file_info["title"].lower()
            clean_title = clean_title.replace("(", "").replace(")", "")
            clean_title = clean_title.replace(" - ", "_").replace(" ", "_")
            clean_title = clean_title.replace("__", "_").strip("_")
            
            new_filename = clean_title + ".mp3"
            destination = scene_path / new_filename
            
            try:
                shutil.copy2(source, destination)
                print(f"  [OK] {source.name} -> {new_filename}")
                copied_count += 1
            except Exception as e:
                print(f"  [ERROR] {source.name}: {e}")
    
    print(f"\nCopied {copied_count} files successfully")
    
    # Clean up corrupted drive music files
    print("\nCleaning up old corrupted music files...")
    old_drive_files = ["highway_dreams.mp3", "sunset_cruise.mp3", "turbo_rush.mp3"]
    drive_path = MUSIC_BASE_PATH / "drive"
    
    for old_file in old_drive_files:
        old_path = drive_path / old_file
        if old_path.exists():
            try:
                os.remove(old_path)
                print(f"  [OK] Removed old {old_file}")
            except Exception as e:
                print(f"  [ERROR] Could not remove {old_file}: {e}")
    
    return organized

def create_music_manifests(organized_files):
    """Create music manifest files for each scene"""
    
    print("\nCreating music manifests...")
    
    for scene, files in organized_files.items():
        scene_path = MUSIC_BASE_PATH / scene
        manifest_path = scene_path / "music_manifest.json"
        
        # Create track entries
        tracks = []
        for file_info in files:
            # Use the same clean filename logic
            clean_title = file_info["title"].lower()
            clean_title = clean_title.replace("(", "").replace(")", "")
            clean_title = clean_title.replace(" - ", "_").replace(" ", "_")
            clean_title = clean_title.replace("__", "_").strip("_")
            filename = clean_title + ".mp3"
            
            # Determine track properties based on title
            track = {
                "name": filename.replace(".mp3", ""),
                "display_name": file_info["title"],
                "description": f"Music for {scene} scene",
                "filename": filename,
                "bpm": 120,  # Default, can be updated
                "mood": "energetic",
                "preview_start": 10.0
            }
            
            # Customize based on title keywords
            if "frenzy" in file_info["title"].lower():
                track["bpm"] = 140
                track["mood"] = "intense"
            elif "cruise" in file_info["title"].lower():
                track["bpm"] = 100
                track["mood"] = "relaxed"
            elif "victory" in file_info["title"].lower():
                track["mood"] = "triumphant"
            elif "showdown" in file_info["title"].lower():
                track["bpm"] = 125
                track["mood"] = "competitive"
                
            tracks.append(track)
        
        # Create manifest
        manifest = {
            "scene": scene,
            "tracks": tracks,
            "default_track": tracks[0]["name"] if tracks else None
        }
        
        # Write manifest
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"  [OK] Created manifest for {scene} with {len(tracks)} tracks")

def test_new_drive_music():
    """Quick test of the new drive music files"""
    
    print("\nTesting new drive music...")
    drive_path = MUSIC_BASE_PATH / "drive"
    
    if not drive_path.exists():
        print("  Drive music directory not found")
        return
        
    music_files = list(drive_path.glob("*.mp3"))
    
    for music_file in music_files:
        try:
            pygame.mixer.music.load(str(music_file))
            print(f"  [OK] {music_file.name} loads correctly")
        except Exception as e:
            print(f"  [ERROR] {music_file.name}: {e}")

if __name__ == "__main__":
    print("Automatic Music File Organization")
    print("=" * 60)
    
    # Organize files
    organized = organize_music_files()
    
    if organized:
        # Create manifests
        create_music_manifests(organized)
        
        # Test drive music
        test_new_drive_music()
        
        print("\n[SUCCESS] Music organization complete!")
        print("\nWhat was done:")
        print("1. Copied all valid music files to appropriate scene directories")
        print("2. Created music manifests for each scene")
        print("3. Removed old corrupted drive music files")
        print("4. Tested new drive music files")
        
        print("\nThe game should now have working music!")
    else:
        print("\n[ERROR] No files were organized")
    
    pygame.quit()