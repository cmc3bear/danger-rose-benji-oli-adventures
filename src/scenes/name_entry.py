"""Name entry scene for high score submissions."""

from typing import Any

import pygame

from src.config.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from src.scenes.base_scene import Scene
from src.utils.asset_paths import get_font_path


class NameEntryScene(Scene):
    """Scene for entering player name for high scores."""

    def __init__(self):
        """Initialize name entry scene."""
        super().__init__()

        # UI setup
        self.font = None
        self.big_font = None
        self.title_font = None

        # Input state
        self.player_name = ""
        self.max_name_length = 12
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_time = 0.5

        # Scene data
        self.game_mode = ""
        self.character = ""
        self.difficulty = ""
        self.score = 0
        self.callback_scene = "leaderboard"

        # Colors
        self.bg_color = (20, 20, 40)
        self.text_color = (255, 255, 255)
        self.input_bg_color = (40, 40, 60)
        self.input_border_color = (100, 100, 140)
        self.button_color = (60, 60, 100)
        self.button_hover_color = (80, 80, 120)

        # UI elements
        self.input_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 50
        )
        self.submit_button = pygame.Rect(
            SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 80, 150, 40
        )
        self.cancel_button = pygame.Rect(
            SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 130, 150, 40
        )

    def on_enter(
        self,
        previous_scene: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Enter the name entry scene.

        Args:
            previous_scene: Name of the previous scene
            data: Scene data including game_mode, character, score, etc.
        """
        # Initialize fonts
        try:
            font_path = get_font_path("pixel")
            self.font = pygame.font.Font(font_path, 24)
            self.big_font = pygame.font.Font(font_path, 36)
            self.title_font = pygame.font.Font(font_path, 48)
        except Exception:
            # Fallback to system font
            self.font = pygame.font.Font(None, 24)
            self.big_font = pygame.font.Font(None, 36)
            self.title_font = pygame.font.Font(None, 48)

        # Process incoming data
        if data:
            self.game_mode = data.get("game_mode", "")
            self.character = data.get("character", "")
            self.difficulty = data.get("difficulty", "normal")
            self.score = data.get("score", 0)
            self.callback_scene = data.get("callback_scene", "leaderboard")

            # Set default name based on character
            self.player_name = self.character.title() if self.character else "Player"

        # Reset input state
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Handle input events.

        Args:
            event: Pygame event to handle

        Returns:
            Next scene name if transitioning, None otherwise
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Cancel and go back
                return self.callback_scene

            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Submit name
                return self._submit_name()

            if event.key == pygame.K_BACKSPACE:
                # Remove last character
                if self.player_name:
                    self.player_name = self.player_name[:-1]

            elif event.unicode and event.unicode.isprintable():
                # Add character if not at max length
                if len(self.player_name) < self.max_name_length:
                    self.player_name += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()

                if self.submit_button.collidepoint(mouse_pos):
                    return self._submit_name()
                if self.cancel_button.collidepoint(mouse_pos):
                    return self.callback_scene

        return None

    def update(self, dt: float) -> None:
        """Update the name entry scene.

        Args:
            dt: Delta time in seconds
        """
        # Update cursor blink
        self.cursor_timer += dt
        if self.cursor_timer >= self.cursor_blink_time:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the name entry scene.

        Args:
            screen: Screen surface to draw on
        """
        # Clear screen
        screen.fill(self.bg_color)

        # Draw title
        title_text = self.title_font.render("NEW HIGH SCORE!", True, (255, 215, 0))
        title_rect = title_text.get_rect(centerx=SCREEN_WIDTH // 2, y=100)
        screen.blit(title_text, title_rect)

        # Draw score info
        score_info = f"{self.game_mode.upper()} - {self.character.title()} ({self.difficulty.title()})"
        info_text = self.font.render(score_info, True, self.text_color)
        info_rect = info_text.get_rect(centerx=SCREEN_WIDTH // 2, y=160)
        screen.blit(info_text, info_rect)

        # Draw score
        if self.game_mode == "ski":
            score_str = f"Time: {self.score:.2f}s"
        else:
            score_str = f"Score: {int(self.score)}"

        score_text = self.big_font.render(score_str, True, (255, 215, 0))
        score_rect = score_text.get_rect(centerx=SCREEN_WIDTH // 2, y=200)
        screen.blit(score_text, score_rect)

        # Draw prompt
        prompt_text = self.font.render("Enter your name:", True, self.text_color)
        prompt_rect = prompt_text.get_rect(centerx=SCREEN_WIDTH // 2, y=280)
        screen.blit(prompt_text, prompt_rect)

        # Draw input box
        pygame.draw.rect(screen, self.input_bg_color, self.input_rect)
        pygame.draw.rect(screen, self.input_border_color, self.input_rect, 2)

        # Draw entered text with cursor
        display_text = self.player_name
        if self.cursor_visible:
            display_text += "|"

        name_text = self.big_font.render(display_text, True, self.text_color)
        name_rect = name_text.get_rect(center=self.input_rect.center)
        screen.blit(name_text, name_rect)

        # Draw buttons
        self._draw_button(screen, self.submit_button, "SUBMIT")
        self._draw_button(screen, self.cancel_button, "CANCEL")

        # Draw instructions
        instructions = ["Type your name and press ENTER", "ESC to cancel"]

        y = SCREEN_HEIGHT - 100
        for instruction in instructions:
            text = self.font.render(instruction, True, (180, 180, 180))
            text_rect = text.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
            screen.blit(text, text_rect)
            y += 25

    def _draw_button(
        self, screen: pygame.Surface, rect: pygame.Rect, text: str
    ) -> None:
        """Draw a button with hover effect.

        Args:
            screen: Surface to draw on
            rect: Button rectangle
            text: Button text
        """
        mouse_pos = pygame.mouse.get_pos()
        color = (
            self.button_hover_color
            if rect.collidepoint(mouse_pos)
            else self.button_color
        )

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, self.input_border_color, rect, 2)

        button_text = self.font.render(text, True, self.text_color)
        text_rect = button_text.get_rect(center=rect.center)
        screen.blit(button_text, text_rect)

    def _submit_name(self) -> str:
        """Submit the entered name and return to callback scene.

        Returns:
            Next scene name
        """
        # Ensure name is not empty
        if not self.player_name.strip():
            self.player_name = self.character.title() if self.character else "Player"

        # Return to callback scene with name data
        return self.callback_scene

    def on_exit(self) -> dict[str, Any]:
        """Clean up when leaving the scene.

        Returns:
            Data to pass to the next scene including the entered name
        """
        return {
            "player_name": self.player_name.strip()
            or (self.character.title() if self.character else "Player"),
            "game_mode": self.game_mode,
            "character": self.character,
            "difficulty": self.difficulty,
            "score": self.score,
        }
