"""Enhanced sound manager with advanced features for Danger Rose."""

import os
import time
from typing import Dict, List, Optional, Any
import pygame

from src.config.constants import (
    AUDIO_FADE_TIME,
    DEFAULT_MASTER_VOLUME,
    DEFAULT_MUSIC_VOLUME,
    DEFAULT_SFX_VOLUME,
)

# Import audio system components
from .audio.priority_system import SoundPriority, SoundPrioritySystem
from .audio.channel_manager import ChannelManager, SoundCategory
from .audio.spatial_audio import SpatialAudioEngine, SpatialProperties, Vector2
from .audio.event_manager import SoundEventManager, SoundEventConfig
from .audio.performance_monitor import AudioPerformanceMonitor
from .audio.config_system import AudioConfigSystem


class EnhancedSoundManager:
    """Advanced sound manager with pooling, priorities, and 3D audio."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the enhanced sound manager."""
        if hasattr(self, "_initialized"):
            return
        
        self._initialized = True
        
        # Initialize pygame mixer with enhanced settings
        try:
            pygame.mixer.pre_init(
                frequency=44100,  # CD quality
                size=-16,        # 16-bit signed samples
                channels=2,      # Stereo
                buffer=1024      # Balanced latency/performance
            )
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Warning: Could not initialize audio: {e}")
            self._audio_enabled = False
            return
        
        self._audio_enabled = True
        
        # Core audio systems
        self.priority_system = SoundPrioritySystem(max_channels=32)
        self.channel_manager = ChannelManager(total_channels=32)
        self.spatial_audio = SpatialAudioEngine()
        self.event_manager = SoundEventManager(sound_manager=self)
        self.performance_monitor = AudioPerformanceMonitor()
        self.config_system = AudioConfigSystem()
        
        # Volume settings
        self.master_volume = DEFAULT_MASTER_VOLUME
        self.music_volume = DEFAULT_MUSIC_VOLUME
        self.sfx_volume = DEFAULT_SFX_VOLUME
        
        # Category volumes
        self.category_volumes = {
            SoundCategory.UI: 1.0,
            SoundCategory.PLAYER: 1.0,
            SoundCategory.ENVIRONMENT: 0.8,
            SoundCategory.MUSIC: 1.0,
            SoundCategory.AMBIENT: 0.6,
            SoundCategory.VOICE: 1.0,
        }
        
        # Sound cache with memory management
        self.sound_cache: Dict[str, pygame.mixer.Sound] = {}
        self.cache_usage: Dict[str, float] = {}  # Track last usage time
        self.max_cache_size = 50  # Maximum cached sounds
        
        # Music management
        self.current_music = None
        self.music_paused = False
        self.music_queue: List[str] = []
        
        # Performance tracking
        self.sounds_played_this_frame = 0
        self.max_sounds_per_frame = 10
        
        # Apply initial volume settings
        self._apply_volume_settings()
    
    def set_listener_position(self, position: Vector2):
        """Set the listener position for spatial audio.
        
        Args:
            position: New listener position (usually player position)
        """
        self.spatial_audio.set_listener_position(position)
    
    def set_listener_velocity(self, velocity: Vector2):
        """Set listener velocity for doppler effects.
        
        Args:
            velocity: Listener velocity vector
        """
        self.spatial_audio.set_listener_velocity(velocity)
    
    def play_categorized_sfx(self, sound_file: str, 
                           category: SoundCategory = SoundCategory.ENVIRONMENT,
                           priority: SoundPriority = SoundPriority.MEDIUM,
                           volume: float = 1.0,
                           loops: int = 0) -> Optional[pygame.mixer.Channel]:
        """Play a sound effect with category and priority management.
        
        Args:
            sound_file: Path to the sound file
            category: Sound category for channel allocation
            priority: Priority level for the sound
            volume: Volume multiplier (0.0-1.0)
            loops: Number of loops (0 for play once)
            
        Returns:
            Channel the sound is playing on, or None if failed
        """
        if not self._audio_enabled:
            return None
        
        # Performance limiting
        if self.sounds_played_this_frame >= self.max_sounds_per_frame:
            return None
        
        # Load and cache sound
        sound = self._get_cached_sound(sound_file)
        if not sound:
            return None
        
        # Allocate channel from appropriate category
        channel = self.channel_manager.allocate_channel(
            category, priority, sound_file
        )
        
        if not channel:
            return None
        
        # Apply volume settings
        final_volume = self._calculate_final_volume(volume, category)
        sound.set_volume(final_volume)
        
        # Play the sound
        try:
            channel.play(sound, loops=loops)
            self.sounds_played_this_frame += 1
            
            # Update performance metrics
            self.performance_monitor.record_sound_played(category, priority)
            
            return channel
        except pygame.error as e:
            print(f"Error playing sound {sound_file}: {e}")
            return None
    
    def play_spatial_sfx(self, sound_file: str,
                        spatial_properties: SpatialProperties,
                        category: SoundCategory = SoundCategory.ENVIRONMENT,
                        priority: SoundPriority = SoundPriority.MEDIUM) -> Optional[pygame.mixer.Channel]:
        """Play a spatial sound effect with 3D positioning.
        
        Args:
            sound_file: Path to the sound file
            spatial_properties: 3D audio properties
            category: Sound category
            priority: Priority level
            
        Returns:
            Channel the sound is playing on, or None if failed
        """
        if not self._audio_enabled:
            return None
        
        # Check if sound would be audible
        if not self.spatial_audio.is_sound_audible(
            spatial_properties.position, spatial_properties.max_distance
        ):
            return None
        
        # Load sound
        sound = self._get_cached_sound(sound_file)
        if not sound:
            return None
        
        # Calculate spatial volume
        spatial_volume = self.spatial_audio.calculate_spatial_volume(
            spatial_properties.position,
            spatial_properties.max_volume,
            spatial_properties.max_distance,
            spatial_properties.rolloff_factor
        )
        
        if spatial_volume <= 0:
            return None
        
        # Allocate channel
        channel = self.channel_manager.allocate_channel(
            category, priority, sound_file
        )
        
        if not channel:
            return None
        
        # Apply volume
        final_volume = self._calculate_final_volume(spatial_volume, category)
        sound.set_volume(final_volume)
        
        # Play the sound
        try:
            channel.play(sound)
            self.sounds_played_this_frame += 1
            
            # Update performance metrics
            self.performance_monitor.record_sound_played(category, priority)
            
            return channel
        except pygame.error as e:
            print(f"Error playing spatial sound {sound_file}: {e}")
            return None
    
    def play_event(self, event_name: str, **kwargs) -> bool:
        """Play a sound using the event system.
        
        Args:
            event_name: Name of the sound event
            **kwargs: Event parameters (position, volume, etc.)
            
        Returns:
            True if event was triggered successfully
        """
        return self.event_manager.trigger_event(event_name, **kwargs)
    
    def play_music(self, music_file: str, loops: int = -1, 
                   fade_ms: int = 0, queue: bool = False):
        """Play background music with enhanced features.
        
        Args:
            music_file: Path to the music file
            loops: Number of loops (-1 for infinite)
            fade_ms: Fade in duration in milliseconds
            queue: Whether to queue the music instead of playing immediately
        """
        if not self._audio_enabled:
            return
        
        if queue:
            self.music_queue.append(music_file)
            return
        
        try:
            # Check if file exists
            if not os.path.exists(music_file):
                print(f"Warning: Music file not found: {music_file}")
                return
            
            # Stop current music with fade if playing
            if self.current_music:
                self.stop_music(fade_ms=AUDIO_FADE_TIME)
            
            # Load and play new music
            pygame.mixer.music.load(music_file)
            
            if fade_ms > 0:
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
            else:
                pygame.mixer.music.play(loops)
            
            self.current_music = music_file
            self.music_paused = False
            
            # Update performance metrics
            self.performance_monitor.record_music_change()
            
        except pygame.error as e:
            print(f"Error playing music {music_file}: {e}")
    
    def crossfade_music(self, new_music: str, duration_ms: int = 2000):
        """Crossfade from current music to new music.
        
        Args:
            new_music: Path to the new music file
            duration_ms: Duration of the crossfade
        """
        if not self._audio_enabled:
            return
        
        # Fade out current music
        if self.current_music:
            pygame.mixer.music.fadeout(duration_ms // 2)
        
        # Schedule new music to start
        # Note: In a full implementation, this would use a timer system
        # For now, we'll do a simple delayed start
        def start_new_music():
            self.play_music(new_music, fade_ms=duration_ms // 2)
        
        # This is a simplified version - real implementation would use threading
        pygame.time.set_timer(pygame.USEREVENT + 1, duration_ms // 2)
    
    def stop_music(self, fade_ms: int = 0):
        """Stop the currently playing music."""
        if not self._audio_enabled:
            return
        
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
        
        self.current_music = None
        self.music_paused = False
    
    def pause_music(self):
        """Pause the currently playing music."""
        if not self._audio_enabled:
            return
        
        if self.current_music and not self.music_paused:
            pygame.mixer.music.pause()
            self.music_paused = True
    
    def unpause_music(self):
        """Unpause the music."""
        if not self._audio_enabled:
            return
        
        if self.current_music and self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False
    
    def set_master_volume(self, volume: float):
        """Set master volume (0.0-1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
        self._apply_volume_settings()
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0-1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        self._apply_music_volume()
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0-1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_category_volume(self, category: SoundCategory, volume: float):
        """Set volume for a specific sound category.
        
        Args:
            category: Sound category to adjust
            volume: Volume level (0.0-1.0)
        """
        self.category_volumes[category] = max(0.0, min(1.0, volume))
    
    def stop_category_sounds(self, category: SoundCategory):
        """Stop all sounds in a specific category.
        
        Args:
            category: Category to stop
        """
        self.channel_manager.stop_category_sounds(category)
        self.event_manager.stop_category_events(category)
    
    def stop_sounds_by_id(self, sound_id: str):
        """Stop all instances of a specific sound.
        
        Args:
            sound_id: Sound identifier to stop
        """
        self.channel_manager.stop_sounds_by_id(sound_id)
        self.event_manager.stop_event_sounds(sound_id)
    
    def preload_sounds(self, sound_files: List[str]):
        """Preload a list of sound files into cache.
        
        Args:
            sound_files: List of sound file paths to preload
        """
        for sound_file in sound_files:
            self._get_cached_sound(sound_file)
    
    def clear_sound_cache(self):
        """Clear the sound cache to free memory."""
        self.sound_cache.clear()
        self.cache_usage.clear()
    
    def get_performance_info(self) -> Dict[str, Any]:
        """Get performance information about the audio system.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            "cache_size": len(self.sound_cache),
            "channel_usage": self.channel_manager.get_total_usage(),
            "sounds_this_frame": self.sounds_played_this_frame,
            "performance_metrics": self.performance_monitor.get_metrics(),
            "memory_usage_mb": self._estimate_memory_usage()
        }
    
    def update(self, dt: float):
        """Update the sound system (call once per frame).
        
        Args:
            dt: Delta time since last update
        """
        # Reset per-frame counters
        self.sounds_played_this_frame = 0
        
        # Clean up finished sounds
        self.channel_manager.cleanup_all_finished_sounds()
        
        # Update performance monitoring
        self.performance_monitor.update(dt)
        
        # Manage sound cache
        self._manage_cache()
        
        # Handle music queue
        self._update_music_queue()
    
    def shutdown(self):
        """Shutdown the sound system cleanly."""
        self.stop_music()
        self.channel_manager.stop_category_sounds(SoundCategory.UI)
        self.channel_manager.stop_category_sounds(SoundCategory.PLAYER)
        self.channel_manager.stop_category_sounds(SoundCategory.ENVIRONMENT)
        self.channel_manager.stop_category_sounds(SoundCategory.AMBIENT)
        self.clear_sound_cache()
        
        if self._audio_enabled:
            pygame.mixer.quit()
    
    # Backward compatibility methods
    def play_sfx(self, sound_file: str, loops: int = 0, 
                maxtime: int = 0) -> Optional[pygame.mixer.Channel]:
        """Play a sound effect (backward compatibility).
        
        Args:
            sound_file: Path to the sound file
            loops: Number of loops
            maxtime: Maximum time to play (unused in enhanced version)
            
        Returns:
            Channel the sound is playing on, or None if failed
        """
        return self.play_categorized_sfx(
            sound_file, 
            category=SoundCategory.ENVIRONMENT,
            priority=SoundPriority.MEDIUM,
            loops=loops
        )
    
    def preload_sound(self, sound_file: str):
        """Preload a single sound (backward compatibility)."""
        self._get_cached_sound(sound_file)
    
    def get_volumes(self) -> Dict[str, float]:
        """Get current volume settings (backward compatibility)."""
        return {
            "master": self.master_volume,
            "music": self.music_volume,
            "sfx": self.sfx_volume,
        }
    
    # Private methods
    def _get_cached_sound(self, sound_file: str) -> Optional[pygame.mixer.Sound]:
        """Get a sound from cache or load it.
        
        Args:
            sound_file: Path to the sound file
            
        Returns:
            Sound object or None if failed to load
        """
        if sound_file in self.sound_cache:
            self.cache_usage[sound_file] = time.time()
            return self.sound_cache[sound_file]
        
        # Check if file exists
        if not os.path.exists(sound_file):
            print(f"Warning: Sound file not found: {sound_file}")
            return None
        
        try:
            # Load the sound
            sound = pygame.mixer.Sound(sound_file)
            
            # Add to cache if there's room
            if len(self.sound_cache) < self.max_cache_size:
                self.sound_cache[sound_file] = sound
                self.cache_usage[sound_file] = time.time()
            
            return sound
            
        except pygame.error as e:
            print(f"Error loading sound {sound_file}: {e}")
            return None
    
    def _calculate_final_volume(self, base_volume: float, 
                              category: SoundCategory) -> float:
        """Calculate final volume for a sound.
        
        Args:
            base_volume: Base volume for the sound
            category: Sound category
            
        Returns:
            Final volume to apply
        """
        category_volume = self.category_volumes.get(category, 1.0)
        return (base_volume * category_volume * 
                self.sfx_volume * self.master_volume)
    
    def _apply_volume_settings(self):
        """Apply current volume settings."""
        self._apply_music_volume()
    
    def _apply_music_volume(self):
        """Apply the current music volume setting."""
        if not self._audio_enabled:
            return
        
        effective_volume = self.master_volume * self.music_volume
        pygame.mixer.music.set_volume(effective_volume)
    
    def _manage_cache(self):
        """Manage sound cache size and cleanup."""
        if len(self.sound_cache) <= self.max_cache_size:
            return
        
        # Remove least recently used sounds
        current_time = time.time()
        sorted_sounds = sorted(
            self.cache_usage.items(),
            key=lambda x: x[1]  # Sort by usage time
        )
        
        # Remove oldest sounds until we're under the limit
        sounds_to_remove = len(self.sound_cache) - self.max_cache_size
        for sound_file, _ in sorted_sounds[:sounds_to_remove]:
            del self.sound_cache[sound_file]
            del self.cache_usage[sound_file]
    
    def _update_music_queue(self):
        """Update music queue if current music finished."""
        if not self.current_music and self.music_queue:
            next_music = self.music_queue.pop(0)
            self.play_music(next_music)
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage of cached sounds in MB.
        
        Returns:
            Estimated memory usage in megabytes
        """
        # Rough estimation based on sound count
        # In reality, you'd want to track actual sound data sizes
        return len(self.sound_cache) * 0.5  # Assume ~0.5MB per sound