# <¨ Danger Rose - Asset Requirements

## Table of Contents
1. [Overview](#overview)
2. [Character Sprites](#character-sprites)
3. [Environment Assets](#environment-assets)
4. [UI Elements](#ui-elements)
5. [Audio Assets](#audio-assets)
6. [Visual Effects](#visual-effects)
7. [File Naming Conventions](#file-naming-conventions)
8. [Asset Sources](#asset-sources)
9. [Technical Specifications](#technical-specifications)

## Overview

This document outlines all asset requirements for Danger Rose. Assets should be kid-friendly, colorful, and maintain a consistent art style throughout the game.

### Art Style Guidelines
- **Style**: Cartoon/pixel art hybrid
- **Colors**: Bright, saturated palette
- **Outlines**: 2-4 pixel black outlines for clarity
- **Shading**: Simple 3-tone shading (base, shadow, highlight)
- **Perspective**: Side view for characters, 3/4 top-down for environments

## Character Sprites

### Main Characters

#### Sprite Sheet Specifications
```yaml
Format: PNG with transparency
Dimensions: 1024x1024 pixels (full sheet)
Grid: 3 rows x 4 columns = 12 frames
Frame Size: 256x341 pixels per frame
Display Size: 128x128 (scaled down in-game)
```

#### Required Animation Sets

| Character | Idle | Walk | Jump | Attack | Hurt | Victory | Special |
|-----------|------|------|------|--------|------|---------|---------|
| Danger | 4 frames | 8 frames | 3 frames | 6 frames | 2 frames | 8 frames | Double Jump (3) |
| Rose | 4 frames | 8 frames | 3 frames | 6 frames | 2 frames | 8 frames | Precision Aim (4) |
| Dad | 4 frames | 8 frames | 3 frames | 6 frames | 2 frames | 8 frames | Power Mode (6) |

#### Character Design Details

**Danger (Yasha)**
- Hair: Spiky brown
- Outfit: Blue t-shirt, red shorts, sneakers
- Accessories: Wristband, backpack
- Personality in design: Energetic poses

**Rose (Ellie)**
- Hair: Long pink/purple
- Outfit: Green dress, white leggings, boots
- Accessories: Hair bow, bracelet
- Personality in design: Graceful movements

**Dad**
- Hair: Short dark hair, slight stubble
- Outfit: Casual polo, jeans, sneakers
- Accessories: Watch, wedding ring (important!)
- Personality in design: Protective stance

### NPC Sprites

#### Hub World NPCs
- **Cat**: 32x32, idle animation (4 frames)
- **Fish (in tank)**: 16x16, swimming (6 frames)
- **Birds (window)**: 16x16, flying pattern

#### Minigame Characters
- **Ski Instructor**: 128x128, waving animation
- **Pool Lifeguard**: 128x128, whistle animation
- **Vegas Dealer**: 128x128, card shuffle animation

## Environment Assets

### Hub World (Apartment)

#### Tileset Requirements
```yaml
Living Room Tileset:
  - File: living_room_tiles.png
  - Tile Size: 64x64 pixels
  - Required Tiles:
    - Floor: Wood (3 variants)
    - Walls: Painted (4 colors)
    - Carpet: Cozy patterns (2 types)
    - Windows: Day/night variants
```

#### Furniture Sprites
| Asset | Size | Variants | Interactive |
|-------|------|----------|-------------|
| Couch | 256x128 | 3 colors | Yes (save point) |
| TV Stand | 192x96 | 1 | No |
| Trophy Shelf | 128x192 | Empty/Full | Yes (view scores) |
| Doors | 96x128 | 3 (one per game) | Yes (enter game) |
| Coffee Table | 128x64 | 1 | No |
| Potted Plants | 64x96 | 4 types | No |

### Ski Minigame Assets

#### Environment Tiles
```yaml
Ski Slope Tileset:
  - File: ski_tiles.png
  - Tile Size: 64x64 pixels
  - Tiles:
    - Snow: Clean, tracked, deep
    - Ice patches: 3 variants
    - Slope edges: Left, right, corners
    - Ski lift poles: Base, middle, top
```

#### Obstacles & Props
| Asset | Size | Collision Box | Notes |
|-------|------|---------------|-------|
| Pine Tree | 128x192 | 64x64 (base) | 3 variants |
| Rock | 64x48 | 48x32 | 2 variants |
| Jump Ramp | 128x64 | Full size | Animated flag |
| Finish Line | 256x128 | None | Animated banner |
| Snowflake | 32x32 | 24x24 | Rotating animation |

### Pool Minigame Assets

#### Pool Environment
```yaml
Pool Area Tileset:
  - File: pool_tiles.png
  - Tile Size: 64x64 pixels
  - Tiles:
    - Pool water: Animated (4 frames)
    - Pool edge: All directions
    - Concrete: Wet/dry variants
    - Grass: Poolside decoration
```

#### Game Objects
| Asset | Size | Animation | Purpose |
|-------|------|-----------|---------|
| Water Balloon | 32x32 | None | Projectile |
| Target Duck | 64x64 | Bob (4 frames) | Basic target |
| Beach Ball | 48x48 | Bounce (6 frames) | Bouncing target |
| Pool Ring | 64x64 | Float (4 frames) | Collectible |
| Water Splash | 128x128 | 8 frames | Hit effect |

### Vegas Minigame Assets

#### Vegas Street Tileset
```yaml
Vegas Tileset:
  - File: vegas_tiles.png
  - Tile Size: 64x64 pixels
  - Tiles:
    - Sidewalk: Clean, cracked
    - Road: Asphalt with lines
    - Building facades: Neon variants
    - Casino carpets: 3 patterns
```

#### Vegas Props & Enemies
| Asset | Size | Type | Animation |
|-------|------|------|-----------|
| Slot Machine | 96x128 | Enemy | Spin reels (8 frames) |
| Neon Sign | 128x96 | Decoration | Flicker (4 frames) |
| Casino Chip | 32x32 | Collectible | Spin (8 frames) |
| Playing Card | 48x64 | Enemy projectile | Flip (4 frames) |
| Dice | 32x32 | Enemy | Roll (6 frames) |

#### Boss: Vegas Sphere
```yaml
Vegas Sphere Boss:
  - Size: 256x256 pixels
  - Faces: 3 (happy, angry, dizzy)
  - Animations per face:
    - Idle: 4 frames
    - Attack: 6 frames
    - Hurt: 2 frames
  - Special effects: Glow aura
```

## UI Elements

### Menu Components
```yaml
UI Sprite Sheet:
  - File: ui_elements.png
  - Components:
    - Buttons: 192x64 (normal, hover, pressed)
    - Text boxes: 9-slice borders
    - Health bars: Empty, full, segments
    - Score displays: Digital font style
```

### HUD Elements
| Element | Size | States | Notes |
|---------|------|--------|-------|
| Health Heart | 48x48 | Full, half, empty | Pulse animation |
| Score Counter | 256x64 | N/A | Digital display |
| Timer | 192x48 | Normal, warning | Red when < 10s |
| Combo Meter | 32x256 | 0-10 levels | Glow effect |

### Icons
```yaml
Icon Set:
  - Size: 64x64 pixels each
  - Required Icons:
    - Game mode icons (ski, pool, vegas)
    - Character portraits
    - Trophy/medal icons
    - Settings gear
    - Sound on/off
    - Fullscreen toggle
    - Arrow keys
    - Spacebar
    - Mouse cursor
```

## Audio Assets

### Music Tracks

| Track | Duration | Tempo | Style | Loop Point |
|-------|----------|-------|-------|------------|
| Title Theme | 2:00 | 120 BPM | Cheerful, welcoming | 0:30 |
| Hub Theme | 3:00 | 80 BPM | Cozy, relaxed | 1:00 |
| Ski Theme | 2:30 | 140 BPM | Energetic, winter | 0:45 |
| Pool Theme | 2:30 | 100 BPM | Tropical, fun | 0:40 |
| Vegas Theme | 3:00 | 128 BPM | Electronic, intense | 1:00 |
| Boss Theme | 2:00 | 160 BPM | Epic, challenging | 0:30 |
| Victory Fanfare | 0:10 | N/A | Celebratory | No loop |
| Game Over | 0:08 | N/A | Gentle, encouraging | No loop |

### Sound Effects

#### Universal SFX
```yaml
Menu Sounds:
  - menu_move.ogg: Navigation beep
  - menu_select.ogg: Confirmation chime
  - menu_back.ogg: Cancel sound
  - achievement.ogg: Unlock fanfare

Character Sounds:
  - footstep_carpet.ogg: Indoor walking
  - footstep_snow.ogg: Snow walking
  - jump.ogg: Jump vocalization
  - land.ogg: Landing thud
  - attack.ogg: Effort sound
  - hurt.ogg: Damage vocalization
  - victory.ogg: Celebration
```

#### Ski Minigame SFX
- ski_swoosh.ogg: Continuous skiing
- ski_jump.ogg: Ramp launch
- tree_crash.ogg: Collision impact
- snowflake_collect.ogg: Sparkle chime
- dad_cheer.ogg: Encouragement

#### Pool Minigame SFX
- water_splash.ogg: Balloon impact
- balloon_throw.ogg: Whoosh sound
- target_hit.ogg: Success ding
- ring_collect.ogg: Bonus chime
- power_up.ogg: Activation sound

#### Vegas Minigame SFX
- chip_collect.ogg: Casino chip pickup
- slot_spin.ogg: Reel spinning
- sword_slash.ogg: Attack swoosh
- rainbow_beam.ogg: Magic sound
- boss_roar.ogg: Sphere attack
- jackpot.ogg: Victory sound

## Visual Effects

### Particle Effects
```yaml
Effect Sprites:
  - File: particles.png
  - Effects:
    - Snow particles: 8x8, 16x16
    - Water droplets: 8x8
    - Sparkles: 16x16 (8 frames)
    - Smoke puffs: 32x32 (6 frames)
    - Confetti: 8x16 (multiple colors)
    - Speed lines: 64x8
```

### Screen Effects
- **Fade Transitions**: Black, white overlay
- **Screen Shake**: Collision feedback
- **Color Flash**: Damage/power-up
- **Vignette**: Focus during boss
- **Motion Blur**: Speed boost effect

## File Naming Conventions

### General Rules
```
[category]_[name]_[variant]_[state].[ext]

Examples:
- character_danger_idle_01.png
- tile_snow_clean.png
- ui_button_play_hover.png
- sfx_jump.ogg
- music_hub_theme.ogg
```

### Categories
- **character**: Player and NPC sprites
- **tile**: Environment tileset pieces
- **prop**: Interactive/decorative objects
- **ui**: Interface elements
- **vfx**: Visual effects
- **sfx**: Sound effects
- **music**: Background music
- **voice**: Character vocalizations

## Asset Sources

### Recommended Free Resources
1. **[Kenney.nl](https://kenney.nl)**
   - Character sprites
   - UI elements
   - Sound effects

2. **[OpenGameArt.org](https://opengameart.org)**
   - Tilesets
   - Background music
   - Particle effects

3. **[Freesound.org](https://freesound.org)**
   - Sound effects
   - Ambient sounds

4. **[Itch.io Asset Packs](https://itch.io/game-assets)**
   - Complete art packs
   - Themed assets

### Custom Asset Creation Tools
- **Pixel Art**: Aseprite, Piskel
- **Audio**: Bfxr, BeepBox, Audacity
- **Sprite Sheets**: TexturePacker
- **Tilesets**: Tiled Map Editor

## Technical Specifications

### Image Requirements
```yaml
Format: PNG (RGBA)
Color Depth: 32-bit
Compression: Lossless
Max File Size: 10MB per asset
Transparency: Required for sprites
Power of 2: Recommended for textures
```

### Audio Requirements
```yaml
Format: OGG Vorbis
Sample Rate: 44.1 kHz
Bit Depth: 16-bit
Channels: Stereo (music), Mono (SFX)
Max File Size: 5MB per track
Normalization: -3dB peak
```

### Performance Guidelines
- **Sprite Sheets**: Pack related animations
- **Texture Atlases**: Combine small sprites
- **Mipmaps**: Not required (2D game)
- **Audio Compression**: Quality 6-8
- **Load Priority**: Critical assets first

### Fallback System
```python
# Automatic placeholder generation
Placeholder Colors:
  - Missing Character: Magenta (#FF00FF)
  - Missing Tile: Cyan (#00FFFF)
  - Missing UI: Yellow (#FFFF00)
  - Missing VFX: Green (#00FF00)

Placeholder Text:
  - Font: System default
  - Size: 25% of asset height
  - Color: White with black outline
  - Content: Asset filename
```

---

*This asset requirements document should be updated as new assets are identified during development. Always prioritize free, family-friendly assets that match the game's cheerful aesthetic.*
