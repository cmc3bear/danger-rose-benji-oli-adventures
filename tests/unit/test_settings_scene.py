"""Unit tests for SettingsScene class.

Tests focus on behavior verification with proper mocking and isolation.
Follows AAA (Arrange-Act-Assert) pattern for clarity.
"""

from unittest.mock import MagicMock, Mock, patch

import pygame
import pytest

from src.config.constants import SCENE_TITLE
from src.scenes.settings import SettingsScene


class TestSettingsSceneInitialization:
    """Tests for SettingsScene initialization."""

    def test_init_stores_screen_dimensions(self):
        """SettingsScene should store the provided screen dimensions."""
        # Arrange
        width, height = 1280, 720
        sound_manager = Mock()

        # Act
        scene = SettingsScene(width, height, sound_manager)

        # Assert
        assert scene.screen_width == width
        assert scene.screen_height == height

    def test_init_stores_sound_manager(self):
        """SettingsScene should store the sound manager reference."""
        # Arrange
        sound_manager = Mock()

        # Act
        scene = SettingsScene(1280, 720, sound_manager)

        # Assert
        assert scene.sound_manager == sound_manager

    def test_init_loads_config(self):
        """SettingsScene should load the game config on initialization."""
        # Arrange
        sound_manager = Mock()

        with patch("src.scenes.settings.get_config") as mock_get_config:
            mock_config = Mock()
            mock_get_config.return_value = mock_config

            # Act
            scene = SettingsScene(1280, 720, sound_manager)

            # Assert
            assert scene.config == mock_config
            mock_get_config.assert_called_once()

    def test_init_creates_ui_elements(self):
        """SettingsScene should create all UI elements on initialization."""
        # Arrange
        sound_manager = Mock()

        # Act
        scene = SettingsScene(1280, 720, sound_manager)

        # Assert
        assert hasattr(scene, "back_button")
        assert hasattr(scene, "master_volume_rect")
        assert hasattr(scene, "music_volume_rect")
        assert hasattr(scene, "sfx_volume_rect")
        assert hasattr(scene, "fullscreen_rect")
        assert hasattr(scene, "key_binding_rects")
        assert len(scene.key_binding_rects) == 6  # 6 key bindings


class TestSettingsSceneEvents:
    """Tests for SettingsScene event handling."""

    @pytest.fixture
    def scene(self):
        """Create a SettingsScene instance for testing."""
        sound_manager = Mock()
        with patch("src.scenes.settings.get_config"):
            return SettingsScene(1280, 720, sound_manager)

    def test_back_button_returns_to_title(self, scene):
        """Clicking back button should save settings and return to title."""
        # Arrange
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = scene.back_button.center
        scene.config.save = Mock()

        # Act
        result = scene.handle_event(event)

        # Assert
        scene.config.save.assert_called_once()
        assert result == SCENE_TITLE

    def test_back_button_returns_to_paused_scene(self, scene):
        """Clicking back button should return to paused scene if set."""
        # Arrange
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = scene.back_button.center
        scene.config.save = Mock()
        scene.paused_scene = "test_scene"

        # Act
        result = scene.handle_event(event)

        # Assert
        scene.config.save.assert_called_once()
        assert result == "test_scene"
        assert scene.paused_scene is None  # Should be reset

    def test_escape_key_returns_to_title(self, scene):
        """Pressing ESC should save settings and return to title."""
        # Arrange
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_ESCAPE
        scene.config.save = Mock()
        scene.waiting_for_key = False

        # Act
        result = scene.handle_event(event)

        # Assert
        scene.config.save.assert_called_once()
        assert result == SCENE_TITLE

    def test_fullscreen_toggle(self, scene):
        """Clicking fullscreen should toggle the setting."""
        # Arrange
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = scene.fullscreen_rect.center
        scene.config.fullscreen = False

        # Act
        scene.handle_event(event)

        # Assert
        assert scene.config.fullscreen is True

    def test_volume_slider_drag(self, scene):
        """Dragging volume sliders should update volume and apply immediately."""
        # Arrange
        click_event = Mock()
        click_event.type = pygame.MOUSEBUTTONDOWN
        click_event.pos = scene.master_volume_rect.center

        drag_event = Mock()
        drag_event.type = pygame.MOUSEMOTION
        drag_event.pos = (
            scene.master_volume_rect.x + scene.master_volume_rect.width // 2,
            scene.master_volume_rect.centery,
        )

        release_event = Mock()
        release_event.type = pygame.MOUSEBUTTONUP

        # Act
        scene.handle_event(click_event)
        assert scene.dragging_slider == "master"

        scene.handle_event(drag_event)

        scene.handle_event(release_event)

        # Assert
        assert scene.config.master_volume == pytest.approx(0.5, rel=0.1)
        scene.sound_manager.set_master_volume.assert_called_with(
            scene.config.master_volume
        )
        assert scene.dragging_slider is None

    def test_key_binding_rebind(self, scene):
        """Clicking key binding should allow rebinding."""
        # Arrange
        click_event = Mock()
        click_event.type = pygame.MOUSEBUTTONDOWN
        click_event.pos = scene.key_binding_rects["jump"].center

        key_event = Mock()
        key_event.type = pygame.KEYDOWN
        key_event.key = pygame.K_SPACE

        with patch("pygame.key.name", return_value="space"):
            # Act
            scene.handle_event(click_event)
            assert scene.waiting_for_key is True
            assert scene.rebinding_key == "jump"

            scene.handle_event(key_event)

            # Assert
            assert scene.waiting_for_key is False
            assert scene.rebinding_key is None
            scene.config.set.assert_called_with("controls.player1.jump", "space")

    def test_keyboard_navigation_tab(self, scene):
        """Tab key should navigate through focusable elements."""
        # Arrange
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_TAB
        scene.waiting_for_key = False
        initial_index = scene.focused_element_index

        with patch("pygame.key.get_mods", return_value=0):
            # Act
            scene.handle_event(event)

            # Assert
            assert scene.focused_element_index == (initial_index + 1) % len(
                scene.focusable_elements
            )

    def test_keyboard_navigation_arrow_keys_volume(self, scene):
        """Arrow keys should adjust volume when volume slider is focused."""
        # Arrange
        scene.focused_element_index = 0  # master_volume
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_RIGHT
        scene.waiting_for_key = False
        scene.config.master_volume = 0.5  # Set initial volume

        # Act
        scene.handle_event(event)

        # Assert
        assert scene.config.master_volume == pytest.approx(0.55, rel=0.01)
        scene.sound_manager.set_master_volume.assert_called_with(0.55)


