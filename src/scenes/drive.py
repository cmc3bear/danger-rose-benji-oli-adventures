"""The Drive - OutRun-style racing minigame with music selection."""

import random
import time
import math
from typing import Optional

import pygame

from src.config.constants import (
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_YELLOW,
    COLOR_SKY_BLUE,
    FONT_LARGE,
    FONT_SMALL,
    FONT_HUGE,
    GAME_DURATION,
    SCENE_HUB_WORLD,
    SCENE_LEADERBOARD,
    OVERLAY_GAME_OVER_ALPHA,
)
from src.ui.music_selector import MusicSelector, MusicTrack
from src.ui.vehicle_selector import VehicleSelector
from src.managers.race_music_manager import RaceMusicManager, RaceState
from src.utils.asset_paths import get_sfx_path
from src.utils.sprite_loader import load_vehicle_sprite
from src.ui.drawing_helpers import draw_text_with_background, draw_instructions


class DriveGame:
    """
    The Drive - OutRun-inspired racing minigame.
    
    Features music selection before racing, dynamic music during gameplay,
    and classic arcade-style racing mechanics.
    """
    
    # Game states
    STATE_MUSIC_SELECT = "music_select"
    STATE_VEHICLE_SELECT = "vehicle_select"
    STATE_READY = "ready"
    STATE_RACING = "racing"
    STATE_GAME_OVER = "game_over"
    
    def __init__(self, scene_manager):
        """Initialize the Drive racing game."""
        self.scene_manager = scene_manager
        self.screen_width = scene_manager.screen_width
        self.screen_height = scene_manager.screen_height
        
        # Game state
        self.state = self.STATE_MUSIC_SELECT
        self.race_duration = GAME_DURATION * 2  # 2 minutes for racing
        self.time_remaining = self.race_duration
        self.start_time = None
        
        # Music system
        self.music_selector = MusicSelector(
            self.screen_width,
            self.screen_height,
            scene_manager.sound_manager
        )
        self.race_music_manager = RaceMusicManager(scene_manager.sound_manager)
        self.selected_track: Optional[MusicTrack] = None
        
        # Vehicle system
        self.vehicle_selector = VehicleSelector(
            self.screen_width,
            self.screen_height,
            scene_manager.sound_manager
        )
        self.selected_vehicle = None
        self.car_sprite = None
        
        # Music selector doesn't need callbacks - we handle events in handle_event
        
        # Racing mechanics
        self.player_speed = 0.0         # Current speed (0.0 to 1.0)
        self.max_speed = 1.0
        self.acceleration = 0.5         # Speed increase per second
        self.deceleration = 0.8         # Speed decrease per second
        self.player_x = 0.5             # Horizontal position (0.0 to 1.0)
        self.road_curve = 0.0           # Current road curvature
        self.road_position = 0.0        # Position along the road
        
        # Racing state
        self.race_state = RaceState(
            speed=0.0,
            position=1,
            total_racers=8,
            time_remaining=self.race_duration
        )
        
        # Visual elements
        self.horizon_y = self.screen_height // 2
        self.road_width = 200
        self.max_road_width = 400
        self.car_width = 64  # Display width (scaled from 128)
        self.car_height = 96  # Display height (scaled from 192)
        
        # UI fonts
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_huge = pygame.font.Font(None, FONT_HUGE)
        
        # Score and statistics
        self.distance_traveled = 0.0
        self.top_speed_reached = 0.0
        self.score = 0
        
        # Input handling
        self.keys_pressed = set()
        
    def handle_event(self, event):
        """Handle input events."""
        if self.state == self.STATE_MUSIC_SELECT:
            # Music selector handles its own events
            result = self.music_selector.handle_event(event)
            if result == "track_selected":
                self._on_track_selected(self.music_selector.get_selected_track())
            elif result == "cancelled":
                self._on_music_cancelled()
            return None
            
        elif self.state == self.STATE_VEHICLE_SELECT:
            # Vehicle selector handles its own events
            result = self.vehicle_selector.handle_event(event)
            if result == "vehicle_selected":
                self._on_vehicle_selected(self.vehicle_selector.get_selected_vehicle())
            elif result == "cancelled":
                self._on_vehicle_cancelled()
            return None
            
        elif event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            
            if self.state == self.STATE_READY:
                if event.key == pygame.K_SPACE:
                    self._start_race()
                elif event.key == pygame.K_ESCAPE:
                    return SCENE_HUB_WORLD
                elif event.key == pygame.K_m:
                    # Return to music selection
                    self.state = self.STATE_MUSIC_SELECT
                    
            elif self.state == self.STATE_RACING:
                if event.key == pygame.K_ESCAPE:
                    self._end_race()
                    
            elif self.state == self.STATE_GAME_OVER:
                if event.key == pygame.K_SPACE:
                    self._restart_game()
                elif event.key == pygame.K_l:
                    return SCENE_LEADERBOARD
                elif event.key == pygame.K_ESCAPE:
                    return SCENE_HUB_WORLD
                elif event.key == pygame.K_m:
                    # Return to music selection
                    self.state = self.STATE_MUSIC_SELECT
                    
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
            
        return None
        
    def update(self, dt: float):
        """Update game state."""
        if self.state == self.STATE_MUSIC_SELECT:
            self.music_selector.update(dt)
            
        elif self.state == self.STATE_VEHICLE_SELECT:
            self.vehicle_selector.update(dt)
            
        elif self.state == self.STATE_RACING:
            self._update_racing(dt)
            
        # Always update race music manager
        self.race_music_manager.update(dt)
        
    def _update_racing(self, dt: float):
        """Update racing mechanics and state."""
        # Handle input
        self._handle_racing_input(dt)
        
        # Update timer
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.time_remaining = max(0, self.race_duration - elapsed)
            
            if self.time_remaining <= 10:
                self.race_state.is_final_lap = True
                
            if self.time_remaining <= 0:
                self._end_race()
                return
                
        # Update road curvature (simple sine wave)
        curve_frequency = 0.3 + self.player_speed * 0.2
        self.road_curve = math.sin(self.road_position * curve_frequency) * 0.5
        
        # Update road position based on speed
        self.road_position += self.player_speed * dt * 10
        
        # Update distance and score
        distance_delta = self.player_speed * dt * 100
        self.distance_traveled += distance_delta
        self.score += int(distance_delta * 10)
        
        # Track top speed
        self.top_speed_reached = max(self.top_speed_reached, self.player_speed)
        
        # Update race state
        self.race_state.speed = self.player_speed
        self.race_state.time_remaining = self.time_remaining
        
        # Simulate position changes based on speed
        # (In a real game, this would be based on AI opponents)
        target_position = max(1, int(9 - self.player_speed * 8))
        if target_position != self.race_state.position:
            self.race_state.position = target_position
            
        # Update race music
        self.race_music_manager.update_race_state(self.race_state)
        
    def _handle_racing_input(self, dt: float):
        """Handle racing input and update player state."""
        # Acceleration/deceleration
        if pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed:
            self.player_speed = min(
                self.max_speed,
                self.player_speed + self.acceleration * dt
            )
            # Boost effect at high speeds
            if self.player_speed > 0.8:
                self.race_state.is_boost = True
        else:
            self.player_speed = max(
                0.0,
                self.player_speed - self.deceleration * dt
            )
            self.race_state.is_boost = False
            
        # Steering
        steering_speed = 1.5 * dt
        if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
            self.player_x = max(0.0, self.player_x - steering_speed)
        if pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
            self.player_x = min(1.0, self.player_x + steering_speed)
            
        # Apply road curve influence
        curve_influence = self.road_curve * self.player_speed * dt
        self.player_x = max(0.0, min(1.0, self.player_x + curve_influence))
        
        # Check for crashes (hitting road edges at high speed)
        if (self.player_x < 0.1 or self.player_x > 0.9) and self.player_speed > 0.6:
            self._crash()
            
    def _crash(self):
        """Handle player crash."""
        self.race_state.is_crash = True
        self.player_speed *= 0.3  # Reduce speed significantly
        
        # Play crash sound
        try:
            self.scene_manager.sound_manager.play_sfx(get_sfx_path("collision.ogg"))
        except:
            pass  # Sound file not available yet
            
        # Reset crash flag after brief moment
        pygame.time.set_timer(pygame.USEREVENT + 1, 500)  # Clear crash state after 500ms
        
    def draw(self, screen):
        """Draw the game."""
        if self.state == self.STATE_MUSIC_SELECT:
            self._draw_road_background(screen)  # Show road in background
            self.music_selector.draw(screen)
            
        elif self.state == self.STATE_VEHICLE_SELECT:
            self._draw_road_background(screen)  # Show road in background
            self.vehicle_selector.draw(screen)
            
        elif self.state == self.STATE_READY:
            self._draw_road_background(screen)
            self._draw_ready_screen(screen)
            
        elif self.state == self.STATE_RACING:
            self._draw_racing_scene(screen)
            
        elif self.state == self.STATE_GAME_OVER:
            self._draw_racing_scene(screen)  # Show final race state
            self._draw_game_over_screen(screen)
            
    def _draw_road_background(self, screen):
        """Draw a simple road background."""
        # Sky gradient
        for y in range(self.horizon_y):
            color_intensity = int(135 + (100 * y / self.horizon_y))
            color_intensity = min(255, color_intensity)  # Clamp to valid range
            green = min(255, color_intensity + 50)
            color = (color_intensity, green, 255)
            pygame.draw.line(screen, color, (0, y), (self.screen_width, y))
            
        # Ground
        ground_rect = pygame.Rect(0, self.horizon_y, self.screen_width, 
                                 self.screen_height - self.horizon_y)
        screen.fill((34, 139, 34), ground_rect)  # Forest green
        
        # Simple road
        road_center = self.screen_width // 2
        current_width = self.road_width + int(self.road_curve * 100)
        
        road_rect = pygame.Rect(
            road_center - current_width // 2,
            self.horizon_y,
            current_width,
            self.screen_height - self.horizon_y
        )
        screen.fill((60, 60, 60), road_rect)
        
        # Road lines
        line_color = COLOR_YELLOW
        center_line_x = road_center + int(self.road_curve * 50)
        
        for y in range(self.horizon_y, self.screen_height, 20):
            line_y = y + int((self.road_position * 50) % 40) - 20
            if self.horizon_y <= line_y < self.screen_height:
                pygame.draw.line(screen, line_color, 
                               (center_line_x - 2, line_y), 
                               (center_line_x + 2, line_y), 4)
                               
    def _draw_racing_scene(self, screen):
        """Draw the main racing scene."""
        self._draw_road_background(screen)
        
        # Draw player car with sprite
        car_x = int(self.player_x * self.screen_width)
        car_y = self.screen_height - 100
        
        if self.car_sprite:
            # Scale and position sprite
            scaled_sprite = pygame.transform.scale(
                self.car_sprite,
                (self.car_width, self.car_height)
            )
            
            # Apply visual effects
            if self.race_state.is_crash:
                # Flash white during crash
                white_surface = scaled_sprite.copy()
                white_surface.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                scaled_sprite = white_surface
            elif self.race_state.is_boost:
                # Add yellow glow during boost
                glow_surface = scaled_sprite.copy()
                glow_surface.fill((255, 255, 0, 64), special_flags=pygame.BLEND_RGBA_ADD)
                scaled_sprite = glow_surface
            
            car_rect = scaled_sprite.get_rect(center=(car_x, car_y))
            screen.blit(scaled_sprite, car_rect)
        else:
            # Fallback to rectangle if no sprite
            car_rect = pygame.Rect(
                car_x - self.car_width // 2,
                car_y - self.car_height // 2,
                self.car_width,
                self.car_height
            )
            car_color = COLOR_RED
            if self.race_state.is_boost:
                car_color = COLOR_YELLOW
            elif self.race_state.is_crash:
                car_color = COLOR_WHITE
            pygame.draw.rect(screen, car_color, car_rect)
            pygame.draw.rect(screen, COLOR_BLACK, car_rect, 2)
        
        # Draw UI
        self._draw_racing_ui(screen)
        
    def _draw_racing_ui(self, screen):
        """Draw racing UI elements."""
        # Speed indicator
        speed_text = f"Speed: {int(self.player_speed * 100)}%"
        speed_surface = self.font_large.render(speed_text, True, COLOR_WHITE)
        screen.blit(speed_surface, (20, 20))
        
        # Position
        position_text = f"Position: {self.race_state.position}/{self.race_state.total_racers}"
        position_surface = self.font_large.render(position_text, True, COLOR_WHITE)
        screen.blit(position_surface, (20, 60))
        
        # Timer
        timer_text = f"Time: {int(self.time_remaining)}"
        draw_text_with_background(
            screen, timer_text, self.font_large,
            (self.screen_width // 2, 30),
            COLOR_WHITE, COLOR_BLACK, COLOR_WHITE
        )
        
        # Score
        score_text = f"Score: {self.score}"
        score_surface = self.font_small.render(score_text, True, COLOR_WHITE)
        screen.blit(score_surface, (20, 100))
        
        # Current track info
        if self.selected_track:
            track_text = f"♪ {self.selected_track.display_name}"
            track_surface = self.font_small.render(track_text, True, COLOR_GREEN)
            track_rect = track_surface.get_rect(right=self.screen_width - 20, top=20)
            screen.blit(track_surface, track_rect)
            
        # Status indicators
        if self.race_state.is_boost:
            boost_text = self.font_large.render("BOOST!", True, COLOR_YELLOW)
            boost_rect = boost_text.get_rect(center=(self.screen_width // 2, 100))
            screen.blit(boost_text, boost_rect)
            
        if self.race_state.is_final_lap:
            final_text = self.font_large.render("FINAL LAP!", True, COLOR_RED)
            final_rect = final_text.get_rect(center=(self.screen_width // 2, 140))
            screen.blit(final_text, final_rect)
            
    def _draw_ready_screen(self, screen):
        """Draw the ready state screen."""
        # Title
        title_text = self.font_huge.render("THE DRIVE", True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(title_text, title_rect)
        
        # Selected track info
        if self.selected_track:
            track_info = f"Selected: {self.selected_track.display_name}"
            track_surface = self.font_large.render(track_info, True, COLOR_GREEN)
            track_rect = track_surface.get_rect(center=(self.screen_width // 2, 280))
            screen.blit(track_surface, track_rect)
            
            desc_surface = self.font_small.render(
                self.selected_track.description, True, COLOR_WHITE
            )
            desc_rect = desc_surface.get_rect(center=(self.screen_width // 2, 320))
            screen.blit(desc_surface, desc_rect)
            
        # Instructions
        instructions = [
            "Arrow Keys or WASD to drive",
            "Hold UP/W to accelerate",
            "LEFT/RIGHT or A/D to steer",
            "",
            "Press SPACE to start racing",
            "Press M to change music",
            "Press ESC to return to hub"
        ]
        
        draw_instructions(
            screen, instructions, self.font_small,
            self.screen_width // 2, 380, 30, COLOR_WHITE
        )
        
    def _draw_game_over_screen(self, screen):
        """Draw the game over screen."""
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(OVERLAY_GAME_OVER_ALPHA)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        # Results
        results_title = self.font_huge.render("RACE COMPLETE!", True, COLOR_WHITE)
        title_rect = results_title.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(results_title, title_rect)
        
        # Statistics
        stats = [
            f"Final Score: {self.score}",
            f"Distance: {int(self.distance_traveled)}m",
            f"Top Speed: {int(self.top_speed_reached * 100)}%",
            f"Final Position: {self.race_state.position}/{self.race_state.total_racers}",
        ]
        
        y_offset = 280
        for stat in stats:
            stat_surface = self.font_large.render(stat, True, COLOR_WHITE)
            stat_rect = stat_surface.get_rect(center=(self.screen_width // 2, y_offset))
            screen.blit(stat_surface, stat_rect)
            y_offset += 40
            
        # Options
        options = [
            "Press SPACE to race again",
            "Press M to change music",
            "Press L to view leaderboard",
            "Press ESC to return to hub"
        ]
        
        draw_instructions(
            screen, options, self.font_small,
            self.screen_width // 2, 480, 25, COLOR_WHITE
        )
        
    def _on_track_selected(self, track: MusicTrack):
        """Handle track selection from music selector."""
        self.selected_track = track
        self.race_music_manager.select_track(track)
        self.state = self.STATE_VEHICLE_SELECT  # Go to vehicle selection next
        
        print(f"Track selected: {track.display_name}")
        
    def _on_music_cancelled(self):
        """Handle music selection cancellation."""
        # Return to hub if no track was selected
        if not self.selected_track:
            return SCENE_HUB_WORLD
        else:
            # Return to ready state with current track
            self.state = self.STATE_READY
            
    def _on_vehicle_selected(self, vehicle: str):
        """Handle vehicle selection."""
        self.selected_vehicle = vehicle
        
        # Load the vehicle sprite
        try:
            self.car_sprite = load_vehicle_sprite(vehicle)
            print(f"Vehicle selected: {vehicle}")
        except Exception as e:
            print(f"[ERROR] Failed to load vehicle sprite: {e}")
            self.car_sprite = None
            
        # Save vehicle selection
        save_manager = self.scene_manager.save_manager
        if save_manager:
            save_manager.set_selected_vehicle(vehicle)
            save_manager.save()
            
        self.state = self.STATE_READY
        
    def _on_vehicle_cancelled(self):
        """Handle vehicle selection cancellation."""
        # Go back to music selection
        self.state = self.STATE_MUSIC_SELECT
            
    def _start_race(self):
        """Start the racing game."""
        self.state = self.STATE_RACING
        self.start_time = time.time()
        self.time_remaining = self.race_duration
        
        # Start race music
        self.race_music_manager.start_race_music(fade_in_ms=1000)
        
        # Reset race state
        self.race_state = RaceState(
            speed=0.0,
            position=self.race_state.total_racers,  # Start at back
            total_racers=self.race_state.total_racers,
            time_remaining=self.race_duration
        )
        
        # Reset player state
        self.player_speed = 0.0
        self.player_x = 0.5
        self.road_position = 0.0
        self.distance_traveled = 0.0
        self.top_speed_reached = 0.0
        self.score = 0
        
    def _end_race(self):
        """End the current race."""
        self.state = self.STATE_GAME_OVER
        
        # Stop race music
        self.race_music_manager.stop_race_music(fade_out_ms=2000)
        
        # Determine if victory
        if self.race_state.position <= 3:
            self.race_state.is_victory = True
            
        self.race_state.is_game_over = True
        
        # Play victory/game over stinger
        if self.race_state.is_victory:
            self.race_music_manager.play_stinger("victory")
            
    def _restart_game(self):
        """Restart the game with the same track."""
        self.state = self.STATE_READY
        
    def on_enter(self, previous_scene, data):
        """Called when entering this scene."""
        # Load previously selected vehicle from save
        save_manager = self.scene_manager.save_manager
        if save_manager:
            saved_vehicle = save_manager.get_selected_vehicle()
            if saved_vehicle and saved_vehicle != self.selected_vehicle:
                self.selected_vehicle = saved_vehicle
                try:
                    self.car_sprite = load_vehicle_sprite(saved_vehicle)
                except Exception as e:
                    print(f"[ERROR] Failed to load saved vehicle sprite: {e}")
                    self.car_sprite = None
        
        # Start with music selection if no track selected
        if not self.selected_track:
            self.state = self.STATE_MUSIC_SELECT
        else:
            self.state = self.STATE_READY
            
    def on_exit(self):
        """Called when leaving this scene."""
        # Stop any playing music
        self.race_music_manager.stop_race_music(fade_out_ms=500)
        return {}