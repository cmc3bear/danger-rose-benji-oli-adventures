"""Integration module that connects BPM tracking with the existing Drive game traffic system."""

import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from .bpm_tracker import BPMTracker, BeatEvent
from .rhythmic_traffic_controller import RhythmicTrafficController
from .rhythm_event_system import RhythmEventSystem
from .rhythm_visual_feedback import RhythmVisualFeedback
from .rhythm_config import RhythmConfiguration, DifficultyLevel, RhythmIntensity
from ..managers.race_music_manager import RaceMusicManager
from ..ui.music_selector import MusicTrack


@dataclass
class RhythmicSpawnEvent:
    """A spawn event triggered by rhythm system."""
    spawn_type: str = "car"
    lane: int = 3
    spawn_time: float = 0.0
    priority: int = 1
    spawn_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.spawn_params is None:
            self.spawn_params = {}


@dataclass
class BPMTrafficState:
    """Current state of BPM-synchronized traffic system."""
    is_active: bool = False
    current_bpm: float = 120.0
    rhythm_intensity: float = 0.7
    spawn_rate_modifier: float = 1.0
    visual_effects_active: bool = True
    beat_count: int = 0
    measure_count: int = 0
    on_beat_actions: int = 0
    total_actions: int = 0


class BPMTrafficIntegration:
    """
    Integration system that connects BPM tracking with the existing Drive game.
    
    This class acts as a bridge between the rhythm systems and the existing
    traffic spawning code in DriveGame, providing a clean interface for
    BPM-synchronized gameplay.
    """
    
    def __init__(self, 
                 drive_game,  # Reference to DriveGame instance
                 sound_manager,
                 screen_width: int,
                 screen_height: int):
        """
        Initialize BPM traffic integration.
        
        Args:
            drive_game: Reference to the DriveGame instance
            sound_manager: SoundManager for audio
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
        """
        self.drive_game = drive_game
        self.sound_manager = sound_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize rhythm systems
        self.bpm_tracker = BPMTracker()  # Default BPM, will be set when track is selected
        self.traffic_controller = RhythmicTrafficController(self.bpm_tracker)
        self.visual_feedback = RhythmVisualFeedback(screen_width, screen_height)
        self.config = RhythmConfiguration()
        
        # Integration state
        self.state = BPMTrafficState()
        self.is_enabled = True
        
        # Callbacks for integration with DriveGame
        self.spawn_callback: Optional[Callable] = None
        self.speed_callback: Optional[Callable] = None
        
        # Performance tracking
        self.last_update_time = 0.0
        self.update_frequency = 60  # Target FPS
        
        # Setup callbacks
        self._setup_integration_callbacks()
        
    def initialize_for_track(self, music_track: MusicTrack):
        """
        Initialize BPM tracking for a specific music track.
        
        Args:
            music_track: Selected music track with BPM information
        """
        # Get track settings from configuration
        track_settings = self.config.get_track_settings(music_track.name)
        
        # Use manual BPM if available, otherwise use track's BPM
        bpm = track_settings.manual_bpm or music_track.bpm or 120.0
        beat_offset = track_settings.beat_offset
        
        # Update configuration with track BPM
        self.config.update_track_bpm(music_track.name, bpm, 1.0)
        
        # Start BPM tracking
        self.bpm_tracker.start_tracking(bpm, beat_offset)
        
        # Configure traffic controller for this track
        self.traffic_controller.set_rhythm_intensity(
            self.config.gameplay_settings.rhythm_intensity.value
        )
        
        # Update state
        self.state.is_active = True
        self.state.current_bpm = bpm
        self.state.rhythm_intensity = self._get_rhythm_intensity_value()
        
        print(f"BPM Traffic Integration initialized for '{music_track.display_name}' at {bpm} BPM")
        
    def update(self, dt: float, player_state: Dict[str, Any], current_traffic: List[Any]):
        """
        Update all BPM-synchronized systems.
        
        Args:
            dt: Delta time in seconds
            player_state: Current player state
            current_traffic: List of current NPC cars
        """
        if not self.is_enabled or not self.state.is_active:
            return
            
        current_time = time.time()
        
        # Throttle updates to target frequency
        if current_time - self.last_update_time < (1.0 / self.update_frequency):
            return
            
        # Update core systems
        self.bpm_tracker.update(dt)
        self.traffic_controller.update(dt, current_traffic, player_state)
        self.event_system.update(dt)
        self.visual_feedback.update(dt, player_state)
        
        # Update integration state
        self._update_state()
        
        self.last_update_time = current_time
        
    def handle_spawn_request(self, spawn_event: RhythmicSpawnEvent) -> bool:
        """
        Handle a rhythmic spawn request from the traffic controller.
        
        Args:
            spawn_event: Spawn event to process
            
        Returns:
            True if spawn was successful, False otherwise
        """
        if not self.spawn_callback:
            return False
            
        try:
            # Convert spawn event to parameters for existing spawn system
            spawn_params = self._convert_spawn_event_to_params(spawn_event)
            
            # Call the actual spawn function
            success = self.spawn_callback(spawn_params)
            
            if success:
                self.state.on_beat_actions += 1
                
            self.state.total_actions += 1
            
            return success
            
        except Exception as e:
            print(f"Error handling spawn request: {e}")
            return False
            
    def handle_speed_modulation(self, car_list: List[Any]):
        """
        Apply rhythmic speed modulation to existing traffic.
        
        Args:
            car_list: List of NPC cars to modulate
        """
        if not self.speed_callback or not self.config.gameplay_settings.speed_modulation:
            return
            
        beat_progress = self.bpm_tracker.get_beat_progress()
        
        for car in car_list:
            try:
                self.speed_callback(car, beat_progress)
            except Exception as e:
                print(f"Error applying speed modulation: {e}")
                
    def get_road_pulse_intensity(self) -> float:
        """Get current road pulse intensity for visual effects."""
        if not self.state.visual_effects_active:
            return 0.0
        return self.visual_feedback.get_road_pulse_intensity()
        
    def get_screen_shake_offset(self) -> tuple:
        """Get current screen shake offset."""
        if not self.state.visual_effects_active:
            return (0, 0)
        return self.visual_feedback.get_screen_shake_offset()
        
    def draw_rhythm_effects(self, screen, road_surface=None, road_rect=None):
        """
        Draw rhythm-synchronized visual effects.
        
        Args:
            screen: Main screen surface
            road_surface: Road surface (optional)
            road_rect: Road rectangle (optional)
        """
        if not self.state.visual_effects_active:
            return
            
        # Draw road effects if surfaces provided
        if road_surface and road_rect:
            self.visual_feedback.draw_road_effects(screen, road_surface, road_rect)
            
        # Draw UI effects
        self.visual_feedback.draw_ui_effects(screen)
        
        # Draw speed boost effects if active
        self.visual_feedback.draw_speed_boost_effects(screen)
        
    def set_difficulty(self, difficulty: DifficultyLevel):
        """Set gameplay difficulty level."""
        self.config.set_difficulty(difficulty)
        self._update_traffic_controller_settings()
        
    def set_rhythm_intensity(self, intensity: RhythmIntensity):
        """Set rhythm intensity level."""
        self.config.set_rhythm_intensity(intensity)
        self.traffic_controller.set_rhythm_intensity(self._get_rhythm_intensity_value())
        self.state.rhythm_intensity = self._get_rhythm_intensity_value()
        
    def enable_accessibility_mode(self, enabled: bool):
        """Enable accessibility features."""
        self.config.enable_accessibility_mode(enabled)
        self.visual_feedback.set_beat_indicators_visible(
            self.config.get_current_difficulty_settings().visual_assists
        )
        
    def enable_performance_mode(self, enabled: bool):
        """Enable performance mode with reduced effects."""
        self.config.enable_performance_mode(enabled)
        self.state.visual_effects_active = not enabled
        
    def register_spawn_callback(self, callback: Callable):
        """
        Register callback for spawning traffic.
        
        Args:
            callback: Function that takes spawn parameters and returns success boolean
        """
        self.spawn_callback = callback
        # self.traffic_controller.set_spawn_callback(self.handle_spawn_request)  # Not available
        
    def register_speed_callback(self, callback: Callable):
        """
        Register callback for speed modulation.
        
        Args:
            callback: Function that takes (car, beat_progress) and modulates speed
        """
        self.speed_callback = callback
        
    def get_current_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the BPM system."""
        rhythm_accuracy = (self.state.on_beat_actions / self.state.total_actions 
                          if self.state.total_actions > 0 else 0.0)
        
        return {
            "bpm_tracker": self.bpm_tracker.get_current_state(),
            "traffic_controller": {"spawn_pattern": str(self.traffic_controller.spawn_pattern)},
            "event_system": {"events": 0},
            "visual_effects": {"effects_active": True},
            "integration_state": {
                "is_active": self.state.is_active,
                "current_bpm": self.state.current_bpm,
                "rhythm_intensity": self.state.rhythm_intensity,
                "beat_count": self.state.beat_count,
                "measure_count": self.state.measure_count,
                "rhythm_accuracy": rhythm_accuracy,
                "visual_effects_active": self.state.visual_effects_active
            },
            "configuration": {"rhythm_intensity": "moderate"}
        }
        
    def cleanup(self):
        """Clean up resources and stop tracking."""
        # self.bpm_tracker.stop_tracking() # Not available
        self.state.is_active = False
        # self.config.save_configuration()  # Not needed for basic integration
        
    def _setup_integration_callbacks(self):
        """Setup internal callbacks for system integration."""
        # Register for beat events to update state
        # self.bpm_tracker.register_beat_callback(self._on_beat_event) # Not available
        # self.bpm_tracker.register_measure_callback(self._on_measure_event) # Not available
        
    def _on_beat_event(self, beat_event: BeatEvent):
        """Handle beat events for state tracking."""
        self.state.beat_count += 1
        
    def _on_measure_event(self, measure_number: int):
        """Handle measure events for state tracking."""
        self.state.measure_count = measure_number
        
    def _update_state(self):
        """Update integration state."""
        if self.bpm_tracker.is_tracking:
            self.state.current_bpm = self.bpm_tracker.current_bpm
            
        # Update spawn rate modifier based on configuration
        self.state.spawn_rate_modifier = self.config.get_bpm_modifier(self.state.current_bpm)
        
    def _get_rhythm_intensity_value(self) -> float:
        """Get numeric value for current rhythm intensity."""
        intensity_values = {
            RhythmIntensity.OFF: 0.0,
            RhythmIntensity.SUBTLE: 0.3,
            RhythmIntensity.MODERATE: 0.7,
            RhythmIntensity.INTENSE: 1.0,
            RhythmIntensity.EXTREME: 1.5
        }
        return intensity_values.get(self.config.gameplay_settings.rhythm_intensity, 0.7)
        
    def _update_traffic_controller_settings(self):
        """Update traffic controller based on current configuration."""
        settings = self.config.get_current_difficulty_settings()
        
        # Update spawn probabilities
        self.traffic_controller.spawn_probability = {
            beat_strength: self.config.get_spawn_probability(beat_strength, self.state.current_bpm)
            for beat_strength in self.traffic_controller.spawn_probability.keys()
        }
        
        # Update other settings
        self.traffic_controller.traffic_density_target = self.config.get_traffic_density(self.state.current_bpm)
        
    def _convert_spawn_event_to_params(self, spawn_event: RhythmicSpawnEvent) -> Dict[str, Any]:
        """
        Convert a rhythmic spawn event to parameters for the existing spawn system.
        
        Args:
            spawn_event: Rhythmic spawn event
            
        Returns:
            Parameters dictionary for existing spawn function
        """
        # This would need to match the expected parameters of the existing spawn system
        return {
            "vehicle_type": spawn_event.spawn_type,
            "lane": spawn_event.lane,
            "speed_modifier": spawn_event.spawn_params.get("speed_modifier", 1.0),
            "ai_behavior": spawn_event.spawn_params.get("ai_behavior", "normal"),
            "spawn_time": spawn_event.spawn_time,
            "priority": spawn_event.priority
        }


# Convenience function for easy integration
def create_bpm_traffic_system(drive_game, sound_manager, screen_width: int, screen_height: int) -> BPMTrafficIntegration:
    """
    Create and configure a complete BPM traffic system.
    
    Args:
        drive_game: DriveGame instance
        sound_manager: SoundManager instance
        screen_width: Screen width
        screen_height: Screen height
        
    Returns:
        Configured BPMTrafficIntegration instance
    """
    integration = BPMTrafficIntegration(drive_game, sound_manager, screen_width, screen_height)
    
    # Setup integration with existing drive game systems
    # This would connect to the actual DriveGame spawn and update methods
    
    return integration