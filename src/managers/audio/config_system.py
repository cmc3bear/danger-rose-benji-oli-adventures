"""Audio configuration system for managing settings and preferences."""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from .channel_manager import SoundCategory
from .priority_system import SoundPriority


@dataclass
class EQSettings:
    """Equalizer settings for audio processing."""
    low_gain: float = 0.0      # Bass adjustment (-20.0 to +20.0 dB)
    mid_gain: float = 0.0      # Mid adjustment (-20.0 to +20.0 dB)
    high_gain: float = 0.0     # Treble adjustment (-20.0 to +20.0 dB)
    enabled: bool = False


@dataclass
class CategoryConfig:
    """Configuration for a sound category."""
    volume: float = 1.0
    max_concurrent: int = 4
    priority_boost: float = 0.0
    compression: bool = False
    eq_settings: EQSettings = field(default_factory=EQSettings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "volume": self.volume,
            "max_concurrent": self.max_concurrent,
            "priority_boost": self.priority_boost,
            "compression": self.compression,
            "eq_settings": asdict(self.eq_settings)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CategoryConfig':
        """Create from dictionary."""
        eq_data = data.get("eq_settings", {})
        eq_settings = EQSettings(**eq_data) if eq_data else EQSettings()
        
        return cls(
            volume=data.get("volume", 1.0),
            max_concurrent=data.get("max_concurrent", 4),
            priority_boost=data.get("priority_boost", 0.0),
            compression=data.get("compression", False),
            eq_settings=eq_settings
        )


@dataclass
class AccessibilityConfig:
    """Accessibility options for audio."""
    visual_sound_indicators: bool = False
    hearing_impaired_mode: bool = False
    enhanced_important_sounds: bool = False
    reduced_ambient_sounds: bool = False
    subtitle_mode: bool = False
    sound_description_mode: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccessibilityConfig':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class PerformanceConfig:
    """Performance-related audio settings."""
    max_memory_usage_mb: int = 100
    enable_sound_compression: bool = True
    lazy_loading: bool = True
    cache_cleanup_interval: int = 300  # seconds
    max_sounds_per_frame: int = 10
    audio_quality: str = "high"  # "low", "medium", "high"
    enable_spatial_audio: bool = True
    enable_doppler_effect: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceConfig':
        """Create from dictionary."""
        return cls(**data)


class AudioConfigSystem:
    """Comprehensive audio configuration management."""
    
    def __init__(self, config_path: str = "audio_config.json"):
        """Initialize the audio configuration system.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        
        # Initialize category configurations
        self.categories = {
            SoundCategory.UI: CategoryConfig(
                volume=1.0,
                max_concurrent=4,
                priority_boost=10.0,
                compression=False
            ),
            SoundCategory.PLAYER: CategoryConfig(
                volume=1.0,
                max_concurrent=6,
                priority_boost=5.0,
                compression=False
            ),
            SoundCategory.ENVIRONMENT: CategoryConfig(
                volume=0.8,
                max_concurrent=8,
                priority_boost=0.0,
                compression=True
            ),
            SoundCategory.MUSIC: CategoryConfig(
                volume=0.7,
                max_concurrent=2,
                priority_boost=0.0,
                compression=True
            ),
            SoundCategory.AMBIENT: CategoryConfig(
                volume=0.6,
                max_concurrent=4,
                priority_boost=-5.0,
                compression=True
            ),
            SoundCategory.VOICE: CategoryConfig(
                volume=1.0,
                max_concurrent=2,
                priority_boost=15.0,
                compression=False
            ),
        }
        
        # Initialize other configurations
        self.accessibility = AccessibilityConfig()
        self.performance = PerformanceConfig()
        
        # Master settings
        self.master_volume = 0.7
        self.music_volume = 0.5
        self.sfx_volume = 0.8
        
        # Load existing configuration
        self.load_config()
    
    def load_config(self, config_path: Optional[str] = None) -> bool:
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file (uses default if None)
            
        Returns:
            True if configuration was loaded successfully
        """
        if config_path:
            self.config_path = config_path
        
        if not os.path.exists(self.config_path):
            # Create default configuration file
            self.save_config()
            return True
        
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            # Load master volumes
            self.master_volume = data.get("master_volume", 0.7)
            self.music_volume = data.get("music_volume", 0.5)
            self.sfx_volume = data.get("sfx_volume", 0.8)
            
            # Load category configurations
            categories_data = data.get("categories", {})
            for category_name, category_data in categories_data.items():
                try:
                    category = SoundCategory(category_name)
                    self.categories[category] = CategoryConfig.from_dict(category_data)
                except (ValueError, KeyError):
                    print(f"Warning: Invalid category configuration for {category_name}")
            
            # Load accessibility configuration
            accessibility_data = data.get("accessibility", {})
            self.accessibility = AccessibilityConfig.from_dict(accessibility_data)
            
            # Load performance configuration
            performance_data = data.get("performance", {})
            self.performance = PerformanceConfig.from_dict(performance_data)
            
            return True
            
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Error loading audio configuration: {e}")
            return False
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """Save current configuration to file.
        
        Args:
            config_path: Path to save configuration (uses default if None)
            
        Returns:
            True if configuration was saved successfully
        """
        if config_path:
            self.config_path = config_path
        
        try:
            config_data = {
                "master_volume": self.master_volume,
                "music_volume": self.music_volume,
                "sfx_volume": self.sfx_volume,
                "categories": {
                    category.value: config.to_dict()
                    for category, config in self.categories.items()
                },
                "accessibility": self.accessibility.to_dict(),
                "performance": self.performance.to_dict(),
                "version": "1.0"
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
            
        except (IOError, OSError) as e:
            print(f"Error saving audio configuration: {e}")
            return False
    
    def apply_preset(self, preset_name: str) -> bool:
        """Apply a predefined configuration preset.
        
        Args:
            preset_name: Name of the preset to apply
            
        Returns:
            True if preset was applied successfully
        """
        presets = self._get_presets()
        
        if preset_name not in presets:
            print(f"Warning: Preset '{preset_name}' not found")
            return False
        
        preset = presets[preset_name]
        
        # Apply master volumes
        self.master_volume = preset.get("master_volume", self.master_volume)
        self.music_volume = preset.get("music_volume", self.music_volume)
        self.sfx_volume = preset.get("sfx_volume", self.sfx_volume)
        
        # Apply category configurations
        categories_data = preset.get("categories", {})
        for category_name, category_data in categories_data.items():
            try:
                category = SoundCategory(category_name)
                self.categories[category] = CategoryConfig.from_dict(category_data)
            except ValueError:
                continue
        
        # Apply accessibility settings
        accessibility_data = preset.get("accessibility", {})
        if accessibility_data:
            self.accessibility = AccessibilityConfig.from_dict(accessibility_data)
        
        # Apply performance settings
        performance_data = preset.get("performance", {})
        if performance_data:
            self.performance = PerformanceConfig.from_dict(performance_data)
        
        return True
    
    def get_category_config(self, category: SoundCategory) -> CategoryConfig:
        """Get configuration for a specific category.
        
        Args:
            category: Sound category
            
        Returns:
            Category configuration
        """
        return self.categories.get(category, CategoryConfig())
    
    def set_category_config(self, category: SoundCategory, config: CategoryConfig):
        """Set configuration for a specific category.
        
        Args:
            category: Sound category
            config: New configuration
        """
        self.categories[category] = config
    
    def get_all_volumes(self) -> Dict[str, float]:
        """Get all volume settings.
        
        Returns:
            Dictionary with all volume settings
        """
        volumes = {
            "master": self.master_volume,
            "music": self.music_volume,
            "sfx": self.sfx_volume,
        }
        
        # Add category volumes
        for category, config in self.categories.items():
            volumes[f"category_{category.value}"] = config.volume
        
        return volumes
    
    def set_master_volume(self, volume: float):
        """Set master volume.
        
        Args:
            volume: Volume level (0.0-1.0)
        """
        self.master_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume: float):
        """Set music volume.
        
        Args:
            volume: Volume level (0.0-1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume.
        
        Args:
            volume: Volume level (0.0-1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def enable_accessibility_mode(self, mode: str):
        """Enable a specific accessibility mode.
        
        Args:
            mode: Accessibility mode to enable
        """
        if mode == "hearing_impaired":
            self.accessibility.hearing_impaired_mode = True
            self.accessibility.visual_sound_indicators = True
            self.accessibility.enhanced_important_sounds = True
            self.accessibility.subtitle_mode = True
        elif mode == "sound_sensitive":
            self.accessibility.reduced_ambient_sounds = True
            # Reduce ambient and environment volumes
            self.categories[SoundCategory.AMBIENT].volume *= 0.5
            self.categories[SoundCategory.ENVIRONMENT].volume *= 0.7
    
    def optimize_for_performance(self):
        """Optimize settings for better performance."""
        self.performance.audio_quality = "medium"
        self.performance.enable_sound_compression = True
        self.performance.max_memory_usage_mb = 50
        self.performance.max_sounds_per_frame = 6
        self.performance.enable_spatial_audio = False
        self.performance.enable_doppler_effect = False
        
        # Reduce some category limits
        for category in self.categories.values():
            category.max_concurrent = max(1, category.max_concurrent - 1)
            category.compression = True
    
    def _get_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get predefined configuration presets.
        
        Returns:
            Dictionary of preset configurations
        """
        return {
            "default": {
                "master_volume": 0.7,
                "music_volume": 0.5,
                "sfx_volume": 0.8,
                "categories": {
                    "ui": {"volume": 1.0, "max_concurrent": 4},
                    "player": {"volume": 1.0, "max_concurrent": 6},
                    "environment": {"volume": 0.8, "max_concurrent": 8},
                    "music": {"volume": 0.7, "max_concurrent": 2},
                    "ambient": {"volume": 0.6, "max_concurrent": 4},
                    "voice": {"volume": 1.0, "max_concurrent": 2},
                }
            },
            "quiet": {
                "master_volume": 0.4,
                "music_volume": 0.3,
                "sfx_volume": 0.5,
                "categories": {
                    "ambient": {"volume": 0.2},
                    "environment": {"volume": 0.4},
                }
            },
            "loud": {
                "master_volume": 0.9,
                "music_volume": 0.8,
                "sfx_volume": 1.0,
                "categories": {
                    "ambient": {"volume": 0.9},
                    "environment": {"volume": 1.0},
                }
            },
            "performance": {
                "master_volume": 0.6,
                "music_volume": 0.4,
                "sfx_volume": 0.7,
                "performance": {
                    "audio_quality": "medium",
                    "max_memory_usage_mb": 50,
                    "enable_spatial_audio": False,
                    "enable_doppler_effect": False
                },
                "categories": {
                    "ui": {"max_concurrent": 2, "compression": True},
                    "player": {"max_concurrent": 4, "compression": True},
                    "environment": {"max_concurrent": 4, "compression": True},
                    "ambient": {"max_concurrent": 2, "compression": True},
                }
            },
            "accessibility": {
                "master_volume": 0.8,
                "music_volume": 0.3,
                "sfx_volume": 0.9,
                "accessibility": {
                    "visual_sound_indicators": True,
                    "enhanced_important_sounds": True,
                    "reduced_ambient_sounds": True,
                    "subtitle_mode": True
                },
                "categories": {
                    "ui": {"volume": 1.0, "priority_boost": 15.0},
                    "player": {"volume": 1.0, "priority_boost": 10.0},
                    "ambient": {"volume": 0.3},
                    "environment": {"volume": 0.5},
                }
            }
        }