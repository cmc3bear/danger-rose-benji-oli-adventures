# Cut Sprite Sheet

Extract individual frames from a sprite sheet with proper dimensions for character animations.

## Usage

```bash
# Cut sprite sheet with default dimensions (256x341)
poetry run python tools/sprite_cutter.py assets/images/characters/danger.png

# Cut with custom dimensions
poetry run python tools/sprite_cutter.py assets/images/characters/boss.png --width 512 --height 512

# Cut and save to specific directory
poetry run python tools/sprite_cutter.py assets/images/enemies/spider.png --output assets/frames/spider/

# Cut with custom grid layout
poetry run python tools/sprite_cutter.py assets/images/tiles/tileset.png --rows 4 --cols 8
```

## Sprite Sheet Specifications

### Standard Character Sheet
- Full sheet: 1024x1024 pixels
- Grid: 3 rows x 4 columns
- Frame size: 256x341 pixels
- Total frames: 12

### Frame Layout
```
Row 1: idle_1, idle_2, idle_3, idle_4
Row 2: walk_1, walk_2, walk_3, walk_4
Row 3: jump_1, attack_1, hurt_1, victory_1
```

## Tool Implementation

Create this tool at `tools/sprite_cutter.py`:

```python
from PIL import Image
import sys
from pathlib import Path

def cut_sprite_sheet(sheet_path, frame_width=256, frame_height=341, rows=3, cols=4):
    """Cut sprite sheet into individual frames"""
    sheet = Image.open(sheet_path)
    frames = []

    for row in range(rows):
        for col in range(cols):
            x = col * frame_width
            y = row * frame_height
            frame = sheet.crop((x, y, x + frame_width, y + frame_height))
            frames.append(frame)

    return frames

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sprite_cutter.py <sprite_sheet.png>")
        sys.exit(1)

    sheet_path = sys.argv[1]
    frames = cut_sprite_sheet(sheet_path)

    # Save frames
    output_dir = Path(sheet_path).parent / Path(sheet_path).stem
    output_dir.mkdir(exist_ok=True)

    for i, frame in enumerate(frames):
        frame.save(output_dir / f"frame_{i:02d}.png")

    print(f"Extracted {len(frames)} frames to {output_dir}")
```

## Validation

After cutting, the tool will:
1. Check frame dimensions match expected size
2. Verify transparency is preserved
3. Ensure no frames are completely empty
4. Generate a preview sheet showing all frames

## Common Issues

- **Black borders**: Original sheet may need trimming
- **Misaligned frames**: Check grid dimensions match sheet
- **Lost transparency**: Ensure PNG format with alpha channel
