import time

import pygame

from src.config.constants import ANIMATION_DEFAULT_DURATION, SPRITE_DISPLAY_SIZE

from .sprite_loader import load_character_animations


class AnimatedCharacter:
    def __init__(
        self,
        character_name: str,
        sprite_path: str,
        scale: tuple = (SPRITE_DISPLAY_SIZE, SPRITE_DISPLAY_SIZE),
    ):
        self.character_name = character_name
        self.scale = scale
        self.animations = load_character_animations(sprite_path, scale=scale)

        # Animation state
        self.current_animation = "walking"
        self.current_frame = 0
        self.animation_speed = (
            ANIMATION_DEFAULT_DURATION / 1000.0
        )  # Convert ms to seconds
        self.last_frame_time = time.time()

        # Animation cycling
        self.animation_cycle = ["walking", "jumping", "attacking"]
        self.current_cycle_index = 0
        self.animation_hold_time = 2.0  # seconds to hold each animation
        self.animation_start_time = time.time()

    def update(self):
        current_time = time.time()

        # Update animation frame
        if current_time - self.last_frame_time >= self.animation_speed:
            self.current_frame += 1
            frames_in_current_animation = len(self.animations[self.current_animation])

            if self.current_frame >= frames_in_current_animation:
                self.current_frame = 0

            self.last_frame_time = current_time

        # Cycle through animations
        if current_time - self.animation_start_time >= self.animation_hold_time:
            self.current_cycle_index = (self.current_cycle_index + 1) % len(
                self.animation_cycle
            )
            self.current_animation = self.animation_cycle[self.current_cycle_index]
            self.current_frame = 0
            self.animation_start_time = current_time

    def get_current_sprite(self) -> pygame.Surface:
        """Get the current frame of the current animation."""
        if self.current_animation in self.animations:
            frames = self.animations[self.current_animation]
            if frames and self.current_frame < len(frames):
                return frames[self.current_frame]

        # Fallback to first frame of walking animation
        if "walking" in self.animations and self.animations["walking"]:
            return self.animations["walking"][0]

        # Ultimate fallback
        fallback = pygame.Surface(self.scale)
        fallback.fill((255, 0, 255))
        return fallback

    def set_animation(self, animation_name: str):
        """Manually set the current animation."""
        if animation_name in self.animations:
            self.current_animation = animation_name
            self.current_frame = 0
            self.animation_start_time = time.time()

    def get_animation_info(self) -> str:
        """Get current animation info for debugging."""
        return f"{self.current_animation.capitalize()} (Frame {self.current_frame + 1}/{len(self.animations[self.current_animation])})"
