"""Unit tests for SceneManager class.

Tests focus on behavior verification with proper mocking and isolation.
Follows AAA (Arrange-Act-Assert) pattern for clarity.
"""

from unittest.mock import ANY, Mock, patch

import pygame
import pytest

from src.scene_manager import SceneManager

# Apply SoundManager mock to all tests
pytestmark = pytest.mark.usefixtures("mock_sound_manager")


class MockScene:
    """Mock scene for testing SceneManager interactions."""

    def __init__(self):
        self.handle_event = Mock(return_value=None)
        self.update = Mock()
        self.draw = Mock()
        self.selected_character = None

    def configure_transition(self, return_value: str, character: str = None):
        """Configure the mock to trigger a scene transition."""
        self.handle_event.return_value = return_value
        if character:
            self.selected_character = character


class TestSceneManagerInitialization:
    """Tests for SceneManager initialization."""

    def test_init_stores_screen_dimensions(self):
        """SceneManager should store the provided screen dimensions."""
        # Arrange
        width, height = 800, 600

        # Act
        manager = SceneManager(width, height)

        # Assert
        assert manager.screen_width == width
        assert manager.screen_height == height

    def test_init_creates_empty_scenes_dict(self):
        """SceneManager should initialize with a scenes dictionary containing title scene."""
        # Act
        manager = SceneManager(800, 600)

        # Assert
        assert isinstance(manager.scenes, dict)
        assert "title" in manager.scenes

    def test_init_sets_title_as_current_scene(self):
        """SceneManager should set title screen as the initial scene."""
        # Act
        manager = SceneManager(800, 600)

        # Assert
        assert manager.current_scene is not None
        assert manager.current_scene == manager.scenes["title"]

    @patch("src.scene_manager.SaveManager")
    def test_init_creates_game_data_with_no_character(self, mock_save_manager_class):
        """SceneManager should initialize game_data with no selected character."""
        # Arrange - Mock save manager to return no selected character
        mock_save_instance = Mock()
        save_data = {
            "settings": {"master_volume": 1.0, "music_volume": 1.0, "sfx_volume": 1.0},
            "player": {"selected_character": None},
            "high_scores": {},  # Add high_scores to prevent HighScoreManager from failing
        }
        mock_save_instance.load.return_value = save_data
        mock_save_instance._current_save_data = (
            save_data  # Set the internal data for HighScoreManager
        )
        mock_save_manager_class.return_value = mock_save_instance

        # Act
        manager = SceneManager(800, 600)

        # Assert
        assert manager.game_data == {"selected_character": None}


class TestSceneRegistrationAndSwitching:
    """Tests for scene registration and switching functionality."""

    def test_switch_to_existing_scene(self):
        """switch_scene should change current_scene when scene exists."""
        # Arrange
        manager = SceneManager(800, 600)
        mock_scene = MockScene()
        manager.scenes["test_scene"] = mock_scene

        # Act
        manager.switch_scene("test_scene")

        # Assert
        assert manager.current_scene == mock_scene

    def test_switch_to_nonexistent_scene_does_nothing(self):
        """switch_scene should not change current_scene for invalid scene name."""
        # Arrange
        manager = SceneManager(800, 600)
        original_scene = manager.current_scene

        # Act
        manager.switch_scene("nonexistent_scene")

        # Assert
        assert manager.current_scene == original_scene

    def test_can_register_new_scenes(self):
        """Should be able to add new scenes to the scenes dictionary."""
        # Arrange
        manager = SceneManager(800, 600)
        mock_scene = MockScene()

        # Act
        manager.scenes["new_scene"] = mock_scene
        manager.switch_scene("new_scene")

        # Assert
        assert "new_scene" in manager.scenes
        assert manager.current_scene == mock_scene


class TestEventHandling:
    """Tests for event handling and scene transitions."""

    def test_forwards_events_to_current_scene(self):
        """handle_event should forward events to the current scene."""
        # Arrange
        manager = SceneManager(800, 600)
        mock_scene = MockScene()
        manager.current_scene = mock_scene
        mock_event = Mock()

        # Act
        manager.handle_event(mock_event)

        # Assert
        mock_scene.handle_event.assert_called_once_with(mock_event)

    def test_handles_start_game_transition(self):
        """handle_event should save character selection on start_game result."""
        # Arrange
        manager = SceneManager(800, 600)
        mock_scene = MockScene()
        mock_scene.configure_transition("start_game", "Danger")
        manager.current_scene = mock_scene

        # Act
        manager.handle_event(Mock())

        # Assert
        assert manager.game_data["selected_character"] == "Danger"

    def test_no_error_when_no_current_scene(self):
        """handle_event should not error when current_scene is None."""
        # Arrange
        manager = SceneManager(800, 600)
        manager.current_scene = None

        # Act & Assert (no exception)
        manager.handle_event(Mock())

    def test_ignores_non_transition_results(self):
        """handle_event should ignore results that aren't scene transitions."""
        # Arrange
        manager = SceneManager(800, 600)
        mock_scene = MockScene()
        mock_scene.handle_event.return_value = "some_other_result"
        manager.current_scene = mock_scene
        original_character = manager.game_data["selected_character"]

        # Act
        manager.handle_event(Mock())

        # Assert
        assert manager.game_data["selected_character"] == original_character


class TestUpdateAndDraw:
    """Tests for update and draw delegation."""

    def test_update_delegates_to_current_scene(self):
        """update should call update on the current scene."""
        # Arrange
        manager = SceneManager(800, 600)
        mock_scene = MockScene()
        manager.current_scene = mock_scene

        # Act
        manager.update(0.016)  # 60 FPS delta time

        # Assert
        mock_scene.update.assert_called_once_with(0.016)

    def test_draw_delegates_to_current_scene(self):
        """draw should call draw on the current scene with the screen."""
        # Arrange
        manager = SceneManager(800, 600)
        mock_scene = MockScene()
        manager.current_scene = mock_scene
        mock_screen = Mock()

        # Act
        manager.draw(mock_screen)

        # Assert
        mock_scene.draw.assert_called_once_with(mock_screen)

    def test_update_handles_no_current_scene(self):
        """update should not error when current_scene is None."""
        # Arrange
        manager = SceneManager(800, 600)
        manager.current_scene = None

        # Act & Assert (no exception)
        manager.update(0.016)  # 60 FPS delta time

    def test_draw_handles_no_current_scene(self):
        """draw should not error when current_scene is None."""
        # Arrange
        manager = SceneManager(800, 600)
        manager.current_scene = None

        # Act & Assert (no exception)
        manager.draw(Mock())


class TestSceneManagerIntegration:
    """Integration tests for complete workflows."""

    @patch("src.scene_manager.TitleScreen")
    def test_title_screen_integration(self, mock_title_class):
        """Test complete title screen initialization and interaction."""
        # Arrange
        mock_title_instance = MockScene()
        mock_title_class.return_value = mock_title_instance

        # Act
        manager = SceneManager(1920, 1080)

        # Assert
        mock_title_class.assert_called_once_with(1920, 1080, ANY)
        assert manager.scenes["title"] == mock_title_instance
        assert manager.current_scene == mock_title_instance

    def test_complete_character_selection_flow(self):
        """Test the complete flow from initialization through character selection."""
        # Arrange
        manager = SceneManager(800, 600)
        mock_scene = MockScene()
        mock_scene.configure_transition("start_game", "Rose")
        manager.current_scene = mock_scene

        # Act
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        manager.handle_event(event)

        # Assert
        assert manager.game_data["selected_character"] == "Rose"
        mock_scene.handle_event.assert_called_once()
