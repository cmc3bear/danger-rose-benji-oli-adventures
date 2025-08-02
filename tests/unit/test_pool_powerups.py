import time
from unittest.mock import Mock, patch

import pygame
import pytest

from src.entities.pool_targets import DuckTarget
from src.entities.powerup import RapidFirePowerUp, TripleShotPowerUp
from src.scenes.pool import PoolGame, WaterBalloon


@pytest.fixture
def mock_scene_manager():
    """Create a mock scene manager."""
    manager = Mock()
    manager.screen_width = 1280
    manager.screen_height = 720
    manager.game_data = {"selected_character": "Danger"}
    manager.sound_manager = Mock()

    # Mock save manager with proper data structure
    save_manager = Mock()
    save_manager._current_save_data = {"high_scores": {}}
    manager.save_manager = save_manager

    return manager


@pytest.fixture
def pool_game(mock_scene_manager):
    """Create a pool game instance."""
    # Mock pygame.font.Font to return a mock font
    # Create a single surface to reuse instead of creating new ones
    test_surface = pygame.Surface((100, 30))
    test_rect = pygame.Rect(0, 0, 100, 30)

    mock_font = Mock()
    mock_font.render = Mock(return_value=test_surface)
    mock_font.get_rect = Mock(return_value=test_rect)

    with patch("pygame.font.Font", return_value=mock_font):
        game = PoolGame(mock_scene_manager)
    return game


class TestPoolPowerUpSpawning:
    """Test power-up spawning in pool game."""

    def test_spawn_powerup(self, pool_game):
        """Test spawning a power-up."""
        initial_count = len(pool_game.powerups)
        pool_game.spawn_powerup()

        assert len(pool_game.powerups) == initial_count + 1
        powerup = pool_game.powerups[-1]

        # Check position is within bounds
        assert 200 <= powerup.x <= pool_game.screen_width - 200
        assert 200 <= powerup.y <= 400

    def test_spawn_timing(self, pool_game):
        """Test power-up spawn timing."""
        pool_game.state = pool_game.STATE_PLAYING
        pool_game.start_time = time.time() - 8.0  # Start 8 seconds ago

        # Update to trigger spawn
        pool_game.update(0.1)
        assert len(pool_game.powerups) == 1

        # Should not spawn another immediately
        pool_game.update(0.1)
        assert len(pool_game.powerups) == 1

    def test_max_powerups_limit(self, pool_game):
        """Test maximum power-ups on field limit."""
        pool_game.state = pool_game.STATE_PLAYING

        # Spawn max power-ups
        for _ in range(pool_game.max_powerups_on_field):
            pool_game.spawn_powerup()

        count = len(pool_game.powerups)
        pool_game.time_remaining = 0  # Trigger spawn condition
        pool_game.update(0.1)

        # Should not exceed max
        assert len(pool_game.powerups) == count


class TestPoolPowerUpCollection:
    """Test power-up collection mechanics."""

    def test_collect_powerup(self, pool_game):
        """Test collecting a power-up."""
        powerup = TripleShotPowerUp(100, 100)
        pool_game.powerups.append(powerup)

        # Move player near power-up
        pool_game.player.x = 100
        pool_game.player.y = 100

        # Update to trigger collection
        pool_game.state = pool_game.STATE_PLAYING
        pool_game.update(0.1)

        # Power-up should be collected
        assert len(pool_game.powerups) == 0
        assert len(pool_game.active_powerups) == 1
        assert pool_game.triple_shot_active is True

    def test_powerup_expiration(self, pool_game):
        """Test power-up expiration."""
        powerup = TripleShotPowerUp(0, 0)
        pool_game.collect_powerup(powerup)

        assert pool_game.triple_shot_active is True

        # Mock expired power-up
        pool_game.active_powerups[0].is_expired = Mock(return_value=True)

        pool_game.state = pool_game.STATE_PLAYING
        pool_game.update(0.1)

        # Should be removed and effect disabled
        assert len(pool_game.active_powerups) == 0
        assert pool_game.triple_shot_active is False

    def test_same_type_replacement(self, pool_game):
        """Test replacing power-up of same type."""
        powerup1 = TripleShotPowerUp(0, 0)
        powerup2 = TripleShotPowerUp(0, 0)

        pool_game.collect_powerup(powerup1)
        assert len(pool_game.active_powerups) == 1

        # Collect same type
        pool_game.collect_powerup(powerup2)

        # Should still have only one
        assert len(pool_game.active_powerups) == 1


