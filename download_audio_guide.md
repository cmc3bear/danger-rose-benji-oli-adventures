# Danger Rose - Audio Download and Conversion Guide

This guide will help you manually download high-quality audio files for the Danger Rose game.

## Required Tools

1. **Audio Converter**: Download and install one of these:
   - **FFmpeg** (recommended): https://ffmpeg.org/download.html
   - **Online converter**: https://convertio.co/mp3-ogg/ or https://online-audio-converter.com/

## Music Files to Download

### 1. Hub Theme - "Happy Whistling Ukulele"
- **URL**: https://freepd.com/music/Happy%20Whistling%20Ukulele.mp3
- **Destination**: `assets/audio/music/hub_theme.ogg`
- **Description**: Cheerful ukulele track perfect for the main hub world

### 2. Title Theme - "Funshine"
- **URL**: https://freepd.com/music/Funshine.mp3
- **Destination**: `assets/audio/music/title_theme.ogg`
- **Description**: Bright, welcoming music for the title screen

### 3. Ski Theme - "Mountain King"
- **URL**: https://freepd.com/music/Mountain%20King.mp3
- **Destination**: `assets/audio/music/ski_theme.ogg`
- **Description**: Adventure music perfect for skiing minigame

### 4. Pool Theme - "Pickled Pink"
- **URL**: https://freepd.com/upbeat.php (search for "Pickled Pink")
- **Alternative**: https://freepd.com/music/Pickled%20Pink.mp3
- **Destination**: `assets/audio/music/pool_theme.ogg`
- **Description**: Light, playful music for pool/billiards game

### 5. Vegas Theme - "City Sunshine"
- **URL**: https://freepd.com/upbeat.php (search for "City Sunshine")
- **Alternative**: https://freepd.com/music/City%20Sunshine.mp3
- **Destination**: `assets/audio/music/vegas_theme.ogg`
- **Description**: Upbeat music for the Vegas-style minigame

## Sound Effects to Download

Visit https://mixkit.co/free-sound-effects/game/ and download:

### 1. Jump Sound
- **Search**: "Player jumping in a video game"
- **Destination**: `assets/audio/sfx/jump.ogg`

### 2. Collect/Coin Sound
- **Search**: "Winning a coin, video game"
- **Destination**: `assets/audio/sfx/collect_item.ogg`

### 3. Menu Click Sound
- **Search**: "Video game retro click"
- **Destination**: `assets/audio/sfx/menu_select.ogg`

### 4. Victory Sound
- **Search**: "Game level completed"
- **Destination**: `assets/audio/sfx/victory.ogg`

### 5. Attack/Action Sound
- **Search**: "Martial arts fast punch"
- **Destination**: `assets/audio/sfx/attack.ogg`

## Conversion Process

### Using FFmpeg (Command Line)
```bash
# Convert MP3 to OGG
ffmpeg -i input.mp3 -c:a libvorbis -q:a 4 output.ogg

# Convert WAV to OGG
ffmpeg -i input.wav -c:a libvorbis -q:a 4 output.ogg

# Batch conversion example
for file in *.mp3; do
    ffmpeg -i "$file" -c:a libvorbis -q:a 4 "${file%.mp3}.ogg"
done
```

### Using Online Converter
1. Go to https://convertio.co/mp3-ogg/
2. Upload your MP3/WAV file
3. Select OGG as output format
4. Set quality to "High" (around 192 kbps)
5. Download the converted file

## File Size Guidelines

- **Music files**: 500KB - 2MB (typically 1-3 minutes)
- **Sound effects**: 10KB - 50KB (typically 0.5-2 seconds)

## License Information

All FreePD.com files are **Creative Commons 0** - completely free for commercial and non-commercial use, no attribution required.

All Mixkit files are **royalty-free** and can be used in commercial projects.

## Quality Settings

For OGG conversion, use these quality settings:
- **Music**: Quality 4-6 (roughly 128-192 kbps)
- **Sound Effects**: Quality 3-4 (roughly 96-128 kbps)

## Batch Download Script

Create a script called `download_audio.py`:

```python
import urllib.request
import os

# Music files
music_files = {
    "hub_theme.mp3": "https://freepd.com/music/Happy%20Whistling%20Ukulele.mp3",
    "title_theme.mp3": "https://freepd.com/music/Funshine.mp3",
    "ski_theme.mp3": "https://freepd.com/music/Mountain%20King.mp3",
    # Add others as you find the direct URLs
}

# Create directories if they don't exist
os.makedirs("assets/audio/music", exist_ok=True)
os.makedirs("assets/audio/sfx", exist_ok=True)

# Download each file
for filename, url in music_files.items():
    try:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, f"assets/audio/music/{filename}")
        print(f"✓ Downloaded {filename}")
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
```

## Manual Download Steps

1. **Open each URL in your browser**
2. **Right-click the audio player** and select "Save audio as..." or use the download button
3. **Save to a temporary folder** on your computer
4. **Convert to OGG format** using FFmpeg or online converter
5. **Move converted files** to the appropriate game directories
6. **Test in-game** to ensure audio plays correctly

## Testing Your Audio

After downloading and converting, test the audio in the game:

```bash
# Run the game to test
make run

# Or run in debug mode to see audio loading
make debug
```

The game will automatically load OGG files from the assets/audio directory.
