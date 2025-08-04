"""
Enhanced Environmental Logging System Example for Drive Game
===========================================================

This file demonstrates concrete patterns for implementing comprehensive environmental
logging in the Drive minigame. These patterns can be integrated into the existing
Drive scene to provide detailed telemetry for gameplay analysis.

Game Mechanics Agent Implementation:
- Sprite-Environment Interaction Logging
- Traffic Spawning Event Logging  
- Collision Differentiation (Near-miss vs Actual)
- Sound Effect Trigger Logging

Usage: Copy relevant patterns into src/scenes/drive.py and adapt to existing structure.
"""

import pygame
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
import math


class SurfaceType(Enum):
    """Different surface types the player can interact with"""
    ROAD_ASPHALT = "road_asphalt"
    ROAD_SHOULDER = "road_shoulder"
    GRASS = "grass"
    GRAVEL = "gravel"
    CONSTRUCTION = "construction"
    WATER = "water"
    MUD = "mud"


class CollisionSeverity(Enum):
    """Classification of collision events"""
    NEAR_MISS = "near_miss"          # Within 50 units but no contact
    GLANCING = "glancing"            # Light contact, minimal impact
    MODERATE = "moderate"            # Solid hit, some damage
    SEVERE = "severe"                # Major collision, significant impact


class SpawnReason(Enum):
    """Reasons why traffic was spawned"""
    ROUTINE = "routine"              # Regular traffic pattern
    DENSITY_LOW = "density_low"      # Fill gaps in traffic
    CHALLENGE = "challenge"          # Create gameplay challenge
    SCRIPTED = "scripted"            # Predetermined spawn point
    PLAYER_SPEED = "player_speed"    # React to player behavior


@dataclass
class EnvironmentalEvent:
    """Base class for all environmental events"""
    timestamp: float
    event_type: str
    player_x: float
    player_y: float
    player_speed: float
    data: Dict[str, Any]


@dataclass
class SurfaceInteraction:
    """Tracks player interaction with different surface types"""
    surface_type: SurfaceType
    entry_time: float
    exit_time: Optional[float] = None
    duration: Optional[float] = None
    player_speed_avg: float = 0.0
    player_speed_samples: List[float] = None
    
    def __post_init__(self):
        if self.player_speed_samples is None:
            self.player_speed_samples = []


