"""Control traffic spawning and behavior synchronized with music rhythm."""

from enum import Enum
from typing import Dict, List, Callable, Optional
import random
import math

from .bpm_tracker import BPMTracker, BeatInfo, BeatEvent


class SpawnPattern(Enum):
    """Different rhythmic patterns for traffic spawning."""
    STEADY = "steady"           # Spawn on every N beats
    DOWNBEATS = "downbeats"     # Spawn on strong beats (1 and 3)
    SYNCOPATED = "syncopated"   # Spawn on off-beats (2 and 4)
    BURST = "burst"             # Spawn in rhythmic bursts
    RANDOM = "random"           # Random but quantized to beats


class RhythmicTrafficController:
    """Control traffic spawning and behavior with rhythm synchronization."""
    
    def __init__(self, bpm_tracker: BPMTracker):
        """Initialize controller with BPM tracker.
        
        Args:
            bpm_tracker: The BPM tracking system
        """
        self.bpm_tracker = bpm_tracker
        self.spawn_pattern = SpawnPattern.DOWNBEATS
        self.beats_per_spawn = 4  # Spawn every N beats
        self.last_spawn_beat = -1
        
        # Speed modulation
        self.speed_pulse_amount = 0.05  # ±5% speed variation
        self.speed_pulse_smooth = 0.0   # Current smoothed pulse value
        
        # Difficulty scaling
        self.bpm_difficulty_scale = True
        self.base_spawn_rate = 0.5  # Base probability
        self.bpm_spawn_multiplier = 1.0
        
        # Personality rhythm preferences
        self.personality_beat_preferences = {
            "aggressive": {
                "preferred_beats": [1, 3],
                "spawn_multiplier": 1.5,
                "speed_boost": 0.1
            },
            "normal": {
                "preferred_beats": [1, 2, 3, 4],
                "spawn_multiplier": 1.0,
                "speed_boost": 0.0
            },
            "cautious": {
                "preferred_beats": [2, 4],
                "spawn_multiplier": 0.7,
                "speed_boost": -0.05
            }
        }
        
        # Callbacks for traffic events
        self.on_spawn_beat: Optional[Callable[[], None]] = None
        self.on_rhythm_change: Optional[Callable[[float], None]] = None
        
    def update(self, dt: float) -> Dict[str, any]:
        """Update rhythm controller and return traffic modifications.
        
        Args:
            dt: Delta time since last update
            
        Returns:
            Dictionary with rhythm-based modifications
        """
        # Get current beat info
        beat_info = self.bpm_tracker.get_beat_info()
        beat_events = self.bpm_tracker.update(dt)
        
        # Update BPM-based difficulty
        if self.bpm_difficulty_scale:
            # Scale spawn rate with BPM (faster music = more traffic)
            self.bpm_spawn_multiplier = 0.5 + (beat_info.bpm / 120.0) * 0.5
            self.bpm_spawn_multiplier = max(0.3, min(1.5, self.bpm_spawn_multiplier))
        
        # Calculate speed pulse
        self._update_speed_pulse(beat_info, dt)
        
        # Check for beat events
        spawn_now = False
        for event in beat_events:
            if self._should_spawn_on_beat(event, beat_info):
                spawn_now = True
                self.last_spawn_beat = self.bpm_tracker.current_beat_number
                if self.on_spawn_beat:
                    self.on_spawn_beat()
                    
        return {
            "should_spawn": spawn_now,
            "spawn_probability": self._get_spawn_probability(beat_info),
            "speed_modifier": self.speed_pulse_smooth,
            "beat_info": beat_info,
            "is_spawn_window": self._is_spawn_window(beat_info)
        }
        
    def _should_spawn_on_beat(self, event: BeatEvent, beat_info: BeatInfo) -> bool:
        """Determine if traffic should spawn on this beat.
        
        Args:
            event: The beat event
            beat_info: Current beat information
            
        Returns:
            True if traffic should spawn
        """
        beats_since_spawn = self.bpm_tracker.current_beat_number - self.last_spawn_beat
        
        if self.spawn_pattern == SpawnPattern.STEADY:
            # Spawn every N beats
            return beats_since_spawn >= self.beats_per_spawn
            
        elif self.spawn_pattern == SpawnPattern.DOWNBEATS:
            # Spawn on strong beats
            return event.is_downbeat or (event.beat_number == 3 and beats_since_spawn >= 2)
            
        elif self.spawn_pattern == SpawnPattern.SYNCOPATED:
            # Spawn on weak beats
            return event.beat_number in [2, 4] and beats_since_spawn >= 2
            
        elif self.spawn_pattern == SpawnPattern.BURST:
            # Spawn in bursts (multiple cars on downbeats)
            return event.is_downbeat
            
        elif self.spawn_pattern == SpawnPattern.RANDOM:
            # Random but still on beats
            return beats_since_spawn >= 2 and random.random() < 0.6
            
        return False
        
    def _get_spawn_probability(self, beat_info: BeatInfo) -> float:
        """Get current spawn probability based on rhythm.
        
        Args:
            beat_info: Current beat information
            
        Returns:
            Spawn probability (0.0-1.0)
        """
        base_prob = self.base_spawn_rate
        
        # Apply BPM difficulty scaling
        prob = base_prob * self.bpm_spawn_multiplier
        
        # Boost probability on strong beats
        if beat_info.is_downbeat:
            prob *= 1.3
        elif beat_info.beat_number == 3:
            prob *= 1.1
            
        # Reduce on very weak positions
        if beat_info.beat_phase > 0.25 and beat_info.beat_phase < 0.75:
            prob *= 0.8
            
        return min(1.0, max(0.0, prob))
        
    def _is_spawn_window(self, beat_info: BeatInfo) -> bool:
        """Check if we're in a valid spawn window.
        
        Args:
            beat_info: Current beat information
            
        Returns:
            True if spawning is allowed
        """
        # Allow spawning near beats (within 20% of beat interval)
        return beat_info.beat_phase < 0.2 or beat_info.beat_phase > 0.8
        
    def _update_speed_pulse(self, beat_info: BeatInfo, dt: float):
        """Update speed pulse effect based on rhythm.
        
        Args:
            beat_info: Current beat information
            dt: Delta time
        """
        # Target pulse value based on beat position
        if beat_info.is_beat:
            target_pulse = self.speed_pulse_amount * beat_info.beat_strength
        else:
            # Smooth sine wave between beats
            target_pulse = math.sin(beat_info.beat_phase * math.pi * 2) * self.speed_pulse_amount * 0.5
            
        # Smooth the pulse
        smooth_rate = 5.0  # Smoothing speed
        self.speed_pulse_smooth += (target_pulse - self.speed_pulse_smooth) * smooth_rate * dt
        
    def get_personality_speed_modifier(self, personality: str, beat_info: BeatInfo) -> float:
        """Get speed modifier for a personality type based on rhythm.
        
        Args:
            personality: Driver personality type
            beat_info: Current beat information
            
        Returns:
            Speed modifier (-0.1 to 0.1)
        """
        if personality not in self.personality_beat_preferences:
            return 0.0
            
        prefs = self.personality_beat_preferences[personality]
        
        # Base speed boost for personality
        modifier = prefs["speed_boost"]
        
        # Additional boost on preferred beats
        if beat_info.beat_number in prefs["preferred_beats"]:
            modifier += 0.05
            
        return modifier
        
    def get_lane_change_probability(self, personality: str, beat_info: BeatInfo) -> float:
        """Get lane change probability based on personality and rhythm.
        
        Args:
            personality: Driver personality type
            beat_info: Current beat information
            
        Returns:
            Probability modifier for lane changes
        """
        if personality not in self.personality_beat_preferences:
            return 1.0
            
        prefs = self.personality_beat_preferences[personality]
        
        # Higher chance on preferred beats
        if beat_info.beat_number in prefs["preferred_beats"]:
            return 1.5
        else:
            return 0.7
            
    def set_spawn_pattern(self, pattern: SpawnPattern):
        """Change the spawn pattern.
        
        Args:
            pattern: New spawn pattern
        """
        self.spawn_pattern = pattern
        
    def set_beats_per_spawn(self, beats: int):
        """Set how many beats between spawns (for STEADY pattern).
        
        Args:
            beats: Number of beats
        """
        self.beats_per_spawn = max(1, beats)
        
    def set_speed_pulse_amount(self, amount: float):
        """Set the amount of speed pulsing.
        
        Args:
            amount: Pulse amount (0.0-0.2 recommended)
        """
        self.speed_pulse_amount = max(0.0, min(0.2, amount))
        
    def get_spawn_countdown(self) -> float:
        """Get time until next spawn opportunity."""
        if self.spawn_pattern == SpawnPattern.STEADY:
            beats_until_spawn = self.beats_per_spawn - (
                self.bpm_tracker.current_beat_number - self.last_spawn_beat
            )
            if beats_until_spawn <= 0:
                return 0.0
            return self.bpm_tracker.get_next_beat_time() + (beats_until_spawn - 1) * self.bpm_tracker.beat_interval
        else:
            # For other patterns, return time to next suitable beat
            return self.bpm_tracker.get_next_beat_time()