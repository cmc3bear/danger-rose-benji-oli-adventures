#!/usr/bin/env python3
"""
Convert existing WAV files to OGG format for Danger Rose game.

This script finds WAV files in the audio directory and converts them to OGG
using Python's built-in audio processing or provides instructions for manual conversion.
"""

import os
import subprocess
from pathlib import Path


def check_ffmpeg():
    """Check if FFmpeg is available for conversion."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], check=False, capture_output=True, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def convert_with_ffmpeg(wav_path, ogg_path, quality=4):
    """Convert WAV to OGG using FFmpeg."""
    try:
        cmd = [
            "ffmpeg",
            "-i",
            str(wav_path),
            "-c:a",
            "libvorbis",
            "-q:a",
            str(quality),
            "-y",  # Overwrite output file
            str(ogg_path),
        ]

        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        if result.returncode == 0:
            file_size = os.path.getsize(ogg_path)
            print(f"Converted {wav_path.name} -> {ogg_path.name} ({file_size:,} bytes)")
            return True
        print(f"FFmpeg error converting {wav_path.name}: {result.stderr}")
        return False

    except Exception as e:
        print(f"Conversion error for {wav_path.name}: {e}")
        return False


def main():
    """Find WAV files and convert them to OGG."""
    print("Danger Rose - WAV to OGG Converter")
    print("=" * 40)

    # Set up paths
    base_path = Path(__file__).parent.parent / "assets" / "audio"

    if not base_path.exists():
        print(f"Audio directory not found: {base_path}")
        return

    # Find all WAV files
    wav_files = []
    for directory in ["music", "sfx"]:
        dir_path = base_path / directory
        if dir_path.exists():
            wav_files.extend(dir_path.glob("*.wav"))

    if not wav_files:
        print("No WAV files found to convert.")
        return

    print(f"Found {len(wav_files)} WAV files to convert:")
    for wav_file in wav_files:
        print(f"  - {wav_file.relative_to(base_path)}")

    # Check if FFmpeg is available
    ffmpeg_available = check_ffmpeg()
    print(f"\nFFmpeg available: {'Yes' if ffmpeg_available else 'No'}")

    if not ffmpeg_available:
        print("\nFFmpeg not found. Please install FFmpeg or use online conversion:")
        print("1. Download FFmpeg from: https://ffmpeg.org/download.html")
        print("2. Or use online converter: https://convertio.co/wav-ogg/")
        print("\nManual conversion needed for:")
        for wav_file in wav_files:
            ogg_file = wav_file.with_suffix(".ogg")
            print(f"  {wav_file} -> {ogg_file}")
        return

    # Convert files
    print(f"\nConverting {len(wav_files)} files...")
    success_count = 0

    for wav_file in wav_files:
        ogg_file = wav_file.with_suffix(".ogg")

        # Use higher quality for music, lower for SFX
        quality = 5 if "music" in str(wav_file) else 4

        if convert_with_ffmpeg(wav_file, ogg_file, quality):
            success_count += 1
            # Optionally remove the original WAV file
            # wav_file.unlink()  # Uncomment to delete WAV files after conversion

    print(f"\nConversion complete: {success_count}/{len(wav_files)} successful")

    if success_count == len(wav_files):
        print("All files converted successfully!")
        print("You can now delete the original WAV files if desired.")
    else:
        print("Some conversions failed. Check the error messages above.")


if __name__ == "__main__":
    main()