class EnhancedEnvironmentalLogger:
    """
    Enhanced logging system for environmental interactions in the Drive game.
    
    This class provides comprehensive logging for:
    1. Surface type detection and tracking
    2. Traffic spawning with reasoning
    3. Collision differentiation
    4. Sound effect triggering
    """
    
    def __init__(self, game_logger=None):
        self.game_logger = game_logger
        self.logger = logging.getLogger(f"{__name__}.Environmental")
        
        # Surface interaction tracking
        self.current_surface = SurfaceType.ROAD_ASPHALT
        self.surface_history: List[SurfaceInteraction] = []
        self.current_surface_interaction: Optional[SurfaceInteraction] = None
        
        # Traffic spawning tracking
        self.traffic_spawn_history: List[Dict] = []
        self.traffic_density_samples: List[float] = []
        
        # Collision tracking
        self.near_miss_threshold = 50  # Units for near-miss detection
        self.collision_history: List[Dict] = []
        self.last_collision_time = 0.0
        
        # Sound effect tracking
        self.sound_triggers: List[Dict] = []
        self.sound_cooldowns: Dict[str, float] = {}
        
        # Performance counters
        self.events_logged_this_frame = 0
        self.max_events_per_frame = 10
        
    def update(self, dt: float, player_x: float, player_y: float, player_speed: float):
        """Update all environmental tracking systems"""
        current_time = time.time()
        
        # Reset frame counter
        self.events_logged_this_frame = 0
        
        # Update surface interaction tracking
        self._update_surface_tracking(current_time, player_x, player_y, player_speed)
        
        # Update sound cooldowns
        self._update_sound_cooldowns(dt)
        
        # Sample traffic density periodically
        if len(self.traffic_density_samples) == 0 or current_time - self.traffic_density_samples[-1] > 1.0:
            # This would be called with actual traffic count from the game
            # self._sample_traffic_density(current_time, traffic_count)
            pass
    
    def _update_surface_tracking(self, current_time: float, player_x: float, 
                                player_y: float, player_speed: float):
        """Update surface type tracking based on player position"""
        # Determine current surface type based on player position
        detected_surface = self._detect_surface_type(player_x, player_y)
        
        # Check if surface changed
        if detected_surface != self.current_surface:
            self._handle_surface_change(current_time, detected_surface, player_speed)
        
        # Update current surface interaction
        if self.current_surface_interaction:
            self.current_surface_interaction.player_speed_samples.append(player_speed)
    
    def _detect_surface_type(self, player_x: float, player_y: float) -> SurfaceType:
        """
        Detect surface type based on player position.
        
        This is a simplified example - in the real game, this would analyze:
        - Road boundaries and lane positions
        - Construction zones
        - Off-road areas
        - Special surface effects
        """
        # Example detection logic (adapt to actual Drive game coordinates)
        normalized_x = player_x  # Assuming player_x is already normalized 0-1
        
        # Road is roughly in the center 60% of the screen
        if 0.2 <= normalized_x <= 0.8:
            # Check for construction zones or special surfaces
            # This would integrate with the actual hazard system
            return SurfaceType.ROAD_ASPHALT
        elif 0.15 <= normalized_x <= 0.85:
            # Shoulder area
            return SurfaceType.ROAD_SHOULDER
        else:
            # Off-road
            return SurfaceType.GRASS
    
    def _handle_surface_change(self, current_time: float, new_surface: SurfaceType, 
                              player_speed: float):
        """Handle transition between surface types"""
        # Close previous surface interaction
        if self.current_surface_interaction:
            self.current_surface_interaction.exit_time = current_time
            self.current_surface_interaction.duration = (
                current_time - self.current_surface_interaction.entry_time
            )
            if self.current_surface_interaction.player_speed_samples:
                self.current_surface_interaction.player_speed_avg = (
                    sum(self.current_surface_interaction.player_speed_samples) / 
                    len(self.current_surface_interaction.player_speed_samples)
                )
            
            self.surface_history.append(self.current_surface_interaction)
            
            # Log surface change event
            self._log_environmental_event("surface_change", {
                "from_surface": self.current_surface.value,
                "to_surface": new_surface.value,
                "duration_on_previous": self.current_surface_interaction.duration,
                "avg_speed_on_previous": self.current_surface_interaction.player_speed_avg,
                "reason": self._determine_surface_change_reason(self.current_surface, new_surface)
            })
        
        # Start new surface interaction
        self.current_surface = new_surface
        self.current_surface_interaction = SurfaceInteraction(
            surface_type=new_surface,
            entry_time=current_time,
            player_speed_samples=[player_speed]
        )
    
    def _determine_surface_change_reason(self, from_surface: SurfaceType, 
                                       to_surface: SurfaceType) -> str:
        """Determine why the surface change occurred"""
        if from_surface == SurfaceType.ROAD_ASPHALT and to_surface == SurfaceType.GRASS:
            return "off_road_departure"
        elif from_surface == SurfaceType.GRASS and to_surface == SurfaceType.ROAD_ASPHALT:
            return "return_to_road"
        elif to_surface == SurfaceType.CONSTRUCTION:
            return "entered_construction_zone"
        elif from_surface == SurfaceType.CONSTRUCTION:
            return "exited_construction_zone"
        else:
            return "lane_change_or_drift"
    
    def log_traffic_spawn(self, car_data: Dict, spawn_reason: SpawnReason, 
                         traffic_density: float, player_context: Dict):
        """
        Log traffic spawning events with detailed context.
        
        Args:
            car_data: Information about the spawned car (position, speed, lane, etc.)
            spawn_reason: Why this car was spawned
            traffic_density: Current traffic density (0.0 to 1.0)
            player_context: Player state when spawn occurred
        """
        current_time = time.time()
        
        spawn_event = {
            "timestamp": current_time,
            "event_type": "traffic_spawn",
            "car_id": car_data.get("id", f"car_{len(self.traffic_spawn_history)}"),
            "spawn_reason": spawn_reason.value,
            "spawn_position": {
                "x": car_data.get("x", 0.0),
                "y": car_data.get("y", 0.0),
                "lane": car_data.get("lane", 0),
                "distance": car_data.get("distance", 0.0)
            },
            "car_properties": {
                "speed": car_data.get("speed", 0.0),
                "direction": car_data.get("direction", 1),  # 1 = same, -1 = opposite
                "vehicle_type": car_data.get("vehicle_type", "unknown"),
                "ai_behavior": car_data.get("ai_behavior", "cruising")
            },
            "traffic_context": {
                "density": traffic_density,
                "total_cars": car_data.get("total_cars", 0),
                "cars_in_lane": car_data.get("cars_in_lane", 0),
                "nearest_car_distance": car_data.get("nearest_car_distance", float('inf'))
            },
            "player_context": player_context.copy(),
            "spawn_decision_factors": self._analyze_spawn_factors(spawn_reason, traffic_density, player_context)
        }
        
        self.traffic_spawn_history.append(spawn_event)
        
        # Log to game logger if available
        self._log_environmental_event("traffic_spawn", spawn_event)
        
        # Detailed debug logging
        self.logger.info(
            f"Traffic Spawn: {spawn_reason.value} | "
            f"Lane: {car_data.get('lane', 0)} | "
            f"Distance: {car_data.get('distance', 0.0):.1f} | "
            f"Density: {traffic_density:.2f} | "
            f"Player Speed: {player_context.get('speed', 0.0):.1f}"
        )
    
    def _analyze_spawn_factors(self, spawn_reason: SpawnReason, traffic_density: float, 
                              player_context: Dict) -> Dict:
        """Analyze factors that led to traffic spawn decision"""
        factors = {
            "primary_reason": spawn_reason.value,
            "traffic_density_category": self._categorize_density(traffic_density),
            "player_speed_category": self._categorize_player_speed(player_context.get('speed', 0.0)),
        }
        
        # Add specific analysis based on spawn reason
        if spawn_reason == SpawnReason.DENSITY_LOW:
            factors["density_threshold_crossed"] = traffic_density < 0.3
        elif spawn_reason == SpawnReason.CHALLENGE:
            factors["challenge_opportunity"] = player_context.get('speed', 0.0) > 0.7
        elif spawn_reason == SpawnReason.PLAYER_SPEED:
            factors["speed_adaptation"] = True
            
        return factors
    
    def check_collision_event(self, player_rect: pygame.Rect, other_objects: List[Dict], 
                             player_speed: float) -> Optional[Dict]:
        """
        Check for collision events and differentiate between near-misses and actual collisions.
        
        Args:
            player_rect: Player's collision rectangle
            other_objects: List of objects to check against (cars, hazards, etc.)
            player_speed: Current player speed
            
        Returns:
            Collision event data if collision detected, None otherwise
        """
        current_time = time.time()
        closest_distance = float('inf')
        collision_data = None
        
        for obj in other_objects:
            obj_rect = obj.get('rect')
            if not obj_rect:
                continue
                
            # Calculate distance between centers
            distance = math.sqrt(
                (player_rect.centerx - obj_rect.centerx) ** 2 + 
                (player_rect.centery - obj_rect.centery) ** 2
            )
            
            # Check for actual collision
            if player_rect.colliderect(obj_rect):
                severity = self._determine_collision_severity(distance, player_speed, obj)
                collision_data = self._create_collision_event(
                    current_time, obj, distance, severity, "collision", player_speed
                )
                break
            
            # Check for near miss
            elif distance < self.near_miss_threshold and distance < closest_distance:
                closest_distance = distance
                # Only log near-miss if no actual collision
                if collision_data is None:
                    collision_data = self._create_collision_event(
                        current_time, obj, distance, CollisionSeverity.NEAR_MISS, 
                        "near_miss", player_speed
                    )
        
        # Log collision event if found
        if collision_data:
            self.collision_history.append(collision_data)
            self._log_environmental_event(collision_data["collision_type"], collision_data)
            
            # Trigger appropriate sound effect
            self._trigger_collision_sound(collision_data)
            
        return collision_data
    
    def _create_collision_event(self, timestamp: float, obj: Dict, distance: float, 
                               severity: CollisionSeverity, collision_type: str, 
                               player_speed: float) -> Dict:
        """Create a standardized collision event"""
        return {
            "timestamp": timestamp,
            "event_type": "collision",
            "collision_type": collision_type,  # "collision" or "near_miss"
            "severity": severity.value,
            "distance": distance,
            "object_type": obj.get('type', 'unknown'),
            "object_id": obj.get('id', 'unknown'),
            "object_properties": {
                "speed": obj.get('speed', 0.0),
                "lane": obj.get('lane', 0),
                "direction": obj.get('direction', 1),
                "size": obj.get('size', 'medium')
            },
            "player_state": {
                "speed": player_speed,
                "surface": self.current_surface.value if self.current_surface else "unknown",
                "position_x": obj.get('player_x', 0.0),
                "position_y": obj.get('player_y', 0.0)
            },
            "impact_analysis": self._analyze_impact(severity, distance, player_speed, obj)
        }
    
    def _determine_collision_severity(self, distance: float, player_speed: float, 
                                    obj: Dict) -> CollisionSeverity:
        """Determine the severity of a collision based on multiple factors"""
        if distance >= self.near_miss_threshold:
            return CollisionSeverity.NEAR_MISS
        
        # Consider speed, object type, and impact angle
        speed_factor = player_speed + obj.get('speed', 0.0)
        object_mass_factor = obj.get('mass_factor', 1.0)  # Heavy trucks vs cars
        
        combined_impact = speed_factor * object_mass_factor
        
        if combined_impact > 2.0:
            return CollisionSeverity.SEVERE
        elif combined_impact > 1.0:
            return CollisionSeverity.MODERATE
        else:
            return CollisionSeverity.GLANCING
    
    def _analyze_impact(self, severity: CollisionSeverity, distance: float, 
                       player_speed: float, obj: Dict) -> Dict:
        """Analyze the impact of a collision for learning purposes"""
        return {
            "speed_contribution": player_speed / 2.0,  # Normalize to 0-1
            "object_contribution": obj.get('speed', 0.0) / 2.0,
            "size_factor": obj.get('mass_factor', 1.0),
            "avoidability": "high" if distance > 20 else "low",
            "player_fault": distance < 10,  # Very close = likely player error
            "time_to_react": self._calculate_reaction_time(distance, player_speed)
        }
    
    def _calculate_reaction_time(self, distance: float, speed: float) -> float:
        """Calculate theoretical reaction time available"""
        if speed <= 0:
            return float('inf')
        return distance / (speed * 60)  # Approximate time in seconds
    
    def trigger_sound_effect(self, sound_name: str, trigger_reason: str, 
                           player_context: Dict, sound_context: Dict = None):
        """
        Log sound effect triggers with detailed context.
        
        Args:
            sound_name: Name of the sound file/effect
            trigger_reason: Why the sound was triggered
            player_context: Player state when sound triggered
            sound_context: Additional context about the sound
        """
        current_time = time.time()
        
        # Check cooldown
        if sound_name in self.sound_cooldowns:
            if current_time < self.sound_cooldowns[sound_name]:
                self.logger.debug(f"Sound {sound_name} on cooldown, skipping")
                return
        
        sound_event = {
            "timestamp": current_time,
            "event_type": "sound_trigger",
            "sound_name": sound_name,
            "trigger_reason": trigger_reason,
            "player_context": player_context.copy(),
            "sound_context": sound_context or {},
            "surface_type": self.current_surface.value if self.current_surface else "unknown",
            "cooldown_applied": self._get_sound_cooldown(sound_name)
        }
        
        self.sound_triggers.append(sound_event)
        self._log_environmental_event("sound_trigger", sound_event)
        
        # Apply cooldown
        cooldown_duration = self._get_sound_cooldown(sound_name)
        self.sound_cooldowns[sound_name] = current_time + cooldown_duration
        
        self.logger.info(
            f"Sound Triggered: {sound_name} | "
            f"Reason: {trigger_reason} | "
            f"Surface: {self.current_surface.value if self.current_surface else 'unknown'} | "
            f"Cooldown: {cooldown_duration}s"
        )
    
    def _trigger_collision_sound(self, collision_data: Dict):
        """Trigger appropriate sound for collision type"""
        collision_type = collision_data["collision_type"]
        severity = collision_data["severity"]
        
        if collision_type == "near_miss":
            sound_name = "whoosh_close"
            trigger_reason = "near_miss_detected"
        elif severity == CollisionSeverity.SEVERE.value:
            sound_name = "crash_heavy"
            trigger_reason = "severe_collision"
        elif severity == CollisionSeverity.MODERATE.value:
            sound_name = "crash_medium"
            trigger_reason = "moderate_collision"
        else:
            sound_name = "bump_light"
            trigger_reason = "light_collision"
        
        self.trigger_sound_effect(
            sound_name=sound_name,
            trigger_reason=trigger_reason,
            player_context=collision_data["player_state"],
            sound_context={
                "collision_distance": collision_data["distance"],
                "object_type": collision_data["object_type"]
            }
        )
    
    def _get_sound_cooldown(self, sound_name: str) -> float:
        """Get appropriate cooldown for sound effect"""
        cooldown_map = {
            "crash_heavy": 2.0,
            "crash_medium": 1.5,
            "bump_light": 1.0,
            "whoosh_close": 0.5,
            "engine_rev": 0.3,
            "tire_screech": 1.0,
            "horn": 2.0
        }
        return cooldown_map.get(sound_name, 1.0)
    
    def _update_sound_cooldowns(self, dt: float):
        """Update sound effect cooldowns"""
        current_time = time.time()
        expired_sounds = [
            sound for sound, expiry_time in self.sound_cooldowns.items()
            if current_time >= expiry_time
        ]
        for sound in expired_sounds:
            del self.sound_cooldowns[sound]
    
    def _categorize_density(self, density: float) -> str:
        """Categorize traffic density"""
        if density < 0.2:
            return "very_low"
        elif density < 0.4:
            return "low"
        elif density < 0.6:
            return "medium"
        elif density < 0.8:
            return "high"
        else:
            return "very_high"
    
    def _categorize_player_speed(self, speed: float) -> str:
        """Categorize player speed"""
        if speed < 0.3:
            return "slow"
        elif speed < 0.6:
            return "medium"
        else:
            return "fast"
    
    def _log_environmental_event(self, event_type: str, data: Dict):
        """Log environmental event to game logger if available"""
        if self.events_logged_this_frame >= self.max_events_per_frame:
            return  # Prevent log spam
        
        if hasattr(self, 'game_logger') and self.game_logger:
            self.game_logger.log_system_event("environment", event_type, data)
        
        self.events_logged_this_frame += 1
    
    def get_surface_stats(self) -> Dict:
        """Get statistics about surface interactions"""
        if not self.surface_history:
            return {}
        
        stats = {}
        for surface_type in SurfaceType:
            interactions = [
                interaction for interaction in self.surface_history
                if interaction.surface_type == surface_type
            ]
            
            if interactions:
                total_time = sum(
                    interaction.duration for interaction in interactions
                    if interaction.duration is not None
                )
                avg_speed = sum(
                    interaction.player_speed_avg for interaction in interactions
                ) / len(interactions)
                
                stats[surface_type.value] = {
                    "total_interactions": len(interactions),
                    "total_time": total_time,
                    "average_speed": avg_speed,
                    "percentage_of_time": total_time / sum(
                        i.duration for i in self.surface_history if i.duration
                    ) * 100 if self.surface_history else 0
                }
        
        return stats
    
    def get_collision_stats(self) -> Dict:
        """Get statistics about collision events"""
        if not self.collision_history:
            return {}
        
        total_collisions = len([c for c in self.collision_history if c["collision_type"] == "collision"])
        total_near_misses = len([c for c in self.collision_history if c["collision_type"] == "near_miss"])
        
        severity_counts = {}
        for severity in CollisionSeverity:
            severity_counts[severity.value] = len([
                c for c in self.collision_history 
                if c["severity"] == severity.value
            ])
        
        return {
            "total_collisions": total_collisions,
            "total_near_misses": total_near_misses,
            "collision_rate": total_collisions / max(1, len(self.collision_history)),
            "near_miss_rate": total_near_misses / max(1, len(self.collision_history)),
            "severity_breakdown": severity_counts,
            "average_reaction_time": self._calculate_average_reaction_time()
        }
    
    def _calculate_average_reaction_time(self) -> float:
        """Calculate average reaction time from collision data"""
        reaction_times = [
            c["impact_analysis"]["time_to_react"] 
            for c in self.collision_history 
            if "impact_analysis" in c and "time_to_react" in c["impact_analysis"]
            and c["impact_analysis"]["time_to_react"] != float('inf')
        ]
        
        return sum(reaction_times) / len(reaction_times) if reaction_times else 0.0


