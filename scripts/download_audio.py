#!/usr/bin/env python3
"""
Danger Rose - Audio Download and Conversion Script

This script helps download and convert audio files for the Danger Rose game.
It handles both direct downloads where possible and provides guidance for manual downloads.
"""

import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

# Game audio requirements
MUSIC_FILES = {
    "hub_theme": {
        "url": "https://freepd.com/music/Happy%20Whistling%20Ukulele.mp3",
        "description": "Cheerful ukulele track for hub world",
        "size_target": "1-2MB",
    },
    "title_theme": {
        "url": "https://freepd.com/music/Funshine.mp3",
        "description": "Bright welcome music for title screen",
        "size_target": "1-2MB",
    },
    "ski_theme": {
        "url": "https://freepd.com/music/Mountain%20King.mp3",
        "description": "Adventure music for skiing minigame",
        "size_target": "1-2MB",
    },
    "pool_theme": {
        "url": "https://freepd.com/music/Pickled%20Pink.mp3",
        "description": "Light, playful music for pool game",
        "size_target": "1-2MB",
    },
    "vegas_theme": {
        "url": "https://freepd.com/music/City%20Sunshine.mp3",
        "description": "Upbeat music for Vegas minigame",
        "size_target": "1-2MB",
    },
}

SFX_FILES = {
    "jump": {
        "description": "Player jumping sound",
        "size_target": "10-50KB",
        "mixkit_search": "Player jumping in a video game",
    },
    "collect_item": {
        "description": "Item collection sound",
        "size_target": "10-50KB",
        "mixkit_search": "Winning a coin, video game",
    },
    "menu_select": {
        "description": "Menu selection sound",
        "size_target": "10-50KB",
        "mixkit_search": "Video game retro click",
    },
    "victory": {
        "description": "Level completion sound",
        "size_target": "10-50KB",
        "mixkit_search": "Game level completed",
    },
    "attack": {
        "description": "Attack/action sound",
        "size_target": "10-50KB",
        "mixkit_search": "Martial arts fast punch",
    },
}


def setup_directories():
    """Create audio directories if they don't exist."""
    base_path = Path(__file__).parent.parent / "assets" / "audio"
    music_path = base_path / "music"
    sfx_path = base_path / "sfx"

    music_path.mkdir(parents=True, exist_ok=True)
    sfx_path.mkdir(parents=True, exist_ok=True)

    return base_path, music_path, sfx_path


