import time
from unittest.mock import Mock

import pygame
import pytest

from src.entities.powerup import (
    ActivePowerUp,
    HomingPowerUp,
    RapidFirePowerUp,
    TripleShotPowerUp,
)


@pytest.fixture
def mock_pool_game():
    """Create a mock pool game object."""
    game = Mock()
    game.triple_shot_active = False
    game.rapid_fire_active = False
    game.homing_active = False
    game.reload_time = 0.5
    game.reload_duration = 2.0
    game.original_reload_time = 0.5
    game.original_reload_duration = 2.0
    return game


class TestTripleShotPowerUp:
    """Test the triple shot power-up."""

    def test_initialization(self):
        """Test power-up initialization."""
        powerup = TripleShotPowerUp(100, 200)
        assert powerup.x == 100
        assert powerup.y == 200
        assert not powerup.collected
        assert powerup.active

    def test_properties(self):
        """Test power-up properties."""
        powerup = TripleShotPowerUp(0, 0)
        assert powerup.get_name() == "Triple Shot"
        assert powerup.get_icon_type() == "triple"
        assert powerup.get_duration() == 10.0
        assert powerup.get_color() == (0, 255, 255)

    def test_apply_effect(self, mock_pool_game):
        """Test applying the triple shot effect."""
        powerup = TripleShotPowerUp(0, 0)
        powerup.apply_effect(mock_pool_game)
        assert mock_pool_game.triple_shot_active is True

    def test_remove_effect(self, mock_pool_game):
        """Test removing the triple shot effect."""
        powerup = TripleShotPowerUp(0, 0)
        mock_pool_game.triple_shot_active = True
        powerup.remove_effect(mock_pool_game)
        assert mock_pool_game.triple_shot_active is False

    def test_collection(self):
        """Test power-up collection."""
        powerup = TripleShotPowerUp(100, 100)

        # Player too far away
        assert not powerup.check_collection(200, 200)
        assert not powerup.collected

        # Player close enough
        assert powerup.check_collection(110, 110)
        assert powerup.collected

        # Can't collect again
        assert not powerup.check_collection(110, 110)


class TestRapidFirePowerUp:
    """Test the rapid fire power-up."""

    def test_properties(self):
        """Test power-up properties."""
        powerup = RapidFirePowerUp(0, 0)
        assert powerup.get_name() == "Rapid Fire"
        assert powerup.get_icon_type() == "rapid"
        assert powerup.get_duration() == 8.0
        assert powerup.get_color() == (220, 200, 60)  # COLOR_YELLOW

    def test_apply_effect(self, mock_pool_game):
        """Test applying the rapid fire effect."""
        powerup = RapidFirePowerUp(0, 0)
        powerup.apply_effect(mock_pool_game)

        assert mock_pool_game.rapid_fire_active is True
        assert mock_pool_game.reload_time == 0.15
        assert mock_pool_game.reload_duration == 0.5

    def test_remove_effect(self, mock_pool_game):
        """Test removing the rapid fire effect."""
        powerup = RapidFirePowerUp(0, 0)
        powerup.apply_effect(mock_pool_game)
        powerup.remove_effect(mock_pool_game)

        assert mock_pool_game.rapid_fire_active is False
        assert mock_pool_game.reload_time == mock_pool_game.original_reload_time
        assert mock_pool_game.reload_duration == mock_pool_game.original_reload_duration


class TestHomingPowerUp:
    """Test the homing power-up."""

    def test_properties(self):
        """Test power-up properties."""
        powerup = HomingPowerUp(0, 0)
        assert powerup.get_name() == "Homing Balloons"
        assert powerup.get_icon_type() == "homing"
        assert powerup.get_duration() == 12.0
        assert powerup.get_color() == (180, 60, 60)  # COLOR_RED

    def test_apply_effect(self, mock_pool_game):
        """Test applying the homing effect."""
        powerup = HomingPowerUp(0, 0)
        powerup.apply_effect(mock_pool_game)
        assert mock_pool_game.homing_active is True

    def test_remove_effect(self, mock_pool_game):
        """Test removing the homing effect."""
        powerup = HomingPowerUp(0, 0)
        mock_pool_game.homing_active = True
        powerup.remove_effect(mock_pool_game)
        assert mock_pool_game.homing_active is False


class TestActivePowerUp:
    """Test the active power-up tracker."""

    def test_initialization(self):
        """Test active power-up initialization."""
        powerup = TripleShotPowerUp(0, 0)
        active = ActivePowerUp(powerup)

        assert active.powerup == powerup
        assert active.duration == 10.0
        assert active.name == "Triple Shot"
        assert active.color == (0, 255, 255)

    def test_expiration(self):
        """Test power-up expiration."""
        powerup = Mock()
        powerup.get_duration.return_value = 0.1
        powerup.get_name.return_value = "Test"
        powerup.get_color.return_value = (255, 255, 255)

        active = ActivePowerUp(powerup)
        assert not active.is_expired()

        # Wait for expiration
        time.sleep(0.15)
        assert active.is_expired()
        assert active.get_time_remaining() == 0

    def test_progress(self):
        """Test power-up progress calculation."""
        powerup = Mock()
        powerup.get_duration.return_value = 10.0
        powerup.get_name.return_value = "Test"
        powerup.get_color.return_value = (255, 255, 255)

        active = ActivePowerUp(powerup)

        # Should start at 100% progress
        assert 0.95 <= active.get_progress() <= 1.0

        # Mock time passage
        active.start_time -= 5  # Simulate 5 seconds passed
        assert 0.45 <= active.get_progress() <= 0.55


class TestPowerUpAnimation:
    """Test power-up animation and visual effects."""

    def test_update_animation(self):
        """Test power-up animation update."""
        powerup = TripleShotPowerUp(100, 100)
        initial_pulse = powerup.pulse_time
        initial_float = powerup.float_time

        # Update animation
        powerup.update(0.1)

        assert powerup.pulse_time > initial_pulse
        assert powerup.float_time > initial_float
        assert powerup.float_offset != 0  # Should have some floating offset

    def test_collision_rect_update(self):
        """Test that collision rect follows animation."""
        powerup = TripleShotPowerUp(100, 100)

        # Update to create float offset
        powerup.update(0.5)

        # Rect should follow the floating position
        assert powerup.rect.centerx == 100
        assert powerup.rect.centery == int(100 + powerup.float_offset)


class TestPowerUpIntegration:
    """Test power-up integration with pool game."""

    def test_multiple_powerup_collection(self, mock_pool_game):
        """Test collecting multiple power-ups."""
        triple = TripleShotPowerUp(0, 0)
        rapid = RapidFirePowerUp(0, 0)

        # Apply both
        triple.apply_effect(mock_pool_game)
        rapid.apply_effect(mock_pool_game)

        # Both should be active
        assert mock_pool_game.triple_shot_active is True
        assert mock_pool_game.rapid_fire_active is True

        # Remove one
        triple.remove_effect(mock_pool_game)
        assert mock_pool_game.triple_shot_active is False
        assert mock_pool_game.rapid_fire_active is True

    def test_powerup_draw(self):
        """Test power-up drawing doesn't crash."""
        pygame.init()
        screen = pygame.Surface((100, 100))

        powerup = TripleShotPowerUp(50, 50)

        # Should not raise any exceptions
        powerup.draw(screen)

        # After collection, should not draw
        powerup.collected = True
        powerup.draw(screen)  # Should do nothing
