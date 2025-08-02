from unittest.mock import Mock, patch

import pygame
import pytest

from src.config.constants import SCENE_SETTINGS, SCENE_TITLE
from src.scenes.pause_menu import PauseMenu


class TestPauseMenu:
    """Test the PauseMenu functionality."""

    @pytest.fixture
    def pause_menu(self):
        """Create a pause menu instance for testing."""
        mock_sound = Mock()
        mock_sound.play_sfx = Mock()
        return PauseMenu(800, 600, mock_sound)

    def test_initialization(self, pause_menu):
        """Test pause menu initializes correctly."""
        assert pause_menu.screen_width == 800
        assert pause_menu.screen_height == 600
        assert pause_menu.paused_scene is None
        assert pause_menu.paused_surface is None
        assert len(pause_menu.buttons) == 4  # Resume, Settings, Main Menu, Quit

    def test_esc_key_resumes_game(self, pause_menu):
        """Test that pressing ESC resumes the game."""
        event = Mock(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = pause_menu.handle_event(event)

        assert result == "resume"
        pause_menu.sound_manager.play_sfx.assert_called_once()

    def test_resume_button_click(self, pause_menu):
        """Test clicking resume button."""
        # Get resume button position
        resume_button = pause_menu.buttons["resume"]["rect"]

        # Create mouse click event at button center
        event = Mock(
            type=pygame.MOUSEBUTTONDOWN,
            pos=(resume_button.centerx, resume_button.centery),
        )

        result = pause_menu.handle_event(event)
        assert result == "resume"
        pause_menu.sound_manager.play_sfx.assert_called_once()

    def test_settings_button_click(self, pause_menu):
        """Test clicking settings button."""
        settings_button = pause_menu.buttons["settings"]["rect"]

        event = Mock(
            type=pygame.MOUSEBUTTONDOWN,
            pos=(settings_button.centerx, settings_button.centery),
        )

        result = pause_menu.handle_event(event)
        assert result == SCENE_SETTINGS
        pause_menu.sound_manager.play_sfx.assert_called_once()

    def test_main_menu_button_click(self, pause_menu):
        """Test clicking main menu button."""
        main_menu_button = pause_menu.buttons["main_menu"]["rect"]

        event = Mock(
            type=pygame.MOUSEBUTTONDOWN,
            pos=(main_menu_button.centerx, main_menu_button.centery),
        )

        result = pause_menu.handle_event(event)
        assert result == SCENE_TITLE
        pause_menu.sound_manager.play_sfx.assert_called_once()

    def test_quit_button_click(self, pause_menu):
        """Test clicking quit button."""
        quit_button = pause_menu.buttons["quit"]["rect"]

        event = Mock(
            type=pygame.MOUSEBUTTONDOWN, pos=(quit_button.centerx, quit_button.centery)
        )

        result = pause_menu.handle_event(event)
        assert result == "quit"
        pause_menu.sound_manager.play_sfx.assert_called_once()

    def test_set_paused_scene(self, pause_menu):
        """Test setting the paused scene and surface."""
        mock_scene = Mock()
        mock_surface = Mock()

        pause_menu.set_paused_scene(mock_scene, mock_surface)

        assert pause_menu.paused_scene == mock_scene
        assert pause_menu.paused_surface is not None

    def test_on_enter_with_data(self, pause_menu):
        """Test on_enter method with paused scene data."""
        mock_scene = Mock()
        mock_surface = Mock()
        data = {"paused_scene": mock_scene, "paused_surface": mock_surface}

        pause_menu.on_enter(None, data)

        assert pause_menu.paused_scene == mock_scene
        assert pause_menu.paused_surface == mock_surface

    def test_on_exit(self, pause_menu):
        """Test on_exit returns proper data."""
        data = pause_menu.on_exit()
        assert data == {"resumed_from_pause": True}

    @patch("pygame.draw.rect")
    def test_draw_renders_overlay(self, mock_draw_rect, pause_menu):
        """Test draw method renders overlay and buttons."""
        mock_screen = Mock()
        mock_paused_surface = Mock()
        pause_menu.paused_surface = mock_paused_surface

        # Mock mouse position
        with patch("pygame.mouse.get_pos", return_value=(400, 300)):
            pause_menu.draw(mock_screen)

        # Should blit paused surface
        mock_screen.blit.assert_any_call(mock_paused_surface, (0, 0))

        # Should draw buttons (4 buttons, each with background and border)
        assert mock_draw_rect.call_count >= 8  # At least 4 buttons * 2 rects each

    def test_no_action_on_irrelevant_event(self, pause_menu):
        """Test that irrelevant events return None."""
        # Mouse motion event
        event = Mock(type=pygame.MOUSEMOTION)
        assert pause_menu.handle_event(event) is None

        # Key press that's not ESC
        event = Mock(type=pygame.KEYDOWN, key=pygame.K_SPACE)
        assert pause_menu.handle_event(event) is None

        # Mouse click outside buttons
        event = Mock(type=pygame.MOUSEBUTTONDOWN, pos=(0, 0))
        assert pause_menu.handle_event(event) is None
