"""Tests for the ski minigame scene."""

import time
from unittest.mock import Mock

import pygame
import pytest

from src.config.constants import SCENE_HUB_WORLD
from src.scene_manager import SceneManager
from src.scenes.ski import SkiGame, SkiPlayer


@pytest.fixture
def scene_manager():
    """Create a mock scene manager."""
    manager = Mock(spec=SceneManager)
    manager.screen_width = 800
    manager.screen_height = 600
    manager.game_data = {"selected_character": "Danger"}
    manager.sound_manager = Mock()  # Add mock sound manager
    return manager


@pytest.fixture
def ski_game(scene_manager):
    """Create a ski game instance."""
    return SkiGame(scene_manager)


class TestSkiPlayer:
    """Test the SkiPlayer class."""

    def test_player_initialization(self):
        """Test player is created with correct initial values."""
        player = SkiPlayer(400, 300, "Danger")
        assert player.x == 400
        assert player.y == 300
        assert player.character_name == "Danger"
        assert player.speed == 5
        # Rect is initialized smaller and centered
        assert player.rect.centerx == 400
        assert player.rect.centery == 300
        assert player.rect.width == 48
        assert player.rect.height == 48
        # Check crash state
        assert not player.is_crashing
        assert not player.invincible

    def test_player_movement_left(self):
        """Test player moves left with arrow key."""
        player = SkiPlayer(400, 300, "Danger")

        # Create a mock keys dictionary
        keys = {
            pygame.K_LEFT: True,
            pygame.K_RIGHT: False,
            pygame.K_a: False,
            pygame.K_d: False,
        }

        # Mock pygame.key.get_pressed to return our dictionary
        mock_keys = Mock()
        mock_keys.__getitem__ = Mock(side_effect=lambda k: keys.get(k, False))

        # Move player
        player.handle_input(mock_keys, 800)
        assert player.x == 395  # 400 - 5

    def test_player_movement_right(self):
        """Test player moves right with arrow key."""
        player = SkiPlayer(400, 300, "Danger")

        # Create a mock keys dictionary
        keys = {
            pygame.K_RIGHT: True,
            pygame.K_LEFT: False,
            pygame.K_a: False,
            pygame.K_d: False,
        }

        # Mock pygame.key.get_pressed to return our dictionary
        mock_keys = Mock()
        mock_keys.__getitem__ = Mock(side_effect=lambda k: keys.get(k, False))

        # Move player
        player.handle_input(mock_keys, 800)
        assert player.x == 405  # 400 + 5

    def test_player_screen_boundaries(self):
        """Test player stays within screen boundaries."""
        player = SkiPlayer(50, 300, "Danger")

        # Try to move past left boundary
        keys = {
            pygame.K_LEFT: True,
            pygame.K_RIGHT: False,
            pygame.K_a: False,
            pygame.K_d: False,
        }

        # Mock pygame.key.get_pressed to return our dictionary
        mock_keys = Mock()
        mock_keys.__getitem__ = Mock(side_effect=lambda k: keys.get(k, False))

        # Move left multiple times
        for _ in range(20):
            player.handle_input(mock_keys, 800)

        assert player.x >= 32  # Should not go below minimum

        # Try to move past right boundary
        player.x = 750
        keys = {
            pygame.K_RIGHT: True,
            pygame.K_LEFT: False,
            pygame.K_a: False,
            pygame.K_d: False,
        }
        mock_keys = Mock()
        mock_keys.__getitem__ = Mock(side_effect=lambda k: keys.get(k, False))

        for _ in range(20):
            player.handle_input(mock_keys, 800)

        assert player.x <= 768  # Should not exceed maximum (800 - 32)

    def test_player_crash(self):
        """Test player crash mechanics."""
        player = SkiPlayer(400, 300, "Danger")

        # First crash should succeed
        assert player.crash()
        assert player.is_crashing
        assert player.crash_time == 0.5

        # Can't crash while already crashing
        assert not player.crash()

    def test_player_invincibility(self):
        """Test player invincibility after crash."""
        player = SkiPlayer(400, 300, "Danger")

        # Crash and update to finish crash animation
        player.crash()
        player.update(0.6)  # More than crash time

        # Should now be invincible
        assert not player.is_crashing
        assert player.invincible
        assert 1.0 <= player.invincible_time <= 2.0  # Time should be close to 2.0

        # Can't crash while invincible
        assert not player.crash()

        # Update past invincibility time
        player.update(2.1)
        assert not player.invincible

        # Should be able to crash again
        assert player.crash()

    def test_player_movement_blocked_when_crashing(self):
        """Test player can't move while crashing."""
        player = SkiPlayer(400, 300, "Danger")

        # Crash the player
        player.crash()

        # Try to move
        keys = {
            pygame.K_LEFT: True,
            pygame.K_RIGHT: False,
            pygame.K_a: False,
            pygame.K_d: False,
        }
        mock_keys = Mock()
        mock_keys.__getitem__ = Mock(side_effect=lambda k: keys.get(k, False))

        initial_x = player.x
        player.handle_input(mock_keys, 800)

        # Position should not change
        assert player.x == initial_x


