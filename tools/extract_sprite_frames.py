#!/usr/bin/env python3
"""
Sprite Frame Extraction Tool for Danger Rose
Extracts individual animation frames from sprite sheets and organizes them properly.
"""

import json
import sys
from pathlib import Path

from PIL import Image

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


class SpriteExtractor:
    def __init__(self):
        self.assets_dir = project_root / "assets" / "images" / "characters"
        self.new_sprites_dir = self.assets_dir / "new_sprites"

        # Animation mapping for Kenney sprites
        self.kenney_animations = {
            # Row 1: Idle and walk cycles
            0: [("idle", 4), ("walk", 9)],  # 4 idle frames, 9 walk frames
            # Row 2: More walk frames and actions
            1: [("walk_extra", 9), ("action", 6)],  # Additional frames
            # Row 3: Special actions
            2: [("jump", 3), ("victory", 4), ("hurt", 2), ("misc", 6)],
        }

        # Character mapping
        self.characters = {
            "danger_kenney.png": "danger",
            "rose_kenney.png": "rose",
            "dad_kenney.png": "dad",
        }

    def extract_kenney_sprites(self):
        """Extract frames from Kenney-style sprite sheets"""
        for sprite_file, character_name in self.characters.items():
            sprite_path = self.assets_dir / sprite_file

            if not sprite_path.exists():
                print(f"Warning: {sprite_file} not found")
                continue

            print(f"Processing {character_name} from {sprite_file}")

            # Load sprite sheet
            sprite_sheet = Image.open(sprite_path)
            sheet_width, sheet_height = sprite_sheet.size

            # Calculate frame dimensions (assuming 9 columns)
            frame_width = sheet_width // 9
            frame_height = sheet_height // 3  # 3 rows

            print(f"  Sheet size: {sheet_width}x{sheet_height}")
            print(f"  Frame size: {frame_width}x{frame_height}")

            # Create character directory
            char_dir = self.new_sprites_dir / character_name / "hub"
            char_dir.mkdir(parents=True, exist_ok=True)

            # Extract frames by animation type
            self._extract_animations(sprite_sheet, char_dir, frame_width, frame_height)

            # Create metadata
            self._create_metadata(char_dir, character_name)

    def _extract_animations(self, sprite_sheet, output_dir, frame_width, frame_height):
        """Extract animation frames from sprite sheet"""
        animation_counts = {}

        for row in range(3):  # 3 rows
            y = row * frame_height
            col = 0

            for anim_name, frame_count in self.kenney_animations[row]:
                animation_counts[anim_name] = frame_count

                for frame_num in range(frame_count):
                    if col >= 9:  # Max 9 columns
                        break

                    x = col * frame_width

                    # Extract frame
                    frame = sprite_sheet.crop((x, y, x + frame_width, y + frame_height))

                    # Save frame
                    frame_filename = f"{anim_name}_{frame_num + 1:02d}.png"
                    frame_path = output_dir / frame_filename
                    frame.save(frame_path, "PNG")

                    col += 1

                print(f"    Extracted {frame_count} frames for {anim_name}")

        return animation_counts

    def _create_metadata(self, output_dir, character_name):
        """Create metadata file for animations"""
        metadata = {
            "character": character_name,
            "art_style": "kenney_cartoon",
            "animations": {
                "idle": {"frames": 4, "frame_rate": 8, "loop": True},
                "walk": {"frames": 9, "frame_rate": 12, "loop": True},
                "walk_extra": {
                    "frames": 9,
                    "frame_rate": 12,
                    "loop": True,
                    "description": "Additional walk cycle frames",
                },
                "action": {
                    "frames": 6,
                    "frame_rate": 10,
                    "loop": False,
                    "description": "Generic action animation",
                },
                "jump": {"frames": 3, "frame_rate": 6, "loop": False},
                "victory": {"frames": 4, "frame_rate": 8, "loop": False},
                "hurt": {"frames": 2, "frame_rate": 4, "loop": False},
                "misc": {
                    "frames": 6,
                    "frame_rate": 8,
                    "loop": False,
                    "description": "Miscellaneous animation frames",
                },
            },
            "source": "kenney_platformer_pack",
            "license": "CC0",
            "extracted_date": "2025-07-29",
        }

        metadata_path = output_dir / "animation_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"    Created metadata file: {metadata_path}")

    def create_scene_variants(self):
        """Create placeholder scene variants (copies for now)"""
        scenes = ["pool", "vegas", "ski"]

        for character in ["danger", "rose", "dad"]:
            hub_dir = self.new_sprites_dir / character / "hub"

            if not hub_dir.exists():
                print(f"Warning: Hub sprites for {character} not found")
                continue

            for scene in scenes:
                scene_dir = self.new_sprites_dir / character / scene
                scene_dir.mkdir(parents=True, exist_ok=True)

                # Copy hub sprites as placeholders
                for sprite_file in hub_dir.glob("*.png"):
                    if sprite_file.name != "animation_metadata.json":
                        target_path = scene_dir / sprite_file.name
                        sprite_file.replace(target_path)

                print(f"    Created {scene} variants for {character}")

    def generate_outfit_guide(self):
        """Generate a guide for creating outfit variations"""
        guide_content = """# Outfit Variation Guide

## Scene-Specific Outfits Needed

### Pool Scene
- **Danger**: Swimming trunks (blue/green), water goggles, flip-flops
- **Rose**: One-piece swimsuit (pink/purple), swim cap, beach sandals
- **Dad**: Board shorts (navy), rash guard shirt, sun hat

### Vegas Scene (Adventure/Casual)
- **Danger**: Cargo shorts, t-shirt, sneakers, small backpack
- **Rose**: Sundress or shorts/top, comfortable shoes, sun hat
- **Dad**: Khaki pants, polo shirt, hiking boots, camera strap

### Ski Scene (Winter)
- **Danger**: Snow pants, puffy jacket, winter hat, ski goggles, boots
- **Rose**: Pink/purple ski outfit, warm hat, mittens, snow boots
- **Dad**: Adult ski gear, winter coat, wool hat, snow boots

## Color Schemes to Maintain
- **Danger**: Green accents (helmet/hat colors)
- **Rose**: Pink/purple accents, brown hair
- **Dad**: Blue/navy accents, casual dad style

## Modification Notes
1. Keep same body proportions and animation frames
2. Only change clothing/accessories
3. Maintain character personality through outfit choices
4. Ensure outfits work for all animation states
"""

        guide_path = self.new_sprites_dir / "OUTFIT_GUIDE.md"
        with open(guide_path, "w") as f:
            f.write(guide_content)

        print(f"Created outfit guide: {guide_path}")


def main():
    """Main execution function"""
    print("Danger Rose Sprite Extraction Tool")
    print("=" * 40)

    extractor = SpriteExtractor()

    # Extract frames from existing Kenney sprites
    print("\\n1. Extracting frames from Kenney sprite sheets...")
    extractor.extract_kenney_sprites()

    # Create scene variant placeholders
    print("\\n2. Creating scene variant placeholders...")
    extractor.create_scene_variants()

    # Generate outfit guide
    print("\\n3. Generating outfit variation guide...")
    extractor.generate_outfit_guide()

    print("\\n" + "=" * 40)
    print("Extraction complete!")
    print(f"Check: {extractor.new_sprites_dir}")
    print("\\nNext steps:")
    print("1. Review extracted frames")
    print("2. Create outfit variations based on OUTFIT_GUIDE.md")
    print("3. Test sprites in game scenes")


if __name__ == "__main__":
    main()
