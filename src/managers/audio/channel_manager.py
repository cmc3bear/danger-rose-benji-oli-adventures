"""Advanced channel management system with categories and limits."""

from enum import Enum
from typing import Dict, List, Optional, NamedTuple
import pygame
from .priority_system import SoundPriority, PlayingSoundInfo


class SoundCategory(Enum):
    """Categories for organizing sounds by type."""
    UI = "ui"                    # Menu sounds, button clicks
    PLAYER = "player"            # Player actions, movement
    ENVIRONMENT = "environment"  # Game world sounds, impacts
    MUSIC = "music"             # Background music
    AMBIENT = "ambient"         # Environmental ambient sounds
    VOICE = "voice"             # Character voices, narration


class ChannelGroup:
    """Manages a group of channels for a specific category."""
    
    def __init__(self, start_channel: int, end_channel: int, max_concurrent: int = None):
        """Initialize a channel group.
        
        Args:
            start_channel: First channel index in the group
            end_channel: Last channel index in the group (exclusive)
            max_concurrent: Maximum concurrent sounds (None for no limit)
        """
        self.start_channel = start_channel
        self.end_channel = end_channel
        self.channels = [pygame.mixer.Channel(i) for i in range(start_channel, end_channel)]
        self.max_concurrent = max_concurrent or (end_channel - start_channel)
        self.playing_sounds: Dict[int, PlayingSoundInfo] = {}
        
    def find_available_channel(self) -> Optional[pygame.mixer.Channel]:
        """Find an available channel in this group.
        
        Returns:
            Available channel or None if all busy
        """
        # Clean up finished sounds first
        self._cleanup_finished_sounds()
        
        # Check if we're at max concurrent limit
        if len(self.playing_sounds) >= self.max_concurrent:
            return None
        
        # Find an available channel
        for channel in self.channels:
            if not channel.get_busy():
                return channel
        
        return None
    
    def preempt_lowest_priority(self, min_priority: SoundPriority) -> Optional[pygame.mixer.Channel]:
        """Stop lowest priority sound to free a channel.
        
        Args:
            min_priority: Minimum priority required to preempt
            
        Returns:
            Freed channel or None if no suitable channel found
        """
        # Find the lowest priority sound that can be preempted
        lowest_priority_channel = None
        lowest_priority_value = min_priority.value
        
        for channel_id, sound_info in self.playing_sounds.items():
            if sound_info.priority.value < min_priority.value:
                if sound_info.priority.value < lowest_priority_value:
                    lowest_priority_value = sound_info.priority.value
                    lowest_priority_channel = sound_info.channel
        
        if lowest_priority_channel:
            # Stop the sound and clean up
            lowest_priority_channel.stop()
            self._cleanup_finished_sounds()
            return lowest_priority_channel
        
        return None
    
    def register_sound(self, channel: pygame.mixer.Channel, sound_info: PlayingSoundInfo):
        """Register a sound as playing on this channel group.
        
        Args:
            channel: Channel the sound is playing on
            sound_info: Information about the playing sound
        """
        # Find channel ID within our range
        for i, group_channel in enumerate(self.channels):
            if group_channel == channel:
                channel_id = self.start_channel + i
                self.playing_sounds[channel_id] = sound_info
                break
    
    def stop_all_sounds(self):
        """Stop all sounds in this channel group."""
        for channel in self.channels:
            channel.stop()
        self.playing_sounds.clear()
    
    def stop_sounds_by_id(self, sound_id: str):
        """Stop all instances of a specific sound in this group.
        
        Args:
            sound_id: Sound identifier to stop
        """
        channels_to_stop = []
        
        for channel_id, sound_info in self.playing_sounds.items():
            if sound_info.sound_id == sound_id:
                channels_to_stop.append(channel_id)
        
        for channel_id in channels_to_stop:
            sound_info = self.playing_sounds[channel_id]
            sound_info.channel.stop()
            del self.playing_sounds[channel_id]
    
    def get_usage_info(self) -> Dict[str, int]:
        """Get usage information for this channel group.
        
        Returns:
            Dictionary with usage statistics
        """
        self._cleanup_finished_sounds()
        
        return {
            "total_channels": len(self.channels),
            "max_concurrent": self.max_concurrent,
            "currently_playing": len(self.playing_sounds),
            "available": min(
                len([c for c in self.channels if not c.get_busy()]),
                self.max_concurrent - len(self.playing_sounds)
            )
        }
    
    def _cleanup_finished_sounds(self):
        """Remove finished sounds from tracking."""
        finished_channels = []
        
        for channel_id, sound_info in self.playing_sounds.items():
            if not sound_info.channel.get_busy():
                finished_channels.append(channel_id)
        
        for channel_id in finished_channels:
            del self.playing_sounds[channel_id]


