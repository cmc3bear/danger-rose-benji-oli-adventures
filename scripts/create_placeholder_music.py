#!/usr/bin/env python3
"""
Placeholder Music Generator for Danger Rose - The Drive Minigame

Creates placeholder synthwave tracks for development when Suno API is unavailable.
These are simple synthesized tracks that can be replaced with real music later.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List
import numpy as np
from scipy.io import wavfile
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_track_configurations() -> List[Dict]:
    """Define the 3 synthwave tracks for The Drive minigame"""
    return [
        {
            "title": "Highway Dreams",
            "filename": "highway_dreams.ogg",
            "bpm": 125,
            "key": "C major",
            "style": "synthwave",
            "mood": "upbeat",
            "description": "Main racing theme"
        },
        {
            "title": "Sunset Cruise",
            "filename": "sunset_cruise.ogg", 
            "bpm": 108,
            "key": "G major", 
            "style": "chillwave",
            "mood": "relaxed",
            "description": "Cruising theme"
        },
        {
            "title": "Turbo Rush",
            "filename": "turbo_rush.ogg",
            "bpm": 140,
            "key": "A minor",
            "style": "dark synthwave",
            "mood": "intense",
            "description": "High-energy racing"
        }
    ]

def create_synthwave_track(track_config: Dict, output_path: Path, duration: int = 60) -> bool:
    """
    Create a synthwave-style placeholder track using simple synthesis
    
    Args:
        track_config: Track configuration dictionary
        output_path: Path where to save the track
        duration: Length in seconds
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Creating {track_config['title']} ({track_config['style']})...")
        
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Base frequencies for different keys
        key_frequencies = {
            "C major": [261.63, 329.63, 392.00, 523.25],  # C, E, G, C
            "G major": [196.00, 246.94, 293.66, 392.00],  # G, B, D, G  
            "A minor": [220.00, 261.63, 329.63, 440.00]   # A, C, E, A
        }
        
        base_freqs = key_frequencies.get(track_config['key'], key_frequencies["C major"])
        
        # Create different waveforms based on style
        if "rush" in track_config['title'].lower() or "intense" in track_config['mood']:
            # High energy - aggressive sawtooth waves and arpeggios
            wave = np.zeros_like(t)
            
            # Fast arpeggios
            arp_speed = track_config['bpm'] / 60.0 * 4  # 16th notes
            for i, freq in enumerate(base_freqs):
                phase_offset = i * np.pi / 2
                arp_pattern = np.sin(arp_speed * 2 * np.pi * t + phase_offset) > 0.5
                sawtooth = 2 * (t * freq % 1) - 1  # Sawtooth wave
                wave += sawtooth * arp_pattern * 0.15
            
            # Add driving bass
            bass_freq = base_freqs[0] / 2
            bass_pattern = np.sin(track_config['bpm'] / 60.0 * 2 * np.pi * t) > 0
            bass_wave = np.sin(bass_freq * 2 * np.pi * t) * bass_pattern * 0.3
            wave += bass_wave
            
        elif "cruise" in track_config['title'].lower() or "relaxed" in track_config['mood']:
            # Relaxed - warm pad sounds and gentle arpeggios
            wave = np.zeros_like(t)
            
            # Slow chord progression
            chord_speed = track_config['bpm'] / 60.0 / 4  # Whole notes
            for i, freq in enumerate(base_freqs):
                # Create warm pad sound with multiple harmonics
                for harmonic in [1, 0.5, 0.25]:
                    pad_freq = freq * harmonic
                    envelope = 0.5 + 0.3 * np.sin(chord_speed * 2 * np.pi * t + i * np.pi / 2)
                    pad_wave = np.sin(pad_freq * 2 * np.pi * t) * envelope * 0.1
                    wave += pad_wave
            
            # Gentle arpeggios
            arp_speed = track_config['bpm'] / 60.0 * 2  # 8th notes
            for i, freq in enumerate(base_freqs[:-1]):  # Skip last note for gentleness
                phase_offset = i * np.pi / 3
                arp_envelope = 0.5 * (1 + np.sin(arp_speed * 2 * np.pi * t + phase_offset))
                arp_wave = np.sin(freq * 2 * np.pi * t) * arp_envelope * 0.15
                wave += arp_wave
                
        else:
            # Highway Dreams - balanced upbeat synthwave
            wave = np.zeros_like(t)
            
            # Classic synthwave arpeggios
            arp_speed = track_config['bpm'] / 60.0 * 2  # 8th notes
            for i, freq in enumerate(base_freqs):
                phase_offset = i * np.pi / 4
                arp_pattern = (np.sin(arp_speed * 2 * np.pi * t + phase_offset) + 1) / 2
                synth_wave = np.sin(freq * 2 * np.pi * t) * arp_pattern * 0.2
                wave += synth_wave
            
            # Add some bass line
            bass_freq = base_freqs[0] / 2 
            bass_pattern = np.sin(track_config['bpm'] / 60.0 * 2 * np.pi * t)
            bass_wave = np.sin(bass_freq * 2 * np.pi * t) * (bass_pattern > 0) * 0.25
            wave += bass_wave
            
            # Add some lead melody
            lead_freq = base_freqs[2] * 2  # High octave
            lead_pattern = 0.3 * np.sin(track_config['bpm'] / 60.0 / 2 * 2 * np.pi * t)
            lead_wave = np.sin(lead_freq * 2 * np.pi * t) * (lead_pattern > 0) * 0.15
            wave += lead_wave
        
        # Add subtle reverb-like effect
        delay_samples = int(0.1 * sample_rate)  # 100ms delay
        if len(wave) > delay_samples:
            delayed = np.concatenate([np.zeros(delay_samples), wave[:-delay_samples]])
            wave = wave + delayed * 0.2
        
        # Apply gentle filter sweep for movement
        filter_freq = 0.1  # Very slow sweep
        filter_envelope = 0.8 + 0.2 * np.sin(filter_freq * 2 * np.pi * t)
        wave = wave * filter_envelope
        
        # Normalize and convert to 16-bit
        wave = wave / np.max(np.abs(wave)) * 0.8  # Leave some headroom
        wave = (wave * 32767).astype(np.int16)
        
        # Create stereo by adding slight delay to right channel
        stereo_delay = int(0.01 * sample_rate)  # 10ms
        left_channel = wave
        right_channel = np.concatenate([np.zeros(stereo_delay), wave[:-stereo_delay]])
        stereo_wave = np.column_stack([left_channel, right_channel])
        
        # Save as WAV first
        wav_path = output_path.with_suffix('.wav')
        wavfile.write(wav_path, sample_rate, stereo_wave)
        
        # Convert to OGG using ffmpeg
        try:
            cmd = [
                "ffmpeg", "-i", str(wav_path),
                "-c:a", "libvorbis", "-q:a", "4",  # Good quality OGG
                "-ac", "2",  # Ensure stereo
                "-y", str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                wav_path.unlink()  # Remove temporary WAV
                logger.info(f"✅ Created: {output_path}")
                return True
            else:
                logger.warning(f"FFmpeg failed, keeping WAV format: {result.stderr}")
                wav_path.rename(output_path.with_suffix('.wav'))
                return True
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("FFmpeg not available, keeping WAV format")
            wav_path.rename(output_path.with_suffix('.wav'))
            return True
            
    except Exception as e:
        logger.error(f"Failed to create {track_config['title']}: {e}")
        return False

def main():
    """Create placeholder synthwave tracks for The Drive minigame"""
    logger.info("🎵 Creating placeholder synthwave tracks for The Drive minigame")
    
    # Create output directory
    output_dir = Path("assets/audio/music/drive")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get track configurations
    tracks = get_track_configurations()
    
    successful_tracks = []
    failed_tracks = []
    
    for track_config in tracks:
        logger.info(f"\n{'='*50}")
        logger.info(f"Track: {track_config['title']}")
        logger.info(f"Style: {track_config['style']}")
        logger.info(f"BPM: {track_config['bpm']}")
        logger.info(f"Key: {track_config['key']}")
        logger.info(f"{'='*50}")
        
        output_path = output_dir / track_config['filename']
        
        if create_synthwave_track(track_config, output_path, duration=90):
            successful_tracks.append(track_config['title'])
        else:
            failed_tracks.append(track_config['title'])
    
    # Create manifest file
    manifest = {
        "drive_music_tracks": [
            {
                "id": track['title'].lower().replace(' ', '_'),
                "title": track['title'],
                "filename": track['filename'],
                "bpm": track['bpm'],
                "key": track['key'],
                "mood": track['mood'],
                "description": track['description']
            }
            for track in tracks
        ],
        "created": "placeholder",
        "note": "These are placeholder tracks created for development. Replace with real Suno-generated tracks when API is available."
    }
    
    manifest_path = output_dir / "music_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("🎵 PLACEHOLDER MUSIC GENERATION COMPLETE 🎵")
    logger.info(f"{'='*60}")
    logger.info(f"Successfully created {len(successful_tracks)}/{len(tracks)} tracks:")
    
    for track in successful_tracks:
        logger.info(f"  ✅ {track}")
    
    if failed_tracks:
        logger.info(f"\nFailed tracks:")
        for track in failed_tracks:
            logger.info(f"  ❌ {track}")
    
    logger.info(f"\nTracks saved to: {output_dir}")
    logger.info(f"Manifest created: {manifest_path}")
    
    logger.info("\n🎮 Integration Notes:")
    logger.info("1. These are placeholder tracks for development")
    logger.info("2. Replace with real Suno API tracks when service is available")
    logger.info("3. Each track is 90 seconds and designed to loop seamlessly")
    logger.info("4. Tracks are in OGG format (or WAV if ffmpeg unavailable)")
    logger.info("5. Use the manifest.json to integrate with the game's music system")

if __name__ == "__main__":
    main()