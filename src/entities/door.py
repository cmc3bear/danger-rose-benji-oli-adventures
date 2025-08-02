"""Interactive door entity for scene transitions."""

import pygame

from src.config.constants import (
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_WHITE,
)


class Door:
    """Interactive door that transitions to other scenes."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        target_scene: str,
        label: str,
        color: tuple[int, int, int] = COLOR_BLUE,
    ):
        """Initialize a door with position and target scene.

        Args:
            x: X position of door
            y: Y position of door
            width: Width of door
            height: Height of door
            target_scene: Scene name to transition to when activated
            label: Display label for the door
            color: Door color (default blue)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.target_scene = target_scene
        self.label = label
        self.color = color
        self.highlight_color = COLOR_GREEN
        self.is_highlighted = False

        # Interaction zone (slightly larger than visual door)
        padding = 20
        self.interaction_rect = pygame.Rect(
            x - padding, y - padding, width + padding * 2, height + padding * 2
        )

    def check_player_proximity(self, player_rect: pygame.Rect) -> bool:
        """Check if player is close enough to interact.

        Args:
            player_rect: Player's collision rectangle

        Returns:
            True if player is within interaction range
        """
        return self.interaction_rect.colliderect(player_rect)

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the door and its label.

        Args:
            screen: Surface to draw on
            font: Font for rendering label
        """
        # Draw door rectangle
        color = self.highlight_color if self.is_highlighted else self.color
        pygame.draw.rect(screen, color, self.rect, 3)

        # Fill with semi-transparent color
        s = pygame.Surface((self.rect.width, self.rect.height))
        s.set_alpha(128)
        s.fill(color)
        screen.blit(s, (self.rect.x, self.rect.y))

        # Draw label
        label_text = font.render(self.label, True, COLOR_WHITE)
        label_rect = label_text.get_rect(center=self.rect.center)
        screen.blit(label_text, label_rect)

        # Draw interaction hint if highlighted
        if self.is_highlighted:
            hint_text = font.render("Press E to enter", True, COLOR_WHITE)
            hint_rect = hint_text.get_rect(
                centerx=self.rect.centerx, top=self.rect.bottom + 10
            )
            # Draw background for better readability
            padding = 5
            bg_rect = hint_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(screen, COLOR_BLACK, bg_rect)
            screen.blit(hint_text, hint_rect)
