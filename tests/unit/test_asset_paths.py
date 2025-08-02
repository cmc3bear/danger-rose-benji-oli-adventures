"""Unit tests for asset_paths module.

Tests path construction utilities without file system dependencies.
"""

from pathlib import Path
from unittest.mock import patch

from src.utils.asset_paths import (
    get_asset_path,
    get_audio_path,
    get_character_sprite_path,
    get_danger_sprite,
    get_icon_path,
    get_image_path,
    get_living_room_bg,
    get_music_path,
    get_project_root,
    get_rose_sprite,
    get_sfx_path,
    get_tileset_path,
)


class TestProjectRoot:
    """Tests for get_project_root function."""

    @patch("src.utils.asset_paths.Path")
    def test_get_project_root_returns_correct_path(self, mock_path_class):
        """get_project_root should return path three levels up from module."""
        # Arrange
        mock_file_path = mock_path_class.return_value
        mock_resolve = mock_file_path.resolve.return_value
        mock_parent1 = mock_resolve.parent
        mock_parent2 = mock_parent1.parent
        mock_parent3 = mock_parent2.parent

        # Act
        result = get_project_root()

        # Assert
        assert result == mock_parent3
        mock_path_class.assert_called_once_with(asset_paths.__file__)
        mock_file_path.resolve.assert_called_once()


class TestAssetPaths:
    """Tests for general asset path functions."""

    @patch("src.utils.asset_paths.get_project_root")
    def test_get_asset_path_constructs_correct_path(self, mock_get_root):
        """get_asset_path should construct path relative to assets directory."""
        # Arrange
        mock_root = Path("/project/root")
        mock_get_root.return_value = mock_root

        # Act
        result = get_asset_path("test/file.png")

        # Assert
        expected = str(mock_root / "assets" / "test/file.png")
        assert result == expected

    @patch("src.utils.asset_paths.get_asset_path")
    def test_get_image_path_prepends_images_directory(self, mock_get_asset):
        """get_image_path should prepend 'images/' to relative path."""
        # Arrange
        mock_get_asset.return_value = "/project/assets/images/test.png"

        # Act
        result = get_image_path("test.png")

        # Assert
        mock_get_asset.assert_called_once_with("images/test.png")
        assert result == "/project/assets/images/test.png"

    @patch("src.utils.asset_paths.get_asset_path")
    def test_get_audio_path_prepends_audio_directory(self, mock_get_asset):
        """get_audio_path should prepend 'audio/' to relative path."""
        # Arrange
        mock_get_asset.return_value = "/project/assets/audio/test.ogg"

        # Act
        result = get_audio_path("test.ogg")

        # Assert
        mock_get_asset.assert_called_once_with("audio/test.ogg")
        assert result == "/project/assets/audio/test.ogg"


class TestSpecificAssetPaths:
    """Tests for specific asset type path functions."""

    @patch("src.utils.asset_paths.get_image_path")
    def test_get_character_sprite_path(self, mock_get_image):
        """get_character_sprite_path should construct path in characters directory."""
        # Arrange
        mock_get_image.return_value = "/project/assets/images/characters/hero.png"

        # Act
        result = get_character_sprite_path("hero")

        # Assert
        mock_get_image.assert_called_once_with("characters/hero.png")
        assert result == "/project/assets/images/characters/hero.png"

    @patch("src.utils.asset_paths.get_image_path")
    def test_get_tileset_path(self, mock_get_image):
        """get_tileset_path should construct path in tilesets directory."""
        # Arrange
        mock_get_image.return_value = "/project/assets/images/tilesets/grass.png"

        # Act
        result = get_tileset_path("grass.png")

        # Assert
        mock_get_image.assert_called_once_with("tilesets/grass.png")
        assert result == "/project/assets/images/tilesets/grass.png"

    @patch("src.utils.asset_paths.get_image_path")
    def test_get_icon_path(self, mock_get_image):
        """get_icon_path should construct path in icons directory."""
        # Arrange
        mock_get_image.return_value = "/project/assets/images/icons/heart.png"

        # Act
        result = get_icon_path("heart.png")

        # Assert
        mock_get_image.assert_called_once_with("icons/heart.png")
        assert result == "/project/assets/images/icons/heart.png"

    @patch("src.utils.asset_paths.get_audio_path")
    def test_get_music_path(self, mock_get_audio):
        """get_music_path should construct path in music directory."""
        # Arrange
        mock_get_audio.return_value = "/project/assets/audio/music/theme.ogg"

        # Act
        result = get_music_path("theme.ogg")

        # Assert
        mock_get_audio.assert_called_once_with("music/theme.ogg")
        assert result == "/project/assets/audio/music/theme.ogg"

    @patch("src.utils.asset_paths.get_audio_path")
    def test_get_sfx_path(self, mock_get_audio):
        """get_sfx_path should construct path in sfx directory."""
        # Arrange
        mock_get_audio.return_value = "/project/assets/audio/sfx/jump.wav"

        # Act
        result = get_sfx_path("jump.wav")

        # Assert
        mock_get_audio.assert_called_once_with("sfx/jump.wav")
        assert result == "/project/assets/audio/sfx/jump.wav"


class TestConvenienceFunctions:
    """Tests for convenience functions that get specific assets."""

    @patch("src.utils.asset_paths.get_tileset_path")
    def test_get_living_room_bg(self, mock_get_tileset):
        """get_living_room_bg should return path to living_room.png tileset."""
        # Arrange
        mock_get_tileset.return_value = (
            "/project/assets/images/tilesets/living_room.png"
        )

        # Act
        result = get_living_room_bg()

        # Assert
        mock_get_tileset.assert_called_once_with("living_room.png")
        assert result == "/project/assets/images/tilesets/living_room.png"

    @patch("src.utils.asset_paths.get_character_sprite_path")
    def test_get_danger_sprite(self, mock_get_character):
        """get_danger_sprite should return path to danger character sprite."""
        # Arrange
        mock_get_character.return_value = "/project/assets/images/characters/danger.png"

        # Act
        result = get_danger_sprite()

        # Assert
        mock_get_character.assert_called_once_with("danger")
        assert result == "/project/assets/images/characters/danger.png"

    @patch("src.utils.asset_paths.get_character_sprite_path")
    def test_get_rose_sprite(self, mock_get_character):
        """get_rose_sprite should return path to rose character sprite."""
        # Arrange
        mock_get_character.return_value = "/project/assets/images/characters/rose.png"

        # Act
        result = get_rose_sprite()

        # Assert
        mock_get_character.assert_called_once_with("rose")
        assert result == "/project/assets/images/characters/rose.png"


class TestPathConstructionIntegration:
    """Integration tests for path construction without mocking."""

    def test_paths_use_proper_separators(self):
        """All path functions should return paths with proper OS separators."""
        # This test verifies the actual implementation works correctly
        # without mocking, ensuring paths are constructed properly

        # Get a sample path
        project_root = get_project_root()

        # Verify it's a Path object and absolute
        assert isinstance(project_root, Path)
        assert project_root.is_absolute()

        # Test various path constructions
        asset_path = get_asset_path("test.txt")
        assert isinstance(asset_path, str)
        assert "assets" in asset_path
        assert "test.txt" in asset_path

        # Test nested paths
        sprite_path = get_character_sprite_path("player")
        assert isinstance(sprite_path, str)
        assert "characters" in sprite_path
        assert "player.png" in sprite_path


from src.utils import asset_paths  # noqa: E402
