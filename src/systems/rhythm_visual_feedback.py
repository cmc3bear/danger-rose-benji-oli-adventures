"""Visual feedback system for rhythm-based gameplay."""

import pygame
import math
from typing import Tuple, List, Optional

from .bpm_tracker import BeatInfo


class RhythmVisualFeedback:
    """Provide visual elements that respond to music rhythm."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize visual feedback system.
        
        Args:
            screen_width: Game screen width
            screen_height: Game screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Beat indicator settings
        self.beat_indicator_size = 20
        self.beat_indicator_pos = (50, screen_height - 50)
        self.beat_flash_duration = 0.1
        self.beat_flash_timer = 0.0
        
        # Road pulse settings
        self.road_pulse_amount = 10  # Max pixels of pulse
        self.road_pulse_smooth = 0.0
        self.enable_road_pulse = True
        
        # Speed lines settings
        self.speed_lines: List[SpeedLine] = []
        self.max_speed_lines = 20
        self.speed_line_spawn_rate = 0.5
        self.enable_speed_lines = True
        
        # Screen shake settings
        self.screen_shake_amount = 0.0
        self.screen_shake_decay = 5.0
        self.enable_screen_shake = False  # Off by default for family-friendly
        
        # Color pulse settings
        self.color_pulse_amount = 0.0
        self.color_pulse_target = 0.0
        
    def update(self, dt: float, beat_info: BeatInfo):
        """Update visual effects based on rhythm.
        
        Args:
            dt: Delta time
            beat_info: Current beat information
        """
        # Update beat indicator flash
        if beat_info.is_beat:
            self.beat_flash_timer = self.beat_flash_duration
        else:
            self.beat_flash_timer = max(0, self.beat_flash_timer - dt)
            
        # Update road pulse
        if self.enable_road_pulse:
            target_pulse = 0.0
            if beat_info.is_beat:
                target_pulse = self.road_pulse_amount * beat_info.beat_strength
            else:
                # Gentle sine wave between beats
                target_pulse = math.sin(beat_info.beat_phase * math.pi) * self.road_pulse_amount * 0.3
                
            # Smooth the transition
            self.road_pulse_smooth += (target_pulse - self.road_pulse_smooth) * 8.0 * dt
            
        # Update speed lines
        if self.enable_speed_lines:
            self._update_speed_lines(dt, beat_info)
            
        # Update screen shake
        if self.enable_screen_shake and self.screen_shake_amount > 0:
            self.screen_shake_amount -= self.screen_shake_decay * dt
            self.screen_shake_amount = max(0, self.screen_shake_amount)
            
        # Update color pulse
        if beat_info.is_downbeat:
            self.color_pulse_target = 1.0
        else:
            self.color_pulse_target *= 0.95
        self.color_pulse_amount += (self.color_pulse_target - self.color_pulse_amount) * 10.0 * dt
        
    def render_beat_indicator(self, screen: pygame.Surface, beat_info: BeatInfo):
        """Render the beat indicator on screen.
        
        Args:
            screen: Pygame surface to draw on
            beat_info: Current beat information
        """
        # Calculate indicator brightness
        if self.beat_flash_timer > 0:
            brightness = 255
        else:
            # Pulse with beat phase
            brightness = int(100 + 155 * (1.0 - beat_info.beat_phase))
            
        # Different colors for different beat numbers
        if beat_info.beat_number == 1:
            color = (brightness, brightness // 2, brightness // 2)  # Red for downbeat
        elif beat_info.beat_number == 3:
            color = (brightness // 2, brightness, brightness // 2)  # Green for secondary
        else:
            color = (brightness, brightness, brightness)  # White for weak beats
            
        # Draw the indicator
        pygame.draw.circle(screen, color, self.beat_indicator_pos, 
                          self.beat_indicator_size)
        
        # Draw beat number
        font = pygame.font.Font(None, 24)
        text = font.render(str(beat_info.beat_number), True, (255, 255, 255))
        text_rect = text.get_rect(center=self.beat_indicator_pos)
        screen.blit(text, text_rect)
        
        # Draw BPM
        bpm_text = font.render(f"{beat_info.bpm:.0f} BPM", True, (255, 255, 255))
        bpm_rect = bpm_text.get_rect(midleft=(self.beat_indicator_pos[0] + 30, 
                                              self.beat_indicator_pos[1]))
        screen.blit(bpm_text, bpm_rect)
        
    def get_road_width_modifier(self) -> float:
        """Get current road width modification from pulse effect.
        
        Returns:
            Pixel offset to add to road width
        """
        return self.road_pulse_smooth if self.enable_road_pulse else 0.0
        
    def get_screen_shake_offset(self) -> Tuple[int, int]:
        """Get current screen shake offset.
        
        Returns:
            (x, y) pixel offset for screen shake
        """
        if not self.enable_screen_shake or self.screen_shake_amount <= 0:
            return (0, 0)
            
        # Random shake within amount
        import random
        x_shake = random.randint(-int(self.screen_shake_amount), int(self.screen_shake_amount))
        y_shake = random.randint(-int(self.screen_shake_amount), int(self.screen_shake_amount))
        return (x_shake, y_shake)
        
    def trigger_beat_effect(self, strength: float = 1.0):
        """Trigger a beat-synchronized visual effect.
        
        Args:
            strength: Effect strength (0.0-1.0)
        """
        # Flash beat indicator
        self.beat_flash_timer = self.beat_flash_duration * (1 + strength)
        
        # Add screen shake on strong beats
        if self.enable_screen_shake and strength > 0.7:
            self.screen_shake_amount = 5.0 * strength
            
        # Spawn speed lines on downbeats
        if self.enable_speed_lines and strength > 0.5:
            self._spawn_speed_line_burst(int(5 * strength))
            
    def render_speed_lines(self, screen: pygame.Surface):
        """Render speed line effects.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.enable_speed_lines:
            return
            
        for line in self.speed_lines:
            alpha = int(255 * (1.0 - line.progress))
            color = (*line.color, alpha) if len(line.color) == 3 else line.color
            
            # Calculate line position
            start_y = int(line.y_start + (self.screen_height - line.y_start) * line.progress)
            end_y = start_y + line.length
            
            # Draw with decreasing width
            width = max(1, int(line.width * (1.0 - line.progress)))
            pygame.draw.line(screen, color[:3], (line.x, start_y), (line.x, end_y), width)
            
    def _update_speed_lines(self, dt: float, beat_info: BeatInfo):
        """Update speed line animations.
        
        Args:
            dt: Delta time
            beat_info: Current beat information
        """
        # Update existing lines
        lines_to_remove = []
        for i, line in enumerate(self.speed_lines):
            line.progress += line.speed * dt
            if line.progress >= 1.0:
                lines_to_remove.append(i)
                
        # Remove completed lines
        for i in reversed(lines_to_remove):
            del self.speed_lines[i]
            
        # Spawn new lines on beats
        if beat_info.is_beat and len(self.speed_lines) < self.max_speed_lines:
            if beat_info.is_downbeat:
                self._spawn_speed_line_burst(3)
            else:
                self._spawn_speed_line()
                
    def _spawn_speed_line(self):
        """Spawn a single speed line."""
        import random
        line = SpeedLine(
            x=random.randint(100, self.screen_width - 100),
            y_start=self.screen_height // 3,
            length=random.randint(20, 60),
            width=random.randint(2, 4),
            speed=random.uniform(2.0, 4.0),
            color=(255, 255, 255)
        )
        self.speed_lines.append(line)
        
    def _spawn_speed_line_burst(self, count: int):
        """Spawn multiple speed lines at once.
        
        Args:
            count: Number of lines to spawn
        """
        for _ in range(count):
            if len(self.speed_lines) < self.max_speed_lines:
                self._spawn_speed_line()
                
    def get_color_tint(self) -> Tuple[float, float, float]:
        """Get current color tint for rhythm pulsing.
        
        Returns:
            RGB multipliers (0.8-1.2)
        """
        pulse = self.color_pulse_amount * 0.1
        return (1.0 + pulse, 1.0 + pulse * 0.5, 1.0)
        
    def set_road_pulse_amount(self, amount: float):
        """Set the road pulse effect strength.
        
        Args:
            amount: Pulse amount in pixels
        """
        self.road_pulse_amount = max(0, min(50, amount))
        
    def toggle_effects(self, effect_name: str):
        """Toggle a visual effect on/off.
        
        Args:
            effect_name: Name of effect to toggle
        """
        if effect_name == "road_pulse":
            self.enable_road_pulse = not self.enable_road_pulse
        elif effect_name == "speed_lines":
            self.enable_speed_lines = not self.enable_speed_lines
        elif effect_name == "screen_shake":
            self.enable_screen_shake = not self.enable_screen_shake
            

class SpeedLine:
    """Represents a single speed line effect."""
    
    def __init__(self, x: int, y_start: int, length: int, width: int, 
                 speed: float, color: Tuple[int, int, int]):
        self.x = x
        self.y_start = y_start
        self.length = length
        self.width = width
        self.speed = speed
        self.color = color
        self.progress = 0.0  # 0.0 = top, 1.0 = bottom