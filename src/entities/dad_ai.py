"""Dad AI character for the ski minigame with rubber-band movement."""

import pygame

from src.config.constants import COLOR_GREEN, COLOR_RED, SPRITE_DISPLAY_SIZE
from src.utils.attack_character import AnimatedCharacter


class DadAI:
    """Dad character that follows player using rubber-band AI movement."""

    def __init__(self, x: int, y: int, screen_width: int = 1280):
        """Initialize Dad AI character.

        Args:
            x: Initial x position
            y: Initial y position
            screen_width: Width of the game screen for bounds checking
        """
        self.x = x
        self.y = y
        self.target_x = x  # Target position to move towards
        self.screen_width = screen_width

        # Rubber-band AI parameters
        self.min_distance = 100  # Minimum distance from player
        self.max_distance = 300  # Maximum distance from player
        self.comfort_zone = 150  # Ideal distance from player

        # Movement parameters
        self.base_speed = 4.5  # Base movement speed
        self.max_speed = 8.0  # Maximum speed when catching up
        self.min_speed = 2.0  # Minimum speed when ahead
        self.current_speed = self.base_speed

        # Smooth movement
        self.smooth_factor = 0.15  # How smoothly Dad moves (0-1)

        # Create animated character sprite using new individual file system
        self.sprite = AnimatedCharacter(
            "dad", "ski", (SPRITE_DISPLAY_SIZE, SPRITE_DISPLAY_SIZE)
        )
        # Set to walk animation for skiing
        self.sprite.set_animation("walk", loop=True)

        # Collision rect - smaller than sprite for forgiving collisions
        self.rect = pygame.Rect(x - 24, y - 24, 48, 48)

        # State tracking
        self.is_celebrating = False
        self.celebration_time = 0

        # Distance indicator state
        self.distance_from_player = 0
        self.is_too_far = False
        self.is_too_close = False

    def update(self, dt: float, player_x: int, obstacles: list) -> None:
        """Update Dad's position and state.

        Args:
            dt: Delta time in seconds
            player_x: Player's current x position
            obstacles: List of obstacles to avoid
        """
        # Calculate distance from player
        self.distance_from_player = abs(self.x - player_x)

        # Update distance state for visual indicators
        self.is_too_far = self.distance_from_player > self.max_distance
        self.is_too_close = self.distance_from_player < self.min_distance * 0.5

        # Calculate rubber-band speed based on distance
        if self.distance_from_player > self.comfort_zone:
            # Behind player - speed up proportionally
            speed_multiplier = min(
                (self.distance_from_player - self.comfort_zone) / self.comfort_zone, 1.0
            )
            self.current_speed = self.base_speed + (
                (self.max_speed - self.base_speed) * speed_multiplier
            )
        elif self.distance_from_player < self.min_distance:
            # Too close - slow down
            self.current_speed = self.min_speed
        else:
            # In comfort zone - normal speed
            self.current_speed = self.base_speed

        # Determine target position
        if player_x < self.x - self.min_distance:
            # Player is to the left
            self.target_x = player_x + self.min_distance
        elif player_x > self.x + self.min_distance:
            # Player is to the right
            self.target_x = player_x - self.min_distance
        else:
            # Player is within minimum distance
            self.target_x = self.x  # Stay put

        # Check for obstacles in the path
        obstacle_adjustment = self._check_obstacle_avoidance(obstacles)
        if obstacle_adjustment != 0:
            self.target_x += obstacle_adjustment

        # Smooth movement towards target
        if self.target_x != self.x:
            direction = 1 if self.target_x > self.x else -1
            move_distance = self.current_speed * direction

            # Apply smooth interpolation
            self.x += move_distance * self.smooth_factor

            # Clamp to screen bounds (with margin)
            self.x = max(64, min(self.x, self.screen_width - 64))

        # Update collision rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Update sprite animation
        self.sprite.update()

        # Update celebration state
        if self.is_celebrating:
            self.celebration_time -= dt
            if self.celebration_time <= 0:
                self.is_celebrating = False

    def _check_obstacle_avoidance(self, obstacles: list) -> int:
        """Check if Dad needs to avoid obstacles.

        Args:
            obstacles: List of obstacles to check

        Returns:
            Adjustment value for x position (-1 for left, 1 for right, 0 for none)
        """
        # Look ahead for obstacles
        look_ahead_distance = 100
        avoidance_radius = 80

        for obstacle in obstacles:
            # Check if obstacle is in Dad's path
            if abs(obstacle.y - self.y) < look_ahead_distance:
                obstacle_distance = obstacle.rect.centerx - self.x

                if abs(obstacle_distance) < avoidance_radius:
                    # Obstacle is too close - avoid it
                    if obstacle_distance > 0:
                        # Obstacle is to the right, move left
                        return -avoidance_radius
                    # Obstacle is to the left, move right
                    return avoidance_radius

        return 0

    def start_celebration(self) -> None:
        """Start Dad's celebration animation."""
        self.is_celebrating = True
        self.celebration_time = 3.0  # Celebrate for 3 seconds

    def draw(self, screen: pygame.Surface) -> None:
        """Draw Dad character and any visual indicators.

        Args:
            screen: Surface to draw on
        """
        # Get current sprite
        sprite = self.sprite.get_current_sprite()

        # Apply celebration effect
        if self.is_celebrating:
            # Make sprite bounce or flash during celebration
            if int(self.celebration_time * 10) % 2 == 0:
                sprite = sprite.copy()
                sprite.fill((255, 255, 200), special_flags=pygame.BLEND_ADD)

        # Draw the sprite
        sprite_rect = sprite.get_rect(center=(self.x, self.y))
        screen.blit(sprite, sprite_rect)

        # Draw distance indicator
        self._draw_distance_indicator(screen)

    def _draw_distance_indicator(self, screen: pygame.Surface) -> None:
        """Draw visual indicator showing Dad's distance from player.

        Args:
            screen: Surface to draw on
        """
        # Draw an arrow or indicator if Dad is too far away
        if self.is_too_far:
            # Draw a red arrow pointing to Dad's position
            indicator_y = 100

            # Draw arrow shape
            arrow_points = [
                (self.x - 10, indicator_y),
                (self.x + 10, indicator_y),
                (self.x, indicator_y + 20),
            ]
            pygame.draw.polygon(screen, COLOR_RED, arrow_points)

            # Draw "DAD" text above arrow
            font = pygame.font.Font(None, 24)
            text = font.render("DAD", True, COLOR_RED)
            text_rect = text.get_rect(center=(self.x, indicator_y - 20))
            screen.blit(text, text_rect)

        elif self.is_too_close:
            # Draw a subtle green indicator when Dad is very close
            pygame.draw.circle(screen, COLOR_GREEN, (int(self.x), int(self.y - 40)), 5)

    def get_distance_to_player(self, player_x: int) -> float:
        """Get current distance to player.

        Args:
            player_x: Player's x position

        Returns:
            Distance in pixels
        """
        return abs(self.x - player_x)
