#!/usr/bin/env python3
"""
Celebration tool for Danger Rose
Shows animated celebrations for achievements and milestones
"""

import math
import random
import sys

import pygame


class Celebration:
    def __init__(self, message="Great Job!", celebration_type="confetti"):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("🎉 Celebration! 🎉")
        self.clock = pygame.time.Clock()
        self.message = message
        self.type = celebration_type
        self.particles = []
        self.font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 36)

    def create_confetti(self):
        """Create confetti particles"""
        colors = [
            (255, 0, 0),  # Red
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
        ]

        for _ in range(100):
            self.particles.append(
                {
                    "x": random.randint(0, 800),
                    "y": random.randint(-600, 0),
                    "vx": random.uniform(-2, 2),
                    "vy": random.uniform(2, 5),
                    "color": random.choice(colors),
                    "angle": random.uniform(0, 360),
                    "spin": random.uniform(-10, 10),
                    "size": random.randint(10, 20),
                }
            )

    def create_fireworks(self):
        """Create firework bursts"""
        # Create multiple bursts
        for _ in range(3):
            x = random.randint(200, 600)
            y = random.randint(150, 350)
            self.firework_burst(x, y, 50)

    def firework_burst(self, x, y, count):
        """Create a burst of particles"""
        color = (
            random.randint(200, 255),
            random.randint(100, 255),
            random.randint(100, 255),
        )

        for i in range(count):
            angle = (360 / count) * i + random.uniform(-5, 5)
            speed = random.uniform(3, 6)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(math.radians(angle)) * speed,
                    "vy": math.sin(math.radians(angle)) * speed,
                    "color": color,
                    "life": 60,
                    "size": random.randint(3, 8),
                }
            )

    def create_stars(self):
        """Create twinkling stars"""
        for _ in range(50):
            self.particles.append(
                {
                    "x": random.randint(0, 800),
                    "y": random.randint(0, 400),
                    "vx": random.uniform(-0.5, 0.5),
                    "vy": random.uniform(-0.5, 0.5),
                    "color": (255, 255, 0),
                    "twinkle": random.uniform(0, math.pi * 2),
                    "twinkle_speed": random.uniform(0.05, 0.15),
                    "size": random.randint(10, 30),
                }
            )

    def update_particles(self):
        """Update particle positions and properties"""
        new_particles = []

        for particle in self.particles:
            # Update position
            particle["x"] += particle.get("vx", 0)
            particle["y"] += particle.get("vy", 0)

            # Apply gravity to confetti and fireworks
            if self.type in ["confetti", "fireworks"]:
                particle["vy"] += 0.1

            # Update rotation for confetti
            if "angle" in particle:
                particle["angle"] += particle.get("spin", 0)

            # Update twinkle for stars
            if "twinkle" in particle:
                particle["twinkle"] += particle["twinkle_speed"]

            # Update life for fireworks
            if "life" in particle:
                particle["life"] -= 1
                if particle["life"] > 0:
                    new_particles.append(particle)
            # Keep particle if on screen
            elif 0 <= particle["x"] <= 800 and particle["y"] <= 650:
                new_particles.append(particle)

        self.particles = new_particles

    def draw_particles(self):
        """Draw all particles"""
        for particle in self.particles:
            x, y = int(particle["x"]), int(particle["y"])
            color = particle["color"]
            size = particle.get("size", 10)

            if self.type == "confetti":
                # Draw rotated rectangle
                points = []
                angle = particle.get("angle", 0)
                for dx, dy in [
                    (-size / 2, -size / 3),
                    (size / 2, -size / 3),
                    (size / 2, size / 3),
                    (-size / 2, size / 3),
                ]:
                    rx = dx * math.cos(math.radians(angle)) - dy * math.sin(
                        math.radians(angle)
                    )
                    ry = dx * math.sin(math.radians(angle)) + dy * math.cos(
                        math.radians(angle)
                    )
                    points.append((x + rx, y + ry))
                pygame.draw.polygon(self.screen, color, points)

            elif self.type == "fireworks":
                # Draw glowing circle
                life_ratio = particle.get("life", 60) / 60
                current_size = int(size * life_ratio)
                if current_size > 0:
                    pygame.draw.circle(self.screen, color, (x, y), current_size)
                    # Add glow effect
                    glow_color = tuple(int(c * 0.5) for c in color)
                    pygame.draw.circle(
                        self.screen, glow_color, (x, y), current_size + 2, 1
                    )

            elif self.type == "stars":
                # Draw twinkling star
                twinkle = particle.get("twinkle", 0)
                brightness = (math.sin(twinkle) + 1) / 2
                current_size = int(size * (0.5 + brightness * 0.5))

                # Draw star shape
                points = []
                for i in range(10):
                    angle = i * math.pi / 5
                    if i % 2 == 0:
                        r = current_size
                    else:
                        r = current_size * 0.5
                    px = x + r * math.cos(angle - math.pi / 2)
                    py = y + r * math.sin(angle - math.pi / 2)
                    points.append((px, py))

                star_color = tuple(int(c * brightness) for c in color)
                pygame.draw.polygon(self.screen, star_color, points)

    def draw_message(self):
        """Draw the celebration message"""
        # Create text surface
        text_surface = self.font.render(self.message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(400, 300))

        # Draw shadow
        shadow_surface = self.font.render(self.message, True, (0, 0, 0))
        shadow_rect = text_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        self.screen.blit(shadow_surface, shadow_rect)

        # Draw main text
        self.screen.blit(text_surface, text_rect)

        # Draw subtitle
        subtitle = "Press any key to continue..."
        subtitle_surface = self.small_font.render(subtitle, True, (200, 200, 200))
        subtitle_rect = subtitle_surface.get_rect(center=(400, 400))
        self.screen.blit(subtitle_surface, subtitle_rect)

    def run(self):
        """Run celebration animation"""
        # Initialize particles based on type
        if self.type == "confetti":
            self.create_confetti()
        elif self.type == "fireworks":
            self.create_fireworks()
        elif self.type == "stars":
            self.create_stars()
        else:
            # Default to confetti
            self.type = "confetti"
            self.create_confetti()

        # Animation loop
        running = True
        duration = 5000  # 5 seconds
        start_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    running = False

            # Auto-close after duration
            if current_time - start_time > duration:
                running = False

            # Clear screen with dark background
            self.screen.fill((20, 20, 40))

            # Update and draw particles
            self.update_particles()
            self.draw_particles()

            # Draw message
            self.draw_message()

            # Add more particles for continuous effect
            if (
                self.type == "confetti"
                and len(self.particles) < 100
                and random.random() < 0.3
            ):
                self.particles.append(
                    {
                        "x": random.randint(0, 800),
                        "y": -20,
                        "vx": random.uniform(-2, 2),
                        "vy": random.uniform(2, 5),
                        "color": random.choice(
                            [
                                (255, 0, 0),
                                (0, 255, 0),
                                (0, 0, 255),
                                (255, 255, 0),
                                (255, 0, 255),
                                (0, 255, 255),
                            ]
                        ),
                        "angle": random.uniform(0, 360),
                        "spin": random.uniform(-10, 10),
                        "size": random.randint(10, 20),
                    }
                )

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


def main():
    """Main entry point"""
    # Parse arguments
    message = "Great Job!"
    celebration_type = "confetti"

    if len(sys.argv) > 1:
        # Check for type flag
        if "--type" in sys.argv:
            type_index = sys.argv.index("--type")
            if type_index + 1 < len(sys.argv):
                celebration_type = sys.argv[type_index + 1]
                # Remove type arguments
                sys.argv.pop(type_index)
                sys.argv.pop(type_index)

        # Get message (all remaining arguments)
        if len(sys.argv) > 1:
            message = " ".join(sys.argv[1:])

    # Create and run celebration
    celebration = Celebration(message, celebration_type)
    celebration.run()


if __name__ == "__main__":
    main()
