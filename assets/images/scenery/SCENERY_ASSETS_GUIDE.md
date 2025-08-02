# Drive Minigame Scenery Assets Guide

This guide lists recommended free scenery assets for the Drive minigame background that match our pixel art style and are family-friendly.

## Asset Sources

### Primary Sources
1. **Kenney.nl** - CC0 licensed assets (no attribution required)
2. **OpenGameArt.org** - Various free licenses (check individual assets)

## Recommended Assets by Category

### 🌲 Trees & Forest Elements
**Source: OpenGameArt.org**
- **Pine Trees**: Search for "pine trees" - multiple pixel art options available
- **General Trees**: Look for "tree sprites" and "forest tilesets"
- **Forest Backgrounds**: Search "forest background" for complete scenes

**Recommended Search Terms:**
- "pine trees"
- "forest tileset"
- "tree sprites pixel art"

### 🏔️ Mountains
**Source: OpenGameArt.org**
- **Mountain Backgrounds**: Search "mountains background" 
- Features parallax-ready mountain silhouettes
- Simple color palettes that match our style

**Recommended Search Terms:**
- "mountains background"
- "mountain landscape pixel"
- "parallax mountains"

### 🏢 City/Buildings
**Source: Kenney.nl**
- **Tiny Town**: Contains building elements
- **Brick Pack**: Useful for urban structures

**Source: OpenGameArt.org**
- Search "city buildings" or "urban tileset"

### 💧 Water Elements
**Source: OpenGameArt.org**
- **Lakes**: Search "lake water"
- **Rivers**: Look for "river tiles"
- **Water Effects**: Animated water surfaces

**Recommended Search Terms:**
- "water tiles"
- "lake background"
- "animated water"

### 🌵 Desert Elements
**Source: OpenGameArt.org**
- **Cacti**: Search "desert cactus" - ~25 options available
- **Desert Rocks**: Look for "desert decoration"
- **Sand Dunes**: Search "desert background"

**Recommended Search Terms:**
- "desert cactus"
- "desert tileset"
- "sand dunes pixel"

## Asset Requirements

### Technical Specs
- **Format**: PNG with transparency
- **Style**: Pixel art or simple cartoon style
- **Size**: Small to medium (32x32 to 128x128 for individual elements)
- **Colors**: Bright, family-friendly palette

### Licensing
- ✅ CC0 (Public Domain) - Preferred
- ✅ CC BY (Attribution Required) - Acceptable
- ✅ CC BY-SA (Share Alike) - Acceptable
- ❌ Commercial licenses requiring payment

## Download Instructions

### From Kenney.nl
1. Browse to https://kenney.nl/assets
2. Filter by "2D" category
3. Look for relevant packs (Tiny Town, etc.)
4. Download ZIP files
5. Extract to appropriate scenery subdirectories

### From OpenGameArt.org
1. Go to https://opengameart.org
2. Use search terms from above
3. Check license on each asset page
4. Download individual assets
5. Organize by scenery type

## Asset Organization

Place downloaded assets in these directories:
```
assets/images/scenery/
├── trees/           # Pine trees, forest elements
├── mountains/       # Mountain backgrounds, hills
├── buildings/       # City skyline, urban elements  
├── water/          # Lakes, rivers, water effects
└── desert/         # Cacti, rocks, sand elements
```

## Integration Notes

### For Drive Minigame
- Use mountains as far background (parallax layer 1)
- Trees and buildings as mid-background (parallax layer 2)
- Desert/water elements as themed sections
- Ensure assets work at different scroll speeds

### Style Consistency
- Prefer pixel art style to match existing character sprites
- Use similar color palettes across biomes
- Maintain consistent lighting (top-down/side lighting)
- Keep detail level appropriate for background elements

## Next Steps

1. **Download Priority Assets**:
   - Start with pine trees (most versatile)
   - Get mountain backgrounds for depth
   - Add desert cacti for variety

2. **Test Integration**:
   - Import assets into game
   - Test parallax scrolling
   - Verify visual consistency

3. **Create Attribution File**:
   - Document asset sources
   - Include required attributions
   - Update ATTRIBUTION.md

## Attribution Template

When using assets from OpenGameArt.org, add to `assets/audio/ATTRIBUTION.md`:

```
# Scenery Assets

## Trees
- Pine Tree Pack: [Asset Name] by [Creator] (CC0/CC BY)
  Source: [URL]

## Mountains  
- Mountain Background: [Asset Name] by [Creator] (CC0/CC BY)
  Source: [URL]
```