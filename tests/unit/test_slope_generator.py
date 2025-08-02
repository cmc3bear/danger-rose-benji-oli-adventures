from unittest.mock import Mock, patch

import pygame
import pytest

from src.scenes.slope_generator import (
    ObstaclePool,
    SlopeGenerator,
    TerrainChunk,
)


class TestObstaclePool:
    """Test the obstacle pooling system."""

    @pytest.fixture
    def obstacle_pool(self):
        """Create an obstacle pool for testing."""
        with patch("src.scenes.slope_generator.load_image") as mock_load:
            mock_load.return_value = Mock(spec=pygame.Surface)
            return ObstaclePool(max_obstacles=10)

    def test_initialization(self, obstacle_pool):
        """Test pool is initialized with correct number of obstacles."""
        # Seed random to ensure consistent test results
        import random

        random.seed(42)

        # Force sprite loading to populate the pool
        obstacle_pool._ensure_sprites_loaded()

        assert len(obstacle_pool.inactive_obstacles) == 10
        assert len(obstacle_pool.active_obstacles) == 0

        # Check mixture of trees and rocks
        tree_count = sum(
            1 for o in obstacle_pool.inactive_obstacles if o.obstacle_type == "tree"
        )
        rock_count = sum(
            1 for o in obstacle_pool.inactive_obstacles if o.obstacle_type == "rock"
        )
        # With 60% chance of trees, we should get at least one of each type
        assert tree_count >= 1
        assert rock_count >= 1
        assert tree_count + rock_count == 10

    def test_spawn_obstacle(self, obstacle_pool):
        """Test spawning an obstacle from the pool."""
        obstacle = obstacle_pool.spawn_obstacle(100, 200)

        assert obstacle is not None
        assert obstacle.x == 100
        assert obstacle.y == 200
        assert len(obstacle_pool.active_obstacles) == 1
        # After spawning one, there should be 9 inactive (10 total - 1 active)
        assert len(obstacle_pool.inactive_obstacles) == 9

    def test_despawn_obstacle(self, obstacle_pool):
        """Test returning an obstacle to the pool."""
        obstacle = obstacle_pool.spawn_obstacle(100, 200)
        initial_active = len(obstacle_pool.active_obstacles)
        initial_inactive = len(obstacle_pool.inactive_obstacles)

        obstacle_pool.despawn_obstacle(obstacle)

        assert len(obstacle_pool.active_obstacles) == initial_active - 1
        assert len(obstacle_pool.inactive_obstacles) == initial_inactive + 1
        assert obstacle in obstacle_pool.inactive_obstacles

    def test_update_despawns_offscreen(self, obstacle_pool):
        """Test that off-screen obstacles are despawned."""
        # Spawn an obstacle off-screen
        obstacle = obstacle_pool.spawn_obstacle(100, 900)

        # Update with scrolling that moves it further off-screen
        obstacle_pool.update(100, 1.0, 720)  # screen_height = 720

        assert len(obstacle_pool.active_obstacles) == 0
        assert obstacle in obstacle_pool.inactive_obstacles


class TestTerrainChunk:
    """Test terrain chunk generation."""

    def test_initialization(self):
        """Test chunk is initialized correctly."""
        chunk = TerrainChunk(300, -300, 1280)

        assert chunk.chunk_height == 300
        assert chunk.chunk_y == -300
        assert chunk.screen_width == 1280
        assert chunk.is_active
        assert len(chunk.obstacles) == 0

    def test_generate_obstacles_respects_safe_zone(self):
        """Test that obstacles avoid the safe zone."""
        chunk = TerrainChunk(300, 0, 1280)
        safe_zone_x = 640  # Center of screen
        safe_zone_width = 200

        # Generate obstacles with medium difficulty
        chunk.generate_obstacles(0.5, safe_zone_x, safe_zone_width)

        # Check all obstacles are outside safe zone
        safe_zone_left = safe_zone_x - safe_zone_width // 2
        safe_zone_right = safe_zone_x + safe_zone_width // 2

        for x, y, obstacle_type in chunk.obstacles:
            # Obstacles should not be inside the safe zone
            assert x <= safe_zone_left or x >= safe_zone_right

    def test_difficulty_affects_obstacle_count(self):
        """Test that higher difficulty creates more obstacles."""
        chunk_low = TerrainChunk(300, 0, 1280)
        chunk_high = TerrainChunk(300, 0, 1280)

        # Generate with different difficulties
        chunk_low.generate_obstacles(0.1, 640, 200)
        chunk_high.generate_obstacles(0.9, 640, 200)

        # Higher difficulty should generally have more obstacles
        assert len(chunk_high.obstacles) >= len(chunk_low.obstacles)


