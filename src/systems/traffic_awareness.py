"""
Traffic Awareness System for Drive Scene

Provides intelligent traffic scanning and passing decision logic for NPC vehicles.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class DriverPersonality(Enum):
    """Different driver personality types affecting passing behavior."""
    CAUTIOUS = "cautious"      # Rarely passes, large safety margins
    NORMAL = "normal"          # Balanced passing behavior
    AGGRESSIVE = "aggressive"  # Passes frequently, smaller margins
    TRUCK = "truck"           # Special behavior for trucks


@dataclass
class TrafficScan:
    """Results of scanning surrounding traffic."""
    ahead_same_lane: Optional[object] = None
    ahead_left_lane: Optional[object] = None
    ahead_right_lane: Optional[object] = None
    behind_same_lane: Optional[object] = None
    behind_left_lane: Optional[object] = None
    behind_right_lane: Optional[object] = None
    safe_to_change_left: bool = False
    safe_to_change_right: bool = False
    left_lane_exists: bool = False
    right_lane_exists: bool = False
    distance_to_ahead: float = float('inf')
    speed_differential: float = 0.0


class TrafficAwareness:
    """System for intelligent traffic awareness and passing decisions."""
    
    # Safety margins by personality type (in game units)
    SAFETY_MARGINS = {
        DriverPersonality.CAUTIOUS: {
            'front_gap': 150.0,
            'rear_gap': 100.0,
            'speed_threshold': 0.15  # Only pass if 15% faster
        },
        DriverPersonality.NORMAL: {
            'front_gap': 100.0,
            'rear_gap': 60.0,
            'speed_threshold': 0.10  # Pass if 10% faster
        },
        DriverPersonality.AGGRESSIVE: {
            'front_gap': 60.0,
            'rear_gap': 40.0,
            'speed_threshold': 0.05  # Pass if 5% faster
        },
        DriverPersonality.TRUCK: {
            'front_gap': 200.0,
            'rear_gap': 120.0,
            'speed_threshold': 0.20  # Only pass if 20% faster
        }
    }
    
    def __init__(self):
        """Initialize the traffic awareness system."""
        self.scan_range = 300.0  # Maximum scanning distance
        
    def scan_surrounding_traffic(self, car: object, all_cars: List[object]) -> TrafficScan:
        """
        Scan for nearby vehicles in all lanes.
        
        Args:
            car: The car doing the scanning
            all_cars: List of all NPC cars in the scene
            
        Returns:
            TrafficScan object with detected vehicles and safety assessment
        """
        scan = TrafficScan()
        
        # Determine which lanes exist relative to current car
        if car.direction == 1:  # Same direction as player (lanes 3,4)
            scan.left_lane_exists = car.lane == 4  # Can go to lane 3
            scan.right_lane_exists = car.lane == 3  # Can go to lane 4
        else:  # Oncoming direction (lanes 1,2)
            scan.left_lane_exists = car.lane == 2  # Can go to lane 1
            scan.right_lane_exists = car.lane == 1  # Can go to lane 2
            
        # Scan all other cars
        for other in all_cars:
            if other == car:
                continue
                
            # Only consider cars in same direction
            if other.direction != car.direction:
                continue
                
            # Calculate relative position
            distance = other.y - car.y
            
            # Check if within scan range
            if abs(distance) > self.scan_range:
                continue
                
            # Categorize by lane and position
            if other.lane == car.lane:
                if distance > 0:  # Ahead
                    if scan.ahead_same_lane is None or distance < scan.distance_to_ahead:
                        scan.ahead_same_lane = other
                        scan.distance_to_ahead = distance
                        scan.speed_differential = car.speed - other.speed
                else:  # Behind
                    if scan.behind_same_lane is None or abs(distance) < abs(scan.behind_same_lane.y - car.y):
                        scan.behind_same_lane = other
                        
            elif car.direction == 1:  # Same direction lanes (3,4)
                if other.lane == 3 and car.lane == 4:  # Left lane
                    if distance > 0:
                        if scan.ahead_left_lane is None or distance < (scan.ahead_left_lane.y - car.y):
                            scan.ahead_left_lane = other
                    else:
                        if scan.behind_left_lane is None or abs(distance) < abs(scan.behind_left_lane.y - car.y):
                            scan.behind_left_lane = other
                elif other.lane == 4 and car.lane == 3:  # Right lane
                    if distance > 0:
                        if scan.ahead_right_lane is None or distance < (scan.ahead_right_lane.y - car.y):
                            scan.ahead_right_lane = other
                    else:
                        if scan.behind_right_lane is None or abs(distance) < abs(scan.behind_right_lane.y - car.y):
                            scan.behind_right_lane = other
                            
        # Assess safety of lane changes
        personality = self._get_driver_personality(car)
        margins = self.SAFETY_MARGINS[personality]
        
        # Check left lane safety
        if scan.left_lane_exists:
            scan.safe_to_change_left = self._is_lane_safe(
                scan.ahead_left_lane,
                scan.behind_left_lane,
                car,
                margins
            )
            
        # Check right lane safety
        if scan.right_lane_exists:
            scan.safe_to_change_right = self._is_lane_safe(
                scan.ahead_right_lane,
                scan.behind_right_lane,
                car,
                margins
            )
            
        return scan
        
    def should_attempt_pass(self, car: object, scan: TrafficScan) -> Tuple[bool, Optional[str]]:
        """
        Determine if car should attempt to pass.
        
        Args:
            car: The car considering passing
            scan: Results of traffic scan
            
        Returns:
            Tuple of (should_pass, target_direction) where target_direction is 'left' or 'right'
        """
        # No car ahead, no need to pass
        if scan.ahead_same_lane is None:
            return False, None
            
        personality = self._get_driver_personality(car)
        margins = self.SAFETY_MARGINS[personality]
        
        # Check if we're going significantly faster than car ahead
        if scan.speed_differential < margins['speed_threshold']:
            return False, None
            
        # Check if we're too close to car ahead
        if scan.distance_to_ahead > margins['front_gap'] * 1.5:
            return False, None  # Still have room, no need to pass yet
            
        # Trucks prefer right lane, cars prefer left for passing
        if car.vehicle_type == "truck":
            # Trucks only pass if really necessary and prefer right lane
            if scan.safe_to_change_right and scan.ahead_right_lane is None:
                return True, 'right'
            elif scan.safe_to_change_left and scan.ahead_left_lane is None:
                return True, 'left'
        else:
            # Cars prefer left lane for passing (in countries with right-hand traffic)
            if car.direction == 1:  # Same direction as player
                if car.lane == 3 and scan.safe_to_change_right:  # Currently in slow lane
                    # Check if fast lane is clear or has faster traffic
                    if (scan.ahead_right_lane is None or 
                        (scan.ahead_right_lane.y - car.y) > margins['front_gap'] * 2):
                        return True, 'right'
                elif car.lane == 4 and scan.safe_to_change_left:  # Currently in fast lane
                    # Return to slow lane if clear
                    if scan.ahead_left_lane is None and scan.speed_differential < 0:
                        return True, 'left'
                        
        return False, None
        
    def get_emergency_evasion(self, car: object, scan: TrafficScan) -> Optional[str]:
        """
        Determine emergency evasion direction if collision imminent.
        
        Args:
            car: The car needing to evade
            scan: Results of traffic scan
            
        Returns:
            'left', 'right', or None if no evasion possible
        """
        # Check for imminent collision
        if scan.ahead_same_lane and scan.distance_to_ahead < 30:
            if scan.safe_to_change_left:
                return 'left'
            elif scan.safe_to_change_right:
                return 'right'
                
        return None
        
    def _get_driver_personality(self, car: object) -> DriverPersonality:
        """Determine driver personality based on vehicle attributes."""
        if car.vehicle_type == "truck":
            return DriverPersonality.TRUCK
            
        # Use color or other attributes to assign personality
        # This could be expanded to store personality in the car object
        if hasattr(car, 'personality'):
            return car.personality
            
        # Default assignment based on speed
        if car.speed > 1.0:
            return DriverPersonality.AGGRESSIVE
        elif car.speed < 0.8:
            return DriverPersonality.CAUTIOUS
        else:
            return DriverPersonality.NORMAL
            
    def _is_lane_safe(self, ahead: Optional[object], behind: Optional[object], 
                     car: object, margins: Dict) -> bool:
        """Check if a lane is safe to change into."""
        # Check front clearance
        if ahead:
            front_distance = ahead.y - car.y
            if front_distance < margins['front_gap']:
                return False
                
        # Check rear clearance
        if behind:
            rear_distance = car.y - behind.y
            if rear_distance < margins['rear_gap']:
                # Also check relative speed - if car behind is faster, need more room
                if behind.speed > car.speed:
                    if rear_distance < margins['rear_gap'] * 1.5:
                        return False
                else:
                    if rear_distance < margins['rear_gap']:
                        return False
                        
        return True