"""Event-based sound system for decoupled audio management."""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
import random
import pygame
from .channel_manager import SoundCategory
from .priority_system import SoundPriority
from .spatial_audio import Vector2, SpatialProperties


@dataclass
class SoundEventConfig:
    """Configuration for a sound event."""
    sound_path: str
    category: SoundCategory = SoundCategory.ENVIRONMENT
    priority: SoundPriority = SoundPriority.MEDIUM
    volume: float = 1.0
    volume_range: tuple = (1.0, 1.0)  # (min, max) for random variation
    pitch_range: tuple = (1.0, 1.0)  # (min, max) for pitch variation
    spatial: bool = False
    max_distance: float = 500.0
    rolloff_factor: float = 1.0
    variations: List[str] = field(default_factory=list)  # Alternative sound files
    cooldown: float = 0.0  # Minimum time between same event triggers
    max_instances: int = 0  # Maximum concurrent instances (0 = no limit)
    fade_in: float = 0.0  # Fade in duration in seconds
    fade_out: float = 0.0  # Fade out duration in seconds


class SoundEventHandler:
    """Base class for custom sound event handlers."""
    
    def handle_event(self, event_name: str, config: SoundEventConfig, **kwargs) -> bool:
        """Handle a sound event.
        
        Args:
            event_name: Name of the event
            config: Sound configuration
            **kwargs: Additional event parameters
            
        Returns:
            True if event was handled, False to continue with default handling
        """
        return False


