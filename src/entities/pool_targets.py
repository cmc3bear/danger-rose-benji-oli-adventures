import math
import random
from abc import ABC, abstractmethod

import pygame

from src.config.constants import (
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_WHITE,
    COLOR_YELLOW,
)


class PoolTarget(ABC):
    """Base class for all pool game targets."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.initial_x = x
        self.initial_y = y
        self.hit = False
        self.hit_time = 0
        self.active = True
        self.time_alive = 0

        # Movement properties
        self.vx = 0
        self.vy = 0
        self.movement_time = 0

        # Visual properties
        self.rotation = 0
        self.scale = 1.0

        # Create rect for collision
        self.rect = pygame.Rect(0, 0, self.get_size(), self.get_size())
        self.update_rect()

    @abstractmethod
    def get_size(self) -> int:
        """Get the size of the target."""
        pass

    @abstractmethod
    def get_point_value(self) -> int:
        """Get the point value for hitting this target."""
        pass

    @abstractmethod
    def get_color(self) -> tuple[int, int, int]:
        """Get the primary color of the target."""
        pass

    @abstractmethod
    def update_movement(self, dt: float):
        """Update the target's movement pattern."""
        pass

    @abstractmethod
    def draw_shape(
        self, screen, x: int, y: int, size: int, color: tuple[int, int, int]
    ):
        """Draw the specific shape of this target."""
        pass

    def update_rect(self):
        """Update collision rectangle position."""
        size = self.get_size()
        self.rect.width = size
        self.rect.height = size
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

    def update(self, dt: float):
        """Update target state and movement."""
        if not self.active:
            return

        self.time_alive += dt
        self.movement_time += dt

        if self.hit:
            # Update hit animation
            self.hit_time += dt
            self.scale = 1.0 + self.hit_time * 2
            self.rotation += dt * 720  # Spin when hit

            if self.hit_time > 0.5:
                self.active = False
        else:
            # Update movement
            self.update_movement(dt)

            # Keep targets within pool bounds (with some margin)
            margin = self.get_size() // 2
            self.x = max(margin + 150, min(self.x, 1280 - margin - 150))
            self.y = max(margin + 150, min(self.y, 500))

        self.update_rect()

    def draw(self, screen):
        """Draw the target."""
        if not self.active:
            return

        # Calculate visual properties
        size = int(self.get_size() * self.scale)
        color = self.get_color()

        if self.hit:
            # Fade out when hit
            alpha = max(0, 1.0 - self.hit_time * 2)
            color = tuple(int(c * alpha) for c in color)

        # Save current transform
        x, y = int(self.x), int(self.y)

        # Draw the target shape
        self.draw_shape(screen, x, y, size, color)

        # Draw point value when hit
        if self.hit and self.hit_time < 0.3:
            font = pygame.font.Font(None, 48)
            points_text = f"+{self.get_point_value()}"
            text_surface = font.render(points_text, True, COLOR_GREEN)
            text_rect = text_surface.get_rect(center=(x, y - size))
            screen.blit(text_surface, text_rect)

    def check_collision(self, balloon) -> bool:
        """Check if balloon hits this target."""
        if self.hit or not self.active:
            return False

        # Simple circle collision
        distance = math.sqrt((balloon.x - self.x) ** 2 + (balloon.y - self.y) ** 2)
        if distance < (self.get_size() // 2) + balloon.radius:
            self.hit = True
            return True

        return False


class DuckTarget(PoolTarget):
    """Rubber duck that moves in a sine wave pattern."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.amplitude = 50
        self.frequency = 1.5
        self.speed = 50
        self.direction = random.choice([-1, 1])

    def get_size(self) -> int:
        return 50

    def get_point_value(self) -> int:
        return 25  # Medium points

    def get_color(self) -> tuple[int, int, int]:
        return COLOR_YELLOW

    def update_movement(self, dt: float):
        """Move in a sine wave pattern."""
        self.x += self.speed * self.direction * dt
        self.y = (
            self.initial_y
            + math.sin(self.movement_time * self.frequency) * self.amplitude
        )

        # Bounce off edges
        if self.x <= 200 or self.x >= 1080:
            self.direction *= -1

    def draw_shape(
        self, screen, x: int, y: int, size: int, color: tuple[int, int, int]
    ):
        """Draw a rubber duck shape."""
        # Body
        body_rect = pygame.Rect(x - size // 2, y - size // 4, size, size // 2)
        pygame.draw.ellipse(screen, color, body_rect)
        pygame.draw.ellipse(screen, COLOR_WHITE, body_rect, 2)

        # Head
        head_size = size // 2
        head_rect = pygame.Rect(x - head_size // 2, y - size // 2, head_size, head_size)
        pygame.draw.ellipse(screen, color, head_rect)
        pygame.draw.ellipse(screen, COLOR_WHITE, head_rect, 2)

        # Eye
        eye_x = x - head_size // 4
        eye_y = y - size // 3
        pygame.draw.circle(screen, COLOR_WHITE, (eye_x, eye_y), 3)
        pygame.draw.circle(screen, (0, 0, 0), (eye_x, eye_y), 2)

        # Beak
        beak_points = [
            (x - head_size // 2 - 5, y - size // 3),
            (x - head_size // 2 - 12, y - size // 3 + 3),
            (x - head_size // 2 - 5, y - size // 3 + 6),
        ]
        pygame.draw.polygon(screen, (255, 140, 0), beak_points)


class BeachBallTarget(PoolTarget):
    """Beach ball that bounces around randomly."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(80, 120)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.rotation_speed = random.uniform(90, 180) * random.choice([-1, 1])

    def get_size(self) -> int:
        return 45

    def get_point_value(self) -> int:
        return 30  # Higher points for harder target

    def get_color(self) -> tuple[int, int, int]:
        return COLOR_RED

    def update_movement(self, dt: float):
        """Bounce around randomly."""
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Update rotation
        self.rotation += self.rotation_speed * dt

        # Bounce off edges
        margin = self.get_size() // 2
        if self.x <= 150 + margin or self.x >= 1130 - margin:
            self.vx *= -1
            self.x = max(150 + margin, min(self.x, 1130 - margin))

        if self.y <= 150 + margin or self.y >= 500 - margin:
            self.vy *= -1
            self.y = max(150 + margin, min(self.y, 500 - margin))

    def draw_shape(
        self, screen, x: int, y: int, size: int, color: tuple[int, int, int]
    ):
        """Draw a beach ball with colored segments."""
        # Draw main circle
        pygame.draw.circle(screen, COLOR_WHITE, (x, y), size // 2)

        # Draw colored segments
        colors = [COLOR_RED, COLOR_BLUE, COLOR_YELLOW, COLOR_GREEN]
        num_segments = 6

        for i in range(num_segments):
            start_angle = (i * 2 * math.pi / num_segments) + math.radians(self.rotation)
            end_angle = ((i + 1) * 2 * math.pi / num_segments) + math.radians(
                self.rotation
            )

            # Calculate arc points
            points = [(x, y)]  # Center point
            for angle in range(
                int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1
            ):
                px = x + math.cos(math.radians(angle)) * (size // 2)
                py = y + math.sin(math.radians(angle)) * (size // 2)
                points.append((int(px), int(py)))

            if len(points) > 2:
                pygame.draw.polygon(screen, colors[i % len(colors)], points)

        # Draw outline
        pygame.draw.circle(screen, COLOR_WHITE, (x, y), size // 2, 3)


class DonutFloatTarget(PoolTarget):
    """Donut float that moves in straight lines slowly."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        # Random direction
        angle = random.choice([0, math.pi / 2, math.pi, 3 * math.pi / 2])
        self.speed = 40  # Slow movement
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.bob_amplitude = 5
        self.bob_frequency = 2

    def get_size(self) -> int:
        return 60  # Largest target

    def get_point_value(self) -> int:
        return 15  # Lower points for easier target

    def get_color(self) -> tuple[int, int, int]:
        return (255, 192, 203)  # Pink

    def update_movement(self, dt: float):
        """Move in straight lines with gentle bobbing."""
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Add bobbing effect
        bob_offset = (
            math.sin(self.movement_time * self.bob_frequency) * self.bob_amplitude
        )
        self.y = self.y + bob_offset

        # Bounce off edges
        margin = self.get_size() // 2
        if self.x <= 150 + margin or self.x >= 1130 - margin:
            self.vx *= -1
            self.x = max(150 + margin, min(self.x, 1130 - margin))

        if self.y <= 150 + margin or self.y >= 500 - margin:
            self.vy *= -1
            self.y = max(150 + margin, min(self.y, 500 - margin))

    def draw_shape(
        self, screen, x: int, y: int, size: int, color: tuple[int, int, int]
    ):
        """Draw a donut float shape."""
        # Outer circle
        pygame.draw.circle(screen, color, (x, y), size // 2)

        # Inner hole
        hole_size = size // 3
        pygame.draw.circle(screen, (100, 150, 255), (x, y), hole_size)  # Water color

        # Sprinkles
        if not self.hit:
            for i in range(8):
                angle = (i * math.pi * 2) / 8
                sprinkle_x = x + math.cos(angle) * (size // 3)
                sprinkle_y = y + math.sin(angle) * (size // 3)
                colors = [COLOR_RED, COLOR_YELLOW, COLOR_GREEN, COLOR_BLUE]
                pygame.draw.circle(
                    screen, colors[i % 4], (int(sprinkle_x), int(sprinkle_y)), 3
                )

        # Outline
        pygame.draw.circle(screen, COLOR_WHITE, (x, y), size // 2, 3)
        pygame.draw.circle(screen, COLOR_WHITE, (x, y), hole_size, 2)