def check_ffmpeg():
    """Check if FFmpeg is available for conversion."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], check=False, capture_output=True, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def download_file(url, destination):
    """Download a file from URL to destination."""
    try:
        print(f"Downloading from {url}...")
        urllib.request.urlretrieve(url, destination)
        file_size = os.path.getsize(destination)
        print(f"Downloaded {destination.name} ({file_size:,} bytes)")
        return True
    except urllib.error.URLError as e:
        print(f"Failed to download {url}: {e}")
        return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


def convert_to_ogg(input_path, output_path, quality=4):
    """Convert audio file to OGG format using FFmpeg."""
    if not check_ffmpeg():
        print("FFmpeg not found. Please install FFmpeg or use online converter.")
        return False

    try:
        cmd = [
            "ffmpeg",
            "-i",
            str(input_path),
            "-c:a",
            "libvorbis",
            "-q:a",
            str(quality),
            "-y",  # Overwrite output file
            str(output_path),
        ]

        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        if result.returncode == 0:
            file_size = os.path.getsize(output_path)
            print(f"Converted to {output_path.name} ({file_size:,} bytes)")
            return True
        print(f"FFmpeg error: {result.stderr}")
        return False

    except Exception as e:
        print(f"Conversion error: {e}")
        return False


def download_music():
    """Download and convert music files."""
    print("\n=== DOWNLOADING MUSIC FILES ===")
    base_path, music_path, sfx_path = setup_directories()

    success_count = 0
    total_count = len(MUSIC_FILES)

    for name, info in MUSIC_FILES.items():
        print(f"\nProcessing {name}...")
        print(f"   Description: {info['description']}")
        print(f"   Target size: {info['size_target']}")

        # Download MP3 first
        temp_mp3 = music_path / f"{name}.mp3"
        final_ogg = music_path / f"{name}.ogg"

        if download_file(info["url"], temp_mp3):
            # Convert to OGG
            if convert_to_ogg(temp_mp3, final_ogg, quality=5):
                success_count += 1
                # Remove temporary MP3
                temp_mp3.unlink()
            else:
                print(f"MP3 file saved as {temp_mp3}")
                print(f"   Please convert manually to {final_ogg}")
        else:
            print(f"Manual download needed from: {info['url']}")

    print(f"\nMusic download summary: {success_count}/{total_count} successful")
    return success_count


def generate_sfx_guide():
    """Generate guide for manually downloading SFX files."""
    print("\n=== SOUND EFFECTS DOWNLOAD GUIDE ===")
    print("Visit https://mixkit.co/free-sound-effects/game/ and download:")

    base_path, music_path, sfx_path = setup_directories()

    for name, info in SFX_FILES.items():
        print(f"\n{name}.ogg")
        print(f"   Search: '{info['mixkit_search']}'")
        print(f"   Description: {info['description']}")
        print(f"   Target size: {info['size_target']}")
        print(f"   Save as: {sfx_path / f'{name}.ogg'}")


def check_existing_files():
    """Check what audio files already exist."""
    print("\n=== CHECKING EXISTING FILES ===")
    base_path, music_path, sfx_path = setup_directories()

    print("\nMusic files:")
    for name in MUSIC_FILES:
        ogg_file = music_path / f"{name}.ogg"
        if ogg_file.exists():
            size = os.path.getsize(ogg_file)
            print(f"[EXISTS] {name}.ogg ({size:,} bytes)")
        else:
            print(f"[MISSING] {name}.ogg")

    print("\nSound effect files:")
    for name in SFX_FILES:
        ogg_file = sfx_path / f"{name}.ogg"
        if ogg_file.exists():
            size = os.path.getsize(ogg_file)
            print(f"[EXISTS] {name}.ogg ({size:,} bytes)")
        else:
            print(f"[MISSING] {name}.ogg")


def create_attribution_file():
    """Create attribution file for audio sources."""
    base_path, music_path, sfx_path = setup_directories()
    attribution_file = base_path / "ATTRIBUTION.md"

    content = """# Audio Attribution

This file documents the sources of audio files used in Danger Rose.

## Music Files (FreePD.com)

All music files are from FreePD.com and are Creative Commons 0 licensed.
No attribution required, but provided for transparency.

"""

    for name, info in MUSIC_FILES.items():
        content += f"- **{name}.ogg**: {info['description']}\n"
        content += f"  - Source: {info['url']}\n"
        content += "  - License: Creative Commons 0 (Public Domain)\n\n"

    content += """## Sound Effects (Mixkit.co)

All sound effects are from Mixkit.co and are royalty-free.
Licensed for commercial use.

"""

    for name, info in SFX_FILES.items():
        content += f"- **{name}.ogg**: {info['description']}\n"
        content += f"  - Search term: '{info['mixkit_search']}'\n"
        content += "  - Source: https://mixkit.co/free-sound-effects/game/\n"
        content += "  - License: Royalty-free (Commercial use allowed)\n\n"

    with open(attribution_file, "w") as f:
        f.write(content)

    print(f"Created attribution file: {attribution_file}")


def main():
    """Main function to orchestrate audio download process."""
    print("Danger Rose - Audio Download Script")
    print("=" * 50)

    # Check system setup
    print(f"FFmpeg available: {'Yes' if check_ffmpeg() else 'No'}")

    # Check existing files
    check_existing_files()

    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. Download music files (requires internet)")
    print("2. Show SFX download guide")
    print("3. Create attribution file")
    print("4. All of the above")
    print("5. Exit")

    try:
        choice = input("\nEnter choice (1-5): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting...")
        return

    if choice == "1":
        download_music()
    elif choice == "2":
        generate_sfx_guide()
    elif choice == "3":
        create_attribution_file()
    elif choice == "4":
        download_music()
        generate_sfx_guide()
        create_attribution_file()
    elif choice == "5":
        print("Goodbye!")
        return
    else:
        print("Invalid choice.")
        return

    print("\nAudio setup complete!")
    print("Run 'make run' to test the game with new audio files.")


if __name__ == "__main__":
    main()
