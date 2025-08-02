#!/usr/bin/env python3
"""Create placeholder music files for The Drive minigame."""

import os
import json
import wave
import struct
import math
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "audio" / "music" / "drive"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Track definitions
TRACKS = [
    {
        "id": "highway_dreams",
        "title": "Highway Dreams",
        "bpm": 125,
        "key": "C major",
        "mood": "energetic",
        "description": "Main racing theme",
        "frequencies": [261.63, 329.63, 392.00, 523.25],  # C major chord
        "pattern": [0, 1, 2, 1, 3, 2, 1, 0]  # Arpeggio pattern
    },
    {
        "id": "sunset_cruise",
        "title": "Sunset Cruise",
        "bpm": 108,
        "key": "G major",
        "mood": "relaxed",
        "description": "Peaceful cruising music",
        "frequencies": [392.00, 493.88, 587.33],  # G major chord
        "pattern": [0, 1, 2, 1]  # Simple pattern
    },
    {
        "id": "turbo_rush",
        "title": "Turbo Rush",
        "bpm": 140,
        "key": "A minor",
        "mood": "intense",
        "description": "High-energy racing",
        "frequencies": [440.00, 523.25, 659.25],  # A minor chord
        "pattern": [0, 0, 1, 0, 2, 0, 1, 0]  # Driving pattern
    }
]

def generate_tone(frequency, duration, sample_rate=44100):
    """Generate a sine wave tone."""
    frames = int(duration * sample_rate)
    return [int(32767 * 0.3 * math.sin(2 * math.pi * frequency * x / sample_rate)) 
            for x in range(frames)]

def generate_synth_track(track_info, duration=30):
    """Generate a simple synthesizer track."""
    sample_rate = 44100
    
    # Calculate timing
    bpm = track_info["bpm"]
    beat_duration = 60.0 / bpm
    note_duration = beat_duration / 4  # 16th notes
    
    # Generate pattern
    pattern = track_info["pattern"]
    frequencies = track_info["frequencies"]
    
    audio_data = []
    
    # Generate multiple bars
    total_beats = int(duration / beat_duration)
    
    for beat in range(total_beats):
        for step in pattern:
            if step < len(frequencies):
                freq = frequencies[step]
                # Add some variation
                if track_info["mood"] == "intense":
                    freq *= (1 + 0.1 * math.sin(beat * 0.5))  # Slight pitch bend
                
                tone = generate_tone(freq, note_duration, sample_rate)
                audio_data.extend(tone)
    
    # Add simple envelope (fade in/out)
    fade_samples = int(0.5 * sample_rate)
    for i in range(min(fade_samples, len(audio_data))):
        audio_data[i] = int(audio_data[i] * (i / fade_samples))
        audio_data[-(i+1)] = int(audio_data[-(i+1)] * (i / fade_samples))
    
    return audio_data, sample_rate

def save_wav_file(filename, audio_data, sample_rate):
    """Save audio data as WAV file."""
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)   # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Write audio data
        for sample in audio_data:
            wav_file.writeframes(struct.pack('<h', sample))

def main():
    """Generate placeholder music tracks."""
    print("Creating placeholder music for The Drive minigame")
    print("=" * 50)
    
    manifest = {"tracks": []}
    
    for track in TRACKS:
        print(f"\nGenerating: {track['title']}")
        print(f"  BPM: {track['bpm']}, Key: {track['key']}")
        
        # Generate audio
        audio_data, sample_rate = generate_synth_track(track, duration=30)
        
        # Save as WAV
        output_file = OUTPUT_DIR / f"{track['id']}.wav"
        save_wav_file(str(output_file), audio_data, sample_rate)
        
        print(f"  [OK] Saved: {output_file.name}")
        
        # Update manifest
        manifest_entry = {
            "id": track["id"],
            "title": track["title"],
            "filename": f"{track['id']}.wav",
            "bpm": track["bpm"],
            "key": track["key"],
            "mood": track["mood"],
            "description": track["description"]
        }
        manifest["tracks"].append(manifest_entry)
    
    # Save manifest
    manifest_path = OUTPUT_DIR / "music_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nManifest saved: {manifest_path}")
    print("\n[OK] Placeholder music generation complete!")
    print("\nNote: These are simple placeholder tracks. Replace with")
    print("professional music when available.")

if __name__ == "__main__":
    main()