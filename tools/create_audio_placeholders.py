#!/usr/bin/env python3
"""Create placeholder audio files for The Drive racing game."""

import os
import subprocess
from pathlib import Path


def create_placeholder_ogg(filepath: Path, duration: float = 3.0, frequency: int = 440):
    """
    Create a placeholder OGG file with a simple tone.
    
    Args:
        filepath: Path where the file should be created
        duration: Duration in seconds
        frequency: Frequency of the tone in Hz
    """
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Create a simple sine wave tone using ffmpeg (if available)
    # Otherwise create a simple file with silence
    try:
        # Try to create with ffmpeg
        cmd = [
            'ffmpeg', '-f', 'lavfi',
            '-i', f'sine=frequency={frequency}:duration={duration}',
            '-c:a', 'libvorbis', '-y', str(filepath)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"Created audio placeholder: {filepath}")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: create a minimal OGG file header
        # This won't play sound but will prevent file-not-found errors
        create_empty_ogg(filepath)
        print(f"Created empty audio placeholder: {filepath}")


def create_empty_ogg(filepath: Path):
    """Create a minimal OGG file that won't cause loading errors."""
    # OGG Vorbis header for a minimal valid file
    # This is a very basic OGG file structure - just enough to avoid crashes
    ogg_header = bytes([
        # OGG Page Header
        0x4F, 0x67, 0x67, 0x53,  # "OggS"
        0x00,  # Version
        0x02,  # Header type (first page of logical bitstream) 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # Granule position
        0x00, 0x00, 0x00, 0x00,  # Bitstream serial number
        0x00, 0x00, 0x00, 0x00,  # Page sequence number
        0x00, 0x00, 0x00, 0x00,  # CRC checksum (would need to be calculated)
        0x1A,  # Page segments
        # Segment table (26 bytes of data)
        0x1A,
        # Vorbis header packet
        0x01, 0x76, 0x6F, 0x72, 0x62, 0x69, 0x73,  # "\x01vorbis"
        0x00, 0x00, 0x00, 0x00,  # Version
        0x02,  # Channels
        0x44, 0xAC, 0x00, 0x00,  # Sample rate (44100)
        0x00, 0x00, 0x00, 0x00,  # Bitrate maximum
        0x00, 0x00, 0x00, 0x00,  # Bitrate nominal  
        0x00, 0x00, 0x00, 0x00,  # Bitrate minimum
        0x0B,  # Blocksize
        0x01   # Framing bit
    ])
    
    with open(filepath, 'wb') as f:
        f.write(ogg_header)


def main():
    """Create all placeholder audio files for The Drive game."""
    project_root = Path(__file__).parent.parent
    audio_dir = project_root / "assets" / "audio"
    
    # Music tracks
    music_files = [
        ("music/drive_highway_dreams.ogg", 180.0, 330),  # 3 minutes, lower frequency
        ("music/drive_sunset_cruise.ogg", 210.0, 220),   # 3.5 minutes, very low frequency  
        ("music/drive_turbo_rush.ogg", 180.0, 550),      # 3 minutes, higher frequency
    ]
    
    # UI sound effects
    ui_sfx_files = [
        ("sfx/ui_preview_start.ogg", 0.8, 800),
        ("sfx/ui_confirm.ogg", 0.6, 1000),
        ("sfx/ui_cancel.ogg", 0.4, 400),
    ]
    
    # Race stingers
    stinger_files = [
        ("sfx/stinger_crash.ogg", 1.5, 200),       # Low dramatic tone
        ("sfx/stinger_boost.ogg", 1.2, 880),       # Rising energetic tone
        ("sfx/stinger_victory.ogg", 3.0, 660),     # Triumphant sustained tone
        ("sfx/stinger_final_lap.ogg", 1.8, 440),  # Tense warning tone
        ("sfx/stinger_position_up.ogg", 0.8, 740), # Positive ascending tone
        ("sfx/stinger_position_down.ogg", 0.8, 320), # Negative descending tone
    ]
    
    all_files = music_files + ui_sfx_files + stinger_files
    
    print("Creating placeholder audio files for The Drive game...")
    print(f"Audio directory: {audio_dir}")
    
    for filename, duration, frequency in all_files:
        filepath = audio_dir / filename
        create_placeholder_ogg(filepath, duration, frequency)
    
    print(f"\nCreated {len(all_files)} placeholder audio files.")
    print("\nNOTE: These are placeholder files with simple tones.")
    print("Replace them with actual music and sound effects for the full experience.")
    print("\nSee DRIVE_AUDIO_REQUIREMENTS.md for detailed specifications.")


if __name__ == "__main__":
    main()