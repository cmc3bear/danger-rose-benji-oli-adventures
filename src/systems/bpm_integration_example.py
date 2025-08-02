"""Example integration of BPM system with Drive minigame.

This file shows how to integrate the BPM synchronization system
with the existing Drive scene without major refactoring.
"""

import pygame
from typing import Optional

from src.systems import (
    BPMTracker, 
    RhythmicTrafficController, 
    RhythmVisualFeedback,
    RhythmConfiguration,
    SpawnPattern
)


class BPMDriveIntegration:
    """Integration layer for adding BPM sync to Drive minigame."""
    
    def __init__(self, drive_scene):
        """Initialize BPM integration with Drive scene.
        
        Args:
            drive_scene: The DriveGame instance to enhance
        """
        self.drive_scene = drive_scene
        
        # Initialize BPM components
        self.config = RhythmConfiguration()
        self.bpm_tracker: Optional[BPMTracker] = None
        self.traffic_controller: Optional[RhythmicTrafficController] = None
        self.visual_feedback: Optional[RhythmVisualFeedback] = None
        
        # Integration state
        self.bpm_enabled = False
        self.original_spawn_interval = 2.5
        self.original_spawn_probability = 0.5
        
    def initialize(self, track_bpm: float = 120.0):
        """Initialize BPM systems with a specific tempo.
        
        Args:
            track_bpm: BPM of the current music track
        """
        # Create BPM tracker
        self.bpm_tracker = BPMTracker(track_bpm)
        
        # Create traffic controller
        self.traffic_controller = RhythmicTrafficController(self.bpm_tracker)
        self.traffic_controller.set_spawn_pattern(SpawnPattern.DOWNBEATS)
        
        # Create visual feedback
        self.visual_feedback = RhythmVisualFeedback(
            self.drive_scene.screen_width,
            self.drive_scene.screen_height
        )
        
        # Store original values
        self.original_spawn_interval = getattr(self.drive_scene, 'spawn_interval', 2.5)
        
        self.bpm_enabled = True
        
    def update(self, dt: float):
        """Update BPM systems.
        
        Args:
            dt: Delta time since last update
        """
        if not self.bpm_enabled or not self.bpm_tracker:
            return
            
        # Update BPM tracker
        beat_events = self.bpm_tracker.update(dt)
        beat_info = self.bpm_tracker.get_beat_info()
        
        # Update traffic controller
        rhythm_data = self.traffic_controller.update(dt)
        
        # Update visual feedback
        self.visual_feedback.update(dt, beat_info)
        
        # Apply rhythm modifications to Drive scene
        self._apply_rhythm_modifications(rhythm_data)
        
        # Handle beat events
        for event in beat_events:
            if event.is_downbeat:
                self.visual_feedback.trigger_beat_effect(event.strength)
                
    def _apply_rhythm_modifications(self, rhythm_data: dict):
        """Apply rhythm-based modifications to the Drive scene.
        
        Args:
            rhythm_data: Dictionary of rhythm modifications
        """
        # Modify traffic spawning
        if rhythm_data["should_spawn"] and len(self.drive_scene.npc_cars) < self.drive_scene.max_traffic_cars:
            # Force a spawn on the beat
            self.drive_scene._spawn_npc_car()
            self.drive_scene.traffic_spawn_timer = 0.0
            
        # Apply speed modulation to existing traffic
        speed_modifier = rhythm_data["speed_modifier"]
        for car in self.drive_scene.npc_cars:
            # Add personality-based modifier
            personality = getattr(car, 'personality', 'normal')
            personality_mod = self.traffic_controller.get_personality_speed_modifier(
                personality, rhythm_data["beat_info"]
            )
            
            # Apply combined speed modification
            total_modifier = 1.0 + speed_modifier + personality_mod
            car.speed = car.base_speed * total_modifier  # Assumes we store base_speed
            
        # Modify road width with pulse effect
        if hasattr(self.drive_scene, 'road_width'):
            pulse_offset = self.visual_feedback.get_road_width_modifier()
            self.drive_scene.road_width = self.drive_scene.base_road_width + int(pulse_offset)
            
    def render(self, screen: pygame.Surface):
        """Render BPM visual elements.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.bpm_enabled or not self.visual_feedback:
            return
            
        # Get beat info for rendering
        beat_info = self.bpm_tracker.get_beat_info()
        
        # Apply screen shake if enabled
        shake_x, shake_y = self.visual_feedback.get_screen_shake_offset()
        if shake_x or shake_y:
            # This would require modifying the Drive scene's rendering
            # For now, just store the offset
            pass
            
        # Render speed lines (before UI elements)
        self.visual_feedback.render_speed_lines(screen)
        
        # Render beat indicator (on top of everything)
        if self.config.beat_indicator_enabled:
            self.visual_feedback.render_beat_indicator(screen, beat_info)
            
    def handle_event(self, event: pygame.event.Event):
        """Handle input events for BPM system.
        
        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            # Toggle rhythm effects
            if event.key == pygame.K_F1:
                self.config.rhythm_enabled = not self.config.rhythm_enabled
                print(f"Rhythm sync: {'ON' if self.config.rhythm_enabled else 'OFF'}")
                
            # Change spawn patterns
            elif event.key == pygame.K_F2:
                patterns = list(SpawnPattern)
                current_idx = patterns.index(self.traffic_controller.spawn_pattern)
                new_pattern = patterns[(current_idx + 1) % len(patterns)]
                self.traffic_controller.set_spawn_pattern(new_pattern)
                print(f"Spawn pattern: {new_pattern.value}")
                
            # Adjust rhythm intensity
            elif event.key == pygame.K_F3:
                self.config.rhythm_intensity = (self.config.rhythm_intensity + 0.2) % 1.2
                print(f"Rhythm intensity: {self.config.rhythm_intensity:.1f}")
                
            # Toggle visual effects
            elif event.key == pygame.K_F4:
                self.visual_feedback.toggle_effects("road_pulse")
                self.visual_feedback.toggle_effects("speed_lines")
                print("Toggled visual effects")
                
    def sync_to_music_position(self, position: float):
        """Synchronize BPM tracker to current music position.
        
        Args:
            position: Current position in music (seconds)
        """
        if self.bpm_tracker:
            self.bpm_tracker.sync_to_audio_position(position)
            
    def set_track_bpm(self, bpm: float):
        """Update the BPM for a new track.
        
        Args:
            bpm: New BPM value
        """
        if self.bpm_tracker:
            self.bpm_tracker.set_bpm(bpm)
            
    def cleanup(self):
        """Clean up BPM systems and restore original values."""
        if hasattr(self.drive_scene, 'spawn_interval'):
            self.drive_scene.spawn_interval = self.original_spawn_interval
        self.bpm_enabled = False


# Example usage in DriveGame class:
"""
# In DriveGame.__init__():
self.bpm_integration = BPMDriveIntegration(self)

# In DriveGame._on_track_selected():
track_bpm = track.bpm  # From MusicTrack
self.bpm_integration.initialize(track_bpm)

# In DriveGame.update():
self.bpm_integration.update(dt)

# In DriveGame.draw():
# ... existing rendering ...
self.bpm_integration.render(screen)

# In DriveGame.handle_event():
self.bpm_integration.handle_event(event)
"""