class ChannelManager:
    """Advanced channel management with categories and limits."""
    
    def __init__(self, total_channels: int = 32):
        """Initialize the channel manager.
        
        Args:
            total_channels: Total number of mixer channels to allocate
        """
        self.total_channels = total_channels
        pygame.mixer.set_num_channels(total_channels)
        
        # Allocate channels to categories
        self.channel_groups = self._setup_channel_groups()
        
        # Category configuration
        self.category_configs = {
            SoundCategory.UI: {"max_concurrent": 4, "priority_boost": 10},
            SoundCategory.PLAYER: {"max_concurrent": 6, "priority_boost": 5},
            SoundCategory.ENVIRONMENT: {"max_concurrent": 8, "priority_boost": 0},
            SoundCategory.MUSIC: {"max_concurrent": 2, "priority_boost": 0},
            SoundCategory.AMBIENT: {"max_concurrent": 4, "priority_boost": -5},
            SoundCategory.VOICE: {"max_concurrent": 2, "priority_boost": 15},
        }
    
    def _setup_channel_groups(self) -> Dict[SoundCategory, ChannelGroup]:
        """Setup channel groups for different sound categories.
        
        Returns:
            Dictionary mapping categories to channel groups
        """
        # Allocate channels to categories
        # UI: 0-3 (4 channels)
        # Player: 4-9 (6 channels) 
        # Environment: 10-17 (8 channels)
        # Music: 18-19 (2 channels)
        # Ambient: 20-23 (4 channels)
        # Voice: 24-25 (2 channels)
        # Reserved: 26-31 (6 channels for overflow)
        
        return {
            SoundCategory.UI: ChannelGroup(0, 4, max_concurrent=4),
            SoundCategory.PLAYER: ChannelGroup(4, 10, max_concurrent=6),
            SoundCategory.ENVIRONMENT: ChannelGroup(10, 18, max_concurrent=8),
            SoundCategory.MUSIC: ChannelGroup(18, 20, max_concurrent=2),
            SoundCategory.AMBIENT: ChannelGroup(20, 24, max_concurrent=4),
            SoundCategory.VOICE: ChannelGroup(24, 26, max_concurrent=2),
        }
    
    def allocate_channel(self, category: SoundCategory, 
                        priority: SoundPriority, sound_id: str,
                        duration: Optional[float] = None) -> Optional[pygame.mixer.Channel]:
        """Allocate channel from appropriate category.
        
        Args:
            category: Sound category
            priority: Sound priority
            sound_id: Unique sound identifier
            duration: Expected duration in seconds
            
        Returns:
            Allocated channel or None if allocation failed
        """
        group = self.channel_groups.get(category)
        if not group:
            return None
        
        # Try to find an available channel in the category
        channel = group.find_available_channel()
        
        if not channel:
            # Try to preempt a lower priority sound
            adjusted_priority = self._get_adjusted_priority(category, priority)
            channel = group.preempt_lowest_priority(adjusted_priority)
        
        if not channel:
            # Try overflow channels if available
            channel = self._allocate_overflow_channel(priority, sound_id)
        
        if channel:
            # Register the sound
            from .priority_system import PlayingSoundInfo
            import time
            
            sound_info = PlayingSoundInfo(
                channel=channel,
                priority=priority,
                sound_id=sound_id,
                start_time=time.time(),
                duration=duration
            )
            group.register_sound(channel, sound_info)
        
        return channel
    
    def _get_adjusted_priority(self, category: SoundCategory, 
                             priority: SoundPriority) -> SoundPriority:
        """Get priority adjusted for category-specific boosts.
        
        Args:
            category: Sound category
            priority: Base priority
            
        Returns:
            Adjusted priority
        """
        config = self.category_configs.get(category, {})
        priority_boost = config.get("priority_boost", 0)
        
        # Calculate new priority value
        new_value = priority.value + priority_boost
        
        # Find closest matching priority enum
        for p in SoundPriority:
            if p.value <= new_value:
                return p
        
        return SoundPriority.CRITICAL
    
    def _allocate_overflow_channel(self, priority: SoundPriority, 
                                 sound_id: str) -> Optional[pygame.mixer.Channel]:
        """Allocate from overflow channels (26-31).
        
        Args:
            priority: Sound priority
            sound_id: Sound identifier
            
        Returns:
            Overflow channel or None
        """
        # Use channels 26-31 as overflow
        for i in range(26, self.total_channels):
            channel = pygame.mixer.Channel(i)
            if not channel.get_busy():
                return channel
        
        return None
    
    def stop_category_sounds(self, category: SoundCategory):
        """Stop all sounds in a specific category.
        
        Args:
            category: Category to stop
        """
        group = self.channel_groups.get(category)
        if group:
            group.stop_all_sounds()
    
    def stop_sounds_by_id(self, sound_id: str):
        """Stop all instances of a sound across all categories.
        
        Args:
            sound_id: Sound identifier to stop
        """
        for group in self.channel_groups.values():
            group.stop_sounds_by_id(sound_id)
    
    def get_channel_usage(self) -> Dict[SoundCategory, Dict[str, int]]:
        """Get current channel usage statistics.
        
        Returns:
            Dictionary mapping categories to usage information
        """
        return {
            category: group.get_usage_info()
            for category, group in self.channel_groups.items()
        }
    
    def get_total_usage(self) -> Dict[str, int]:
        """Get total channel usage across all categories.
        
        Returns:
            Overall usage statistics
        """
        total_playing = 0
        total_available = 0
        
        for group in self.channel_groups.values():
            info = group.get_usage_info()
            total_playing += info["currently_playing"]
            total_available += info["available"]
        
        return {
            "total_channels": self.total_channels,
            "currently_playing": total_playing,
            "available": total_available,
            "utilization_percent": int((total_playing / self.total_channels) * 100)
        }
    
    def set_category_max_concurrent(self, category: SoundCategory, max_concurrent: int):
        """Set maximum concurrent sounds for a category.
        
        Args:
            category: Category to configure
            max_concurrent: Maximum concurrent sounds
        """
        if category in self.channel_groups:
            self.channel_groups[category].max_concurrent = max_concurrent
        
        if category in self.category_configs:
            self.category_configs[category]["max_concurrent"] = max_concurrent
    
    def cleanup_all_finished_sounds(self):
        """Clean up finished sounds across all channel groups."""
        for group in self.channel_groups.values():
            group._cleanup_finished_sounds()