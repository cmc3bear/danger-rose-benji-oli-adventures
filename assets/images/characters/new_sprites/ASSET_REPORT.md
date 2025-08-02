# Character Sprite Asset Report - Danger Rose

## Current Assets Status

### Existing Sprites (Good Quality)
1. **Kenney Style Characters** (Recommended for consistency)
   - `danger_kenney.png` - Complete animation set
   - `rose_kenney.png` - Complete animation set
   - `dad_kenney.png` - Complete animation set
   - Style: Cartoon/vector-like, family-friendly
   - Animations: Idle, walk, run, jump, victory states
   - Format: Sprite sheets with multiple frames

2. **Pixel Art Style Characters** (Alternative option)
   - `danger.png` - Green helmet kid, partial animations
   - `rose.png` - Brown hair kid, partial animations
   - Style: Retro pixel art
   - Animations: Idle, walk, attack (missing jump, hurt, victory)

## Recommended Approach

### Primary Recommendation: Expand Kenney Assets
The Kenney-style sprites you already have are perfect for a family game:
- Consistent cartoon art style
- Rich animation sets
- Professional quality
- Family-friendly appearance

### Scene-Specific Outfit Variations Needed
For each character (Danger, Rose, Dad), create outfit variants:

1. **Hub World (Home)** - Casual clothes (current sprites work)
2. **Pool Scene** - Swimwear/beach clothes
3. **Vegas Scene** - Casual outdoor clothes
4. **Ski Scene** - Winter gear/snow clothes

## Asset Sources Found

### High Quality Sources
1. **LPC Character Bases (OpenGameArt.org)**
   - Download: `lpc-character-bases-v3_1.zip` (34MB)
   - Includes: Child, teen, adult body types
   - Animations: Walk, cast, thrust, shoot, hurt, jump
   - License: CC-BY-SA 3.0 / GPL 3.0

2. **Sprout Lands Asset Pack (itch.io)**
   - Style: Cute 16-bit pixel art
   - Animations: Idle, walk, run, tilling, chopping, watering
   - Good for farming/casual scenes

3. **Kenney.nl Assets**
   - Your current sprites appear to be from Kenney
   - Consistent high-quality cartoon style
   - May have additional outfit variations available

## Implementation Plan

### Phase 1: Extract Current Sprites
1. Convert existing Kenney sprite sheets to individual PNG files
2. Organize by character → scene → animation state
3. Ensure consistent naming convention

### Phase 2: Create Scene Variants
1. **Pool Outfits**: Swimwear variations
   - Danger: Swimming trunks, goggles
   - Rose: One-piece swimsuit, swim cap
   - Dad: Board shorts, swim shirt

2. **Winter/Ski Outfits**: Snow gear
   - All characters: Winter coats, hats, snow boots
   - Maintain character colors (green for Danger, etc.)

3. **Vegas/Casual Outfits**: Adventure wear
   - Comfortable exploring clothes
   - Backpacks, hiking boots

### Phase 3: Missing Animations
Add any missing animation states:
- Hurt/damage animation
- Victory/celebration animation
- Scene-specific actions (swimming, skiing, etc.)

## File Naming Convention
```
assets/images/characters/new_sprites/
├── danger/
│   ├── hub/
│   │   ├── idle_01.png
│   │   ├── idle_02.png
│   │   ├── walk_01.png
│   │   └── ...
│   ├── pool/
│   ├── vegas/
│   └── ski/
├── rose/
└── dad/
```

## Next Steps
1. Download LPC character bases for reference
2. Extract frames from existing Kenney sprites
3. Create outfit variations using existing art style
4. Test sprites in game scenes
5. Create missing animation frames if needed

## Quality Standards
- Maintain consistent art style (prefer Kenney cartoon style)
- Family-friendly appearance
- Clear, readable at game resolution
- Smooth animation transitions
- Proper transparency (PNG format)
