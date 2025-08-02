"""Tests for the Door entity."""

from unittest.mock import Mock, patch

import pygame

from src.config.constants import COLOR_BLUE, COLOR_GREEN, COLOR_WHITE
from src.entities.door import Door


class TestDoorInitialization:
    """Test Door initialization."""

    def test_door_init_default(self):
        """Door should initialize with default values."""
        # Act
        door = Door(
            x=100, y=200, width=80, height=120, target_scene="hub", label="Hub World"
        )

        # Assert
        assert door.rect.x == 100
        assert door.rect.y == 200
        assert door.rect.width == 80
        assert door.rect.height == 120
        assert door.target_scene == "hub"
        assert door.label == "Hub World"
        assert door.color == COLOR_BLUE
        assert door.highlight_color == COLOR_GREEN
        assert door.is_highlighted is False

    def test_door_init_custom_color(self):
        """Door should initialize with custom color."""
        # Arrange
        custom_color = (255, 0, 0)  # Red

        # Act
        door = Door(
            x=50,
            y=100,
            width=60,
            height=80,
            target_scene="secret",
            label="Secret Room",
            color=custom_color,
        )

        # Assert
        assert door.color == custom_color

    def test_door_interaction_rect_is_larger(self):
        """Door interaction rect should be larger than visual rect."""
        # Act
        door = Door(
            x=100, y=100, width=80, height=120, target_scene="test", label="Test"
        )

        # Assert
        assert door.interaction_rect.width > door.rect.width
        assert door.interaction_rect.height > door.rect.height
        assert door.interaction_rect.center == door.rect.center


class TestDoorInteraction:
    """Test door interaction mechanics."""

    def test_check_player_proximity_when_close(self):
        """check_player_proximity should return True when player is close."""
        # Arrange
        door = Door(
            x=100, y=100, width=80, height=120, target_scene="level1", label="Level 1"
        )
        # Player rect overlapping with interaction zone
        player_rect = pygame.Rect(110, 110, 32, 48)

        # Act
        result = door.check_player_proximity(player_rect)

        # Assert
        assert result is True

    def test_check_player_proximity_when_far(self):
        """check_player_proximity should return False when player is far."""
        # Arrange
        door = Door(
            x=100, y=100, width=80, height=120, target_scene="level1", label="Level 1"
        )
        # Player rect far from door
        player_rect = pygame.Rect(300, 300, 32, 48)

        # Act
        result = door.check_player_proximity(player_rect)

        # Assert
        assert result is False

    def test_check_player_proximity_edge_of_interaction(self):
        """check_player_proximity should work at edge of interaction zone."""
        # Arrange
        door = Door(
            x=100, y=100, width=80, height=120, target_scene="level1", label="Level 1"
        )
        # Player rect just touching interaction zone (20px padding)
        player_rect = pygame.Rect(75, 100, 32, 48)  # Just inside left edge

        # Act
        result = door.check_player_proximity(player_rect)

        # Assert
        assert result is True


class TestDoorRendering:
    """Test door rendering."""

    @patch("pygame.Surface")
    @patch("pygame.draw.rect")
    @patch("pygame.font.Font")
    def test_draw_renders_door(
        self, mock_font_class, mock_draw_rect, mock_surface_class
    ):
        """Draw should render door with correct elements."""
        # Arrange
        door = Door(
            x=150, y=250, width=80, height=120, target_scene="hub", label="Hub World"
        )
        mock_screen = Mock()
        mock_font = Mock()
        mock_label_surface = Mock()
        mock_font.render.return_value = mock_label_surface
        mock_label_surface.get_rect.return_value = Mock(center=(190, 310))

        # Mock the semi-transparent surface
        mock_alpha_surface = Mock()
        mock_surface_class.return_value = mock_alpha_surface

        # Act
        door.draw(mock_screen, mock_font)

        # Assert
        # Should draw door rectangle
        mock_draw_rect.assert_called()
        # Should render label
        mock_font.render.assert_called_with("Hub World", True, COLOR_WHITE)
        # Should blit label
        mock_screen.blit.assert_any_call(
            mock_label_surface, mock_label_surface.get_rect()
        )

    @patch("pygame.Surface")
    @patch("pygame.draw.rect")
    @patch("pygame.font.Font")
    def test_draw_highlighted_door(
        self, mock_font_class, mock_draw_rect, mock_surface_class
    ):
        """Draw should show highlight and hint when door is highlighted."""
        # Arrange
        door = Door(x=100, y=100, width=80, height=120, target_scene="hub", label="Hub")
        door.is_highlighted = True
        mock_screen = Mock()
        mock_font = Mock()

        # Mock render calls
        mock_label = Mock()
        mock_hint = Mock()
        mock_font.render.side_effect = [mock_label, mock_hint]
        mock_label.get_rect.return_value = Mock(center=(140, 160))
        mock_hint.get_rect.return_value = Mock(centerx=140, top=230)

        # Mock the semi-transparent surface
        mock_alpha_surface = Mock()
        mock_surface_class.return_value = mock_alpha_surface

        # Act
        door.draw(mock_screen, mock_font)

        # Assert
        # Should render hint text
        mock_font.render.assert_any_call("Press E to enter", True, COLOR_WHITE)
        # Should use highlight color
        assert mock_draw_rect.call_args_list[0][0][1] == COLOR_GREEN


class TestDoorUtilities:
    """Test door utility methods."""

    def test_highlight_state(self):
        """Door should track highlight state."""
        # Arrange
        door = Door(x=100, y=100, width=80, height=120, target_scene="hub", label="Hub")

        # Assert initial state
        assert door.is_highlighted is False

        # Act
        door.is_highlighted = True

        # Assert
        assert door.is_highlighted is True
