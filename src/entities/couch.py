"""Interactive couch entity for save point functionality."""

import pygame

from src.config.constants import (
    COLOR_BLACK,
    COLOR_BROWN,
    COLOR_GREEN,
    COLOR_WHITE,
)


class Couch:
    """Interactive couch that serves as a save point."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int = 200,
        height: int = 100,
    ):
        """Initialize a couch save point.

        Args:
            x: X position of couch
            y: Y position of couch
            width: Width of couch (default 200)
            height: Height of couch (default 100)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = COLOR_BROWN if COLOR_BROWN else (101, 67, 33)  # Brown color
        self.highlight_color = COLOR_GREEN
        self.is_highlighted = False
        self.is_saving = False
        self.save_animation_timer = 0.0

        # Interaction zone (slightly larger than visual couch)
        padding = 30
        self.interaction_rect = pygame.Rect(
            x - padding, y - padding, width + padding * 2, height + padding * 2
        )

        # Visual elements
        self.cushion_color = (139, 90, 43)  # Darker brown for cushions

    def check_player_proximity(self, player_rect: pygame.Rect) -> bool:
        """Check if player is close enough to interact.

        Args:
            player_rect: Player's collision rectangle

        Returns:
            True if player is within interaction range
        """
        return self.interaction_rect.colliderect(player_rect)

    def trigger_save(self) -> None:
        """Trigger the save animation."""
        self.is_saving = True
        self.save_animation_timer = 2.0  # 2 seconds for save animation

    def update(self, dt: float) -> None:
        """Update save animation timer.

        Args:
            dt: Delta time in seconds
        """
        if self.is_saving and self.save_animation_timer > 0:
            self.save_animation_timer -= dt
            if self.save_animation_timer <= 0:
                self.is_saving = False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the couch and interaction hints.

        Args:
            screen: Surface to draw on
            font: Font for rendering text
        """
        # Draw couch base
        color = self.highlight_color if self.is_highlighted else self.color
        pygame.draw.rect(screen, color, self.rect, 0)
        pygame.draw.rect(screen, COLOR_BLACK, self.rect, 3)

        # Draw cushions
        cushion_width = self.rect.width // 3
        cushion_height = self.rect.height // 2
        cushion_y = self.rect.y + self.rect.height // 4

        for i in range(3):
            cushion_x = self.rect.x + i * cushion_width + 5
            cushion_rect = pygame.Rect(
                cushion_x, cushion_y, cushion_width - 10, cushion_height
            )
            pygame.draw.rect(screen, self.cushion_color, cushion_rect, 0)
            pygame.draw.rect(screen, COLOR_BLACK, cushion_rect, 2)

        # Draw interaction hints
        if self.is_highlighted and not self.is_saving:
            # Primary action hint
            hint_text = font.render("Press E to save game", True, COLOR_WHITE)
            hint_rect = hint_text.get_rect(
                centerx=self.rect.centerx, bottom=self.rect.top - 10
            )
            # Draw background for better readability
            padding = 5
            bg_rect = hint_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(screen, COLOR_BLACK, bg_rect)
            screen.blit(hint_text, hint_rect)

            # Secondary action hint
            settings_text = font.render("Press TAB for settings", True, COLOR_WHITE)
            settings_rect = settings_text.get_rect(
                centerx=self.rect.centerx, bottom=hint_rect.top - 5
            )
            bg_rect2 = settings_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(screen, COLOR_BLACK, bg_rect2)
            screen.blit(settings_text, settings_rect)

        # Draw save animation
        if self.is_saving:
            save_text = font.render("Saving...", True, COLOR_WHITE)
            save_rect = save_text.get_rect(
                center=(self.rect.centerx, self.rect.centery)
            )
            # Pulsing effect
            alpha = int(abs(self.save_animation_timer * 255) % 255)
            save_surface = pygame.Surface((save_rect.width + 20, save_rect.height + 10))
            save_surface.set_alpha(alpha)
            save_surface.fill(COLOR_GREEN)
            screen.blit(
                save_surface,
                (save_rect.x - 10, save_rect.y - 5),
            )
            screen.blit(save_text, save_rect)
