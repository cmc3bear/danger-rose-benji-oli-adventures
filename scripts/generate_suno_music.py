#!/usr/bin/env python3
"""Generate racing music for The Drive minigame using Suno API."""

import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any

# Suno API configuration
SUNO_API_BASE = "https://suno.gcui.ai"
API_KEY = "sk_ed822333d35b476ea444e7dd6f839227"  # From vault

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "audio" / "music" / "drive"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Track definitions
TRACKS = [
    {
        "id": "highway_dreams",
        "title": "Highway Dreams",
        "prompt": "Upbeat 80s synthwave racing music, energetic driving beat, nostalgic arcade vibes, catchy lead synth melody, 125 BPM, C major key, perfect for cruising down a sunset highway",
        "tags": "80s synthwave instrumental arcade racing upbeat nostalgic",
        "bpm": 125,
        "key": "C major",
        "mood": "energetic"
    },
    {
        "id": "sunset_cruise", 
        "title": "Sunset Cruise",
        "prompt": "Relaxed 80s chillwave driving music, smooth synthesizers, dreamy atmosphere, gentle rhythm, 108 BPM, G major key, perfect for scenic coastal drives",
        "tags": "80s chillwave instrumental relaxed dreamy synthpop",
        "bpm": 108,
        "key": "G major",
        "mood": "relaxed"
    },
    {
        "id": "turbo_rush",
        "title": "Turbo Rush",
        "prompt": "Intense 80s dark synthwave racing music, powerful bass, aggressive synths, fast-paced rhythm, 140 BPM, A minor key, adrenaline-pumping arcade action",
        "tags": "80s darkwave synthwave instrumental intense racing",
        "bpm": 140,
        "key": "A minor",
        "mood": "intense"
    }
]


def generate_music(track_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a music track using Suno API."""
    print(f"\n🎵 Generating: {track_info['title']}")
    print(f"   Style: {track_info['mood']} ({track_info['bpm']} BPM, {track_info['key']})")
    
    # Prepare request
    headers = {
        "Content-Type": "application/json",
        # Note: This API doesn't seem to use the API key in headers
    }
    
    payload = {
        "prompt": track_info["prompt"],
        "tags": track_info["tags"],
        "title": track_info["title"],
        "make_instrumental": True,  # No vocals for racing game
        "wait_audio": True  # Wait for generation to complete
    }
    
    try:
        # Make request to custom_generate endpoint for more control
        response = requests.post(
            f"{SUNO_API_BASE}/api/custom_generate",
            headers=headers,
            json=payload,
            timeout=120  # 2 minutes timeout for generation
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Generated successfully!")
            return data
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request error: {e}")
        return None


def download_audio(audio_url: str, output_path: Path) -> bool:
    """Download audio file from URL."""
    try:
        print(f"   📥 Downloading: {output_path.name}")
        response = requests.get(audio_url, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"   ✅ Downloaded: {output_path.name}")
            return True
        else:
            print(f"   ❌ Download failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Download error: {e}")
        return False


def check_api_limits():
    """Check API usage limits."""
    try:
        response = requests.get(f"{SUNO_API_BASE}/api/get_limit")
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 API Status:")
            print(f"   Credits used this month: {data.get('credits_used', 'Unknown')}")
            print(f"   Total credits available: {data.get('total_credits', 'Unknown')}")
            return True
    except:
        print("⚠️  Could not check API limits")
    return False


def main():
    """Generate all music tracks for The Drive minigame."""
    print("🎮 Danger Rose - The Drive Music Generator")
    print("==========================================")
    
    # Check API status
    check_api_limits()
    
    # Track results
    results = []
    manifest = {"tracks": []}
    
    # Generate each track
    for i, track in enumerate(TRACKS):
        print(f"\n[{i+1}/{len(TRACKS)}] Processing track...")
        
        # Generate music
        result = generate_music(track)
        
        if result and len(result) > 0:
            # Suno returns 2 versions, we'll take the first one
            audio_data = result[0]
            audio_url = audio_data.get("audio_url")
            
            if audio_url:
                # Download the audio
                output_file = OUTPUT_DIR / f"{track['id']}.mp3"
                if download_audio(audio_url, output_file):
                    # Update manifest
                    manifest_entry = {
                        "id": track["id"],
                        "title": track["title"],
                        "filename": f"{track['id']}.ogg",  # Will be converted
                        "bpm": track["bpm"],
                        "key": track["key"],
                        "mood": track["mood"],
                        "description": track["prompt"][:50] + "...",
                        "suno_id": audio_data.get("id", ""),
                        "duration": audio_data.get("duration", 0)
                    }
                    manifest["tracks"].append(manifest_entry)
                    results.append({
                        "track": track["title"],
                        "status": "✅ Success",
                        "file": str(output_file)
                    })
                else:
                    results.append({
                        "track": track["title"],
                        "status": "❌ Download failed"
                    })
            else:
                results.append({
                    "track": track["title"],
                    "status": "❌ No audio URL"
                })
        else:
            results.append({
                "track": track["title"],
                "status": "❌ Generation failed"
            })
        
        # Rate limiting - wait between requests
        if i < len(TRACKS) - 1:
            print("\n⏳ Waiting 10 seconds before next track...")
            time.sleep(10)
    
    # Save manifest
    manifest_path = OUTPUT_DIR / "music_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Print summary
    print("\n" + "="*50)
    print("📋 GENERATION SUMMARY")
    print("="*50)
    for result in results:
        print(f"{result['track']}: {result['status']}")
        if "file" in result:
            print(f"   📁 {result['file']}")
    
    print(f"\n📄 Manifest saved: {manifest_path}")
    
    # Conversion reminder
    print("\n⚠️  IMPORTANT: Convert MP3 files to OGG format:")
    print("   ffmpeg -i input.mp3 -c:a libvorbis -q:a 4 output.ogg")
    
    print("\n✅ Music generation complete!")


if __name__ == "__main__":
    main()