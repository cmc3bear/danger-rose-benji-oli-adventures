import math
import random
from dataclasses import dataclass

import pygame

from src.utils.asset_paths import get_item_path
from src.utils.sprite_loader import load_image


@dataclass
class Snowflake:
    """Represents a collectible snowflake."""

    x: float
    y: float
    width: int = 32
    height: int = 32
    collected: bool = False
    sprite: pygame.Surface | None = None
    rect: pygame.Rect | None = None
    # Animation properties
    float_offset: float = 0.0
    float_speed: float = 2.0
    float_amplitude: float = 10.0
    rotation: float = 0.0
    rotation_speed: float = 2.0


class SnowflakePool:
    """Object pool for efficient snowflake management."""

    def __init__(self, max_snowflakes: int = 30):
        self.max_snowflakes = max_snowflakes
        self.active_snowflakes: list[Snowflake] = []
        self.inactive_snowflakes: list[Snowflake] = []

        # Sprite will be loaded on first use
        self.snowflake_sprite = None
        self.sprites_loaded = False

    def _ensure_sprites_loaded(self):
        """Load sprites if not already loaded."""
        if self.sprites_loaded:
            return

        # Load snowflake sprite
        self.snowflake_sprite = load_image(get_item_path("snowflake.png"), (32, 32))

        # Pre-create snowflakes
        for _ in range(self.max_snowflakes):
            snowflake = Snowflake(
                x=0,
                y=0,
                sprite=self.snowflake_sprite,
                rect=pygame.Rect(0, 0, 24, 24),  # Smaller collision box
                float_offset=random.uniform(0, math.pi * 2),
                float_speed=random.uniform(1.5, 2.5),
                float_amplitude=random.uniform(8, 12),
                rotation_speed=random.uniform(1.5, 3.0),
            )
            self.inactive_snowflakes.append(snowflake)

        self.sprites_loaded = True

    def spawn_snowflake(self, x: float, y: float) -> Snowflake | None:
        """Spawn a snowflake from the pool."""
        self._ensure_sprites_loaded()

        if not self.inactive_snowflakes:
            return None

        snowflake = self.inactive_snowflakes.pop()
        snowflake.x = x
        snowflake.y = y
        snowflake.collected = False
        snowflake.rotation = 0

        # Update rect position
        snowflake.rect.center = (int(x), int(y))

        self.active_snowflakes.append(snowflake)
        return snowflake

    def despawn_snowflake(self, snowflake: Snowflake):
        """Return a snowflake to the pool."""
        if snowflake in self.active_snowflakes:
            self.active_snowflakes.remove(snowflake)
            self.inactive_snowflakes.append(snowflake)

    def update(self, scroll_speed: float, dt: float, screen_height: int):
        """Update all active snowflakes."""
        snowflakes_to_despawn = []

        for snowflake in self.active_snowflakes:
            if not snowflake.collected:
                # Move snowflake down with scrolling
                snowflake.y += scroll_speed * dt

                # Apply floating animation
                snowflake.float_offset += snowflake.float_speed * dt
                x_offset = math.sin(snowflake.float_offset) * snowflake.float_amplitude

                # Update rotation
                snowflake.rotation += snowflake.rotation_speed * dt

                # Update rect position with floating offset
                snowflake.rect.center = (int(snowflake.x + x_offset), int(snowflake.y))

                # Check if off screen
                if snowflake.y > screen_height + 50:
                    snowflakes_to_despawn.append(snowflake)

        # Despawn off-screen snowflakes
        for snowflake in snowflakes_to_despawn:
            self.despawn_snowflake(snowflake)

    def draw(self, screen: pygame.Surface):
        """Draw all active snowflakes."""
        for snowflake in self.active_snowflakes:
            if not snowflake.collected and snowflake.sprite:
                # Apply rotation
                rotated_sprite = pygame.transform.rotate(
                    snowflake.sprite, snowflake.rotation
                )
                sprite_rect = rotated_sprite.get_rect(center=snowflake.rect.center)

                # Draw with slight transparency for magical effect
                rotated_sprite.set_alpha(230)
                screen.blit(rotated_sprite, sprite_rect)

    def check_collection(self, player_rect: pygame.Rect) -> list[Snowflake]:
        """Check which snowflakes are collected by the player."""
        collected = []

        for snowflake in self.active_snowflakes:
            if not snowflake.collected and snowflake.rect.colliderect(player_rect):
                snowflake.collected = True
                collected.append(snowflake)

        return collected


class SnowflakeEffect:
    """Visual effect when collecting a snowflake."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.lifetime = 0.5  # seconds
        self.particles = []

        # Create sparkle particles
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "size": random.randint(2, 4),
                    "lifetime": random.uniform(0.3, 0.5),
                }
            )

    def update(self, dt: float) -> bool:
        """Update effect. Returns False when effect is complete."""
        self.lifetime -= dt

        for particle in self.particles[:]:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["lifetime"] -= dt

            # Apply gravity
            particle["vy"] += 200 * dt

            # Fade out
            particle["size"] = max(1, particle["size"] * (1 - dt * 2))

            if particle["lifetime"] <= 0:
                self.particles.remove(particle)

        return self.lifetime > 0 and len(self.particles) > 0

    def draw(self, screen: pygame.Surface):
        """Draw the sparkle effect."""
        for particle in self.particles:
            alpha = particle["lifetime"] / 0.5
            color = (255, 255, 255)  # White sparkles
            pos = (int(particle["x"]), int(particle["y"]))
            size = int(particle["size"])

            # Draw sparkle
            pygame.draw.circle(screen, color, pos, size)

            # Draw glow
            if size > 2:
                glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surf,
                    (*color, int(100 * alpha)),
                    (size * 2, size * 2),
                    size * 2,
                )
                screen.blit(glow_surf, (pos[0] - size * 2, pos[1] - size * 2))
