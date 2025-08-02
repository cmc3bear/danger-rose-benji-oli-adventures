"""Notification system for game messages."""

from datetime import datetime

import pygame

from src.config.constants import (
    COLOR_BLACK,
    COLOR_GREEN,
    COLOR_WHITE,
    SCREEN_WIDTH,
)


class SaveNotification:
    """Animated notification for save confirmations."""

    def __init__(
        self,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        position: tuple[int, int] | None = None,
    ):
        """Initialize save notification.

        Args:
            font: Main font for notification text
            small_font: Smaller font for timestamp
            position: Optional custom position (defaults to top-center)
        """
        self.font = font
        self.small_font = small_font
        self.active = False
        self.timer = 0.0
        self.alpha = 0
        self.last_save_time: datetime | None = None

        # Animation settings
        self.fade_in_duration = 0.3
        self.display_duration = 2.0
        self.fade_out_duration = 0.5
        self.total_duration = (
            self.fade_in_duration + self.display_duration + self.fade_out_duration
        )

        # Position
        if position:
            self.x, self.y = position
        else:
            self.x = SCREEN_WIDTH // 2
            self.y = 100

        # Visual settings
        self.bg_color = COLOR_BLACK
        self.text_color = COLOR_WHITE
        self.accent_color = COLOR_GREEN

    def show(self, save_time: datetime | None = None) -> None:
        """Show the save notification.

        Args:
            save_time: Time of save (defaults to current time)
        """
        self.active = True
        self.timer = 0.0
        self.last_save_time = save_time or datetime.now()

    def update(self, dt: float) -> None:
        """Update notification animation.

        Args:
            dt: Delta time in seconds
        """
        if not self.active:
            return

        self.timer += dt

        # Calculate alpha based on animation phase
        if self.timer < self.fade_in_duration:
            # Fade in
            self.alpha = int((self.timer / self.fade_in_duration) * 255)
        elif self.timer < self.fade_in_duration + self.display_duration:
            # Full display
            self.alpha = 255
        elif self.timer < self.total_duration:
            # Fade out
            fade_progress = (
                self.timer - self.fade_in_duration - self.display_duration
            ) / self.fade_out_duration
            self.alpha = int((1 - fade_progress) * 255)
        else:
            # Animation complete
            self.active = False
            self.alpha = 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the notification.

        Args:
            screen: Surface to draw on
        """
        if not self.active or self.alpha == 0:
            return

        # Create notification surface
        main_text = self.font.render("Game Saved!", True, self.text_color)
        main_rect = main_text.get_rect(center=(self.x, self.y))

        # Add timestamp if available
        time_text = None
        time_rect = None
        if self.last_save_time:
            time_str = self.last_save_time.strftime("%I:%M %p")
            time_text = self.small_font.render(time_str, True, self.text_color)
            time_rect = time_text.get_rect(centerx=self.x, top=main_rect.bottom + 5)

        # Create background
        padding = 20
        bg_width = (
            max(
                main_rect.width,
                time_rect.width if time_rect else 0,
            )
            + padding * 2
        )
        bg_height = main_rect.height + padding * 2
        if time_rect:
            bg_height += time_rect.height + 5

        bg_rect = pygame.Rect(0, 0, bg_width, bg_height)
        bg_rect.center = (
            self.x,
            self.y + (bg_height - main_rect.height) // 2 - padding // 2,
        )

        # Create surfaces with alpha
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(int(self.alpha * 0.8))  # Semi-transparent background
        bg_surface.fill(self.bg_color)

        # Draw accent border
        border_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        border_surface.set_alpha(self.alpha)
        pygame.draw.rect(
            border_surface, self.accent_color, (0, 0, bg_rect.width, bg_rect.height), 3
        )

        # Apply surfaces
        screen.blit(bg_surface, bg_rect)
        screen.blit(border_surface, bg_rect)

        # Draw text with alpha
        text_surface = pygame.Surface(
            (main_rect.width, main_rect.height), pygame.SRCALPHA
        )
        text_surface.blit(main_text, (0, 0))
        text_surface.set_alpha(self.alpha)
        screen.blit(text_surface, main_rect)

        if time_text and time_rect:
            time_surface = pygame.Surface(
                (time_rect.width, time_rect.height), pygame.SRCALPHA
            )
            time_surface.blit(time_text, (0, 0))
            time_surface.set_alpha(self.alpha)
            screen.blit(time_surface, time_rect)

        # Draw checkmark icon
        if self.alpha == 255:  # Only when fully visible
            check_size = 20
            check_x = bg_rect.left + padding
            check_y = bg_rect.centery
            # Simple checkmark using lines
            pygame.draw.lines(
                screen,
                self.accent_color,
                False,
                [
                    (check_x, check_y),
                    (check_x + check_size // 3, check_y + check_size // 3),
                    (check_x + check_size, check_y - check_size // 2),
                ],
                3,
            )