class TestTripleShotMechanic:
    """Test triple shot shooting mechanic."""

    def test_triple_shot_creates_three_balloons(self, pool_game):
        """Test that triple shot creates 3 balloons."""
        pool_game.triple_shot_active = True
        pool_game.can_shoot = True
        pool_game.current_ammo = 5
        pool_game.mouse_x = 500
        pool_game.mouse_y = 300

        initial_count = len(pool_game.projectiles)
        pool_game.shoot_balloon()

        # Should create 3 balloons
        assert len(pool_game.projectiles) == initial_count + 3

        # Only uses 1 ammo
        assert pool_game.current_ammo == 4

    def test_triple_shot_spread_pattern(self, pool_game):
        """Test triple shot spread pattern."""
        pool_game.triple_shot_active = True
        pool_game.can_shoot = True
        pool_game.current_ammo = 5
        pool_game.player.x = 640
        pool_game.player.y = 600
        pool_game.mouse_x = 640
        pool_game.mouse_y = 400

        pool_game.shoot_balloon()

        # Check that balloons have different velocities
        velocities = [(b.vx, b.vy) for b in pool_game.projectiles]
        assert len(set(velocities)) == 3  # All different


class TestRapidFireMechanic:
    """Test rapid fire mechanic."""

    def test_rapid_fire_reduces_cooldown(self, pool_game):
        """Test that rapid fire reduces shot cooldown."""
        original_reload = pool_game.reload_time
        original_duration = pool_game.reload_duration

        powerup = RapidFirePowerUp(0, 0)
        pool_game.collect_powerup(powerup)

        assert pool_game.reload_time < original_reload
        assert pool_game.reload_duration < original_duration
        assert pool_game.rapid_fire_active is True

    def test_rapid_fire_restoration(self, pool_game):
        """Test restoring normal fire rate."""
        powerup = RapidFirePowerUp(0, 0)
        powerup.apply_effect(pool_game)
        powerup.remove_effect(pool_game)

        assert pool_game.reload_time == pool_game.original_reload_time
        assert pool_game.reload_duration == pool_game.original_reload_duration
        assert pool_game.rapid_fire_active is False


class TestHomingMechanic:
    """Test homing balloon mechanic."""

    def test_homing_balloon_creation(self, pool_game):
        """Test creating homing balloons."""
        pool_game.homing_active = True
        pool_game.can_shoot = True
        pool_game.current_ammo = 5

        pool_game.shoot_balloon()

        balloon = pool_game.projectiles[-1]
        assert balloon.is_homing is True

    def test_homing_balloon_tracking(self):
        """Test homing balloon tracking targets."""
        # Create a homing balloon
        balloon = WaterBalloon(100, 100, 200, 200, is_homing=True)

        # Create targets
        target1 = DuckTarget(150, 150)
        target2 = DuckTarget(500, 500)
        targets = [target1, target2]

        # Store initial velocity
        initial_vx = balloon.vx
        initial_vy = balloon.vy

        # Update with targets
        balloon.update(0.1, targets)

        # Velocity should change towards nearest target
        assert balloon.vx != initial_vx or balloon.vy != initial_vy

    def test_homing_ignores_hit_targets(self):
        """Test homing ignores already hit targets."""
        balloon = WaterBalloon(100, 100, 200, 200, is_homing=True)

        # Create hit target
        target = DuckTarget(150, 150)
        target.active = False
        targets = [target]

        # Store initial velocity
        initial_vx = balloon.vx

        # Update should not change velocity
        balloon.update(0.1, targets)

        # Velocity should not change (accounting for gravity)
        assert abs(balloon.vx - initial_vx) < 0.01


class TestPowerUpUI:
    """Test power-up UI display."""

    def test_active_powerup_display(self, pool_game):
        """Test drawing active power-ups doesn't crash."""
        # Don't initialize pygame here - it's already initialized
        screen = pygame.Surface((1280, 720))

        # Add active power-ups
        powerup1 = TripleShotPowerUp(0, 0)
        powerup2 = RapidFirePowerUp(0, 0)

        pool_game.collect_powerup(powerup1)
        pool_game.collect_powerup(powerup2)

        # Should not crash
        pool_game.state = pool_game.STATE_PLAYING
        try:
            pool_game.draw_game_ui(screen)
        except Exception as e:
            pytest.fail(f"draw_game_ui raised {e!r}")


class TestPowerUpReset:
    """Test power-up system reset."""

    def test_reset_clears_powerups(self, pool_game):
        """Test that resetting game clears all power-ups."""
        # Add power-ups
        pool_game.spawn_powerup()
        powerup = TripleShotPowerUp(0, 0)
        pool_game.collect_powerup(powerup)

        assert len(pool_game.powerups) > 0
        assert len(pool_game.active_powerups) > 0
        assert pool_game.triple_shot_active is True

        # Reset game
        pool_game.reset_game()

        # All should be cleared
        assert len(pool_game.powerups) == 0
        assert len(pool_game.active_powerups) == 0
        assert pool_game.triple_shot_active is False
