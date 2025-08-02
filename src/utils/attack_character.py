import time

import pygame

from src.config.constants import (
    ANIMATION_ATTACK_DURATION,
    COLOR_PLACEHOLDER,
    SPRITE_DISPLAY_SIZE,
)
from src.utils.sprite_loader import load_character_individual_files


class AnimatedCharacter:
    """Flexible character animation system supporting multiple animation types and scenes."""

    def __init__(
        self,
        character_name: str,
        scene: str = "hub",
        scale: tuple = (SPRITE_DISPLAY_SIZE, SPRITE_DISPLAY_SIZE),
        sprite_path: str | None = None,  # For backward compatibility
    ):
        # Convert character name to lowercase and replace spaces with underscores
        self.character_name = character_name.lower().replace(" ", "_")
        self.scene = scene
        self.scale = scale

        # Load all animations for this character and scene
        self.animations = self._load_character_animations(sprite_path)

        # Animation state
        self.current_animation = "idle"
        self.current_frame = 0
        self.animation_speed = 0.1  # Default speed in seconds per frame
        self.last_frame_time = time.time()
        self.loop_animation = True

        # Animation-specific speeds
        self.animation_speeds = {
            "idle": 0.2,
            "walk": 0.1,
            "jump": 0.15,
            "attack": ANIMATION_ATTACK_DURATION / 1000.0 / 6,  # 6 frames for attack
            "hurt": 0.2,
            "victory": 0.15,
        }

    def _load_character_animations(
        self, sprite_path: str | None = None
    ) -> dict[str, list[pygame.Surface]]:
        """Load all character animations from individual files or fallback to sprite sheet."""
        try:
            # Try loading from individual files first
            animations = load_character_individual_files(
                character_name=self.character_name, scene=self.scene, scale=self.scale
            )
            if animations:
                return animations
        except Exception as e:
            print(f"Error loading individual files for {self.character_name}: {e}")

        # Fallback to old sprite sheet method if individual files not available
        if sprite_path:
            return self._load_legacy_sprite_sheet(sprite_path)

        # Final fallback: create placeholder animations
        return self._create_placeholder_animations()

    def _load_legacy_sprite_sheet(
        self, sprite_path: str
    ) -> dict[str, list[pygame.Surface]]:
        """Legacy method to load from sprite sheets (for backward compatibility)."""
        try:
            from src.utils.sprite_loader import load_character_animations

            return load_character_animations(sprite_path, scale=self.scale)
        except Exception as e:
            print(f"Error loading legacy sprite sheet {sprite_path}: {e}")
            return self._create_placeholder_animations()

    def _create_placeholder_animations(self) -> dict[str, list[pygame.Surface]]:
        """Create placeholder animations if loading fails."""
        placeholder = pygame.Surface(self.scale)
        placeholder.fill(COLOR_PLACEHOLDER)  # Magenta placeholder

        return {
            "idle": [placeholder] * 4,
            "walk": [placeholder] * 5,
            "jump": [placeholder] * 3,
            "attack": [placeholder] * 6,
            "hurt": [placeholder] * 2,
            "victory": [placeholder] * 4,
            # Add backward compatibility mappings
            "walking": [placeholder] * 5,
            "jumping": [placeholder] * 3,
            "attacking": [placeholder] * 6,
        }

    def update(self):
        """Update the animation frame."""
        current_time = time.time()

        # Use animation-specific speed if available
        speed = self.animation_speeds.get(self.current_animation, self.animation_speed)

        if current_time - self.last_frame_time >= speed:
            current_frames = self.animations.get(self.current_animation, [])
            if current_frames:
                if self.loop_animation:
                    self.current_frame = (self.current_frame + 1) % len(current_frames)
                # Non-looping animation (e.g., attack, hurt)
                elif self.current_frame < len(current_frames) - 1:
                    self.current_frame += 1
                    # Stay on last frame if not looping
            self.last_frame_time = current_time

    def set_animation(self, animation_name: str, loop: bool = True):
        """Switch to a different animation.

        Args:
            animation_name: Name of animation (idle, walk, jump, attack, hurt, victory)
            loop: Whether the animation should loop
        """
        if (
            animation_name in self.animations
            and animation_name != self.current_animation
        ):
            self.current_animation = animation_name
            self.current_frame = 0
            self.loop_animation = loop
            self.last_frame_time = time.time()

    def get_current_sprite(self) -> pygame.Surface:
        """Get the current animation frame."""
        current_frames = self.animations.get(self.current_animation, [])

        if current_frames and 0 <= self.current_frame < len(current_frames):
            return current_frames[self.current_frame]

        # Fallback
        fallback = pygame.Surface(self.scale)
        fallback.fill((255, 0, 255))
        return fallback

    def get_frame_count(self) -> int:
        """Get the number of frames in current animation."""
        current_frames = self.animations.get(self.current_animation, [])
        return len(current_frames)

    def get_animation_info(self) -> str:
        """Get current animation info for debugging."""
        frame_count = self.get_frame_count()
        return f"{self.current_animation.title()} (Frame {self.current_frame + 1}/{frame_count})"

    def has_animation(self, animation_name: str) -> bool:
        """Check if character has a specific animation."""
        return animation_name in self.animations

    def get_available_animations(self) -> list[str]:
        """Get list of available animation names."""
        return list(self.animations.keys())

    def change_scene(self, scene: str):
        """Change the character's scene and reload sprites."""
        if scene != self.scene:
            self.scene = scene
            self.animations = self._load_character_animations()
            # Reset to idle animation
            self.set_animation("idle")


# Maintain backward compatibility with old class name
class AttackCharacter(AnimatedCharacter):
    """Backward compatibility wrapper for the old AttackCharacter class."""

    def __init__(
        self,
        character_name: str,
        sprite_path: str,
        scale: tuple = (SPRITE_DISPLAY_SIZE, SPRITE_DISPLAY_SIZE),
    ):
        super().__init__(character_name, "hub", scale, sprite_path)
        # Start with attack animation for backward compatibility
        self.set_animation("attack", loop=True)

    @property
    def attack_frames(self) -> list[pygame.Surface]:
        """Backward compatibility property."""
        return self.animations.get("attack", [])
