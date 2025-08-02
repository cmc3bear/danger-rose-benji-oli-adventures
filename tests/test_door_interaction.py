"""Tests for door interaction system."""

import pygame
import pytest

from src.config.constants import COLOR_BLUE, COLOR_GREEN
from src.entities.door import Door
from src.scene_manager import SceneManager
from src.scenes.hub import HubWorld


class TestDoorEntity:
    """Test the Door entity class."""

    def test_door_creation(self):
        """Test creating a door with proper attributes."""
        door = Door(100, 200, 80, 120, "ski", "Ski Game", COLOR_BLUE)

        assert door.rect.x == 100
        assert door.rect.y == 200
        assert door.rect.width == 80
        assert door.rect.height == 120
        assert door.target_scene == "ski"
        assert door.label == "Ski Game"
        assert door.color == COLOR_BLUE
        assert door.highlight_color == COLOR_GREEN
        assert not door.is_highlighted

    def test_door_interaction_rect(self):
        """Test that interaction rect is larger than visual rect."""
        door = Door(100, 200, 80, 120, "ski", "Ski Game")

        # Interaction rect should be 20 pixels larger on each side
        assert door.interaction_rect.x == 80  # 100 - 20
        assert door.interaction_rect.y == 180  # 200 - 20
        assert door.interaction_rect.width == 120  # 80 + 40
        assert door.interaction_rect.height == 160  # 120 + 40

    def test_player_proximity_detection(self):
        """Test door detects when player is nearby."""
        door = Door(400, 300, 100, 150, "pool", "Pool Game")

        # Create a mock player rect
        # Player far away - should not detect
        far_player = pygame.Rect(100, 100, 128, 128)
        assert not door.check_player_proximity(far_player)

        # Player nearby - should detect
        near_player = pygame.Rect(380, 280, 128, 128)  # Overlapping interaction rect
        assert door.check_player_proximity(near_player)

        # Player touching edge of interaction rect - should detect
        edge_player = pygame.Rect(360, 260, 128, 128)  # Just touching interaction rect
        assert door.check_player_proximity(edge_player)


class TestHubWorldDoorIntegration:
    """Test door integration in the hub world."""

    @pytest.fixture
    def setup_pygame(self):
        """Initialize pygame for tests."""
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.HIDDEN)
        yield
        pygame.quit()

    def test_hub_world_has_doors(self, setup_pygame):
        """Test that hub world creates door objects."""
        scene_manager = SceneManager(800, 600)
        hub = HubWorld(scene_manager)

        # Should have 3 doors
        assert len(hub.doors) == 3

        # Check door properties
        door_labels = [door.label for door in hub.doors]
        assert "Ski Game" in door_labels
        assert "Pool Game" in door_labels
        assert "Vegas Game" in door_labels

        door_targets = [door.target_scene for door in hub.doors]
        assert "ski" in door_targets
        assert "pool" in door_targets
        assert "vegas" in door_targets

    def test_door_highlighting_on_proximity(self, setup_pygame):
        """Test doors highlight when player is near."""
        scene_manager = SceneManager(800, 600)
        hub = HubWorld(scene_manager)

        # Move player near first door (ski door at x=200, y=100)
        hub.player.x = 250
        hub.player.y = 175
        hub.player.rect.centerx = int(hub.player.x)
        hub.player.rect.centery = int(hub.player.y)

        # Update hub world
        hub.update(0.016)  # 60 FPS

        # First door should be highlighted
        assert hub.doors[0].is_highlighted
        assert hub.highlighted_door == hub.doors[0]

        # Other doors should not be highlighted
        assert not hub.doors[1].is_highlighted
        assert not hub.doors[2].is_highlighted

    def test_door_interaction_with_e_key(self, setup_pygame):
        """Test pressing E near a door triggers scene transition."""
        scene_manager = SceneManager(800, 600)
        hub = HubWorld(scene_manager)

        # Move player near pool door (second door)
        hub.player.x = 450
        hub.player.y = 175
        hub.player.rect.centerx = int(hub.player.x)
        hub.player.rect.centery = int(hub.player.y)

        # Update to detect proximity
        hub.update(0.016)

        # Simulate pressing E key
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        next_scene = hub.handle_event(event)

        # Should transition to pool scene
        assert next_scene == "pool"

    def test_no_interaction_when_far_from_doors(self, setup_pygame):
        """Test E key does nothing when not near any door."""
        scene_manager = SceneManager(800, 600)
        hub = HubWorld(scene_manager)

        # Move player to center (away from all doors)
        hub.player.x = 640
        hub.player.y = 400
        hub.player.rect.centerx = int(hub.player.x)
        hub.player.rect.centery = int(hub.player.y)

        # Update to check proximity
        hub.update(0.016)

        # No door should be highlighted
        assert hub.highlighted_door is None
        assert all(not door.is_highlighted for door in hub.doors)

        # Pressing E should do nothing
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        next_scene = hub.handle_event(event)
        assert next_scene is None
