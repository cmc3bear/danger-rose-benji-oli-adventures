"""
Road Geometry System - Issue #32

Provides road-relative positioning for traffic and hazards to ensure proper
tracking along curved roads.
"""

import math
from dataclasses import dataclass
from typing import Tuple, Optional
from src.systems.game_state_logger import get_global_logger


@dataclass
class RoadPosition:
    """Position relative to road instead of screen coordinates."""
    distance: float      # Distance along road from player (positive = ahead)
    lane: int           # Lane number (1=left oncoming, 2=right oncoming, 3=left same, 4=right same)
    lane_offset: float  # Offset within lane (-0.5 to 0.5, 0 = center)
    
    def to_screen_pos(self, road_geometry: 'RoadGeometry') -> Tuple[int, int]:
        """Convert road position to screen coordinates."""
        return road_geometry.road_to_screen(self.distance, self.lane, self.lane_offset)


class RoadGeometry:
    """
    Manages road geometry calculations for proper traffic and hazard positioning.
    
    This system ensures objects stay locked to the road surface during curves
    and provides realistic lane-relative positioning.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_y = screen_height // 2  # Player's fixed screen position
        
        # Road dimensions
        self.base_road_width = 400  # Base road width in pixels
        self.lane_width = self.base_road_width / 4  # 4 lanes total
        
        # Lane center positions (relative to road center)
        # Lane 1: Left oncoming, Lane 2: Right oncoming
        # Lane 3: Left same direction, Lane 4: Right same direction
        self.lane_centers = {
            1: -1.5 * self.lane_width / self.base_road_width,  # -0.375
            2: -0.5 * self.lane_width / self.base_road_width,  # -0.125  
            3: 0.5 * self.lane_width / self.base_road_width,   # 0.125
            4: 1.5 * self.lane_width / self.base_road_width    # 0.375
        }
        
        # Logging
        self.logger = get_global_logger()
        self._log_system_init()
    
    def _log_system_init(self):
        """Log road geometry system initialization."""
        if self.logger:
            self.logger.log_system_event("road_geometry", "system_initialized", {
                "screen_width": self.screen_width,
                "screen_height": self.screen_height,
                "base_road_width": self.base_road_width,
                "lane_width": self.lane_width,
                "lane_centers": self.lane_centers
            })
    
    def get_curve_at_distance(self, distance: float, road_curve: float, 
                            curve_frequency: float = 0.02) -> float:
        """
        Calculate road curve offset at a specific distance from player.
        
        Args:
            distance: Distance along road (positive = ahead, negative = behind)
            road_curve: Current road curve value
            curve_frequency: Frequency of curve oscillations
            
        Returns:
            Curve offset in normalized coordinates (-1.0 to 1.0)
        """
        # For now, use simplified curve that varies with distance
        # This creates a natural progression of curves ahead/behind player
        base_curve = road_curve
        distance_variation = math.sin(distance * curve_frequency) * 0.3
        
        return base_curve + distance_variation
    
    def get_road_width_at_distance(self, distance: float, base_width_variation: float = 0,
                                 surface_noise: float = 0) -> float:
        """
        Calculate road width at a specific distance.
        
        Args:
            distance: Distance along road from player
            base_width_variation: Width oscillation from drive scene
            surface_noise: Surface variation from drive scene
            
        Returns:
            Road width in pixels
        """
        return self.base_road_width + base_width_variation + surface_noise
    
    def road_to_screen(self, distance: float, lane: int, lane_offset: float = 0.0,
                      road_curve: float = 0.0, width_variation: float = 0.0,
                      surface_noise: float = 0.0) -> Tuple[int, int]:
        """
        Convert road-relative position to screen coordinates.
        
        Args:
            distance: Distance along road from player (positive = ahead)
            lane: Lane number (1-4)
            lane_offset: Additional offset within lane (-0.5 to 0.5)
            road_curve: Current road curve value
            width_variation: Width variation from drive scene
            surface_noise: Surface noise from drive scene
            
        Returns:
            (screen_x, screen_y) coordinates
        """
        # Calculate screen Y position (distance from player)
        # Positive distance = ahead of player (screen_y < player_y)
        # Negative distance = behind player (screen_y > player_y)
        screen_y = int(self.player_y - distance)
        
        # Get curve at this distance
        curve_at_distance = self.get_curve_at_distance(distance, road_curve)
        
        # Calculate road center at this distance
        road_center_pixels = self.screen_width // 2 + int(curve_at_distance * 200)
        
        # Get lane center position
        lane_center_normalized = self.lane_centers.get(lane, 0.0)
        
        # Apply lane offset
        total_lane_offset = lane_center_normalized + (lane_offset * 0.25)  # Scale lane offset
        
        # Get road width at this distance
        road_width = self.get_road_width_at_distance(distance, width_variation, surface_noise)
        
        # Calculate final screen X position
        screen_x = int(road_center_pixels + (total_lane_offset * road_width))
        
        # Ensure position is within screen bounds
        screen_x = max(0, min(self.screen_width - 1, screen_x))
        screen_y = max(0, min(self.screen_height - 1, screen_y))
        
        return screen_x, screen_y
    
    def screen_to_road(self, screen_x: int, screen_y: int,
                      road_curve: float = 0.0) -> Optional[RoadPosition]:
        """
        Convert screen coordinates to road-relative position.
        
        Args:
            screen_x: Screen X coordinate
            screen_y: Screen Y coordinate
            road_curve: Current road curve value
            
        Returns:
            RoadPosition or None if position is off-road
        """
        # Calculate distance from player
        distance = float(self.player_y - screen_y)
        
        # Get curve at this distance
        curve_at_distance = self.get_curve_at_distance(distance, road_curve)
        road_center_pixels = self.screen_width // 2 + int(curve_at_distance * 200)
        
        # Calculate normalized position relative to road center
        normalized_offset = (screen_x - road_center_pixels) / self.base_road_width
        
        # Determine which lane this position corresponds to
        best_lane = 3  # Default to lane 3
        min_distance = float('inf')
        
        for lane_num, lane_center in self.lane_centers.items():
            lane_distance = abs(normalized_offset - lane_center)
            if lane_distance < min_distance:
                min_distance = lane_distance
                best_lane = lane_num
        
        # Calculate offset within the lane
        lane_center = self.lane_centers[best_lane]
        lane_offset = (normalized_offset - lane_center) / 0.25  # Scale back to -0.5 to 0.5
        
        # Check if position is reasonable (within road bounds)
        if abs(normalized_offset) > 0.6:  # Beyond reasonable road width
            return None
        
        return RoadPosition(distance=distance, lane=best_lane, lane_offset=lane_offset)
    
    def get_road_normal(self, distance: float, road_curve: float = 0.0) -> float:
        """
        Get road surface normal/angle at a specific distance.
        
        Args:
            distance: Distance along road from player
            road_curve: Current road curve value
            
        Returns:
            Road angle in degrees
        """
        # Calculate curve derivative to get road angle
        curve_delta = 1.0  # Small distance for derivative calculation
        curve_here = self.get_curve_at_distance(distance, road_curve)
        curve_ahead = self.get_curve_at_distance(distance + curve_delta, road_curve)
        
        # Calculate angle from curve change
        curve_change = curve_ahead - curve_here
        angle_radians = math.atan2(curve_change * 200, curve_delta)  # Scale curve change
        angle_degrees = math.degrees(angle_radians)
        
        return angle_degrees
    
    def is_position_on_road(self, road_pos: RoadPosition, margin: float = 0.1) -> bool:
        """
        Check if a road position is within valid road boundaries.
        
        Args:
            road_pos: Road position to check
            margin: Safety margin (0.0 to 1.0)
            
        Returns:
            True if position is on road
        """
        # Check lane validity
        if road_pos.lane not in self.lane_centers:
            return False
        
        # Check lane offset bounds
        if abs(road_pos.lane_offset) > 0.5 + margin:
            return False
        
        return True
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics for the road geometry system."""
        return {
            "calculations_per_frame": 0,  # Would be tracked in a real implementation
            "cache_hit_rate": 0.0,        # Would be tracked if caching is implemented
            "average_calculation_time_ms": 0.0
        }