"""BPM tracking and beat detection system."""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import math


@dataclass
class BeatInfo:
    """Information about the current beat state."""
    timestamp: float          # Current time in song
    bpm: float               # Beats per minute
    beat_number: int         # 1, 2, 3, 4 within measure
    beat_phase: float        # 0.0-1.0 position within current beat
    is_beat: bool           # True on exact beat
    is_downbeat: bool       # True on beat 1
    is_upbeat: bool         # True on beats 2 and 4
    beat_strength: float    # 0.0-1.0, strength of current beat
    next_beat_time: float   # Time until next beat


@dataclass 
class BeatEvent:
    """Event fired when a beat occurs."""
    beat_number: int
    is_downbeat: bool
    timestamp: float
    strength: float


class BPMTracker:
    """Track beats and provide rhythm information for game synchronization."""
    
    def __init__(self, bpm: float = 120.0):
        """Initialize BPM tracker with given tempo.
        
        Args:
            bpm: Beats per minute (default 120)
        """
        self.bpm = bpm
        self.beat_interval = 60.0 / bpm  # Seconds per beat
        self.time_elapsed = 0.0
        self.last_beat_time = 0.0
        self.current_beat_number = 0  # Total beats since start
        self.beats_per_measure = 4
        
        # Event tracking
        self.pending_events: List[BeatEvent] = []
        self.event_threshold = 0.05  # Fire events within 50ms of beat
        
    def update(self, dt: float) -> List[BeatEvent]:
        """Update beat tracking and return any beat events.
        
        Args:
            dt: Delta time since last update
            
        Returns:
            List of beat events that occurred this frame
        """
        self.time_elapsed += dt
        events = []
        
        # Check if we've crossed a beat boundary
        beats_elapsed = self.time_elapsed / self.beat_interval
        new_beat_number = int(beats_elapsed)
        
        if new_beat_number > self.current_beat_number:
            # We've crossed one or more beats
            for beat_num in range(self.current_beat_number + 1, new_beat_number + 1):
                measure_beat = ((beat_num - 1) % self.beats_per_measure) + 1
                is_downbeat = measure_beat == 1
                
                # Calculate beat strength
                if is_downbeat:
                    strength = 1.0
                elif measure_beat == 3:
                    strength = 0.7  # Secondary strong beat
                else:
                    strength = 0.5  # Weak beats
                
                event = BeatEvent(
                    beat_number=measure_beat,
                    is_downbeat=is_downbeat,
                    timestamp=beat_num * self.beat_interval,
                    strength=strength
                )
                events.append(event)
            
            self.current_beat_number = new_beat_number
            self.last_beat_time = self.current_beat_number * self.beat_interval
            
        return events
        
    def get_beat_info(self) -> BeatInfo:
        """Get current beat information.
        
        Returns:
            BeatInfo with current rhythm state
        """
        # Calculate position within current beat
        time_since_beat = self.time_elapsed - self.last_beat_time
        beat_phase = time_since_beat / self.beat_interval
        
        # Determine beat number within measure (1-4)
        measure_beat = ((self.current_beat_number - 1) % self.beats_per_measure) + 1
        
        # Check if we're close enough to consider it "on the beat"
        is_beat = beat_phase < self.event_threshold or beat_phase > (1.0 - self.event_threshold)
        
        # Calculate beat strength
        if measure_beat == 1:
            strength = 1.0  # Downbeat
        elif measure_beat == 3:
            strength = 0.7  # Secondary strong beat
        else:
            strength = 0.5  # Weak beats
            
        return BeatInfo(
            timestamp=self.time_elapsed,
            bpm=self.bpm,
            beat_number=measure_beat,
            beat_phase=beat_phase,
            is_beat=is_beat,
            is_downbeat=(measure_beat == 1),
            is_upbeat=(measure_beat in [2, 4]),
            beat_strength=strength,
            next_beat_time=self.beat_interval - time_since_beat
        )
        
    def get_next_beat_time(self) -> float:
        """Get time until next beat in seconds."""
        time_since_beat = self.time_elapsed - self.last_beat_time
        return self.beat_interval - time_since_beat
        
    def get_next_downbeat_time(self) -> float:
        """Get time until next downbeat (beat 1) in seconds."""
        measure_position = self.current_beat_number % self.beats_per_measure
        beats_until_downbeat = (self.beats_per_measure - measure_position) % self.beats_per_measure
        if beats_until_downbeat == 0:
            beats_until_downbeat = self.beats_per_measure
        return self.get_next_beat_time() + (beats_until_downbeat - 1) * self.beat_interval
        
    def quantize_to_beat(self, time: float, subdivision: int = 1) -> float:
        """Quantize a time value to the nearest beat or subdivision.
        
        Args:
            time: Time to quantize
            subdivision: Beat subdivision (1=quarter, 2=eighth, 4=sixteenth)
            
        Returns:
            Quantized time value
        """
        interval = self.beat_interval / subdivision
        return round(time / interval) * interval
        
    def set_bpm(self, new_bpm: float):
        """Change the BPM (for dynamic music or song changes).
        
        Args:
            new_bpm: New beats per minute
        """
        self.bpm = new_bpm
        self.beat_interval = 60.0 / new_bpm
        
    def sync_to_audio_position(self, audio_position: float):
        """Synchronize tracker to current audio playback position.
        
        Args:
            audio_position: Current position in audio file (seconds)
        """
        self.time_elapsed = audio_position
        self.current_beat_number = int(audio_position / self.beat_interval)
        self.last_beat_time = self.current_beat_number * self.beat_interval
        
    def get_measure_progress(self) -> float:
        """Get progress through current measure (0.0-1.0)."""
        measure_position = (self.current_beat_number % self.beats_per_measure) 
        beat_progress = (self.time_elapsed - self.last_beat_time) / self.beat_interval
        return (measure_position + beat_progress) / self.beats_per_measure
        
    def is_near_beat(self, tolerance: float = 0.1) -> bool:
        """Check if we're near a beat (for input timing).
        
        Args:
            tolerance: Time window in seconds
            
        Returns:
            True if within tolerance of a beat
        """
        beat_info = self.get_beat_info()
        time_to_beat = min(beat_info.beat_phase * self.beat_interval,
                          (1.0 - beat_info.beat_phase) * self.beat_interval)
        return time_to_beat <= tolerance