"""Tests for the Player entity."""

from unittest.mock import Mock, patch

import pygame

from src.config.constants import PLAYER_SPEED, SPRITE_DISPLAY_SIZE
from src.entities.player import Player


class TestPlayerInitialization:
    """Test Player initialization."""

    @patch("src.entities.player.AnimatedCharacter")
    def test_player_init_basic(self, mock_animated_character):
        """Player should initialize with correct default values."""
        # Arrange
        mock_animated_character.return_value = Mock()

        # Act
        player = Player(x=100, y=200, character_name="danger")

        # Assert
        assert player.x == 100
        assert player.y == 200
        assert player.vx == 0.0
        assert player.vy == 0.0
        assert player.move_left is False
        assert player.move_right is False
        assert player.move_up is False
        assert player.move_down is False
        assert player.facing_right is True

    @patch("src.entities.player.AnimatedCharacter")
    def test_player_init_with_character(self, mock_animated_character):
        """Player should create AnimatedCharacter with correct parameters."""
        # Arrange
        mock_sprite = Mock()
        mock_animated_character.return_value = mock_sprite

        # Act
        Player(x=0, y=0, character_name="rose")

        # Assert
        mock_animated_character.assert_called_once_with(
            "rose", "hub", scale=(SPRITE_DISPLAY_SIZE, SPRITE_DISPLAY_SIZE)
        )


class TestPlayerMovement:
    """Test player movement mechanics."""

    @patch("src.entities.player.AnimatedCharacter")
    def test_handle_movement_keys(self, mock_animated_character):
        """Player should respond to movement key events."""
        # Arrange
        mock_animated_character.return_value = Mock()
        player = Player(100, 100, "danger")

        # Test left key press
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT})
        player.handle_event(event)
        assert player.move_left is True

        # Test right key press
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_d})
        player.handle_event(event)
        assert player.move_right is True

        # Test key release
        event = pygame.event.Event(pygame.KEYUP, {"key": pygame.K_LEFT})
        player.handle_event(event)
        assert player.move_left is False

    @patch("src.entities.player.AnimatedCharacter")
    def test_update_movement(self, mock_animated_character):
        """Player should update position based on movement flags."""
        # Arrange
        mock_sprite = Mock()
        mock_animated_character.return_value = mock_sprite
        player = Player(100, 100, "danger")
        player.move_right = True

        # Act
        player.update(1.0, [])  # 1 second, no boundaries

        # Assert
        assert player.vx == PLAYER_SPEED
        assert player.x > 100  # Moved right
        assert player.facing_right is True
        mock_sprite.update.assert_called()

    @patch("src.entities.player.AnimatedCharacter")
    def test_boundary_collision(self, mock_animated_character):
        """Player should stop at boundaries."""
        # Arrange
        mock_animated_character.return_value = Mock()
        player = Player(100, 100, "danger")
        player.move_right = True

        # Create boundary that blocks movement
        boundary = pygame.Rect(150, 50, 50, 200)

        # Act
        player.update(0.1, [boundary])

        # Assert
        # Player should be stopped by boundary
        assert player.x < 150  # Can't move past boundary


class TestPlayerRendering:
    """Test player rendering."""

    @patch("src.entities.player.AnimatedCharacter")
    def test_draw_player(self, mock_animated_character):
        """Player should draw sprite at correct position."""
        # Arrange
        mock_sprite_manager = Mock()
        mock_surface = Mock()
        mock_surface.get_rect.return_value = Mock(center=(200, 300))
        mock_sprite_manager.get_current_sprite.return_value = mock_surface
        mock_animated_character.return_value = mock_sprite_manager
        player = Player(200, 300, "danger")
        mock_screen = Mock()

        # Act
        player.draw(mock_screen)

        # Assert
        mock_sprite_manager.get_current_sprite.assert_called_once()
        mock_screen.blit.assert_called_once()

    @patch("src.entities.player.AnimatedCharacter")
    def test_rect_updates_with_position(self, mock_animated_character):
        """Player rect should update when position changes."""
        # Arrange
        mock_animated_character.return_value = Mock()
        player = Player(100, 100, "danger")
        player.rect.copy()

        # Act
        player.x = 200
        player.y = 150
        player.update(0.016, [])

        # Assert
        assert player.rect.centerx == 200
        assert player.rect.centery == 150