class TestSkiGame:
    """Test the SkiGame scene."""

    def test_game_initialization(self, ski_game):
        """Test ski game initializes correctly."""
        assert ski_game.state == SkiGame.STATE_READY
        assert ski_game.time_remaining == 60.0
        assert ski_game.game_duration == 60.0
        assert ski_game.start_time is None
        assert ski_game.player is not None
        assert ski_game.player.character_name == "Danger"
        assert ski_game.lives == 3
        assert ski_game.max_lives == 3

    def test_game_start(self, ski_game):
        """Test game transitions from ready to playing state."""
        # Simulate space key press in ready state
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_SPACE

        result = ski_game.handle_event(event)

        assert ski_game.state == SkiGame.STATE_PLAYING
        assert ski_game.start_time is not None
        assert result is None

    def test_escape_to_hub_from_ready(self, ski_game):
        """Test escape key returns to hub from ready state."""
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_ESCAPE

        result = ski_game.handle_event(event)

        assert result == SCENE_HUB_WORLD

    def test_escape_to_hub_from_playing(self, ski_game):
        """Test escape key returns to hub from playing state."""
        # Start the game first
        ski_game.start_game()

        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_ESCAPE

        result = ski_game.handle_event(event)

        assert result == SCENE_HUB_WORLD

    def test_game_timer_countdown(self, ski_game):
        """Test game timer counts down during play."""
        ski_game.start_game()
        initial_time = ski_game.time_remaining

        # Simulate some time passing
        time.sleep(0.1)
        ski_game.update(0.1)

        assert ski_game.time_remaining < initial_time
        assert ski_game.state == SkiGame.STATE_PLAYING

    def test_game_over_when_time_expires(self, ski_game):
        """Test game transitions to game over when time runs out."""
        ski_game.start_game()

        # Manually set time to expired
        ski_game.start_time = time.time() - 61  # Started 61 seconds ago
        ski_game.update(0.016)  # One frame update

        assert ski_game.state == SkiGame.STATE_GAME_OVER
        assert ski_game.time_remaining == 0

    def test_game_reset(self, ski_game):
        """Test game resets properly."""
        # Start and modify game state
        ski_game.start_game()
        ski_game.scroll_offset = 100
        ski_game.player.x = 200

        # Reset the game
        ski_game.reset_game()

        assert ski_game.state == SkiGame.STATE_READY
        assert ski_game.time_remaining == 60.0
        assert ski_game.scroll_offset == 0
        assert ski_game.player.x == ski_game.screen_width // 2

    def test_restart_from_game_over(self, ski_game):
        """Test space key restarts game from game over state."""
        ski_game.state = SkiGame.STATE_GAME_OVER

        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_SPACE

        result = ski_game.handle_event(event)

        assert ski_game.state == SkiGame.STATE_READY
        assert result is None

    def test_on_enter_resets_game(self, ski_game):
        """Test entering scene resets game state."""
        # Modify game state
        ski_game.state = SkiGame.STATE_PLAYING
        ski_game.scroll_offset = 100

        # Enter the scene
        ski_game.on_enter(SCENE_HUB_WORLD, {})

        assert ski_game.state == SkiGame.STATE_READY
        assert ski_game.scroll_offset == 0

    def test_scrolling_updates(self, ski_game):
        """Test slope scrolling updates during gameplay."""
        ski_game.start_game()
        initial_offset = ski_game.scroll_offset

        # Update for one frame
        ski_game.update(0.016)  # 60 FPS frame time

        assert ski_game.scroll_offset > initial_offset

    def test_player_update_during_gameplay(self, ski_game):
        """Test player is updated during gameplay."""
        ski_game.start_game()

        # Mock pygame key state - return a dict-like object
        mock_keys = Mock()
        mock_keys.__getitem__ = Mock(return_value=False)
        pygame.key.get_pressed = Mock(return_value=mock_keys)

        # Mock player update to track if it was called
        ski_game.player.update = Mock()

        ski_game.update(0.016)

        ski_game.player.update.assert_called_once()

    def test_collision_detection(self, ski_game):
        """Test collision detection with obstacles."""
        ski_game.start_game()

        # Create a mock obstacle
        mock_obstacle = Mock()
        mock_obstacle.rect = pygame.Rect(400, 300, 48, 48)

        # Mock the slope generator to return our obstacle
        ski_game.slope_generator.get_obstacles = Mock(return_value=[mock_obstacle])

        # Position player to collide
        ski_game.player.rect.center = (400, 300)

        # Mock the crash method
        ski_game.player.crash = Mock(return_value=True)

        # Check collisions
        ski_game.check_collisions()

        # Verify crash was called and life was lost
        ski_game.player.crash.assert_called_once()
        assert ski_game.lives == 2

    def test_game_over_on_lives_depleted(self, ski_game):
        """Test game ends when all lives are lost."""
        ski_game.start_game()

        # Create a mock obstacle
        mock_obstacle = Mock()
        mock_obstacle.rect = pygame.Rect(400, 300, 48, 48)
        ski_game.slope_generator.get_obstacles = Mock(return_value=[mock_obstacle])

        # Position player to collide
        ski_game.player.rect.center = (400, 300)

        # Mock crash to always succeed
        ski_game.player.crash = Mock(return_value=True)

        # Lose all lives
        for i in range(3):
            ski_game.check_collisions()
            ski_game.player.crash.reset_mock()

        assert ski_game.lives == 0
        assert ski_game.state == SkiGame.STATE_GAME_OVER

    def test_no_collision_when_invincible(self, ski_game):
        """Test player doesn't lose lives when invincible."""
        ski_game.start_game()

        # Create a mock obstacle
        mock_obstacle = Mock()
        mock_obstacle.rect = pygame.Rect(400, 300, 48, 48)
        ski_game.slope_generator.get_obstacles = Mock(return_value=[mock_obstacle])

        # Position player to collide
        ski_game.player.rect.center = (400, 300)

        # Mock crash to fail (player is invincible)
        ski_game.player.crash = Mock(return_value=False)

        initial_lives = ski_game.lives
        ski_game.check_collisions()

        # Lives should not change
        assert ski_game.lives == initial_lives
        ski_game.player.crash.assert_called_once()

    def test_reset_restores_lives(self, ski_game):
        """Test reset restores lives to full."""
        ski_game.start_game()
        ski_game.lives = 1  # Simulate lost lives

        ski_game.reset_game()

        assert ski_game.lives == ski_game.max_lives
        assert not ski_game.player.is_crashing
        assert not ski_game.player.invincible
