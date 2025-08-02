"""Unit tests for sprite_loader module.

Tests image loading functionality with proper mocking to avoid pygame display requirements.
"""

import os
from unittest.mock import Mock, patch

import pygame

# Set up headless environment for tests
os.environ["SDL_VIDEODRIVER"] = "dummy"

from src.config.constants import COLOR_PLACEHOLDER
from src.utils.sprite_loader import (
    load_character_animations,
    load_image,
    load_sprite_sheet,
)


class TestLoadImage:
    """Tests for the load_image function."""

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.image.load")
    def test_load_existing_image(self, mock_load, mock_exists):
        """load_image should load and return an image surface."""
        # Arrange
        mock_exists.return_value = True
        mock_surface = Mock()
        mock_surface.convert_alpha.return_value = mock_surface
        mock_load.return_value = mock_surface

        # Act
        result = load_image("test.png")

        # Assert
        mock_exists.assert_called_once_with("test.png")
        mock_load.assert_called_once_with("test.png")
        assert result == mock_surface

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.Surface")
    def test_load_missing_image_returns_placeholder(
        self, mock_surface_class, mock_exists
    ):
        """load_image should return placeholder surface for missing files."""
        # Arrange
        mock_exists.return_value = False
        mock_placeholder = Mock()
        mock_surface_class.return_value = mock_placeholder

        # Act
        result = load_image("missing.png")

        # Assert
        mock_surface_class.assert_called_once_with((64, 64))
        mock_placeholder.fill.assert_called_once_with(COLOR_PLACEHOLDER)
        assert result == mock_placeholder

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.image.load")
    @patch("src.utils.sprite_loader.pygame.transform.scale")
    def test_load_image_with_scale(self, mock_scale, mock_load, mock_exists):
        """load_image should scale image when scale parameter provided."""
        # Arrange
        mock_exists.return_value = True
        mock_surface = Mock()
        mock_surface.convert_alpha.return_value = mock_surface
        mock_load.return_value = mock_surface
        mock_scaled = Mock(spec=pygame.Surface)
        mock_scale.return_value = mock_scaled

        # Act
        result = load_image("test.png", scale=(100, 100))

        # Assert
        mock_scale.assert_called_once_with(mock_surface, (100, 100))
        assert result == mock_scaled

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.image.load")
    @patch("src.utils.sprite_loader.pygame.Surface")
    def test_load_image_handles_pygame_error(
        self, mock_surface_class, mock_load, mock_exists
    ):
        """load_image should return placeholder on pygame loading error."""
        # Arrange
        mock_exists.return_value = True
        mock_load.side_effect = pygame.error("Loading failed")
        mock_placeholder = Mock()
        mock_surface_class.return_value = mock_placeholder

        # Act
        result = load_image("corrupt.png")

        # Assert
        mock_placeholder.fill.assert_called_once_with(COLOR_PLACEHOLDER)
        assert result == mock_placeholder


class TestLoadSpriteSheet:
    """Tests for the load_sprite_sheet function."""

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.Surface")
    def test_load_missing_sprite_sheet_returns_placeholder(
        self, mock_surface_class, mock_exists
    ):
        """load_sprite_sheet should return placeholder for missing files."""
        # Arrange
        mock_exists.return_value = False
        mock_placeholder = Mock()
        mock_surface_class.return_value = mock_placeholder

        # Act
        result = load_sprite_sheet("missing.png", 64, 64)

        # Assert
        assert len(result) == 1
        assert result[0] == mock_placeholder
        mock_placeholder.fill.assert_called_once_with(COLOR_PLACEHOLDER)

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.image.load")
    @patch("src.utils.sprite_loader.pygame.Surface")
    @patch("src.utils.sprite_loader.pygame.transform.scale")
    def test_load_sprite_sheet_with_scale(
        self, mock_scale, mock_surface_class, mock_load, mock_exists
    ):
        """load_sprite_sheet should scale frames when scale parameter is provided."""
        # Arrange
        mock_exists.return_value = True

        # Mock the sprite sheet
        mock_sheet = Mock()
        mock_sheet.get_width.return_value = 128  # 2 frames wide
        mock_sheet.get_height.return_value = 64  # 1 frame tall
        mock_sheet.convert_alpha.return_value = mock_sheet
        mock_load.return_value = mock_sheet

        # Mock frame creation and scaling
        mock_frames = [Mock(), Mock()]
        mock_scaled_frames = [Mock(), Mock()]
        mock_surface_class.side_effect = mock_frames
        mock_scale.side_effect = mock_scaled_frames

        # Act
        result = load_sprite_sheet("sheet.png", 64, 64, scale=(32, 32))

        # Assert
        assert len(result) == 2
        assert all(frame in mock_scaled_frames for frame in result)
        assert mock_scale.call_count == 2

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.image.load")
    @patch("src.utils.sprite_loader.pygame.Surface")
    def test_load_sprite_sheet_extracts_frames(
        self, mock_surface_class, mock_load, mock_exists
    ):
        """load_sprite_sheet should extract frames from sheet."""
        # Arrange
        mock_exists.return_value = True

        # Mock the sprite sheet
        mock_sheet = Mock()
        mock_sheet.get_width.return_value = 128  # 2 frames wide
        mock_sheet.get_height.return_value = 128  # 2 frames tall
        mock_sheet.convert_alpha.return_value = mock_sheet
        mock_load.return_value = mock_sheet

        # Mock frame creation
        mock_frames = [Mock() for _ in range(4)]
        mock_surface_class.side_effect = mock_frames

        # Act
        result = load_sprite_sheet("sheet.png", 64, 64)

        # Assert
        assert len(result) == 4  # 2x2 grid = 4 frames
        assert all(frame in mock_frames for frame in result)

        # Verify blit was called for each frame position
        expected_positions = [(0, 0), (64, 0), (0, 64), (64, 64)]
        for i, (x, y) in enumerate(expected_positions):
            mock_frames[i].blit.assert_called_once_with(
                mock_sheet, (0, 0), (x, y, 64, 64)
            )

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.image.load")
    @patch("src.utils.sprite_loader.pygame.Surface")
    def test_load_sprite_sheet_handles_pygame_error(
        self, mock_surface_class, mock_load, mock_exists
    ):
        """load_sprite_sheet should return placeholder on loading error."""
        # Arrange
        mock_exists.return_value = True
        mock_load.side_effect = pygame.error("Loading failed")
        mock_placeholder = Mock()
        mock_surface_class.return_value = mock_placeholder

        # Act
        result = load_sprite_sheet("corrupt.png", 64, 64)

        # Assert
        assert len(result) == 1
        assert result[0] == mock_placeholder
        mock_placeholder.fill.assert_called_once_with(COLOR_PLACEHOLDER)


