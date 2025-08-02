import math
import random

import pygame


class TargetDestroyParticle:
    """Individual particle for target destruction effect."""

    def __init__(self, x: float, y: float, color: tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color

        # Random velocity
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(100, 300)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 100  # Slight upward bias

        # Physics
        self.gravity = 800
        self.drag = 0.98

        # Visual properties
        self.size = random.uniform(3, 8)
        self.lifetime = random.uniform(0.5, 1.0)
        self.age = 0
        self.active = True

    def update(self, dt: float):
        """Update particle physics."""
        if not self.active:
            return

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Apply physics
        self.vy += self.gravity * dt
        self.vx *= self.drag
        self.vy *= self.drag

        # Update age
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False

    def draw(self, screen):
        """Draw the particle."""
        if not self.active:
            return

        # Fade out based on age
        alpha = 1.0 - (self.age / self.lifetime)
        if alpha <= 0:
            return

        # Draw with fade
        size = int(self.size * (1.0 - self.age / self.lifetime))
        if size > 0:
            color = tuple(int(c * alpha) for c in self.color)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)


class TargetDestroyEffect:
    """Particle effect system for target destruction."""

    def __init__(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int],
        target_type: str = "default",
    ):
        self.x = x
        self.y = y
        self.particles: list[TargetDestroyParticle] = []
        self.active = True

        # Create particles based on target type
        if target_type == "duck":
            self._create_duck_particles(color)
        elif target_type == "beachball":
            self._create_beachball_particles(color)
        elif target_type == "donut":
            self._create_donut_particles(color)
        else:
            self._create_default_particles(color)

    def _create_duck_particles(self, color: tuple[int, int, int]):
        """Create feather-like particles for duck."""
        # Main explosion
        for _ in range(15):
            particle = TargetDestroyParticle(self.x, self.y, color)
            self.particles.append(particle)

        # Add some white feathers
        for _ in range(10):
            particle = TargetDestroyParticle(self.x, self.y, (255, 255, 255))
            particle.gravity = 400  # Feathers fall slower
            self.particles.append(particle)

    def _create_beachball_particles(self, color: tuple[int, int, int]):
        """Create colorful particles for beach ball."""
        colors = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 0)]

        for _ in range(20):
            particle_color = random.choice(colors)
            particle = TargetDestroyParticle(self.x, self.y, particle_color)
            self.particles.append(particle)

    def _create_donut_particles(self, color: tuple[int, int, int]):
        """Create sprinkle-like particles for donut."""
        # Main donut pieces
        for _ in range(12):
            particle = TargetDestroyParticle(self.x, self.y, color)
            self.particles.append(particle)

        # Colorful sprinkles
        sprinkle_colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255)]
        for _ in range(15):
            sprinkle_color = random.choice(sprinkle_colors)
            particle = TargetDestroyParticle(self.x, self.y, sprinkle_color)
            particle.size = random.uniform(2, 4)  # Smaller sprinkles
            self.particles.append(particle)

    def _create_default_particles(self, color: tuple[int, int, int]):
        """Create generic particles."""
        for _ in range(15):
            particle = TargetDestroyParticle(self.x, self.y, color)
            self.particles.append(particle)

    def update(self, dt: float):
        """Update all particles."""
        active_count = 0
        for particle in self.particles:
            particle.update(dt)
            if particle.active:
                active_count += 1

        # Deactivate effect when all particles are done
        if active_count == 0:
            self.active = False

    def draw(self, screen):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(screen)
