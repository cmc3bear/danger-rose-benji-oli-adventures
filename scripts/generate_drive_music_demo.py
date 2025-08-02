#!/usr/bin/env python3
"""Generate racing music for The Drive using the public Suno demo API."""

import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, List
import subprocess

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "audio" / "music" / "drive"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Track definitions for The Drive minigame
TRACKS = [
    {
        "id": "highway_dreams",
        "title": "Highway Dreams", 
        "prompt": "[Instrumental] Upbeat 80s synthwave racing music with energetic driving beat and nostalgic arcade vibes. Catchy lead synth melody perfect for cruising down a sunset highway. No vocals, pure instrumental energy.",
        "tags": "80s synthwave instrumental arcade racing upbeat nostalgic outrun",
        "bpm": 125,
        "key": "C major",
        "mood": "energetic",
        "description": "Main racing theme"
    },
    {
        "id": "sunset_cruise",
        "title": "Sunset Cruise",
        "prompt": "[Instrumental] Relaxed 80s chillwave driving music with smooth synthesizers and dreamy atmosphere. Gentle rhythm perfect for scenic coastal drives. No vocals, pure instrumental relaxation.",
        "tags": "80s chillwave instrumental relaxed dreamy synthpop cruising",
        "bpm": 108,
        "key": "G major", 
        "mood": "relaxed",
        "description": "Peaceful cruising music"
    },
    {
        "id": "turbo_rush",
        "title": "Turbo Rush",
        "prompt": "[Instrumental] Intense 80s dark synthwave racing music with powerful bass and aggressive synths. Fast-paced rhythm for adrenaline-pumping arcade action. No vocals, pure instrumental intensity.",
        "tags": "80s darkwave synthwave instrumental intense racing outrun",
        "bpm": 140,
        "key": "A minor",
        "mood": "intense", 
        "description": "High-energy racing"
    }
]


