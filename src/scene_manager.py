import logging
import time
from pathlib import Path
from typing import Dict, Any

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
from src.systems.game_state_logger import get_global_logger
from src.systems.oqe_metric_collector import OQEMetricCollector
from src.ui.live_testing_overlay import LiveTestingOverlay
from src.testing.test_plan_loader import TestPlanLoader
from src.ui.universal_music_selector import UniversalMusicSelector
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
        
        # Initialize logging and testing systems
        self.game_logger = get_global_logger()
        self.oqe_collector = OQEMetricCollector()
        self.testing_overlay = LiveTestingOverlay(screen_width, screen_height)
        self.test_plan_loader = TestPlanLoader(str(Path(__file__).parent.parent))
        
        # Music selection system
        self.music_selector = None
        self.pending_scene = None
        self.in_music_selection = False
        self.scene_music_preferences = {}  # Store selected music per scene
        
        # Scenes that should have music selection
        self.music_enabled_scenes = [
            SCENE_HUB_WORLD,
            SCENE_POOL_GAME,
            SCENE_SKI_GAME,
            SCENE_VEGAS_GAME,
            SCENE_DRIVE_GAME,
            SCENE_HACKER_TYPING
        ]
        
        # Auto-load test procedures for Issue #34 (logging system) by default
        self.load_test_procedures_for_issue(34)
        
        # Performance tracking
        self.last_fps_measurement = time.time()
        self.fps_measurement_interval = 1.0  # Measure FPS every second

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
        # Let testing overlay handle events first
        if self.testing_overlay.handle_event(event):
            return
        
        # Handle music selection if active
        if self.in_music_selection and self.music_selector:
            result = self.music_selector.handle_event(event)
            if result == "track_selected":
                # Music selected, proceed to scene
                selected_track = self.music_selector.get_selected_track()
                self._complete_scene_transition(self.pending_scene, selected_track)
                return
            elif result == "skip_music":
                # Skip music selection, proceed to scene
                self._complete_scene_transition(self.pending_scene, None)
                return
            # If no result, continue with music selection
            return
        
        # Log input events
        if self.game_logger:
            self.game_logger.log_player_action(
                action=f"input_{event.type}",
                details={
                    "event_type": event.type,
                    "key": getattr(event, 'key', None),
                    "button": getattr(event, 'button', None),
                    "pos": getattr(event, 'pos', None)
                }
            )

        # Handle ESC key for pause (only in allowed scenes)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            current_scene_name = self._get_current_scene_name()
            if current_scene_name in self.pause_allowed_scenes and not self.paused:
                self.pause_game()
                return

        if self.current_scene:
            action_start_time = time.perf_counter()
            result = self.current_scene.handle_event(event)
            
            # Log response time for UI interactions
            if result and self.game_logger:
                response_time = self.oqe_collector.measure_response_time("scene_action", action_start_time)
                self.game_logger.log_performance_metric("response_time", response_time, {
                    "action": result,
                    "scene": self._get_current_scene_name()
                })

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
        # Update testing overlay
        self.testing_overlay.update(dt)
        
        # Update music selector if active
        if self.in_music_selection and self.music_selector:
            self.music_selector.update(dt)
            return
        
        # Periodic performance measurements
        current_time = time.time()
        if current_time - self.last_fps_measurement >= self.fps_measurement_interval:
            self._measure_performance()
            self.last_fps_measurement = current_time
        
        if self.current_scene:
            # Only update pause menu when paused, not the underlying scene
            if self.paused:
                self.scenes[SCENE_PAUSE].update(dt)
            else:
                self.current_scene.update(dt)

    def draw(self, screen):
        # Draw music selector if active
        if self.in_music_selection and self.music_selector:
            self.music_selector.draw(screen)
        elif self.current_scene:
            self.current_scene.draw(screen)
            
        # Draw testing overlay last (on top)
        self.testing_overlay.draw(screen)

    def switch_scene(self, scene_name: str):
        if scene_name in self.scenes:
            # Check if this scene should have music selection
            if scene_name in self.music_enabled_scenes:
                self._start_music_selection(scene_name)
                return
            
            # Proceed with immediate scene transition
            self._perform_scene_transition(scene_name)
    
    def _start_music_selection(self, scene_name: str):
        """Start music selection for a scene."""
        self.pending_scene = scene_name
        self.in_music_selection = True
        
        # Map scene names to music folder names
        music_scene_map = {
            SCENE_HUB_WORLD: "hub",
            SCENE_POOL_GAME: "pool", 
            SCENE_SKI_GAME: "ski",
            SCENE_VEGAS_GAME: "vegas",
            SCENE_DRIVE_GAME: "drive",
            SCENE_HACKER_TYPING: "hacker_typing"
        }
        
        music_scene_name = music_scene_map.get(scene_name, scene_name.lower())
        self.music_selector = UniversalMusicSelector(
            self.screen_width,
            self.screen_height, 
            self.sound_manager,
            music_scene_name
        )
        
        if self.game_logger:
            self.game_logger.log_audio_event(
                audio_action="music_selection_started",
                track="none",
                details={
                    "target_scene": scene_name,
                    "music_scene": music_scene_name
                }
            )
    
    def _complete_scene_transition(self, scene_name: str, selected_track):
        """Complete scene transition after music selection."""
        self.in_music_selection = False
        if self.music_selector:
            self.music_selector.cleanup()
            self.music_selector = None
        self.pending_scene = None
        
        # Store selected music for the scene
        if selected_track:
            self._set_scene_music(scene_name, selected_track)
        
        # Perform the actual scene transition
        self._perform_scene_transition(scene_name)
    
    def _perform_scene_transition(self, scene_name: str):
        """Perform the actual scene transition."""
        if scene_name in self.scenes:
            transition_start = time.time()
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
            
            # Log scene transition
            if self.game_logger and previous_scene_name:
                memory_data = self.oqe_collector.measure_memory(scene_name)
                self.game_logger.log_scene_transition(
                    from_scene=previous_scene_name,
                    to_scene=scene_name,
                    data={
                        "transition_data": data,
                        "memory_before_mb": memory_data["current_memory_mb"],
                        "memory_delta_mb": memory_data["memory_delta_mb"]
                    }
                )

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
    
    def _set_scene_music(self, scene_name: str, track):
        """Store selected music track for a scene."""
        self.scene_music_preferences[scene_name] = track
        
        if self.game_logger:
            self.game_logger.log_audio_event(
                audio_action="scene_music_preference_stored",
                track=track.filename if track else "none",
                details={
                    "scene": scene_name,
                    "track_name": track.name if track else "none",
                    "mood": track.mood if track else "none"
                }
            )
    
    def _get_scene_music(self, scene_name: str):
        """Get stored music track for a scene."""
        return self.scene_music_preferences.get(scene_name)

    def _handle_music_transition(self, scene_name: str):
        """Handle music transitions between scenes."""
        # Check if user selected a specific track for this scene
        selected_track = self._get_scene_music(scene_name)
        
        music_file = None
        track_name = "none"
        
        if selected_track:
            # Use user-selected track
            scene_folder_map = {
                SCENE_HUB_WORLD: "hub",
                SCENE_POOL_GAME: "pool",
                SCENE_SKI_GAME: "ski", 
                SCENE_VEGAS_GAME: "vegas",
                SCENE_DRIVE_GAME: "drive",
                SCENE_HACKER_TYPING: "hacker_typing"
            }
            
            folder = scene_folder_map.get(scene_name)
            if folder:
                music_file = get_music_path(f"{folder}/{selected_track.filename}")
                track_name = selected_track.filename
        else:
            # Fall back to default music
            default_music_map = {
                SCENE_TITLE: "title_theme.ogg",
                SCENE_HUB_WORLD: "hub_theme.ogg",
                SCENE_SKI_GAME: "ski_theme.ogg",
                SCENE_VEGAS_GAME: "vegas_theme.ogg",
                SCENE_POOL_GAME: "pool_theme.ogg",
            }
            
            if scene_name in default_music_map:
                music_file = get_music_path(default_music_map[scene_name])
                track_name = default_music_map[scene_name]

        if music_file:
            # Log audio transition
            if self.game_logger:
                self.game_logger.log_audio_event(
                    audio_action="music_crossfade",
                    track=track_name,
                    details={
                        "scene": scene_name,
                        "crossfade_duration_ms": 1000,
                        "file_path": str(music_file),
                        "user_selected": selected_track is not None
                    }
                )
            
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
    
    def _measure_performance(self):
        """Measure current performance metrics."""
        if not self.game_logger:
            return
        
        current_scene_name = self._get_current_scene_name()
        
        # Measure FPS
        fps_data = self.oqe_collector.measure_fps(current_scene_name)
        self.game_logger.log_performance_metric("fps", fps_data["current_fps"], fps_data)
        
        # Measure memory usage
        memory_data = self.oqe_collector.measure_memory(current_scene_name)
        self.game_logger.log_performance_metric("memory", memory_data["current_memory_mb"], memory_data)
    
    def load_test_procedures_for_issue(self, issue_number: int):
        """Load and activate test procedures for a specific issue."""
        try:
            procedures = self.test_plan_loader.load_issue_test_plan(issue_number)
            for procedure in procedures:
                self.testing_overlay.add_test_procedure(procedure)
            
            if self.game_logger:
                self.game_logger.log_system_event("testing", "procedures_loaded", {
                    "issue_number": issue_number,
                    "procedure_count": len(procedures)
                })
            
            logger.info(f"Loaded {len(procedures)} test procedures for issue #{issue_number}")
            return procedures
        except Exception as e:
            logger.error(f"Failed to load test procedures for issue #{issue_number}: {e}")
            return []
    
    def get_testing_overlay(self) -> LiveTestingOverlay:
        """Get the live testing overlay instance."""
        return self.testing_overlay
    
    def get_performance_impact_report(self) -> Dict[str, Any]:
        """Get performance impact report for the logging system."""
        report = {
            "logging_system": self.game_logger.get_performance_impact() if self.game_logger else {},
            "overlay_rendering": self.testing_overlay.get_performance_stats(),
            "oqe_collector": {
                "sample_count": len(self.oqe_collector.samples),
                "memory_overhead_mb": len(self.oqe_collector.samples) * 0.001  # Rough estimate
            }
        }
        
        return report
