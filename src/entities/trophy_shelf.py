"""Trophy shelf entity for displaying achievements and high scores."""

from typing import Any

import pygame

from src.config.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from src.effects.trophy_particles import TrophyParticleEffect
from src.utils.high_score_manager import HighScoreManager
from src.utils.sprite_loader import load_image


class TrophyLevel:
    """Trophy achievement levels."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class TrophyShelf:
    """Interactive trophy shelf that displays achievements and high scores."""

    def __init__(self, x: int, y: int, high_score_manager: HighScoreManager):
        """Initialize trophy shelf.

        Args:
            x: X position of the shelf
            y: Y position of the shelf
            high_score_manager: HighScoreManager instance for score data
        """
        self.x = x
        self.y = y
        self.width = 300
        self.height = 200
        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.high_score_manager = high_score_manager
        self.is_highlighted = False
        self.show_popup = False
        self.popup_timer = 0.0

        # Load shelf sprite using proper asset path function
        from src.utils.asset_paths import get_image_path

        self.shelf_sprite = load_image(
            get_image_path("furniture/trophy_shelf.png"), (self.width, self.height)
        )

        # Load trophy sprites
        self.trophy_sprites = {
            TrophyLevel.BRONZE: load_image(
                get_image_path("trophies/bronze_trophy.png"), (32, 48)
            ),
            TrophyLevel.SILVER: load_image(
                get_image_path("trophies/silver_trophy.png"), (32, 48)
            ),
            TrophyLevel.GOLD: load_image(
                get_image_path("trophies/gold_trophy.png"), (32, 48)
            ),
        }

        # Trophy positions on shelf (relative to shelf position)
        self.trophy_positions = [
            (50, 120),  # Ski game trophies
            (150, 120),  # Pool game trophies
            (250, 120),  # Vegas game trophies
        ]

        # Game modes corresponding to trophy positions
        self.game_modes = ["ski", "pool", "vegas"]

        # Particle effects system
        self.particle_effect = TrophyParticleEffect()
        self.last_trophy_levels = {}  # Track trophy levels to detect new achievements

        # Score thresholds for trophy levels
        self.score_thresholds = {
            "ski": {
                TrophyLevel.BRONZE: 120.0,  # 2 minutes
                TrophyLevel.SILVER: 90.0,  # 1.5 minutes
                TrophyLevel.GOLD: 60.0,  # 1 minute
            },
            "pool": {
                TrophyLevel.BRONZE: 500,
                TrophyLevel.SILVER: 1000,
                TrophyLevel.GOLD: 2000,
            },
            "vegas": {
                TrophyLevel.BRONZE: 1000,
                TrophyLevel.SILVER: 2500,
                TrophyLevel.GOLD: 5000,
            },
        }

    def check_player_proximity(self, player_rect: pygame.Rect) -> bool:
        """Check if player is close enough to interact with trophy shelf.

        Args:
            player_rect: Player's collision rectangle

        Returns:
            True if player is within interaction range
        """
        return self.rect.colliderect(player_rect.inflate(20, 20))

    def get_trophy_level(self, game_mode: str, character: str) -> str | None:
        """Get the highest trophy level achieved for a game/character.

        Args:
            game_mode: Game mode (ski, pool, vegas)
            character: Character name

        Returns:
            Trophy level (bronze, silver, gold) or None if no trophy earned
        """
        # Get best score across all difficulties
        leaderboard = self.high_score_manager.get_leaderboard(game_mode, character)

        if not leaderboard:
            return None

        best_score = leaderboard[0].score
        thresholds = self.score_thresholds.get(game_mode, {})

        # Check from highest to lowest
        for level in [TrophyLevel.GOLD, TrophyLevel.SILVER, TrophyLevel.BRONZE]:
            threshold = thresholds.get(level)
            if threshold is None:
                continue

            if game_mode == "ski":
                # Lower time is better
                if best_score <= threshold:
                    return level
            # Higher score is better
            elif best_score >= threshold:
                return level

        return None

    def get_trophy_stats(self, game_mode: str, character: str) -> dict[str, Any]:
        """Get detailed statistics for a game/character combination.

        Args:
            game_mode: Game mode
            character: Character name

        Returns:
            Dictionary with detailed stats
        """
        leaderboard = self.high_score_manager.get_leaderboard(game_mode, character)
        trophy_level = self.get_trophy_level(game_mode, character)

        stats = {
            "game_mode": game_mode,
            "character": character,
            "trophy_level": trophy_level,
            "best_score": leaderboard[0].score if leaderboard else 0,
            "total_games": len(leaderboard),
            "last_played": leaderboard[0].date if leaderboard else None,
        }

        return stats

    def update(self, dt: float, selected_character: str) -> None:
        """Update trophy shelf state.

        Args:
            dt: Delta time in seconds
            selected_character: Currently selected character
        """
        if self.show_popup:
            self.popup_timer += dt
            # Hide popup after 5 seconds
            if self.popup_timer > 5.0:
                self.show_popup = False
                self.popup_timer = 0.0

        # Update particle effects
        self.particle_effect.update(dt)

        # Check for new trophy achievements and create celebration effects
        self._check_new_achievements(selected_character)

    def show_stats_popup(self, selected_character: str) -> None:
        """Show the detailed stats popup.

        Args:
            selected_character: Currently selected character
        """
        self.show_popup = True
        self.popup_timer = 0.0
        self.selected_character = selected_character

    def draw(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        selected_character: str,
    ) -> None:
        """Draw the trophy shelf and trophies.

        Args:
            screen: Surface to draw on
            font: Main font for text
            small_font: Small font for details
            selected_character: Currently selected character
        """
        # Draw shelf background
        screen.blit(self.shelf_sprite, (self.x, self.y))

        # Draw shelf outline if highlighted
        if self.is_highlighted:
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)

        # Draw title
        title_text = small_font.render("Trophy Shelf", True, (255, 255, 255))
        title_rect = title_text.get_rect(
            centerx=self.x + self.width // 2, y=self.y - 30
        )
        screen.blit(title_text, title_rect)

        # Draw trophies for each game
        for i, game_mode in enumerate(self.game_modes):
            trophy_level = self.get_trophy_level(game_mode, selected_character)
            pos_x, pos_y = self.trophy_positions[i]

            # Draw trophy if earned
            if trophy_level:
                trophy_sprite = self.trophy_sprites[trophy_level]
                screen.blit(trophy_sprite, (self.x + pos_x - 16, self.y + pos_y - 24))
            else:
                # Draw empty trophy placeholder
                placeholder_rect = pygame.Rect(
                    self.x + pos_x - 16, self.y + pos_y - 24, 32, 48
                )
                pygame.draw.rect(screen, (64, 64, 64), placeholder_rect)
                pygame.draw.rect(screen, (128, 128, 128), placeholder_rect, 2)

            # Draw game label
            game_label = small_font.render(game_mode.title(), True, (200, 200, 200))
            label_rect = game_label.get_rect(
                centerx=self.x + pos_x, y=self.y + pos_y + 30
            )
            screen.blit(game_label, label_rect)

            # Draw high score below trophy
            leaderboard = self.high_score_manager.get_leaderboard(
                game_mode, selected_character
            )
            if leaderboard:
                best_score = leaderboard[0].score
                if game_mode == "ski":
                    score_text = f"{best_score:.1f}s"
                else:
                    score_text = f"{int(best_score)}"

                score_surface = small_font.render(score_text, True, (255, 255, 0))
                score_rect = score_surface.get_rect(
                    centerx=self.x + pos_x, y=self.y + pos_y + 50
                )
                screen.blit(score_surface, score_rect)

        # Draw interaction prompt if highlighted
        if self.is_highlighted:
            prompt_text = small_font.render(
                "Press [E] to view stats", True, (255, 255, 255)
            )
            prompt_rect = prompt_text.get_rect(
                centerx=self.x + self.width // 2, y=self.y + self.height + 10
            )
            screen.blit(prompt_text, prompt_rect)

        # Draw particle effects
        self.particle_effect.draw(screen)

        # Draw detailed popup if shown
        if self.show_popup:
            self._draw_stats_popup(screen, font, small_font, selected_character)

    def _draw_stats_popup(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        selected_character: str,
    ) -> None:
        """Draw the detailed statistics popup.

        Args:
            screen: Surface to draw on
            font: Main font
            small_font: Small font for details
            selected_character: Currently selected character
        """
        # Popup dimensions and position
        popup_width = 400
        popup_height = 300
        popup_x = (SCREEN_WIDTH - popup_width) // 2
        popup_y = (SCREEN_HEIGHT - popup_height) // 2

        # Draw popup background
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(screen, (40, 40, 60), popup_rect)
        pygame.draw.rect(screen, (255, 255, 255), popup_rect, 3)

        # Title
        title_text = font.render(
            f"{selected_character.title()}'s Achievements", True, (255, 255, 255)
        )
        title_rect = title_text.get_rect(
            centerx=popup_x + popup_width // 2, y=popup_y + 20
        )
        screen.blit(title_text, title_rect)

        # Draw stats for each game
        y_offset = 70
        for game_mode in self.game_modes:
            stats = self.get_trophy_stats(game_mode, selected_character)

            # Game title
            game_title = small_font.render(f"{game_mode.title()}:", True, (255, 255, 0))
            screen.blit(game_title, (popup_x + 30, popup_y + y_offset))

            # Trophy level
            trophy_level = stats["trophy_level"] or "None"
            trophy_text = small_font.render(
                f"Trophy: {trophy_level.title()}", True, (200, 200, 200)
            )
            screen.blit(trophy_text, (popup_x + 150, popup_y + y_offset))

            # Best score
            best_score = stats["best_score"]
            if best_score > 0:
                if game_mode == "ski":
                    score_text = f"Best: {best_score:.1f}s"
                else:
                    score_text = f"Best: {int(best_score)}"
            else:
                score_text = "Best: No scores"

            score_surface = small_font.render(score_text, True, (200, 200, 200))
            screen.blit(score_surface, (popup_x + 270, popup_y + y_offset))

            y_offset += 30

        # Close instruction
        close_text = small_font.render(
            "Press [E] or wait to close", True, (150, 150, 150)
        )
        close_rect = close_text.get_rect(
            centerx=popup_x + popup_width // 2, y=popup_y + popup_height - 30
        )
        screen.blit(close_text, close_rect)

    def _check_new_achievements(self, selected_character: str) -> None:
        """Check for new trophy achievements and trigger celebration effects.

        Args:
            selected_character: Currently selected character
        """
        for i, game_mode in enumerate(self.game_modes):
            current_level = self.get_trophy_level(game_mode, selected_character)
            key = f"{game_mode}_{selected_character}"
            previous_level = self.last_trophy_levels.get(key)

            # If we have a new trophy level, trigger celebration
            if current_level and current_level != previous_level:
                pos_x, pos_y = self.trophy_positions[i]
                trophy_x = self.x + pos_x
                trophy_y = self.y + pos_y - 24  # Adjust for trophy sprite position

                self.particle_effect.create_trophy_celebration(
                    trophy_x, trophy_y, current_level
                )

            # Update last known level
            self.last_trophy_levels[key] = current_level
