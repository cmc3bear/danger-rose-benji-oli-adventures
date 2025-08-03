# Character Animation Guide

This guide documents the animation system used for Danger Rose characters and provides guidelines for creating consistent animations for new characters.

## Animation System Overview

The game uses a sprite sheet-based animation system defined in `src/utils/attack_character.py`.

### Sprite Sheet Specifications
- **Full Sheet Size**: 1024x1024 pixels
- **Grid Layout**: 3 rows x 4 columns (12 frames total)
- **Frame Size**: 256x341 pixels per frame
- **Display Size**: 128x128 pixels (scaled in-game)

### Animation States and Frame Counts
```python
animation_frames = {
    "idle": 4,      # Frames 0-3
    "walk": 8,      # Frames 0-7  
    "jump": 3,      # Frames 0-2
    "attack": 6,    # Frames 0-5
    "hurt": 2,      # Frames 0-1
    "victory": 8    # Frames 0-7
}
```

### Animation Speeds (seconds per frame)
```python
animation_speeds = {
    "idle": 0.2,
    "walk": 0.1,
    "jump": 0.15,
    "attack": 0.0833,  # ~12 FPS
    "hurt": 0.2,
    "victory": 0.15
}
```

## Current Character Implementation Status

### ✅ Complete Characters
- **Benji**: Full sprite sets for all scenes with consistent metadata
- **Olive**: Full sprite sets for all scenes with consistent metadata

### ⚠️ Incomplete Characters  
- **Danger**: Missing action frames for pool, ski, and vegas scenes
- **Rose**: Missing action frames for pool, ski, and vegas scenes
- **Dad**: Missing action frames for pool, ski, and vegas scenes
- **Uncle Bear**: No sprite files exist yet

## Animation Style Guide

Based on analysis of existing characters (Danger, Rose, Dad), follow these principles:

### 1. Consistent Poses
- **Idle**: Standing neutral, slight breathing motion
- **Walk**: Side-view walking cycle with arm swing
- **Jump**: Three-phase jump (crouch, air, land)
- **Attack**: Dynamic action pose specific to minigame
- **Hurt**: Recoil or damage reaction
- **Victory**: Celebration or success pose

### 2. Color Palette
- Use consistent colors for each character across all animations
- Maintain clear outlines for visibility
- Consider the game's retro aesthetic

### 3. Scene-Specific Variations
Each minigame should have character-appropriate animations:
- **Ski**: Winter clothing, skiing poses
- **Pool**: Summer attire, water balloon throwing
- **Vegas**: Action poses, combat stances
- **Drive**: Driving poses, seated positions

## Creating New Character Animations

### Step 1: Create Sprite Sheet
1. Use 1024x1024 canvas
2. Arrange frames in 3x4 grid
3. Each frame should be 256x341 pixels
4. Leave transparent background

### Step 2: Create Metadata File
For each sprite sheet, create a corresponding `_metadata.json`:
```json
{
    "frame_width": 256,
    "frame_height": 341,
    "animations": {
        "idle": {"frames": 4, "row": 0},
        "walk": {"frames": 8, "row": 0},
        "jump": {"frames": 3, "row": 1},
        "attack": {"frames": 6, "row": 1},
        "hurt": {"frames": 2, "row": 2},
        "victory": {"frames": 8, "row": 2}
    }
}
```

### Step 3: File Structure
Place animations in appropriate directories:
```
assets/images/characters/
├── [character_name]/
│   ├── hub/
│   │   ├── [character]_hub_spritesheet.png
│   │   └── [character]_hub_spritesheet_metadata.json
│   ├── ski/
│   │   ├── [character]_ski_spritesheet.png
│   │   └── [character]_ski_spritesheet_metadata.json
│   ├── pool/
│   │   ├── [character]_pool_spritesheet.png
│   │   └── [character]_pool_spritesheet_metadata.json
│   ├── vegas/
│   │   ├── [character]_vegas_spritesheet.png
│   │   └── [character]_vegas_spritesheet_metadata.json
│   └── drive/
│       ├── [character]_drive_spritesheet.png
│       └── [character]_drive_spritesheet_metadata.json
```

## Testing Animations

Use the visual test tools to verify animations:
```bash
python tools/visual/test_character_animations.py [character_name]
```

This will display all animations for the character to ensure they're working correctly.

## Common Issues and Solutions

1. **Animation Flickering**: Check frame counts match metadata
2. **Wrong Speed**: Adjust animation_speeds values
3. **Missing Frames**: Ensure sprite sheet has all required frames
4. **Scaling Issues**: Verify frame dimensions are 256x341