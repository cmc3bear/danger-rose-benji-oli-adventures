"""Racing-specific music management with dynamic playback features."""

import pygame
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

from src.managers.sound_manager import SoundManager
from src.ui.music_selector import MusicTrack
from src.utils.asset_paths import get_music_path, get_sfx_path
from src.config.constants import AUDIO_FADE_TIME


@dataclass
class RaceState:
    """Current state of the race for dynamic music adjustments."""
    speed: float = 0.0          # Current speed (0.0 to 1.0)
    position: int = 1           # Current race position
    total_racers: int = 1       # Total number of racers
    time_remaining: float = 0.0 # Time remaining in race
    is_boost: bool = False      # Whether boost/turbo is active
    is_crash: bool = False      # Whether player just crashed
    is_final_lap: bool = False  # Whether it's the final lap
    is_victory: bool = False    # Whether player won
    is_game_over: bool = False  # Whether race is over


class RaceMusicManager:
    """
    Enhanced music manager for racing games with dynamic features.
    
    Features:
    - Seamless music looping
    - Dynamic tempo/pitch adjustment based on speed
    - Special stingers for events (crash, boost, victory)
    - Music ducking for important sounds
    - Smooth transitions between race states
    """
    
    def __init__(self, sound_manager: SoundManager):
        """
        Initialize the race music manager.
        
        Args:
            sound_manager: Base SoundManager instance
        """
        self.sound_manager = sound_manager
        
        # Current track state
        self.current_track: Optional[MusicTrack] = None
        self.is_playing = False
        self.base_volume = 0.7
        self.current_volume = self.base_volume
        
        # Dynamic music parameters
        self.base_pitch = 1.0
        self.current_pitch = 1.0
        self.pitch_range = (0.85, 1.15)  # Min/max pitch multipliers
        self.speed_sensitivity = 0.3     # How much speed affects pitch
        
        # Music looping state
        self.loop_start_time = 0.0
        self.loop_end_time = 0.0
        self.music_start_time = 0.0
        
        # Event stingers (short musical clips for events)
        self.stingers: Dict[str, str] = {
            "crash": "stinger_crash.ogg",
            "boost": "stinger_boost.ogg",
            "victory": "stinger_victory.ogg",
            "final_lap": "stinger_final_lap.ogg",
            "position_up": "stinger_position_up.ogg",
            "position_down": "stinger_position_down.ogg",
        }
        
        # State tracking
        self.race_state = RaceState()
        self.previous_position = 1
        
        # Audio ducking
        self.is_ducked = False
        self.duck_volume = 0.3
        self.duck_restore_time = 0.0
        
    def select_track(self, track: MusicTrack):
        """
        Select and prepare a music track for racing.
        
        Args:
            track: MusicTrack to play during the race
        """
        self.current_track = track
        
        # Calculate loop points based on track (would be enhanced with actual loop data)
        # For now, assume the middle section of the track loops
        estimated_length = 180.0  # 3 minutes default
        self.loop_start_time = track.preview_start
        self.loop_end_time = estimated_length - 20.0  # Leave 20s at end
        
        print(f"Selected track: {track.display_name}")
        print(f"Loop points: {self.loop_start_time}s - {self.loop_end_time}s")
        
    def start_race_music(self, fade_in_ms: int = 1000):
        """
        Start playing the selected race music.
        
        Args:
            fade_in_ms: Fade in duration in milliseconds
        """
        if not self.current_track:
            print("Warning: No track selected for race music")
            return
            
        # Build path to music file in drive subdirectory
        from pathlib import Path
        music_path = Path(__file__).parent.parent.parent / "assets" / "audio" / "music" / "drive" / self.current_track.filename
        
        try:
            print(f"Attempting to play music from: {music_path}")
            
            # CRITICAL FIX: Ensure any existing music is stopped first
            # This prevents crashes from conflicting music streams
            import pygame
            pygame.mixer.music.stop()
            
            # Wait a short moment for the stop to take effect
            import time
            time.sleep(0.1)
            
            # Check if file exists before attempting to play
            if not music_path.exists():
                print(f"ERROR: Music file does not exist: {music_path}")
                return
            
            # Set initial volume
            self.current_volume = self.base_volume
            self.sound_manager.set_music_volume(self.current_volume)
            
            # Start playing the music with enhanced error handling
            self.sound_manager.play_music(str(music_path), loops=-1, fade_ms=fade_in_ms)
            print(f"Music started: {self.current_track.display_name}")
            
            self.is_playing = True
            self.music_start_time = time.time()
            
            print(f"Started race music: {self.current_track.display_name}")
            
        except Exception as e:
            print(f"CRITICAL ERROR starting race music: {e}")
            print(f"Music file path: {music_path}")
            print(f"Track details: {self.current_track}")
            # Don't crash the game - just continue without music
            self.is_playing = False
            
    def stop_race_music(self, fade_out_ms: int = 1000):
        """
        Stop the race music.
        
        Args:
            fade_out_ms: Fade out duration in milliseconds
        """
        if self.is_playing:
            self.sound_manager.stop_music(fade_ms=fade_out_ms)
            self.is_playing = False
            
    def update_race_state(self, state: RaceState):
        """
        Update the race state and adjust music accordingly.
        
        Args:
            state: Current RaceState
        """
        old_state = self.race_state
        self.race_state = state
        
        # Handle position changes
        if state.position != old_state.position:
            self._handle_position_change(old_state.position, state.position)
            
        # Handle special states
        if state.is_boost and not old_state.is_boost:
            self.play_stinger("boost")
        elif state.is_crash and not old_state.is_crash:
            self.play_stinger("crash")
        elif state.is_final_lap and not old_state.is_final_lap:
            self.play_stinger("final_lap")
        elif state.is_victory and not old_state.is_victory:
            self.play_stinger("victory")
            
        # Update dynamic music parameters
        self._update_dynamic_music()
        
    def _handle_position_change(self, old_position: int, new_position: int):
        """Handle race position changes with appropriate audio feedback."""
        if new_position < old_position:
            # Moved up in position
            self.play_stinger("position_up")
        elif new_position > old_position:
            # Moved down in position
            self.play_stinger("position_down")
            
    def _update_dynamic_music(self):
        """Update music parameters based on current race state."""
        if not self.is_playing:
            return
            
        # Calculate target pitch based on speed
        speed_factor = self.race_state.speed * self.speed_sensitivity
        target_pitch = 1.0 + speed_factor
        
        # Clamp pitch to valid range
        target_pitch = max(self.pitch_range[0], min(self.pitch_range[1], target_pitch))
        
        # Smooth pitch transition (would need pygame extension or alternative approach)
        self.current_pitch = target_pitch
        
        # Adjust volume based on race state
        target_volume = self.base_volume
        
        if self.race_state.is_boost:
            target_volume *= 1.1  # Slightly louder during boost
        elif self.race_state.is_crash:
            target_volume *= 0.5  # Quieter during crash
            
        if self.race_state.is_final_lap:
            target_volume *= 1.05  # Slightly more intense for final lap
            
        # Apply volume changes
        if abs(self.current_volume - target_volume) > 0.05:
            self.current_volume = target_volume
            if not self.is_ducked:
                self.sound_manager.set_music_volume(self.current_volume)
                
    def play_stinger(self, stinger_name: str, volume: float = 0.8):
        """
        Play a musical stinger for race events.
        
        Args:
            stinger_name: Name of the stinger to play
            volume: Volume multiplier for the stinger
        """
        if stinger_name not in self.stingers:
            print(f"Warning: Unknown stinger '{stinger_name}'")
            return
            
        stinger_file = self.stingers[stinger_name]
        stinger_path = get_sfx_path(stinger_file)
        
        try:
            # Duck main music briefly for stinger
            self.duck_music(duration_ms=1500)
            
            # Play the stinger
            self.sound_manager.play_sfx(stinger_path)
            
            print(f"Played stinger: {stinger_name}")
            
        except Exception as e:
            print(f"Error playing stinger {stinger_name}: {e}")
            
    def duck_music(self, duck_level: float = None, duration_ms: int = 1000):
        """
        Temporarily lower music volume for important sounds.
        
        Args:
            duck_level: Volume level during duck (0.0-1.0)
            duration_ms: Duration to maintain ducked volume
        """
        if duck_level is None:
            duck_level = self.duck_volume
            
        if not self.is_playing:
            return
            
        # Duck the music
        ducked_volume = self.current_volume * duck_level
        self.sound_manager.set_music_volume(ducked_volume)
        self.is_ducked = True
        
        # Set restore time
        self.duck_restore_time = time.time() + (duration_ms / 1000.0)
        
    def update(self, dt: float):
        """
        Update the music manager state.
        
        Args:
            dt: Delta time in seconds
        """
        # Check if we need to restore volume after ducking
        if self.is_ducked and time.time() >= self.duck_restore_time:
            self.sound_manager.set_music_volume(self.current_volume)
            self.is_ducked = False
            
        # Handle music looping (would need more sophisticated implementation)
        # This is a placeholder for custom loop point handling
        if self.is_playing and self.current_track:
            current_time = time.time() - self.music_start_time
            # In a real implementation, you'd check if we've reached loop_end_time
            # and seek back to loop_start_time
            
    def set_base_volume(self, volume: float):
        """
        Set the base volume for race music.
        
        Args:
            volume: Base volume level (0.0-1.0)
        """
        self.base_volume = max(0.0, min(1.0, volume))
        if not self.is_ducked:
            self.current_volume = self.base_volume
            self.sound_manager.set_music_volume(self.current_volume)
            
    def set_speed_sensitivity(self, sensitivity: float):
        """
        Set how much speed affects music pitch.
        
        Args:
            sensitivity: Speed sensitivity factor (0.0-1.0)
        """
        self.speed_sensitivity = max(0.0, min(1.0, sensitivity))
        
    def get_current_track(self) -> Optional[MusicTrack]:
        """Get the currently selected track."""
        return self.current_track
        
    def is_music_playing(self) -> bool:
        """Check if race music is currently playing."""
        return self.is_playing
        
    def get_music_info(self) -> Dict[str, Any]:
        """Get information about the current music state."""
        return {
            "track": self.current_track.display_name if self.current_track else None,
            "is_playing": self.is_playing,
            "volume": self.current_volume,
            "pitch": self.current_pitch,
            "is_ducked": self.is_ducked,
            "race_state": {
                "speed": self.race_state.speed,
                "position": self.race_state.position,
                "is_boost": self.race_state.is_boost,
                "is_final_lap": self.race_state.is_final_lap,
            }
        }