class SoundEventManager:
    """Event-driven sound system for decoupled audio."""
    
    def __init__(self, sound_manager=None):
        """Initialize the sound event manager.
        
        Args:
            sound_manager: Reference to the main sound manager
        """
        self.sound_manager = sound_manager
        self.event_configs: Dict[str, SoundEventConfig] = {}
        self.event_handlers: Dict[str, List[SoundEventHandler]] = {}
        self.event_cooldowns: Dict[str, float] = {}
        self.instance_counts: Dict[str, int] = {}
        self.last_trigger_times: Dict[str, float] = {}
        
        # Load default event mappings
        self._setup_default_events()
    
    def _setup_default_events(self):
        """Setup default sound event mappings."""
        self.register_events({
            # Player events
            "player.jump": SoundEventConfig(
                sound_path="sfx/player_jump.ogg",
                category=SoundCategory.PLAYER,
                priority=SoundPriority.HIGH,
                volume_range=(0.7, 0.9),
                pitch_range=(0.9, 1.1),
                cooldown=0.1
            ),
            "player.land": SoundEventConfig(
                sound_path="sfx/player_land.ogg",
                category=SoundCategory.PLAYER,
                priority=SoundPriority.HIGH,
                volume_range=(0.6, 0.8),
                cooldown=0.1
            ),
            "player.hurt": SoundEventConfig(
                sound_path="sfx/player_hurt.ogg",
                category=SoundCategory.PLAYER,
                priority=SoundPriority.CRITICAL,
                volume=0.8,
                cooldown=0.5
            ),
            "player.victory": SoundEventConfig(
                sound_path="sfx/victory.ogg",
                category=SoundCategory.PLAYER,
                priority=SoundPriority.CRITICAL,
                volume=1.0
            ),
            
            # Item collection events
            "item.collect": SoundEventConfig(
                sound_path="sfx/collect_item.ogg",
                category=SoundCategory.PLAYER,
                priority=SoundPriority.MEDIUM,
                volume_range=(0.7, 0.9),
                pitch_range=(0.8, 1.2),
                variations=["sfx/collect1.ogg", "sfx/collect2.ogg"],
                max_instances=3
            ),
            "item.coin": SoundEventConfig(
                sound_path="sfx/coin_collect.ogg",
                category=SoundCategory.PLAYER,
                priority=SoundPriority.MEDIUM,
                pitch_range=(0.9, 1.1),
                max_instances=2
            ),
            "item.powerup": SoundEventConfig(
                sound_path="sfx/powerup.ogg",
                category=SoundCategory.PLAYER,
                priority=SoundPriority.HIGH,
                volume=0.9
            ),
            
            # UI events
            "ui.menu_move": SoundEventConfig(
                sound_path="sfx/menu_move.ogg",
                category=SoundCategory.UI,
                priority=SoundPriority.CRITICAL,
                volume=0.6,
                cooldown=0.1
            ),
            "ui.menu_select": SoundEventConfig(
                sound_path="sfx/menu_select.ogg",
                category=SoundCategory.UI,
                priority=SoundPriority.CRITICAL,
                volume=0.8
            ),
            "ui.button_click": SoundEventConfig(
                sound_path="sfx/button_click.ogg",
                category=SoundCategory.UI,
                priority=SoundPriority.HIGH,
                volume=0.7,
                cooldown=0.05
            ),
            
            # Environment events
            "environment.collision": SoundEventConfig(
                sound_path="sfx/collision.ogg",
                category=SoundCategory.ENVIRONMENT,
                priority=SoundPriority.MEDIUM,
                volume_range=(0.5, 0.8),
                spatial=True,
                max_distance=400.0,
                max_instances=3
            ),
            "environment.door_open": SoundEventConfig(
                sound_path="sfx/door_open.ogg",
                category=SoundCategory.ENVIRONMENT,
                priority=SoundPriority.MEDIUM,
                volume=0.7,
                spatial=True
            ),
            "environment.splash": SoundEventConfig(
                sound_path="sfx/splash.ogg",
                category=SoundCategory.ENVIRONMENT,
                priority=SoundPriority.LOW,
                volume_range=(0.4, 0.7),
                spatial=True,
                max_distance=300.0,
                variations=["sfx/splash1.ogg", "sfx/splash2.ogg"],
                max_instances=4
            ),
            
            # Game-specific events
            "ski.crash": SoundEventConfig(
                sound_path="sfx/ski_crash.ogg",
                category=SoundCategory.PLAYER,
                priority=SoundPriority.HIGH,
                volume=0.8,
                cooldown=1.0
            ),
            "pool.balloon_launch": SoundEventConfig(
                sound_path="sfx/balloon_launch.ogg",
                category=SoundCategory.PLAYER,
                priority=SoundPriority.MEDIUM,
                volume_range=(0.6, 0.8),
                pitch_range=(0.9, 1.1),
                spatial=True,
                max_instances=3
            ),
            "pool.target_hit": SoundEventConfig(
                sound_path="sfx/target_hit.ogg",
                category=SoundCategory.ENVIRONMENT,
                priority=SoundPriority.MEDIUM,
                volume_range=(0.7, 0.9),
                spatial=True,
                variations=["sfx/hit1.ogg", "sfx/hit2.ogg", "sfx/hit3.ogg"]
            ),
            "vegas.enemy_defeat": SoundEventConfig(
                sound_path="sfx/enemy_defeat.ogg",
                category=SoundCategory.ENVIRONMENT,
                priority=SoundPriority.MEDIUM,
                volume=0.7,
                spatial=True
            )
        })
    
    def register_event(self, event_name: str, config: SoundEventConfig):
        """Register a single sound event mapping.
        
        Args:
            event_name: Name of the event
            config: Sound configuration
        """
        self.event_configs[event_name] = config
    
    def register_events(self, events: Dict[str, SoundEventConfig]):
        """Register multiple sound event mappings.
        
        Args:
            events: Dictionary of event names to configurations
        """
        self.event_configs.update(events)
    
    def register_handler(self, event_name: str, handler: SoundEventHandler):
        """Register custom event handler.
        
        Args:
            event_name: Name of the event to handle
            handler: Handler instance
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
    
    def trigger_event(self, event_name: str, **kwargs) -> bool:
        """Trigger a sound event with parameters.
        
        Args:
            event_name: Name of the event to trigger
            **kwargs: Additional parameters (position, volume, etc.)
            
        Returns:
            True if event was triggered successfully
        """
        # Check if event is registered
        if event_name not in self.event_configs:
            print(f"Warning: Sound event '{event_name}' not registered")
            return False
        
        config = self.event_configs[event_name]
        
        # Check cooldown
        if not self._check_cooldown(event_name, config.cooldown):
            return False
        
        # Check instance limit
        if not self._check_instance_limit(event_name, config.max_instances):
            return False
        
        # Call custom handlers first
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                if handler.handle_event(event_name, config, **kwargs):
                    return True  # Handler handled the event
        
        # Default handling
        return self._play_event_sound(event_name, config, **kwargs)
    
    def _check_cooldown(self, event_name: str, cooldown: float) -> bool:
        """Check if event is off cooldown.
        
        Args:
            event_name: Name of the event
            cooldown: Cooldown duration in seconds
            
        Returns:
            True if event can be triggered
        """
        if cooldown <= 0:
            return True
        
        import time
        current_time = time.time()
        
        if event_name in self.last_trigger_times:
            time_since_last = current_time - self.last_trigger_times[event_name]
            if time_since_last < cooldown:
                return False
        
        self.last_trigger_times[event_name] = current_time
        return True
    
    def _check_instance_limit(self, event_name: str, max_instances: int) -> bool:
        """Check if event is under instance limit.
        
        Args:
            event_name: Name of the event
            max_instances: Maximum concurrent instances
            
        Returns:
            True if event can be triggered
        """
        if max_instances <= 0:
            return True
        
        current_instances = self.instance_counts.get(event_name, 0)
        return current_instances < max_instances
    
    def _play_event_sound(self, event_name: str, config: SoundEventConfig, **kwargs) -> bool:
        """Play the sound for an event.
        
        Args:
            event_name: Name of the event
            config: Sound configuration
            **kwargs: Additional parameters
            
        Returns:
            True if sound was played successfully
        """
        if not self.sound_manager:
            return False
        
        # Choose sound file (with variations)
        sound_file = self._choose_sound_file(config)
        
        # Calculate volume
        volume = self._calculate_volume(config, kwargs.get('volume'))
        
        # Handle spatial audio
        position = kwargs.get('position')
        if config.spatial and position:
            return self._play_spatial_sound(event_name, sound_file, config, position, volume, **kwargs)
        else:
            return self._play_regular_sound(event_name, sound_file, config, volume, **kwargs)
    
    def _choose_sound_file(self, config: SoundEventConfig) -> str:
        """Choose sound file from variations.
        
        Args:
            config: Sound configuration
            
        Returns:
            Path to sound file to play
        """
        if config.variations:
            # Include original sound in the choices
            all_sounds = [config.sound_path] + config.variations
            return random.choice(all_sounds)
        return config.sound_path
    
    def _calculate_volume(self, config: SoundEventConfig, override_volume: Optional[float] = None) -> float:
        """Calculate final volume for sound.
        
        Args:
            config: Sound configuration
            override_volume: Volume override from event parameters
            
        Returns:
            Final volume to use
        """
        if override_volume is not None:
            return max(0.0, min(1.0, override_volume))
        
        min_vol, max_vol = config.volume_range
        if min_vol == max_vol:
            return config.volume
        
        # Random volume within range
        volume_variation = random.uniform(min_vol, max_vol)
        return config.volume * volume_variation
    
    def _play_spatial_sound(self, event_name: str, sound_file: str, 
                          config: SoundEventConfig, position: Vector2, 
                          volume: float, **kwargs) -> bool:
        """Play a spatial sound.
        
        Args:
            event_name: Name of the event
            sound_file: Path to sound file
            config: Sound configuration
            position: Sound position
            volume: Base volume
            **kwargs: Additional parameters
            
        Returns:
            True if sound was played
        """
        # Create spatial properties
        spatial_props = SpatialProperties()
        spatial_props.position = position
        spatial_props.max_distance = config.max_distance
        spatial_props.rolloff_factor = config.rolloff_factor
        spatial_props.max_volume = volume
        
        # Use enhanced sound manager's spatial audio capabilities
        if hasattr(self.sound_manager, 'play_spatial_sfx'):
            channel = self.sound_manager.play_spatial_sfx(
                sound_file,
                spatial_props,
                category=config.category,
                priority=config.priority
            )
        else:
            # Fallback to regular sound
            channel = self.sound_manager.play_sfx(sound_file)
        
        if channel:
            self._track_instance(event_name)
            return True
        
        return False
    
    def _play_regular_sound(self, event_name: str, sound_file: str,
                          config: SoundEventConfig, volume: float, **kwargs) -> bool:
        """Play a regular (non-spatial) sound.
        
        Args:
            event_name: Name of the event
            sound_file: Path to sound file
            config: Sound configuration
            volume: Volume to use
            **kwargs: Additional parameters
            
        Returns:
            True if sound was played
        """
        # Use enhanced sound manager if available
        if hasattr(self.sound_manager, 'play_categorized_sfx'):
            channel = self.sound_manager.play_categorized_sfx(
                sound_file,
                category=config.category,
                priority=config.priority,
                volume=volume
            )
        else:
            # Fallback to basic sound manager
            channel = self.sound_manager.play_sfx(sound_file)
            
        if channel:
            self._track_instance(event_name)
            return True
        
        return False
    
    def _track_instance(self, event_name: str):
        """Track that an instance of the event is playing.
        
        Args:
            event_name: Name of the event
        """
        if event_name not in self.instance_counts:
            self.instance_counts[event_name] = 0
        self.instance_counts[event_name] += 1
        
        # TODO: Set up callback to decrement when sound finishes
        # This would require channel completion callbacks
    
    def stop_event_sounds(self, event_name: str):
        """Stop all instances of a specific event's sounds.
        
        Args:
            event_name: Name of the event to stop
        """
        if hasattr(self.sound_manager, 'stop_sounds_by_id'):
            self.sound_manager.stop_sounds_by_id(event_name)
        
        # Reset instance count
        self.instance_counts[event_name] = 0
    
    def stop_category_events(self, category: SoundCategory):
        """Stop all events in a specific category.
        
        Args:
            category: Category to stop
        """
        if hasattr(self.sound_manager, 'stop_category_sounds'):
            self.sound_manager.stop_category_sounds(category)
        
        # Reset instance counts for events in this category
        for event_name, config in self.event_configs.items():
            if config.category == category:
                self.instance_counts[event_name] = 0
    
    def get_event_info(self, event_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a registered event.
        
        Args:
            event_name: Name of the event
            
        Returns:
            Dictionary with event information or None if not found
        """
        if event_name not in self.event_configs:
            return None
        
        config = self.event_configs[event_name]
        
        return {
            "sound_path": config.sound_path,
            "category": config.category.value,
            "priority": config.priority.value,
            "volume": config.volume,
            "spatial": config.spatial,
            "variations": len(config.variations),
            "cooldown": config.cooldown,
            "max_instances": config.max_instances,
            "current_instances": self.instance_counts.get(event_name, 0)
        }
    
    def list_events(self) -> List[str]:
        """Get list of all registered event names.
        
        Returns:
            List of event names
        """
        return list(self.event_configs.keys())
    
    def clear_cooldowns(self):
        """Clear all event cooldowns."""
        self.last_trigger_times.clear()
    
    def reset_instance_counts(self):
        """Reset all instance counts."""
        self.instance_counts.clear()