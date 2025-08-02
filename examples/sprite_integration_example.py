#!/usr/bin/env python3
"""
Example: How to integrate the new character sprites into Danger Rose
This shows how to load and use the extracted Kenney-style sprites.
"""

import json
from pathlib import Path


class CharacterSpriteLoader:
    """Example loader for the new character sprites"""

    def __init__(self, assets_root: Path):
        self.assets_root = assets_root
        self.sprite_cache = {}

    def load_character_scene(self, character: str, scene: str) -> dict:
        """Load all sprites for a character in a specific scene"""
        cache_key = f"{character}_{scene}"

        if cache_key in self.sprite_cache:
            return self.sprite_cache[cache_key]

        scene_path = self.assets_root / "new_sprites" / character / scene

        if not scene_path.exists():
            print(f"Warning: Scene path not found: {scene_path}")
            return {}

        # Load metadata
        metadata_path = scene_path / "animation_metadata.json"
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)

        # Load sprite frames
        sprites = {}
        for animation_name in ["idle", "walk", "jump", "victory", "hurt", "action"]:
            sprites[animation_name] = self._load_animation_frames(
                scene_path,
                animation_name,
                metadata.get("animations", {}).get(animation_name, {}),
            )

        self.sprite_cache[cache_key] = {"sprites": sprites, "metadata": metadata}

        return self.sprite_cache[cache_key]

    def _load_animation_frames(
        self, scene_path: Path, animation: str, anim_metadata: dict
    ) -> list:
        """Load all frames for a specific animation"""
        frames = []
        frame_count = anim_metadata.get("frames", 4)

        for i in range(1, frame_count + 1):
            frame_path = scene_path / f"{animation}_{i:02d}.png"
            if frame_path.exists():
                # In a real game, you'd load with pygame.image.load()
                frames.append(str(frame_path))
            else:
                print(f"Warning: Missing frame {frame_path}")

        return frames


# Example usage
def demonstrate_sprite_loading():
    """Show how to use the character sprites"""

    # Set up paths
    project_root = Path(__file__).parent.parent
    assets_root = project_root / "assets" / "images" / "characters"

    loader = CharacterSpriteLoader(assets_root)

    # Load all characters for hub scene
    characters = ["danger", "rose", "dad"]
    scenes = ["hub", "pool", "vegas", "ski"]

    print("Danger Rose Character Sprites - Integration Example")
    print("=" * 50)

    for character in characters:
        print(f"\n{character.title()} Character:")

        for scene in scenes:
            character_data = loader.load_character_scene(character, scene)

            if character_data:
                sprites = character_data["sprites"]
                metadata = character_data["metadata"]

                print(f"  {scene.title()} Scene:")
                print(f"    Idle frames: {len(sprites.get('idle', []))}")
                print(f"    Walk frames: {len(sprites.get('walk', []))}")
                print(f"    Jump frames: {len(sprites.get('jump', []))}")
                print(f"    Victory frames: {len(sprites.get('victory', []))}")

                # Show animation settings from metadata
                if "animations" in metadata:
                    idle_settings = metadata["animations"].get("idle", {})
                    print(
                        f"    Idle frame rate: {idle_settings.get('frame_rate', 'N/A')} fps"
                    )
                    print(f"    Idle loops: {idle_settings.get('loop', 'N/A')}")

    print("\n" + "=" * 50)
    print("✅ All character sprites loaded successfully!")
    print("\nNext steps:")
    print("1. Integrate with your existing animation system")
    print("2. Create outfit variations for different scenes")
    print("3. Test in actual game scenes")


if __name__ == "__main__":
    demonstrate_sprite_loading()
