# Sound Generation Guide for Danger Rose

## Overview
This guide explains how to generate retro-style sound effects for Danger Rose using the 11labs API, with priority focus on Hub World and Drive minigame sounds. All sounds follow a classic 8-bit/16-bit arcade aesthetic.

## Prerequisites

1. **11labs API Key**: Located in `C:\dev\api-key-forge\vault\11LABS\API-KEY.txt`
2. **FFmpeg**: Required for audio conversion
   - Download from: https://ffmpeg.org/download.html
   - Add to system PATH

## Quick Start

### Generate Priority Sounds (Hub & Drive)
```bash
cd C:\dev\danger-rose
python tools\generate_sounds_11labs.py
```

This will:
1. Generate character voices for Danger, Rose, and Dad
2. Create retro Hub world interaction sounds (RPG-style)
3. Generate arcade Drive game sounds (racing game style)
4. Convert all sounds to optimized OGG format
5. Organize files in proper directory structure

### Apply Retro Processing
```bash
# Process generated sounds with retro effects
python tools\retro_sound_processor.py assets\audio\sfx\hub --preset 16bit
python tools\retro_sound_processor.py assets\audio\sfx\drive --preset arcade
```

## Sound Categories (Retro Style)

### Hub World (Priority) - 16-bit RPG Style
- **Character Voices**: Natural voices for personality
- **Movement**: Classic RPG footsteps, Mario-style jumps
- **Interactions**: Simple beeps and chimes
- **Ambient**: 8-bit room tones

### Drive Game (Priority) - Arcade Racing Style
- **Vehicle**: Retro engine sounds, Pac-Man horn
- **Collisions**: Bumper car impacts, arcade crashes
- **Environment**: Simple wind whooshes, retro traffic
- **UI**: Space Invaders warnings, arcade fanfares

### Retro Processing Presets
- **8bit**: Ultra-retro chiptune style (11kHz, mono)
- **16bit**: SNES-era quality (22kHz, stereo) 
- **arcade**: Classic arcade cabinet sound
- **chiptune**: Extreme 8-bit processing

## File Organization
```
assets/audio/sfx/
├── hub/
│   ├── character/     # Character voices
│   ├── ambient/       # Background sounds
│   └── interactive/   # Object interactions
├── drive/
│   ├── vehicle/       # Car sounds
│   ├── traffic/       # Environment
│   └── collision/     # Impact sounds
└── [other games...]
```

## Usage in Game

### Basic Integration
```python
# In hub scene
self.sound_manager.play_event("hub.character.danger_hello")
self.sound_manager.play_event("hub.interactive.door_open")

# In drive scene
self.sound_manager.play_event("drive.vehicle.engine_start")
self.sound_manager.play_event("drive.collision.collision_soft")
```

### With Spatial Audio
```python
# Play sound at specific position
player_pos = (self.player.x, self.player.y)
self.sound_manager.play_event("hub.character.footsteps_walk", position=player_pos)
```

## Troubleshooting

### API Key Not Found
- Check vault location: `C:\dev\api-key-forge\vault\11LABS\`
- Ensure file is named `API-KEY.txt`

### FFmpeg Not Found
- Install FFmpeg from official site
- Add to system PATH
- Restart terminal/IDE

### Generation Failed
- Check API quota/credits
- Verify internet connection
- Review error messages in console

## Next Steps

After generating priority sounds:
1. Test sounds in game scenes
2. Adjust volume levels as needed
3. Generate remaining game sounds
4. Implement spatial audio positioning
5. Add event triggers in gameplay

## Sound List Status

### Completed Priority Areas
- [x] Hub character voices
- [x] Hub interactions
- [x] Drive vehicle sounds
- [x] Drive collision effects
- [x] Drive environment

### Remaining Areas
- [ ] Ski game sounds
- [ ] Pool game sounds
- [ ] Vegas game sounds
- [ ] UI/menu sounds
- [ ] Victory/completion sounds

## Tips for Best Results

1. **Voice Selection**: Use appropriate voice IDs for different sound types
2. **Text Prompts**: Clear descriptions in brackets for sound effects
3. **Rate Limiting**: Script includes delays to respect API limits
4. **Batch Processing**: Generate related sounds together
5. **Quality Control**: Always validate generated files

---

For questions or issues, refer to Issue #33 in the project documentation.