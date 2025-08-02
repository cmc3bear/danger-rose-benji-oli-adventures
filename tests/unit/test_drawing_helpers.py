"""Unit tests for UI drawing helper functions."""

from unittest.mock import Mock, patch

from src.config.constants import (
    COLOR_BLACK,
    COLOR_RED,
    COLOR_WHITE,
    UI_HEART_SIZE,
    UI_TIMER_BORDER,
    UI_TIMER_PADDING,
)
from src.ui.drawing_helpers import (
    draw_heart,
    draw_instructions,
    draw_lives,
    draw_progress_bar,
    draw_text_with_background,
)


class TestDrawHeart:
    """Tests for the draw_heart function."""

    @patch("pygame.draw.circle")
    @patch("pygame.draw.polygon")
    def test_draw_filled_heart(self, mock_polygon, mock_circle):
        """Test drawing a filled heart."""
        # Arrange
        screen = Mock()
        x, y = 100, 50

        # Act
        draw_heart(screen, x, y)

        # Assert
        # Should draw two circles and a polygon for filled heart
        assert mock_circle.call_count == 2
        assert mock_polygon.call_count == 1

        # Check circle positions
        circle_calls = mock_circle.call_args_list
        assert circle_calls[0][0][1] == COLOR_RED  # Color
        assert circle_calls[0][0][2] == (x + UI_HEART_SIZE // 4, y + UI_HEART_SIZE // 4)
        assert circle_calls[1][0][2] == (
            x + 3 * UI_HEART_SIZE // 4,
            y + UI_HEART_SIZE // 4,
        )

    @patch("pygame.draw.circle")
    @patch("pygame.draw.lines")
    def test_draw_outline_heart(self, mock_lines, mock_circle):
        """Test drawing an outline heart."""
        # Arrange
        screen = Mock()
        x, y = 100, 50

        # Act
        draw_heart(screen, x, y, filled=False)

        # Assert
        # Should draw two circle outlines and lines
        assert mock_circle.call_count == 2
        assert mock_lines.call_count == 1

        # Check that circles have width parameter (outline)
        circle_calls = mock_circle.call_args_list
        assert circle_calls[0][0][4] == 2  # Width parameter


class TestDrawLives:
    """Tests for the draw_lives function."""

    @patch("src.ui.drawing_helpers.draw_heart")
    def test_draw_lives_with_full_health(self, mock_draw_heart):
        """Test drawing lives when all hearts are filled."""
        # Arrange
        screen = Mock()
        screen.get_width.return_value = 800
        current_lives = 3
        max_lives = 3

        # Act
        draw_lives(screen, current_lives, max_lives)

        # Assert
        assert mock_draw_heart.call_count == 3
        # All hearts should be filled
        for i in range(3):
            call_args = mock_draw_heart.call_args_list[i]
            assert call_args[0][3] == UI_HEART_SIZE
            assert call_args[0][4] is True  # filled
            assert call_args[0][5] == COLOR_RED

    @patch("src.ui.drawing_helpers.draw_heart")
    def test_draw_lives_with_partial_health(self, mock_draw_heart):
        """Test drawing lives when some hearts are empty."""
        # Arrange
        screen = Mock()
        screen.get_width.return_value = 800
        current_lives = 1
        max_lives = 3

        # Act
        draw_lives(screen, current_lives, max_lives)

        # Assert
        assert mock_draw_heart.call_count == 3
        # First heart should be filled
        assert mock_draw_heart.call_args_list[0][0][4] is True
        assert mock_draw_heart.call_args_list[0][0][5] == COLOR_RED
        # Last two should be outlines
        assert mock_draw_heart.call_args_list[1][0][4] is False
        assert mock_draw_heart.call_args_list[1][0][5] == COLOR_BLACK
        assert mock_draw_heart.call_args_list[2][0][4] is False


class TestDrawTextWithBackground:
    """Tests for the draw_text_with_background function."""

    @patch("pygame.draw.rect")
    def test_draw_text_with_background_centered(self, mock_rect):
        """Test drawing text with background centered at position."""
        # Arrange
        screen = Mock()
        font = Mock()
        text_surface = Mock()
        text_rect = Mock()
        bg_rect = Mock()

        font.render.return_value = text_surface
        text_surface.get_rect.return_value = text_rect
        text_rect.inflate.return_value = bg_rect

        # Act
        result = draw_text_with_background(screen, "Test Text", font, (400, 300))

        # Assert
        font.render.assert_called_once_with("Test Text", True, COLOR_BLACK)
        text_surface.get_rect.assert_called_once_with(center=(400, 300))
        text_rect.inflate.assert_called_once_with(UI_TIMER_PADDING, UI_TIMER_BORDER)

        # Check drawing calls
        assert mock_rect.call_count == 2  # Background and border
        screen.blit.assert_called_once_with(text_surface, text_rect)
        assert result == bg_rect


class TestDrawProgressBar:
    """Tests for the draw_progress_bar function."""

    @patch("pygame.draw.rect")
    def test_draw_progress_bar_half_full(self, mock_rect):
        """Test drawing a progress bar at 50% progress."""
        # Arrange
        screen = Mock()
        x, y, width, height = 100, 200, 200, 20
        progress = 0.5

        # Act
        draw_progress_bar(screen, x, y, width, height, progress)

        # Assert
        # Should draw background, fill and border
        assert mock_rect.call_count == 3

        # Check background rect
        bg_call = mock_rect.call_args_list[0]
        assert bg_call[0][0] == screen  # screen
        assert bg_call[0][1] == COLOR_BLACK  # background color
        assert bg_call[0][2] == (x, y, width, height)

        # Check fill rect
        fill_call = mock_rect.call_args_list[1]
        assert fill_call[0][0] == screen  # screen
        assert fill_call[0][1] == COLOR_RED  # fill color
        assert fill_call[0][2] == (x, y, 100, height)  # 50% of width

        # Check border
        border_call = mock_rect.call_args_list[2]
        assert border_call[0][2] == (x, y, width, height)
        assert border_call[0][3] == 2  # border width

    @patch("pygame.draw.rect")
    def test_draw_progress_bar_clamps_values(self, mock_rect):
        """Test that progress values are clamped to 0-1 range."""
        # Arrange
        screen = Mock()

        # Act - Test with progress > 1
        draw_progress_bar(screen, 0, 0, 100, 20, 1.5)

        # Assert - Should draw full width
        fill_call = mock_rect.call_args_list[1]  # Second call is the fill
        assert fill_call[0][2][2] == 100  # Full width

        # Reset
        mock_rect.reset_mock()

        # Act - Test with negative progress
        draw_progress_bar(screen, 0, 0, 100, 20, -0.5)

        # Assert - Should draw background and border (no fill)
        assert mock_rect.call_count == 2  # Background and border


class TestDrawInstructions:
    """Tests for the draw_instructions function."""

    def test_draw_instructions_centered(self):
        """Test drawing centered instruction text."""
        # Arrange
        screen = Mock()
        font = Mock()
        instructions = ["Press SPACE to start", "Press ESC to quit"]
        text_surfaces = [Mock(), Mock()]
        text_rects = [Mock(), Mock()]

        font.render.side_effect = text_surfaces
        for i, surface in enumerate(text_surfaces):
            surface.get_rect.return_value = text_rects[i]

        # Act
        draw_instructions(screen, instructions, font, 400, 300, 40)

        # Assert
        assert font.render.call_count == 2
        font.render.assert_any_call("Press SPACE to start", True, COLOR_BLACK)
        font.render.assert_any_call("Press ESC to quit", True, COLOR_BLACK)

        # Check positioning
        text_surfaces[0].get_rect.assert_called_with(center=(400, 300))
        text_surfaces[1].get_rect.assert_called_with(center=(400, 340))

        assert screen.blit.call_count == 2

    def test_draw_instructions_left_aligned(self):
        """Test drawing left-aligned instruction text."""
        # Arrange
        screen = Mock()
        font = Mock()
        instructions = ["Option 1", "Option 2"]
        text_surfaces = [Mock(), Mock()]
        text_rects = [Mock(), Mock()]

        font.render.side_effect = text_surfaces
        for i, surface in enumerate(text_surfaces):
            surface.get_rect.return_value = text_rects[i]

        # Act
        draw_instructions(
            screen, instructions, font, 50, 100, 30, COLOR_WHITE, center=False
        )

        # Assert
        # Check left alignment
        text_surfaces[0].get_rect.assert_called_with(topleft=(50, 100))
        text_surfaces[1].get_rect.assert_called_with(topleft=(50, 130))
