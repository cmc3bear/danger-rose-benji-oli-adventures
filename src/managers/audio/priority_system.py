"""Sound priority system for managing audio playback priorities."""

from enum import Enum
from typing import Dict, List, Optional, NamedTuple
import pygame
import time


class SoundPriority(Enum):
    """Priority levels for sound effects."""
    CRITICAL = 100    # UI sounds, game over, victory
    HIGH = 80        # Player actions, important feedback  
    MEDIUM = 60      # Collectibles, minor effects
    LOW = 40         # Ambient sounds, background effects
    AMBIENT = 20     # Environmental audio


class PlayingSoundInfo(NamedTuple):
    """Information about a currently playing sound."""
    channel: pygame.mixer.Channel
    priority: SoundPriority
    sound_id: str
    start_time: float
    duration: Optional[float] = None


class SoundPrioritySystem:
    """Manages sound priorities and channel allocation."""
    
    def __init__(self, max_channels: int = 20):
        """Initialize the priority system.
        
        Args:
            max_channels: Maximum number of mixer channels to use
        """
        self.max_channels = max_channels
        self.playing_sounds: Dict[int, PlayingSoundInfo] = {}
        self.priority_thresholds = {
            SoundPriority.CRITICAL: 0,    # Always play critical sounds
            SoundPriority.HIGH: 2,        # Allow up to 2 lower priority preemptions
            SoundPriority.MEDIUM: 4,      # Allow up to 4 lower priority preemptions
            SoundPriority.LOW: 6,         # Allow up to 6 lower priority preemptions
            SoundPriority.AMBIENT: 8,     # Can be preempted by anything
        }
        
        # Set up pygame mixer channels
        pygame.mixer.set_num_channels(max_channels)
        
    def request_channel(self, priority: SoundPriority, sound_id: str, 
                       duration: Optional[float] = None) -> Optional[pygame.mixer.Channel]:
        """Request a channel based on priority.
        
        Args:
            priority: Priority level of the sound
            sound_id: Unique identifier for the sound
            duration: Expected duration of the sound in seconds
            
        Returns:
            Available channel or None if request denied
        """
        # First, try to find an available channel
        for i in range(self.max_channels):
            channel = pygame.mixer.Channel(i)
            if not channel.get_busy():
                self._register_playing_sound(channel, priority, sound_id, duration)
                return channel
        
        # No free channels, check if we can preempt a lower priority sound
        preempted_channel = self._preempt_if_needed(priority)
        if preempted_channel:
            self._register_playing_sound(preempted_channel, priority, sound_id, duration)
            return preempted_channel
            
        # No channel available
        return None
    
    def _preempt_if_needed(self, incoming_priority: SoundPriority) -> Optional[pygame.mixer.Channel]:
        """Preempt lower priority sounds if needed.
        
        Args:
            incoming_priority: Priority of the incoming sound
            
        Returns:
            Channel that was freed, or None if no preemption possible
        """
        # Find the lowest priority sound that we can preempt
        lowest_priority_channel = None
        lowest_priority_value = incoming_priority.value
        
        current_time = time.time()
        
        for channel_id, sound_info in self.playing_sounds.items():
            # Skip if this sound has higher or equal priority
            if sound_info.priority.value >= incoming_priority.value:
                continue
                
            # Check if sound is still actually playing
            channel = pygame.mixer.Channel(channel_id)
            if not channel.get_busy():
                # Clean up stale entry
                del self.playing_sounds[channel_id]
                continue
            
            # Consider age of sound - newer sounds are less likely to be preempted
            sound_age = current_time - sound_info.start_time
            age_protection = min(sound_age * 0.1, 0.5)  # Up to 0.5 priority boost for age
            
            effective_priority = sound_info.priority.value + age_protection
            
            if effective_priority < lowest_priority_value:
                lowest_priority_value = effective_priority
                lowest_priority_channel = channel
        
        if lowest_priority_channel:
            # Stop the lower priority sound
            lowest_priority_channel.stop()
            # Remove from tracking
            channel_id = None
            for cid, sound_info in self.playing_sounds.items():
                if sound_info.channel == lowest_priority_channel:
                    channel_id = cid
                    break
            if channel_id is not None:
                del self.playing_sounds[channel_id]
            
            return lowest_priority_channel
            
        return None
    
    def _register_playing_sound(self, channel: pygame.mixer.Channel, 
                              priority: SoundPriority, sound_id: str,
                              duration: Optional[float] = None):
        """Register a sound as currently playing.
        
        Args:
            channel: Channel the sound is playing on
            priority: Priority of the sound
            sound_id: Unique identifier for the sound
            duration: Expected duration in seconds
        """
        # Find the channel ID
        for i in range(self.max_channels):
            if pygame.mixer.Channel(i) == channel:
                self.playing_sounds[i] = PlayingSoundInfo(
                    channel=channel,
                    priority=priority,
                    sound_id=sound_id,
                    start_time=time.time(),
                    duration=duration
                )
                break
    
    def cleanup_finished_sounds(self):
        """Remove finished sounds from tracking."""
        finished_channels = []
        
        for channel_id, sound_info in self.playing_sounds.items():
            if not sound_info.channel.get_busy():
                finished_channels.append(channel_id)
        
        for channel_id in finished_channels:
            del self.playing_sounds[channel_id]
    
    def stop_sounds_by_priority(self, max_priority: SoundPriority):
        """Stop all sounds at or below a given priority level.
        
        Args:
            max_priority: Maximum priority level to stop
        """
        channels_to_stop = []
        
        for channel_id, sound_info in self.playing_sounds.items():
            if sound_info.priority.value <= max_priority.value:
                channels_to_stop.append(channel_id)
        
        for channel_id in channels_to_stop:
            sound_info = self.playing_sounds[channel_id]
            sound_info.channel.stop()
            del self.playing_sounds[channel_id]
    
    def stop_sounds_by_id(self, sound_id: str):
        """Stop all instances of a specific sound.
        
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
    
    def get_active_sounds_by_priority(self) -> Dict[SoundPriority, List[str]]:
        """Get currently active sounds grouped by priority.
        
        Returns:
            Dictionary mapping priority levels to lists of sound IDs
        """
        # Clean up finished sounds first
        self.cleanup_finished_sounds()
        
        result = {priority: [] for priority in SoundPriority}
        
        for sound_info in self.playing_sounds.values():
            result[sound_info.priority].append(sound_info.sound_id)
        
        return result
    
    def get_channel_utilization(self) -> float:
        """Get current channel utilization as a percentage.
        
        Returns:
            Percentage of channels currently in use (0.0 to 1.0)
        """
        self.cleanup_finished_sounds()
        return len(self.playing_sounds) / self.max_channels
    
    def can_play_sound(self, priority: SoundPriority) -> bool:
        """Check if a sound with given priority can be played.
        
        Args:
            priority: Priority level to check
            
        Returns:
            True if the sound can be played, False otherwise
        """
        # Always allow critical sounds
        if priority == SoundPriority.CRITICAL:
            return True
        
        # Check if there are free channels
        if len(self.playing_sounds) < self.max_channels:
            return True
        
        # Check if we can preempt a lower priority sound
        for sound_info in self.playing_sounds.values():
            if sound_info.priority.value < priority.value:
                return True
        
        return False