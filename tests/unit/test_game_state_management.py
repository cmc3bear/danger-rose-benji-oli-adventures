"""Tests for game state management in SceneManager."""

from unittest.mock import Mock, patch

import pytest

from src.config.constants import (
    SCENE_HUB_WORLD,
    SCENE_POOL_GAME,
    SCENE_SKI_GAME,
    SCENE_VEGAS_GAME,
)
from src.scene_manager import SceneManager

pytestmark = pytest.mark.usefixtures("mock_sound_manager")


class TestGameStateManagement:
    """Test game state transitions and management."""

    def test_character_selection_persists_across_scenes(self):
        """Selected character should persist when switching scenes."""
        # Arrange
        manager = SceneManager(800, 600)
        manager.game_data["selected_character"] = "Danger"

        # Act
        manager.switch_scene(SCENE_HUB_WORLD)

        # Assert
        assert manager.game_data["selected_character"] == "Danger"

    def test_auto_save_triggers_on_gameplay_scene_transition(self):
        """Auto-save should trigger when leaving gameplay scenes."""
        # Arrange
        manager = SceneManager(800, 600)
        manager._auto_save = Mock()

        # Start in hub world
        manager.switch_scene(SCENE_HUB_WORLD)
        manager._auto_save.reset_mock()

        # Act - switch to ski game
        manager.switch_scene(SCENE_SKI_GAME)

        # Assert - auto-save should have been called
        manager._auto_save.assert_called_once()

    def test_no_auto_save_from_title_scene(self):
        """Auto-save should not trigger when leaving title scene."""
        # Arrange
        manager = SceneManager(800, 600)
        manager._auto_save = Mock()

        # Act - switch from title to hub
        manager.switch_scene(SCENE_HUB_WORLD)

        # Assert - auto-save should not have been called
        manager._auto_save.assert_not_called()

    def test_music_transitions_between_scenes(self):
        """Music should transition when switching scenes."""
        # Arrange
        manager = SceneManager(800, 600)

        # Act
        manager.switch_scene(SCENE_SKI_GAME)

        # Assert
        manager.sound_manager.crossfade_music.assert_called()
        args = manager.sound_manager.crossfade_music.call_args[0]
        assert "ski_theme.ogg" in args[0]

    def test_scene_on_enter_receives_previous_scene_data(self):
        """Scenes should receive data from previous scene on enter."""
        # Arrange
        manager = SceneManager(800, 600)
        mock_scene = Mock()
        mock_scene.on_enter = Mock()
        mock_scene.on_exit = Mock(return_value={"score": 100})

        # Mock the hub scene's on_enter method
        hub_scene = manager.scenes[SCENE_HUB_WORLD]
        hub_scene.on_enter = Mock()

        manager.scenes["test_scene"] = mock_scene
        manager.current_scene = mock_scene

        # Act
        manager.switch_scene(SCENE_HUB_WORLD)

        # Assert
        hub_scene.on_enter.assert_called_once_with("test_scene", {"score": 100})

    def test_save_game_manual_trigger(self):
        """Manual save should trigger auto-save."""
        # Arrange
        manager = SceneManager(800, 600)
        manager._auto_save = Mock()

        # Act
        manager.save_game()

        # Assert
        manager._auto_save.assert_called_once()

    def test_get_save_manager_returns_instance(self):
        """get_save_manager should return the save manager instance."""
        # Arrange
        manager = SceneManager(800, 600)

        # Act
        save_manager = manager.get_save_manager()

        # Assert
        assert save_manager is manager.save_manager

    def test_scene_transitions_from_event_handling(self):
        """Test all scene transition event results."""
        # Arrange
        manager = SceneManager(800, 600)
        mock_scene = Mock()
        manager.current_scene = mock_scene

        # Test each transition
        transitions = [
            ("vegas", SCENE_VEGAS_GAME),
            ("ski", SCENE_SKI_GAME),
            ("pool", SCENE_POOL_GAME),
            ("settings", "settings"),  # Direct scene name
        ]

        for event_result, expected_scene in transitions:
            # Reset
            manager.switch_scene = Mock()
            mock_scene.handle_event.return_value = event_result

            # Act
            manager.handle_event(Mock())

            # Assert
            manager.switch_scene.assert_called_once_with(expected_scene)


class TestSaveDataIntegration:
    """Test save data integration with game state."""

    @patch("src.scene_manager.SaveManager")
    def test_load_game_data_applies_settings(self, mock_save_manager_class):
        """Loading game data should apply saved settings."""
        # Arrange
        mock_save_instance = Mock()
        save_data = {
            "settings": {
                "master_volume": 0.5,
                "music_volume": 0.7,
                "sfx_volume": 0.3,
            },
            "player": {"selected_character": "Rose"},
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
        manager.sound_manager.set_master_volume.assert_called_with(0.5)
        manager.sound_manager.set_music_volume.assert_called_with(0.7)
        manager.sound_manager.set_sfx_volume.assert_called_with(0.3)
        assert manager.game_data["selected_character"] == "Rose"

    def test_auto_save_updates_character_selection(self):
        """Auto-save should update the selected character in save data."""
        # Arrange
        manager = SceneManager(800, 600)
        manager.game_data["selected_character"] = "Dad"
        manager.save_manager.set_selected_character = Mock()
        manager.save_manager.save = Mock(return_value=True)

        # Act
        manager._auto_save()

        # Assert
        manager.save_manager.set_selected_character.assert_called_with("Dad")
        manager.save_manager.save.assert_called_once()

    def test_auto_save_handles_errors_gracefully(self):
        """Auto-save should handle errors without crashing."""
        # Arrange
        manager = SceneManager(800, 600)
        manager.save_manager.save = Mock(side_effect=Exception("Save failed"))

        # Act - should not raise
        manager._auto_save()

        # Assert - save was attempted
        manager.save_manager.save.assert_called_once()