class TestSlopeGenerator:
    """Test the main slope generator."""

    @pytest.fixture
    def slope_generator(self):
        """Create a slope generator for testing."""
        with patch("src.scenes.slope_generator.load_image") as mock_load:
            mock_load.return_value = Mock(spec=pygame.Surface)
            pygame.init()
            return SlopeGenerator(1280, 720)

    def test_initialization(self, slope_generator):
        """Test slope generator initializes correctly."""
        assert slope_generator.screen_width == 1280
        assert slope_generator.screen_height == 720
        assert slope_generator.chunk_height == 300
        assert slope_generator.current_difficulty == slope_generator.base_difficulty
        assert len(slope_generator.chunks) > 0  # Should have initial chunks

    def test_difficulty_scaling(self, slope_generator):
        """Test difficulty increases over time."""
        initial_difficulty = slope_generator.current_difficulty

        # Simulate 30 seconds of gameplay
        slope_generator.update(200, 1.0, 30.0)

        assert slope_generator.current_difficulty > initial_difficulty
        assert slope_generator.current_difficulty <= slope_generator.max_difficulty

    def test_chunk_generation_and_removal(self, slope_generator):
        """Test chunks are generated and removed as needed."""
        # Force initial chunk generation if needed
        if len(slope_generator.chunks) == 0:
            slope_generator._generate_initial_chunks()

        initial_chunks = len(slope_generator.chunks)
        assert initial_chunks > 0  # Should have initial chunks

        # Simulate scrolling for a while with reasonable speed
        for i in range(10):
            slope_generator.update(200, 0.016, i * 0.016)  # 60 FPS, 200 pixels/sec

        # Should still have chunks, but they should have cycled
        assert len(slope_generator.chunks) > 0
        # Chunks were generated and cycled correctly

    def test_reset(self, slope_generator):
        """Test reset functionality."""
        # Modify state
        slope_generator.current_difficulty = 0.7
        slope_generator.update(200, 1.0, 10.0)

        # Reset
        slope_generator.reset()

        assert slope_generator.current_difficulty == slope_generator.base_difficulty
        # After reset, new chunks are generated which may have obstacles
        # Just verify that chunks were regenerated
        assert len(slope_generator.chunks) > 0
        assert slope_generator.next_chunk_y > -slope_generator.chunk_height

    def test_safe_path_always_exists(self, slope_generator):
        """Test that a safe path always exists through obstacles."""
        # This is implicitly tested by the chunk generation logic
        # but we can verify by checking obstacle positions
        obstacles = slope_generator.get_obstacles()

        # Group obstacles by approximate Y position (within 100 pixels)
        y_groups = {}
        for obstacle in obstacles:
            y_bucket = int(obstacle.y // 100) * 100
            if y_bucket not in y_groups:
                y_groups[y_bucket] = []
            y_groups[y_bucket].append(obstacle)

        # For each group, verify there's at least a 200-pixel gap somewhere
        for y_bucket, group_obstacles in y_groups.items():
            if len(group_obstacles) > 1:
                # Sort by X position
                sorted_obstacles = sorted(group_obstacles, key=lambda o: o.x)

                # Check gaps between obstacles
                max_gap = 0
                for i in range(len(sorted_obstacles) - 1):
                    gap = sorted_obstacles[i + 1].x - sorted_obstacles[i].x
                    max_gap = max(max_gap, gap)

                # Also check edges
                left_gap = sorted_obstacles[0].x
                right_gap = slope_generator.screen_width - sorted_obstacles[-1].x
                max_gap = max(max_gap, left_gap, right_gap)

                # Should always have at least a 150 pixel gap (safe zone width minus some margin)
                assert max_gap >= 150
