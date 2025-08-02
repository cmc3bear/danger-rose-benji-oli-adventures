"""Tests for the Snowflake entity and related classes."""

from unittest.mock import Mock, patch

import pytest

from src.entities.snowflake import Snowflake, SnowflakeEffect, SnowflakePool


class TestSnowflake:
    """Test individual snowflake behavior."""

    def test_initialization(self):
        """Snowflake should initialize with dataclass values."""
        # Act
        snowflake = Snowflake(x=100, y=50)

        # Assert
        assert snowflake.x == 100
        assert snowflake.y == 50
        assert snowflake.width == 32
        assert snowflake.height == 32
        assert snowflake.collected is False
        assert snowflake.sprite is None
        assert snowflake.rect is None
        assert snowflake.float_offset == 0.0
        assert snowflake.float_speed == 2.0
        assert snowflake.float_amplitude == 10.0
        assert snowflake.rotation == 0.0
        assert snowflake.rotation_speed == 2.0


class TestSnowflakePool:
    """Test snowflake pool management."""

    def test_initialization(self):
        """SnowflakePool should initialize with empty lists."""
        # Act
        pool = SnowflakePool(max_snowflakes=30)

        # Assert
        assert pool.max_snowflakes == 30
        assert pool.active_snowflakes == []
        assert pool.inactive_snowflakes == []
        assert pool.snowflake_sprite is None
        assert pool.sprites_loaded is False

    @patch("src.entities.snowflake.load_image")
    def test_spawn_snowflake_first_time_loads_sprite(self, mock_load_image):
        """First spawn should load the sprite."""
        # Arrange
        pool = SnowflakePool()
        mock_sprite = Mock()
        mock_load_image.return_value = mock_sprite

        # Act
        snowflake = pool.spawn_snowflake(100, 200)

        # Assert
        assert pool.sprites_loaded is True
        assert pool.snowflake_sprite == mock_sprite
        mock_load_image.assert_called_once()
        assert snowflake is not None
        assert snowflake.x == 100
        assert snowflake.y == 200

    @patch("src.entities.snowflake.load_image")
    def test_spawn_reuses_inactive_snowflakes(self, mock_load_image):
        """Spawn should reuse inactive snowflakes when available."""
        # Arrange
        pool = SnowflakePool()
        mock_load_image.return_value = Mock()

        # Create and despawn a snowflake
        snowflake = pool.spawn_snowflake(50, 50)
        pool.despawn_snowflake(snowflake)

        # Act
        new_snowflake = pool.spawn_snowflake(100, 200)

        # Assert
        assert new_snowflake is snowflake  # Same object reused
        assert new_snowflake.x == 100
        assert new_snowflake.y == 200
        assert new_snowflake.collected is False

    def test_despawn_moves_to_inactive(self):
        """Despawn should move snowflake to inactive list."""
        # Arrange
        pool = SnowflakePool()
        pool.sprites_loaded = True  # Skip sprite loading
        snowflake = Snowflake(100, 100)
        pool.active_snowflakes.append(snowflake)

        # Act
        pool.despawn_snowflake(snowflake)

        # Assert
        assert snowflake not in pool.active_snowflakes
        assert snowflake in pool.inactive_snowflakes
        # Note: despawn_snowflake doesn't set collected to True

    @patch("src.entities.snowflake.load_image")
    def test_update_animations(self, mock_load_image):
        """Update should animate all active snowflakes."""
        # Arrange
        pool = SnowflakePool()
        mock_load_image.return_value = Mock()

        # Create active snowflakes
        snowflake1 = pool.spawn_snowflake(100, 100)
        snowflake2 = pool.spawn_snowflake(200, 200)

        # Act
        pool.update(scroll_speed=100, dt=0.016, screen_height=600)  # 60 FPS delta time

        # Assert
        # Check that animation values changed
        assert snowflake1.float_offset > 0
        assert snowflake1.rotation > 0
        assert snowflake2.float_offset > 0
        assert snowflake2.rotation > 0


class TestSnowflakeEffect:
    """Test snowflake visual effect."""

    def test_initialization(self):
        """SnowflakeEffect should initialize with particles."""
        # Act
        effect = SnowflakeEffect(100, 100)

        # Assert
        assert effect.x == 100
        assert effect.y == 100
        assert len(effect.particles) == 8  # Fixed number in constructor
        assert effect.lifetime == 0.5  # Different default lifetime
        # SnowflakeEffect doesn't have 'alive' attribute

    def test_update_moves_particles(self):
        """Update should move particles and reduce lifetime."""
        # Arrange
        effect = SnowflakeEffect(100, 100)
        initial_positions = [(p["x"], p["y"]) for p in effect.particles]

        # Act
        effect.update(0.1)  # 100ms

        # Assert
        assert effect.lifetime == pytest.approx(0.4)  # 0.5 - 0.1
        # All particles should have moved
        for i, particle in enumerate(effect.particles):
            assert (particle["x"], particle["y"]) != initial_positions[i]

    def test_effect_dies_after_lifetime(self):
        """Effect should die when lifetime reaches zero."""
        # Arrange
        effect = SnowflakeEffect(100, 100)

        # Act
        result = effect.update(0.6)  # More than lifetime (0.5)

        # Assert
        assert effect.lifetime <= 0
        assert result is False  # update returns False when effect is complete

    @patch("pygame.Surface")
    @patch("pygame.draw.circle")
    def test_draw_renders_particles(self, mock_draw_circle, mock_surface_class):
        """Draw should render all particles."""
        # Arrange
        effect = SnowflakeEffect(100, 100)  # Creates 8 particles
        mock_screen = Mock()
        mock_glow_surf = Mock()
        mock_surface_class.return_value = mock_glow_surf

        # Act
        effect.draw(mock_screen)

        # Assert
        # Should draw each particle (8 particles, some with glow effect)
        assert mock_draw_circle.call_count >= 8
