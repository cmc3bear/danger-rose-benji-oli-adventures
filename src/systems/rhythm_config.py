"""Configuration and tuning system for BPM-synchronized gameplay."""

import json
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum

from .bpm_tracker import BeatEvent
from .rhythm_event_system import QuantizationMode


class BeatStrength(Enum):
    """Beat strength levels for rhythm systems."""
    WEAK = "weak"
    STRONG = "strong"
    DOWNBEAT = "downbeat"
    ACCENT = "accent"


class DifficultyLevel(Enum):
    """Difficulty levels for rhythm gameplay."""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"


class RhythmIntensity(Enum):
    """Rhythm intensity settings."""
    OFF = "off"           # No rhythm synchronization
    SUBTLE = "subtle"     # Light rhythm effects
    MODERATE = "moderate" # Balanced rhythm gameplay
    INTENSE = "intense"   # Strong rhythm synchronization
    EXTREME = "extreme"   # Maximum rhythm challenge


@dataclass
class BPMDifficultySettings:
    """Difficulty settings that scale with BPM."""
    # Spawn rate modifiers for different BPM ranges
    slow_bpm_modifier: float = 0.8    # BPM < 90
    normal_bpm_modifier: float = 1.0  # BPM 90-140
    fast_bpm_modifier: float = 1.3    # BPM > 140
    
    # Traffic density scaling
    base_traffic_density: float = 0.5
    bpm_density_factor: float = 0.2   # How much BPM affects density
    
    # Player assistance
    beat_tolerance: float = 0.1       # Timing tolerance in seconds
    visual_assists: bool = True       # Show beat indicators
    audio_assists: bool = True        # Audio cues for beats
    
    # Scoring multipliers
    on_beat_bonus: float = 1.2        # Score multiplier for on-beat actions
    rhythm_streak_bonus: float = 0.1  # Bonus per consecutive on-beat action


@dataclass
class RhythmGameplaySettings:
    """Core rhythm gameplay configuration."""
    # Global rhythm settings
    rhythm_intensity: RhythmIntensity = RhythmIntensity.MODERATE
    auto_detect_bpm: bool = True
    manual_bpm_override: Optional[float] = None
    
    # Event quantization
    default_quantization: QuantizationMode = QuantizationMode.NEAREST
    quantization_tolerance: float = 0.05
    
    # Visual feedback
    show_beat_indicators: bool = True
    road_pulse_intensity: float = 0.7
    screen_shake_enabled: bool = True
    color_cycling_enabled: bool = True
    
    # Audio feedback
    metronome_enabled: bool = False
    beat_sound_volume: float = 0.3
    
    # Traffic behavior
    rhythmic_spawning: bool = True
    speed_modulation: bool = True
    pattern_variation: bool = True
    
    # Performance
    max_active_effects: int = 10
    update_frequency: int = 60  # Hz


@dataclass
class BPMTrackSettings:
    """Settings for specific music tracks."""
    track_name: str
    detected_bpm: float
    manual_bpm: Optional[float] = None
    beat_offset: float = 0.0
    confidence: float = 0.0
    time_signature: Tuple[int, int] = (4, 4)
    
    # Track-specific modifiers
    spawn_rate_modifier: float = 1.0
    difficulty_modifier: float = 1.0
    rhythm_intensity_override: Optional[RhythmIntensity] = None
    
    # Metadata
    genre: str = "unknown"
    energy_level: str = "medium"  # low, medium, high, extreme
    recommended_difficulty: DifficultyLevel = DifficultyLevel.NORMAL


