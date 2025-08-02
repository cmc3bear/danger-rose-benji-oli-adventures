"""Configuration system for rhythm-based gameplay features."""

from dataclasses import dataclass, field
from typing import Dict, Any
import json
import os


@dataclass
class RhythmConfiguration:
    """Configuration settings for the BPM synchronization system."""
    
    # Core rhythm settings
    rhythm_enabled: bool = True
    rhythm_intensity: float = 0.7  # 0.0-1.0, how much rhythm affects gameplay
    
    # Spawn settings
    spawn_pattern: str = "downbeats"  # steady, downbeats, syncopated, burst, random
    beats_per_spawn: int = 4          # For steady pattern
    spawn_on_beats: bool = True       # Quantize spawns to beats
    
    # Speed modulation
    speed_pulse_enabled: bool = True
    speed_pulse_amount: float = 0.05  # ±5% speed variation
    
    # Visual effects
    visual_feedback_enabled: bool = True
    beat_indicator_enabled: bool = True
    road_pulse_enabled: bool = True
    road_pulse_amount: float = 10.0   # Pixels of pulse
    speed_lines_enabled: bool = True
    screen_shake_enabled: bool = False  # Off by default (family-friendly)
    
    # Difficulty scaling
    bpm_difficulty_scaling: bool = True
    min_difficulty_multiplier: float = 0.5
    max_difficulty_multiplier: float = 1.5
    
    # Accessibility
    accessibility_mode: bool = False   # Disable rhythm requirements
    colorblind_mode: bool = False     # Use shapes instead of colors
    reduced_effects: bool = False     # Minimize visual effects
    
    # Performance
    update_rate: int = 60            # Updates per second
    effect_quality: str = "medium"   # low, medium, high
    max_visual_effects: int = 20     # Max concurrent effects
    
    # Player preferences (saved per profile)
    player_preferences: Dict[str, Any] = field(default_factory=lambda: {
        "preferred_pattern": "downbeats",
        "custom_intensity": 0.7,
        "effects_enabled": True
    })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for saving."""
        return {
            "rhythm_enabled": self.rhythm_enabled,
            "rhythm_intensity": self.rhythm_intensity,
            "spawn_pattern": self.spawn_pattern,
            "beats_per_spawn": self.beats_per_spawn,
            "spawn_on_beats": self.spawn_on_beats,
            "speed_pulse_enabled": self.speed_pulse_enabled,
            "speed_pulse_amount": self.speed_pulse_amount,
            "visual_feedback_enabled": self.visual_feedback_enabled,
            "beat_indicator_enabled": self.beat_indicator_enabled,
            "road_pulse_enabled": self.road_pulse_enabled,
            "road_pulse_amount": self.road_pulse_amount,
            "speed_lines_enabled": self.speed_lines_enabled,
            "screen_shake_enabled": self.screen_shake_enabled,
            "bpm_difficulty_scaling": self.bpm_difficulty_scaling,
            "min_difficulty_multiplier": self.min_difficulty_multiplier,
            "max_difficulty_multiplier": self.max_difficulty_multiplier,
            "accessibility_mode": self.accessibility_mode,
            "colorblind_mode": self.colorblind_mode,
            "reduced_effects": self.reduced_effects,
            "update_rate": self.update_rate,
            "effect_quality": self.effect_quality,
            "max_visual_effects": self.max_visual_effects,
            "player_preferences": self.player_preferences
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RhythmConfiguration":
        """Create configuration from dictionary."""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
        
    def save_to_file(self, filepath: str):
        """Save configuration to JSON file.
        
        Args:
            filepath: Path to save configuration
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
            
    @classmethod
    def load_from_file(cls, filepath: str) -> "RhythmConfiguration":
        """Load configuration from JSON file.
        
        Args:
            filepath: Path to load configuration from
            
        Returns:
            Loaded configuration or default if file doesn't exist
        """
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                return cls.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                print(f"Error loading rhythm config from {filepath}, using defaults")
        return cls()
        
    def apply_preset(self, preset_name: str):
        """Apply a configuration preset.
        
        Args:
            preset_name: Name of preset to apply
        """
        presets = {
            "casual": {
                "rhythm_intensity": 0.3,
                "spawn_pattern": "steady",
                "speed_pulse_amount": 0.02,
                "road_pulse_amount": 5.0,
                "bpm_difficulty_scaling": False
            },
            "normal": {
                "rhythm_intensity": 0.7,
                "spawn_pattern": "downbeats",
                "speed_pulse_amount": 0.05,
                "road_pulse_amount": 10.0,
                "bpm_difficulty_scaling": True
            },
            "rhythmic": {
                "rhythm_intensity": 1.0,
                "spawn_pattern": "syncopated",
                "speed_pulse_amount": 0.08,
                "road_pulse_amount": 15.0,
                "bpm_difficulty_scaling": True
            },
            "accessibility": {
                "accessibility_mode": True,
                "rhythm_intensity": 0.0,
                "visual_feedback_enabled": False,
                "bpm_difficulty_scaling": False,
                "reduced_effects": True
            },
            "performance": {
                "effect_quality": "low",
                "max_visual_effects": 10,
                "speed_lines_enabled": False,
                "screen_shake_enabled": False,
                "reduced_effects": True
            }
        }
        
        if preset_name in presets:
            for key, value in presets[preset_name].items():
                setattr(self, key, value)
                
    def validate(self) -> bool:
        """Validate configuration values are within acceptable ranges.
        
        Returns:
            True if valid, False otherwise
        """
        valid = True
        
        # Clamp values to valid ranges
        self.rhythm_intensity = max(0.0, min(1.0, self.rhythm_intensity))
        self.speed_pulse_amount = max(0.0, min(0.2, self.speed_pulse_amount))
        self.road_pulse_amount = max(0.0, min(50.0, self.road_pulse_amount))
        self.beats_per_spawn = max(1, min(16, self.beats_per_spawn))
        self.update_rate = max(30, min(120, self.update_rate))
        self.max_visual_effects = max(5, min(100, self.max_visual_effects))
        
        # Validate string values
        valid_patterns = ["steady", "downbeats", "syncopated", "burst", "random"]
        if self.spawn_pattern not in valid_patterns:
            self.spawn_pattern = "downbeats"
            valid = False
            
        valid_qualities = ["low", "medium", "high"]
        if self.effect_quality not in valid_qualities:
            self.effect_quality = "medium"
            valid = False
            
        return valid
        
    def get_effective_intensity(self) -> float:
        """Get the effective rhythm intensity considering all settings.
        
        Returns:
            Effective intensity value (0.0-1.0)
        """
        if not self.rhythm_enabled or self.accessibility_mode:
            return 0.0
        return self.rhythm_intensity
        
    def should_use_visual_effects(self) -> bool:
        """Check if visual effects should be used.
        
        Returns:
            True if visual effects are enabled
        """
        return (self.visual_feedback_enabled and 
                not self.accessibility_mode and 
                not self.reduced_effects)
                
    def get_spawn_pattern_info(self) -> str:
        """Get human-readable description of current spawn pattern.
        
        Returns:
            Description string
        """
        descriptions = {
            "steady": f"Every {self.beats_per_spawn} beats",
            "downbeats": "On strong beats (1 and 3)",
            "syncopated": "On weak beats (2 and 4)",
            "burst": "Multiple cars on downbeats",
            "random": "Random but on-beat"
        }
        return descriptions.get(self.spawn_pattern, "Unknown pattern")