class TestSettingsSceneDrawing:
    """Tests for SettingsScene drawing."""

    @pytest.fixture
    def scene(self):
        """Create a SettingsScene instance for testing."""
        sound_manager = Mock()
        with patch("src.scenes.settings.get_config"):
            return SettingsScene(1280, 720, sound_manager)

    @patch("pygame.draw.rect")
    @patch("pygame.font.Font")
    def test_draw_renders_all_elements(self, mock_font, mock_draw_rect, scene):
        """Draw should render all UI elements."""
        # Arrange
        screen = Mock()
        scene.config.fullscreen = True
        scene.config.master_volume = 0.5
        scene.config.music_volume = 0.7
        scene.config.sfx_volume = 0.3

        # Mock fonts
        mock_font_instance = MagicMock()
        mock_surface = Mock()
        mock_surface.get_rect.return_value = Mock(center=(640, 360))
        mock_font_instance.render.return_value = mock_surface
        mock_font.return_value = mock_font_instance

        # Mock config.get to return valid key bindings
        scene.config.get = Mock(
            side_effect=lambda path, default=None: "w" if "up" in path else default
        )

        # Act
        scene.draw(screen)

        # Assert
        # Check that screen.fill was called (clear screen)
        screen.fill.assert_called()

        # Check that various elements were drawn
        assert screen.blit.call_count > 0
        assert mock_draw_rect.call_count > 0


class TestSettingsSceneLifecycle:
    """Tests for SettingsScene lifecycle methods."""

    @pytest.fixture
    def scene(self):
        """Create a SettingsScene instance for testing."""
        sound_manager = Mock()
        with patch("src.scenes.settings.get_config"):
            return SettingsScene(1280, 720, sound_manager)

    def test_on_enter_reloads_config(self, scene):
        """on_enter should reload the config."""
        # Arrange
        with patch("src.scenes.settings.get_config") as mock_get_config:
            new_config = Mock()
            mock_get_config.return_value = new_config

            # Act
            scene.on_enter("previous_scene", {})

            # Assert
            assert scene.config == new_config
            mock_get_config.assert_called_once()

    def test_on_exit_saves_modified_config(self, scene):
        """on_exit should save config if modified."""
        # Arrange
        scene.config.is_modified.return_value = True
        scene.config.save = Mock()

        # Act
        data = scene.on_exit()

        # Assert
        scene.config.save.assert_called_once()
        assert data == {}

    def test_on_exit_no_save_if_not_modified(self, scene):
        """on_exit should not save config if not modified."""
        # Arrange
        scene.config.is_modified.return_value = False
        scene.config.save = Mock()

        # Act
        data = scene.on_exit()

        # Assert
        scene.config.save.assert_not_called()
        assert data == {}