# Example Integration Patterns for Drive Scene
# ===========================================

class DriveGameIntegrationExample:
    """
    Example showing how to integrate EnhancedEnvironmentalLogger into the Drive scene.
    
    These patterns would be added to the existing DriveGame class in src/scenes/drive.py
    """
    
    def __init__(self):
        # Initialize the enhanced logger
        self.env_logger = EnhancedEnvironmentalLogger(
            game_logger=getattr(self.scene_manager, 'game_logger', None)
        )
        
    def update(self, dt: float):
        """Modified update method with enhanced logging"""
        # Update environmental logger
        self.env_logger.update(dt, self.player_x, self.player_y, self.player_speed)
        
        # Existing update logic...
        # self._update_racing(dt)
        # self._update_traffic(dt)
        
        # Enhanced collision checking
        self._check_enhanced_collisions(dt)
        
    def _spawn_npc_car(self):
        """Modified NPC car spawning with enhanced logging"""
        # Existing spawn logic...
        # car = NPCCar(...)
        
        # Determine spawn reason based on game state
        spawn_reason = self._determine_spawn_reason()
        
        # Calculate current traffic density
        traffic_density = len(self.npc_cars) / 8.0  # Max 8 cars
        
        # Prepare car data for logging
        car_data = {
            "id": f"npc_{len(self.npc_cars)}",
            "x": 0.5,  # car.x
            "y": -200,  # car.y  
            "lane": 3,  # car.lane
            "distance": -200,  # car.road_pos.distance
            "speed": 1.0,  # car.speed
            "direction": 1,  # car.direction
            "vehicle_type": "sedan",  # car.vehicle_type
            "ai_behavior": "cruising",  # car.ai_state
            "total_cars": len(self.npc_cars),
            "cars_in_lane": len([c for c in self.npc_cars if c.road_pos.lane == 3])
        }
        
        # Prepare player context
        player_context = {
            "speed": self.player_speed,
            "x": self.player_x,
            "y": self.player_y,
            "surface": self.env_logger.current_surface.value,
            "distance_traveled": self.distance_traveled
        }
        
        # Log the spawn event
        self.env_logger.log_traffic_spawn(car_data, spawn_reason, traffic_density, player_context)
        
    def _determine_spawn_reason(self) -> SpawnReason:
        """Determine why we're spawning a car"""
        traffic_density = len(self.npc_cars) / 8.0
        
        if traffic_density < 0.3:
            return SpawnReason.DENSITY_LOW
        elif self.player_speed > 0.8:
            return SpawnReason.CHALLENGE
        elif hasattr(self, 'scripted_spawns') and self.scripted_spawns:
            return SpawnReason.SCRIPTED
        else:
            return SpawnReason.ROUTINE
    
    def _check_enhanced_collisions(self, dt: float):
        """Enhanced collision checking with environmental logging"""
        # Prepare collision objects list
        collision_objects = []
        
        # Add traffic cars
        for i, car in enumerate(self.npc_cars):
            collision_objects.append({
                "rect": pygame.Rect(car.x * self.screen_width - 20, 
                                  self.screen_height * 0.5 - 15, 40, 30),
                "type": "traffic_car",
                "id": f"npc_{i}",
                "speed": car.speed,
                "lane": car.road_pos.lane,
                "direction": car.direction,
                "mass_factor": 1.0,  # Regular car
                "player_x": self.player_x,
                "player_y": self.player_y
            })
        
        # Add hazards
        for i, hazard in enumerate(getattr(self, 'hazards', [])):
            collision_objects.append({
                "rect": pygame.Rect(hazard.x * self.screen_width - 15,
                                  self.screen_height * 0.5 - 10, 30, 20),
                "type": f"hazard_{hazard.hazard_type}",
                "id": f"hazard_{i}",
                "speed": 0.0,
                "lane": hazard.road_pos.lane,
                "direction": 0,
                "mass_factor": 0.5,  # Lighter than cars
                "player_x": self.player_x,
                "player_y": self.player_y
            })
        
        # Player collision rectangle
        player_rect = pygame.Rect(self.player_x * self.screen_width - 20,
                                self.screen_height * 0.5 - 15, 40, 30)
        
        # Check for collisions with enhanced logging
        collision_event = self.env_logger.check_collision_event(
            player_rect, collision_objects, self.player_speed
        )
        
        # Handle collision if detected
        if collision_event and collision_event["collision_type"] == "collision":
            self._handle_enhanced_collision(collision_event)
    
    def _handle_enhanced_collision(self, collision_event: Dict):
        """Handle collision with enhanced feedback"""
        severity = collision_event["severity"]
        
        # Apply different effects based on severity
        if severity == CollisionSeverity.SEVERE.value:
            self.collision_cooldown = 3.0
            self.lives -= 2
            # Screen shake, heavy sound effect, etc.
        elif severity == CollisionSeverity.MODERATE.value:
            self.collision_cooldown = 2.0
            self.lives -= 1
            # Medium effects
        else:  # Glancing
            self.collision_cooldown = 1.0
            # Light effects
        
        # Sound is automatically triggered by the environmental logger
    
    def _trigger_engine_sound(self, player_speed_delta: float):
        """Example of triggering sound effects through environmental logger"""
        if abs(player_speed_delta) > 0.1:  # Significant speed change
            trigger_reason = "acceleration" if player_speed_delta > 0 else "deceleration"
            
            player_context = {
                "speed": self.player_speed,
                "speed_delta": player_speed_delta,
                "surface": self.env_logger.current_surface.value
            }
            
            sound_context = {
                "intensity": min(1.0, abs(player_speed_delta) * 5),
                "engine_type": "v6"  # Could vary by vehicle
            }
            
            self.env_logger.trigger_sound_effect(
                sound_name="engine_rev",
                trigger_reason=trigger_reason,
                player_context=player_context,
                sound_context=sound_context
            )


