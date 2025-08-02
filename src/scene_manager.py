import logging

import pygame

from src.config.constants import (
    SCENE_HUB_WORLD,
    SCENE_LEADERBOARD,
    SCENE_NAME_ENTRY,
    SCENE_PAUSE,
    SCENE_POOL_GAME,
    SCENE_SETTINGS,
    SCENE_SKI_GAME,
    SCENE_TITLE,
    SCENE_VEGAS_GAME,
    SCENE_DRIVE_GAME,
    SCENE_HACKER_TYPING,
)
from src.managers.sound_manager import SoundManager
from src.scenes.hub import HubWorld
from src.scenes.leaderboard import LeaderboardScene
from src.scenes.name_entry import NameEntryScene
from src.scenes.pause_menu import PauseMenu
from src.scenes.pool import PoolGame
from src.scenes.settings import SettingsScene
from src.scenes.ski import SkiGame
from src.scenes.title_screen import TitleScreen
from src.scenes.vegas import VegasGame
from src.scenes.drive import DriveGame
from src.scenes.hacker_typing import HackerTypingScene
from src.utils.asset_paths import get_music_path
from src.utils.save_manager import SaveManager

logger = logging.getLogger(__name__)


class SceneManager:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_scene = None
        self.scenes = {}
        self.game_data = {"selected_character": None}
        self.paused = False
        self.paused_scene_name = None
        self.pause_allowed_scenes = [
            SCENE_HUB_WORLD,
            SCENE_VEGAS_GAME,
            SCENE_SKI_GAME,
            SCENE_POOL_GAME,
            SCENE_DRIVE_GAME,
        ]

        # Initialize sound manager
        self.sound_manager = SoundManager()

        # Initialize save manager and load save data
        self.save_manager = SaveManager()
        self._load_game_data()

        # Initialize scenes
        self.scenes[SCENE_TITLE] = TitleScreen(
            screen_width, screen_height, self.sound_manager
        )
        self.scenes[SCENE_SETTINGS] = SettingsScene(
            screen_width, screen_height, self.sound_manager
        )
        self.scenes[SCENE_HUB_WORLD] = HubWorld(self)
        self.scenes[SCENE_VEGAS_GAME] = VegasGame(self)
        self.scenes[SCENE_SKI_GAME] = SkiGame(self)
        self.scenes[SCENE_POOL_GAME] = PoolGame(self)
        self.scenes[SCENE_DRIVE_GAME] = DriveGame(self)
        self.scenes[SCENE_HACKER_TYPING] = HackerTypingScene(self)
        self.scenes[SCENE_PAUSE] = PauseMenu(
            screen_width, screen_height, self.sound_manager
        )
        self.scenes[SCENE_LEADERBOARD] = LeaderboardScene()
        self.scenes[SCENE_NAME_ENTRY] = NameEntryScene()
        self.current_scene = self.scenes[SCENE_TITLE]

        # Start title music
        self.sound_manager.play_music(get_music_path("title_theme.ogg"), fade_ms=1000)

    def handle_event(self, event):
        # Handle ESC key for pause (only in allowed scenes)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            current_scene_name = self._get_current_scene_name()
            if current_scene_name in self.pause_allowed_scenes and not self.paused:
                self.pause_game()
                return

        if self.current_scene:
            result = self.current_scene.handle_event(event)

            # Get previous scene name for checking
            previous_scene_name = self._get_current_scene_name()

            # Handle pause menu results
            if self.paused and result:
                if result == "resume":
                    self.resume_game()
                elif result == "quit":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif result == SCENE_TITLE:
                    self.resume_game()
                    self.switch_scene(SCENE_TITLE)
                elif result == SCENE_SETTINGS:
                    # Don't resume yet, let settings handle the return
                    self.switch_scene(SCENE_SETTINGS)
                return

            # Handle scene transitions
            if result == "start_game":
                self.game_data["selected_character"] = (
                    self.current_scene.selected_character
                )
                # Transition to hub world
                self.switch_scene(SCENE_HUB_WORLD)
            elif result == "vegas":
                self.switch_scene(SCENE_VEGAS_GAME)
            elif result == "ski":
                self.switch_scene(SCENE_SKI_GAME)
            elif result == "pool":
                self.switch_scene(SCENE_POOL_GAME)
            elif result == "drive":
                self.switch_scene(SCENE_DRIVE_GAME)
            elif result == "hacker_typing":
                self.switch_scene(SCENE_HACKER_TYPING)
            elif (
                result in self.pause_allowed_scenes
                and previous_scene_name == SCENE_SETTINGS
            ):
                # Returning from settings to a paused game
                self.paused = False
                self.paused_scene_name = None
                self.switch_scene(result)
            elif result:
                # Handle other scene transitions
                self.switch_scene(result)

    def update(self, dt: float):
        if self.current_scene:
            # Only update pause menu when paused, not the underlying scene
            if self.paused:
                self.scenes[SCENE_PAUSE].update(dt)
            else:
                self.current_scene.update(dt)

    def draw(self, screen):
        if self.current_scene:
            self.current_scene.draw(screen)

    def switch_scene(self, scene_name: str):
        if scene_name in self.scenes:
            previous_scene_name = None
            data = {}

            # Call on_exit for the current scene if it has the method
            if self.current_scene:
                for name, scene in self.scenes.items():
                    if scene == self.current_scene:
                        previous_scene_name = name
                        break
                if hasattr(self.current_scene, "on_exit"):
                    data = self.current_scene.on_exit()

            # Special handling for settings from pause menu
            if scene_name == SCENE_SETTINGS and self.paused:
                self.scenes[SCENE_SETTINGS].paused_scene = self.paused_scene_name
                # Don't clear pause state yet

            # Auto-save when transitioning between gameplay scenes
            if previous_scene_name not in [SCENE_TITLE, SCENE_SETTINGS, SCENE_PAUSE]:
                self._auto_save()

            # Switch to the new scene
            self.current_scene = self.scenes[scene_name]

            # Call on_enter for the new scene if it has the method
            if hasattr(self.current_scene, "on_enter"):
                self.current_scene.on_enter(previous_scene_name, data)

            # Handle music transitions
            self._handle_music_transition(scene_name)

    def _handle_music_transition(self, scene_name: str):
        """Handle music transitions between scenes."""
        music_map = {
            SCENE_TITLE: "title_theme.ogg",
            SCENE_HUB_WORLD: "hub_theme.ogg",
            SCENE_SKI_GAME: "ski_theme.ogg",
            SCENE_VEGAS_GAME: "vegas_theme.ogg",
            SCENE_POOL_GAME: "pool_theme.ogg",
        }

        if scene_name in music_map:
            music_file = get_music_path(music_map[scene_name])
            self.sound_manager.crossfade_music(music_file, duration_ms=1000)

    def _load_game_data(self):
        """Load saved game data from disk."""
        save_data = self.save_manager.load()

        # Apply saved settings
        self.sound_manager.set_master_volume(save_data["settings"]["master_volume"])
        self.sound_manager.set_music_volume(save_data["settings"]["music_volume"])
        self.sound_manager.set_sfx_volume(save_data["settings"]["sfx_volume"])

        # Restore game data
        self.game_data["selected_character"] = save_data["player"]["selected_character"]

        logger.info("Game data loaded successfully")

    def _auto_save(self):
        """Automatically save game progress."""
        try:
            # Update save data with current game state
            self.save_manager.set_selected_character(
                self.game_data.get("selected_character")
            )

            # Save to disk
            if self.save_manager.save():
                logger.info("Auto-save completed")
            else:
                logger.warning("Auto-save failed")
        except Exception as e:
            logger.error(f"Error during auto-save: {e}")

    def save_game(self):
        """Manually save the game."""
        self._auto_save()

    def get_save_manager(self):
        """Get the save manager instance for other components to use."""
        return self.save_manager

    def _get_current_scene_name(self):
        """Get the name of the current scene."""
        for name, scene in self.scenes.items():
            if scene == self.current_scene:
                return name
        return None

    def pause_game(self):
        """Pause the current game scene and show pause menu."""
        if self.paused:
            return

        # Store the current scene name
        self.paused_scene_name = self._get_current_scene_name()

        # Create a surface with the current frame
        screen = pygame.display.get_surface()
        paused_surface = screen.copy()

        # Set up the pause menu with the paused scene info
        self.scenes[SCENE_PAUSE].set_paused_scene(self.current_scene, paused_surface)

        # Switch to pause menu (without triggering auto-save)
        self.paused = True
        self.current_scene = self.scenes[SCENE_PAUSE]

        logger.info(f"Game paused from scene: {self.paused_scene_name}")

    def resume_game(self):
        """Resume the paused game scene."""
        if not self.paused or not self.paused_scene_name:
            return

        # Return to the paused scene
        self.current_scene = self.scenes[self.paused_scene_name]
        self.paused = False

        logger.info(f"Game resumed to scene: {self.paused_scene_name}")
        self.paused_scene_name = None
