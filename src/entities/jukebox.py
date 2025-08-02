"""Interactive jukebox entity for the hub world."""

import pygame
from typing import Optional, List
from src.managers.audio.music_manager import MusicManager, MusicTrack
from src.utils.asset_paths import get_image_path, get_sfx_path


class Jukebox:
    """Interactive jukebox for selecting and playing music in the hub."""
    
    def __init__(self, x: int, y: int, music_manager: MusicManager, sound_manager=None):
        """Initialize the jukebox.
        
        Args:
            x: X position in the hub world
            y: Y position in the hub world
            music_manager: Music manager instance
            sound_manager: Sound manager for UI sounds
        """
        self.x = x
        self.y = y
        self.music_manager = music_manager
        self.sound_manager = sound_manager
        
        # Jukebox state
        self.is_active = False
        self.is_interactable = True
        self.interaction_range = 80
        self.menu_open = False
        
        # UI state
        self.selected_track_index = 0
        self.scroll_offset = 0
        self.max_visible_tracks = 5
        self.menu_animation = 0.0
        self.menu_target = 0.0
        
        # Visual properties
        self.width = 120
        self.height = 180
        self.collision_rect = pygame.Rect(x, y, self.width, self.height)
        
        # Load sprites
        self._load_sprites()
        
        # UI styling
        self.menu_width = 400
        self.menu_height = 350
        self.track_item_height = 50
        
        # Colors
        self.bg_color = (20, 20, 30, 200)
        self.selected_color = (100, 150, 255, 150)
        self.text_color = (255, 255, 255)
        self.locked_color = (120, 120, 120)
        self.hint_color = (200, 200, 100)
        
        # Input handling
        self.input_cooldown = 0.0
        self.input_delay = 0.15  # Seconds between inputs
        
        # Interaction prompt
        self.show_prompt = False
        self.prompt_text = "Press E to use Jukebox"
        
    def _load_sprites(self):
        """Load jukebox sprites."""
        try:
            # Try to load actual jukebox sprite
            self.sprite = pygame.image.load(get_image_path("entities/jukebox.png"))
            self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
        except (pygame.error, FileNotFoundError):
            # Create placeholder jukebox sprite
            self.sprite = pygame.Surface((self.width, self.height))
            
            # Draw a retro jukebox design
            # Main body
            pygame.draw.rect(self.sprite, (80, 40, 20), (0, 0, self.width, self.height))
            pygame.draw.rect(self.sprite, (60, 30, 15), (0, 0, self.width, self.height), 3)
            
            # Speaker grilles
            grill_color = (40, 40, 40)
            for i in range(0, self.height - 40, 8):
                pygame.draw.line(self.sprite, grill_color, (10, i + 20), (self.width - 10, i + 20), 2)
            
            # Control panel
            panel_rect = pygame.Rect(20, self.height - 60, self.width - 40, 40)
            pygame.draw.rect(self.sprite, (120, 120, 120), panel_rect)
            pygame.draw.rect(self.sprite, (100, 100, 100), panel_rect, 2)
            
            # Buttons
            for i in range(3):
                btn_x = 30 + i * 20
                btn_y = self.height - 45
                pygame.draw.circle(self.sprite, (200, 200, 200), (btn_x, btn_y), 6)
                pygame.draw.circle(self.sprite, (150, 150, 150), (btn_x, btn_y), 6, 2)
            
            # Top dome/selector
            dome_rect = pygame.Rect(30, 10, self.width - 60, 30)
            pygame.draw.ellipse(self.sprite, (150, 100, 50), dome_rect)
            pygame.draw.ellipse(self.sprite, (120, 80, 40), dome_rect, 2)
    
    def update(self, dt: float, player_pos: tuple):
        """Update jukebox state.
        
        Args:
            dt: Delta time since last update
            player_pos: Player position (x, y)
        """
        # Update input cooldown
        if self.input_cooldown > 0:
            self.input_cooldown -= dt
        
        # Check if player is in range
        player_x, player_y = player_pos
        distance = ((player_x - (self.x + self.width // 2)) ** 2 + 
                   (player_y - (self.y + self.height // 2)) ** 2) ** 0.5
        
        self.show_prompt = distance <= self.interaction_range and not self.menu_open
        
        # Update menu animation
        if self.menu_open:
            self.menu_target = 1.0
        else:
            self.menu_target = 0.0
        
        # Smooth animation
        animation_speed = 8.0
        self.menu_animation += (self.menu_target - self.menu_animation) * animation_speed * dt
        self.menu_animation = max(0.0, min(1.0, self.menu_animation))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled
        """
        if not self.is_interactable or self.input_cooldown > 0:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and self.show_prompt:
                # Open/close menu
                self.menu_open = not self.menu_open
                self._play_ui_sound("menu_open.ogg" if self.menu_open else "menu_close.ogg")
                self.input_cooldown = self.input_delay
                return True
            
            elif self.menu_open:
                if event.key == pygame.K_ESCAPE:
                    # Close menu
                    self.menu_open = False
                    self._play_ui_sound("menu_close.ogg")
                    self.input_cooldown = self.input_delay
                    return True
                
                elif event.key == pygame.K_UP:
                    self._navigate_up()
                    return True
                
                elif event.key == pygame.K_DOWN:
                    self._navigate_down()
                    return True
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self._select_track()
                    return True
                
                elif event.key == pygame.K_h:
                    # Show hints for locked tracks
                    self._show_unlock_hints()
                    return True
        
        return False
    
    def _navigate_up(self):
        """Navigate up in the track list."""
        tracks = self.music_manager.get_jukebox_tracks()
        if tracks:
            self.selected_track_index = (self.selected_track_index - 1) % len(tracks)
            self._update_scroll()
            self._play_ui_sound("menu_move.ogg")
            self.input_cooldown = self.input_delay
    
    def _navigate_down(self):
        """Navigate down in the track list."""
        tracks = self.music_manager.get_jukebox_tracks()
        if tracks:
            self.selected_track_index = (self.selected_track_index + 1) % len(tracks)
            self._update_scroll()
            self._play_ui_sound("menu_move.ogg")
            self.input_cooldown = self.input_delay
    
    def _update_scroll(self):
        """Update scroll offset to keep selected item visible."""
        if self.selected_track_index < self.scroll_offset:
            self.scroll_offset = self.selected_track_index
        elif self.selected_track_index >= self.scroll_offset + self.max_visible_tracks:
            self.scroll_offset = self.selected_track_index - self.max_visible_tracks + 1
    
    def _select_track(self):
        """Select and play the current track."""
        tracks = self.music_manager.get_jukebox_tracks()
        if tracks and 0 <= self.selected_track_index < len(tracks):
            track = tracks[self.selected_track_index]
            
            if track.unlocked:
                # Play the track
                success = self.music_manager.play_track(track.id)
                if success:
                    self._play_ui_sound("menu_select.ogg")
                    # Could show "Now Playing" notification here
                else:
                    self._play_ui_sound("menu_error.ogg")
            else:
                # Track is locked
                self._play_ui_sound("menu_denied.ogg")
            
            self.input_cooldown = self.input_delay
    
    def _show_unlock_hints(self):
        """Show hints for unlocking tracks (could trigger popup)."""
        hints = self.music_manager.get_unlock_hints()
        if hints:
            # In a full implementation, this could show a popup or notification
            print("🎵 Unlock Hints:")
            for title, hint in hints.items():
                print(f"  {title}: {hint}")
        
        self._play_ui_sound("menu_info.ogg")
        self.input_cooldown = self.input_delay
    
    def _play_ui_sound(self, sound_file: str):
        """Play a UI sound effect.
        
        Args:
            sound_file: Name of the sound file
        """
        if self.sound_manager:
            try:
                self.sound_manager.play_sfx(get_sfx_path(sound_file))
            except:
                # Fallback to basic sound
                pass
    
    def draw(self, screen: pygame.Surface, camera_offset: tuple = (0, 0)):
        """Draw the jukebox and its menu.
        
        Args:
            screen: Surface to draw on
            camera_offset: Camera offset (x, y)
        """
        camera_x, camera_y = camera_offset
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        
        # Draw jukebox sprite
        screen.blit(self.sprite, (draw_x, draw_y))
        
        # Draw interaction prompt
        if self.show_prompt:
            self._draw_prompt(screen, draw_x + self.width // 2, draw_y - 30)
        
        # Draw menu if open
        if self.menu_animation > 0.01:
            self._draw_menu(screen)
    
    def _draw_prompt(self, screen: pygame.Surface, x: int, y: int):
        """Draw interaction prompt.
        
        Args:
            screen: Surface to draw on
            x: Center X position
            y: Center Y position
        """
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.prompt_text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(x, y))
        
        # Draw background
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        
        # Draw text
        screen.blit(text_surface, text_rect)
    
    def _draw_menu(self, screen: pygame.Surface):
        """Draw the jukebox menu.
        
        Args:
            screen: Surface to draw on
        """
        # Calculate menu position (center of screen)
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        menu_x = (screen_width - self.menu_width) // 2
        menu_y = (screen_height - self.menu_height) // 2
        
        # Apply animation scaling
        scale = self.menu_animation
        if scale <= 0:
            return
        
        # Create menu surface
        menu_surface = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
        
        # Draw background
        bg_color = (*self.bg_color[:3], int(self.bg_color[3] * scale))
        menu_surface.fill(bg_color)
        
        # Draw border
        pygame.draw.rect(menu_surface, self.text_color, 
                        (0, 0, self.menu_width, self.menu_height), 2)
        
        # Draw title
        title_font = pygame.font.Font(None, 36)
        title_text = title_font.render("🎵 Music Jukebox", True, self.text_color)
        title_rect = title_text.get_rect(centerx=self.menu_width // 2, y=15)
        menu_surface.blit(title_text, title_rect)
        
        # Draw track list
        self._draw_track_list(menu_surface, 20, 60)
        
        # Draw controls help
        self._draw_controls_help(menu_surface)
        
        # Scale and draw menu
        if scale < 1.0:
            # Scale the menu surface
            scaled_width = int(self.menu_width * scale)
            scaled_height = int(self.menu_height * scale)
            scaled_surface = pygame.transform.scale(menu_surface, (scaled_width, scaled_height))
            
            # Center the scaled surface
            scaled_x = menu_x + (self.menu_width - scaled_width) // 2
            scaled_y = menu_y + (self.menu_height - scaled_height) // 2
            screen.blit(scaled_surface, (scaled_x, scaled_y))
        else:
            screen.blit(menu_surface, (menu_x, menu_y))
    
    def _draw_track_list(self, surface: pygame.Surface, x: int, y: int):
        """Draw the list of tracks.
        
        Args:
            surface: Surface to draw on
            x: X position
            y: Y position
        """
        tracks = self.music_manager.get_jukebox_tracks()
        if not tracks:
            # No tracks available
            font = pygame.font.Font(None, 24)
            text = font.render("No music tracks available", True, self.locked_color)
            surface.blit(text, (x, y))
            return
        
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 20)
        
        # Draw visible tracks
        for i in range(self.max_visible_tracks):
            track_index = self.scroll_offset + i
            if track_index >= len(tracks):
                break
            
            track = tracks[track_index]
            item_y = y + i * self.track_item_height
            
            # Highlight selected track
            if track_index == self.selected_track_index:
                highlight_rect = pygame.Rect(x - 5, item_y - 5, 
                                           self.menu_width - 30, self.track_item_height)
                highlight_surface = pygame.Surface(highlight_rect.size, pygame.SRCALPHA)
                highlight_surface.fill(self.selected_color)
                surface.blit(highlight_surface, highlight_rect)
            
            # Choose color based on unlock status
            if track.unlocked:
                text_color = self.text_color
                status_icon = "🎵"
            else:
                text_color = self.locked_color
                status_icon = "🔒"
            
            # Draw track title
            title_text = font.render(f"{status_icon} {track.title}", True, text_color)
            surface.blit(title_text, (x, item_y))
            
            # Draw artist and duration
            if track.unlocked:
                info_text = f"{track.artist} - {track.duration:.0f}s"
                info_surface = small_font.render(info_text, True, text_color)
                surface.blit(info_surface, (x + 20, item_y + 20))
        
        # Draw scroll indicators
        if self.scroll_offset > 0:
            # Up arrow
            arrow_text = font.render("▲", True, self.text_color)
            surface.blit(arrow_text, (self.menu_width - 30, y - 20))
        
        if self.scroll_offset + self.max_visible_tracks < len(tracks):
            # Down arrow
            arrow_text = font.render("▼", True, self.text_color)
            surface.blit(arrow_text, (self.menu_width - 30, y + self.max_visible_tracks * self.track_item_height))
    
    def _draw_controls_help(self, surface: pygame.Surface):
        """Draw controls help text.
        
        Args:
            surface: Surface to draw on
        """
        help_y = self.menu_height - 60
        font = pygame.font.Font(None, 20)
        
        controls = [
            "↑↓ Navigate  ENTER Play  H Hints  ESC Close"
        ]
        
        for i, control_text in enumerate(controls):
            text_surface = font.render(control_text, True, self.hint_color)
            text_rect = text_surface.get_rect(centerx=self.menu_width // 2, 
                                            y=help_y + i * 20)
            surface.blit(text_surface, text_rect)
    
    def get_collision_rect(self) -> pygame.Rect:
        """Get collision rectangle for the jukebox.
        
        Returns:
            Collision rectangle
        """
        return self.collision_rect
    
    def is_near_player(self, player_pos: tuple) -> bool:
        """Check if player is near the jukebox.
        
        Args:
            player_pos: Player position (x, y)
            
        Returns:
            True if player is in interaction range
        """
        player_x, player_y = player_pos
        distance = ((player_x - (self.x + self.width // 2)) ** 2 + 
                   (player_y - (self.y + self.height // 2)) ** 2) ** 0.5
        return distance <= self.interaction_range