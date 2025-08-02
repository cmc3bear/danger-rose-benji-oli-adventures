"""The Drive - OutRun-style racing minigame with music selection."""

import random
import time
import math
from typing import Optional, List
from dataclasses import dataclass

import pygame

from src.config.constants import (
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_YELLOW,
    COLOR_SKY_BLUE,
    FONT_LARGE,
    FONT_SMALL,
    FONT_HUGE,
    GAME_DURATION,
    SCENE_HUB_WORLD,
    SCENE_LEADERBOARD,
    OVERLAY_GAME_OVER_ALPHA,
)
from src.ui.music_selector import MusicSelector, MusicTrack
from src.ui.vehicle_selector import VehicleSelector
from src.managers.race_music_manager import RaceMusicManager, RaceState
from src.utils.asset_paths import get_sfx_path
from src.utils.sprite_loader import load_vehicle_sprite
from src.ui.drawing_helpers import draw_text_with_background, draw_instructions


@dataclass
class NPCCar:
    """Represents an NPC vehicle in traffic (cars and trucks)."""
    x: float               # Horizontal position (0.0-1.0)
    y: float               # Vertical position (distance ahead/behind player)
    lane: int              # Lane number (0-3: 0,1=player direction, 2,3=oncoming)
    speed: float           # Relative speed compared to player
    color: tuple           # RGB color for the vehicle
    vehicle_type: str = "car"       # "car" or "truck"
    direction: int = 1     # 1 = same direction as player, -1 = oncoming
    width: int = 32        # Vehicle width in pixels
    height: int = 48       # Vehicle height in pixels
    lane_change_timer: float = 0.0  # Timer for lane changes
    ai_state: str = "cruising"      # AI behavior state
    collision_zone: tuple = (32, 48)  # Collision detection size (width, height)


@dataclass
class Hazard:
    """Represents a hazard on the road (static or dynamic)."""
    x: float               # Horizontal position (0.0-1.0)
    y: float               # Vertical position (distance ahead/behind player)
    lane: int              # Lane number where hazard is placed
    hazard_type: str       # "cone", "barrier", "warning_sign", "oil_slick", "debris", "water_puddle"
    width: int = 16        # Hazard width in pixels
    height: int = 24       # Hazard height in pixels
    collision_zone: tuple = (16, 24)  # Collision detection size
    color: tuple = (255, 140, 0)  # Default orange for cones
    
    # Dynamic hazard properties
    is_dynamic: bool = False      # True for oil slicks, debris, etc.
    effect_type: str = "damage"   # "damage", "slip", "slow"
    effect_duration: float = 0.0  # How long the effect lasts
    effect_strength: float = 1.0  # Multiplier for effect intensity
    spawn_source: str = None      # What caused this hazard (e.g., "truck" for oil)


