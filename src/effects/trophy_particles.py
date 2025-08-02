"""Particle effects for trophy achievements."""

import math
import random

import pygame


class Particle:
    """A single particle for trophy effects."""

    def __init__(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int],
        velocity_x: float,
        velocity_y: float,
        lifetime: float,
    ):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 4)

    def update(self, dt: float) -> bool:
        """Update particle position and lifetime.

        Args:
            dt: Delta time in seconds

        Returns:
            True if particle is still alive
        """
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.velocity_y += 200 * dt  # Gravity
        self.lifetime -= dt

        return self.lifetime > 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the particle."""
        if self.lifetime <= 0:
            return

        # Fade alpha based on remaining lifetime
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        alpha = max(0, min(255, alpha))

        # Create surface with alpha
        particle_surface = pygame.Surface(
            (self.size * 2, self.size * 2), pygame.SRCALPHA
        )
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(
            particle_surface, color_with_alpha, (self.size, self.size), self.size
        )

        screen.blit(
            particle_surface, (int(self.x - self.size), int(self.y - self.size))
        )


class TrophyParticleEffect:
    """Particle effect system for trophy achievements."""

    # Color schemes for different trophy levels
    TROPHY_COLORS = {
        "bronze": [(205, 127, 50), (139, 69, 19), (255, 165, 0)],
        "silver": [(192, 192, 192), (128, 128, 128), (255, 255, 255)],
        "gold": [(255, 215, 0), (218, 165, 32), (255, 255, 0)],
    }

    def __init__(self):
        self.particles: list[Particle] = []

    def create_trophy_celebration(self, x: float, y: float, trophy_level: str) -> None:
        """Create celebration particles for a trophy achievement.

        Args:
            x: Center X position
            y: Center Y position
            trophy_level: Trophy level (bronze, silver, gold)
        """
        colors = self.TROPHY_COLORS.get(trophy_level, self.TROPHY_COLORS["bronze"])

        # Create burst of particles
        particle_count = 30 if trophy_level == "gold" else 20

        for _ in range(particle_count):
            # Random angle and speed for burst effect
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)

            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed - random.uniform(
                50, 100
            )  # Upward bias

            color = random.choice(colors)
            lifetime = random.uniform(1.0, 2.5)

            # Add some spread to starting position
            start_x = x + random.uniform(-10, 10)
            start_y = y + random.uniform(-10, 10)

            particle = Particle(
                start_x, start_y, color, velocity_x, velocity_y, lifetime
            )
            self.particles.append(particle)

    def create_sparkle_effect(self, x: float, y: float, trophy_level: str) -> None:
        """Create subtle sparkle effect around trophy.

        Args:
            x: Center X position
            y: Center Y position
            trophy_level: Trophy level (bronze, silver, gold)
        """
        colors = self.TROPHY_COLORS.get(trophy_level, self.TROPHY_COLORS["bronze"])

        # Create smaller, more subtle particles
        for _ in range(8):
            # Random position in circle around trophy
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(20, 40)

            start_x = x + math.cos(angle) * radius
            start_y = y + math.sin(angle) * radius

            # Slow floating motion
            velocity_x = random.uniform(-20, 20)
            velocity_y = random.uniform(-30, -10)  # Slight upward motion

            color = random.choice(colors)
            lifetime = random.uniform(0.5, 1.5)

            particle = Particle(
                start_x, start_y, color, velocity_x, velocity_y, lifetime
            )
            self.particles.append(particle)

    def update(self, dt: float) -> None:
        """Update all particles.

        Args:
            dt: Delta time in seconds
        """
        # Update particles and remove dead ones
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, screen: pygame.Surface) -> None:
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(screen)

    def has_particles(self) -> bool:
        """Check if there are any active particles."""
        return len(self.particles) > 0

    def clear(self) -> None:
        """Clear all particles."""
        self.particles.clear()
