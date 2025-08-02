"""Tests for Dad AI character in ski minigame."""

import pygame
import pytest

from src.entities.dad_ai import DadAI
from src.scenes.slope_generator import Obstacle


class TestDadAI:
    """Test suite for Dad AI behavior."""

    @pytest.fixture
    def dad(self):
        """Create a Dad AI instance for testing."""
        pygame.init()
        return DadAI(640, 600, 1280)

    def test_initialization(self, dad):
        """Test Dad AI is properly initialized."""
        assert dad.x == 640
        assert dad.y == 600
        assert dad.screen_width == 1280
        assert dad.min_distance == 100
        assert dad.max_distance == 300
        assert dad.base_speed == 4.5
        assert not dad.is_celebrating

    def test_rubber_band_movement_too_far(self, dad):
        """Test Dad speeds up when too far from player."""
        player_x = 1000  # Player is far to the right
        dad.update(0.1, player_x, [])

        # Dad should speed up
        assert dad.current_speed > dad.base_speed
        assert dad.is_too_far

    def test_rubber_band_movement_too_close(self, dad):
        """Test Dad slows down when too close to player."""
        player_x = dad.x + 50  # Player is very close
        dad.update(0.1, player_x, [])

        # Dad should slow down
        assert dad.current_speed < dad.base_speed

    def test_rubber_band_movement_comfort_zone(self, dad):
        """Test Dad maintains normal speed in comfort zone."""
        player_x = dad.x + 150  # Player is at ideal distance
        dad.update(0.1, player_x, [])

        # Dad should maintain base speed
        assert dad.current_speed == dad.base_speed

    def test_movement_bounds(self, dad):
        """Test Dad stays within screen bounds."""
        # Try to move Dad far left
        dad.x = 0
        player_x = -500
        dad.update(0.1, player_x, [])

        # Dad should be clamped to minimum bound
        assert dad.x >= 64

        # Try to move Dad far right
        dad.x = 1280
        player_x = 2000
        dad.update(0.1, player_x, [])

        # Dad should be clamped to maximum bound
        assert dad.x <= 1280 - 64

    def test_obstacle_avoidance(self, dad):
        """Test Dad avoids obstacles in his path."""
        # Create a mock obstacle directly in front of Dad
        obstacle = Obstacle(
            x=dad.x + 50,
            y=dad.y - 50,
            width=48,
            height=48,
            obstacle_type="rock",
            sprite=pygame.Surface((48, 48)),
            rect=pygame.Rect(dad.x + 50, dad.y - 50, 48, 48),
        )

        player_x = dad.x + 200  # Player is to the right
        initial_x = dad.x  # noqa: F841

        dad.update(0.1, player_x, [obstacle])

        # Dad should have adjusted his path
        # The specific adjustment depends on obstacle position
        assert dad.target_x != player_x - dad.min_distance

    def test_celebration_state(self, dad):
        """Test Dad's celebration behavior."""
        assert not dad.is_celebrating

        # Start celebration
        dad.start_celebration()
        assert dad.is_celebrating
        assert dad.celebration_time == 3.0

        # Update for 2 seconds
        dad.update(2.0, dad.x, [])
        assert dad.is_celebrating
        assert dad.celebration_time == 1.0

        # Update for another 2 seconds (total 4 seconds)
        dad.update(2.0, dad.x, [])
        assert not dad.is_celebrating

    def test_distance_calculation(self, dad):
        """Test distance calculation to player."""
        player_x = 800
        distance = dad.get_distance_to_player(player_x)

        expected_distance = abs(dad.x - player_x)
        assert distance == expected_distance

    def test_update_rect_position(self, dad):
        """Test collision rect follows Dad's position."""
        dad.x = 500
        dad.y = 400
        dad.update(0.1, 600, [])

        assert dad.rect.centerx == int(dad.x)
        assert dad.rect.centery == int(dad.y)

    def test_distance_indicators(self, dad):
        """Test distance indicator flags are set correctly."""
        # Test too far
        player_x = dad.x + 400  # Beyond max distance
        dad.update(0.1, player_x, [])
        assert dad.is_too_far
        assert not dad.is_too_close

        # Test too close
        player_x = dad.x + 25  # Very close
        dad.update(0.1, player_x, [])
        assert not dad.is_too_far
        assert dad.is_too_close

        # Test normal distance
        player_x = dad.x + 150  # Comfort zone
        dad.update(0.1, player_x, [])
        assert not dad.is_too_far
        assert not dad.is_too_close


@pytest.mark.skipif(
    not pygame.display.get_init(), reason="Pygame display not initialized"
)
class TestDadAIRendering:
    """Test rendering-related functionality of Dad AI."""

    @pytest.fixture
    def dad(self):
        """Create Dad AI with display initialized."""
        pygame.init()
        pygame.display.set_mode((1280, 720))
        return DadAI(640, 600, 1280)

    @pytest.fixture
    def screen(self):
        """Get the pygame display surface."""
        return pygame.display.get_surface()

    def test_draw_without_errors(self, dad, screen):
        """Test Dad can be drawn without errors."""
        # This should not raise any exceptions
        dad.draw(screen)

    def test_draw_celebration_effect(self, dad, screen):
        """Test celebration visual effect is applied."""
        dad.start_celebration()
        # Drawing during celebration should not raise errors
        dad.draw(screen)

    def test_draw_distance_indicators(self, dad, screen):
        """Test distance indicators are drawn correctly."""
        # Set Dad as too far
        dad.is_too_far = True
        dad.draw(screen)

        # Set Dad as too close
        dad.is_too_far = False
        dad.is_too_close = True
        dad.draw(screen)
