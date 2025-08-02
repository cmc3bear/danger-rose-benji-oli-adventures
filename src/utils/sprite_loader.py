import json
import os

import pygame

from src.config.constants import COLOR_PLACEHOLDER


def load_vehicle_sprite(vehicle_name: str) -> pygame.Surface:
    """Load a vehicle sprite for the drive minigame.
    
    Args:
        vehicle_name: Name of the vehicle (e.g., 'professional' or 'kids_drawing')
        
    Returns:
        The loaded vehicle sprite surface
    """
    # Get the path to the vehicle sprite
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    vehicle_path = os.path.join(project_root, "assets", "images", "vehicles", f"ev_{vehicle_name}.png")
    
    # Load and return the sprite
    return load_image(vehicle_path, scale=(128, 192))


def load_image(path: str, scale: tuple | None = None) -> pygame.Surface:
    """Load an image from an absolute path."""
    if not os.path.exists(path):
        # Create a placeholder surface if image doesn't exist
        surface = pygame.Surface((64, 64))
        surface.fill(COLOR_PLACEHOLDER)  # Magenta placeholder
        return surface

    try:
        surface = pygame.image.load(path).convert_alpha()
        if scale:
            surface = pygame.transform.scale(surface, scale)
        return surface
    except pygame.error:
        # Create a placeholder surface if loading fails
        surface = pygame.Surface((64, 64))
        surface.fill(COLOR_PLACEHOLDER)  # Magenta placeholder
        return surface


def load_character_individual_files(
    character_name: str,
    scene: str = "hub",
    scale: tuple | None = None,
    base_path: str = None,
) -> dict[str, list[pygame.Surface]]:
    """Load character animations from individual PNG files organized by scene.

    Args:
        character_name: Name of character (danger, rose, dad)
        scene: Scene name (hub, pool, vegas, ski)
        scale: Optional scaling tuple (width, height)
        base_path: Base path to character assets (auto-detected if None)

    Returns:
        Dictionary mapping animation names to lists of Surface objects
    """
    if base_path is None:
        # Auto-detect base path relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        base_path = os.path.join(
            project_root, "assets", "images", "characters", "new_sprites"
        )

    character_path = os.path.join(base_path, character_name, scene)
    metadata_path = os.path.join(
        base_path, character_name, "hub", "animation_metadata.json"
    )

    # Load animation metadata if available
    animation_config = {
        "idle": {"frames": 4},
        "walk": {"frames": 5},  # Using walk instead of walk_extra for now
        "jump": {"frames": 3},
        "victory": {"frames": 4},
        "hurt": {"frames": 2},
        "action": {"frames": 6},  # Map to attack
    }

    if os.path.exists(metadata_path):
        try:
            with open(metadata_path) as f:
                metadata = json.load(f)
                if "animations" in metadata:
                    animation_config.update(
                        {
                            name: {"frames": info["frames"]}
                            for name, info in metadata["animations"].items()
                        }
                    )
        except (json.JSONDecodeError, KeyError):
            pass  # Use default config if metadata is invalid

    animations = {}

    for animation_name, config in animation_config.items():
        frames = []
        frame_count = config["frames"]

        for i in range(1, frame_count + 1):
            frame_path = os.path.join(character_path, f"{animation_name}_{i:02d}.png")

            if os.path.exists(frame_path):
                frame = load_image(frame_path, scale)
                frames.append(frame)
            else:
                # Create placeholder frame
                placeholder = pygame.Surface((80, 110))
                placeholder.fill((255, 0, 255))
                frames.append(placeholder)

        if frames:
            animations[animation_name] = frames

    # Map some animations to expected names for backward compatibility
    if "action" in animations:
        animations["attack"] = animations["action"]
    if "walk" in animations:
        animations["walking"] = animations["walk"]
    if "jump" in animations:
        animations["jumping"] = animations["jump"]

    return animations


def load_sprite_sheet(
    path: str, frame_width: int, frame_height: int, scale: tuple | None = None
) -> list:
    """Load a sprite sheet and return a list of individual frames."""
    if not os.path.exists(path):
        # Create placeholder frames if sprite sheet doesn't exist
        placeholder = pygame.Surface((frame_width, frame_height))
        placeholder.fill(COLOR_PLACEHOLDER)  # Magenta placeholder
        return [placeholder]

    try:
        sheet = pygame.image.load(path).convert_alpha()
        frames = []

        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()

        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (x, y, frame_width, frame_height))

                if scale:
                    frame = pygame.transform.scale(frame, scale)

                frames.append(frame)

        return frames if frames else [pygame.Surface((frame_width, frame_height))]

    except pygame.error:
        # Create placeholder frame if loading fails
        placeholder = pygame.Surface((frame_width, frame_height))
        placeholder.fill(COLOR_PLACEHOLDER)  # Magenta placeholder
        return [placeholder]


def load_character_animations(
    path: str,
    frame_width: int = 256,
    frame_height: int = 256,
    scale: tuple | None = None,
) -> dict:
    """Load a character sprite sheet and return animations organized by type."""
    if not os.path.exists(path):
        # Create placeholder animations if sprite sheet doesn't exist
        placeholder = pygame.Surface((frame_width, frame_height))
        placeholder.fill(COLOR_PLACEHOLDER)  # Magenta placeholder
        return {
            "walking": [placeholder] * 4,
            "jumping": [placeholder] * 4,
            "attacking": [placeholder] * 3,
        }

    try:
        sheet = pygame.image.load(path).convert_alpha()
        animations = {"walking": [], "jumping": [], "attacking": []}

        # Row 0: Walking animation (4 frames)
        for x in range(0, 4 * frame_width, frame_width):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (x, 0, frame_width, frame_height))
            if scale:
                frame = pygame.transform.scale(frame, scale)
            animations["walking"].append(frame)

        # Row 1: Jumping animation (4 frames)
        for x in range(0, 4 * frame_width, frame_width):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (x, frame_height, frame_width, frame_height))
            if scale:
                frame = pygame.transform.scale(frame, scale)
            animations["jumping"].append(frame)

        # Row 2: Attacking animation (3 frames, ignoring the effect frame)
        for x in range(0, 3 * frame_width, frame_width):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (x, 2 * frame_height, frame_width, frame_height))
            if scale:
                frame = pygame.transform.scale(frame, scale)
            animations["attacking"].append(frame)

        return animations

    except pygame.error:
        # Create placeholder animations if loading fails
        placeholder = pygame.Surface((frame_width, frame_height))
        placeholder.fill(COLOR_PLACEHOLDER)  # Magenta placeholder
        return {
            "walking": [placeholder] * 4,
            "jumping": [placeholder] * 4,
            "attacking": [placeholder] * 3,
        }
