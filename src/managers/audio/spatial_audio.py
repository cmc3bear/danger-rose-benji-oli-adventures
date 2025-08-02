"""Spatial audio system for 3D positioning and distance-based effects."""

from typing import Tuple, Optional
import math
import pygame


class Vector2:
    """Simple 2D vector class for spatial calculations."""
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y
    
    def distance_to(self, other: 'Vector2') -> float:
        """Calculate distance to another vector."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def __sub__(self, other: 'Vector2') -> 'Vector2':
        """Subtract two vectors."""
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __add__(self, other: 'Vector2') -> 'Vector2':
        """Add two vectors."""
        return Vector2(self.x + other.x, self.y + other.y)
    
    def magnitude(self) -> float:
        """Get the magnitude of the vector."""
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalized(self) -> 'Vector2':
        """Get normalized version of the vector."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)


class SpatialProperties:
    """Properties for 3D audio positioning."""
    
    def __init__(self):
        self.position = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.max_distance = 500.0
        self.rolloff_factor = 1.0
        self.use_doppler = False
        self.min_volume = 0.0
        self.max_volume = 1.0
        self.pan_strength = 1.0  # How strong the stereo panning effect is


class SpatialAudioEngine:
    """3D positional audio calculations and effects."""
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        """Initialize the spatial audio engine.
        
        Args:
            screen_width: Screen width for positioning calculations
            screen_height: Screen height for positioning calculations
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Listener position (typically the player or camera center)
        self.listener_position = Vector2(screen_width // 2, screen_height // 2)
        self.listener_velocity = Vector2(0, 0)
        
        # Audio settings
        self.max_audible_distance = 800.0
        self.rolloff_factor = 1.0
        self.doppler_factor = 1.0
        self.speed_of_sound = 343.0  # m/s, but we'll treat it as pixels/second
        
        # Pan settings
        self.pan_width = screen_width * 0.8  # Effective width for panning
        self.pan_center = screen_width // 2
    
    def set_listener_position(self, position: Vector2):
        """Set the listener position (usually player position).
        
        Args:
            position: New listener position
        """
        self.listener_position = position
    
    def set_listener_velocity(self, velocity: Vector2):
        """Set the listener velocity for doppler effect.
        
        Args:
            velocity: Listener velocity vector
        """
        self.listener_velocity = velocity
    
    def calculate_spatial_volume(self, sound_position: Vector2, 
                               base_volume: float,
                               max_distance: Optional[float] = None,
                               rolloff: Optional[float] = None) -> float:
        """Calculate volume based on distance from listener.
        
        Args:
            sound_position: Position of the sound source
            base_volume: Base volume of the sound (0.0-1.0)
            max_distance: Maximum audible distance (uses default if None)
            rolloff: Rolloff factor (uses default if None)
            
        Returns:
            Calculated volume (0.0-1.0)
        """
        if max_distance is None:
            max_distance = self.max_audible_distance
        if rolloff is None:
            rolloff = self.rolloff_factor
        
        # Calculate distance
        distance = self.listener_position.distance_to(sound_position)
        
        # If beyond max distance, return 0
        if distance >= max_distance:
            return 0.0
        
        # Calculate volume falloff
        if distance <= 0:
            return base_volume
        
        # Linear rolloff by default
        volume_factor = 1.0 - (distance / max_distance)
        
        # Apply rolloff curve
        if rolloff != 1.0:
            volume_factor = volume_factor ** rolloff
        
        return base_volume * volume_factor
    
    def calculate_stereo_pan(self, sound_position: Vector2,
                           pan_strength: float = 1.0) -> Tuple[float, float]:
        """Calculate left/right channel volumes for stereo positioning.
        
        Args:
            sound_position: Position of the sound source
            pan_strength: Strength of the panning effect (0.0-1.0)
            
        Returns:
            Tuple of (left_volume, right_volume) multipliers
        """
        # Calculate horizontal offset from center
        offset = sound_position.x - self.pan_center
        
        # Normalize to -1.0 to 1.0 range
        pan_range = self.pan_width / 2
        if pan_range <= 0:
            return (1.0, 1.0)
        
        normalized_pan = max(-1.0, min(1.0, offset / pan_range))
        
        # Apply pan strength
        normalized_pan *= pan_strength
        
        # Calculate left/right volumes
        # -1.0 = full left, 0.0 = center, 1.0 = full right
        if normalized_pan <= 0:
            # Left side
            left_volume = 1.0
            right_volume = 1.0 + normalized_pan  # normalized_pan is negative
        else:
            # Right side
            left_volume = 1.0 - normalized_pan
            right_volume = 1.0
        
        # Ensure volumes are in valid range
        left_volume = max(0.0, min(1.0, left_volume))
        right_volume = max(0.0, min(1.0, right_volume))
        
        return (left_volume, right_volume)
    
    def calculate_doppler_effect(self, sound_position: Vector2,
                               sound_velocity: Vector2) -> float:
        """Apply doppler effect to sound frequency.
        
        Args:
            sound_position: Position of the sound source
            sound_velocity: Velocity of the sound source
            
        Returns:
            Frequency multiplier (1.0 = no change)
        """
        if not self.doppler_factor or self.doppler_factor == 0:
            return 1.0
        
        # Calculate direction from sound to listener
        direction = self.listener_position - sound_position
        distance = direction.magnitude()
        
        if distance <= 0:
            return 1.0
        
        direction = direction.normalized()
        
        # Calculate relative velocities along the line between source and listener
        sound_velocity_component = (sound_velocity.x * direction.x + 
                                  sound_velocity.y * direction.y)
        listener_velocity_component = (self.listener_velocity.x * direction.x + 
                                     self.listener_velocity.y * direction.y)
        
        # Doppler effect calculation
        # frequency = original_frequency * (speed_of_sound + listener_velocity) / 
        #                                  (speed_of_sound + source_velocity)
        
        numerator = self.speed_of_sound + listener_velocity_component
        denominator = self.speed_of_sound + sound_velocity_component
        
        if abs(denominator) < 0.1:  # Avoid division by zero
            return 1.0
        
        frequency_multiplier = numerator / denominator
        
        # Apply doppler factor to control strength of effect
        frequency_multiplier = 1.0 + (frequency_multiplier - 1.0) * self.doppler_factor
        
        # Clamp to reasonable range
        return max(0.5, min(2.0, frequency_multiplier))
    
    def apply_spatial_effects(self, sound: pygame.mixer.Sound, 
                            properties: SpatialProperties) -> pygame.mixer.Sound:
        """Apply spatial effects to a sound.
        
        Args:
            sound: Original sound object
            properties: Spatial properties for the sound
            
        Returns:
            Sound with spatial effects applied
        """
        # Calculate spatial volume
        spatial_volume = self.calculate_spatial_volume(
            properties.position,
            properties.max_volume,
            properties.max_distance,
            properties.rolloff_factor
        )
        
        # Apply minimum volume constraint
        final_volume = max(properties.min_volume, spatial_volume)
        
        # Set volume on the sound
        sound.set_volume(final_volume)
        
        # Note: pygame doesn't support individual channel volume control or
        # frequency manipulation out of the box, so stereo panning and doppler
        # would need additional libraries like numpy or custom audio processing
        
        return sound
    
    def get_3d_audio_info(self, sound_position: Vector2,
                         sound_velocity: Vector2 = None,
                         properties: SpatialProperties = None) -> dict:
        """Get comprehensive 3D audio information for a sound.
        
        Args:
            sound_position: Position of the sound source
            sound_velocity: Velocity of the sound source
            properties: Spatial properties (uses defaults if None)
            
        Returns:
            Dictionary with audio information
        """
        if sound_velocity is None:
            sound_velocity = Vector2(0, 0)
        if properties is None:
            properties = SpatialProperties()
            properties.position = sound_position
        
        distance = self.listener_position.distance_to(sound_position)
        
        volume = self.calculate_spatial_volume(
            sound_position,
            properties.max_volume,
            properties.max_distance,
            properties.rolloff_factor
        )
        
        left_volume, right_volume = self.calculate_stereo_pan(
            sound_position,
            properties.pan_strength
        )
        
        doppler_multiplier = 1.0
        if properties.use_doppler:
            doppler_multiplier = self.calculate_doppler_effect(
                sound_position,
                sound_velocity
            )
        
        return {
            "distance": distance,
            "volume": volume,
            "left_volume": left_volume,
            "right_volume": right_volume,
            "doppler_multiplier": doppler_multiplier,
            "audible": volume > 0 and distance < properties.max_distance
        }
    
    def is_sound_audible(self, sound_position: Vector2, 
                        max_distance: Optional[float] = None) -> bool:
        """Check if a sound at given position would be audible.
        
        Args:
            sound_position: Position of the sound source
            max_distance: Maximum audible distance
            
        Returns:
            True if the sound would be audible
        """
        if max_distance is None:
            max_distance = self.max_audible_distance
        
        distance = self.listener_position.distance_to(sound_position)
        return distance < max_distance
    
    def get_closest_audible_distance(self, sound_position: Vector2) -> float:
        """Get the closest distance at which a sound would become audible.
        
        Args:
            sound_position: Position of the sound source
            
        Returns:
            Distance at which sound becomes audible
        """
        return self.listener_position.distance_to(sound_position)