import random
from dataclasses import dataclass

import pygame

from src.entities.snowflake import SnowflakePool
from src.utils.asset_paths import get_tileset_path
from src.utils.sprite_loader import load_image


@dataclass
class Obstacle:
    """Represents an obstacle on the slope."""

    x: float
    y: float
    width: int
    height: int
    obstacle_type: str  # "tree" or "rock"
    sprite: pygame.Surface
    rect: pygame.Rect


class ObstaclePool:
    """Object pool for efficient obstacle management."""

    def __init__(self, max_obstacles: int = 50):
        self.max_obstacles = max_obstacles
        self.active_obstacles: list[Obstacle] = []
        self.inactive_obstacles: list[Obstacle] = []

        # Sprites will be loaded on first use
        self.tree_sprite = None
        self.rock_sprite = None
        self.sprites_loaded = False

    def _ensure_sprites_loaded(self):
        """Load sprites if not already loaded."""
        if self.sprites_loaded:
            return

        # Load obstacle sprites
        self.tree_sprite = load_image(get_tileset_path("ski/tree.png"), (64, 96))
        self.rock_sprite = load_image(get_tileset_path("ski/rock.png"), (48, 48))

        # Pre-create obstacles
        for _ in range(self.max_obstacles):
            # Create trees and rocks
            if random.random() < 0.6:
                obstacle = Obstacle(
                    x=0,
                    y=0,
                    width=64,
                    height=96,
                    obstacle_type="tree",
                    sprite=self.tree_sprite,
                    rect=pygame.Rect(0, 0, 48, 32),  # Smaller collision box at base
                )
            else:
                obstacle = Obstacle(
                    x=0,
                    y=0,
                    width=48,
                    height=48,
                    obstacle_type="rock",
                    sprite=self.rock_sprite,
                    rect=pygame.Rect(0, 0, 40, 40),
                )
            self.inactive_obstacles.append(obstacle)

        self.sprites_loaded = True

    def spawn_obstacle(
        self, x: float, y: float, obstacle_type: str | None = None
    ) -> Obstacle | None:
        """Spawn an obstacle from the pool."""
        self._ensure_sprites_loaded()

        if not self.inactive_obstacles:
            return None

        obstacle = self.inactive_obstacles.pop()
        obstacle.x = x
        obstacle.y = y

        # Update rect position
        if obstacle.obstacle_type == "tree":
            # Center rect at base of tree
            obstacle.rect.centerx = int(x)
            obstacle.rect.bottom = int(y + obstacle.height - 10)
        else:
            # Center rect on rock
            obstacle.rect.center = (int(x), int(y + obstacle.height // 2))

        self.active_obstacles.append(obstacle)
        return obstacle

    def despawn_obstacle(self, obstacle: Obstacle):
        """Return an obstacle to the pool."""
        if obstacle in self.active_obstacles:
            self.active_obstacles.remove(obstacle)
            self.inactive_obstacles.append(obstacle)

    def update(self, scroll_speed: float, dt: float, screen_height: int):
        """Update all active obstacles and despawn off-screen ones."""
        obstacles_to_despawn = []

        for obstacle in self.active_obstacles:
            # Move obstacle down with scrolling
            obstacle.y += scroll_speed * dt

            # Update rect position
            if obstacle.obstacle_type == "tree":
                obstacle.rect.centerx = int(obstacle.x)
                obstacle.rect.bottom = int(obstacle.y + obstacle.height - 10)
            else:
                obstacle.rect.center = (
                    int(obstacle.x),
                    int(obstacle.y + obstacle.height // 2),
                )

            # Check if off screen
            if obstacle.y > screen_height + 100:
                obstacles_to_despawn.append(obstacle)

        # Despawn off-screen obstacles
        for obstacle in obstacles_to_despawn:
            self.despawn_obstacle(obstacle)


class TerrainChunk:
    """Represents a chunk of terrain with obstacles."""

    def __init__(self, chunk_height: int, chunk_y: float, screen_width: int):
        self.chunk_height = chunk_height
        self.chunk_y = chunk_y
        self.screen_width = screen_width
        self.obstacles: list[tuple[float, float, str]] = []
        self.snowflakes: list[tuple[float, float]] = []
        self.is_active = True

    def generate_obstacles(
        self, difficulty: float, safe_zone_x: float, safe_zone_width: float
    ):
        """Generate obstacles for this chunk with guaranteed safe path."""
        # Calculate obstacle density based on difficulty
        base_obstacles = 3
        max_obstacles = 8
        num_obstacles = int(
            base_obstacles + (max_obstacles - base_obstacles) * min(difficulty, 1.0)
        )

        # Define spawn zones (avoiding safe zone)
        left_zone = (100, safe_zone_x - safe_zone_width // 2)
        right_zone = (safe_zone_x + safe_zone_width // 2, self.screen_width - 100)

        for _ in range(num_obstacles):
            # Choose which zone to spawn in
            if random.random() < 0.5 and left_zone[1] > left_zone[0]:
                x = random.randint(int(left_zone[0]), int(left_zone[1]))
            elif right_zone[1] > right_zone[0]:
                x = random.randint(int(right_zone[0]), int(right_zone[1]))
            else:
                continue

            # Random y position within chunk
            y = self.chunk_y + random.randint(50, self.chunk_height - 50)

            # Choose obstacle type
            obstacle_type = "tree" if random.random() < 0.6 else "rock"

            self.obstacles.append((x, y, obstacle_type))

    def generate_snowflakes(self, num_snowflakes: int):
        """Generate snowflakes for this chunk."""
        for _ in range(num_snowflakes):
            # Random position across the width
            x = random.randint(100, self.screen_width - 100)
            y = self.chunk_y + random.randint(50, self.chunk_height - 50)
            self.snowflakes.append((x, y))


class SlopeGenerator:
    """Manages procedural generation of the ski slope."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Chunk system
        self.chunk_height = 300
        self.chunks: list[TerrainChunk] = []
        self.next_chunk_y = -self.chunk_height

        # Difficulty scaling
        self.base_difficulty = 0.2
        self.current_difficulty = self.base_difficulty
        self.difficulty_increase_rate = 0.01  # Per second
        self.max_difficulty = 0.8

        # Safe path parameters
        self.safe_zone_width = 200
        self.safe_zone_x = screen_width // 2
        self.safe_zone_variance = 100

        # Obstacle pool
        self.obstacle_pool = ObstaclePool()

        # Snowflake pool
        self.snowflake_pool = SnowflakePool()

        # Snowflake spawn parameters
        self.min_snowflakes_per_chunk = 2
        self.max_snowflakes_per_chunk = 5

        # Generate initial chunks
        self._generate_initial_chunks()

    def _generate_initial_chunks(self):
        """Generate initial chunks to fill the screen."""
        while self.next_chunk_y < self.screen_height + self.chunk_height:
            self._generate_chunk()

    def _generate_chunk(self):
        """Generate a new terrain chunk."""
        chunk = TerrainChunk(self.chunk_height, self.next_chunk_y, self.screen_width)

        # Vary safe zone position slightly for variety
        safe_x = self.safe_zone_x + random.randint(
            -self.safe_zone_variance, self.safe_zone_variance
        )
        safe_x = max(200, min(safe_x, self.screen_width - 200))

        # Generate obstacles with safe path
        chunk.generate_obstacles(self.current_difficulty, safe_x, self.safe_zone_width)

        # Generate snowflakes
        num_snowflakes = random.randint(
            self.min_snowflakes_per_chunk, self.max_snowflakes_per_chunk
        )
        chunk.generate_snowflakes(num_snowflakes)

        # Spawn obstacles from pool
        for x, y, obstacle_type in chunk.obstacles:
            self.obstacle_pool.spawn_obstacle(x, y, obstacle_type)

        # Spawn snowflakes from pool
        for x, y in chunk.snowflakes:
            self.snowflake_pool.spawn_snowflake(x, y)

        self.chunks.append(chunk)
        self.next_chunk_y += self.chunk_height

    def update(self, scroll_speed: float, dt: float, elapsed_time: float):
        """Update slope generation and difficulty."""
        # Update difficulty over time
        self.current_difficulty = min(
            self.base_difficulty + (elapsed_time * self.difficulty_increase_rate),
            self.max_difficulty,
        )

        # Update obstacle positions
        self.obstacle_pool.update(scroll_speed, dt, self.screen_height)

        # Update snowflake positions
        self.snowflake_pool.update(scroll_speed, dt, self.screen_height)

        # Update chunk positions
        for chunk in self.chunks[:]:
            chunk.chunk_y += scroll_speed * dt

            # Remove chunks that have scrolled off screen
            if chunk.chunk_y > self.screen_height + self.chunk_height:
                self.chunks.remove(chunk)

        # Update next chunk position
        self.next_chunk_y += scroll_speed * dt

        # Generate new chunks as needed
        while self.next_chunk_y < self.screen_height + self.chunk_height:
            self._generate_chunk()

    def draw(self, screen: pygame.Surface):
        """Draw all obstacles and snowflakes."""
        # Draw snowflakes first (behind obstacles)
        self.snowflake_pool.draw(screen)

        # Draw obstacles
        for obstacle in self.obstacle_pool.active_obstacles:
            # Draw sprite centered on position
            sprite_rect = obstacle.sprite.get_rect()
            sprite_rect.centerx = int(obstacle.x)
            sprite_rect.bottom = int(obstacle.y + obstacle.height)
            screen.blit(obstacle.sprite, sprite_rect)

    def get_obstacles(self) -> list[Obstacle]:
        """Get all active obstacles for collision detection."""
        return self.obstacle_pool.active_obstacles

    def get_snowflake_pool(self) -> SnowflakePool:
        """Get the snowflake pool for collision detection."""
        return self.snowflake_pool

    def reset(self):
        """Reset the slope generator to initial state."""
        # Clear all chunks
        self.chunks.clear()

        # Reset obstacle pool
        for obstacle in self.obstacle_pool.active_obstacles[:]:
            self.obstacle_pool.despawn_obstacle(obstacle)

        # Reset snowflake pool
        for snowflake in self.snowflake_pool.active_snowflakes[:]:
            self.snowflake_pool.despawn_snowflake(snowflake)

        # Reset difficulty
        self.current_difficulty = self.base_difficulty

        # Reset chunk position
        self.next_chunk_y = -self.chunk_height

        # Generate initial chunks
        self._generate_initial_chunks()
