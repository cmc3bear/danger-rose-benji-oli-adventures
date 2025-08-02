"""Hub world scene - the main apartment area."""

from datetime import datetime
from typing import Any

import pygame

from src.config.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from src.entities.couch import Couch
from src.entities.door import Door
from src.entities.player import Player
from src.entities.trophy_shelf import TrophyShelf
from src.ui.notification import SaveNotification
from src.utils.asset_paths import get_living_room_bg, get_sfx_path
from src.utils.high_score_manager import HighScoreManager


class HubWorld:
    """The main hub world scene where players navigate the apartment."""

    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Load background
        try:
            self.background = pygame.image.load(get_living_room_bg())
            self.background = pygame.transform.scale(
                self.background, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except (pygame.error, FileNotFoundError):
            # Create a simple background if image fails to load
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((50, 30, 20))  # Dark brown color

        # Define room boundaries (for future collision detection)
        self._setup_boundaries()

        # Get selected character from game data
        self.selected_character = self.scene_manager.game_data.get(
            "selected_character", "danger"
        )

        # Create player entity
        # Start player in center of room
        self.player = Player(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.selected_character
        )

        # Initialize high score manager and trophy shelf
        self.high_score_manager = HighScoreManager(self.scene_manager.save_manager)
        self.trophy_shelf = TrophyShelf(100, 200, self.high_score_manager)

    def _setup_boundaries(self):
        """Set up room boundaries and collision areas."""
        # Room boundaries (walls)
        self.boundaries = [
            pygame.Rect(0, 0, SCREEN_WIDTH, 50),  # Top wall
            pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),  # Bottom wall
            pygame.Rect(0, 0, 50, SCREEN_HEIGHT),  # Left wall
            pygame.Rect(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT),  # Right wall
        ]

        # Create door objects
        self.doors = [
            Door(200, 100, 100, 150, "ski", "Ski Game", (100, 150, 255)),
            Door(400, 100, 100, 150, "pool", "Pool Game", (50, 200, 100)),
            Door(600, 100, 100, 150, "vegas", "Vegas Game", (200, 50, 200)),
            Door(800, 100, 100, 150, "drive", "The Drive", (255, 100, 50)),
        ]

        # Track which door is highlighted
        self.highlighted_door = None

        # Other interactive areas - removed since trophy_shelf handles its own rect

        # Create couch save point
        self.couch = Couch(350, 400)

        # Save notification
        self.save_notification = SaveNotification(self.font, self.small_font)

    def handle_event(self, event) -> str | None:
        """Handle input events."""
        # Let player handle movement events
        self.player.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "settings"
            if event.key == pygame.K_e:
                # Check if player is near trophy shelf
                if self.trophy_shelf.is_highlighted:
                    if self.trophy_shelf.show_popup:
                        # Close popup if already showing
                        self.trophy_shelf.show_popup = False
                    else:
                        # Show trophy stats popup
                        self.trophy_shelf.show_stats_popup(self.selected_character)
                # Check if player is near couch
                elif self.couch.is_highlighted:
                    # Save the game
                    self.scene_manager.save_game()
                    self.couch.trigger_save()
                    self.save_notification.show()
                    self.scene_manager.sound_manager.play_sfx(
                        get_sfx_path("collect_item.ogg")
                    )
                # Check if player is near any door
                elif self.highlighted_door:
                    self.scene_manager.sound_manager.play_sfx(
                        get_sfx_path("door_open.wav")
                    )
                    return self.highlighted_door.target_scene
            elif event.key == pygame.K_TAB:
                # Check if player is near couch for settings access
                if self.couch.is_highlighted:
                    return "settings"

        return None

    def update(self, dt: float) -> None:
        """Update the hub world state."""
        # Update player with collision boundaries
        self.player.update(dt, self.boundaries)

        # Check door proximity for highlighting
        self.highlighted_door = None
        for door in self.doors:
            door.is_highlighted = False
            if door.check_player_proximity(self.player.rect):
                door.is_highlighted = True
                self.highlighted_door = door

        # Check couch proximity
        self.couch.is_highlighted = self.couch.check_player_proximity(self.player.rect)

        # Check trophy shelf proximity
        self.trophy_shelf.is_highlighted = self.trophy_shelf.check_player_proximity(
            self.player.rect
        )

        # Update couch animation
        self.couch.update(dt)

        # Update trophy shelf
        self.trophy_shelf.update(dt, self.selected_character)

        # Update save notification
        self.save_notification.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the hub world."""
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw temporary UI elements
        title_text = self.font.render("Hub World", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_text, title_rect)

        # Draw doors
        for door in self.doors:
            door.draw(screen, self.small_font)

        # Draw couch
        self.couch.draw(screen, self.small_font)

        # Draw trophy shelf
        self.trophy_shelf.draw(
            screen, self.font, self.small_font, self.selected_character
        )

        # Draw player
        self.player.draw(screen)

        # Draw selected character info
        if self.selected_character:
            char_text = self.small_font.render(
                f"Playing as: {self.selected_character}", True, (255, 255, 255)
            )
            char_rect = char_text.get_rect(topleft=(20, 20))
            screen.blit(char_text, char_rect)

        # Draw instructions
        instructions = [
            "Arrow keys or WASD - Move",
            "E - Enter door",
            "ESC - Settings",
        ]
        y_offset = SCREEN_HEIGHT - 140
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, (255, 255, 255))
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(inst_text, inst_rect)
            y_offset += 25

        # Draw save notification (on top of everything)
        self.save_notification.draw(screen)

        # Draw last save time in corner
        last_save_time = self.scene_manager.save_manager.get_last_save_time()
        if last_save_time:
            # Calculate time ago
            now = datetime.now()
            time_diff = now - last_save_time

            if time_diff.total_seconds() < 60:
                time_str = "Just now"
            elif time_diff.total_seconds() < 3600:
                minutes = int(time_diff.total_seconds() / 60)
                time_str = f"{minutes} min ago"
            else:
                time_str = last_save_time.strftime("%I:%M %p")

            save_text = self.small_font.render(
                f"Last save: {time_str}", True, (200, 200, 200)
            )
            save_rect = save_text.get_rect(
                bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
            )
            screen.blit(save_text, save_rect)

    def on_enter(self, previous_scene: str | None, data: dict[str, Any]) -> None:
        """Called when entering the hub world."""
        # Update selected character if coming from character select
        if previous_scene == "character_select" and data.get("selected_character"):
            self.selected_character = data["selected_character"]
            self.scene_manager.game_data["selected_character"] = self.selected_character

            # Recreate player with new character
            self.player = Player(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.selected_character
            )

            # Update trophy shelf with new character data
            self.trophy_shelf = TrophyShelf(100, 200, self.high_score_manager)

    def on_exit(self) -> dict[str, Any]:
        """Called when leaving the hub world."""
        return {"from_scene": "hub"}
