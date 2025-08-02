"""
Example of how to integrate the BPM traffic system with the existing DriveGame.

This example shows how to modify the DriveGame class to use BPM-synchronized
traffic spawning and visual effects.
"""

import pygame
import time
from typing import Dict, Any, List

# Import the BPM system
from src.systems import (
    BPMTrafficIntegration,
    create_bpm_traffic_system,
    DifficultyLevel,
    RhythmIntensity
)

# Import existing game components
from src.scenes.drive import DriveGame, NPCCar
from src.managers.sound_manager import SoundManager
from src.ui.music_selector import MusicTrack


class BPMEnhancedDriveGame(DriveGame):
    """
    Enhanced DriveGame with BPM-synchronized traffic system.
    
    This example shows how to integrate the BPM system with minimal
    changes to the existing DriveGame code.
    """
    
    def __init__(self, scene_manager):
        """Initialize the enhanced drive game."""
        # Initialize parent class
        super().__init__(scene_manager)
        
        # Initialize BPM traffic system
        self.bpm_system = create_bmp_traffic_system(
            drive_game=self,
            sound_manager=self.scene_manager.sound_manager,
            screen_width=self.screen_width,
            screen_height=self.screen_height
        )
        
        # Register callbacks for integration
        self._setup_bmp_callbacks()
        
        # Track whether BPM system is active
        self.bmp_enabled = True
        self.show_bmp_debug = False
        
    def _setup_bmp_callbacks(self):
        """Setup callbacks for BPM system integration."""
        # Register spawn callback
        self.bpm_system.register_spawn_callback(self._handle_rhythmic_spawn)
        
        # Register speed modulation callback
        self.bmp_system.register_speed_callback(self._handle_speed_modulation)
        
    def _handle_rhythmic_spawn(self, spawn_params: Dict[str, Any]) -> bool:
        """
        Handle a rhythmic spawn request.
        
        Args:
            spawn_params: Spawn parameters from BPM system
            
        Returns:
            True if spawn was successful
        """
        try:
            # Convert BPM spawn parameters to existing spawn format
            lane = spawn_params.get("lane", 3)
            vehicle_type = spawn_params.get("vehicle_type", "car")
            speed_modifier = spawn_params.get("speed_modifier", 1.0)
            ai_behavior = spawn_params.get("ai_behavior", "normal")
            
            # Create NPC car using existing logic but with BPM parameters
            npc_car = self._create_rhythmic_npc_car(
                lane=lane,
                vehicle_type=vehicle_type,
                speed_modifier=speed_modifier,
                ai_behavior=ai_behavior
            )
            
            if npc_car:
                self.npc_cars.append(npc_car)
                return True
                
        except Exception as e:
            print(f"Error handling rhythmic spawn: {e}")
            
        return False
        
    def _create_rhythmic_npc_car(self, 
                                lane: int, 
                                vehicle_type: str,
                                speed_modifier: float,
                                ai_behavior: str) -> NPCCar:
        """
        Create an NPC car with rhythm-based parameters.
        
        Args:
            lane: Target lane (1-4)
            vehicle_type: Type of vehicle ("car" or "truck")
            speed_modifier: Speed multiplier
            ai_behavior: AI behavior type
            
        Returns:
            Created NPCCar instance or None if creation failed
        """
        # Use existing lane position calculation logic
        x_position = self._calculate_lane_position(lane)
        
        # Determine spawn position (ahead or behind player)
        if lane in [3, 4]:  # Same direction as player
            y_position = 200.0  # Spawn ahead
            direction = 1
            speed = 0.8 * speed_modifier
        else:  # Oncoming traffic
            y_position = 400.0  # Spawn far ahead
            direction = -1
            speed = 0.7 * speed_modifier
            
        # Create car with rhythm-enhanced properties
        if vehicle_type == "truck":
            width, height = 40, 80
            collision_zone = (40, 80)
            color = (100, 100, 150)  # Truck color
        else:
            width, height = 32, 48
            collision_zone = (32, 48)
            color = (150, 100, 100)  # Car color
            
        npc_car = NPCCar(
            x=x_position,
            y=y_position,
            lane=lane,
            speed=speed,
            color=color,
            vehicle_type=vehicle_type,
            direction=direction,
            width=width,
            height=height,
            collision_zone=collision_zone,
            ai_state=ai_behavior
        )
        
        # Add rhythm-specific attributes
        npc_car.rhythmic_speed_modifier = speed_modifier
        npc_car.base_speed_modifier = speed_modifier
        npc_car.rhythm_spawned = True
        
        return npc_car
        
    def _handle_speed_modulation(self, car: NPCCar, beat_progress: float):
        """
        Apply rhythmic speed modulation to a car.
        
        Args:
            car: NPC car to modulate
            beat_progress: Current beat progress (0.0-1.0)
        """
        if not hasattr(car, 'rhythmic_speed_modifier'):
            return
            
        # Create subtle speed variation synchronized to beat
        import math
        speed_wave = math.sin(beat_progress * 2 * math.pi) * 0.1
        
        # Apply modulation to base speed
        base_modifier = getattr(car, 'base_speed_modifier', 1.0)
        car.rhythmic_speed_modifier = base_modifier + speed_wave
        
        # Update actual car speed (this would depend on how speed is handled)
        # car.speed *= car.rhythmic_speed_modifier
        
    def _calculate_lane_position(self, lane: int) -> float:
        """
        Calculate normalized x position for a lane.
        
        Args:
            lane: Lane number (1-4)
            
        Returns:
            Normalized x position (0.0-1.0)
        """
        # This should use the same logic as the existing spawn system
        # For this example, we'll use simplified lane positions
        lane_positions = {
            1: 0.2,   # Left oncoming
            2: 0.35,  # Right oncoming
            3: 0.65,  # Left player direction
            4: 0.8    # Right player direction
        }
        return lane_positions.get(lane, 0.5)
        
    def start_race_music(self, music_track: MusicTrack):
        """
        Start race music with BPM tracking.
        
        Args:
            music_track: Selected music track
        """
        # Call parent method to start music
        super().start_race_music(music_track)
        
        # Initialize BPM system for this track
        if self.bmp_enabled:
            self.bmp_system.initialize_for_track(music_track)
            print(f"BPM system activated for {music_track.display_name}")
            
    def update(self, dt: float):
        """Update game with BPM synchronization."""
        # Call parent update
        super().update(dt)
        
        # Update BPM system
        if self.bmp_enabled and hasattr(self, 'bmp_system'):
            player_state = {
                "x": self.player_x,
                "speed": self.player_speed,
                "boost_active": getattr(self, 'boost_active', False)
            }
            
            self.bmp_system.update(dt, player_state, self.npc_cars)
            
            # Apply speed modulation to existing traffic
            self.bmp_system.handle_speed_modulation(self.npc_cars)
            
    def draw(self, screen: pygame.Surface):
        """Draw game with rhythm visual effects."""
        # Get screen shake offset before drawing
        if self.bmp_enabled and hasattr(self, 'bpm_system'):
            shake_offset = self.bmp_system.get_screen_shake_offset()
            
            # Apply screen shake by offsetting the entire screen
            if shake_offset != (0, 0):
                # Create offset surface
                offset_surface = pygame.Surface((self.screen_width, self.screen_height))
                
                # Draw to offset surface first
                super().draw(offset_surface)
                
                # Blit with shake offset
                screen.blit(offset_surface, shake_offset)
            else:
                # Normal drawing
                super().draw(screen)
                
            # Draw rhythm effects on top
            self.bmp_system.draw_rhythm_effects(screen)
            
            # Draw debug info if enabled
            if self.show_bmp_debug:
                self._draw_bmp_debug_info(screen)
        else:
            # Normal drawing without BPM effects
            super().draw(screen)
            
    def _draw_bmp_debug_info(self, screen: pygame.Surface):
        """Draw BPM debug information."""
        if not hasattr(self, 'bmp_system'):
            return
            
        # Get current stats
        stats = self.bmp_system.get_current_stats()
        
        # Setup font
        font = pygame.font.Font(None, 24)
        y_offset = 10
        
        # Display key information
        debug_info = [
            f"BPM: {stats['bmp_tracker']['bpm']:.1f}",
            f"Beat: {stats['bmp_tracker']['current_beat']}",
            f"Measure: {stats['bmp_tracker']['current_measure']}",
            f"Time to Beat: {stats['bmp_tracker']['time_to_next_beat']:.2f}s",
            f"Rhythm Accuracy: {stats['integration_state']['rhythm_accuracy']:.1%}",
            f"Active Effects: {stats['visual_effects']['active_pulses']}",
            f"Traffic Pattern: {stats['traffic_controller'].get('current_pattern', 'N/A')}"
        ]
        
        for info in debug_info:
            text_surface = font.render(info, True, (255, 255, 255))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 25
            
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle events including BPM system controls."""
        result = super().handle_event(event)
        
        # Add BPM system controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                # Toggle BPM system
                self.bmp_enabled = not self.bmp_enabled
                print(f"BPM system {'enabled' if self.bpm_enabled else 'disabled'}")
            elif event.key == pygame.K_F2:
                # Toggle debug display
                self.show_bmp_debug = not self.show_bmp_debug
            elif event.key == pygame.K_F3:
                # Cycle difficulty
                difficulties = list(DifficultyLevel)
                current_config = self.bmp_system.config.current_difficulty
                current_index = difficulties.index(current_config)
                next_index = (current_index + 1) % len(difficulties)
                self.bmp_system.set_difficulty(difficulties[next_index])
                print(f"Difficulty set to {difficulties[next_index].value}")
            elif event.key == pygame.K_F4:
                # Cycle rhythm intensity
                intensities = list(RhythmIntensity)
                current_intensity = self.bmp_system.config.gameplay_settings.rhythm_intensity
                current_index = intensities.index(current_intensity)
                next_index = (current_index + 1) % len(intensities)
                self.bmp_system.set_rhythm_intensity(intensities[next_index])
                print(f"Rhythm intensity set to {intensities[next_index].value}")
                
        return result
        
    def cleanup(self):
        """Clean up resources including BPM system."""
        if hasattr(self, 'bmp_system'):
            self.bmp_system.cleanup()
        super().cleanup()


# Usage example
def create_enhanced_drive_game(scene_manager):
    """
    Create an enhanced drive game with BPM synchronization.
    
    Args:
        scene_manager: Scene manager instance
        
    Returns:
        BPMEnhancedDriveGame instance
    """
    return BPMEnhancedDriveGame(scene_manager)


# Integration notes for existing DriveGame class:
"""
To integrate this BPM system with the existing DriveGame, you would:

1. Add BPM system initialization in __init__:
   self.bmp_system = create_bpm_traffic_system(...)

2. Modify the _spawn_npc_car method to optionally use BPM spawning:
   if self.bpm_enabled and should_use_rhythmic_spawn():
       # Let BPM system handle spawning
       return
   # Otherwise use existing spawn logic

3. Add BPM system update in the main update method:
   self.bmp_system.update(dt, player_state, self.npc_cars)

4. Enhance the draw method to include rhythm effects:
   self.bmp_system.draw_rhythm_effects(screen)

5. Add music track initialization:
   self.bmp_system.initialize_for_track(selected_track)

6. Optional: Add configuration UI for BPM settings

The system is designed to be non-intrusive and can be enabled/disabled
without affecting the existing gameplay.
"""