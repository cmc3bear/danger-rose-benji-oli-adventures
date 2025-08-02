import math
import time
from abc import ABC, abstractmethod

import pygame

from src.config.constants import (
    COLOR_RED,
    COLOR_WHITE,
    COLOR_YELLOW,
)


class PowerUp(ABC):
    """Base class for all power-ups in the pool game."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = 20
        self.collected = False
        self.active = True

        # Visual properties
        self.pulse_time = 0
        self.float_offset = 0
        self.float_time = 0

        # Collection properties
        self.collection_radius = 30

        # Create rect for collision
        self.rect = pygame.Rect(
            self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2
        )

    @abstractmethod
    def get_color(self) -> tuple[int, int, int]:
        """Get the color of the power-up."""
        pass

    @abstractmethod
    def get_icon_type(self) -> str:
        """Get the icon type for rendering."""
        pass

    @abstractmethod
    def get_duration(self) -> float:
        """Get the duration of the power-up effect in seconds."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the display name of the power-up."""
        pass

    @abstractmethod
    def apply_effect(self, pool_game):
        """Apply the power-up effect to the game."""
        pass

    @abstractmethod
    def remove_effect(self, pool_game):
        """Remove the power-up effect from the game."""
        pass

    def update(self, dt: float):
        """Update power-up animation."""
        if self.collected:
            return

        # Pulsing effect
        self.pulse_time += dt

        # Floating effect
        self.float_time += dt
        self.float_offset = math.sin(self.float_time * 2) * 5

        # Update collision rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y + self.float_offset)

    def draw(self, screen):
        """Draw the power-up."""
        if self.collected:
            return

        # Calculate pulse effect
        pulse_scale = 1 + math.sin(self.pulse_time * 4) * 0.1
        current_radius = int(self.radius * pulse_scale)

        # Draw outer glow (simplified without creating surfaces)
        color = self.get_color()

        # Draw glow rings directly to screen
        for i in range(10, 0, -1):
            # Fade the glow color based on distance from center
            fade_factor = (10 - i) / 10.0
            glow_color = tuple(int(c * (1 - fade_factor * 0.8)) for c in color)
            pygame.draw.circle(
                screen,
                glow_color,
                (int(self.x), int(self.y + self.float_offset)),
                current_radius + i,
                1,
            )

        # Draw main circle
        pygame.draw.circle(
            screen,
            color,
            (int(self.x), int(self.y + self.float_offset)),
            current_radius,
        )

        # Draw inner circle
        pygame.draw.circle(
            screen,
            COLOR_WHITE,
            (int(self.x), int(self.y + self.float_offset)),
            current_radius - 3,
            2,
        )

        # Draw icon
        self._draw_icon(screen, int(self.x), int(self.y + self.float_offset))

    def _draw_icon(self, screen, x: int, y: int):
        """Draw the power-up icon."""
        icon_type = self.get_icon_type()

        if icon_type == "triple":
            # Draw three small circles
            for i in range(3):
                angle = (math.pi * 2 * i) / 3 - math.pi / 2
                icon_x = x + int(math.cos(angle) * 8)
                icon_y = y + int(math.sin(angle) * 8)
                pygame.draw.circle(screen, COLOR_WHITE, (icon_x, icon_y), 4)

        elif icon_type == "rapid":
            # Draw lightning bolt
            points = [(x - 5, y - 8), (x + 2, y - 2), (x - 2, y + 2), (x + 5, y + 8)]
            pygame.draw.lines(screen, COLOR_WHITE, False, points, 3)

        elif icon_type == "homing":
            # Draw target
            pygame.draw.circle(screen, COLOR_WHITE, (x, y), 8, 2)
            pygame.draw.circle(screen, COLOR_WHITE, (x, y), 2)
            # Crosshair
            pygame.draw.line(screen, COLOR_WHITE, (x - 12, y), (x - 8, y), 2)
            pygame.draw.line(screen, COLOR_WHITE, (x + 8, y), (x + 12, y), 2)
            pygame.draw.line(screen, COLOR_WHITE, (x, y - 12), (x, y - 8), 2)
            pygame.draw.line(screen, COLOR_WHITE, (x, y + 8), (x, y + 12), 2)

    def check_collection(self, player_x: float, player_y: float) -> bool:
        """Check if the player has collected this power-up."""
        if self.collected:
            return False

        distance = math.sqrt(
            (player_x - self.x) ** 2 + (player_y - self.y - self.float_offset) ** 2
        )

        if distance < self.collection_radius + 20:  # Player radius estimate
            self.collected = True
            return True

        return False


class TripleShotPowerUp(PowerUp):
    """Fires 3 water balloons at once in a spread pattern."""

    def get_color(self) -> tuple[int, int, int]:
        return (0, 255, 255)  # Cyan

    def get_icon_type(self) -> str:
        return "triple"

    def get_duration(self) -> float:
        return 10.0  # 10 seconds

    def get_name(self) -> str:
        return "Triple Shot"

    def apply_effect(self, pool_game):
        """Enable triple shot mode."""
        pool_game.triple_shot_active = True

    def remove_effect(self, pool_game):
        """Disable triple shot mode."""
        pool_game.triple_shot_active = False


class RapidFirePowerUp(PowerUp):
    """Reduces cooldown between shots for faster firing."""

    def get_color(self) -> tuple[int, int, int]:
        return COLOR_YELLOW

    def get_icon_type(self) -> str:
        return "rapid"

    def get_duration(self) -> float:
        return 8.0  # 8 seconds

    def get_name(self) -> str:
        return "Rapid Fire"

    def apply_effect(self, pool_game):
        """Reduce reload time and increase ammo capacity."""
        pool_game.original_reload_time = pool_game.reload_time
        pool_game.original_reload_duration = pool_game.reload_duration
        pool_game.reload_time = 0.15  # Much faster shots
        pool_game.reload_duration = 0.5  # Faster reload
        pool_game.rapid_fire_active = True

    def remove_effect(self, pool_game):
        """Restore normal firing rate."""
        pool_game.reload_time = pool_game.original_reload_time
        pool_game.reload_duration = pool_game.original_reload_duration
        pool_game.rapid_fire_active = False


class HomingPowerUp(PowerUp):
    """Water balloons curve towards the nearest target."""

    def get_color(self) -> tuple[int, int, int]:
        return COLOR_RED

    def get_icon_type(self) -> str:
        return "homing"

    def get_duration(self) -> float:
        return 12.0  # 12 seconds

    def get_name(self) -> str:
        return "Homing Balloons"

    def apply_effect(self, pool_game):
        """Enable homing balloons."""
        pool_game.homing_active = True

    def remove_effect(self, pool_game):
        """Disable homing balloons."""
        pool_game.homing_active = False


class ActivePowerUp:
    """Tracks an active power-up effect with its timer."""

    def __init__(self, powerup: PowerUp):
        self.powerup = powerup
        self.start_time = time.time()
        self.duration = powerup.get_duration()
        self.name = powerup.get_name()
        self.color = powerup.get_color()

    def get_time_remaining(self) -> float:
        """Get the time remaining for this power-up."""
        elapsed = time.time() - self.start_time
        return max(0, self.duration - elapsed)

    def is_expired(self) -> bool:
        """Check if the power-up has expired."""
        return self.get_time_remaining() <= 0

    def get_progress(self) -> float:
        """Get the progress percentage (0-1) of the power-up."""
        if self.duration <= 0:
            return 0
        return self.get_time_remaining() / self.duration
