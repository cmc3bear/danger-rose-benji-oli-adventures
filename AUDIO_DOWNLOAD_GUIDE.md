# Danger Rose Audio Download Guide

## High-Quality Family-Friendly Audio Sources

### Background Music Downloads

#### 1. Hub Theme (Cozy, Family-Friendly)
**Recommended Track**: "Happy Whistling Ukulele" by Kevin MacLeod
- **Source**: FreePD.com
- **URL**: https://freepd.com/music/Happy%20Whistling%20Ukulele.mp3
- **License**: Public Domain
- **Description**: Happy, positive and cheerful track featuring ukulele, light percussion and uplifting vibe
- **Save As**: `hub_theme.ogg`

**Alternative**: "Kidding Around" by Ahjay Stelino
- **Source**: Mixkit.co
- **URL**: https://mixkit.co/free-stock-music/tag/children/
- **License**: Mixkit License (Free Commercial Use)

#### 2. Pool Theme (Playful, Upbeat)
**Recommended Track**: "Splashing Around" by Kevin MacLeod
- **Source**: FreePD.com
- **URL**: https://freepd.com/music/Splashing%20Around.mp3
- **License**: Public Domain
- **Description**: Playful, bouncy track perfect for water-themed games
- **Save As**: `pool_theme.ogg`

**Alternative**: Search Mixkit for "playful" or "children" tagged music
- **Source**: https://mixkit.co/free-stock-music/tag/playful/

#### 3. Ski Theme (Winter Adventure, Energetic)
**Recommended Track**: "Mountain Expedition" by Kevin MacLeod
- **Source**: FreePD.com
- **URL**: https://freepd.com/music/Mountain%20Expedition.mp3
- **License**: Public Domain
- **Description**: Energetic, adventurous track with winter/mountain feel
- **Save As**: `ski_theme.ogg`

**Alternative**: "The Greatest Comeback" by Michael Ramir C.
- **Source**: Mixkit.co
- **URL**: https://mixkit.co/free-stock-music/

#### 4. Vegas Theme (Fun, Energetic Arcade)
**Recommended Track**: "Arcade Funtime" by Kevin MacLeod
- **Source**: FreePD.com
- **URL**: https://freepd.com/music/Arcade%20Funtime.mp3
- **License**: Public Domain
- **Description**: Fun, energetic arcade-style music (no gambling themes)
- **Save As**: `vegas_theme.ogg`

#### 5. Title Theme (Welcoming, Exciting)
**Recommended Track**: "Funshine" by Kevin MacLeod
- **Source**: FreePD.com
- **URL**: https://freepd.com/music/Funshine.mp3
- **License**: Public Domain
- **Description**: Uplifting and energetic welcome music
- **Save As**: `title_theme.ogg`

### Sound Effects Downloads

#### Jump Sounds (3-4 variations)
**Source**: Mixkit Game Sound Effects
- **URL**: https://mixkit.co/free-sound-effects/game/
- **Recommended**:
  - "Game jump coin"
  - "Quick jump arcade"
  - "Retro game notification"
- **Save As**: `jump_1.ogg`, `jump_2.ogg`, `jump_3.ogg`

#### Attack/Action Sounds
**Source**: Mixkit
- **Recommended**:
  - "Game punch hit"
  - "Arcade game jump"
- **Save As**: `attack_1.ogg`, `attack_2.ogg`

#### Collect Item Sounds
**Source**: Mixkit
- **Recommended**:
  - "Game bonus reached"
  - "Arcade bonus notification"
  - "Prize earned sound effect"
- **Save As**: `collect_coin.ogg`, `collect_powerup.ogg`

#### Door Opening Sounds
**Source**: Mixkit
- **Recommended**:
  - "Door opening sound effect"
  - "Wooden door opening"
- **Save As**: `door_open.ogg`

#### Menu Navigation Sounds
**Source**: Mixkit
- **Recommended**:
  - "Interface click notification"
  - "Game interface beep"
- **Save As**: `menu_select.ogg`, `menu_navigate.ogg`

#### Player Hurt Sounds
**Source**: Mixkit (Look for gentle, not scary sounds)
- **Recommended**:
  - "Game over notification" (gentle version)
  - "Error notification" (soft)
- **Save As**: `player_hurt.ogg`

#### Victory/Celebration Sounds
**Source**: Mixkit
- **Recommended**:
  - "Level completion notification"
  - "Victory fanfare"
  - "Achievement unlocked"
- **Save As**: `victory.ogg`, `celebration.ogg`

#### Splash/Water Sounds
**Source**: Mixkit or FreeSFX
- **Recommended**:
  - "Water splash"
  - "Pool splash sound"
- **Save As**: `splash.ogg`

## Download Instructions

