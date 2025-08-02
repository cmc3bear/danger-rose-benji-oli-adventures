from unittest.mock import Mock, patch

import pygame
import pytest

from src.config.constants import (
    SCENE_HUB_WORLD,
    SCENE_PAUSE,
    SCENE_SETTINGS,
    SCENE_SKI_GAME,
    SCENE_TITLE,
)
from src.scene_manager import SceneManager


class TestSceneManagerPause:
    """Test the pause functionality in SceneManager."""

    @pytest.fixture
    @patch("src.scene_manager.SoundManager")
    @patch("src.scene_manager.SaveManager")
    def scene_manager(self, mock_save_manager, mock_sound_manager):
        """Create a scene manager instance for testing."""
        # Mock the save manager load method
        mock_save_instance = Mock()
        save_data = {
            "settings": {
                "master_volume": 0.8,
                "music_volume": 0.7,
                "sfx_volume": 0.6,
            },
            "player": {"selected_character": "Danger"},
            "high_scores": {},  # Add high_scores to prevent HighScoreManager from failing
        }
        mock_save_instance.load.return_value = save_data
        mock_save_instance._current_save_data = (
            save_data  # Set the internal data for HighScoreManager
        )
        mock_save_manager.return_value = mock_save_instance

        # Create scene manager
        with patch("pygame.display.get_surface", return_value=Mock()):
            manager = SceneManager(800, 600)

        return manager

    def test_esc_key_triggers_pause_in_allowed_scenes(self, scene_manager):
        """Test ESC key pauses the game in allowed scenes."""
        # Switch to hub world
        scene_manager.switch_scene(SCENE_HUB_WORLD)
        scene_manager.paused = False

        # Create ESC key event
        event = Mock(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)

        # Handle event
        scene_manager.handle_event(event)

        # Should be paused
        assert scene_manager.paused is True
        assert scene_manager.paused_scene_name == SCENE_HUB_WORLD
        assert scene_manager.current_scene == scene_manager.scenes[SCENE_PAUSE]

    def test_esc_key_ignored_in_non_pauseable_scenes(self, scene_manager):
        """Test ESC key doesn't pause in title or settings."""
        # Start at title screen (default)
        assert scene_manager._get_current_scene_name() == SCENE_TITLE

        # Create ESC key event
        event = Mock(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)

        # Handle event
        scene_manager.handle_event(event)

        # Should not be paused
        assert scene_manager.paused is False
        assert scene_manager.current_scene == scene_manager.scenes[SCENE_TITLE]

    def test_pause_game_method(self, scene_manager):
        """Test pause_game method functionality."""
        # Switch to a pauseable scene
        scene_manager.switch_scene(SCENE_SKI_GAME)

        # Mock pygame display
        mock_screen = Mock()
        mock_screen.copy.return_value = Mock()  # Mock surface copy

        with patch("pygame.display.get_surface", return_value=mock_screen):
            scene_manager.pause_game()

        assert scene_manager.paused is True
        assert scene_manager.paused_scene_name == SCENE_SKI_GAME
        assert scene_manager.current_scene == scene_manager.scenes[SCENE_PAUSE]

        # Verify pause menu was set up with paused scene
        pause_menu = scene_manager.scenes[SCENE_PAUSE]
        assert pause_menu.paused_scene is not None

    def test_resume_game_method(self, scene_manager):
        """Test resume_game method functionality."""
        # First pause from ski game
        scene_manager.switch_scene(SCENE_SKI_GAME)
        scene_manager.paused = True
        scene_manager.paused_scene_name = SCENE_SKI_GAME
        scene_manager.current_scene = scene_manager.scenes[SCENE_PAUSE]

        # Resume
        scene_manager.resume_game()

        assert scene_manager.paused is False
        assert scene_manager.paused_scene_name is None
        assert scene_manager.current_scene == scene_manager.scenes[SCENE_SKI_GAME]

    def test_resume_from_pause_menu(self, scene_manager):
        """Test resuming from pause menu via handle_event."""
        # Pause the game
        scene_manager.switch_scene(SCENE_HUB_WORLD)
        scene_manager.paused = True
        scene_manager.paused_scene_name = SCENE_HUB_WORLD
        scene_manager.current_scene = scene_manager.scenes[SCENE_PAUSE]

        # Mock pause menu returning "resume"
        scene_manager.scenes[SCENE_PAUSE].handle_event = Mock(return_value="resume")

        # Handle any event
        event = Mock()
        scene_manager.handle_event(event)

        # Should be resumed
        assert scene_manager.paused is False
        assert scene_manager.current_scene == scene_manager.scenes[SCENE_HUB_WORLD]

    def test_quit_from_pause_menu(self, scene_manager):
        """Test quit action from pause menu."""
        # Pause the game
        scene_manager.paused = True
        scene_manager.current_scene = scene_manager.scenes[SCENE_PAUSE]

        # Mock pause menu returning "quit"
        scene_manager.scenes[SCENE_PAUSE].handle_event = Mock(return_value="quit")

        # Mock pygame.event.post
        with patch("pygame.event.post") as mock_post:
            scene_manager.handle_event(Mock())

            # Should post a quit event
            mock_post.assert_called_once()
            quit_event = mock_post.call_args[0][0]
            assert quit_event.type == pygame.QUIT

    def test_main_menu_from_pause(self, scene_manager):
        """Test returning to main menu from pause."""
        # Pause from hub world
        scene_manager.switch_scene(SCENE_HUB_WORLD)
        scene_manager.paused = True
        scene_manager.paused_scene_name = SCENE_HUB_WORLD
        scene_manager.current_scene = scene_manager.scenes[SCENE_PAUSE]

        # Mock pause menu returning title scene
        scene_manager.scenes[SCENE_PAUSE].handle_event = Mock(return_value=SCENE_TITLE)

        # Handle event
        scene_manager.handle_event(Mock())

        # Should be at title, not paused
        assert scene_manager.paused is False
        assert scene_manager.current_scene == scene_manager.scenes[SCENE_TITLE]

    def test_settings_from_pause_menu(self, scene_manager):
        """Test opening settings from pause menu."""
        # Pause from ski game
        scene_manager.switch_scene(SCENE_SKI_GAME)
        scene_manager.paused = True
        scene_manager.paused_scene_name = SCENE_SKI_GAME
        scene_manager.current_scene = scene_manager.scenes[SCENE_PAUSE]

        # Mock pause menu returning settings
        scene_manager.scenes[SCENE_PAUSE].handle_event = Mock(
            return_value=SCENE_SETTINGS
        )

        # Handle event
        scene_manager.handle_event(Mock())

        # Should be at settings, with paused scene stored
        assert scene_manager.current_scene == scene_manager.scenes[SCENE_SETTINGS]
        assert scene_manager.scenes[SCENE_SETTINGS].paused_scene == SCENE_SKI_GAME

    def test_update_only_updates_pause_menu_when_paused(self, scene_manager):
        """Test that only pause menu updates when paused."""
        # Set up mocks
        ski_scene = scene_manager.scenes[SCENE_SKI_GAME]
        pause_scene = scene_manager.scenes[SCENE_PAUSE]
        ski_scene.update = Mock()
        pause_scene.update = Mock()

        # Update while playing ski game
        scene_manager.switch_scene(SCENE_SKI_GAME)
        scene_manager.paused = False
        scene_manager.update(0.016)

        ski_scene.update.assert_called_once_with(0.016)
        pause_scene.update.assert_not_called()

        # Reset mocks
        ski_scene.update.reset_mock()
        pause_scene.update.reset_mock()

        # Update while paused
        scene_manager.paused = True
        scene_manager.current_scene = pause_scene
        scene_manager.update(0.016)

        ski_scene.update.assert_not_called()
        pause_scene.update.assert_called_once_with(0.016)

    def test_cannot_pause_while_already_paused(self, scene_manager):
        """Test that pause_game does nothing if already paused."""
        # Already paused
        scene_manager.paused = True
        original_scene = scene_manager.current_scene

        # Try to pause again
        scene_manager.pause_game()

        # Nothing should change
        assert scene_manager.paused is True
        assert scene_manager.current_scene == original_scene
