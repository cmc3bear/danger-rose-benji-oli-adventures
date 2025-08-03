"""
Script to organize and integrate new music files into the game
Moves files from downloads/music to appropriate scene directories
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
        print(f"  [OK] {filepath.name} - Valid MP3")
        return True
    except Exception as e:
        print(f"  [ERROR] {filepath.name} - Error: {e}")
        return False

def organize_music_files(dry_run=True):
    """Organize music files into proper directories"""
    
    if not DOWNLOADS_PATH.exists():
        print(f"Downloads path not found: {DOWNLOADS_PATH}")
        return
    
    # Get all MP3 files
    music_files = list(DOWNLOADS_PATH.glob("*.mp3"))
    print(f"Found {len(music_files)} music files to organize\n")
    
    # Test all files first
    print("Testing music files...")
    valid_files = []
    for music_file in music_files:
        if test_music_file(music_file):
            valid_files.append(music_file)
    
    print(f"\n{len(valid_files)} out of {len(music_files)} files are valid\n")
    
    # Organize files by scene
    organized = {}
    for music_file in valid_files:
        title, scene_tag = clean_filename(music_file.name)
        
        # Map to proper scene directory
        scene_dir = SCENE_MAPPINGS.get(scene_tag, scene_tag)
        if scene_dir == "unknown":
            print(f"Warning: Could not determine scene for {music_file.name}")
            continue
            
        if scene_dir not in organized:
            organized[scene_dir] = []
        
        organized[scene_dir].append({
            "file": music_file,
            "title": title,
            "scene": scene_dir,
            "original_name": music_file.name
        })
    
    # Display organization plan
    print("Organization Plan:")
    print("=" * 60)
    
    for scene, files in organized.items():
        scene_path = MUSIC_BASE_PATH / scene
        print(f"\n{scene.upper()} ({scene_path}):")
        
        for file_info in files:
            new_filename = file_info["title"].lower().replace(" ", "_") + ".mp3"
            print(f"  {file_info['original_name']}")
            print(f"    -> {new_filename}")
    
    if dry_run:
        print("\n[DRY RUN] No files moved. Run with dry_run=False to execute.")
        return organized
    
    # Execute the organization
    print("\nMoving files...")
    for scene, files in organized.items():
        scene_path = MUSIC_BASE_PATH / scene
        
        # Create directory if it doesn't exist
        scene_path.mkdir(parents=True, exist_ok=True)
        
        for file_info in files:
            source = file_info["file"]
            new_filename = file_info["title"].lower().replace(" ", "_") + ".mp3"
            destination = scene_path / new_filename
            
            try:
                shutil.copy2(source, destination)
                print(f"  [OK] Copied {source.name} -> {destination}")
            except Exception as e:
                print(f"  [ERROR] Error copying {source.name}: {e}")
    
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
            filename = file_info["title"].lower().replace(" ", "_") + ".mp3"
            
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
                
            tracks.append(track)
        
        # Create manifest
        manifest = {
            "scene": scene,
            "tracks": tracks,
            "default_track": tracks[0]["name"] if tracks else None
        }
        
        # Write manifest
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"  [OK] Created manifest for {scene} with {len(tracks)} tracks")

def update_drive_music_selector():
    """Update the drive scene to use the new music files"""
    
    drive_manifest_path = MUSIC_BASE_PATH / "drive" / "music_manifest.json"
    
    if drive_manifest_path.exists():
        with open(drive_manifest_path, 'r') as f:
            manifest = json.load(f)
        
        print("\nDrive scene music updated:")
        for track in manifest["tracks"]:
            print(f"  - {track['display_name']} ({track['filename']})")
    else:
        print("\nNo drive music manifest found")

if __name__ == "__main__":
    print("Music File Organization Tool")
    print("=" * 60)
    
    # First, do a dry run
    organized = organize_music_files(dry_run=True)
    
    if organized:
        print("\n" + "=" * 60)
        response = input("\nProceed with file organization? (y/n): ")
        
        if response.lower() == 'y':
            # Execute the organization
            organized = organize_music_files(dry_run=False)
            
            # Create manifests
            create_music_manifests(organized)
            
            # Update drive scene
            update_drive_music_selector()
            
            print("\n[SUCCESS] Music organization complete!")
            print("\nNext steps:")
            print("1. Test the game to verify music plays correctly")
            print("2. Update BPM values in manifests for rhythm sync")
            print("3. Configure music selection UI for each scene")
        else:
            print("\nOrganization cancelled.")
    
    pygame.quit()