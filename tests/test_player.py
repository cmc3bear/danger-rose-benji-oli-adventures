"""Unit tests for the Player entity class."""

import pygame
import pytest

from src.config.constants import PLAYER_SPEED, SPRITE_DISPLAY_SIZE
from src.entities.player import Player


@pytest.fixture
def player():
    """Create a test player instance."""
    pygame.init()
    pygame.display.set_mode((800, 600))  # Required for sprite loading
    return Player(400, 300, "danger")


class TestPlayerInitialization:
    """Test player initialization."""

    def test_initial_position(self, player):
        """Test that player starts at given position."""
        assert player.x == 400
        assert player.y == 300

    def test_initial_velocity(self, player):
        """Test that player starts with zero velocity."""
        assert player.vx == 0.0
        assert player.vy == 0.0

    def test_initial_movement_flags(self, player):
        """Test that movement flags start as False."""
        assert player.move_left is False
        assert player.move_right is False
        assert player.move_up is False
        assert player.move_down is False

    def test_initial_facing_direction(self, player):
        """Test that player starts facing right."""
        assert player.facing_right is True

    def test_collision_rect_centered(self, player):
        """Test that collision rect is centered on position."""
        assert player.rect.centerx == 400
        assert player.rect.centery == 300
        assert player.rect.width == SPRITE_DISPLAY_SIZE
        assert player.rect.height == SPRITE_DISPLAY_SIZE


class TestPlayerMovement:
    """Test player movement mechanics."""

    def test_keyboard_input_keydown(self, player):
        """Test that keydown events set movement flags."""
        # Test arrow keys
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT})
        player.handle_event(event)
        assert player.move_left is True

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT})
        player.handle_event(event)
        assert player.move_right is True

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP})
        player.handle_event(event)
        assert player.move_up is True

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_DOWN})
        player.handle_event(event)
        assert player.move_down is True

    def test_keyboard_input_wasd(self, player):
        """Test that WASD keys also work for movement."""
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_a})
        player.handle_event(event)
        assert player.move_left is True

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_d})
        player.handle_event(event)
        assert player.move_right is True

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_w})
        player.handle_event(event)
        assert player.move_up is True

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_s})
        player.handle_event(event)
        assert player.move_down is True

    def test_keyboard_input_keyup(self, player):
        """Test that keyup events clear movement flags."""
        # Set flags first
        player.move_left = True
        player.move_right = True

        # Test key up
        event = pygame.event.Event(pygame.KEYUP, {"key": pygame.K_LEFT})
        player.handle_event(event)
        assert player.move_left is False

        event = pygame.event.Event(pygame.KEYUP, {"key": pygame.K_d})
        player.handle_event(event)
        assert player.move_right is False

    def test_horizontal_movement(self, player):
        """Test horizontal movement physics."""
        player.move_right = True
        player.update(0.1, [])  # 0.1 second update

        # Should have positive x velocity
        assert player.vx > 0
        assert player.vy == 0
        # Position should have changed
        assert player.x > 400
        assert player.y == 300

    def test_vertical_movement(self, player):
        """Test vertical movement physics."""
        player.move_up = True
        player.update(0.1, [])

        # Should have negative y velocity (up is negative)
        assert player.vy < 0
        assert player.vx == 0
        # Position should have changed
        assert player.y < 300
        assert player.x == 400

    def test_diagonal_movement_normalized(self, player):
        """Test that diagonal movement is normalized."""
        player.move_right = True
        player.move_down = True
        player.update(0.1, [])

        # Diagonal velocity should be normalized
        # Each component should be less than full speed
        assert 0 < player.vx < PLAYER_SPEED
        assert 0 < player.vy < PLAYER_SPEED

        # Combined magnitude should be approximately PLAYER_SPEED
        magnitude = (player.vx**2 + player.vy**2) ** 0.5
        expected_magnitude = PLAYER_SPEED
        assert abs(magnitude - expected_magnitude) < 1  # Within 1 pixel/s

    def test_friction_stops_movement(self, player):
        """Test that movement stops immediately when no input."""
        # Start moving
        player.move_right = True
        player.update(0.1, [])
        assert player.vx > 0

        # Stop input
        player.move_right = False
        player.update(0.1, [])

        # Velocity should be zero immediately with instant velocity
        assert player.vx == 0
        assert player.vy == 0

    def test_facing_direction_changes(self, player):
        """Test that facing direction changes with movement."""
        # Move left
        player.move_left = True
        player.update(0.1, [])
        assert player.facing_right is False

        # Move right
        player.move_left = False
        player.move_right = True
        player.update(0.1, [])
        assert player.facing_right is True


class TestPlayerCollision:
    """Test player collision detection."""

    def test_collision_stops_movement(self, player):
        """Test that collision with boundary stops movement."""
        # Create boundary close to player's right
        # Player starts at 400, has radius of 64 (half of 128), so edge is at 464
        # Put boundary at 470 so there's a small gap
        boundary = pygame.Rect(470, 250, 100, 100)

        # Try to move right into boundary
        player.move_right = True
        old_x = player.x

        # Update once
        player.update(0.1, [boundary])

        # Player should have moved some but not into boundary
        assert player.x > old_x  # Should have moved
        assert player.x < 470 - SPRITE_DISPLAY_SIZE / 2  # But not past boundary edge

    def test_slide_along_wall(self, player):
        """Test that player can slide along walls."""
        # Create vertical wall to the right, close enough to collide diagonally
        wall = pygame.Rect(440, 200, 20, 200)

        # Move diagonally into wall
        player.move_right = True
        player.move_up = True

        old_y = player.y
        player.update(0.1, [wall])

        # Should move up but not right (sliding along wall)
        assert player.y < old_y  # Moved up
        assert player.x <= 440 - SPRITE_DISPLAY_SIZE / 2  # Didn't pass wall

    def test_corner_collision(self, player):
        """Test collision at corners."""
        # Create walls forming a corner
        walls = [
            pygame.Rect(450, 250, 100, 20),  # Horizontal wall
            pygame.Rect(450, 250, 20, 100),  # Vertical wall
        ]

        # Move diagonally toward corner
        player.move_right = True
        player.move_up = True

        player.update(0.1, walls)

        # Should not pass either wall
        assert player.x < 450
        assert player.y > 250


class TestPlayerUtilities:
    """Test player utility methods."""

    def test_get_position(self, player):
        """Test position getter."""
        pos = player.get_position()
        assert pos == (400, 300)

        # Move and check again
        player.x = 500
        player.y = 200
        pos = player.get_position()
        assert pos == (500, 200)

    def test_get_velocity(self, player):
        """Test velocity getter."""
        vel = player.get_velocity()
        assert vel == (0, 0)

        # Set velocity and check
        player.vx = 100
        player.vy = -50
        vel = player.get_velocity()
        assert vel == (100, -50)

    def test_is_moving(self, player):
        """Test movement detection."""
        assert player.is_moving() is False

        # Small velocity should not count as moving
        player.vx = 5
        assert player.is_moving() is False

        # Larger velocity should count
        player.vx = 50
        assert player.is_moving() is True

        # Test with y velocity
        player.vx = 0
        player.vy = 50
        assert player.is_moving() is True
