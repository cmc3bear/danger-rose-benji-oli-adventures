"""
Universal Music Selection System for All Scenes/Minigames

Provides a consistent music selection interface that can be used across
all game scenes including Hub, Pool, Ski, Vegas, and Drive minigames.
"""

import pygame
import json
import math
from pathlib import Path
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass

from src.config.constants import (
    COLOR_WHITE,
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_YELLOW,
    FONT_LARGE,
    FONT_SMALL,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_PADDING,
)
from src.utils.asset_paths import get_music_path, get_sfx_path
from src.systems.game_state_logger import get_global_logger


@dataclass
class MusicTrack:
    """Represents a selectable music track."""
    name: str
    display_name: str
    description: str
    filename: str
    scene: str
    bpm: int = 120
    mood: str = "energetic"  # energetic, relaxed, intense, cozy, competitive
    preview_start: float = 30.0  # Seconds into track to start preview
    loop_start: float = 0.0  # Loop start point in seconds
    loop_end: float = 0.0    # Loop end point (0 = full track)


class UniversalMusicSelector:
    """
    Universal music selection interface for all game scenes.
    
    Provides a consistent music selection experience across Hub, Pool, Ski,
    Vegas, and Drive scenes with track preview and atmosphere matching.
    """
    
    def __init__(self, screen_width: int, screen_height: int, sound_manager, scene_name: str):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sound_manager = sound_manager
        self.scene_name = scene_name
        self.logger = get_global_logger()
        
        # UI configuration
        self.track_height = 80
        self.preview_volume = 0.3
        self.selection_index = 0
        self.is_previewing = False
        self.preview_timer = 0.0
        self.preview_duration = 15.0  # Preview for 15 seconds
        
        # Load tracks for this scene
        self.tracks = self.load_tracks_for_scene(scene_name)
        self.selected_track: Optional[MusicTrack] = self.tracks[0] if self.tracks else None
        
        # UI elements
        self.font_title = pygame.font.Font(None, 48)
        self.font_track = pygame.font.Font(None, 32)
        self.font_description = pygame.font.Font(None, 24)
        
        # Colors based on scene theme
        self.colors = self._get_scene_colors(scene_name)
        
        # Log music selector initialization
        if self.logger:
            self.logger.log_audio_event(
                audio_action="music_selector_init",
                track="none",
                details={
                    "scene": scene_name,
                    "available_tracks": len(self.tracks),
                    "track_names": [t.name for t in self.tracks]
                }
            )
    
    def _get_scene_colors(self, scene_name: str) -> Dict[str, tuple]:
        """Get color scheme based on scene theme."""
        color_schemes = {
            "hub": {
                "primary": (100, 150, 200),    # Cozy blue
                "secondary": (200, 180, 140),  # Warm beige
                "accent": (150, 200, 150),     # Soft green
                "text": COLOR_WHITE
            },
            "pool": {
                "primary": (50, 150, 255),     # Pool blue
                "secondary": (255, 200, 100),  # Sun yellow
                "accent": (100, 255, 200),     # Splash cyan
                "text": COLOR_WHITE
            },
            "ski": {
                "primary": (220, 230, 255),    # Snow white
                "secondary": (100, 150, 200),  # Ice blue
                "accent": (255, 200, 100),     # Sunset orange
                "text": (50, 50, 100)
            },
            "vegas": {
                "primary": (255, 50, 100),     # Neon pink
                "secondary": (255, 200, 50),   # Gold
                "accent": (100, 255, 150),     # Neon green
                "text": COLOR_WHITE
            },
            "drive": {
                "primary": (255, 100, 50),     # Racing red
                "secondary": (100, 100, 255),  # Speed blue
                "accent": (255, 255, 100),     # Lightning yellow
                "text": COLOR_WHITE
            }
        }
        return color_schemes.get(scene_name, color_schemes["hub"])
    
    @staticmethod
    def load_tracks_for_scene(scene_name: str) -> List[MusicTrack]:
        """Load music tracks for a specific scene from manifest."""
        try:
            manifest_path = Path(__file__).parent.parent.parent / "assets" / "audio" / "music" / scene_name / "music_manifest.json"
            
            if not manifest_path.exists():
                # Create default manifest if none exists
                return UniversalMusicSelector._create_default_tracks(scene_name)
            
            with open(manifest_path, 'r') as f:
                data = json.load(f)
            
            tracks = []
            for track_data in data.get('tracks', []):
                track = MusicTrack(
                    name=track_data['name'],
                    display_name=track_data.get('display_name', track_data['name']),
                    description=track_data.get('description', ''),
                    filename=track_data['filename'],
                    scene=scene_name,
                    bpm=track_data.get('bpm', 120),
                    mood=track_data.get('mood', 'energetic'),
                    preview_start=track_data.get('preview_start', 30.0),
                    loop_start=track_data.get('loop_start', 0.0),
                    loop_end=track_data.get('loop_end', 0.0)
                )
                tracks.append(track)
            
            return tracks
            
        except Exception as e:
            print(f"Warning: Could not load music manifest for {scene_name}: {e}")
            return UniversalMusicSelector._create_default_tracks(scene_name)
    
    @staticmethod
    def _create_default_tracks(scene_name: str) -> List[MusicTrack]:
        """Create default tracks if no manifest exists."""
        defaults = {
            "hub": [
                MusicTrack("cozy_home", "Cozy Home Theme", "Relaxing hub atmosphere", "code_breaker.mp3", "hub", mood="cozy"),
                MusicTrack("debug_mode", "Debug Mode", "Chill programming vibes", "debug_mode.mp3", "hub", mood="relaxed"),
                MusicTrack("git_glory", "Git Push Glory", "Achievement celebration", "git_push_glory.mp3", "hub", mood="energetic")
            ],
            "pool": [
                MusicTrack("splashdown", "Splashdown Showdown", "Main pool competition theme", "splashdown_showdown.mp3", "pool", mood="competitive"),
                MusicTrack("water_warriors", "Water Balloon Warriors", "Fast-paced pool action", "water_balloon_warriors.mp3", "pool", mood="energetic"),
                MusicTrack("victory_splash", "Victory Splash Anthem", "Pool victory celebration", "victory_splash_anthem.mp3", "pool", mood="triumphant")
            ],
            "ski": [
                MusicTrack("snow_rush", "Snow Rush Showdown", "Main skiing theme", "snow_rush_showdown.mp3", "ski", mood="energetic"),
                MusicTrack("frostbite", "Frostbite Frenzy", "Intense downhill racing", "frostbite_frenzy.mp3", "ski", mood="intense"),
                MusicTrack("pixel_peaks", "Pixel Peaks Victory", "Mountain victory theme", "pixel_peaks_victory.mp3", "ski", mood="triumphant")
            ],
            "vegas": [
                MusicTrack("neon_fury", "Neon Fury", "Main Vegas adventure theme", "neon_fury.mp3", "vegas", mood="energetic"),
                MusicTrack("battle_strip", "Battle on the Strip", "Boss battle music", "battle_on_the_strip.mp3", "vegas", mood="intense"),
                MusicTrack("vegas_lights", "Las Vegas Lights Up", "Victory and exploration", "las_vegas_lights_up.mp3", "vegas", mood="triumphant")
            ],
            "drive": [
                MusicTrack("highway_dreams", "Highway Dreams", "Main racing theme", "highway_dreams_main_theme.mp3", "drive", mood="energetic"),
                MusicTrack("sunset_cruise", "Sunset Cruise", "Relaxed driving experience", "sunset_cruise.mp3", "drive", mood="relaxed"),
                MusicTrack("turbo_rush", "Turbo Rush", "High-speed racing", "turbo_rush.mp3", "drive", mood="intense")
            ]
        }
        
        return defaults.get(scene_name, [])
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input events for music selection."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selection_index = (self.selection_index - 1) % len(self.tracks)
                self._stop_preview()
                
            elif event.key == pygame.K_DOWN:
                self.selection_index = (self.selection_index + 1) % len(self.tracks)
                self._stop_preview()
                
            elif event.key == pygame.K_SPACE or event.key == pygame.K_p:
                # Preview selected track
                self._toggle_preview()
                
            elif event.key == pygame.K_RETURN:
                # Select track and continue
                self.selected_track = self.tracks[self.selection_index]
                self._stop_preview()
                
                # Log track selection
                if self.logger:
                    self.logger.log_audio_event(
                        audio_action="music_track_selected",
                        track=self.selected_track.filename,
                        details={
                            "scene": self.scene_name,
                            "track_name": self.selected_track.name,
                            "mood": self.selected_track.mood,
                            "bpm": self.selected_track.bpm
                        }
                    )
                
                return "track_selected"
                
            elif event.key == pygame.K_ESCAPE:
                # Skip music selection
                self._stop_preview()
                return "skip_music"
        
        return None
    
    def _toggle_preview(self):
        """Toggle music preview playback."""
        if self.is_previewing:
            self._stop_preview()
        else:
            self._start_preview()
    
    def _start_preview(self):
        """Start previewing the selected track."""
        if not self.tracks:
            return
            
        track = self.tracks[self.selection_index]
        music_path = get_music_path(f"{self.scene_name}/{track.filename}")
        
        try:
            self.sound_manager.play_music(music_path, volume=self.preview_volume)
            self.is_previewing = True
            self.preview_timer = 0.0
            
            # Log preview start
            if self.logger:
                self.logger.log_audio_event(
                    audio_action="music_preview_start",
                    track=track.filename,
                    details={
                        "scene": self.scene_name,
                        "track_name": track.name,
                        "preview_volume": self.preview_volume
                    }
                )
                
        except Exception as e:
            print(f"Could not preview track {track.filename}: {e}")
    
    def _stop_preview(self):
        """Stop preview playback."""
        if self.is_previewing:
            self.sound_manager.stop_music()
            self.is_previewing = False
            self.preview_timer = 0.0
    
    def update(self, dt: float):
        """Update music selector state."""
        if self.is_previewing:
            self.preview_timer += dt
            if self.preview_timer >= self.preview_duration:
                self._stop_preview()
    
    def draw(self, screen: pygame.Surface):
        """Draw the music selection interface."""
        if not self.tracks:
            return
        
        # Clear screen with scene-appropriate background
        screen.fill(self.colors["primary"])
        
        # Draw title
        title_text = f"Choose Music for {self.scene_name.title()}"
        title_surface = self.font_title.render(title_text, True, self.colors["text"])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Draw tracks
        start_y = 200
        for i, track in enumerate(self.tracks):
            y_pos = start_y + i * self.track_height
            
            # Highlight selected track
            if i == self.selection_index:
                highlight_rect = pygame.Rect(50, y_pos - 10, self.screen_width - 100, self.track_height - 10)
                pygame.draw.rect(screen, self.colors["accent"], highlight_rect)
                pygame.draw.rect(screen, self.colors["secondary"], highlight_rect, 3)
            
            # Track name
            name_surface = self.font_track.render(track.display_name, True, self.colors["text"])
            screen.blit(name_surface, (100, y_pos))
            
            # Track description and mood
            desc_text = f"{track.description} | {track.mood.title()} | {track.bpm} BPM"
            desc_surface = self.font_description.render(desc_text, True, self.colors["text"])
            screen.blit(desc_surface, (100, y_pos + 35))
        
        # Draw instructions
        instructions = [
            "↑↓ Navigate  SPACE Preview  ENTER Select  ESC Skip"
        ]
        
        if self.is_previewing:
            preview_time = int(self.preview_duration - self.preview_timer)
            instructions.append(f"♪ Previewing... {preview_time}s remaining")
        
        inst_y = self.screen_height - 100
        for instruction in instructions:
            inst_surface = self.font_description.render(instruction, True, self.colors["text"])
            inst_rect = inst_surface.get_rect(center=(self.screen_width // 2, inst_y))
            screen.blit(inst_surface, inst_rect)
            inst_y += 30
    
    def get_selected_track(self) -> Optional[MusicTrack]:
        """Get the currently selected track."""
        return self.selected_track
    
    def cleanup(self):
        """Clean up resources."""
        self._stop_preview()