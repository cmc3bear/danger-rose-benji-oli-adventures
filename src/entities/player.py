"""Player entity class for Danger Rose game."""

import pygame

from src.config.constants import (
    PLAYER_SPEED,
    SPRITE_DISPLAY_SIZE,
)
from src.utils.attack_character import AnimatedCharacter


class Player:
    """Player character with movement, physics, and collision detection."""

    def __init__(self, x: float, y: float, character_name: str):
        """Initialize player with position and character sprite.

        Args:
            x: Initial x position
            y: Initial y position
            character_name: Name of the character (danger, rose, dad)
        """
        self.x = x
        self.y = y
        self.vx = 0.0  # Velocity x
        self.vy = 0.0  # Velocity y

        # Movement input tracking
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

        # Direction facing (for sprite flipping)
        self.facing_right = True

        # Load character sprite using new individual file system
        # Default to "danger" if no character name provided
        character_name = character_name or "danger"
        self.sprite = AnimatedCharacter(
            character_name.lower(),
            "hub",
            scale=(SPRITE_DISPLAY_SIZE, SPRITE_DISPLAY_SIZE),
        )

        # Collision rectangle (centered on position)
        self.rect = pygame.Rect(
            self.x - SPRITE_DISPLAY_SIZE // 2,
            self.y - SPRITE_DISPLAY_SIZE // 2,
            SPRITE_DISPLAY_SIZE,
            SPRITE_DISPLAY_SIZE,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard input events.

        Args:
            event: Pygame event to process
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.move_left = True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.move_right = True
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.move_up = True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.move_down = True

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.move_left = False
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.move_right = False
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.move_up = False
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.move_down = False

    def update(self, dt: float, boundaries: list[pygame.Rect]) -> None:
        """Update player physics and position.

        Args:
            dt: Delta time in seconds
            boundaries: List of boundary rectangles to check collision against
        """
        # Calculate target velocity based on input
        target_vx = 0.0
        target_vy = 0.0

        if self.move_left:
            target_vx -= PLAYER_SPEED
        if self.move_right:
            target_vx += PLAYER_SPEED
        if self.move_up:
            target_vy -= PLAYER_SPEED
        if self.move_down:
            target_vy += PLAYER_SPEED

        # Normalize diagonal movement to prevent speed advantage
        if target_vx != 0 and target_vy != 0:
            diagonal_factor = 0.707  # 1/sqrt(2)
            target_vx *= diagonal_factor
            target_vy *= diagonal_factor

        # Apply instant velocity change for responsive controls
        self.vx = target_vx
        self.vy = target_vy

        # Store old position for collision rollback
        old_x = self.x
        old_y = self.y

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Update collision rectangle
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Check collisions with boundaries
        collided = False
        for boundary in boundaries:
            if self.rect.colliderect(boundary):
                collided = True
                break

        if collided:
            # Try horizontal movement only
            self.x = old_x + self.vx * dt
            self.y = old_y
            self.rect.centerx = int(self.x)
            self.rect.centery = int(self.y)

            if any(self.rect.colliderect(b) for b in boundaries):
                # Can't move horizontally, try vertical only
                self.x = old_x
                self.y = old_y + self.vy * dt
                self.rect.centerx = int(self.x)
                self.rect.centery = int(self.y)

                if any(self.rect.colliderect(b) for b in boundaries):
                    # Can't move at all, stay at old position
                    self.x = old_x
                    self.y = old_y
                    self.rect.centerx = int(self.x)
                    self.rect.centery = int(self.y)

        # Update facing direction
        if self.vx > 0:
            self.facing_right = True
        elif self.vx < 0:
            self.facing_right = False

        # Update animation state
        if abs(self.vx) > 10 or abs(self.vy) > 10:
            self.sprite.set_animation("walk", loop=True)
        else:
            self.sprite.set_animation("idle", loop=True)

        # Update sprite animation
        self.sprite.update()

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player sprite to the screen.

        Args:
            screen: Surface to draw on
        """
        sprite = self.sprite.get_current_sprite()

        # Flip sprite if facing left
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)

        # Draw centered on position
        sprite_rect = sprite.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(sprite, sprite_rect)

    def get_position(self) -> tuple[float, float]:
        """Get current player position.

        Returns:
            Tuple of (x, y) position
        """
        return (self.x, self.y)

    def get_velocity(self) -> tuple[float, float]:
        """Get current player velocity.

        Returns:
            Tuple of (vx, vy) velocity
        """
        return (self.vx, self.vy)

    def is_moving(self) -> bool:
        """Check if player is currently moving.

        Returns:
            True if player has non-zero velocity
        """
        return abs(self.vx) > 10 or abs(self.vy) > 10
