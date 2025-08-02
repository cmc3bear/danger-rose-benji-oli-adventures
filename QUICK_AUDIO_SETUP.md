# Quick Audio Setup for Danger Rose

## Current Status
Your project already has placeholder audio files in OGG format. The current files are very small (~8-40KB) which indicates they are likely low-quality placeholders or very short clips.

## Immediate Action Steps

### Option 1: Use Provided Scripts
1. Run `scripts\download_audio.bat` (Windows) or `python scripts/download_audio.py`
2. This will download high-quality public domain music and replace your placeholders

### Option 2: Manual High-Quality Downloads

#### Best Free Music Sources (Public Domain)
1. **FreePD.com** - No attribution required
   - Visit: https://freepd.com/upbeat.php
   - Download: "Happy Whistling Ukulele" for hub theme
   - Download: "Funshine" for title theme
   - All files are MP3, convert to OGG using online converter or ffmpeg

2. **Kevin MacLeod (Incompetech.com)** - Requires attribution
   - Visit: https://incompetech.com/music/royalty-free/music.html
   - Search for: "Carefree", "Wallpaper", "Sneaky Snitch" (all family-friendly)
   - License: CC Attribution (add to game credits)

#### Best Free SFX Sources
1. **Mixkit.co** - No attribution required
   - Visit: https://mixkit.co/free-sound-effects/game/
   - Download various game sounds (jump, collect, menu, etc.)

2. **Freesound.org** - Community sounds
   - Visit: https://freesound.org
   - Filter by: CC0 (Public Domain) license
   - Search: "game jump", "coin collect", "menu click"

### Option 3: Quick Quality Improvement

If you want to keep your current files but improve them:

#### Using Audacity (Free)
1. Download Audacity: https://www.audacityteam.org/
2. Open your current audio files
3. Apply effects:
   - Effect → Amplify (normalize volume)
   - Effect → Noise Reduction (clean up audio)
   - Effect → Compressor (even out levels)
4. Export as OGG Vorbis (Quality 5-6)

## Recommended Immediate Downloads

### For Hub Theme (Cozy Family Feeling)
**Direct Link**: https://freepd.com/music/Happy%20Whistling%20Ukulele.mp3
- Right-click → Save As → hub_theme.mp3
- Convert to OGG using online converter or ffmpeg
- Replace: `assets/audio/music/hub_theme.ogg`

### For Title Screen (Exciting Welcome)
**Direct Link**: https://freepd.com/music/Funshine.mp3
- Right-click → Save As → title_theme.mp3
- Convert to OGG and replace: `assets/audio/music/title_theme.ogg`

### For Ski Game (Energetic Adventure)
**Direct Link**: https://freepd.com/music/Mountain%20King.mp3
- Energetic classical piece perfect for skiing
- Convert to OGG and replace: `assets/audio/music/ski_theme.ogg`

### For Pool Game (Playful Fun)
**Search**: https://freepd.com/cheerful.php
- Look for "Silly Fun" or similar upbeat tracks
- Convert to OGG and replace: `assets/audio/music/pool_theme.ogg`

### For Vegas Game (Arcade Energy)
**Search**: https://freepd.com/electronic.php
- Look for "8-bit" or "Arcade" style tracks
- Avoid anything with gambling themes
- Convert to OGG and replace: `assets/audio/music/vegas_theme.ogg`

## Quick Sound Effects

### Essential SFX Downloads (Mixkit.co)
1. **Jump Sound**: https://mixkit.co/free-sound-effects/game/
   - Search "jump" → Download "Game jump coin"
   - Save as: `assets/audio/sfx/jump.ogg`

2. **Collect Sound**: Search "bonus" → Download "Game bonus reached"
   - Save as: `assets/audio/sfx/collect_item.ogg`

3. **Menu Sounds**: Search "interface" → Download "Interface click"
   - Save as: `assets/audio/sfx/menu_select.ogg`

4. **Victory Sound**: Search "level complete" → Download "Completion of a level"
   - Save as: `assets/audio/sfx/victory.ogg`

## Audio Conversion Tools

### Online Converters (No Installation)
1. **CloudConvert**: https://cloudconvert.com/mp3-to-ogg
   - Upload MP3 → Convert to OGG → Download
   - Free, no registration required

2. **Online-Convert**: https://audio.online-convert.com/convert-to-ogg
   - Upload audio → Convert → Download

### Desktop Tools
1. **FFmpeg** (Command Line): https://ffmpeg.org/download.html
   ```bash
   ffmpeg -i input.mp3 -codec:a libvorbis -q:a 4 output.ogg
   ```

2. **Audacity** (GUI): https://www.audacityteam.org/
   - Open file → File → Export → Export as OGG

## File Size Guidelines

### Current vs. Target Sizes
- **Current music files**: ~8-40KB (too small - likely placeholders)
- **Target music files**: 500KB - 2MB (2-3 minute loops)
- **Current SFX files**: ~4-70KB (some okay, some too small)
- **Target SFX files**: 10-50KB (1-3 second clips)

### Quality Settings
- **Music**: OGG Quality 4-5 (128-160 kbps)
- **SFX**: OGG Quality 5-6 (160-192 kbps)
- **Sample Rate**: 44.1kHz (CD quality)
- **Channels**: Stereo for music, Mono for SFX

## Testing Your Audio

### In-Game Testing
1. Run: `make run` (or `poetry run python src/main.py`)
2. Listen for:
   - Consistent volume levels
   - Clear audio quality
   - Appropriate mood for each scene
   - No distortion or clipping

### Audio Validation Script
```python
# Quick test script
import pygame
pygame.mixer.init()

# Test loading all audio files
music_files = ['hub_theme.ogg', 'title_theme.ogg', 'ski_theme.ogg', 'pool_theme.ogg', 'vegas_theme.ogg']
sfx_files = ['jump.ogg', 'collect_item.ogg', 'menu_select.ogg', 'victory.ogg']

for file in music_files:
    try:
        pygame.mixer.music.load(f'assets/audio/music/{file}')
        print(f'✓ {file} loads correctly')
    except:
        print(f'✗ {file} failed to load')

for file in sfx_files:
    try:
        sound = pygame.mixer.Sound(f'assets/audio/sfx/{file}')
        print(f'✓ {file} loads correctly')
    except:
        print(f'✗ {file} failed to load')
```

## License Compliance

### Public Domain (FreePD.com)
- ✅ No attribution required
- ✅ Use anywhere, including commercial games
- ✅ Modify as needed

### Creative Commons Attribution (Incompetech.com)
- ⚠️ Attribution required in game credits
- ✅ Commercial use allowed
- Example credit: "Music by Kevin MacLeod (incompetech.com)"

### Mixkit License
- ✅ No attribution required
- ✅ Commercial use allowed
- ❌ Cannot resell audio files separately

## Next Steps

1. **Priority 1**: Replace music files with high-quality versions (500KB-2MB each)
2. **Priority 2**: Add missing sound effects (jump variations, UI sounds)
3. **Priority 3**: Test all audio in-game for volume consistency
4. **Priority 4**: Add license information to game credits
5. **Priority 5**: Consider adding more audio layers (ambient sounds, etc.)

## Quick Win: 15-Minute Audio Upgrade

1. Visit https://freepd.com/upbeat.php
2. Download "Happy Whistling Ukulele" → Convert to OGG → Replace hub_theme.ogg
3. Visit https://mixkit.co/free-sound-effects/game/
4. Download 3-4 game sound effects → Convert to OGG → Replace current SFX
5. Test in-game: `make run`

This will immediately improve your game's audio quality with minimal effort!
