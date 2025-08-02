"""Music selection component for racing games with OutRun-style track selection."""

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


@dataclass
class MusicTrack:
    """Represents a selectable music track."""
    name: str
    display_name: str
    description: str
    filename: str
    bpm: int = 120
    mood: str = "energetic"  # energetic, relaxed, intense
    preview_start: float = 30.0  # Seconds into track to start preview


class MusicSelector:
    """
    OutRun-style music selection interface for racing games.
    
    Allows players to choose from multiple music tracks before starting a race.
    Features preview playback and visual track information.
    """
    
    @staticmethod
    def load_tracks_from_manifest(game_mode: str = "drive") -> List[MusicTrack]:
        """Load tracks from the music manifest file."""
        manifest_path = Path(__file__).parent.parent.parent / "assets" / "audio" / "music" / game_mode / "music_manifest.json"
        
        # Default tracks if manifest not found
        default_tracks = [
            MusicTrack(
                name="highway_dreams",
                display_name="Highway Dreams",
                description="The main theme - cruising down endless roads",
                filename="highway_dreams.mp3",
                bpm=125,
                mood="energetic",
                preview_start=15.0
            ),
            MusicTrack(
                name="sunset_cruise",
                display_name="Sunset Cruise",
                description="Relaxed vibes for a peaceful drive",
                filename="sunset_cruise.mp3",
                bpm=108,
                mood="relaxed",
                preview_start=20.0
            ),
            MusicTrack(
                name="turbo_rush",
                display_name="Turbo Rush",
                description="High energy beats for intense racing",
                filename="turbo_rush.mp3",
                bpm=140,
                mood="intense",
                preview_start=10.0
            ),
        ]
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                
            tracks = []
            for track_data in manifest.get("tracks", []):
                track = MusicTrack(
                    name=track_data["id"],
                    display_name=track_data["title"],
                    description=track_data["description"],
                    filename=track_data["filename"],
                    bpm=track_data.get("bpm", 120),
                    mood=track_data.get("mood", "energetic"),
                    preview_start=15.0  # Default preview start
                )
                tracks.append(track)
            
            return tracks if tracks else default_tracks
            
        except Exception as e:
            print(f"[WARNING] Could not load music manifest: {e}")
            return default_tracks
    
    def __init__(self, 
                 screen_width: int, 
                 screen_height: int,
                 sound_manager,
                 tracks: List[MusicTrack] = None,
                 game_mode: str = "drive"):
        """
        Initialize the music selector.
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            sound_manager: SoundManager instance for audio playback
            tracks: List of MusicTrack objects (loads from manifest if not provided)
            game_mode: Game mode for loading tracks (default: "drive")
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sound_manager = sound_manager
        self.game_mode = game_mode
        
        # Load tracks from manifest if not provided
        self.tracks = tracks or self.load_tracks_from_manifest(game_mode)
        
        # Selection state
        self.selected_track_index = 0
        self.is_previewing = False
        self.preview_volume = 0.3  # Lower volume for preview
        self.original_music_volume = sound_manager.music_volume
        
        # Visual elements
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SMALL + 10)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Track cards layout
        self.card_width = 300
        self.card_height = 400
        self.card_spacing = 50
        self.cards_y = screen_height // 2 - self.card_height // 2
        
        # Animation state
        self.animation_offset = 0.0
        self.animation_time = 0.0
        
        # Preview state
        self.preview_start_time = 0.0
        self.preview_duration = 15.0  # 15 seconds of preview
        
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle input events for music selection.
        
        Args:
            event: Pygame event to process
            
        Returns:
            "track_selected" when a track is selected, None otherwise
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._select_previous()
                return None
            elif event.key == pygame.K_RIGHT:
                self._select_next()
                return None
            elif event.key == pygame.K_SPACE:
                self._toggle_preview()
                return "preview_toggled"
            elif event.key == pygame.K_RETURN:
                self._stop_preview()
                return "track_selected"
            elif event.key == pygame.K_ESCAPE:
                self._stop_preview()
                return "cancelled"
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicked on a track card
                mouse_x, mouse_y = event.pos
                for i, rect in enumerate(self._get_card_rects()):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if i == self.selected_track_index:
                            self._stop_preview()
                            return "track_selected"
                        else:
                            self.selected_track_index = i
                            self._stop_preview()
                            return None
                            
        return None
        
    def update(self, dt: float):
        """
        Update animations and preview state.
        
        Args:
            dt: Delta time in seconds
        """
        # Update animation
        self.animation_time += dt
        self.animation_offset = math.sin(self.animation_time * 2) * 10
        
        # Check preview timeout
        if self.is_previewing:
            elapsed = pygame.time.get_ticks() / 1000.0 - self.preview_start_time
            if elapsed >= self.preview_duration:
                self._stop_preview()
                
    def draw(self, screen: pygame.Surface):
        """
        Draw the music selection interface.
        
        Args:
            screen: Surface to draw on
        """
        # Title
        title_text = self.font_large.render("SELECT MUSIC", True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_text, title_rect)
        
        # Draw track cards
        card_rects = self._get_card_rects()
        
        for i, (track, rect) in enumerate(zip(self.tracks, card_rects)):
            # Determine card state
            is_selected = i == self.selected_track_index
            
            # Card background
            if is_selected:
                # Add glow effect for selected card
                glow_rect = rect.inflate(20, 20)
                pygame.draw.rect(screen, COLOR_YELLOW, glow_rect, border_radius=15)
                pygame.draw.rect(screen, COLOR_BLACK, rect, border_radius=10)
                
                # Add animation offset
                rect.y += int(self.animation_offset)
            else:
                pygame.draw.rect(screen, (40, 40, 40), rect, border_radius=10)
                
            # Card border
            border_color = COLOR_YELLOW if is_selected else COLOR_WHITE
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=10)
            
            # Track number
            track_num = str(i + 1)
            num_text = self.font_large.render(track_num, True, COLOR_WHITE)
            num_rect = num_text.get_rect(center=(rect.centerx, rect.top + 40))
            screen.blit(num_text, num_rect)
            
            # Track name
            name_text = self.font_medium.render(track.display_name, True, COLOR_WHITE)
            name_rect = name_text.get_rect(center=(rect.centerx, rect.top + 100))
            screen.blit(name_text, name_rect)
            
            # BPM and mood
            info_text = f"{track.bpm} BPM - {track.mood.upper()}"
            info_surface = self.font_small.render(info_text, True, COLOR_GREEN)
            info_rect = info_surface.get_rect(center=(rect.centerx, rect.top + 140))
            screen.blit(info_surface, info_rect)
            
            # Description (word wrap)
            desc_lines = self._wrap_text(track.description, self.card_width - 40)
            y_offset = rect.top + 180
            for line in desc_lines:
                line_surface = self.font_small.render(line, True, COLOR_WHITE)
                line_rect = line_surface.get_rect(center=(rect.centerx, y_offset))
                screen.blit(line_surface, line_rect)
                y_offset += 25
                
            # Preview indicator
            if is_selected and self.is_previewing:
                preview_text = "PREVIEWING..."
                preview_surface = self.font_small.render(preview_text, True, COLOR_GREEN)
                preview_rect = preview_surface.get_rect(center=(rect.centerx, rect.bottom - 40))
                
                # Blink effect
                if int(self.animation_time * 2) % 2 == 0:
                    screen.blit(preview_surface, preview_rect)
                    
        # Instructions
        instructions = [
            "← → to select track",
            "SPACE to preview",
            "ENTER to confirm",
            "ESC to cancel"
        ]
        
        y_offset = self.screen_height - 120
        for instruction in instructions:
            inst_surface = self.font_small.render(instruction, True, COLOR_WHITE)
            inst_rect = inst_surface.get_rect(center=(self.screen_width // 2, y_offset))
            screen.blit(inst_surface, inst_rect)
            y_offset += 25
            
    def _get_card_rects(self) -> List[pygame.Rect]:
        """Get rectangles for track cards."""
        rects = []
        total_width = len(self.tracks) * self.card_width + (len(self.tracks) - 1) * self.card_spacing
        start_x = self.screen_width // 2 - total_width // 2
        
        for i in range(len(self.tracks)):
            x = start_x + i * (self.card_width + self.card_spacing)
            rect = pygame.Rect(x, self.cards_y, self.card_width, self.card_height)
            rects.append(rect)
            
        return rects
        
    def _select_previous(self):
        """Select previous track."""
        self.selected_track_index = (self.selected_track_index - 1) % len(self.tracks)
        self._stop_preview()
        self.sound_manager.play_sfx(get_sfx_path("menu_move.ogg"))
        
    def _select_next(self):
        """Select next track."""
        self.selected_track_index = (self.selected_track_index + 1) % len(self.tracks)
        self._stop_preview()
        self.sound_manager.play_sfx(get_sfx_path("menu_move.ogg"))
        
    def _toggle_preview(self):
        """Toggle music preview for the selected track."""
        if self.is_previewing:
            self._stop_preview()
        else:
            self._start_preview()
            
    def _start_preview(self):
        """Start previewing the selected track."""
        if not self.is_previewing:
            track = self.tracks[self.selected_track_index]
            
            # Build the full path to the music file
            music_path = Path(__file__).parent.parent.parent / "assets" / "audio" / "music" / self.game_mode / track.filename
            
            # Set preview volume
            self.sound_manager.set_music_volume(self.preview_volume)
            
            # Load and play the track
            try:
                print(f"Loading preview from: {music_path}")
                pygame.mixer.music.load(str(music_path))
                pygame.mixer.music.play(-1, track.preview_start)
                self.is_previewing = True
                self.preview_start_time = pygame.time.get_ticks() / 1000.0
                print(f"Preview started for: {track.display_name}")
                
                # Try to play the UI sound effect if it exists
                try:
                    self.sound_manager.play_sfx(get_sfx_path("ui_preview_start.ogg"))
                except:
                    pass  # Ignore if sound effect doesn't exist
            except Exception as e:
                print(f"[ERROR] Could not preview track: {e}")
                
    def _stop_preview(self):
        """Stop the preview."""
        if self.is_previewing:
            pygame.mixer.music.stop()
            self.sound_manager.set_music_volume(self.original_music_volume)
            self.is_previewing = False
            
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within given width."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font_small.render(test_line, True, COLOR_WHITE)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
        
    def get_selected_track(self) -> MusicTrack:
        """Get the currently selected track."""
        return self.tracks[self.selected_track_index]
        
    def cleanup(self):
        """Clean up resources."""
        self._stop_preview()
        
    def on_confirm(self):
        """Handle track confirmation."""
        self._stop_preview()
        self.sound_manager.play_sfx(get_sfx_path("ui_confirm.ogg"))
        return self.get_selected_track()
        
    def on_cancel(self):
        """Handle cancellation."""
        self._stop_preview()
        self.sound_manager.play_sfx(get_sfx_path("ui_cancel.ogg"))