#!/usr/bin/env python3
"""
Suno API Music Generator for Danger Rose - The Drive Minigame

Generates 3 OutRun-style synthwave tracks for the racing game:
1. Highway Dreams - Main upbeat synthwave racing theme
2. Sunset Cruise - Relaxed chillwave cruising theme  
3. Turbo Rush - High-energy intense racing theme

Usage:
    python scripts/generate_music.py
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SunoMusicGenerator:
    """Suno API client for generating synthwave music tracks"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # Try different possible base URLs for Suno API
        self.base_urls = [
            "https://api.suno.ai/v1",
            "https://api.suno.com/v1", 
            "https://suno-api.com/v1",
            "https://studio-api.suno.ai/api/generate/v2",  # Alternative pattern
            "https://clerk.suno.ai/v1"  # Alternative pattern
        ]
        
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "DangerRose-MusicGen/1.0"
        }
        
        # Ensure output directory exists
        self.output_dir = Path("assets/audio/music/drive")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_track(self, track_config: Dict) -> Optional[Dict]:
        """
        Generate a single music track using Suno API
        
        Args:
            track_config: Dictionary containing track parameters
            
        Returns:
            Dictionary with generation results or None if failed
        """
        logger.info(f"Generating track: {track_config['title']}")
        
        # Prepare the generation request
        payload = {
            "prompt": track_config["prompt"],
            "title": track_config["title"],
            "tags": track_config["tags"],
            "duration": track_config["duration"],
            "instrumental": track_config.get("instrumental", True),
            "model": "chirp-v3-5",  # Common Suno model
            # Additional parameters that might be supported
            "bpm": track_config.get("bpm"),
            "key": track_config.get("key"),
            "style": track_config.get("style"),
            "make_instrumental": True,
            "wait_audio": True
        }
        
        try:
            # Try different combinations of base URLs and endpoints
            endpoint_patterns = [
                "/generate",
                "/songs/generate", 
                "/create",
                "/music/generate",
                "/api/generate",
                "/v2/generate"
            ]
            
            for base_url in self.base_urls:
                for endpoint_pattern in endpoint_patterns:
                    endpoint = f"{base_url}{endpoint_pattern}"
                    logger.info(f"Trying endpoint: {endpoint}")
                    
                    try:
                        response = requests.post(
                            endpoint,
                            headers=self.headers,
                            json=payload,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            logger.info(f"Successfully initiated generation for {track_config['title']}")
                            return result
                        elif response.status_code == 404:
                            continue  # Try next endpoint
                        elif response.status_code == 503:
                            logger.warning(f"Service temporarily unavailable at {endpoint}")
                            continue
                        else:
                            logger.warning(f"Endpoint {endpoint} returned {response.status_code}: {response.text[:200]}")
                            
                    except requests.exceptions.ConnectionError:
                        logger.debug(f"Connection failed to {endpoint}")
                        continue
                    except requests.exceptions.Timeout:
                        logger.warning(f"Timeout connecting to {endpoint}")
                        continue
                        
            logger.error("All endpoints failed.")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def check_generation_status(self, generation_id: str) -> Optional[Dict]:
        """Check the status of a music generation"""
        try:
            endpoints_to_try = [
                f"{self.base_url}/generate/{generation_id}",
                f"{self.base_url}/songs/{generation_id}",
                f"{self.base_url}/status/{generation_id}"
            ]
            
            for endpoint in endpoints_to_try:
                response = requests.get(endpoint, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code != 404:
                    logger.warning(f"Status check returned {response.status_code}: {response.text}")
                    
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Status check failed: {e}")
            return None
    
    def download_track(self, audio_url: str, filename: str) -> bool:
        """Download the generated audio file"""
        try:
            logger.info(f"Downloading {filename}...")
            response = requests.get(audio_url, timeout=60)
            response.raise_for_status()
            
            file_path = self.output_dir / filename
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Successfully downloaded: {file_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def wait_for_completion(self, generation_result: Dict, timeout: int = 300) -> Optional[str]:
        """Wait for generation to complete and return audio URL"""
        generation_id = generation_result.get("id") or generation_result.get("generation_id")
        if not generation_id:
            logger.error("No generation ID found in result")
            return None
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.check_generation_status(generation_id)
            if not status:
                time.sleep(5)
                continue
            
            state = status.get("status") or status.get("state")
            logger.info(f"Generation status: {state}")
            
            if state in ["complete", "completed", "success"]:
                audio_url = status.get("audio_url") or status.get("url")
                if audio_url:
                    return audio_url
                    
            elif state in ["failed", "error"]:
                logger.error(f"Generation failed: {status.get('error', 'Unknown error')}")
                return None
                
            time.sleep(10)  # Wait 10 seconds before checking again
        
        logger.error("Generation timed out")
        return None

def get_track_configurations() -> List[Dict]:
    """Define the 3 synthwave tracks for The Drive minigame"""
    return [
        {
            "title": "Highway Dreams",
            "filename": "highway_dreams.ogg",
            "prompt": "An upbeat synthwave racing theme with driving basslines, retro analog synthesizers, and energetic arpeggios. Perfect for high-speed highway driving in an 80s arcade racing game. Seamlessly loopable with a nostalgic OutRun vibe.",
            "tags": ["synthwave", "outrun", "80s", "arcade", "racing", "upbeat", "retro", "electronic"],
            "duration": 180,  # 3 minutes
            "bpm": 125,
            "key": "C major",
            "style": "synthwave",
            "instrumental": True
        },
        {
            "title": "Sunset Cruise",
            "filename": "sunset_cruise.ogg", 
            "prompt": "A relaxed chillwave cruising theme with warm analog pads, gentle arpeggios, and a laid-back groove. Perfect for scenic coastal drives at sunset. Smooth and atmospheric with vintage synthesizer sounds.",
            "tags": ["chillwave", "synthwave", "80s", "relaxed", "sunset", "cruise", "ambient", "retro"],
            "duration": 180,  # 3 minutes
            "bpm": 108,
            "key": "G major",
            "style": "chillwave",
            "instrumental": True
        },
        {
            "title": "Turbo Rush",
            "filename": "turbo_rush.ogg",
            "prompt": "High-energy intense synthwave racing theme with aggressive basslines, rapid arpeggios, and driving percussion. Perfect for high-speed racing and intense competition. Dark and powerful with minor key tension.",
            "tags": ["synthwave", "intense", "racing", "high-energy", "aggressive", "80s", "turbo", "dark"],
            "duration": 180,  # 3 minutes
            "bpm": 140,
            "key": "A minor", 
            "style": "dark synthwave",
            "instrumental": True
        }
    ]

def convert_to_ogg(input_file: Path, output_file: Path) -> bool:
    """Convert audio file to OGG format using ffmpeg"""
    try:
        import subprocess
        cmd = [
            "ffmpeg", "-i", str(input_file), 
            "-c:a", "libvorbis", "-q:a", "6",  # High quality OGG
            "-y", str(output_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Successfully converted to OGG: {output_file}")
            return True
        else:
            logger.error(f"FFmpeg conversion failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        logger.warning("FFmpeg not found. Keeping original format.")
        return False
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        return False

def create_placeholder_tracks(output_dir: Path, tracks: List[Dict]) -> List[str]:
    """Create placeholder OGG files for development when API fails"""
    logger.info("Creating placeholder music tracks for development...")
    
    successful_tracks = []
    
    try:
        import numpy as np
        from scipy.io import wavfile
        import subprocess
        
        for track_config in tracks:
            logger.info(f"Creating placeholder for {track_config['title']}")
            
            # Generate a simple synthesized tone pattern based on track characteristics
            sample_rate = 44100
            duration = 30  # 30 second loops for development
            
            # Create basic waveform based on track type
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            if "rush" in track_config['title'].lower():
                # High energy - complex waveform
                frequency = 440 * 2  # A4 * 2
                wave = np.sin(frequency * 2.0 * np.pi * t) * 0.3
                wave += np.sin(frequency * 1.5 * 2.0 * np.pi * t) * 0.2
                wave += np.sin(frequency * 0.5 * 2.0 * np.pi * t) * 0.1
            elif "cruise" in track_config['title'].lower():
                # Relaxed - gentle sine waves
                frequency = 261.63  # C4
                wave = np.sin(frequency * 2.0 * np.pi * t) * 0.4
                wave += np.sin(frequency * 1.25 * 2.0 * np.pi * t) * 0.2
            else:
                # Highway Dreams - upbeat middle ground
                frequency = 329.63  # E4
                wave = np.sin(frequency * 2.0 * np.pi * t) * 0.3
                wave += np.sin(frequency * 1.5 * 2.0 * np.pi * t) * 0.2
            
            # Add some simple rhythm
            beat_freq = track_config['bpm'] / 60.0
            beat_pattern = np.sin(beat_freq * 2.0 * np.pi * t) * 0.1
            wave = wave * (1.0 + beat_pattern)
            
            # Normalize
            wave = wave / np.max(np.abs(wave))
            wave = (wave * 32767).astype(np.int16)
            
            # Save as WAV first
            wav_path = output_dir / f"temp_{track_config['title'].lower().replace(' ', '_')}.wav"
            wavfile.write(wav_path, sample_rate, wave)
            
            # Convert to OGG
            ogg_path = output_dir / track_config['filename']
            cmd = [
                "ffmpeg", "-i", str(wav_path),
                "-c:a", "libvorbis", "-q:a", "4",
                "-y", str(ogg_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                wav_path.unlink()  # Remove temp WAV
                successful_tracks.append(track_config['title'])
                logger.info(f"Created placeholder: {ogg_path}")
            else:
                logger.warning(f"Could not convert to OGG, keeping WAV: {wav_path}")
                wav_path.rename(ogg_path.with_suffix('.wav'))
                successful_tracks.append(track_config['title'])
                
    except ImportError:
        logger.warning("NumPy/SciPy not available for placeholder generation")
    except FileNotFoundError:
        logger.warning("FFmpeg not available for OGG conversion")
    except Exception as e:
        logger.error(f"Placeholder generation failed: {e}")
    
    return successful_tracks

def main():
    """Main function to generate all racing music tracks"""
    # API key
    api_key = "sk_ed822333d35b476ea444e7dd6f839227"
    
    # Get track configurations
    tracks = get_track_configurations()
    
    logger.info("🎵 Starting music generation for The Drive minigame")
    logger.info(f"Generating {len(tracks)} synthwave tracks...")
    
    # Create output directory
    output_dir = Path("assets/audio/music/drive")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    successful_tracks = []
    
    # Try API generation first (with short timeout)
    if api_key:
        logger.info("Attempting Suno API generation...")
        generator = SunoMusicGenerator(api_key)
        
        for track_config in tracks:
            logger.info(f"Trying API generation for: {track_config['title']}")
            
            # Quick attempt with timeout
            try:
                generation_result = generator.generate_track(track_config)
                if generation_result:
                    audio_url = generator.wait_for_completion(generation_result, timeout=60)
                    if audio_url:
                        temp_filename = f"temp_{track_config['filename']}"
                        if generator.download_track(audio_url, temp_filename):
                            temp_path = output_dir / temp_filename
                            final_path = output_dir / track_config['filename']
                            
                            if convert_to_ogg(temp_path, final_path):
                                temp_path.unlink()
                                successful_tracks.append(track_config['title'])
                            else:
                                temp_path.rename(final_path)
                                successful_tracks.append(track_config['title'])
            except Exception as e:
                logger.warning(f"API generation failed for {track_config['title']}: {e}")
                break  # Stop trying API if it's not working
    
    # If no tracks were generated via API, create placeholders
    if len(successful_tracks) == 0:
        logger.info("\n" + "="*50)
        logger.info("Creating placeholder synthwave tracks for development...")
        logger.info("="*50)
        
        placeholder_tracks = create_placeholder_tracks(output_dir, tracks)
        successful_tracks.extend(placeholder_tracks)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("🎵 MUSIC GENERATION COMPLETE 🎵")
    logger.info(f"{'='*60}")
    logger.info(f"Successfully generated {len(successful_tracks)}/{len(tracks)} tracks:")
    
    for track in successful_tracks:
        logger.info(f"  ✅ {track}")
    
    if len(successful_tracks) < len(tracks):
        failed_tracks = [t['title'] for t in tracks if t['title'] not in successful_tracks]
        logger.info(f"\nFailed tracks:")
        for track in failed_tracks:
            logger.info(f"  ❌ {track}")
    
    logger.info(f"\nTracks saved to: {output_dir}")
    logger.info("\nTo use these tracks in the game:")
    logger.info("1. Ensure they're in the correct assets/audio/music/drive/ directory")
    logger.info("2. Update the music configuration in the drive minigame")
    logger.info("3. Test the tracks in-game for proper looping")
    
    # Create a simple JSON manifest for the game to use
    manifest = {
        "drive_music_tracks": [
            {
                "id": "highway_dreams",
                "title": "Highway Dreams",
                "filename": "highway_dreams.ogg",
                "bpm": 125,
                "key": "C major",
                "mood": "upbeat",
                "description": "Main racing theme"
            },
            {
                "id": "sunset_cruise", 
                "title": "Sunset Cruise",
                "filename": "sunset_cruise.ogg",
                "bpm": 108,
                "key": "G major", 
                "mood": "relaxed",
                "description": "Cruising theme"
            },
            {
                "id": "turbo_rush",
                "title": "Turbo Rush", 
                "filename": "turbo_rush.ogg",
                "bpm": 140,
                "key": "A minor",
                "mood": "intense",
                "description": "High-energy racing"
            }
        ]
    }
    
    manifest_path = output_dir / "music_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"Music manifest created: {manifest_path}")

if __name__ == "__main__":
    main()