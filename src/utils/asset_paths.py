from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory (where pyproject.toml is located)."""
    current_path = Path(__file__).resolve()
    # Go up from src/utils/asset_paths.py to project root
    return current_path.parent.parent.parent


def get_asset_path(relative_path: str) -> str:
    """Get absolute path to an asset file relative to the assets directory."""
    project_root = get_project_root()
    asset_path = project_root / "assets" / relative_path
    return str(asset_path)


def get_image_path(relative_path: str) -> str:
    """Get absolute path to an image file relative to assets/images/."""
    return get_asset_path(f"images/{relative_path}")


def get_audio_path(relative_path: str) -> str:
    """Get absolute path to an audio file relative to assets/audio/."""
    return get_asset_path(f"audio/{relative_path}")


def get_character_sprite_path(character_name: str) -> str:
    """Get path to a character sprite sheet."""
    return get_image_path(f"characters/{character_name}.png")


def get_tileset_path(tileset_name: str) -> str:
    """Get path to a tileset image."""
    return get_image_path(f"tilesets/{tileset_name}")


def get_icon_path(icon_name: str) -> str:
    """Get path to an icon image."""
    return get_image_path(f"icons/{icon_name}")


def get_item_path(item_name: str) -> str:
    """Get path to an item image."""
    return get_image_path(f"items/{item_name}")


def get_music_path(music_name: str) -> str:
    """Get path to a music file."""
    return get_audio_path(f"music/{music_name}")


def get_sfx_path(sfx_name: str) -> str:
    """Get path to a sound effect file."""
    return get_audio_path(f"sfx/{sfx_name}")


def get_font_path(font_name: str) -> str:
    """Get path to a font file."""
    return get_asset_path(f"fonts/{font_name}")


# Convenience functions for common assets
def get_living_room_bg() -> str:
    """Get path to the living room background."""
    return get_tileset_path("living_room.png")


def get_danger_sprite() -> str:
    """Get path to Danger's sprite sheet."""
    return get_character_sprite_path("danger")


def get_rose_sprite() -> str:
    """Get path to Rose's sprite sheet."""
    return get_character_sprite_path("rose")


def get_vegas_bg() -> str:
    """Get path to the Vegas background."""
    return get_tileset_path("vegas_bg.png")
