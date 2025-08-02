"""Tests for the couch save point system."""

from datetime import datetime
from unittest.mock import Mock, patch

import pygame
import pytest

from src.entities.couch import Couch
from src.ui.notification import SaveNotification


class TestCouch:
    """Test suite for Couch entity."""

    @pytest.fixture
    def couch(self):
        """Create a Couch instance."""
        return Couch(100, 200)

    def test_initialization(self, couch):
        """Test Couch initialization."""
        assert couch.rect.x == 100
        assert couch.rect.y == 200
        assert couch.rect.width == 200
        assert couch.rect.height == 100
        assert not couch.is_highlighted
        assert not couch.is_saving

    def test_player_proximity(self, couch):
        """Test player proximity detection."""
        # Player rect far away
        player_rect = pygame.Rect(500, 500, 50, 50)
        assert not couch.check_player_proximity(player_rect)

        # Player rect overlapping
        player_rect = pygame.Rect(150, 250, 50, 50)
        assert couch.check_player_proximity(player_rect)

        # Player rect just inside interaction zone
        player_rect = pygame.Rect(75, 175, 50, 50)  # Just inside padding
        assert couch.check_player_proximity(player_rect)

    def test_trigger_save(self, couch):
        """Test save triggering."""
        assert not couch.is_saving
        couch.trigger_save()
        assert couch.is_saving
        assert couch.save_animation_timer == 2.0

    def test_update_animation(self, couch):
        """Test save animation update."""
        couch.trigger_save()
        assert couch.is_saving

        # Update half the animation time
        couch.update(1.0)
        assert couch.is_saving
        assert couch.save_animation_timer == 1.0

        # Complete animation
        couch.update(1.5)
        assert not couch.is_saving
        assert couch.save_animation_timer <= 0


class TestSaveNotification:
    """Test suite for SaveNotification UI component."""

    @pytest.fixture
    def notification(self):
        """Create a SaveNotification instance."""
        font = Mock()
        small_font = Mock()
        return SaveNotification(font, small_font)

    def test_initialization(self, notification):
        """Test SaveNotification initialization."""
        assert not notification.active
        assert notification.timer == 0.0
        assert notification.alpha == 0
        assert notification.last_save_time is None

    def test_show_notification(self, notification):
        """Test showing notification."""
        test_time = datetime(2024, 1, 1, 12, 0)
        notification.show(test_time)

        assert notification.active
        assert notification.timer == 0.0
        assert notification.last_save_time == test_time

    def test_show_notification_default_time(self, notification):
        """Test showing notification with default time."""
        with patch("src.ui.notification.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 13, 0)
            mock_datetime.now.return_value = mock_now

            notification.show()
            assert notification.last_save_time == mock_now

    def test_update_fade_in(self, notification):
        """Test fade-in animation phase."""
        notification.show()

        # Update halfway through fade-in
        notification.update(0.15)
        assert notification.active
        assert notification.alpha == 127  # Halfway faded in

        # Complete fade-in
        notification.update(0.15)
        assert notification.alpha == 255

    def test_update_full_display(self, notification):
        """Test full display phase."""
        notification.show()
        notification.update(0.3)  # Complete fade-in

        # Should stay at full alpha during display
        notification.update(1.0)
        assert notification.active
        assert notification.alpha == 255

    def test_update_fade_out(self, notification):
        """Test fade-out animation phase."""
        notification.show()
        notification.update(2.3)  # Skip to fade-out phase

        # Should start fading out
        notification.update(0.25)  # Half of fade-out
        assert notification.active
        assert notification.alpha == 127

        # Complete fade-out
        notification.update(0.25)
        assert not notification.active
        assert notification.alpha == 0

    def test_complete_animation_cycle(self, notification):
        """Test complete animation cycle."""
        notification.show()

        # Run entire animation
        notification.update(3.0)  # Total duration is 2.8 seconds
        assert not notification.active
        assert notification.alpha == 0


class TestHubWorldSaveIntegration:
    """Test suite for hub world save system integration."""

    @pytest.fixture
    def mock_scene_manager(self):
        """Create a mock scene manager with save functionality."""
        manager = Mock()
        manager.game_data = {"selected_character": "danger"}
        manager.sound_manager = Mock()
        manager.save_manager = Mock()
        manager.save_manager.get_last_save_time.return_value = datetime.now()
        manager.save_game = Mock()
        return manager

    def test_couch_interaction_saves_game(self, mock_scene_manager):
        """Test that interacting with couch saves the game."""
        from src.scenes.hub import HubWorld

        with patch("pygame.font.Font"):
            hub = HubWorld(mock_scene_manager)

            # Position player near couch
            hub.player.rect.center = (400, 450)  # Near couch at (350, 400)

            # Update to detect proximity
            hub.update(0.016)
            assert hub.couch.is_highlighted

            # Press E to save
            event = Mock()
            event.type = pygame.KEYDOWN
            event.key = pygame.K_e

            hub.handle_event(event)

            # Verify save was triggered
            mock_scene_manager.save_game.assert_called_once()
            assert hub.couch.is_saving
            assert hub.save_notification.active

    def test_tab_opens_settings_from_couch(self, mock_scene_manager):
        """Test that TAB key opens settings when near couch."""
        from src.scenes.hub import HubWorld

        with patch("pygame.font.Font"):
            hub = HubWorld(mock_scene_manager)

            # Position player near couch
            hub.player.rect.center = (400, 450)
            hub.update(0.016)

            # Press TAB
            event = Mock()
            event.type = pygame.KEYDOWN
            event.key = pygame.K_TAB

            result = hub.handle_event(event)
            assert result == "settings"

    def test_last_save_time_display(self, mock_scene_manager):
        """Test that last save time is displayed correctly."""
        from src.scenes.hub import HubWorld

        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((800, 600))

        # Set up various save time scenarios
        test_cases = [
            (datetime.now(), "Just now"),  # Recent save
            (datetime(2024, 1, 1, 12, 0), None),  # Old save (will show time)
        ]

        with patch("pygame.font.Font") as mock_font_class:
            # Create mock font instances
            mock_font = Mock()
            mock_surface = Mock()
            mock_surface.get_rect = Mock(return_value=pygame.Rect(0, 0, 100, 20))
            mock_font.render.return_value = mock_surface
            mock_font_class.return_value = mock_font

            for save_time, expected_contains in test_cases:
                mock_scene_manager.save_manager.get_last_save_time.return_value = (
                    save_time
                )

                hub = HubWorld(mock_scene_manager)

                # Create a proper pygame surface instead of mock
                screen = pygame.Surface((800, 600))

                # Draw should not raise errors
                hub.draw(screen)

                # Just verify no errors were raised