class TestLoadCharacterAnimations:
    """Tests for the load_character_animations function."""

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.Surface")
    def test_load_missing_animations_returns_placeholders(
        self, mock_surface_class, mock_exists
    ):
        """load_character_animations should return placeholder animations for missing files."""
        # Arrange
        mock_exists.return_value = False
        mock_placeholder = Mock()
        mock_surface_class.return_value = mock_placeholder

        # Act
        result = load_character_animations("missing.png")

        # Assert
        assert "walking" in result
        assert "jumping" in result
        assert "attacking" in result
        assert len(result["walking"]) == 4
        assert len(result["jumping"]) == 4
        assert len(result["attacking"]) == 3
        mock_placeholder.fill.assert_called_once_with(COLOR_PLACEHOLDER)

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.image.load")
    @patch("src.utils.sprite_loader.pygame.Surface")
    def test_load_character_animations_handles_pygame_error(
        self, mock_surface_class, mock_load, mock_exists
    ):
        """load_character_animations should handle pygame errors and return placeholders."""
        # Arrange
        mock_exists.return_value = True
        mock_load.side_effect = pygame.error("Failed to load")
        mock_placeholder = Mock()
        mock_surface_class.return_value = mock_placeholder

        # Act
        result = load_character_animations("corrupt.png", 128, 128)

        # Assert
        assert "walking" in result
        assert "jumping" in result
        assert "attacking" in result
        assert len(result["walking"]) == 4
        assert len(result["jumping"]) == 4
        assert len(result["attacking"]) == 3
        mock_placeholder.fill.assert_called_once_with(COLOR_PLACEHOLDER)

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.image.load")
    @patch("src.utils.sprite_loader.pygame.Surface")
    def test_load_character_animations_extracts_correct_frames(
        self, mock_surface_class, mock_load, mock_exists
    ):
        """load_character_animations should extract animations from correct rows."""
        # Arrange
        mock_exists.return_value = True

        # Mock the sprite sheet
        mock_sheet = Mock()
        mock_sheet.convert_alpha.return_value = mock_sheet
        mock_load.return_value = mock_sheet

        # Create enough mock frames for all animations
        mock_frames = [Mock() for _ in range(11)]  # 4 + 4 + 3
        mock_surface_class.side_effect = mock_frames

        # Act
        result = load_character_animations("character.png", 256, 256)

        # Assert
        assert len(result["walking"]) == 4
        assert len(result["jumping"]) == 4
        assert len(result["attacking"]) == 3

        # Verify walking frames (row 0)
        for i in range(4):
            x_pos = i * 256
            mock_frames[i].blit.assert_called_once_with(
                mock_sheet, (0, 0), (x_pos, 0, 256, 256)
            )

        # Verify jumping frames (row 1)
        for i in range(4):
            x_pos = i * 256
            mock_frames[4 + i].blit.assert_called_once_with(
                mock_sheet, (0, 0), (x_pos, 256, 256, 256)
            )

        # Verify attacking frames (row 2, only 3 frames)
        for i in range(3):
            x_pos = i * 256
            mock_frames[8 + i].blit.assert_called_once_with(
                mock_sheet, (0, 0), (x_pos, 512, 256, 256)
            )

    @patch("src.utils.sprite_loader.os.path.exists")
    @patch("src.utils.sprite_loader.pygame.image.load")
    @patch("src.utils.sprite_loader.pygame.Surface")
    @patch("src.utils.sprite_loader.pygame.transform.scale")
    def test_load_character_animations_with_scale(
        self, mock_scale, mock_surface_class, mock_load, mock_exists
    ):
        """load_character_animations should scale frames when scale parameter provided."""
        # Arrange
        mock_exists.return_value = True
        mock_sheet = Mock()
        mock_sheet.convert_alpha.return_value = mock_sheet
        mock_load.return_value = mock_sheet

        # Create mock frames and scaled versions
        mock_frames = [Mock() for _ in range(11)]
        mock_scaled_frames = [Mock() for _ in range(11)]
        mock_surface_class.side_effect = mock_frames
        mock_scale.side_effect = mock_scaled_frames

        # Act
        result = load_character_animations("character.png", scale=(128, 128))

        # Assert
        # All frames should be scaled
        assert mock_scale.call_count == 11

        # Results should contain scaled frames
        all_frames = result["walking"] + result["jumping"] + result["attacking"]
        assert all(frame in mock_scaled_frames for frame in all_frames)