class RhythmConfiguration:
    """
    Central configuration system for rhythm-based gameplay.
    
    Manages difficulty scaling, player preferences, and track-specific settings.
    """
    
    def __init__(self, config_file: str = "rhythm_config.json"):
        """
        Initialize rhythm configuration.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        
        # Default settings for each difficulty
        self.difficulty_settings = {
            DifficultyLevel.EASY: BPMDifficultySettings(
                slow_bpm_modifier=0.6,
                normal_bpm_modifier=0.8,
                fast_bpm_modifier=1.0,
                base_traffic_density=0.3,
                beat_tolerance=0.15,
                visual_assists=True,
                audio_assists=True,
                on_beat_bonus=1.1,
                rhythm_streak_bonus=0.05
            ),
            DifficultyLevel.NORMAL: BPMDifficultySettings(
                slow_bpm_modifier=0.8,
                normal_bpm_modifier=1.0,
                fast_bpm_modifier=1.3,
                base_traffic_density=0.5,
                beat_tolerance=0.1,
                visual_assists=True,
                audio_assists=False,
                on_beat_bonus=1.2,
                rhythm_streak_bonus=0.1
            ),
            DifficultyLevel.HARD: BPMDifficultySettings(
                slow_bpm_modifier=1.0,
                normal_bpm_modifier=1.2,
                fast_bpm_modifier=1.5,
                base_traffic_density=0.7,
                beat_tolerance=0.075,
                visual_assists=False,
                audio_assists=False,
                on_beat_bonus=1.5,
                rhythm_streak_bonus=0.15
            ),
            DifficultyLevel.EXPERT: BPMDifficultySettings(
                slow_bpm_modifier=1.2,
                normal_bpm_modifier=1.5,
                fast_bpm_modifier=1.8,
                base_traffic_density=0.9,
                beat_tolerance=0.05,
                visual_assists=False,
                audio_assists=False,
                on_beat_bonus=2.0,
                rhythm_streak_bonus=0.2
            )
        }
        
        # Current settings
        self.current_difficulty = DifficultyLevel.NORMAL
        self.gameplay_settings = RhythmGameplaySettings()
        self.track_settings: Dict[str, BPMTrackSettings] = {}
        
        # Player preferences
        self.player_preferences = {
            "preferred_rhythm_intensity": RhythmIntensity.MODERATE,
            "auto_adjust_difficulty": True,
            "performance_mode": False,  # Disable effects for better performance
            "accessibility_mode": False  # Enhanced assists for accessibility
        }
        
        # Load configuration
        self.load_configuration()
        
    def get_current_difficulty_settings(self) -> BPMDifficultySettings:
        """Get settings for current difficulty level."""
        return self.difficulty_settings[self.current_difficulty]
        
    def get_bpm_modifier(self, current_bpm: float) -> float:
        """
        Get BPM-based difficulty modifier.
        
        Args:
            current_bpm: Current BPM of the music
            
        Returns:
            Difficulty modifier based on BPM
        """
        settings = self.get_current_difficulty_settings()
        
        if current_bpm < 90:
            return settings.slow_bpm_modifier
        elif current_bpm > 140:
            return settings.fast_bpm_modifier
        else:
            return settings.normal_bpm_modifier
            
    def get_traffic_density(self, current_bpm: float) -> float:
        """
        Calculate target traffic density based on BPM and difficulty.
        
        Args:
            current_bpm: Current BPM of the music
            
        Returns:
            Target traffic density (0.0-1.0)
        """
        settings = self.get_current_difficulty_settings()
        base_density = settings.base_traffic_density
        
        # Adjust based on BPM
        bpm_factor = (current_bpm - 120) / 120  # Normalize around 120 BPM
        bpm_adjustment = bpm_factor * settings.bpm_density_factor
        
        return max(0.1, min(1.0, base_density + bpm_adjustment))
        
    def get_spawn_probability(self, beat_strength: BeatStrength, current_bpm: float) -> float:
        """
        Calculate spawn probability for a beat.
        
        Args:
            beat_strength: Strength of the current beat
            current_bpm: Current BPM
            
        Returns:
            Spawn probability (0.0-1.0)
        """
        # Base probabilities
        base_probabilities = {
            BeatStrength.WEAK: 0.1,
            BeatStrength.STRONG: 0.3,
            BeatStrength.DOWNBEAT: 0.6,
            BeatStrength.ACCENT: 0.8
        }
        
        base_prob = base_probabilities.get(beat_strength, 0.2)
        bpm_modifier = self.get_bpm_modifier(current_bpm)
        rhythm_modifier = self._get_rhythm_intensity_modifier()
        
        return base_prob * bpm_modifier * rhythm_modifier
        
    def get_track_settings(self, track_name: str) -> BPMTrackSettings:
        """
        Get settings for a specific track.
        
        Args:
            track_name: Name of the music track
            
        Returns:
            Track-specific settings
        """
        if track_name not in self.track_settings:
            # Create default settings for new track
            self.track_settings[track_name] = BPMTrackSettings(
                track_name=track_name,
                detected_bpm=120.0
            )
            
        return self.track_settings[track_name]
        
    def update_track_bpm(self, track_name: str, detected_bpm: float, confidence: float):
        """
        Update BPM information for a track.
        
        Args:
            track_name: Name of the track
            detected_bpm: Detected BPM value
            confidence: Confidence in the detection (0.0-1.0)
        """
        settings = self.get_track_settings(track_name)
        settings.detected_bpm = detected_bpm
        settings.confidence = confidence
        
        # Auto-save configuration
        self.save_configuration()
        
    def set_difficulty(self, difficulty: DifficultyLevel):
        """Set current difficulty level."""
        self.current_difficulty = difficulty
        self._update_gameplay_settings_for_difficulty()
        
    def set_rhythm_intensity(self, intensity: RhythmIntensity):
        """Set rhythm intensity level."""
        self.gameplay_settings.rhythm_intensity = intensity
        self.player_preferences["preferred_rhythm_intensity"] = intensity
        
    def enable_accessibility_mode(self, enabled: bool):
        """
        Enable or disable accessibility mode.
        
        Args:
            enabled: Whether to enable accessibility features
        """
        self.player_preferences["accessibility_mode"] = enabled
        
        if enabled:
            # Enhanced assists for accessibility
            self.gameplay_settings.show_beat_indicators = True
            self.gameplay_settings.metronome_enabled = True
            self.gameplay_settings.beat_sound_volume = 0.5
            
            # More forgiving timing
            settings = self.get_current_difficulty_settings()
            settings.beat_tolerance *= 1.5
            settings.visual_assists = True
            settings.audio_assists = True
            
    def enable_performance_mode(self, enabled: bool):
        """
        Enable performance mode for better FPS.
        
        Args:
            enabled: Whether to enable performance mode
        """
        self.player_preferences["performance_mode"] = enabled
        
        if enabled:
            # Reduce visual effects
            self.gameplay_settings.max_active_effects = 5
            self.gameplay_settings.road_pulse_intensity = 0.3
            self.gameplay_settings.screen_shake_enabled = False
            self.gameplay_settings.color_cycling_enabled = False
        else:
            # Restore full effects
            self.gameplay_settings.max_active_effects = 10
            self.gameplay_settings.road_pulse_intensity = 0.7
            self.gameplay_settings.screen_shake_enabled = True
            self.gameplay_settings.color_cycling_enabled = True
            
    def auto_adjust_difficulty(self, player_performance: Dict[str, float]):
        """
        Automatically adjust difficulty based on player performance.
        
        Args:
            player_performance: Dictionary with performance metrics
        """
        if not self.player_preferences.get("auto_adjust_difficulty", True):
            return
            
        # Extract performance metrics
        rhythm_accuracy = player_performance.get("rhythm_accuracy", 0.5)
        average_score = player_performance.get("average_score", 0.5)
        completion_rate = player_performance.get("completion_rate", 0.5)
        
        # Calculate overall performance
        overall_performance = (rhythm_accuracy + average_score + completion_rate) / 3
        
        # Adjust difficulty based on performance
        if overall_performance > 0.8 and self.current_difficulty != DifficultyLevel.EXPERT:
            # Player is doing well, increase difficulty
            difficulties = list(DifficultyLevel)
            current_index = difficulties.index(self.current_difficulty)
            if current_index < len(difficulties) - 1:
                self.set_difficulty(difficulties[current_index + 1])
                print(f"Difficulty increased to {self.current_difficulty.value}")
                
        elif overall_performance < 0.3 and self.current_difficulty != DifficultyLevel.EASY:
            # Player is struggling, decrease difficulty
            difficulties = list(DifficultyLevel)
            current_index = difficulties.index(self.current_difficulty)
            if current_index > 0:
                self.set_difficulty(difficulties[current_index - 1])
                print(f"Difficulty decreased to {self.current_difficulty.value}")
                
    def _get_rhythm_intensity_modifier(self) -> float:
        """Get modifier based on rhythm intensity setting."""
        intensity_modifiers = {
            RhythmIntensity.OFF: 0.0,
            RhythmIntensity.SUBTLE: 0.3,
            RhythmIntensity.MODERATE: 0.7,
            RhythmIntensity.INTENSE: 1.0,
            RhythmIntensity.EXTREME: 1.5
        }
        
        return intensity_modifiers.get(self.gameplay_settings.rhythm_intensity, 0.7)
        
    def _update_gameplay_settings_for_difficulty(self):
        """Update gameplay settings based on current difficulty."""
        settings = self.get_current_difficulty_settings()
        
        # Update quantization tolerance
        self.gameplay_settings.quantization_tolerance = settings.beat_tolerance
        
        # Update visual assists
        self.gameplay_settings.show_beat_indicators = settings.visual_assists
        
        # Update audio assists
        self.gameplay_settings.metronome_enabled = settings.audio_assists
        
    def load_configuration(self):
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
                
            # Load difficulty settings
            if "difficulty_settings" in config_data:
                for diff_name, settings_data in config_data["difficulty_settings"].items():
                    difficulty = DifficultyLevel(diff_name)
                    self.difficulty_settings[difficulty] = BPMDifficultySettings(**settings_data)
                    
            # Load gameplay settings
            if "gameplay_settings" in config_data:
                gameplay_data = config_data["gameplay_settings"]
                self.gameplay_settings = RhythmGameplaySettings(**gameplay_data)
                
            # Load track settings
            if "track_settings" in config_data:
                for track_name, track_data in config_data["track_settings"].items():
                    self.track_settings[track_name] = BPMTrackSettings(**track_data)
                    
            # Load player preferences
            if "player_preferences" in config_data:
                self.player_preferences.update(config_data["player_preferences"])
                
            print("Rhythm configuration loaded successfully")
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Could not load rhythm configuration: {e}")
            print("Using default settings")
            
    def save_configuration(self):
        """Save configuration to file."""
        try:
            config_data = {
                "difficulty_settings": {
                    diff.value: asdict(settings)
                    for diff, settings in self.difficulty_settings.items()
                },
                "gameplay_settings": asdict(self.gameplay_settings),
                "track_settings": {
                    name: asdict(settings)
                    for name, settings in self.track_settings.items()
                },
                "player_preferences": self.player_preferences
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            print("Rhythm configuration saved successfully")
            
        except Exception as e:
            print(f"Could not save rhythm configuration: {e}")
            
    def get_current_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            "difficulty": self.current_difficulty.value,
            "rhythm_intensity": self.gameplay_settings.rhythm_intensity.value,
            "quantization_tolerance": self.gameplay_settings.quantization_tolerance,
            "show_beat_indicators": self.gameplay_settings.show_beat_indicators,
            "rhythmic_spawning": self.gameplay_settings.rhythmic_spawning,
            "accessibility_mode": self.player_preferences.get("accessibility_mode", False),
            "performance_mode": self.player_preferences.get("performance_mode", False),
            "auto_adjust_difficulty": self.player_preferences.get("auto_adjust_difficulty", True),
            "track_count": len(self.track_settings)
        }