### Step 1: Create Download Script
```bash
# Create a batch download script
mkdir -p assets/downloads/temp_audio

# Download all music files (replace URLs with actual links)
wget -O "assets/downloads/temp_audio/hub_theme.mp3" "https://freepd.com/music/Happy%20Whistling%20Ukulele.mp3"
wget -O "assets/downloads/temp_audio/pool_theme.mp3" "https://freepd.com/music/Splashing%20Around.mp3"
# ... continue for all tracks
```

### Step 2: Convert to OGG Format
```bash
# Install ffmpeg if not already installed
# Convert all MP3 files to OGG
for file in assets/downloads/temp_audio/*.mp3; do
    base=$(basename "$file" .mp3)
    ffmpeg -i "$file" -codec:a libvorbis -q:a 4 "assets/audio/music/$base.ogg"
done

# Convert WAV to OGG for sound effects
for file in assets/downloads/temp_audio/*.wav; do
    base=$(basename "$file" .wav)
    ffmpeg -i "$file" -codec:a libvorbis -q:a 5 "assets/audio/sfx/$base.ogg"
done
```

### Step 3: Normalize Audio Levels
```bash
# Normalize all music to consistent volume
ffmpeg-normalize assets/audio/music/*.ogg --normalization-type rms --target-level -23

# Normalize SFX to consistent levels
ffmpeg-normalize assets/audio/sfx/*.ogg --normalization-type peak --target-level -6
```

### Step 4: Validate Audio Files
```bash
# Check file integrity and format
for file in assets/audio/music/*.ogg assets/audio/sfx/*.ogg; do
    echo "Checking $file:"
    ffprobe -v quiet -show_format -show_streams "$file"
done
```

## Alternative High-Quality Sources

### Backup Music Sources
1. **OpenGameArt.org** - CC-licensed game music
   - URL: https://opengameart.org/art-search-advanced?keys=&field_art_type_tid%5B%5D=12
   - Filter by: CC0 (Public Domain)

2. **Incompetech.com** - Kevin MacLeod's extensive library
   - URL: https://incompetech.com/music/royalty-free/music.html
   - License: CC Attribution (credit required)

3. **Zapsplat.com** - Professional audio library
   - URL: https://www.zapsplat.com
   - License: Free with account, commercial use allowed

### Backup SFX Sources
1. **FreeSound.org** - Community-driven sound library
   - URL: https://freesound.org
   - Filter by: CC0 or CC Attribution

2. **Adobe Audition's built-in library** - If you have access
   - High-quality, royalty-free game sounds

## License Compliance

### Public Domain (FreePD.com)
- ✅ No attribution required
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ No restrictions

### Mixkit License
- ✅ Commercial use allowed
- ✅ No attribution required for most content
- ✅ Can be used in games and apps
- ❌ Cannot resell as standalone audio

### Creative Commons Attribution
- ✅ Commercial use allowed
- ⚠️ Attribution required (include in game credits)
- ✅ Modification allowed

## Audio Specifications Met

### Music Files
- Format: OGG Vorbis
- Sample Rate: 44.1kHz
- Bit Depth: 16-bit minimum
- Channels: Stereo
- Quality: VBR Q4 (approximately 128 kbps)
- Loop-friendly (trimmed for seamless loops)

### Sound Effects
- Format: OGG Vorbis
- Sample Rate: 44.1kHz
- Bit Depth: 16-bit
- Channels: Mono (for smaller file sizes)
- Quality: VBR Q5 (approximately 160 kbps)
- Normalized levels for consistency

## Final File Structure
```
assets/audio/
├── music/
│   ├── hub_theme.ogg      # Cozy family theme
│   ├── pool_theme.ogg     # Playful water game
│   ├── ski_theme.ogg      # Energetic winter adventure
│   ├── vegas_theme.ogg    # Fun arcade style
│   └── title_theme.ogg    # Welcoming main menu
└── sfx/
    ├── jump_1.ogg
    ├── jump_2.ogg
    ├── jump_3.ogg
    ├── attack_1.ogg
    ├── attack_2.ogg
    ├── collect_coin.ogg
    ├── collect_powerup.ogg
    ├── door_open.ogg
    ├── menu_select.ogg
    ├── menu_navigate.ogg
    ├── player_hurt.ogg
    ├── victory.ogg
    ├── celebration.ogg
    └── splash.ogg
```

## Quality Control Checklist

- [ ] All files are family-friendly (no scary or inappropriate content)
- [ ] Consistent audio levels across all files
- [ ] Proper OGG Vorbis encoding
- [ ] Seamless loops for music tracks
- [ ] Short duration for sound effects (< 3 seconds)
- [ ] License compliance documented
- [ ] File naming matches game code expectations
- [ ] Audio quality meets 44.1kHz/16-bit minimum
- [ ] File sizes optimized for game distribution

## Next Steps

1. Download files from recommended sources
2. Convert to OGG format using ffmpeg
3. Normalize audio levels
4. Test in-game to ensure proper playback
5. Document licenses in game credits
6. Replace placeholder audio files

This curated selection provides a cohesive, family-friendly audio experience that enhances gameplay without being distracting or inappropriate for younger players.
