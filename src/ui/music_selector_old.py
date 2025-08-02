"""Music selection component for racing games with OutRun-style track selection."""

import pygame
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
    
    # Track definitions for The Drive racing game
    DRIVE_TRACKS = [
        MusicTrack(
            name="highway_dreams",
            display_name="Highway Dreams",
            description="The main theme - cruising down endless roads",
            filename="drive_highway_dreams.ogg",
            bpm=125,
            mood="cruising",
            preview_start=15.0
        ),
        MusicTrack(
            name="sunset_cruise",
            display_name="Sunset Cruise",
            description="Relaxed vibes for a peaceful drive",
            filename="drive_sunset_cruise.ogg",
            bpm=108,
            mood="relaxed",
            preview_start=20.0
        ),
        MusicTrack(
            name="turbo_rush",
            display_name="Turbo Rush",
            description="High energy beats for intense racing",
            filename="drive_turbo_rush.ogg",
            bpm=140,
            mood="intense",
            preview_start=10.0
        ),
    ]
    
    def __init__(self, 
                 screen_width: int, 
                 screen_height: int,
                 sound_manager,
                 tracks: List[MusicTrack] = None):
        """
        Initialize the music selector.
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            sound_manager: SoundManager instance for audio playback
            tracks: List of MusicTrack objects (defaults to DRIVE_TRACKS)
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sound_manager = sound_manager
        self.tracks = tracks or self.DRIVE_TRACKS
        
        # Selection state
        self.selected_track_index = 0
        self.is_previewing = False
        self.preview_volume = 0.3  # Lower volume for preview
        self.original_music_volume = sound_manager.music_volume
        
        # Visual elements
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Animation state
        self.selection_pulse = 0.0
        self.pulse_speed = 3.0
        
        # Track info panel dimensions
        self.panel_width = 500
        self.panel_height = 200
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2 - 50
        
        # Button dimensions
        self.button_width = BUTTON_WIDTH
        self.button_height = BUTTON_HEIGHT
        self.button_spacing = BUTTON_PADDING
        
        # Callbacks
        self.on_track_selected: Optional[Callable[[MusicTrack], None]] = None
        self.on_cancelled: Optional[Callable[[], None]] = None
        
    def handle_event(self, event) -> Optional[str]:
        """
        Handle input events for music selection.
        
        Args:
            event: Pygame event
            
        Returns:
            Action string or None
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self._select_previous_track()
                return "track_changed"
                
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self._select_next_track()
                return "track_changed"
                
            elif event.key == pygame.K_SPACE:
                self._toggle_preview()
                return "preview_toggled"
                
            elif event.key == pygame.K_RETURN:
                self._confirm_selection()
                return "track_confirmed"
                
            elif event.key == pygame.K_ESCAPE:
                self._cancel_selection()
                return "selection_cancelled"
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                clicked_track = self._get_track_at_position(mouse_pos)
                
                if clicked_track is not None:
                    if clicked_track == self.selected_track_index:
                        # Double-click to confirm
                        self._confirm_selection()
                        return "track_confirmed"
                    else:
                        # Select different track
                        self.selected_track_index = clicked_track
                        self._play_selection_sound()
                        return "track_changed"
                        
        return None
        
    def update(self, dt: float):
        """
        Update animation and state.
        
        Args:
            dt: Delta time in seconds
        """
        # Update selection pulse animation
        self.selection_pulse += self.pulse_speed * dt
        if self.selection_pulse > 2 * 3.14159:  # 2π
            self.selection_pulse -= 2 * 3.14159
            
    def draw(self, screen):
        """
        Draw the music selection interface.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self.font_large.render("SELECT MUSIC", True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title_text, title_rect)
        
        # Draw track list
        self._draw_track_list(screen)
        
        # Draw selected track info panel
        self._draw_track_info_panel(screen)
        
        # Draw controls help
        self._draw_controls_help(screen)
        
    def _select_previous_track(self):
        """Select the previous track in the list."""
        self.selected_track_index = (self.selected_track_index - 1) % len(self.tracks)
        self._play_selection_sound()
        self._stop_preview()  # Stop current preview when changing tracks
        
    def _select_next_track(self):
        """Select the next track in the list."""
        self.selected_track_index = (self.selected_track_index + 1) % len(self.tracks)
        self._play_selection_sound()
        self._stop_preview()  # Stop current preview when changing tracks
        
    def _toggle_preview(self):
        """Toggle music preview for the selected track."""
        if self.is_previewing:
            self._stop_preview()
        else:
            self._start_preview()
            
    def _start_preview(self):
        """Start previewing the selected track."""
        if self.is_previewing:
            return
            
        selected_track = self.tracks[self.selected_track_index]
        music_path = get_music_path(selected_track.filename)
        
        try:
            # Lower music volume for preview
            self.sound_manager.set_music_volume(self.preview_volume)
            
            # Play the track (will need to be modified to start at preview_start time)
            self.sound_manager.play_music(music_path, loops=0)  # Play once for preview
            
            self.is_previewing = True
            
            # Play preview start sound
            try:
                self.sound_manager.play_sfx(get_sfx_path("ui_preview_start.ogg"))
            except:
                pass  # Sound file not available yet
                
        except Exception as e:
            print(f"Could not preview track {selected_track.filename}: {e}")
            
    def _stop_preview(self):
        """Stop the music preview."""
        if not self.is_previewing:
            return
            
        self.sound_manager.stop_music(fade_ms=500)
        self.sound_manager.set_music_volume(self.original_music_volume)
        self.is_previewing = False
        
    def _confirm_selection(self):
        """Confirm the current track selection."""
        self._stop_preview()
        selected_track = self.tracks[self.selected_track_index]
        
        # Play confirmation sound
        try:
            self.sound_manager.play_sfx(get_sfx_path("ui_confirm.ogg"))
        except:
            pass  # Sound file not available yet
            
        if self.on_track_selected:
            self.on_track_selected(selected_track)
            
    def _cancel_selection(self):
        """Cancel track selection and return to previous state."""
        self._stop_preview()
        
        # Play cancel sound
        try:
            self.sound_manager.play_sfx(get_sfx_path("ui_cancel.ogg"))
        except:
            pass  # Sound file not available yet
            
        if self.on_cancelled:
            self.on_cancelled()
            
    def _play_selection_sound(self):
        """Play sound when changing track selection."""
        try:
            self.sound_manager.play_sfx(get_sfx_path("menu_move.ogg"))
        except:
            pass  # Sound file not available yet
            
    def _get_track_at_position(self, mouse_pos) -> Optional[int]:
        """
        Get the track index at the given mouse position.
        
        Args:
            mouse_pos: (x, y) mouse position
            
        Returns:
            Track index or None if no track at position
        """
        # Calculate track list area
        start_y = 220
        track_height = 60
        
        for i, track in enumerate(self.tracks):
            track_y = start_y + i * track_height
            track_rect = pygame.Rect(
                self.screen_width // 2 - 200,
                track_y,
                400,
                track_height - 10
            )
            
            if track_rect.collidepoint(mouse_pos):
                return i
                
        return None
        
    def _draw_track_list(self, screen):
        """Draw the list of available tracks."""
        start_y = 220
        track_height = 60
        
        for i, track in enumerate(self.tracks):
            # Calculate position
            track_y = start_y + i * track_height
            
            # Determine colors based on selection
            if i == self.selected_track_index:
                # Animated selection color
                pulse_intensity = (1.0 + 0.3 * pygame.math.Vector2(1, 0).rotate(
                    self.selection_pulse * 180 / 3.14159
                ).x)
                bg_color = (
                    int(COLOR_BLUE[0] * pulse_intensity),
                    int(COLOR_BLUE[1] * pulse_intensity),
                    int(COLOR_BLUE[2] * pulse_intensity)
                )
                text_color = COLOR_WHITE
                border_color = COLOR_YELLOW
            else:
                bg_color = (40, 40, 40)
                text_color = COLOR_WHITE
                border_color = (80, 80, 80)
                
            # Draw track background
            track_rect = pygame.Rect(
                self.screen_width // 2 - 200,
                track_y,
                400,
                track_height - 10
            )
            pygame.draw.rect(screen, bg_color, track_rect)
            pygame.draw.rect(screen, border_color, track_rect, 2)
            
            # Draw track name
            name_text = self.font_large.render(track.display_name, True, text_color)
            name_rect = name_text.get_rect(
                left=track_rect.left + 15,
                centery=track_rect.centery - 8
            )
            screen.blit(name_text, name_rect)
            
            # Draw track info
            mood_color = self._get_mood_color(track.mood)
            info_text = f"{track.mood.upper()} • {track.bpm} BPM"
            info_surface = self.font_small.render(info_text, True, mood_color)
            info_rect = info_surface.get_rect(
                left=track_rect.left + 15,
                centery=track_rect.centery + 12
            )
            screen.blit(info_surface, info_rect)
            
            # Draw preview indicator
            if i == self.selected_track_index and self.is_previewing:
                preview_text = "♪ PREVIEWING"
                preview_surface = self.font_small.render(preview_text, True, COLOR_GREEN)
                preview_rect = preview_surface.get_rect(
                    right=track_rect.right - 15,
                    centery=track_rect.centery
                )
                screen.blit(preview_surface, preview_rect)
                
    def _draw_track_info_panel(self, screen):
        """Draw detailed information panel for the selected track."""
        selected_track = self.tracks[self.selected_track_index]
        
        # Panel background
        panel_rect = pygame.Rect(self.panel_x, self.panel_y + 250, self.panel_width, 120)
        pygame.draw.rect(screen, (20, 20, 20), panel_rect)
        pygame.draw.rect(screen, COLOR_WHITE, panel_rect, 2)
        
        # Track description
        desc_lines = self._wrap_text(selected_track.description, self.font_small, self.panel_width - 30)
        y_offset = panel_rect.top + 15
        
        for line in desc_lines:
            desc_surface = self.font_small.render(line, True, COLOR_WHITE)
            screen.blit(desc_surface, (panel_rect.left + 15, y_offset))
            y_offset += 25
            
    def _draw_controls_help(self, screen):
        """Draw control instructions."""
        controls = [
            "↑/↓ or W/S: Select track",
            "SPACE: Preview track",
            "ENTER: Confirm selection",
            "ESC: Cancel"
        ]
        
        start_y = self.screen_height - 120
        for i, control in enumerate(controls):
            control_surface = self.font_small.render(control, True, COLOR_WHITE)
            control_rect = control_surface.get_rect(
                center=(self.screen_width // 2, start_y + i * 20)
            )
            screen.blit(control_surface, control_rect)
            
    def _get_mood_color(self, mood: str) -> tuple:
        """Get color associated with track mood."""
        mood_colors = {
            "cruising": COLOR_BLUE,
            "relaxed": COLOR_GREEN,
            "intense": COLOR_RED,
            "energetic": COLOR_YELLOW,
        }
        return mood_colors.get(mood, COLOR_WHITE)
        
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within the given width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding this word would exceed the width
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, add it anyway
                    lines.append(word)
                    
        if current_line:
            lines.append(" ".join(current_line))
            
        return lines
        
    def get_selected_track(self) -> MusicTrack:
        """Get the currently selected track."""
        return self.tracks[self.selected_track_index]
        
    def set_track_selected_callback(self, callback: Callable[[MusicTrack], None]):
        """Set callback for when a track is selected."""
        self.on_track_selected = callback
        
    def set_cancelled_callback(self, callback: Callable[[], None]):
        """Set callback for when selection is cancelled."""
        self.on_cancelled = callback