def generate_music_demo(track_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate music using the demo API (no auth required)."""
    print(f"\nGenerating: {track_info['title']}")
    print(f"   Style: {track_info['mood']} ({track_info['bpm']} BPM, {track_info['key']})")
    
    # Use the custom_generate endpoint for better control
    url = "https://suno.gcui.ai/api/custom_generate"
    
    payload = {
        "prompt": track_info["prompt"],
        "tags": track_info["tags"], 
        "title": track_info["title"],
        "make_instrumental": True,
        "wait_audio": False  # We'll poll for completion
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        # Submit generation request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Generation started! IDs: {[d.get('id') for d in data]}")
            return data
        else:
            print(f"   [ERROR] Error: {response.status_code} - {response.text[:200]}")
            return []
            
    except Exception as e:
        print(f"   [ERROR] Request error: {e}")
        return []


def poll_for_completion(track_ids: List[str], max_wait: int = 120) -> List[Dict[str, Any]]:
    """Poll the API until tracks are complete."""
    print("   Waiting for generation to complete...")
    
    start_time = time.time()
    url = "https://suno.gcui.ai/api/get"
    
    while time.time() - start_time < max_wait:
        try:
            # Check status
            params = {"ids": ",".join(track_ids)}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                tracks = response.json()
                
                # Check if all tracks are complete
                all_complete = all(
                    track.get("status") == "complete" and track.get("audio_url")
                    for track in tracks
                )
                
                if all_complete:
                    print("   [OK] Generation complete!")
                    return tracks
                else:
                    # Show progress
                    statuses = [track.get("status", "unknown") for track in tracks]
                    print(f"   Status: {statuses[0]}", end="\r")
            
        except Exception as e:
            print(f"   [WARNING] Poll error: {e}")
        
        time.sleep(5)  # Wait 5 seconds between polls
    
    print("   [TIMEOUT] Timeout waiting for completion")
    return []


def download_and_convert(audio_url: str, output_path: Path) -> bool:
    """Download MP3 and convert to OGG."""
    try:
        # Download MP3
        mp3_path = output_path.with_suffix('.mp3')
        print(f"   Downloading: {mp3_path.name}")
        
        response = requests.get(audio_url, stream=True, timeout=60)
        if response.status_code == 200:
            with open(mp3_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"   [OK] Downloaded: {mp3_path.name}")
            
            # Convert to OGG
            ogg_path = output_path.with_suffix('.ogg')
            print(f"   Converting to OGG...")
            
            # Try to use ffmpeg if available
            try:
                subprocess.run([
                    'ffmpeg', '-i', str(mp3_path), 
                    '-c:a', 'libvorbis', '-q:a', '6',
                    '-y', str(ogg_path)
                ], capture_output=True, check=True)
                
                # Remove MP3 after successful conversion
                mp3_path.unlink()
                print(f"   [OK] Converted: {ogg_path.name}")
                return True
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"   [WARNING] FFmpeg not available, keeping MP3 format")
                # Rename MP3 to match expected filename
                mp3_path.rename(output_path.with_suffix('.mp3'))
                return True
        else:
            print(f"   [ERROR] Download failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False


def main():
    """Generate all music tracks for The Drive minigame."""
    print("Danger Rose - The Drive Music Generator")
    print("==========================================")
    print("Using public Suno demo API")
    print()
    
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("[OK] FFmpeg detected - will convert to OGG format")
    except:
        print("[WARNING] FFmpeg not found - will save as MP3")
    
    results = []
    manifest = {"tracks": []}
    
    # Generate each track
    for i, track in enumerate(TRACKS):
        print(f"\n[{i+1}/{len(TRACKS)}] Processing: {track['title']}")
        
        # Generate music
        generation_result = generate_music_demo(track)
        
        if generation_result:
            # Get track IDs
            track_ids = [item.get("id") for item in generation_result if item.get("id")]
            
            if track_ids:
                # Poll for completion
                completed_tracks = poll_for_completion(track_ids)
                
                if completed_tracks and completed_tracks[0].get("audio_url"):
                    # Download and convert the first version
                    audio_url = completed_tracks[0]["audio_url"]
                    output_file = OUTPUT_DIR / track["id"]
                    
                    if download_and_convert(audio_url, output_file):
                        # Determine actual file extension
                        if (output_file.with_suffix('.ogg')).exists():
                            filename = f"{track['id']}.ogg"
                        else:
                            filename = f"{track['id']}.mp3"
                        
                        # Update manifest
                        manifest_entry = {
                            "id": track["id"],
                            "title": track["title"],
                            "filename": filename,
                            "bpm": track["bpm"],
                            "key": track["key"],
                            "mood": track["mood"],
                            "description": track["description"]
                        }
                        manifest["tracks"].append(manifest_entry)
                        
                        results.append({
                            "track": track["title"],
                            "status": "[OK] Success",
                            "file": filename
                        })
                    else:
                        results.append({
                            "track": track["title"],
                            "status": "[ERROR] Download failed"
                        })
                else:
                    results.append({
                        "track": track["title"],
                        "status": "[ERROR] Generation incomplete"
                    })
            else:
                results.append({
                    "track": track["title"],
                    "status": "[ERROR] No track IDs"
                })
        else:
            results.append({
                "track": track["title"],
                "status": "[ERROR] Generation failed"
            })
        
        # Rate limiting
        if i < len(TRACKS) - 1:
            print("\nWaiting 15 seconds before next track...")
            time.sleep(15)
    
    # Save manifest
    manifest_path = OUTPUT_DIR / "music_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Print summary
    print("\n" + "="*50)
    print("GENERATION SUMMARY")
    print("="*50)
    for result in results:
        print(f"{result['track']}: {result['status']}")
        if result.get("file"):
            print(f"   File: {OUTPUT_DIR / result['file']}")
    
    print(f"\nManifest saved: {manifest_path}")
    print("\n[OK] Music generation complete!")
    print("\nThe tracks are ready to use in The Drive minigame!")


if __name__ == "__main__":
    main()