# Usage Example in Main Game Loop
# ================================

def example_usage():
    """
    Example of how the enhanced environmental logger would be used
    in the main game loop of the Drive scene.
    """
    
    # Initialize (in DriveGame.__init__)
    env_logger = EnhancedEnvironmentalLogger()
    
    # In update loop
    dt = 1/60  # 60 FPS
    player_x = 0.5  # Center of screen
    player_y = 0.0  # Current position
    player_speed = 0.8  # 80% of max speed
    
    # Update environmental tracking
    env_logger.update(dt, player_x, player_y, player_speed)
    
    # Example traffic spawn
    car_data = {
        "id": "npc_1",
        "x": 0.3, "y": -150, "lane": 2, "speed": 0.6,
        "direction": 1, "vehicle_type": "sedan"
    }
    env_logger.log_traffic_spawn(
        car_data, 
        SpawnReason.ROUTINE, 
        traffic_density=0.4,
        player_context={"speed": player_speed, "x": player_x}
    )
    
    # Example collision check
    collision_objects = [{"rect": pygame.Rect(100, 100, 40, 30), "type": "car"}]
    player_rect = pygame.Rect(95, 95, 40, 30)  # Very close = near miss
    
    collision_event = env_logger.check_collision_event(
        player_rect, collision_objects, player_speed
    )
    
    # Example sound trigger
    env_logger.trigger_sound_effect(
        sound_name="tire_screech",
        trigger_reason="hard_turn",
        player_context={"speed": player_speed, "surface": "road_asphalt"}
    )
    
    # Get statistics
    surface_stats = env_logger.get_surface_stats()
    collision_stats = env_logger.get_collision_stats()
    
    print(f"Surface Stats: {surface_stats}")
    print(f"Collision Stats: {collision_stats}")


if __name__ == "__main__":
    # This file is meant to be imported and integrated into the Drive scene
    # But we can run some basic tests here
    example_usage()
    print("Enhanced Environmental Logging Example Complete!")
    print("\nIntegration Instructions:")
    print("1. Copy relevant classes to src/scenes/drive.py")
    print("2. Initialize EnhancedEnvironmentalLogger in DriveGame.__init__")
    print("3. Add env_logger.update() call to main update loop")
    print("4. Replace collision checking with enhanced version")
    print("5. Add logging calls to traffic spawning logic")
    print("6. Integrate sound effect triggers throughout the scene")