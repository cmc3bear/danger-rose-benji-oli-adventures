import pygame
import pytest

from src.entities.snowflake import Snowflake, SnowflakeEffect, SnowflakePool


class TestSnowflake:
    """Test the Snowflake entity."""

    def test_snowflake_initialization(self):
        """Test snowflake is initialized with correct properties."""
        snowflake = Snowflake(x=100, y=200)

        assert snowflake.x == 100
        assert snowflake.y == 200
        assert snowflake.width == 32
        assert snowflake.height == 32
        assert not snowflake.collected
        assert snowflake.float_offset == 0.0
        assert snowflake.float_speed == 2.0
        assert snowflake.float_amplitude == 10.0
        assert snowflake.rotation == 0.0
        assert snowflake.rotation_speed == 2.0


class TestSnowflakePool:
    """Test the SnowflakePool object pooling system."""

    @pytest.fixture
    def pool(self):
        """Create a snowflake pool for testing."""
        return SnowflakePool(max_snowflakes=5)

    def test_pool_initialization(self, pool):
        """Test pool is initialized correctly."""
        assert pool.max_snowflakes == 5
        assert len(pool.active_snowflakes) == 0
        assert len(pool.inactive_snowflakes) == 0
        assert not pool.sprites_loaded

    def test_spawn_snowflake(self, pool):
        """Test spawning a snowflake from the pool."""
        # Spawn first snowflake
        snowflake = pool.spawn_snowflake(150, 250)

        assert snowflake is not None
        assert snowflake.x == 150
        assert snowflake.y == 250
        assert not snowflake.collected
        assert len(pool.active_snowflakes) == 1
        assert len(pool.inactive_snowflakes) == 4  # 5 total - 1 active

    def test_spawn_max_snowflakes(self, pool):
        """Test spawning maximum number of snowflakes."""
        snowflakes = []
        for i in range(5):
            snowflake = pool.spawn_snowflake(100 * i, 200)
            snowflakes.append(snowflake)

        assert len(pool.active_snowflakes) == 5
        assert len(pool.inactive_snowflakes) == 0

        # Try to spawn one more - should return None
        extra_snowflake = pool.spawn_snowflake(600, 200)
        assert extra_snowflake is None

    def test_despawn_snowflake(self, pool):
        """Test despawning a snowflake back to the pool."""
        snowflake = pool.spawn_snowflake(100, 200)
        assert len(pool.active_snowflakes) == 1

        pool.despawn_snowflake(snowflake)
        assert len(pool.active_snowflakes) == 0
        assert len(pool.inactive_snowflakes) == 5

    def test_update_snowflakes(self, pool):
        """Test updating snowflake positions."""
        snowflake = pool.spawn_snowflake(100, 100)
        initial_y = snowflake.y

        # Update with scroll speed
        pool.update(scroll_speed=100, dt=0.1, screen_height=600)

        # Snowflake should have moved down
        assert snowflake.y > initial_y
        assert snowflake.y == initial_y + 10  # 100 * 0.1

    def test_despawn_offscreen_snowflakes(self, pool):
        """Test that off-screen snowflakes are despawned."""
        # Spawn snowflake near bottom of screen
        pool.spawn_snowflake(100, 600)
        assert len(pool.active_snowflakes) == 1

        # Update to move it off screen
        pool.update(scroll_speed=200, dt=1.0, screen_height=600)

        # Should be despawned
        assert len(pool.active_snowflakes) == 0
        assert len(pool.inactive_snowflakes) == 5

    def test_check_collection(self, pool):
        """Test collision detection for snowflake collection."""
        pygame.init()

        # Spawn a snowflake
        snowflake = pool.spawn_snowflake(100, 100)

        # Create player rect that overlaps
        player_rect = pygame.Rect(90, 90, 50, 50)
        collected = pool.check_collection(player_rect)

        assert len(collected) == 1
        assert collected[0] == snowflake
        assert snowflake.collected

        # Check again - should not collect already collected snowflake
        collected_again = pool.check_collection(player_rect)
        assert len(collected_again) == 0


class TestSnowflakeEffect:
    """Test the SnowflakeEffect visual effect."""

    def test_effect_initialization(self):
        """Test effect is initialized with particles."""
        effect = SnowflakeEffect(200, 300)

        assert effect.x == 200
        assert effect.y == 300
        assert effect.lifetime == 0.5
        assert len(effect.particles) == 8

    def test_particle_properties(self):
        """Test particles have correct properties."""
        effect = SnowflakeEffect(200, 300)

        for particle in effect.particles:
            assert particle["x"] == 200
            assert particle["y"] == 300
            assert "vx" in particle
            assert "vy" in particle
            assert 2 <= particle["size"] <= 4
            assert 0.3 <= particle["lifetime"] <= 0.5

    def test_effect_update(self):
        """Test effect updates correctly."""
        effect = SnowflakeEffect(200, 300)

        # Update effect
        still_alive = effect.update(0.1)

        assert still_alive
        assert effect.lifetime < 0.5

        # Particles should have moved
        for particle in effect.particles:
            assert particle["x"] != 200 or particle["y"] != 300

    def test_effect_expiration(self):
        """Test effect expires after lifetime."""
        effect = SnowflakeEffect(200, 300)

        # Update with large time step
        still_alive = effect.update(1.0)

        assert not still_alive
        assert effect.lifetime <= 0