class DriveGame:
    """
    The Drive - OutRun-inspired racing minigame.
    
    Features music selection before racing, dynamic music during gameplay,
    and classic arcade-style racing mechanics.
    """
    
    # Game states
    STATE_MUSIC_SELECT = "music_select"
    STATE_VEHICLE_SELECT = "vehicle_select"
    STATE_READY = "ready"
    STATE_RACING = "racing"
    STATE_GAME_OVER = "game_over"
    
    def __init__(self, scene_manager):
        """Initialize the Drive racing game."""
        self.scene_manager = scene_manager
        self.screen_width = scene_manager.screen_width
        self.screen_height = scene_manager.screen_height
        
        # Game state
        self.state = self.STATE_MUSIC_SELECT
        self.race_duration = GAME_DURATION * 2  # 2 minutes for racing
        self.time_remaining = self.race_duration
        self.start_time = None
        
        # Music system
        self.music_selector = MusicSelector(
            self.screen_width,
            self.screen_height,
            scene_manager.sound_manager
        )
        self.race_music_manager = RaceMusicManager(scene_manager.sound_manager)
        self.selected_track: Optional[MusicTrack] = None
        
        # Vehicle system
        self.vehicle_selector = VehicleSelector(
            self.screen_width,
            self.screen_height,
            scene_manager.sound_manager
        )
        self.selected_vehicle = None
        self.car_sprite = None
        self.car_rotation = 0.0          # Current car sprite rotation angle
        self.momentum_x = 0.0            # Horizontal momentum for drift effects
        self.drift_factor = 0.0          # Current drift intensity
        
        # Dynamic hazard effects
        self.active_effects = []         # List of active hazard effects
        self.slip_factor = 1.0          # Steering multiplier (1.0 = normal, 0.3 = slippery)
        self.effect_visual_timer = 0.0   # Timer for visual feedback
        self.slip_spin_angle = 0.0      # Current spin angle during slip effect
        self.slip_spin_speed = 720.0    # Degrees per second for 360 spin
        
        # Street boundary system
        self.off_road_timer = 0.0        # Time spent off-road
        self.off_road_penalty = 0.0      # Speed penalty for off-road driving
        self.road_left_edge = 0.0        # Current left road boundary (0.0-1.0)
        self.road_right_edge = 1.0       # Current right road boundary (0.0-1.0)
        
        # NPC Traffic System
        self.npc_cars: List[NPCCar] = []  # List of active NPC cars
        self.traffic_spawn_timer = 0.0    # Timer for spawning new traffic
        self.traffic_density = 0.3        # Probability of spawning traffic
        self.max_traffic_cars = 10        # Maximum number of NPC cars on screen (increased for better flow)
        
        # Collision Detection System
        self.collision_cooldown = 0.0     # Cooldown timer to prevent multiple collisions
        self.collision_damage = 0.0       # Accumulated collision damage (0.0-1.0)
        self.collision_speed_penalty = 0.0  # Current speed penalty from collisions
        self.collision_recovery_rate = 0.5   # How fast collision penalties recover
        self.last_collision_type = None   # "car", "truck", "cone", "barrier" for feedback
        self.collision_flash_timer = 0.0  # Timer for visual collision feedback
        
        # Static Hazard System
        self.hazards: List[Hazard] = []   # List of active hazards
        self.construction_zones = []       # List of (start_y, end_y) for construction zones
        self.next_construction_y = 500     # Y position for next construction zone
        self.construction_spawn_timer = 0.0 # Timer for spawning construction zones
        
        # Scenic Background System
        self.scenery_distance = 0.0       # Distance traveled for scenery changes
        self.current_scenery = "forest"   # Current scenery type
        self.scenery_transition = 0.0     # Transition between scenery types (0-1)
        self.scenery_types = ["forest", "mountains", "city", "lake", "desert"]
        self.next_scenery_change = 1000   # Distance until next scenery change
        
        # Comic Text Taunt System
        self.comic_text_timer = random.uniform(10.0, 15.0)  # Time until next taunt
        self.current_comic_text = None    # Current text being displayed
        self.comic_text_duration = 3.0    # How long to show the text
        self.comic_text_fade_timer = 0.0  # Timer for fade animation
        self.comic_taunts = [
            "Learn how to drive!",
            "Nice driving, grandma!",
            "Did you get your license from a cereal box?",
            "Sunday driver alert!",
            "Is this your first time?",
            "The gas pedal is on the right!",
            "Speed limit's just a suggestion!",
            "Move it or lose it!",
            "You drive like my neighbor!",
            "Beep beep! Coming through!",
            "Are we there yet?",
            "I've seen snails go faster!",
            "Driving school dropout?",
            "Born to be mild!",
            "Wake me when we get there..."
        ]
        
        # Music selector doesn't need callbacks - we handle events in handle_event
        
        # Racing mechanics
        self.player_speed = 0.0         # Current speed (0.0 to 1.0)
        self.max_speed = 1.0
        self.acceleration = 0.5         # Speed increase per second
        self.deceleration = 0.8         # Speed decrease per second
        self.player_x = 0.5             # Horizontal position (0.0 to 1.0)
        self.road_curve = 0.0           # Current road curvature
        self.road_position = 0.0        # Position along the road
        
        # Road surface variation effects
        self.width_oscillation = 0.0    # Independent width variation
        self.surface_noise = 0.0         # Road surface micro-variations
        self.speed_shimmer = 0.0         # Visual speed feedback effect
        
        # Turn system for discrete left/right turns
        self.turn_state = "straight"     # "straight", "turning_left", "turning_right"
        self.turn_intensity = 0.0        # 0.0 to 1.0, how sharp the current turn is
        self.turn_progress = 0.0         # 0.0 to 1.0, progress through current turn
        self.turn_timer = 0.0            # Time until next turn decision
        self.straight_duration = 8.0     # Seconds of straight road before turns
        self.turn_duration = 4.0         # Seconds to complete a turn
        self.next_turn_direction = None  # "left" or "right" for the next turn
        
        # Racing state
        self.race_state = RaceState(
            speed=0.0,
            position=1,
            total_racers=8,
            time_remaining=self.race_duration
        )
        
        # Visual elements
        self.horizon_y = self.screen_height // 2
        self.road_width = 500  # Increased 25% from 400 to 500 for proper 4-lane highway
        self.max_road_width = 1000  # Increased proportionally from 800 to 1000
        self.car_width = 64  # Display width (scaled from 128)
        self.car_height = 96  # Display height (scaled from 192)
        
        # UI fonts
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_huge = pygame.font.Font(None, FONT_HUGE)
        
        # Score and statistics
        self.distance_traveled = 0.0
        self.top_speed_reached = 0.0
        self.score = 0
        
        # Input handling
        self.keys_pressed = set()
        
    def handle_event(self, event):
        """Handle input events."""
        if self.state == self.STATE_MUSIC_SELECT:
            # Music selector handles its own events
            result = self.music_selector.handle_event(event)
            if result == "track_selected":
                self._on_track_selected(self.music_selector.get_selected_track())
            elif result == "cancelled":
                self._on_music_cancelled()
            return None
            
        elif self.state == self.STATE_VEHICLE_SELECT:
            # Vehicle selector handles its own events
            result = self.vehicle_selector.handle_event(event)
            if result == "vehicle_selected":
                self._on_vehicle_selected(self.vehicle_selector.get_selected_vehicle())
            elif result == "cancelled":
                self._on_vehicle_cancelled()
            return None
            
        elif event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            
            if self.state == self.STATE_READY:
                if event.key == pygame.K_SPACE:
                    self._start_race()
                elif event.key == pygame.K_ESCAPE:
                    return SCENE_HUB_WORLD
                elif event.key == pygame.K_m:
                    # Return to music selection
                    self.state = self.STATE_MUSIC_SELECT
                    
            elif self.state == self.STATE_RACING:
                if event.key == pygame.K_ESCAPE:
                    self._end_race()
                elif event.key == pygame.K_q:
                    # Quick return to hub world
                    return SCENE_HUB_WORLD
                    
            elif self.state == self.STATE_GAME_OVER:
                if event.key == pygame.K_SPACE:
                    self._restart_game()
                elif event.key == pygame.K_l:
                    return SCENE_LEADERBOARD
                elif event.key == pygame.K_ESCAPE:
                    return SCENE_HUB_WORLD
                elif event.key == pygame.K_m:
                    # Return to music selection
                    self.state = self.STATE_MUSIC_SELECT
                    
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
            
        return None
        
    def update(self, dt: float):
        """Update game state."""
        if self.state == self.STATE_MUSIC_SELECT:
            self.music_selector.update(dt)
            
        elif self.state == self.STATE_VEHICLE_SELECT:
            self.vehicle_selector.update(dt)
            
        elif self.state == self.STATE_RACING:
            self._update_racing(dt)
            
        # Always update race music manager
        self.race_music_manager.update(dt)
        
    def _update_racing(self, dt: float):
        """Update racing mechanics and state."""
        # Handle input
        self._handle_racing_input(dt)
        
        # Update timer
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.time_remaining = max(0, self.race_duration - elapsed)
            
            if self.time_remaining <= 10:
                self.race_state.is_final_lap = True
                
            if self.time_remaining <= 0:
                self._end_race()
                return
                
        # Update turn system - discrete turns every 8-10 seconds
        self._update_turn_system(dt)
        
        # Update road position based on speed
        self.road_position += self.player_speed * dt * 10
        
        # Add gentle freeway curves in addition to discrete turns
        # Use low-frequency sine waves for gradual highway curves
        freeway_curve_freq = 0.02  # Slower curves for more noticeable effect
        freeway_curve_amplitude = 0.4  # More noticeable curves (was 0.25)
        
        # Base freeway curve
        freeway_curve = math.sin(self.road_position * freeway_curve_freq) * freeway_curve_amplitude
        
        # Add slight variation with a second wave
        freeway_variation = math.sin(self.road_position * freeway_curve_freq * 1.7) * freeway_curve_amplitude * 0.3
        
        # Combine freeway curves with turn system curves
        # When in a discrete turn, reduce freeway curve influence
        if self.turn_state != "straight":
            freeway_influence = 0.3  # Reduce freeway curves during sharp turns
        else:
            freeway_influence = 1.0  # Full freeway curves on straights
            
        # Apply combined road curve
        self.road_curve = (self.road_curve * 0.7) + ((freeway_curve + freeway_variation) * freeway_influence * 0.3)
        
        # Natural road width variation system (±5% = ±25 pixels from 500px base)
        # Use layered noise for more natural variation
        primary_freq = 0.08 + self.player_speed * 0.05  # Slower, broader changes
        secondary_freq = 0.25 + self.player_speed * 0.1  # Faster detail
        
        # Combine two sine waves with different frequencies for natural feel
        primary_wave = math.sin(self.road_position * primary_freq) * 20.0  # Increased for 500px base
        secondary_wave = math.sin(self.road_position * secondary_freq * 1.3) * 7.5  # Increased for 500px base
        
        # Ensure total amplitude stays within ±5% (±25 pixels)
        self.width_oscillation = primary_wave + secondary_wave
        
        # Subtle movement effects for enhanced racing feel
        # Surface micro-variations (very small road texture simulation)
        surface_freq = 1.8 + self.player_speed * 2.0  # High frequency, speed-dependent
        self.surface_noise = math.sin(self.road_position * surface_freq) * 3.75  # Increased for 500px base
        
        # Speed shimmer effect (visual feedback for speed)
        shimmer_intensity = self.player_speed * 0.8  # Stronger at higher speeds
        self.speed_shimmer = math.sin(self.road_position * 3.2) * shimmer_intensity
        
        # Update distance and score
        distance_delta = self.player_speed * dt * 100
        self.distance_traveled += distance_delta
        self.score += int(distance_delta * 10)
        
        # Track top speed
        self.top_speed_reached = max(self.top_speed_reached, self.player_speed)
        
        # Update race state
        self.race_state.speed = self.player_speed
        self.race_state.time_remaining = self.time_remaining
        
        # Simulate position changes based on speed
        # (In a real game, this would be based on AI opponents)
        target_position = max(1, int(9 - self.player_speed * 8))
        if target_position != self.race_state.position:
            self.race_state.position = target_position
            
        # Update street boundaries for EV restriction
        self._update_road_boundaries()
        
        # Update NPC traffic system
        self._update_traffic(dt)
        
        # Update static hazards system
        self._update_hazards(dt)
        
        # Update dynamic hazard spawning
        self._update_dynamic_hazard_spawning(dt)
        
        # Update active hazard effects
        self._update_hazard_effects(dt)
        
        # Update comic text taunts
        self._update_comic_text(dt)
        
        # Check for collisions with traffic
        self._check_traffic_collisions(dt)
        
        # Check for collisions with hazards
        self._check_hazard_collisions(dt)
        
        # Update race music
        self.race_music_manager.update_race_state(self.race_state)
        
    def _update_road_boundaries(self):
        """Calculate current road boundaries based on road geometry."""
        # Calculate road center and width (same logic as drawing)
        road_center_pixels = self.screen_width // 2 + int(self.road_curve * 100)  # Doubled curve effect
        
        # Apply road width variations
        base_width_variation = int(self.width_oscillation)
        surface_variation = int(self.surface_noise)
        current_width_pixels = self.road_width + base_width_variation + surface_variation
        
        # Convert pixel boundaries to normalized coordinates (0.0-1.0)
        road_left_pixels = road_center_pixels - current_width_pixels // 2
        road_right_pixels = road_center_pixels + current_width_pixels // 2
        
        # Add safety margin for car width (car is 64px wide, so 32px each side)
        car_half_width = 32
        safe_left_pixels = road_left_pixels + car_half_width
        safe_right_pixels = road_right_pixels - car_half_width
        
        # Convert to normalized coordinates
        self.road_left_edge = max(0.0, safe_left_pixels / self.screen_width)
        self.road_right_edge = min(1.0, safe_right_pixels / self.screen_width)
        
        # Ensure valid boundaries
        if self.road_left_edge >= self.road_right_edge:
            # Emergency fallback - narrow road, use center area
            center = (self.road_left_edge + self.road_right_edge) / 2
            margin = 0.1
            self.road_left_edge = max(0.0, center - margin)
            self.road_right_edge = min(1.0, center + margin)
            
    def _enforce_street_boundaries(self, dt: float):
        """Enforce EV street boundary restrictions and apply off-road penalties."""
        # Check if car is off-road
        is_off_road = (self.player_x < self.road_left_edge or self.player_x > self.road_right_edge)
        
        if is_off_road:
            # Accumulate off-road time
            self.off_road_timer += dt
            
            # Apply immediate corrections to keep car near road
            if self.player_x < self.road_left_edge:
                # Off-road to the left - push back toward road
                overshoot = self.road_left_edge - self.player_x
                correction_strength = min(1.0, overshoot * 8.0)  # Stronger correction for bigger overshoot
                self.player_x += correction_strength * dt * 2.0
                self.player_x = min(self.player_x, self.road_left_edge + 0.02)  # Allow small overshoot
                
            elif self.player_x > self.road_right_edge:
                # Off-road to the right - push back toward road
                overshoot = self.player_x - self.road_right_edge
                correction_strength = min(1.0, overshoot * 8.0)
                self.player_x -= correction_strength * dt * 2.0
                self.player_x = max(self.player_x, self.road_right_edge - 0.02)  # Allow small overshoot
            
            # Build up off-road penalty based on time and speed
            penalty_rate = 1.5 * self.player_speed  # Faster = worse penalty
            max_penalty = 0.6  # Maximum 60% speed reduction
            self.off_road_penalty = min(max_penalty, self.off_road_penalty + penalty_rate * dt)
            
            # Add visual and audio feedback for off-road driving
            if self.off_road_timer > 0.5:  # After 0.5 seconds off-road
                # Trigger warning effects (will be shown in UI)
                pass
                
        else:
            # On-road - gradually reduce penalties
            self.off_road_timer = max(0.0, self.off_road_timer - dt * 2.0)  # Recover faster than accumulate
            self.off_road_penalty = max(0.0, self.off_road_penalty - dt * 0.8)  # Gradual penalty recovery
            
        # Apply speed penalty
        if self.off_road_penalty > 0.0:
            # Reduce max effective speed when off-road
            effective_max_speed = self.max_speed * (1.0 - self.off_road_penalty)
            if self.player_speed > effective_max_speed:
                # Force deceleration
                deceleration_rate = 2.0 * dt  # Quick slowdown when off-road
                self.player_speed = max(effective_max_speed, self.player_speed - deceleration_rate)
        
    def _update_turn_system(self, dt: float):
        """Update the discrete turn system for realistic racing turns."""
        import random
        
        # Update turn timer
        self.turn_timer += dt
        
        if self.turn_state == "straight":
            # Check if it's time to start a turn
            if self.turn_timer >= self.straight_duration:
                # Decide next turn direction (alternate with some randomness)
                if self.next_turn_direction is None:
                    self.next_turn_direction = random.choice(["left", "right"])
                else:
                    # Prefer alternating turns, but add some randomness
                    if random.random() < 0.8:  # 80% chance to alternate
                        self.next_turn_direction = "left" if self.next_turn_direction == "right" else "right"
                    # else keep same direction (20% chance)
                
                # Start the turn
                self.turn_state = f"turning_{self.next_turn_direction}"
                self.turn_progress = 0.0
                self.turn_timer = 0.0
                
                # Set turn intensity (randomize slightly for variety)
                base_intensity = 0.6
                intensity_variation = random.uniform(-0.2, 0.2)
                self.turn_intensity = max(0.3, min(1.0, base_intensity + intensity_variation))
                
        elif self.turn_state in ["turning_left", "turning_right"]:
            # Update turn progress
            self.turn_progress = min(1.0, self.turn_timer / self.turn_duration)
            
            # Check if turn is complete
            if self.turn_progress >= 1.0:
                self.turn_state = "straight"
                self.turn_progress = 0.0
                self.turn_timer = 0.0
                # Add some variation to straight duration (8-10 seconds)
                self.straight_duration = random.uniform(8.0, 10.0)
        
        # Calculate road curve based on turn state
        if self.turn_state == "straight":
            # Gradually return to straight
            self.road_curve *= 0.95  # Smooth transition back to straight
        else:
            # Calculate smooth turn curve using sine function
            turn_progress_smooth = 0.5 * (1 - math.cos(self.turn_progress * math.pi))
            turn_direction = 1.0 if self.turn_state == "turning_right" else -1.0
            self.road_curve = turn_direction * self.turn_intensity * turn_progress_smooth
            
    def _handle_racing_input(self, dt: float):
        """Handle racing input and update player state."""
        # Enhanced acceleration/deceleration with turn physics
        base_acceleration = self.acceleration
        base_deceleration = self.deceleration
        
        # Apply turn-based speed adjustment (realistic racing physics)
        if self.turn_state != "straight":
            # Reduce acceleration and increase deceleration in turns
            turn_severity = self.turn_intensity * self.turn_progress
            acceleration_penalty = 0.4 * turn_severity  # Up to 40% reduction
            deceleration_increase = 0.6 * turn_severity  # Up to 60% increase
            
            base_acceleration *= (1.0 - acceleration_penalty)
            base_deceleration *= (1.0 + deceleration_increase)
        
        if pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed:
            self.player_speed = min(
                self.max_speed,
                self.player_speed + base_acceleration * dt
            )
            # Boost effect at high speeds (harder to achieve in turns)
            boost_threshold = 0.8 if self.turn_state == "straight" else 0.9
            if self.player_speed > boost_threshold:
                self.race_state.is_boost = True
        else:
            self.player_speed = max(
                0.0,
                self.player_speed - base_deceleration * dt
            )
            self.race_state.is_boost = False
            
        # Apply collision speed penalty to effective speed
        effective_speed = self.player_speed * (1.0 - self.collision_speed_penalty)
        self.player_speed = max(0.1, effective_speed)  # Minimum speed to prevent complete stop
            
        # Enhanced steering with off-road resistance
        base_steering_speed = 0.35 * dt  # Ultra-tight: reduced from 0.5 to 0.35 for precision control
        
        # Reduce steering responsiveness when off-road or penalized
        steering_penalty = self.off_road_penalty * 0.5  # Up to 30% steering reduction
        effective_steering_speed = base_steering_speed * (1.0 - steering_penalty) * self.slip_factor
        
        if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
            self.player_x = max(0.0, self.player_x - effective_steering_speed)
        if pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
            self.player_x = min(1.0, self.player_x + effective_steering_speed)
            
        # Enhanced vehicle physics: gradual turn response
        if self.turn_state != "straight":
            # Calculate desired position based on turn
            turn_influence_strength = 0.04  # Ultra-reduced from 0.08 to 0.04 for minimal auto-assistance
            turn_direction = 1.0 if self.turn_state == "turning_right" else -1.0
            
            # Desired position shifts toward inside of turn for realistic racing line
            desired_offset = -turn_direction * self.turn_intensity * turn_influence_strength * self.turn_progress
            target_x = 0.5 + desired_offset  # Start from center and shift
            
            # Gradually move toward target position (realistic steering response)
            steering_response_rate = 0.15 * dt  # Ultra-reduced from 0.3 to 0.15 for tight response
            position_difference = target_x - self.player_x
            self.player_x += position_difference * steering_response_rate
        
        # Apply road curve influence (reduced since we have better turn physics)
        curve_influence = self.road_curve * self.player_speed * dt * 0.04  # Ultra-reduced from 0.08 to 0.04
        self.player_x = max(0.0, min(1.0, self.player_x + curve_influence))
        
        # Update car rotation based on ACTUAL steering input (tied tightly to movement)
        max_rotation = 18.0  # Maximum rotation in degrees (within 15-20% range)
        
        # Calculate rotation based on actual steering input AND turn state
        input_rotation = 0.0
        
        # Direct steering input rotation (immediate response tied to movement)
        if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
            input_rotation = -max_rotation * 0.7  # Left turn rotation
        elif pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
            input_rotation = max_rotation * 0.7   # Right turn rotation
            
        # Add turn state influence (road turns) - reduced to let player control dominate
        turn_rotation = 0.0
        if self.turn_state != "straight":
            turn_direction = 1.0 if self.turn_state == "turning_right" else -1.0
            turn_rotation = turn_direction * max_rotation * 0.3 * self.turn_intensity * self.turn_progress
            
        # Combine input and turn rotations (input has priority)
        target_rotation = input_rotation + turn_rotation
        target_rotation = max(-max_rotation, min(max_rotation, target_rotation))  # Clamp to max
        
        # Smooth rotation transition (very responsive to input)
        rotation_speed = 150.0 * dt  # Very fast response to steering input
        rotation_diff = target_rotation - self.car_rotation
        if abs(rotation_diff) > rotation_speed:
            self.car_rotation += rotation_speed * (1 if rotation_diff > 0 else -1)
        else:
            self.car_rotation = target_rotation
                
        # Enhanced momentum and drift effects (Issue #9)
        if self.turn_state != "straight":
            # Build up momentum in turn direction
            turn_direction = 1.0 if self.turn_state == "turning_right" else -1.0
            momentum_build_rate = self.player_speed * self.turn_intensity * dt * 0.8
            target_momentum = turn_direction * momentum_build_rate
            
            # Smooth momentum buildup
            self.momentum_x += (target_momentum - self.momentum_x) * 3.0 * dt
            
            # Calculate drift based on speed and turn sharpness
            drift_threshold = 0.6  # Speed threshold for drift
            if self.player_speed > drift_threshold:
                drift_intensity = (self.player_speed - drift_threshold) * self.turn_intensity
                self.drift_factor = min(1.0, drift_intensity * 2.0)
            else:
                self.drift_factor *= 0.9  # Fade out drift
        else:
            # Momentum decays when straight
            self.momentum_x *= 0.85  # Gradual decay
            self.drift_factor *= 0.95  # Drift fades out
            
        # Apply momentum to player position (realistic car physics)
        momentum_influence = self.momentum_x * dt * 0.04  # Ultra-reduced from 0.08 to 0.04
        self.player_x += momentum_influence
        
        # Enforce street boundaries and apply off-road effects
        self._enforce_street_boundaries(dt)
        
        # Check for crashes (hitting road edges at high speed)
        if (self.player_x < 0.1 or self.player_x > 0.9) and self.player_speed > 0.6:
            self._crash()
            
    def _crash(self):
        """Handle player crash."""
        self.race_state.is_crash = True
        self.player_speed *= 0.3  # Reduce speed significantly
        
        # Play crash sound
        try:
            self.scene_manager.sound_manager.play_sfx(get_sfx_path("collision.ogg"))
        except:
            pass  # Sound file not available yet
            
        # Reset crash flag after brief moment
        pygame.time.set_timer(pygame.USEREVENT + 1, 500)  # Clear crash state after 500ms
        
    def _update_traffic(self, dt: float):
        """Update NPC traffic system."""
        # Update spawn timer
        self.traffic_spawn_timer += dt
        
        # Spawn new traffic cars
        spawn_interval = 1.5  # Spawn more frequently for consistent traffic
        if (self.traffic_spawn_timer > spawn_interval and  
            len(self.npc_cars) < self.max_traffic_cars):
            # Spawn with higher probability to ensure consistent traffic flow
            if random.random() < 0.7:  # 70% chance every 1.5 seconds
                self._spawn_npc_car()
            self.traffic_spawn_timer = 0.0
            
        # Update existing traffic cars
        cars_to_remove = []
        for i, car in enumerate(self.npc_cars):
            # Update car position based on direction - all from player's POV
            if car.direction == 1:
                # Same direction as player - normal relative movement
                relative_speed = car.speed - self.player_speed
                car.y += relative_speed * dt * 100  # Move relative to player
            else:
                # Oncoming traffic - from player POV they approach from ahead
                # They should appear to come toward player and pass by naturally
                # Use base speed + player speed for realistic relative motion
                base_oncoming_speed = 0.7  # Base speed for oncoming traffic when player is stopped
                oncoming_relative_speed = base_oncoming_speed + self.player_speed  # Combined approach speed
                car.y -= oncoming_relative_speed * dt * 100  # Approach from ahead (toward player)
            
            # Update AI behavior
            self._update_npc_ai(car, dt)
            
            # Check for traffic-to-traffic collision avoidance
            self._avoid_traffic_collisions(car, dt)
            
            # Enforce road boundaries for traffic cars
            self._enforce_traffic_boundaries(car)
            
            # Remove cars that are too far behind or ahead
            if car.y < -250 or car.y > 700:
                cars_to_remove.append(i)
                
        # Remove old cars (reverse order to maintain indices)
        for i in reversed(cars_to_remove):
            del self.npc_cars[i]
            
    def _spawn_npc_car(self):
        """Spawn a new NPC car in proper 4-lane traffic."""
        # 4-lane system (corrected): 
        # Lane 1: Left lane, oncoming traffic (opposite direction)
        # Lane 2: Right lane, oncoming traffic (opposite direction)
        # Lane 3: Left lane, player direction (same as player)
        # Lane 4: Right lane, player direction (same as player) 
        
        # Player is in lanes 3-4, oncoming traffic in lanes 1-2
        player_lane = 3 if self.player_x < 0.5 else 4  # Left or right in player direction
        
        # 70% chance for same direction (lanes 3-4), 30% for oncoming (lanes 1-2)
        if random.random() < 0.7:
            # Same direction traffic (lanes 3-4)
            direction = 1
            lane = random.choice([3, 4])
            # Prefer lane away from player
            if random.random() < 0.6 and lane == player_lane:
                lane = 7 - lane  # Switch to other lane (3↔4)
                
            # Spawn ahead or behind player
            spawn_ahead = random.choice([True, False])
            if spawn_ahead:
                y_position = random.uniform(150, 400)  # Ahead of player
                npc_speed = random.uniform(0.4, 0.9)   # Slower than player typically
            else:
                y_position = random.uniform(-150, -50)  # Behind player
                npc_speed = random.uniform(0.6, 1.2)    # Mix of speeds
        else:
            # Oncoming traffic (lanes 1-2)
            direction = -1
            lane = random.choice([1, 2])
            
            # Oncoming cars start far ahead and move toward player
            y_position = random.uniform(300, 600)  # Start far ahead
            npc_speed = random.uniform(0.5, 1.0)   # Oncoming speed
            
        # Convert lane to screen position using ACTUAL road boundaries
        # Use the same road calculation as the drawing code
        road_center_pixels = self.screen_width // 2  # Screen center in pixels
        base_width_variation = int(self.width_oscillation)
        surface_variation = int(self.surface_noise)
        current_road_width_pixels = self.road_width + base_width_variation + surface_variation
        
        # Calculate actual road edges in pixels
        road_left_pixels = road_center_pixels - current_road_width_pixels // 2
        road_right_pixels = road_center_pixels + current_road_width_pixels // 2
        
        # Convert to normalized coordinates (0.0-1.0)
        road_left_normalized = road_left_pixels / self.screen_width
        road_right_normalized = road_right_pixels / self.screen_width
        road_width_normalized = road_right_normalized - road_left_normalized
        
        # Split road into two directions: left half (lanes 1,2) and right half (lanes 3,4)
        direction_width = road_width_normalized / 2  # Each direction gets half the road
        lane_width = direction_width / 2  # 2 lanes per direction
        
        if direction == -1:  # Oncoming traffic (left half of road)
            if lane == 1:    # Left lane, oncoming direction
                x_position = road_left_normalized + lane_width * 0.5
            else:           # Right lane, oncoming direction (lane == 2)
                x_position = road_left_normalized + lane_width * 1.5
        else:              # Same direction as player (right half of road)
            direction_start = road_left_normalized + direction_width  # Center of road
            if lane == 3:    # Left lane, player direction
                x_position = direction_start + lane_width * 0.5
            else:           # Right lane, player direction (lane == 4)
                x_position = direction_start + lane_width * 1.5
            
        # Determine vehicle type (10% chance for trucks)
        is_truck = random.random() < 0.15  # 15% chance for semi trucks
        
        if is_truck:
            vehicle_type = "truck"
            vehicle_width = 40      # Wider than cars
            vehicle_height = 80     # Much longer than cars
            collision_zone = (40, 80)
            # Trucks are typically darker colors
            truck_colors = [
                (100, 100, 100),  # Dark gray
                (80, 80, 80),     # Darker gray
                (60, 60, 60),     # Very dark gray
                (120, 80, 40),    # Brown
                (40, 40, 120),    # Dark blue
                (80, 40, 40),     # Dark red
            ]
            vehicle_color = random.choice(truck_colors)
            # Trucks move slightly slower
            npc_speed *= 0.85
        else:
            vehicle_type = "car"
            vehicle_width = 32
            vehicle_height = 48
            collision_zone = (32, 48)
            # Regular car colors (different colors for different directions)
            if direction == 1:  # Same direction - warmer colors
                car_colors = [
                    (255, 0, 0),    # Red
                    (255, 255, 0),  # Yellow
                    (255, 128, 0),  # Orange
                    (0, 255, 0),    # Green
                ]
            else:  # Oncoming traffic - cooler colors
                car_colors = [
                    (0, 0, 255),    # Blue
                    (0, 255, 255),  # Cyan
                    (255, 0, 255),  # Magenta
                    (128, 0, 128),  # Purple
                ]
            vehicle_color = random.choice(car_colors)
        
        npc_car = NPCCar(
            x=x_position,
            y=y_position,
            lane=lane,
            speed=npc_speed,
            color=vehicle_color,
            vehicle_type=vehicle_type,
            direction=direction,
            width=vehicle_width,
            height=vehicle_height,
            collision_zone=collision_zone,
            ai_state="cruising"
        )
        
        self.npc_cars.append(npc_car)
        
    def _update_npc_ai(self, car: NPCCar, dt: float):
        """Update NPC car AI behavior for 4-lane traffic."""
        # Update lane change timer
        car.lane_change_timer += dt
        
        # Different AI behavior for same-direction vs oncoming traffic
        if car.direction == 1:
            # Same direction traffic can change lanes
            if car.ai_state == "cruising":
                # Lane change frequency depends on vehicle type
                lane_change_chance = 0.01 * dt if car.vehicle_type == "truck" else 0.03 * dt  # Trucks change lanes less
                lane_change_cooldown = 8.0 if car.vehicle_type == "truck" else 4.0  # Trucks wait longer
                
                if random.random() < lane_change_chance and car.lane_change_timer > lane_change_cooldown:
                    # Only change within same direction lanes
                    target_lane = None
                    
                    if car.direction == 1:  # Same direction as player - can change between lanes 3 and 4
                        if car.lane == 3:
                            target_lane = 4
                        elif car.lane == 4:
                            target_lane = 3
                    else:  # Oncoming direction - can change between lanes 1 and 2
                        if car.lane == 1:
                            target_lane = 2
                        elif car.lane == 2:
                            target_lane = 1
                        
                    if target_lane is not None and self._is_lane_change_safe(car, target_lane):
                        car.ai_state = "changing_lanes"
                        # Calculate target position using proper directional positioning
                        road_center_normalized = 0.5
                        road_width_normalized = 0.6
                        left_road_edge = road_center_normalized - road_width_normalized / 2
                        direction_width = road_width_normalized / 2
                        lane_width = direction_width / 2
                        
                        if car.direction == 1:  # Same direction (right half)
                            lane_offset = target_lane - 3  # Convert 3,4 to 0,1
                            car.target_x = road_center_normalized + lane_width * (lane_offset + 0.5)
                        else:  # Oncoming direction (left half)
                            lane_offset = target_lane - 1  # Convert 1,2 to 0,1
                            car.target_x = left_road_edge + lane_width * (lane_offset + 0.5)
                            
                        car.lane = target_lane
                        car.lane_change_timer = 0.0
                        
            elif car.ai_state == "changing_lanes":
                # Smoothly move to target lane
                if hasattr(car, 'target_x'):
                    lane_change_speed = 0.8 * dt  # Reduced lane change speed
                    if abs(car.x - car.target_x) < 0.05:
                        car.x = car.target_x
                        car.ai_state = "cruising"
                        delattr(car, 'target_x')
                    else:
                        direction = 1 if car.target_x > car.x else -1
                        car.x += direction * lane_change_speed
        else:
            # Oncoming traffic stays in their lanes (no lane changes)
            car.ai_state = "cruising"
                    
        # Speed variation for realism (less variation for oncoming traffic)
        variation_chance = 0.05 * dt if car.direction == -1 else 0.1 * dt
        if random.random() < variation_chance:
            speed_change = random.uniform(-0.05, 0.05)
            if car.direction == 1:
                car.speed = max(0.2, min(1.2, car.speed + speed_change))
            else:
                car.speed = max(0.4, min(1.0, car.speed + speed_change))
            
    def _is_lane_change_safe(self, car: NPCCar, target_lane: int) -> bool:
        """Check if lane change is safe for NPC car within their directional lanes."""
        # Calculate target position using proper directional positioning
        road_center_normalized = 0.5
        road_width_normalized = 0.6
        left_road_edge = road_center_normalized - road_width_normalized / 2
        direction_width = road_width_normalized / 2
        lane_width = direction_width / 2
        
        if car.direction == 1:  # Same direction (right half)
            if target_lane not in [3, 4]:  # Only allow lanes 3,4 for same direction
                return False
            lane_offset = target_lane - 3  # Convert 3,4 to 0,1
            target_x = road_center_normalized + lane_width * (lane_offset + 0.5)
        else:  # Oncoming direction (left half)
            if target_lane not in [1, 2]:  # Only allow lanes 1,2 for oncoming
                return False
            lane_offset = target_lane - 1  # Convert 1,2 to 0,1
            target_x = left_road_edge + lane_width * (lane_offset + 0.5)
        
        # Ensure target position is within the correct directional boundaries
        if car.direction == 1:
            # Same direction - must stay in left half
            direction_left = left_road_edge + 0.02
            direction_right = road_center_normalized - 0.02
        else:
            # Oncoming direction - must stay in right half
            direction_left = road_center_normalized + 0.02
            direction_right = left_road_edge + road_width_normalized - 0.02
            
        if target_x < direction_left or target_x > direction_right:
            return False  # Target would be outside directional lanes
        
        # Check for collisions with other cars in target lane
        for other_car in self.npc_cars:
            if other_car != car:
                # Check if other car is in or near the target lane
                if other_car.lane == target_lane or abs(other_car.x - target_x) < 0.08:
                    # Car is in target lane, check distance
                    if abs(other_car.y - car.y) < 100:  # Increased safety distance
                        return False
                # Also check if a car is currently changing into the target lane
                if hasattr(other_car, 'target_x') and abs(other_car.target_x - target_x) < 0.08:
                    if abs(other_car.y - car.y) < 120:  # Even more distance for merging cars
                        return False
                    
        # Check distance from player (only for same-direction traffic)
        if car.direction == 1 and abs(target_x - self.player_x) < 0.15 and abs(car.y) < 100:
            return False  # Too close to player
            
        return True
        
    def _get_road_boundaries(self):
        """Get current road boundaries in normalized coordinates."""
        # Use the same road calculation as the drawing code
        road_center_pixels = self.screen_width // 2
        base_width_variation = int(self.width_oscillation)
        surface_variation = int(self.surface_noise)
        current_road_width_pixels = self.road_width + base_width_variation + surface_variation
        
        # Calculate actual road edges in pixels
        road_left_pixels = road_center_pixels - current_road_width_pixels // 2
        road_right_pixels = road_center_pixels + current_road_width_pixels // 2
        
        # Convert to normalized coordinates (0.0-1.0)
        road_left_normalized = road_left_pixels / self.screen_width
        road_right_normalized = road_right_pixels / self.screen_width
        road_width_normalized = road_right_normalized - road_left_normalized
        
        return road_left_normalized, road_right_normalized, road_width_normalized
        
    def _enforce_traffic_boundaries(self, car: NPCCar):
        """Ensure traffic cars stay within their directional lanes and road boundaries."""
        # Get actual road boundaries
        road_left_normalized, road_right_normalized, road_width_normalized = self._get_road_boundaries()
        
        # Split road into two directions
        direction_width = road_width_normalized / 2  # Each direction gets half the road
        lane_width = direction_width / 2  # 2 lanes per direction
        road_center_normalized = road_left_normalized + road_width_normalized / 2
        
        # Define directional boundaries
        car_width_normalized = 0.02  # Approximate car width in normalized coordinates
        
        if car.direction == 1:  # Same direction (right half)
            direction_left = road_center_normalized + car_width_normalized
            direction_right = road_right_normalized - car_width_normalized
        else:  # Oncoming direction (left half)
            direction_left = road_left_normalized + car_width_normalized
            direction_right = road_center_normalized - car_width_normalized
        
        # Enforce directional boundaries - push cars back into their side
        if car.x < direction_left:
            car.x = direction_left
            # If changing lanes, cancel the lane change
            if car.ai_state == "changing_lanes":
                car.ai_state = "cruising"
                if hasattr(car, 'target_x'):
                    delattr(car, 'target_x')
                    
        elif car.x > direction_right:
            car.x = direction_right
            # If changing lanes, cancel the lane change
            if car.ai_state == "changing_lanes":
                car.ai_state = "cruising"
                if hasattr(car, 'target_x'):
                    delattr(car, 'target_x')
                    
        # Keep cars roughly in their designated lanes when not changing
        if car.ai_state == "cruising":
            # Calculate ideal lane position based on direction
            if car.direction == 1:  # Same direction (right half)
                lane_offset = car.lane - 3  # Convert 3,4 to 0,1
                ideal_x = road_center_normalized + lane_width * (lane_offset + 0.5)
            else:  # Oncoming direction (left half)
                lane_offset = car.lane - 1  # Convert 1,2 to 0,1
                ideal_x = road_left_normalized + lane_width * (lane_offset + 0.5)
            
            # Gently guide cars toward their lane center
            lane_drift_correction = 0.5  # Stronger correction for lane discipline
            if abs(car.x - ideal_x) > lane_width * 0.4:  # If drifting too far from lane center
                correction = (ideal_x - car.x) * lane_drift_correction * 0.02  # Correction per frame
                car.x += correction
    
    def _avoid_traffic_collisions(self, car: NPCCar, dt: float):
        """Make traffic cars avoid collisions with each other."""
        # Define safe following distance based on relative speeds
        min_safe_distance = 60  # Minimum distance in pixels
        brake_distance = 120    # Distance at which to start braking
        
        for other_car in self.npc_cars:
            if other_car == car:
                continue
                
            # Check if cars are in same or adjacent lanes
            lane_diff = abs(car.lane - other_car.lane)
            if lane_diff > 1:  # Cars are too far apart laterally
                continue
                
            # Check if cars are in the same direction
            if car.direction != other_car.direction:
                # For oncoming traffic, only check if they're in exact same lane (head-on)
                if car.lane != other_car.lane:
                    continue
                # Head-on collision avoidance - emergency lane change
                if car.y > -50 and car.y < 50 and other_car.y > -50 and other_car.y < 50:
                    # Try to change lanes to avoid head-on collision
                    if car.ai_state == "cruising":
                        emergency_lane = None
                        if car.direction == 1:  # Same as player
                            emergency_lane = 4 if car.lane == 3 else 3
                        else:  # Oncoming
                            emergency_lane = 2 if car.lane == 1 else 1
                        
                        if emergency_lane and self._is_lane_change_safe(car, emergency_lane):
                            car.ai_state = "changing_lanes"
                            car.lane = emergency_lane
                            car.lane_change_timer = 0.0
                continue
            
            # Same direction collision avoidance
            # Check if other car is ahead and too close
            if car.direction == 1:  # Same direction as player
                distance = other_car.y - car.y  # Positive if other car is ahead
            else:  # Oncoming traffic
                distance = car.y - other_car.y  # Positive if other car is ahead
                
            if distance > 0 and distance < brake_distance:
                # Other car is ahead and within braking distance
                if lane_diff == 0:  # Same lane
                    if distance < min_safe_distance:
                        # Emergency brake
                        car.speed = max(0.1, car.speed - 2.0 * dt)
                    else:
                        # Gradual speed matching
                        speed_diff = car.speed - other_car.speed
                        if speed_diff > 0:  # We're going faster
                            brake_force = (1.0 - distance / brake_distance) * speed_diff
                            car.speed = max(other_car.speed * 0.9, car.speed - brake_force * dt)
                    
                    # Try to change lanes if stuck behind for too long
                    if car.ai_state == "cruising" and distance < brake_distance * 0.7:
                        # Increase chance of lane change when following closely
                        if random.random() < 0.02 * dt:  # 2% chance per second
                            # Try to change lanes
                            target_lane = None
                            if car.direction == 1:
                                target_lane = 4 if car.lane == 3 else 3
                            else:
                                target_lane = 2 if car.lane == 1 else 1
                                
                            if target_lane and self._is_lane_change_safe(car, target_lane):
                                car.ai_state = "changing_lanes"
                                # Store target for lane change
                                road_center_normalized = 0.5
                                road_width_normalized = 0.6
                                left_road_edge = road_center_normalized - road_width_normalized / 2
                                direction_width = road_width_normalized / 2
                                lane_width = direction_width / 2
                                
                                if car.direction == 1:  # Same direction (right half)
                                    lane_offset = target_lane - 3
                                    car.target_x = road_center_normalized + lane_width * (lane_offset + 0.5)
                                else:  # Oncoming (left half)
                                    lane_offset = target_lane - 1
                                    car.target_x = left_road_edge + lane_width * (lane_offset + 0.5)
                                
                                car.lane = target_lane
                                car.lane_change_timer = 0.0
    
    def _check_traffic_collisions(self, dt: float):
        """Check for collisions between player and traffic vehicles."""
        # Update collision cooldown and flash timer
        if self.collision_cooldown > 0:
            self.collision_cooldown -= dt
        if self.collision_flash_timer > 0:
            self.collision_flash_timer -= dt
            
        # Recover from collision penalties over time
        if self.collision_speed_penalty > 0:
            recovery = self.collision_recovery_rate * dt
            self.collision_speed_penalty = max(0, self.collision_speed_penalty - recovery)
            
        # Only check collisions if cooldown expired (prevents multiple rapid collisions)
        if self.collision_cooldown > 0:
            return
            
        # Get player collision rectangle in normalized coordinates
        player_collision_width = 0.03  # Smaller collision box (~40px at 1280px width)
        player_collision_height = 0.06  # Smaller height for more forgiving collisions
        player_left = self.player_x - player_collision_width / 2
        player_right = self.player_x + player_collision_width / 2
        player_top = 0.42   # Player Y position (slightly adjusted)
        player_bottom = player_top + player_collision_height
        
        # Check collision with each traffic car
        for car in self.npc_cars:
            # Convert car position to collision rectangle
            car_collision_width = car.collision_zone[0] / self.screen_width  # Convert pixels to normalized
            car_collision_height = car.collision_zone[1] / 200  # Rough conversion for Y-axis
            
            car_left = car.x - car_collision_width / 2
            car_right = car.x + car_collision_width / 2
            
            # Convert car Y position to screen space for collision detection
            # Car Y is distance ahead/behind - convert to screen Y position
            car_screen_y = 0.5 - (car.y / 400)  # Rough conversion
            car_top = car_screen_y - car_collision_height / 2
            car_bottom = car_screen_y + car_collision_height / 2
            
            # Check for rectangle collision
            if (player_right > car_left and player_left < car_right and
                player_bottom > car_top and player_top < car_bottom):
                
                # Collision detected!
                self._handle_collision(car)
                break  # Only handle one collision per frame
                
    def _handle_collision(self, car: NPCCar):
        """Handle collision with a traffic vehicle."""
        # Set collision cooldown to prevent multiple rapid collisions
        self.collision_cooldown = 1.0  # 1 second cooldown
        
        # Different penalties for different vehicle types
        if car.vehicle_type == "truck":
            speed_penalty = 0.4  # 40% speed reduction for truck collision
            self.collision_damage += 0.2  # Trucks cause more damage
            self.last_collision_type = "truck"
        else:  # car
            speed_penalty = 0.2  # 20% speed reduction for car collision
            self.collision_damage += 0.1  # Cars cause less damage
            self.last_collision_type = "car"
            
        # Apply speed penalty
        self.collision_speed_penalty = max(self.collision_speed_penalty, speed_penalty)
        
        # Cap total damage at 1.0
        self.collision_damage = min(1.0, self.collision_damage)
        
        # Visual feedback
        self.collision_flash_timer = 0.3  # Flash screen for 300ms
        
        # Audio feedback (if sound manager available)
        if hasattr(self.scene_manager, 'sound_manager') and self.scene_manager.sound_manager:
            try:
                if car.vehicle_type == "truck":
                    # Play heavy collision sound for trucks
                    self.scene_manager.sound_manager.play_sfx("crash_heavy")
                else:
                    # Play light collision sound for cars  
                    self.scene_manager.sound_manager.play_sfx("crash_light")
            except:
                pass  # Sound files might not exist yet
                
        # Push car away slightly to prevent stuck collisions
        if car.direction == 1:  # Same direction traffic
            car.y += 50  # Push car ahead
        else:  # Oncoming traffic
            car.y -= 50  # Push car back
    
    def _update_hazards(self, dt: float):
        """Update static hazard system with construction zones."""
        # Update construction zone spawn timer
        self.construction_spawn_timer += dt
        
        # Spawn new construction zones periodically
        if self.construction_spawn_timer > 8.0 and len(self.construction_zones) < 2:
            self._spawn_construction_zone()
            self.construction_spawn_timer = 0.0
        
        # Update hazard positions relative to player
        hazards_to_remove = []
        for i, hazard in enumerate(self.hazards):
            # Move hazards relative to player speed
            hazard.y -= self.player_speed * dt * 100
            
            # Remove hazards that are too far behind
            if hazard.y < -300:
                hazards_to_remove.append(i)
        
        # Remove old hazards
        for i in reversed(hazards_to_remove):
            del self.hazards[i]
            
        # Update construction zones
        zones_to_remove = []
        for i, (start_y, end_y) in enumerate(self.construction_zones):
            # Move zones with player
            self.construction_zones[i] = (
                start_y - self.player_speed * dt * 100,
                end_y - self.player_speed * dt * 100
            )
            # Remove zones that have passed
            if self.construction_zones[i][1] < -300:
                zones_to_remove.append(i)
                
        for i in reversed(zones_to_remove):
            del self.construction_zones[i]
    
    def _spawn_construction_zone(self):
        """Spawn a construction zone with cones and barriers."""
        # Determine zone length and lanes affected
        zone_length = random.randint(200, 400)
        start_y = self.next_construction_y
        end_y = start_y + zone_length
        
        # Choose which lanes to block (1-2 lanes)
        num_lanes_blocked = random.choice([1, 2])
        if num_lanes_blocked == 1:
            # Block one lane
            blocked_lane = random.choice([1, 2, 3, 4])
            lanes_to_block = [blocked_lane]
        else:
            # Block two adjacent lanes
            if random.random() < 0.5:
                # Block player direction lanes
                lanes_to_block = random.choice([[3, 4]])
            else:
                # Block oncoming lanes
                lanes_to_block = random.choice([[1, 2]])
        
        # Add construction zone
        self.construction_zones.append((start_y, end_y))
        
        # Spawn warning sign before zone
        warning_y = start_y - 100
        self._spawn_hazard("warning_sign", 0.5, warning_y, 0)  # Center of road
        
        # Spawn cones at start and end of blocked lanes
        for lane in lanes_to_block:
            # Get lane position
            lane_x = self._get_lane_x_position(lane)
            
            # Cones at intervals
            for y in range(int(start_y), int(end_y), 40):
                self._spawn_hazard("cone", lane_x, y, lane)
                
            # Barriers for longer blockages
            if zone_length > 300:
                barrier_y = start_y + zone_length // 2
                self._spawn_hazard("barrier", lane_x, barrier_y, lane)
        
        # Update next construction zone position
        self.next_construction_y = end_y + random.randint(400, 800)
    
    def _spawn_hazard(self, hazard_type: str, x: float, y: float, lane: int):
        """Spawn a single hazard at the specified position."""
        if hazard_type == "cone":
            hazard = Hazard(
                x=x,
                y=y,
                lane=lane,
                hazard_type="cone",
                width=16,
                height=24,
                collision_zone=(16, 24),
                color=(255, 140, 0)  # Orange
            )
        elif hazard_type == "barrier":
            hazard = Hazard(
                x=x,
                y=y,
                lane=lane,
                hazard_type="barrier",
                width=48,
                height=32,
                collision_zone=(48, 32),
                color=(128, 128, 128)  # Gray
            )
        elif hazard_type == "warning_sign":
            hazard = Hazard(
                x=x,
                y=y,
                lane=lane,
                hazard_type="warning_sign",
                width=32,
                height=32,
                collision_zone=(0, 0),  # No collision for signs
                color=(255, 255, 0)  # Yellow
            )
        
        self.hazards.append(hazard)
    
    def _spawn_dynamic_hazard(self, hazard_type: str, x: float, y: float, source: str = None):
        """Spawn a dynamic hazard like oil slick or debris."""
        if hazard_type == "oil_slick":
            hazard = Hazard(
                x=x,
                y=y,
                lane=-1,  # Not lane-specific
                hazard_type="oil_slick",
                width=64,
                height=32,
                collision_zone=(60, 28),
                color=(32, 32, 48),  # Dark with blue tint
                is_dynamic=True,
                effect_type="slip",
                effect_duration=1.5,
                effect_strength=0.3,  # 70% steering reduction
                spawn_source=source
            )
        elif hazard_type == "debris":
            # Random debris types
            debris_types = ["tire", "metal", "cargo"]
            debris_choice = random.choice(debris_types)
            
            hazard = Hazard(
                x=x,
                y=y,
                lane=-1,
                hazard_type=f"debris_{debris_choice}",
                width=random.randint(16, 32),
                height=random.randint(16, 32),
                collision_zone=(24, 24),
                color=(64, 48, 32),  # Dark brown
                is_dynamic=True,
                effect_type="damage",
                effect_duration=0.0,  # Instant
                effect_strength=0.15,  # 15% speed reduction
                spawn_source=source
            )
        elif hazard_type == "water_puddle":
            hazard = Hazard(
                x=x,
                y=y,
                lane=-1,
                hazard_type="water_puddle",
                width=48,
                height=24,
                collision_zone=(44, 20),
                color=(64, 128, 192),  # Light blue
                is_dynamic=True,
                effect_type="slip",
                effect_duration=0.8,
                effect_strength=0.7,  # 30% steering reduction
                spawn_source="weather"
            )
        
        self.hazards.append(hazard)
    
    def _update_dynamic_hazard_spawning(self, dt: float):
        """Update spawning of dynamic hazards based on traffic and conditions."""
        # Oil slicks from trucks
        for npc in self.npc_cars:
            if npc.vehicle_type == "truck" and npc.y > 0 and random.random() < 0.003:  # Moderate spawn rate
                # Spawn oil slick behind truck
                oil_x = npc.x + random.uniform(-0.02, 0.02)
                oil_y = npc.y - 50
                self._spawn_dynamic_hazard("oil_slick", oil_x, oil_y, "truck")
        
        # Random debris spawning
        if random.random() < 0.002:  # Moderate spawn rate
            debris_x = random.uniform(0.2, 0.8)
            debris_y = self.horizon_y + 500
            self._spawn_dynamic_hazard("debris", debris_x, debris_y, "random")
        
        # Water puddles (if we add weather later)
        # Currently disabled - could be enabled with weather system
    
    def _update_hazard_effects(self, dt: float):
        """Update active hazard effects on the player."""
        # Reset slip factor
        self.slip_factor = 1.0
        has_slip_effect = False
        
        # Update active effects
        effects_to_remove = []
        for i, effect in enumerate(self.active_effects):
            # Decrease timer
            effect["timer"] -= dt
            
            # Apply effect
            if effect["type"] == "slip":
                # Reduce steering control (multiplicative for multiple effects)
                self.slip_factor *= effect["strength"]
                has_slip_effect = True
            
            # Remove expired effects
            if effect["timer"] <= 0:
                effects_to_remove.append(i)
        
        # Remove expired effects
        for i in reversed(effects_to_remove):
            self.active_effects.pop(i)
        
        # Update slip spin animation
        if has_slip_effect:
            # Spin the car during slip effect
            self.slip_spin_angle += self.slip_spin_speed * dt
            if self.slip_spin_angle >= 360:
                self.slip_spin_angle -= 360
        else:
            # Smoothly return to normal rotation
            if self.slip_spin_angle > 0:
                return_speed = 1080 * dt  # Faster return to normal
                self.slip_spin_angle = max(0, self.slip_spin_angle - return_speed)
        
        # Update visual timer
        if self.effect_visual_timer > 0:
            self.effect_visual_timer -= dt
    
    def _update_comic_text(self, dt: float):
        """Update comic text taunt system."""
        # Update timer for next taunt
        if self.current_comic_text is None:
            self.comic_text_timer -= dt
            
            # Time to show a new taunt
            if self.comic_text_timer <= 0:
                # Pick a random taunt
                self.current_comic_text = random.choice(self.comic_taunts)
                self.comic_text_fade_timer = self.comic_text_duration
                # Reset timer for next taunt
                self.comic_text_timer = random.uniform(10.0, 15.0)
        else:
            # Update fade timer for current text
            self.comic_text_fade_timer -= dt
            
            # Remove text when timer expires
            if self.comic_text_fade_timer <= 0:
                self.current_comic_text = None
    
    def _get_lane_x_position(self, lane: int) -> float:
        """Get the normalized X position for a given lane."""
        # Get current road boundaries
        road_left, road_right, road_width = self._get_road_boundaries()
        
        # Calculate lane positions
        direction_width = road_width / 2
        lane_width = direction_width / 2
        road_center = road_left + road_width / 2
        
        if lane in [1, 2]:  # Oncoming lanes (left side)
            lane_offset = lane - 1  # Convert to 0, 1
            return road_left + lane_width * (lane_offset + 0.5)
        else:  # Player direction lanes (right side)
            lane_offset = lane - 3  # Convert to 0, 1
            return road_center + lane_width * (lane_offset + 0.5)
    
    def _check_hazard_collisions(self, dt: float):
        """Check for collisions between player and static hazards."""
        # Skip if in collision cooldown
        if self.collision_cooldown > 0:
            return
            
        # Get player collision rectangle
        player_collision_width = 0.03  # Smaller collision box
        player_collision_height = 0.06  # Smaller height
        player_left = self.player_x - player_collision_width / 2
        player_right = self.player_x + player_collision_width / 2
        player_top = 0.42
        player_bottom = player_top + player_collision_height
        
        # Check collision with each hazard
        for hazard in self.hazards:
            # Skip warning signs (no collision)
            if hazard.hazard_type == "warning_sign":
                continue
                
            # Convert hazard position to collision rectangle
            hazard_collision_width = hazard.collision_zone[0] / self.screen_width
            hazard_collision_height = hazard.collision_zone[1] / 200
            
            hazard_left = hazard.x - hazard_collision_width / 2
            hazard_right = hazard.x + hazard_collision_width / 2
            
            # Convert hazard Y position to screen space
            hazard_screen_y = 0.5 - (hazard.y / 400)
            hazard_top = hazard_screen_y - hazard_collision_height / 2
            hazard_bottom = hazard_screen_y + hazard_collision_height / 2
            
            # Check for collision
            if (player_right > hazard_left and player_left < hazard_right and
                player_bottom > hazard_top and player_top < hazard_bottom):
                
                # Handle collision based on hazard type
                self._handle_hazard_collision(hazard)
                break
    
    def _handle_hazard_collision(self, hazard: Hazard):
        """Handle collision with hazards (static or dynamic)."""
        # Handle dynamic hazards differently
        if hazard.is_dynamic:
            # Apply effect based on type
            if hazard.effect_type == "slip":
                # Add slip effect
                self.active_effects.append({
                    "type": "slip",
                    "duration": hazard.effect_duration,
                    "strength": hazard.effect_strength,
                    "timer": hazard.effect_duration
                })
                self.effect_visual_timer = hazard.effect_duration
                self.last_collision_type = f"slippery_{hazard.hazard_type}"
                
            elif hazard.effect_type == "damage":
                # Instant damage and speed reduction
                self.collision_damage += hazard.effect_strength
                self.player_speed *= (1.0 - hazard.effect_strength)
                self.collision_flash_timer = 0.3
                self.last_collision_type = hazard.hazard_type
                
            # Remove dynamic hazards after collision (they're consumed)
            if hazard in self.hazards:
                self.hazards.remove(hazard)
                
        else:
            # Static hazard handling (existing code)
            # Set collision cooldown
            self.collision_cooldown = 0.5  # Shorter cooldown for hazards
            
            # Different penalties for different hazards
            if hazard.hazard_type == "cone":
                speed_penalty = 0.1  # 10% speed reduction
                self.collision_damage += 0.05  # Minor damage
                self.last_collision_type = "cone"
            elif hazard.hazard_type == "barrier":
                speed_penalty = 0.3  # 30% speed reduction
                self.collision_damage += 0.15  # Significant damage
                self.last_collision_type = "barrier"
                
            # Apply speed penalty
            self.collision_speed_penalty = max(self.collision_speed_penalty, speed_penalty)
            
            # Cap damage
            self.collision_damage = min(1.0, self.collision_damage)
            
            # Visual feedback
            self.collision_flash_timer = 0.2  # Shorter flash for hazards
        
        # Audio feedback
        if hasattr(self.scene_manager, 'sound_manager') and self.scene_manager.sound_manager:
            try:
                if hazard.hazard_type == "cone":
                    self.scene_manager.sound_manager.play_sfx("cone_hit")
                else:
                    self.scene_manager.sound_manager.play_sfx("barrier_hit")
            except:
                pass
                
        # Remove cone after hit (barriers stay)
        if hazard.hazard_type == "cone":
            self.hazards.remove(hazard)
        
    def draw(self, screen):
        """Draw the game."""
        if self.state == self.STATE_MUSIC_SELECT:
            self._draw_road_background(screen)  # Show road in background
            self.music_selector.draw(screen)
            
        elif self.state == self.STATE_VEHICLE_SELECT:
            self._draw_road_background(screen)  # Show road in background
            self.vehicle_selector.draw(screen)
            
        elif self.state == self.STATE_READY:
            self._draw_road_background(screen)
            self._draw_ready_screen(screen)
            
        elif self.state == self.STATE_RACING:
            self._draw_racing_scene(screen)
            
        elif self.state == self.STATE_GAME_OVER:
            self._draw_racing_scene(screen)  # Show final race state
            self._draw_game_over_screen(screen)
            
    def _draw_road_background(self, screen):
        """Draw a simple road background."""
        # Sky gradient
        for y in range(self.horizon_y):
            color_intensity = int(135 + (100 * y / self.horizon_y))
            color_intensity = min(255, color_intensity)  # Clamp to valid range
            green = min(255, color_intensity + 50)
            color = (color_intensity, green, 255)
            pygame.draw.line(screen, color, (0, y), (self.screen_width, y))
            
        # Ground
        ground_rect = pygame.Rect(0, self.horizon_y, self.screen_width, 
                                 self.screen_height - self.horizon_y)
        screen.fill((34, 139, 34), ground_rect)  # Forest green
        
        # Enhanced road with natural variation
        road_center = self.screen_width // 2 + int(self.road_curve * 100)  # Doubled curve effect for visibility
        
        # Apply multiple layers of variation for realistic road
        base_width_variation = int(self.width_oscillation)  # Primary width changes
        surface_variation = int(self.surface_noise)  # Micro road texture
        current_width = self.road_width + base_width_variation + surface_variation
        
        road_rect = pygame.Rect(
            road_center - current_width // 2,
            self.horizon_y,
            current_width,
            self.screen_height - self.horizon_y
        )
        screen.fill((60, 60, 60), road_rect)
        
        # Enhanced road lines with speed effects for 4-lane traffic
        line_color = COLOR_YELLOW
        center_line_x = road_center  # Already calculated with curve offset above
        
        # Apply speed shimmer to road lines for visual feedback
        shimmer_offset = int(self.speed_shimmer)
        
        # Draw center divider line (solid white line to separate traffic directions)
        center_divider_color = COLOR_WHITE
        for y in range(self.horizon_y, self.screen_height, 10):
            line_y = y + int((self.road_position * 30) % 20) - 10
            if self.horizon_y <= line_y < self.screen_height:
                pygame.draw.line(screen, center_divider_color,
                               (center_line_x - 1, line_y),
                               (center_line_x + 1, line_y + 8), 3)
        
        # Draw lane markings (dashed yellow lines for lane changes)
        for y in range(self.horizon_y, self.screen_height, 30):
            line_y = y + int((self.road_position * 50) % 60) - 30
            if self.horizon_y <= line_y < self.screen_height:
                # Add subtle horizontal shimmer based on speed
                line_x_offset = shimmer_offset if (y // 30) % 2 == 0 else -shimmer_offset // 2
                
                # Left lane divider (between lanes 0 and 1 - player direction)
                left_lane_x = center_line_x - current_width // 4 + line_x_offset
                pygame.draw.line(screen, line_color,
                               (left_lane_x - 1, line_y),
                               (left_lane_x + 1, line_y + 10), 2)
                               
                # Right lane divider (between lanes 2 and 3 - oncoming direction)  
                right_lane_x = center_line_x + current_width // 4 + line_x_offset
                pygame.draw.line(screen, line_color,
                               (right_lane_x - 1, line_y),
                               (right_lane_x + 1, line_y + 10), 2)
        
        # Draw road edge markers for EV boundary visualization
        self._draw_road_edges(screen, road_center, current_width)
                               
    def _draw_road_edges(self, screen, road_center: int, road_width: int):
        """Draw road edge markers to show EV boundaries."""
        # Calculate edge positions
        left_edge = road_center - road_width // 2
        right_edge = road_center + road_width // 2
        
        edge_color = COLOR_WHITE
        warning_color = COLOR_RED
        
        # Determine if player is near edges (for warning colors)
        player_pixel_x = int(self.player_x * self.screen_width)
        near_left_edge = abs(player_pixel_x - left_edge) < 40
        near_right_edge = abs(player_pixel_x - right_edge) < 40
        
        # Draw left edge markers
        left_color = warning_color if near_left_edge else edge_color
        for y in range(self.horizon_y, self.screen_height, 30):
            line_y = y + int((self.road_position * 30) % 60) - 30
            if self.horizon_y <= line_y < self.screen_height:
                pygame.draw.line(screen, left_color,
                               (left_edge - 1, line_y),
                               (left_edge - 1, line_y + 15), 3)
        
        # Draw right edge markers
        right_color = warning_color if near_right_edge else edge_color
        for y in range(self.horizon_y, self.screen_height, 30):
            line_y = y + int((self.road_position * 30) % 60) - 30
            if self.horizon_y <= line_y < self.screen_height:
                pygame.draw.line(screen, right_color,
                               (right_edge + 1, line_y),
                               (right_edge + 1, line_y + 15), 3)
    
    def _draw_hazards(self, screen):
        """Draw all hazards (static and dynamic)."""
        for hazard in self.hazards:
            # Convert hazard position to screen coordinates
            hazard_screen_x = int(hazard.x * self.screen_width)
            hazard_screen_y = int(self.screen_height - 100 - hazard.y)
            
            # Only draw if visible on screen
            if -50 <= hazard_screen_y <= self.screen_height + 50:
                if hazard.hazard_type == "cone":
                    # Draw traffic cone (triangle shape)
                    cone_points = [
                        (hazard_screen_x, hazard_screen_y - hazard.height // 2),  # Top
                        (hazard_screen_x - hazard.width // 2, hazard_screen_y + hazard.height // 2),  # Bottom left
                        (hazard_screen_x + hazard.width // 2, hazard_screen_y + hazard.height // 2)   # Bottom right
                    ]
                    pygame.draw.polygon(screen, hazard.color, cone_points)
                    # Add white stripe
                    stripe_y = hazard_screen_y - hazard.height // 4
                    pygame.draw.line(screen, COLOR_WHITE,
                                   (hazard_screen_x - hazard.width // 3, stripe_y),
                                   (hazard_screen_x + hazard.width // 3, stripe_y), 2)
                    
                elif hazard.hazard_type == "barrier":
                    # Draw concrete barrier (rectangle)
                    barrier_rect = pygame.Rect(
                        hazard_screen_x - hazard.width // 2,
                        hazard_screen_y - hazard.height // 2,
                        hazard.width,
                        hazard.height
                    )
                    pygame.draw.rect(screen, hazard.color, barrier_rect)
                    # Add warning stripes
                    stripe_width = hazard.width // 4
                    for i in range(0, hazard.width, stripe_width * 2):
                        stripe_rect = pygame.Rect(
                            barrier_rect.x + i,
                            barrier_rect.y,
                            stripe_width,
                            barrier_rect.height
                        )
                        pygame.draw.rect(screen, COLOR_YELLOW, stripe_rect)
                    # Outline
                    pygame.draw.rect(screen, COLOR_BLACK, barrier_rect, 2)
                    
                elif hazard.hazard_type == "warning_sign":
                    # Draw warning sign (diamond shape)
                    sign_points = [
                        (hazard_screen_x, hazard_screen_y - hazard.height // 2),  # Top
                        (hazard_screen_x + hazard.width // 2, hazard_screen_y),   # Right
                        (hazard_screen_x, hazard_screen_y + hazard.height // 2),  # Bottom
                        (hazard_screen_x - hazard.width // 2, hazard_screen_y)    # Left
                    ]
                    pygame.draw.polygon(screen, hazard.color, sign_points)
                    pygame.draw.polygon(screen, COLOR_BLACK, sign_points, 2)
                    # Add exclamation mark
                    font = pygame.font.Font(None, 20)
                    text = font.render("!", True, COLOR_BLACK)
                    text_rect = text.get_rect(center=(hazard_screen_x, hazard_screen_y))
                    screen.blit(text, text_rect)
                    
                elif hazard.hazard_type == "oil_slick":
                    # Draw oil slick (elongated ellipse with glossy effect)
                    oil_rect = pygame.Rect(
                        hazard_screen_x - hazard.width // 2,
                        hazard_screen_y - hazard.height // 2,
                        hazard.width,
                        hazard.height
                    )
                    # Dark base
                    pygame.draw.ellipse(screen, hazard.color, oil_rect)
                    # Rainbow sheen effect
                    sheen_rect = oil_rect.inflate(-10, -6)
                    pygame.draw.ellipse(screen, (48, 48, 80), sheen_rect, 2)
                    # Glossy highlight
                    highlight_rect = pygame.Rect(
                        oil_rect.x + oil_rect.width // 4,
                        oil_rect.y + 4,
                        oil_rect.width // 3,
                        6
                    )
                    pygame.draw.ellipse(screen, (64, 64, 128), highlight_rect)
                    
                elif hazard.hazard_type.startswith("debris_"):
                    # Draw debris (irregular shapes)
                    debris_type = hazard.hazard_type.split("_")[1]
                    if debris_type == "tire":
                        # Draw tire chunk
                        pygame.draw.circle(screen, hazard.color, 
                                         (hazard_screen_x, hazard_screen_y), 
                                         hazard.width // 2, 3)
                        pygame.draw.circle(screen, (32, 32, 32), 
                                         (hazard_screen_x, hazard_screen_y), 
                                         hazard.width // 3)
                    else:
                        # Draw generic debris
                        debris_points = [
                            (hazard_screen_x - hazard.width // 2, hazard_screen_y),
                            (hazard_screen_x - hazard.width // 3, hazard_screen_y - hazard.height // 2),
                            (hazard_screen_x + hazard.width // 3, hazard_screen_y - hazard.height // 3),
                            (hazard_screen_x + hazard.width // 2, hazard_screen_y + hazard.height // 3),
                            (hazard_screen_x, hazard_screen_y + hazard.height // 2)
                        ]
                        pygame.draw.polygon(screen, hazard.color, debris_points)
                    
                elif hazard.hazard_type == "water_puddle":
                    # Draw water puddle
                    puddle_rect = pygame.Rect(
                        hazard_screen_x - hazard.width // 2,
                        hazard_screen_y - hazard.height // 2,
                        hazard.width,
                        hazard.height
                    )
                    pygame.draw.ellipse(screen, hazard.color, puddle_rect)
                    # Reflection effect
                    pygame.draw.ellipse(screen, (96, 160, 224), puddle_rect, 2)
    
    def _draw_npc_cars(self, screen):
        """Draw NPC traffic cars with proper directional orientation."""
        for car in self.npc_cars:
            # Convert car position to screen coordinates
            car_screen_x = int(car.x * self.screen_width)
            car_screen_y = int(self.screen_height - 100 - car.y)  # Player car is at screen_height - 100
            
            # Only draw if vehicle is visible on screen
            if -50 <= car_screen_y <= self.screen_height + 50:
                # Draw vehicle rectangle based on type
                car_rect = pygame.Rect(
                    car_screen_x - car.width // 2,
                    car_screen_y - car.height // 2,
                    car.width,
                    car.height
                )
                
                # Draw main vehicle body
                pygame.draw.rect(screen, car.color, car_rect)
                
                # Add truck-specific details
                if car.vehicle_type == "truck":
                    # Draw truck cab (front section)
                    cab_height = car.height // 3
                    cab_rect = pygame.Rect(
                        car_rect.x,
                        car_rect.y,
                        car_rect.width,
                        cab_height
                    )
                    cab_color = tuple(max(0, c - 30) for c in car.color)  # Darker cab
                    pygame.draw.rect(screen, cab_color, cab_rect)
                    
                    # Draw trailer separation line
                    sep_y = car_rect.y + cab_height
                    pygame.draw.line(screen, (0, 0, 0), 
                                   (car_rect.x, sep_y), 
                                   (car_rect.x + car_rect.width, sep_y), 2)
                
                # Add simple details
                # Car outline
                pygame.draw.rect(screen, (0, 0, 0), car_rect, 2)
                
                # Windshield position depends on direction
                windshield_color = tuple(min(255, c + 50) for c in car.color)
                
                if car.direction == 1:
                    # Same direction as player - windshield at front (top)
                    windshield_rect = pygame.Rect(
                        car_rect.x + 4,
                        car_rect.y + 4,
                        car_rect.width - 8,
                        car_rect.height // 3
                    )
                else:
                    # Oncoming traffic - windshield at front (bottom) since they're coming toward us
                    windshield_rect = pygame.Rect(
                        car_rect.x + 4,
                        car_rect.y + car_rect.height * 2 // 3 - 4,
                        car_rect.width - 8,
                        car_rect.height // 3
                    )
                    
                pygame.draw.rect(screen, windshield_color, windshield_rect)
                
                # Headlights/taillights to show direction
                if car.direction == 1:
                    # Same direction - white headlights at front (top), red taillights at back (bottom)
                    # Headlights
                    pygame.draw.circle(screen, (255, 255, 200), 
                                     (car_rect.x + 8, car_rect.y + 5), 3)
                    pygame.draw.circle(screen, (255, 255, 200), 
                                     (car_rect.x + car_rect.width - 8, car_rect.y + 5), 3)
                    # Taillights
                    pygame.draw.circle(screen, (200, 0, 0), 
                                     (car_rect.x + 8, car_rect.y + car_rect.height - 5), 2)
                    pygame.draw.circle(screen, (200, 0, 0), 
                                     (car_rect.x + car_rect.width - 8, car_rect.y + car_rect.height - 5), 2)
                else:
                    # Oncoming traffic - white headlights at front (bottom), red taillights at back (top)
                    # Headlights (at bottom since they're coming toward us)
                    pygame.draw.circle(screen, (255, 255, 200), 
                                     (car_rect.x + 8, car_rect.y + car_rect.height - 5), 4)
                    pygame.draw.circle(screen, (255, 255, 200), 
                                     (car_rect.x + car_rect.width - 8, car_rect.y + car_rect.height - 5), 4)
                    # Taillights (at top)
                    pygame.draw.circle(screen, (200, 0, 0), 
                                     (car_rect.x + 8, car_rect.y + 5), 2)
                    pygame.draw.circle(screen, (200, 0, 0), 
                                     (car_rect.x + car_rect.width - 8, car_rect.y + 5), 2)
                
                # Wheels (simple black rectangles)
                wheel_width = 4
                wheel_height = 8
                
                # Left wheels
                left_front_wheel = pygame.Rect(
                    car_rect.x - 2,
                    car_rect.y + 6,
                    wheel_width,
                    wheel_height
                )
                left_rear_wheel = pygame.Rect(
                    car_rect.x - 2,
                    car_rect.y + car_rect.height - wheel_height - 6,
                    wheel_width,
                    wheel_height
                )
                
                # Right wheels
                right_front_wheel = pygame.Rect(
                    car_rect.x + car_rect.width - 2,
                    car_rect.y + 6,
                    wheel_width,
                    wheel_height
                )
                right_rear_wheel = pygame.Rect(
                    car_rect.x + car_rect.width - 2,
                    car_rect.y + car_rect.height - wheel_height - 6,
                    wheel_width,
                    wheel_height
                )
                
                # Draw all wheels
                for wheel in [left_front_wheel, left_rear_wheel, right_front_wheel, right_rear_wheel]:
                    pygame.draw.rect(screen, (0, 0, 0), wheel)
                               
    def _draw_racing_scene(self, screen):
        """Draw the main racing scene."""
        self._draw_road_background(screen)
        
        # Draw static hazards (cones, barriers, signs)
        self._draw_hazards(screen)
        
        # Draw NPC traffic cars
        self._draw_npc_cars(screen)
        
        # Draw player car with sprite
        car_x = int(self.player_x * self.screen_width)
        car_y = self.screen_height - 100
        
        if self.car_sprite:
            # Scale and position sprite
            scaled_sprite = pygame.transform.scale(
                self.car_sprite,
                (self.car_width, self.car_height)
            )
            
            # Apply rotation for turn physics and slip spin
            total_rotation = self.car_rotation + self.slip_spin_angle
            if abs(total_rotation) > 0.1:  # Only rotate if meaningful angle
                rotated_sprite = pygame.transform.rotate(scaled_sprite, -total_rotation)  # Negative for correct direction
            else:
                rotated_sprite = scaled_sprite
            
            # Apply visual effects
            if self.race_state.is_crash:
                # Flash white during crash
                white_surface = rotated_sprite.copy()
                white_surface.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                rotated_sprite = white_surface
            elif self.race_state.is_boost:
                # Add yellow glow during boost
                glow_surface = rotated_sprite.copy()
                glow_surface.fill((255, 255, 0, 64), special_flags=pygame.BLEND_RGBA_ADD)
                rotated_sprite = glow_surface
            
            car_rect = rotated_sprite.get_rect(center=(car_x, car_y))
            screen.blit(rotated_sprite, car_rect)
        else:
            # Fallback to rectangle if no sprite
            car_rect = pygame.Rect(
                car_x - self.car_width // 2,
                car_y - self.car_height // 2,
                self.car_width,
                self.car_height
            )
            car_color = COLOR_RED
            if self.race_state.is_boost:
                car_color = COLOR_YELLOW
            elif self.race_state.is_crash:
                car_color = COLOR_WHITE
            pygame.draw.rect(screen, car_color, car_rect)
            pygame.draw.rect(screen, COLOR_BLACK, car_rect, 2)
        
        # Draw UI
        self._draw_racing_ui(screen)
        
    def _draw_racing_ui(self, screen):
        """Draw racing UI elements."""
        # Speed indicator
        speed_text = f"Speed: {int(self.player_speed * 100)}%"
        speed_surface = self.font_large.render(speed_text, True, COLOR_WHITE)
        screen.blit(speed_surface, (20, 20))
        
        # Position
        position_text = f"Position: {self.race_state.position}/{self.race_state.total_racers}"
        position_surface = self.font_large.render(position_text, True, COLOR_WHITE)
        screen.blit(position_surface, (20, 60))
        
        # Timer
        timer_text = f"Time: {int(self.time_remaining)}"
        draw_text_with_background(
            screen, timer_text, self.font_large,
            (self.screen_width // 2, 30),
            COLOR_WHITE, COLOR_BLACK, COLOR_WHITE
        )
        
        # Score
        score_text = f"Score: {self.score}"
        score_surface = self.font_small.render(score_text, True, COLOR_WHITE)
        screen.blit(score_surface, (20, 100))
        
        # Current track info
        if self.selected_track:
            track_text = f"♪ {self.selected_track.display_name}"
            track_surface = self.font_small.render(track_text, True, COLOR_GREEN)
            track_rect = track_surface.get_rect(right=self.screen_width - 20, top=20)
            screen.blit(track_surface, track_rect)
            
        # Status indicators
        if self.race_state.is_boost:
            boost_text = self.font_large.render("BOOST!", True, COLOR_YELLOW)
            boost_rect = boost_text.get_rect(center=(self.screen_width // 2, 100))
            screen.blit(boost_text, boost_rect)
            
        if self.race_state.is_final_lap:
            final_text = self.font_large.render("FINAL LAP!", True, COLOR_RED)
            final_rect = final_text.get_rect(center=(self.screen_width // 2, 140))
            screen.blit(final_text, final_rect)
            
        # Hazard effect indicators
        if self.active_effects:
            effect_y = self.screen_height - 100
            for effect in self.active_effects:
                if effect["type"] == "slip":
                    # Draw slippery warning
                    slip_text = f"SLIPPERY! ({int(effect['timer'])}s)"
                    slip_surface = self.font_large.render(slip_text, True, COLOR_YELLOW)
                    slip_rect = slip_surface.get_rect(center=(self.screen_width // 2, effect_y))
                    # Draw background
                    bg_rect = slip_rect.inflate(20, 10)
                    pygame.draw.rect(screen, (32, 32, 48), bg_rect)
                    pygame.draw.rect(screen, COLOR_YELLOW, bg_rect, 3)
                    screen.blit(slip_surface, slip_rect)
                    
                    # Visual effect - slightly wavy screen edges
                    if self.effect_visual_timer > 0:
                        wave_amount = int(10 * math.sin(self.effect_visual_timer * 20))
                        pygame.draw.rect(screen, (64, 64, 128), 
                                       (0, 0, wave_amount, self.screen_height))
                        pygame.draw.rect(screen, (64, 64, 128), 
                                       (self.screen_width - wave_amount, 0, wave_amount, self.screen_height))
                    effect_y -= 60
        
        # Draw comic text bubble
        if self.current_comic_text:
            # Calculate fade alpha
            fade_alpha = min(255, int(255 * min(1.0, self.comic_text_fade_timer)))
            
            # Position near the car
            car_screen_x = int(self.player_x * self.screen_width)
            bubble_x = car_screen_x + 50
            bubble_y = self.screen_height - 200
            
            # Measure text for bubble size
            text_surface = self.font_large.render(self.current_comic_text, True, COLOR_BLACK)
            text_rect = text_surface.get_rect()
            
            # Create bubble background
            bubble_padding = 20
            bubble_rect = text_rect.inflate(bubble_padding * 2, bubble_padding)
            bubble_rect.center = (bubble_x, bubble_y)
            
            # Draw comic bubble with transparency
            bubble_surface = pygame.Surface((bubble_rect.width, bubble_rect.height), pygame.SRCALPHA)
            
            # White bubble with black border
            pygame.draw.rect(bubble_surface, (255, 255, 255, fade_alpha), 
                           (0, 0, bubble_rect.width, bubble_rect.height), 
                           border_radius=15)
            pygame.draw.rect(bubble_surface, (0, 0, 0, fade_alpha), 
                           (0, 0, bubble_rect.width, bubble_rect.height), 
                           width=3, border_radius=15)
            
            # Draw bubble tail pointing to car
            tail_points = [
                (bubble_rect.width // 2 - 10, bubble_rect.height - 2),
                (bubble_rect.width // 2 + 10, bubble_rect.height - 2),
                (bubble_rect.width // 2 - 20, bubble_rect.height + 20)
            ]
            pygame.draw.polygon(bubble_surface, (255, 255, 255, fade_alpha), tail_points)
            pygame.draw.lines(bubble_surface, (0, 0, 0, fade_alpha), False, 
                            [(tail_points[0][0] - 1, tail_points[0][1]),
                             (tail_points[2][0] - 1, tail_points[2][1]),
                             (tail_points[1][0] + 1, tail_points[1][1])], 3)
            
            # Blit bubble to screen
            screen.blit(bubble_surface, bubble_rect)
            
            # Draw text with fade
            text_surface.set_alpha(fade_alpha)
            text_rect.center = bubble_rect.center
            screen.blit(text_surface, text_rect)
        
        # Control hints
        control_text = "Press Q to return to Hub"
        control_surface = self.font_small.render(control_text, True, COLOR_YELLOW)
        control_rect = control_surface.get_rect(bottomleft=(20, self.screen_height - 20))
        screen.blit(control_surface, control_rect)
        
        # Turn indicators for enhanced racing experience
        if self.turn_state != "straight":
            turn_direction = self.turn_state.replace("turning_", "").upper()
            turn_text = f"{turn_direction} TURN - {int(self.turn_progress * 100)}%"
            turn_surface = self.font_small.render(turn_text, True, COLOR_WHITE)
            turn_rect = turn_surface.get_rect(right=self.screen_width - 20, top=60)
            screen.blit(turn_surface, turn_rect)
            
            # Turn intensity indicator
            intensity_text = f"Intensity: {int(self.turn_intensity * 100)}%"
            intensity_surface = self.font_small.render(intensity_text, True, COLOR_WHITE)
            intensity_rect = intensity_surface.get_rect(right=self.screen_width - 20, top=80)
            screen.blit(intensity_surface, intensity_rect)
            
            # Car rotation indicator (for debugging/feedback)
            rotation_text = f"Rotation: {self.car_rotation:.1f}°"
            rotation_surface = self.font_small.render(rotation_text, True, COLOR_WHITE)
            rotation_rect = rotation_surface.get_rect(right=self.screen_width - 20, top=100)
            screen.blit(rotation_surface, rotation_rect)
            
        # Drift indicator (when drifting)
        if self.drift_factor > 0.1:
            drift_text = f"DRIFT! {int(self.drift_factor * 100)}%"
            drift_color = COLOR_YELLOW if self.drift_factor < 0.7 else COLOR_RED
            drift_surface = self.font_large.render(drift_text, True, drift_color)
            drift_rect = drift_surface.get_rect(center=(self.screen_width // 2, 180))
            screen.blit(drift_surface, drift_rect)
            
        # Off-road warning indicators
        is_off_road = (self.player_x < self.road_left_edge or self.player_x > self.road_right_edge)
        
        if is_off_road or self.off_road_penalty > 0.1:
            # Main off-road warning
            if is_off_road:
                warning_text = "OFF ROAD!"
                warning_color = COLOR_RED
            else:
                warning_text = f"SPEED PENALTY: {int(self.off_road_penalty * 100)}%"
                warning_color = COLOR_YELLOW
                
            warning_surface = self.font_large.render(warning_text, True, warning_color)
            warning_rect = warning_surface.get_rect(center=(self.screen_width // 2, 220))
            screen.blit(warning_surface, warning_rect)
            
            # Off-road timer (if significant)
            if self.off_road_timer > 0.2:
                timer_text = f"Off-road: {self.off_road_timer:.1f}s"
                timer_surface = self.font_small.render(timer_text, True, COLOR_WHITE)
                timer_rect = timer_surface.get_rect(center=(self.screen_width // 2, 245))
                screen.blit(timer_surface, timer_rect)
        
        # Collision indicators
        if self.collision_speed_penalty > 0.05:  # Show if significant collision penalty
            collision_text = f"COLLISION DAMAGE: {int(self.collision_speed_penalty * 100)}%"
            collision_color = COLOR_YELLOW if self.collision_speed_penalty < 0.3 else COLOR_RED
            collision_surface = self.font_large.render(collision_text, True, collision_color)
            collision_rect = collision_surface.get_rect(center=(self.screen_width // 2, 270))
            screen.blit(collision_surface, collision_rect)
            
            # Show last collision type for feedback
            if self.last_collision_type:
                type_text = f"Hit {self.last_collision_type.upper()}"
                type_surface = self.font_small.render(type_text, True, COLOR_WHITE)
                type_rect = type_surface.get_rect(center=(self.screen_width // 2, 295))
                screen.blit(type_surface, type_rect)
        
        # Collision flash effect
        if self.collision_flash_timer > 0:
            # Create red flash overlay
            flash_alpha = int(128 * (self.collision_flash_timer / 0.3))  # Fade out over 300ms
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill(COLOR_RED)
            screen.blit(flash_surface, (0, 0))
        
        # Road boundary indicators (debug info)
        if self.turn_state != "straight":  # Only show during turns when boundaries matter most
            boundary_text = f"Road: {self.road_left_edge:.2f} - {self.road_right_edge:.2f}"
            boundary_surface = self.font_small.render(boundary_text, True, COLOR_WHITE)
            boundary_rect = boundary_surface.get_rect(right=self.screen_width - 20, top=120)
            screen.blit(boundary_surface, boundary_rect)
            
    def _draw_ready_screen(self, screen):
        """Draw the ready state screen."""
        # Title
        title_text = self.font_huge.render("THE DRIVE", True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(title_text, title_rect)
        
        # Selected track info
        if self.selected_track:
            track_info = f"Selected: {self.selected_track.display_name}"
            track_surface = self.font_large.render(track_info, True, COLOR_GREEN)
            track_rect = track_surface.get_rect(center=(self.screen_width // 2, 280))
            screen.blit(track_surface, track_rect)
            
            desc_surface = self.font_small.render(
                self.selected_track.description, True, COLOR_WHITE
            )
            desc_rect = desc_surface.get_rect(center=(self.screen_width // 2, 320))
            screen.blit(desc_surface, desc_rect)
            
        # Instructions
        instructions = [
            "Arrow Keys or WASD to drive",
            "Hold UP/W to accelerate",
            "LEFT/RIGHT or A/D to steer",
            "",
            "Press SPACE to start racing",
            "Press M to change music",
            "Press ESC to return to hub"
        ]
        
        draw_instructions(
            screen, instructions, self.font_small,
            self.screen_width // 2, 380, 30, COLOR_WHITE
        )
        
    def _draw_game_over_screen(self, screen):
        """Draw the game over screen."""
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(OVERLAY_GAME_OVER_ALPHA)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        # Results
        results_title = self.font_huge.render("RACE COMPLETE!", True, COLOR_WHITE)
        title_rect = results_title.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(results_title, title_rect)
        
        # Statistics
        stats = [
            f"Final Score: {self.score}",
            f"Distance: {int(self.distance_traveled)}m",
            f"Top Speed: {int(self.top_speed_reached * 100)}%",
            f"Final Position: {self.race_state.position}/{self.race_state.total_racers}",
        ]
        
        y_offset = 280
        for stat in stats:
            stat_surface = self.font_large.render(stat, True, COLOR_WHITE)
            stat_rect = stat_surface.get_rect(center=(self.screen_width // 2, y_offset))
            screen.blit(stat_surface, stat_rect)
            y_offset += 40
            
        # Options
        options = [
            "Press SPACE to race again",
            "Press M to change music",
            "Press L to view leaderboard",
            "Press ESC to return to hub"
        ]
        
        draw_instructions(
            screen, options, self.font_small,
            self.screen_width // 2, 480, 25, COLOR_WHITE
        )
        
    def _on_track_selected(self, track: MusicTrack):
        """Handle track selection from music selector."""
        self.selected_track = track
        self.race_music_manager.select_track(track)
        self.state = self.STATE_VEHICLE_SELECT  # Go to vehicle selection next
        
        print(f"Track selected: {track.display_name}")
        
    def _on_music_cancelled(self):
        """Handle music selection cancellation."""
        # Return to hub if no track was selected
        if not self.selected_track:
            return SCENE_HUB_WORLD
        else:
            # Return to ready state with current track
            self.state = self.STATE_READY
            
    def _on_vehicle_selected(self, vehicle: str):
        """Handle vehicle selection."""
        self.selected_vehicle = vehicle
        
        # Load the vehicle sprite
        try:
            self.car_sprite = load_vehicle_sprite(vehicle)
            print(f"Vehicle selected: {vehicle}")
        except Exception as e:
            print(f"[ERROR] Failed to load vehicle sprite: {e}")
            self.car_sprite = None
            
        # Save vehicle selection
        save_manager = self.scene_manager.save_manager
        if save_manager:
            save_manager.set_selected_vehicle(vehicle)
            save_manager.save()
            
        self.state = self.STATE_READY
        
    def _on_vehicle_cancelled(self):
        """Handle vehicle selection cancellation."""
        # Go back to music selection
        self.state = self.STATE_MUSIC_SELECT
            
    def _start_race(self):
        """Start the racing game."""
        self.state = self.STATE_RACING
        self.start_time = time.time()
        self.time_remaining = self.race_duration
        
        # Start race music
        self.race_music_manager.start_race_music(fade_in_ms=1000)
        
        # Reset race state
        self.race_state = RaceState(
            speed=0.0,
            position=self.race_state.total_racers,  # Start at back
            total_racers=self.race_state.total_racers,
            time_remaining=self.race_duration
        )
        
        # Reset player state
        self.player_speed = 0.0
        self.player_x = 0.5
        self.road_position = 0.0
        self.width_oscillation = 0.0  # Reset width oscillation
        self.distance_traveled = 0.0
        self.top_speed_reached = 0.0
        self.score = 0
        
    def _end_race(self):
        """End the current race."""
        self.state = self.STATE_GAME_OVER
        
        # Stop race music
        self.race_music_manager.stop_race_music(fade_out_ms=2000)
        
        # Determine if victory
        if self.race_state.position <= 3:
            self.race_state.is_victory = True
            
        self.race_state.is_game_over = True
        
        # Play victory/game over stinger
        if self.race_state.is_victory:
            self.race_music_manager.play_stinger("victory")
            
    def _restart_game(self):
        """Restart the game with the same track."""
        self.state = self.STATE_READY
        
    def on_enter(self, previous_scene, data):
        """Called when entering this scene."""
        # Load previously selected vehicle from save
        save_manager = self.scene_manager.save_manager
        if save_manager:
            saved_vehicle = save_manager.get_selected_vehicle()
            if saved_vehicle and saved_vehicle != self.selected_vehicle:
                self.selected_vehicle = saved_vehicle
                try:
                    self.car_sprite = load_vehicle_sprite(saved_vehicle)
                except Exception as e:
                    print(f"[ERROR] Failed to load saved vehicle sprite: {e}")
                    self.car_sprite = None
        
        # Start with music selection if no track selected
        if not self.selected_track:
            self.state = self.STATE_MUSIC_SELECT
        else:
            self.state = self.STATE_READY
            
    def on_exit(self):
        """Called when leaving this scene."""
        # Stop any playing music
        self.race_music_manager.stop_race_music(fade_out_ms=500)
        return {}