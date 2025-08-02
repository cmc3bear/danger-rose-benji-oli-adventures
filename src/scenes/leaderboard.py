"""Leaderboard scene for displaying high scores."""

from typing import Any

import pygame

from src.config.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from src.scenes.base_scene import Scene
from src.utils.asset_paths import get_font_path
from src.utils.high_score_manager import HighScoreManager


class LeaderboardScene(Scene):
    """Scene for displaying high scores and leaderboards."""

    # UI Constants
    TITLE_SIZE = 48
    HEADER_SIZE = 32
    SCORE_SIZE = 24
    MARGIN = 20
    SCORE_SPACING = 30
    TAB_HEIGHT = 50
    TAB_WIDTH = 200

    # Colors
    BG_COLOR = (20, 20, 40)
    TITLE_COLOR = (255, 255, 255)
    HEADER_COLOR = (200, 200, 255)
    SCORE_COLOR = (255, 255, 255)
    RANK_COLOR = (255, 215, 0)  # Gold
    TAB_ACTIVE = (80, 80, 120)
    TAB_INACTIVE = (40, 40, 60)
    TAB_HOVER = (100, 100, 140)

    def __init__(self):
        """Initialize leaderboard scene."""
        super().__init__()
        self.high_score_manager = HighScoreManager()

        # Current view state
        self.current_game = "ski"
        self.current_character = "danger"
        self.current_difficulty = "normal"

        # Fonts (will be initialized in on_enter)
        self.title_font = None
        self.header_font = None
        self.score_font = None

        # UI elements
        self.game_tabs = []
        self.character_tabs = []
        self.difficulty_tabs = []
        self.back_button = None

        # Animation
        self.score_animations = []
        self.highlight_rank = None  # Rank to highlight (for new high scores)

    def on_enter(
        self,
        previous_scene: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Enter the leaderboard scene.

        Args:
            previous_scene: Name of the previous scene
            data: Optional data including game mode, character, new score info
        """
        # Initialize fonts
        try:
            font_path = get_font_path("pixel")
            self.title_font = pygame.font.Font(font_path, self.TITLE_SIZE)
            self.header_font = pygame.font.Font(font_path, self.HEADER_SIZE)
            self.score_font = pygame.font.Font(font_path, self.SCORE_SIZE)
        except Exception:
            # Fallback to system font
            self.title_font = pygame.font.Font(None, self.TITLE_SIZE)
            self.header_font = pygame.font.Font(None, self.HEADER_SIZE)
            self.score_font = pygame.font.Font(None, self.SCORE_SIZE)

        # Setup UI elements
        self._setup_ui()

        # Process incoming data
        if data:
            if "game_mode" in data:
                self.current_game = data["game_mode"]
            if "character" in data:
                self.current_character = data["character"]
            if "difficulty" in data:
                self.current_difficulty = data["difficulty"]
            if "highlight_rank" in data:
                self.highlight_rank = data["highlight_rank"]
                self._start_highlight_animation()

    def _setup_ui(self) -> None:
        """Setup UI elements positions."""
        # Game mode tabs
        games = ["ski", "pool", "vegas"]
        tab_start_x = (SCREEN_WIDTH - len(games) * self.TAB_WIDTH) // 2

        self.game_tabs = []
        for i, game in enumerate(games):
            rect = pygame.Rect(
                tab_start_x + i * self.TAB_WIDTH, 100, self.TAB_WIDTH, self.TAB_HEIGHT
            )
            self.game_tabs.append((game, rect))

        # Character tabs
        characters = ["danger", "rose", "dad"]
        char_start_x = (SCREEN_WIDTH - len(characters) * self.TAB_WIDTH) // 2

        self.character_tabs = []
        for i, char in enumerate(characters):
            rect = pygame.Rect(
                char_start_x + i * self.TAB_WIDTH, 160, self.TAB_WIDTH, self.TAB_HEIGHT
            )
            self.character_tabs.append((char, rect))

        # Difficulty tabs
        difficulties = ["easy", "normal", "hard"]
        diff_start_x = (SCREEN_WIDTH - len(difficulties) * self.TAB_WIDTH) // 2

        self.difficulty_tabs = []
        for i, diff in enumerate(difficulties):
            rect = pygame.Rect(
                diff_start_x + i * self.TAB_WIDTH, 220, self.TAB_WIDTH, self.TAB_HEIGHT
            )
            self.difficulty_tabs.append((diff, rect))

        # Back button
        self.back_button = pygame.Rect(self.MARGIN, SCREEN_HEIGHT - 60, 150, 40)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Handle input events.

        Args:
            event: Pygame event to handle

        Returns:
            Next scene name if transitioning, None otherwise
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "main_menu"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()

                # Check back button
                if self.back_button.collidepoint(mouse_pos):
                    return "main_menu"

                # Check game tabs
                for game, rect in self.game_tabs:
                    if rect.collidepoint(mouse_pos):
                        self.current_game = game
                        break

                # Check character tabs
                for char, rect in self.character_tabs:
                    if rect.collidepoint(mouse_pos):
                        self.current_character = char
                        break

                # Check difficulty tabs
                for diff, rect in self.difficulty_tabs:
                    if rect.collidepoint(mouse_pos):
                        self.current_difficulty = diff
                        break

        return None

    def update(self, dt: float) -> None:
        """Update the leaderboard scene.

        Args:
            dt: Delta time in seconds
        """
        # Update score animations
        for anim in self.score_animations[:]:
            anim["time"] += dt
            if anim["time"] > anim["duration"]:
                self.score_animations.remove(anim)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the leaderboard scene.

        Args:
            screen: Screen surface to draw on
        """
        # Clear screen
        screen.fill(self.BG_COLOR)

        # Draw title
        title_text = self.title_font.render("HIGH SCORES", True, self.TITLE_COLOR)
        title_rect = title_text.get_rect(centerx=SCREEN_WIDTH // 2, y=20)
        screen.blit(title_text, title_rect)

        # Draw tabs
        self._draw_tabs(screen)

        # Draw leaderboard
        self._draw_leaderboard(screen)

        # Draw back button
        self._draw_back_button(screen)

    def _draw_tabs(self, screen: pygame.Surface) -> None:
        """Draw selection tabs."""
        mouse_pos = pygame.mouse.get_pos()

        # Game tabs
        for game, rect in self.game_tabs:
            color = self.TAB_ACTIVE if game == self.current_game else self.TAB_INACTIVE
            if rect.collidepoint(mouse_pos) and game != self.current_game:
                color = self.TAB_HOVER

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, self.HEADER_COLOR, rect, 2)

            text = self.header_font.render(game.upper(), True, self.HEADER_COLOR)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

        # Character tabs
        for char, rect in self.character_tabs:
            color = (
                self.TAB_ACTIVE if char == self.current_character else self.TAB_INACTIVE
            )
            if rect.collidepoint(mouse_pos) and char != self.current_character:
                color = self.TAB_HOVER

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, self.HEADER_COLOR, rect, 2)

            text = self.header_font.render(char.upper(), True, self.HEADER_COLOR)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

        # Difficulty tabs
        for diff, rect in self.difficulty_tabs:
            color = (
                self.TAB_ACTIVE
                if diff == self.current_difficulty
                else self.TAB_INACTIVE
            )
            if rect.collidepoint(mouse_pos) and diff != self.current_difficulty:
                color = self.TAB_HOVER

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, self.HEADER_COLOR, rect, 2)

            text = self.header_font.render(diff.upper(), True, self.HEADER_COLOR)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

    def _draw_leaderboard(self, screen: pygame.Surface) -> None:
        """Draw the leaderboard scores."""
        # Get scores
        scores = self.high_score_manager.get_leaderboard(
            self.current_game, self.current_character, self.current_difficulty
        )

        # Starting position
        start_y = 300

        # Draw header
        if self.current_game == "ski":
            header = "RANK    PLAYER           TIME"
        else:
            header = "RANK    PLAYER          SCORE"

        header_text = self.score_font.render(header, True, self.HEADER_COLOR)
        screen.blit(header_text, (SCREEN_WIDTH // 2 - 200, start_y - 40))

        # Draw scores
        for i, score_entry in enumerate(scores[:10]):
            y_pos = start_y + i * self.SCORE_SPACING

            # Highlight animation for new high score
            color = self.SCORE_COLOR
            x_offset = 0

            if self.highlight_rank == i + 1:
                # Pulsing effect
                for anim in self.score_animations:
                    if anim["type"] == "highlight":
                        progress = anim["time"] / anim["duration"]
                        pulse = abs(progress * 2 - 1)
                        color = self._blend_colors(
                            self.RANK_COLOR, self.SCORE_COLOR, pulse
                        )
                        x_offset = int(pulse * 10)

            # Rank
            rank_text = self.score_font.render(f"{i + 1}.", True, self.RANK_COLOR)
            screen.blit(rank_text, (SCREEN_WIDTH // 2 - 200 + x_offset, y_pos))

            # Player name
            name = score_entry.player_name[:12]  # Truncate long names
            name_text = self.score_font.render(name, True, color)
            screen.blit(name_text, (SCREEN_WIDTH // 2 - 120 + x_offset, y_pos))

            # Score/Time
            if self.current_game == "ski":
                score_str = f"{score_entry.score:.2f}s"
            else:
                score_str = f"{int(score_entry.score)}"

            score_text = self.score_font.render(score_str, True, color)
            screen.blit(score_text, (SCREEN_WIDTH // 2 + 80 + x_offset, y_pos))

        # Show empty message if no scores
        if not scores:
            empty_text = self.score_font.render(
                "No scores yet. Be the first!", True, self.HEADER_COLOR
            )
            empty_rect = empty_text.get_rect(centerx=SCREEN_WIDTH // 2, y=start_y + 50)
            screen.blit(empty_text, empty_rect)

    def _draw_back_button(self, screen: pygame.Surface) -> None:
        """Draw the back button."""
        mouse_pos = pygame.mouse.get_pos()
        color = (
            self.TAB_HOVER
            if self.back_button.collidepoint(mouse_pos)
            else self.TAB_INACTIVE
        )

        pygame.draw.rect(screen, color, self.back_button)
        pygame.draw.rect(screen, self.HEADER_COLOR, self.back_button, 2)

        text = self.header_font.render("BACK", True, self.HEADER_COLOR)
        text_rect = text.get_rect(center=self.back_button.center)
        screen.blit(text, text_rect)

    def _start_highlight_animation(self) -> None:
        """Start animation for highlighting a new high score."""
        self.score_animations.append({"type": "highlight", "time": 0, "duration": 2.0})

    def _blend_colors(
        self, color1: tuple[int, int, int], color2: tuple[int, int, int], factor: float
    ) -> tuple[int, int, int]:
        """Blend two colors together.

        Args:
            color1: First color
            color2: Second color
            factor: Blend factor (0-1)

        Returns:
            Blended color
        """
        return tuple(
            int(c1 * (1 - factor) + c2 * factor)
            for c1, c2 in zip(color1, color2, strict=False)
        )

    def on_exit(self) -> dict[str, Any]:
        """Clean up when leaving the scene.

        Returns:
            Any data to pass to the next scene
        """
        return {}
