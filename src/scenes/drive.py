"""The Drive - OutRun-style racing minigame with music selection."""

import random
import time
import math
import os
import json
from datetime import datetime
from typing import Optional, List, Dict
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
from src.systems.traffic_awareness import TrafficAwareness, DriverPersonality
from src.utils.asset_paths import get_sfx_path
from src.utils.sprite_loader import load_image, load_vehicle_sprite
from src.ui.drawing_helpers import draw_text_with_background, draw_instructions
from src.systems.bmp_traffic_integration import BPMTrafficIntegration
from src.systems.road_geometry import RoadGeometry, RoadPosition
from src.testing.traffic_simulation_framework import TrafficSimulationHooks, SimulationMetrics


@dataclass
class NPCCar:
    """Represents an NPC vehicle in traffic (cars and trucks)."""
    # Road-relative position (NEW - Issue #32)
    road_pos: RoadPosition = None  # Position relative to road geometry
    
    # Legacy screen positions (maintained for compatibility)
    x: float = 0.0         # Horizontal position (0.0-1.0) - calculated from road_pos
    y: float = 0.0         # Vertical position (distance ahead/behind player)
    
    # Vehicle properties
    lane: int = 3          # Lane number (1-4: 1,2=oncoming, 3,4=same direction)
    speed: float = 0.8     # Independent speed (not relative to player anymore)
    color: tuple = (255, 255, 255)  # RGB color for the vehicle
    vehicle_type: str = "car"       # "car" or "truck"
    direction: int = 1     # 1 = same direction as player, -1 = oncoming
    width: int = 32        # Vehicle width in pixels
    height: int = 48       # Vehicle height in pixels
    
    # AI and behavior
    lane_change_timer: float = 0.0  # Timer for lane changes
    ai_state: str = "cruising"      # AI behavior state
    collision_zone: tuple = (32, 48)  # Collision detection size (width, height)
    sprite_name: str = None  # Name of sprite to use for rendering
    prev_x: float = None   # Previous x position for trajectory calculation
    rotation: float = 0.0  # Current rotation angle in degrees
    personality: DriverPersonality = None  # Driver behavior type
    desired_speed: float = 0.8  # Preferred cruising speed
    target_lane: int = None  # Target lane for lane changes
    lane_change_progress: float = 0.0  # Progress of current lane change (0-1)
    
    # Crash behavior properties
    is_crashing: bool = False  # Currently in a crash spin
    crash_rotation: float = 0.0  # Current crash rotation progress
    crash_target_rotation: float = 0.0  # Total rotation to complete
    crash_initial_speed: float = 0.0  # Speed at time of crash
    crash_target_x: float = 0.0  # Target X position (off road)
    
    def update_screen_position(self, road_geometry: RoadGeometry, road_curve: float = 0.0,
                             width_variation: float = 0.0, surface_noise: float = 0.0):
        """Update screen position from road position."""
        if self.road_pos:
            screen_x, screen_y = road_geometry.road_to_screen(
                self.road_pos.distance, self.road_pos.lane, self.road_pos.lane_offset,
                road_curve, width_variation, surface_noise
            )
            self.x = screen_x / road_geometry.screen_width  # Convert back to normalized
            self.y = screen_y


@dataclass
class Hazard:
    """Represents a hazard on the road (static or dynamic)."""
    # Road-relative position (NEW - Issue #32)
    road_pos: RoadPosition = None  # Position relative to road geometry
    
    # Legacy screen positions (maintained for compatibility)
    x: float = 0.0         # Horizontal position (0.0-1.0) - calculated from road_pos
    y: float = 0.0         # Vertical position (distance ahead/behind player)
    
    # Hazard properties
    lane: int = 3          # Lane number where hazard is placed
    hazard_type: str = "cone"  # "cone", "barrier", "warning_sign", "oil_slick", "debris", "water_puddle"
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
    
    def update_screen_position(self, road_geometry: RoadGeometry, road_curve: float = 0.0,
                             width_variation: float = 0.0, surface_noise: float = 0.0):
        """Update screen position from road position."""
        if self.road_pos:
            screen_x, screen_y = road_geometry.road_to_screen(
                self.road_pos.distance, self.road_pos.lane, self.road_pos.lane_offset,
                road_curve, width_variation, surface_noise
            )
            self.x = screen_x / road_geometry.screen_width  # Convert back to normalized
            self.y = screen_y


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
        self.traffic_density = 0.36       # Probability of spawning traffic (increased 20% from 0.3)
        self.max_traffic_cars = 8         # Maximum number of NPC cars on screen (increased 20% from 6)
        
        # Collision Detection System
        self.collision_cooldown = 0.0     # Cooldown timer to prevent multiple collisions
        self.collision_damage = 0.0       # Accumulated collision damage (0.0-1.0)
        self.collision_speed_penalty = 0.0  # Current speed penalty from collisions
        self.collision_recovery_rate = 0.5   # How fast collision penalties recover
        self.last_collision_type = None   # "car", "truck", "cone", "barrier" for feedback
        self.collision_flash_timer = 0.0  # Timer for visual collision feedback
        
        # Static Hazard System
        self.hazards: List[Hazard] = []   # List of active hazards
        self.max_hazards = 4               # Maximum number of hazards on screen
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
        self.straight_duration = 15.0    # Longer straight sections (increased from 8.0)
        self.turn_duration = 5.0         # Slower turns (increased from 4.0)
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
        self.road_width = 700  # Increased to 700 for easier tracking and visibility
        self.max_road_width = 1200  # Increased proportionally for wider road
        self.car_width = 64  # Display width (scaled from 128)
        self.car_height = 96  # Display height (scaled from 192)
        
        # UI fonts
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_huge = pygame.font.Font(None, FONT_HUGE)
        
        # Load traffic sprites
        self.traffic_sprites = self._load_traffic_sprites()
        
        # Score and statistics
        self.distance_traveled = 0.0
        self.top_speed_reached = 0.0
        self.score = 0
        
        # Input handling
        self.keys_pressed = set()
        
        # BMP synchronization system
        self.bmp_system = BPMTrafficIntegration(
            self, 
            scene_manager.sound_manager,
            self.screen_width,
            self.screen_height
        )
        
        # Traffic awareness system
        self.traffic_awareness = TrafficAwareness()
        self.bmp_overlay_visible = False  # Toggle with B key
        
        # OQE Traffic Metrics System (Issue #31 validation)
        self.oqe_metrics = SimulationMetrics()
        self.traffic_hooks = TrafficSimulationHooks(self.oqe_metrics)
        self.oqe_baseline_mode = False  # Toggle for baseline vs AI-enabled testing
        self.oqe_session_start_time = None
        self.oqe_fps_clock = pygame.time.Clock()  # For FPS tracking
        self.oqe_last_frame_time = time.time()
        
        # Road geometry system (Issue #32)
        self.road_geometry = RoadGeometry(self.screen_width, self.screen_height)
        
        # OQE event counter for performance sampling
        self.oqe_frame_count = 0
        
        # Register BMP callbacks
        self._setup_bmp_callbacks()
        
    def _setup_bmp_callbacks(self):
        """Setup BMP system callbacks for traffic spawning and speed modulation."""
        # Register spawn callback - connects BMP system to existing spawn logic
        # TODO: Fix BPM spawn system - temporarily disabled to allow normal traffic spawning
        # self.bmp_system.register_spawn_callback(self._bmp_spawn_callback)
        
        # Register speed callback - connects BMP system to traffic speed modulation
        # TODO: Fix BPM speed modulation - temporarily disabled
        # self.bmp_system.register_speed_callback(self._bmp_speed_callback)
        
    def _bmp_spawn_callback(self, spawn_params: Dict) -> bool:
        """Handle BMP-triggered traffic spawning."""
        try:
            # Use existing spawn logic but with BMP timing
            if len(self.npc_cars) < self.max_traffic_cars:
                self._spawn_npc_car()
                return True
            return False
        except Exception as e:
            print(f"Error in BMP spawn callback: {e}")
            return False
            
    def _bmp_speed_callback(self, car: NPCCar, beat_progress: float):
        """Apply BMP-synchronized speed modulation to traffic."""
        try:
            # Apply subtle speed pulsing based on beat
            base_modifier = 0.05  # 5% speed variation
            speed_modifier = math.sin(beat_progress * math.pi * 2) * base_modifier
            
            # Apply the modifier to the car's speed
            car.speed = car.speed * (1.0 + speed_modifier)
        except Exception as e:
            print(f"Error in BMP speed callback: {e}")
        
    def _load_traffic_sprites(self) -> Dict[str, pygame.Surface]:
        """Load all traffic vehicle sprites."""
        sprites = {}
        traffic_dir = os.path.join("assets", "images", "vehicles", "traffic")
        
        # Car sprites
        car_files = [
            "sedan_blue", "sedan_red", "sedan_green",
            "suv_silver", "suv_black", 
            "compact_yellow", "compact_orange"
        ]
        
        # Truck sprites
        truck_files = [
            "semi_truck_white", "semi_truck_red",
            "delivery_truck_brown", "pickup_truck_blue"
        ]
        
        # Load car sprites (32x48 target size)
        for car_file in car_files:
            path = os.path.join(traffic_dir, f"{car_file}.png")
            try:
                sprite = load_image(path, scale=(32, 48))
                sprites[car_file] = sprite
            except:
                # Create fallback colored rectangle if sprite fails to load
                fallback = pygame.Surface((32, 48), pygame.SRCALPHA)
                fallback.fill((100, 100, 100, 255))  # Gray fallback
                sprites[car_file] = fallback
                
        # Load truck sprites (40x80 target size)
        for truck_file in truck_files:
            path = os.path.join(traffic_dir, f"{truck_file}.png")
            try:
                sprite = load_image(path, scale=(40, 80))
                sprites[truck_file] = sprite
            except:
                # Create fallback colored rectangle if sprite fails to load
                fallback = pygame.Surface((40, 80), pygame.SRCALPHA)
                fallback.fill((80, 80, 80, 255))  # Dark gray fallback
                sprites[truck_file] = fallback
                
        return sprites
        
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
                elif event.key == pygame.K_b:
                    # Toggle BMP overlay
                    self.bmp_overlay_visible = not self.bmp_overlay_visible
                    print(f"BMP overlay {'enabled' if self.bmp_overlay_visible else 'disabled'}")
                elif event.key == pygame.K_F11:
                    # Toggle OQE baseline mode (AI disabled for testing)
                    self.oqe_baseline_mode = not self.oqe_baseline_mode
                    mode_name = "BASELINE (AI disabled)" if self.oqe_baseline_mode else "NORMAL (AI enabled)"
                    print(f"OQE Testing Mode: {mode_name}")
                    # Log mode change to game logger
                    self._log_oqe_event("mode_change", {
                        "new_mode": "baseline" if self.oqe_baseline_mode else "ai_enabled",
                        "timestamp": time.time()
                    })
                elif event.key == pygame.K_F10:
                    # Start new OQE session
                    if hasattr(self, 'traffic_hooks'):
                        self.oqe_session_start_time = time.time()
                        self.oqe_metrics = SimulationMetrics()  # Reset metrics
                        self.traffic_hooks.metrics = self.oqe_metrics
                        self.oqe_frame_count = 0  # Reset frame counter
                        session_type = "baseline" if self.oqe_baseline_mode else "ai_enabled"
                        print(f"OQE Session Started: {session_type}")
                        # Log session start to game logger
                        self._log_oqe_event("session_start", {
                            "session_type": session_type,
                            "timestamp": self.oqe_session_start_time,
                            "baseline_mode": self.oqe_baseline_mode
                        })
                elif event.key == pygame.K_F9:
                    # Export current OQE session
                    if hasattr(self, 'traffic_hooks') and self.oqe_session_start_time:
                        session_duration = time.time() - self.oqe_session_start_time
                        session_type = "baseline" if self.oqe_baseline_mode else "ai_enabled"
                        report = self.traffic_hooks.generate_session_report(session_type, session_duration)
                        
                        # Save report to file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"oqe_session_{session_type}_{timestamp}.json"
                        filepath = os.path.join("pipeline_reports", filename)
                        os.makedirs("pipeline_reports", exist_ok=True)
                        
                        with open(filepath, 'w') as f:
                            json.dump(report, f, indent=2)
                        
                        print(f"OQE Session Report saved: {filepath}")
                        print(f"Duration: {session_duration:.1f}s, Passes: {self.oqe_metrics.total_passes_completed}")
                        
                        # Log the complete export to game logger for persistent tracking
                        self._log_oqe_event("session_export", {
                            "session_type": session_type,
                            "duration_seconds": session_duration,
                            "total_passes": self.oqe_metrics.total_passes_completed,
                            "avg_fps": sum(self.oqe_metrics.fps_samples) / len(self.oqe_metrics.fps_samples) if self.oqe_metrics.fps_samples else 0,
                            "avg_scan_time_ms": sum(self.oqe_metrics.scan_times_ms) / len(self.oqe_metrics.scan_times_ms) if self.oqe_metrics.scan_times_ms else 0,
                            "file_saved": filepath,
                            "report_summary": report.get("summary", {}),
                            "pass_criteria": report["oqe_evidence"]["pass_criteria"] if "oqe_evidence" in report else {},
                            "memory_samples": len(self.oqe_metrics.memory_samples_mb)
                        })
                        
                        self.oqe_session_start_time = None
                    
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
        
    def _log_oqe_event(self, event_type: str, data: dict):
        """Log OQE events to game logger for persistent tracking"""
        if hasattr(self.scene_manager, 'game_logger') and self.scene_manager.game_logger:
            self.scene_manager.game_logger.log_system_event("oqe_traffic", event_type, data)
    
    def _update_racing(self, dt: float):
        """Update racing mechanics and state."""
        # OQE Hook: Frame start for FPS and performance tracking
        if hasattr(self, 'traffic_hooks'):
            # Calculate FPS from delta time
            current_time = time.time()
            frame_time = current_time - self.oqe_last_frame_time
            fps = 1.0 / frame_time if frame_time > 0 else 60.0
            self.oqe_last_frame_time = current_time
            
            # Clamp FPS to reasonable range
            fps = max(10.0, min(fps, 120.0))
            self.traffic_hooks.on_frame_start(fps)
            
            # Log OQE performance data every 5 seconds
            self.oqe_frame_count += 1
            if self.oqe_frame_count % 300 == 0:  # Every 5 seconds at 60 FPS
                import psutil
                process = psutil.Process()
                self._log_oqe_event("performance_sample", {
                    "fps": fps,
                    "frame_time_ms": frame_time * 1000,
                    "memory_mb": process.memory_info().rss / 1024 / 1024,
                    "frame_count": self.oqe_frame_count
                })
        
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
        freeway_curve_freq = 0.01  # Much slower curves (reduced from 0.02)
        freeway_curve_amplitude = 0.3  # Gentler curves (reduced from 0.6)
        
        # Base freeway curve
        freeway_curve = math.sin(self.road_position * freeway_curve_freq) * freeway_curve_amplitude
        
        # Add slight variation with a second wave
        freeway_variation = math.sin(self.road_position * freeway_curve_freq * 1.7) * freeway_curve_amplitude * 0.2
        
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
        
        # Update BMP synchronization system
        player_state = {
            'x': self.player_x,
            'speed': self.player_speed,
            'position': self.race_state.position
        }
        # TODO: Fix BMP system missing methods (is_tracking, etc)
        # self.bmp_system.update(dt, player_state, self.npc_cars)
        
        # Apply BMP speed modulation to existing traffic
        # self.bmp_system.handle_speed_modulation(self.npc_cars)
        
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
        road_center_pixels = self.screen_width // 2 + int(self.road_curve * 200)  # Match drawing curve effect
        
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
        # TODO: Fix BPM system spawning - for now always use normal spawning
        # The BPM system is incomplete and preventing normal traffic from spawning
        
        # Update spawn timer (always spawn traffic regardless of BPM system)
        self.traffic_spawn_timer += dt
        
        # Spawn new traffic cars (20% more traffic)
        spawn_interval = 2.0  # Reduced interval for more traffic (was 2.5)
        if (self.traffic_spawn_timer > spawn_interval and  
            len(self.npc_cars) < self.max_traffic_cars):
            # Increased spawn probability for 20% more traffic
            if random.random() < 0.6:  # 60% chance every 2.0 seconds (was 50% every 2.5s)
                self._spawn_npc_car()
            self.traffic_spawn_timer = 0.0
            
        # Update existing traffic cars
        cars_to_remove = []
        
        # OQE Hook: Detect congestion by counting cars close together in each lane
        if hasattr(self, 'traffic_hooks'):
            lane_car_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}  # Count cars per lane
            for check_car in self.npc_cars:
                # Count cars that are close to player (within visible range)
                if abs(check_car.y) < 200:  # Cars within close proximity
                    lane_car_counts[check_car.lane] += 1
            
            # Detect congestion (3+ cars in same lane within close range)
            for lane, car_count in lane_car_counts.items():
                if car_count >= 3:
                    self.traffic_hooks.on_congestion_detected(lane, car_count)
        
        for i, car in enumerate(self.npc_cars):
            # Store previous x position
            if car.prev_x is None:
                car.prev_x = car.x
            
            # OQE Hook: Log car update with lane and speed information
            if hasattr(self, 'traffic_hooks'):
                # Convert car speed to km/h for more meaningful metrics
                speed_kmh = car.speed * 60  # Rough conversion from normalized speed to km/h
                self.traffic_hooks.on_car_update(car.lane, speed_kmh)
            
            # Update road-relative position first (Issue #32)
            if car.road_pos:
                # Update distance along road based on direction and speeds
                if car.direction == 1:
                    # Same direction as player - use actual speed difference
                    relative_speed = car.speed - self.player_speed
                    car.road_pos.distance -= relative_speed * dt * 100  # Move relative to player
                else:
                    # Oncoming traffic - they approach based on combined speeds
                    combined_approach_speed = car.speed + self.player_speed
                    car.road_pos.distance += combined_approach_speed * dt * 100  # Approach from ahead
                
                # Update screen position from road position
                car.update_screen_position(
                    self.road_geometry, 
                    self.road_curve, 
                    self.width_oscillation,
                    self.surface_noise
                )
                
                # Log road geometry tracking (OQE - Issue #32)
                if hasattr(self.scene_manager, 'game_logger') and self.scene_manager.game_logger:
                    if i == 0 and len(self.npc_cars) > 0:  # Log for first car only to avoid spam
                        self.scene_manager.game_logger.log_system_event("road_geometry", "position_update", {
                            "car_id": f"npc_{i}",
                            "road_distance": car.road_pos.distance,
                            "lane": car.road_pos.lane,
                            "lane_offset": car.road_pos.lane_offset,
                            "screen_x": car.x * self.screen_width,
                            "screen_y": car.y,
                            "road_curve": self.road_curve,
                            "width_variation": self.width_oscillation
                        })
            else:
                # Fallback to legacy position updates for cars without road_pos
                if car.direction == 1:
                    relative_speed = car.speed - self.player_speed
                    car.y += relative_speed * dt * 100
                else:
                    combined_approach_speed = car.speed + self.player_speed
                    car.y -= combined_approach_speed * dt * 100
            
            # Update AI behavior or crash behavior
            if car.is_crashing:
                self._update_crash_behavior(car, dt)
            else:
                self._update_npc_ai(car, dt)
                # Check for traffic-to-traffic collision avoidance
                self._avoid_traffic_collisions(car, dt)
            
            # Enforce road boundaries for traffic cars (unless crashing)
            if not car.is_crashing:
                self._enforce_traffic_boundaries(car)
            
            # Calculate rotation based on lateral movement and road curve
            if car.prev_x is not None:
                # Calculate lateral velocity (change in x per frame)
                lateral_velocity = (car.x - car.prev_x) / dt if dt > 0 else 0
                
                # Also consider road curve for rotation
                # Cars should lean into curves naturally
                curve_rotation = self.road_curve * 15.0  # Base rotation from road curve
                
                # Calculate rotation angle based on lateral velocity and forward speed
                # Positive lateral velocity = moving right = rotate clockwise
                # Scale factor adjusts how much rotation per unit of lateral movement
                rotation_scale = 800.0  # Adjust this to control rotation sensitivity
                
                # For oncoming traffic, reverse the rotation direction
                direction_factor = 1 if car.direction == 1 else -1
                
                # Calculate target rotation combining lane changes and road curve
                lateral_rotation = lateral_velocity * rotation_scale * direction_factor
                total_rotation = lateral_rotation + (curve_rotation * direction_factor)
                
                # Clamp rotation to reasonable range
                target_rotation = max(-25, min(25, total_rotation))
                
                # Smooth rotation changes
                rotation_smoothing = 0.15
                car.rotation = car.rotation * (1 - rotation_smoothing) + target_rotation * rotation_smoothing
                
                # Update previous x position
                car.prev_x = car.x
            
            # Remove cars that are too far behind or ahead
            if car.y < -250 or car.y > 700:
                cars_to_remove.append(i)
                
        # Remove old cars (reverse order to maintain indices)
        for i in reversed(cars_to_remove):
            del self.npc_cars[i]
            
    def _spawn_npc_car(self):
        """Spawn a new NPC car in proper 4-lane traffic.
        
        Spawn Logic:
        - Slower cars (< 100% player speed) spawn ahead - player catches up
        - Faster cars (> 100% player speed) spawn behind - they catch up to player
        - For oncoming traffic: faster cars spawn farther for more reaction time
        """
        # 4-lane system: 
        # Lane 1: Left lane, oncoming traffic (opposite direction)
        # Lane 2: Right lane, oncoming traffic (opposite direction)
        # Lane 3: Left lane, player direction (same as player)
        # Lane 4: Right lane, player direction (same as player) 
        
        # Player is in lanes 3-4, oncoming traffic in lanes 1-2
        player_lane = 3 if self.player_x < 0.5 else 4  # Left or right in player direction
        
        # 50% chance for same direction (lanes 3-4), 50% for oncoming (lanes 1-2)
        if random.random() < 0.5:
            # Same direction traffic (lanes 3-4)
            direction = 1
            lane = random.choice([3, 4])
            # Prefer lane away from player
            if random.random() < 0.6 and lane == player_lane:
                lane = 7 - lane  # Switch to other lane (3↔4)
                
            # First determine speed, then spawn position based on speed
            # All traffic speeds are 80-120% of maximum speed (independent of player)
            max_speed = 1.0  # Maximum game speed
            npc_speed = random.uniform(0.8 * max_speed, 1.2 * max_speed)
            
            # Slower cars spawn ahead (top), faster cars spawn behind (bottom)
            if npc_speed < 1.0:  # Slower than player
                # Spawn ahead - player will catch up to them
                y_position = random.uniform(150, 350)  # Ahead of player
            else:  # Faster than player (>= 100%)
                # Spawn behind - they will catch up to player
                y_position = random.uniform(-250, -50)  # Behind player
                
            # Assign personality based on speed
            if npc_speed < 0.9:
                personality = DriverPersonality.CAUTIOUS
            elif npc_speed > 1.1:
                personality = DriverPersonality.AGGRESSIVE
            else:
                personality = DriverPersonality.NORMAL
        else:
            # Oncoming traffic (lanes 1-2)
            direction = -1
            lane = random.choice([1, 2])
            
            # First determine speed for oncoming traffic (independent of player)
            max_speed = 1.0  # Maximum game speed
            npc_speed = random.uniform(0.8 * max_speed, 1.2 * max_speed)
            
            # For oncoming traffic, faster cars need more distance
            if npc_speed < 1.0:  # Slower oncoming traffic
                # Less relative speed, can spawn closer
                y_position = random.uniform(200, 350)  
            else:  # Faster oncoming traffic (>= 100%)
                # Higher relative speed, need more reaction time
                y_position = random.uniform(350, 550)  # Spawn farther ahead
                
            # Assign personality for oncoming traffic
            if npc_speed < 0.9:
                personality = DriverPersonality.CAUTIOUS
            elif npc_speed > 1.1:
                personality = DriverPersonality.AGGRESSIVE
            else:
                personality = DriverPersonality.NORMAL
            
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
        
        # Apply curve offset to spawn position to align with road curves
        # Use the Y position where the car will spawn to get appropriate curve offset
        spawn_screen_y = self.screen_height - 200 if y_position <= 0 else int(self.horizon_y + (self.screen_height - self.horizon_y - 100) * (1 - min(abs(y_position) / 600.0, 1.0)))
        curve_offset_pixels = self._get_curve_offset_at_y(spawn_screen_y)
        curve_offset_normalized = curve_offset_pixels / self.screen_width
        x_position += curve_offset_normalized
        
        # Clamp to screen boundaries after curve adjustment
        x_position = max(0.05, min(0.95, x_position))
            
        # Determine vehicle type (10% chance for trucks)
        is_truck = random.random() < 0.15  # 15% chance for semi trucks
        
        if is_truck:
            vehicle_type = "truck"
            vehicle_width = 40      # Wider than cars
            vehicle_height = 80     # Much longer than cars
            collision_zone = (40, 80)
            # Select random truck sprite
            truck_sprites = [
                "semi_truck_white", "semi_truck_red",
                "delivery_truck_brown", "pickup_truck_blue"
            ]
            sprite_name = random.choice(truck_sprites)
            # Trucks are typically darker colors (fallback for no sprite)
            truck_colors = [
                (100, 100, 100),  # Dark gray
                (80, 80, 80),     # Darker gray
                (60, 60, 60),     # Very dark gray
                (120, 80, 40),    # Brown
                (40, 40, 120),    # Dark blue
                (80, 40, 40),     # Dark red
            ]
            vehicle_color = random.choice(truck_colors)
            # Trucks are 60-80% of maximum speed (independent of player)
            max_speed = 1.0  # Maximum game speed
            npc_speed = random.uniform(0.6 * max_speed, 0.8 * max_speed)
            # Since trucks are always slower, adjust spawn position if needed
            if direction == 1 and y_position < 0:  # Same direction but spawned behind
                y_position = random.uniform(200, 400)  # Move to ahead position
        else:
            vehicle_type = "car"
            vehicle_width = 32
            vehicle_height = 48
            collision_zone = (32, 48)
            # Select random car sprite
            car_sprites = [
                "sedan_blue", "sedan_red", "sedan_green",
                "suv_silver", "suv_black",
                "compact_yellow", "compact_orange"
            ]
            sprite_name = random.choice(car_sprites)
            # Regular car colors (fallback for no sprite)
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
        
        # Assign personality for trucks
        if vehicle_type == "truck":
            personality = DriverPersonality.TRUCK
            
        # Create road-relative position (Issue #32)
        # y_position is already relative to player (positive = ahead, negative = behind)
        road_distance = -y_position  # Negate because road geometry expects positive = ahead
        road_pos = RoadPosition(
            distance=road_distance,
            lane=lane,
            lane_offset=0.0  # Start in center of lane
        )
        
        npc_car = NPCCar(
            road_pos=road_pos,
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
            ai_state="cruising",
            sprite_name=sprite_name,
            personality=personality,
            desired_speed=npc_speed
        )
        
        # Store original spawn position for curve alignment tracking
        npc_car.original_lane_x = x_position
        npc_car.original_lane = lane
        
        self.npc_cars.append(npc_car)
        
    def _update_crash_behavior(self, car: NPCCar, dt: float):
        """Update car during crash - 720 degree spin and move toward grass."""
        # Update rotation (720 degrees over ~2 seconds)
        rotation_speed = 360.0  # degrees per second
        car.crash_rotation += rotation_speed * dt
        car.rotation += rotation_speed * dt
        
        # Move toward grass target
        x_speed = 0.3  # Move to side at 30% speed
        if car.crash_target_x < car.x:
            car.x -= x_speed * dt
        else:
            car.x += x_speed * dt
            
        # Gradually slow down
        deceleration = 0.5  # Decelerate at 50% per second
        car.speed = max(0, car.speed - deceleration * dt)
        
        # Check if crash animation is complete
        if car.crash_rotation >= car.crash_target_rotation and car.speed <= 0.1:
            # Car has spun 720 degrees and nearly stopped
            car.speed = 0
            car.ai_state = "stopped"
            # Keep car off road permanently
    
    def _update_npc_ai(self, car: NPCCar, dt: float):
        """Update NPC car AI behavior with intelligent passing logic."""
        # Update lane change timer
        car.lane_change_timer += dt
        
        # Only same-direction traffic can change lanes intelligently
        if car.direction == 1 and not getattr(self, 'oqe_baseline_mode', False):
            # Same direction traffic uses intelligent passing logic (disabled in baseline mode)
            if car.ai_state == "cruising":
                # Scan surrounding traffic
                scan_start_time = time.time()
                scan = self.traffic_awareness.scan_surrounding_traffic(car, self.npc_cars)
                
                # OQE Hook: Traffic scan timing
                if hasattr(self, 'traffic_hooks'):
                    scan_time_ms = (time.time() - scan_start_time) * 1000
                    self.traffic_hooks.on_traffic_scan(scan_time_ms)
                
                # Check for emergency evasion first
                evasion_dir = self.traffic_awareness.get_emergency_evasion(car, scan)
                
                # OQE Hook: Log emergency evasion attempt
                if hasattr(self, 'traffic_hooks'):
                    # Check if emergency evasion was needed (imminent collision)
                    emergency_needed = scan.ahead_same_lane and scan.distance_to_ahead < 30
                    if emergency_needed:
                        if evasion_dir:
                            # Emergency evasion attempted and successful direction found
                            self.traffic_hooks.on_emergency_evasion(True, True)
                        else:
                            # Emergency evasion needed but no safe direction available
                            self.traffic_hooks.on_emergency_evasion(True, False)
                
                if evasion_dir:
                    car.ai_state = "emergency_change"
                    target_lane = 4 if evasion_dir == 'right' and car.lane == 3 else 3
                    car.target_lane = target_lane
                    car.lane_change_timer = 0.0
                    car.lane_change_progress = 0.0
                    return
                
                # Check if we should attempt to pass
                should_pass, pass_direction = self.traffic_awareness.should_attempt_pass(car, scan)
                
                # Get cooldown based on personality
                cooldown = 8.0 if car.personality == DriverPersonality.TRUCK else \
                          6.0 if car.personality == DriverPersonality.CAUTIOUS else \
                          3.0 if car.personality == DriverPersonality.NORMAL else 2.0
                
                if should_pass and car.lane_change_timer > cooldown:
                    # Determine target lane based on passing direction
                    if pass_direction == 'right' and car.lane == 3:
                        car.target_lane = 4
                    elif pass_direction == 'left' and car.lane == 4:
                        car.target_lane = 3
                    else:
                        return  # Can't change in requested direction
                        
                    car.ai_state = "changing_lanes"
                    car.lane_change_timer = 0.0
                    car.lane_change_progress = 0.0
                        
            elif car.ai_state == "changing_lanes" or car.ai_state == "emergency_change":
                # Calculate target x position for the target lane
                if car.target_lane is not None:
                    # Use actual road boundaries instead of hardcoded values
                    road_left, road_right, road_width = self._get_road_boundaries()
                    road_center_normalized = road_left + road_width / 2
                    direction_width = road_width / 2
                    lane_width = direction_width / 2
                    
                    # Calculate target position
                    lane_offset = car.target_lane - 3  # Convert 3,4 to 0,1
                    target_x = road_center_normalized + lane_width * (lane_offset + 0.5)
                    
                    # Smoothly move to target position
                    lane_change_speed = 1.2 if car.ai_state == "emergency_change" else 0.8
                    car.lane_change_progress += lane_change_speed * dt
                    
                    if car.lane_change_progress >= 1.0:
                        # Complete the lane change
                        car.x = target_x
                        car.lane = car.target_lane
                        car.target_lane = None
                        car.ai_state = "cruising"
                        car.lane_change_progress = 0.0
                        
                        # OQE Hook: Lane change completed
                        if hasattr(self, 'traffic_hooks'):
                            self.traffic_hooks.on_lane_change_complete(car.personality.value)
                    else:
                        # Interpolate position
                        start_x = car.x if car.lane_change_progress == 0 else car.x
                        car.x = start_x + (target_x - start_x) * car.lane_change_progress
        else:
            # Oncoming traffic stays in their lanes (no lane changes)
            car.ai_state = "cruising"
                    
        # Adjust speed based on traffic ahead and personality (if not in baseline mode)
        if car.direction == 1 and car.ai_state == "cruising" and not getattr(self, 'oqe_baseline_mode', False):
            scan_start_time = time.time()
            scan = self.traffic_awareness.scan_surrounding_traffic(car, self.npc_cars)
            
            # OQE Hook: Additional traffic scan timing
            if hasattr(self, 'traffic_hooks'):
                scan_time_ms = (time.time() - scan_start_time) * 1000
                self.traffic_hooks.on_traffic_scan(scan_time_ms)
            if scan.ahead_same_lane and scan.distance_to_ahead < 100:
                # Slow down to match car ahead
                car.speed = max(0.2, scan.ahead_same_lane.speed - 0.1)
            else:
                # Return to desired speed
                speed_diff = car.desired_speed - car.speed
                car.speed += speed_diff * dt * 0.5  # Gradual acceleration
            
    def _is_lane_change_safe(self, car: NPCCar, target_lane: int) -> bool:
        """Check if lane change is safe for NPC car within their directional lanes."""
        # Calculate target position using actual road boundaries
        road_left, road_right, road_width = self._get_road_boundaries()
        road_center_normalized = road_left + road_width / 2
        direction_width = road_width / 2
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
            target_x = road_left + lane_width * (lane_offset + 0.5)
        
        # Ensure target position is within the correct directional boundaries
        if car.direction == 1:
            # Same direction - right half of road
            direction_left = road_center_normalized + 0.02
            direction_right = road_right - 0.02
        else:
            # Oncoming direction - left half of road
            direction_left = road_left + 0.02
            direction_right = road_center_normalized - 0.02
            
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
        
        # Note: This returns the BASE road boundaries without curve offset
        # Curve offset should be applied separately when positioning objects
        road_left_pixels = road_center_pixels - current_road_width_pixels // 2
        road_right_pixels = road_center_pixels + current_road_width_pixels // 2
        
        # Convert to normalized coordinates (0.0-1.0)
        road_left_normalized = road_left_pixels / self.screen_width
        road_right_normalized = road_right_pixels / self.screen_width
        road_width_normalized = road_right_normalized - road_left_normalized
        
        return road_left_normalized, road_right_normalized, road_width_normalized
    
    def _get_curve_offset_at_y(self, y_position: float) -> int:
        """Get the horizontal curve offset in pixels for a given Y position.
        
        This function calculates the exact curve offset that matches the road rendering,
        ensuring traffic and hazards align perfectly with the road curves.
        """
        # Ensure Y is within screen bounds
        if y_position < self.horizon_y:
            return 0
            
        # Calculate distance factor exactly matching road rendering
        screen_factor = (y_position - self.horizon_y) / (self.screen_height - self.horizon_y)
        screen_factor = max(0, min(1, screen_factor))
        distance_factor = 1.0 - screen_factor
        
        # Match road rendering curve calculation exactly
        # This must match the scanline rendering in _draw_road_background
        curve_intensity = distance_factor * distance_factor
        
        # Primary curve offset (matches road_curve * 300 * curve_intensity in road rendering)
        scanline_curve = int(self.road_curve * 300 * curve_intensity)
        
        # S-curve oscillation (matches road rendering exactly)
        road_phase = self.road_position * 0.01
        s_curve = math.sin(road_phase + distance_factor * 3) * 50 * curve_intensity
        
        return scanline_curve + int(s_curve)
        
    def _enforce_traffic_boundaries(self, car: NPCCar):
        """Ensure traffic cars stay within their directional lanes and road boundaries.
        
        This function now accounts for road curves to keep cars properly aligned.
        """
        # Get actual road boundaries (base road without curve compensation)
        road_left_normalized, road_right_normalized, road_width_normalized = self._get_road_boundaries()
        
        # Split road into two directions
        direction_width = road_width_normalized / 2  # Each direction gets half the road
        lane_width = direction_width / 2  # 2 lanes per direction
        road_center_normalized = road_left_normalized + road_width_normalized / 2
        
        # Define directional boundaries - STRICT enforcement to prevent touching grass
        # Add margin to ensure cars never touch the green grass
        road_margin = 0.05  # 5% margin from road edges
        car_half_width = 0.02  # Half of car width in normalized coordinates
        
        if car.direction == 1:  # Same direction (right half)
            direction_left = road_center_normalized + car_half_width
            direction_right = road_right_normalized - road_margin - car_half_width
        else:  # Oncoming direction (left half)
            direction_left = road_left_normalized + road_margin + car_half_width
            direction_right = road_center_normalized - car_half_width
        
        # Enforce directional boundaries - push cars back into their side
        # Note: We don't apply curve offset here because cars should stay in lanes
        # relative to each other, and curve offset is applied during rendering
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
                                # Store target for lane change using actual road boundaries
                                road_left, road_right, road_width = self._get_road_boundaries()
                                road_center_normalized = road_left + road_width / 2
                                direction_width = road_width / 2
                                lane_width = direction_width / 2
                                
                                if car.direction == 1:  # Same direction (right half)
                                    lane_offset = target_lane - 3
                                    car.target_x = road_center_normalized + lane_width * (lane_offset + 0.5)
                                else:  # Oncoming (left half)
                                    lane_offset = target_lane - 1
                                    car.target_x = road_left + lane_width * (lane_offset + 0.5)
                                
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
        player_collision_width = 0.02  # Smaller collision box (~25px at 1280px width)
        player_collision_height = 0.04  # Smaller height for more forgiving collisions
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
                # OQE Hook: Log collision event
                if hasattr(self, 'traffic_hooks'):
                    self.traffic_hooks.on_collision()
                
                self._handle_collision(car)
                break  # Only handle one collision per frame
                
    def _handle_collision(self, car: NPCCar):
        """Handle collision with a traffic vehicle."""
        # OQE Hook: Log collision with traffic vehicle
        if hasattr(self, 'traffic_hooks'):
            self.traffic_hooks.on_collision()
        
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
                
        # Start collision behavior: 720 degree spin and attempt to go onto grass
        car.is_crashing = True
        car.crash_rotation = 0.0  # Start rotation counter
        car.crash_target_rotation = 720.0  # 720 degrees total
        car.crash_initial_speed = car.speed
        car.ai_state = "crashing"
        
        # Set target to go off road (onto grass)
        if random.random() < 0.5:
            # Go left onto grass
            car.crash_target_x = -0.2  # Well off the road
        else:
            # Go right onto grass  
            car.crash_target_x = 1.2  # Well off the road
            
        # Slow car to a stop
        car.speed = 0.0
    
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
            # Cones at intervals - pass y position for curve-aware positioning
            for y in range(int(start_y), int(end_y), 40):
                # Get lane position with curve compensation for this Y position
                lane_x = self._get_lane_x_position(lane, y)
                self._spawn_hazard("cone", lane_x, y, lane)
                
            # Barriers for longer blockages
            if zone_length > 300:
                barrier_y = start_y + zone_length // 2
                # Get lane position with curve compensation for barrier position
                lane_x = self._get_lane_x_position(lane, barrier_y)
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
        # Don't spawn more hazards if we're at the limit
        if len(self.hazards) >= self.max_hazards:
            return
        
        # Get BMP beat info for rhythmic hazard spawning
        beat_info = None
        if self.bmp_system.is_enabled and hasattr(self.bmp_system.bpm_tracker, 'get_beat_info'):
            beat_info = self.bmp_system.bpm_tracker.get_beat_info()
            
        # Oil slicks from trucks (BMP-enhanced spawn rate)
        for npc in self.npc_cars:
            base_oil_chance = 0.001  # Base chance
            oil_chance = base_oil_chance
            
            # Increase chance on strong beats
            if beat_info and beat_info.is_beat:
                oil_chance *= (1.0 + beat_info.beat_strength * 2.0)  # Up to 3x on downbeats
                
            if npc.vehicle_type == "truck" and npc.y > 0 and random.random() < oil_chance:
                # Spawn oil slick behind truck
                oil_x = npc.x + random.uniform(-0.02, 0.02)
                oil_y = npc.y - 50
                self._spawn_dynamic_hazard("oil_slick", oil_x, oil_y, "truck")
                # Stop if we've hit the limit
                if len(self.hazards) >= self.max_hazards:
                    return
        
        # BMP-synchronized debris spawning
        base_debris_chance = 0.0008  # Base chance
        debris_chance = base_debris_chance
        
        # Sync debris spawning to rhythm
        if beat_info:
            if beat_info.is_downbeat:
                debris_chance *= 4.0  # Much higher chance on downbeats
            elif beat_info.beat_number == 3:
                debris_chance *= 2.0  # Higher chance on beat 3
            elif beat_info.is_beat:
                debris_chance *= 1.5  # Slightly higher on any beat
                
        if random.random() < debris_chance:
            # Get current road boundaries
            road_left, road_right, road_width = self._get_road_boundaries()
            # Spawn within road boundaries with some margin
            margin = 0.05  # 5% margin from edges
            debris_x = random.uniform(road_left + margin, road_right - margin)
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
    
    def _get_lane_x_position(self, lane: int, y_position: float = None) -> float:
        """Get the normalized X position for a given lane, optionally accounting for road curves.
        
        Args:
            lane: Lane number (1-4)
            y_position: Y position to calculate curve offset for (defaults to no curve compensation)
        """
        # Get current road boundaries
        road_left, road_right, road_width = self._get_road_boundaries()
        
        # Calculate base lane positions (no curve compensation)
        direction_width = road_width / 2
        lane_width = direction_width / 2
        road_center = road_left + road_width / 2
        
        if lane in [1, 2]:  # Oncoming lanes (left side)
            lane_offset = lane - 1  # Convert to 0, 1
            base_x = road_left + lane_width * (lane_offset + 0.5)
        else:  # Player direction lanes (right side)
            lane_offset = lane - 3  # Convert to 0, 1
            base_x = road_center + lane_width * (lane_offset + 0.5)
        
        # Apply curve offset if y_position provided (for hazard positioning)
        if y_position is not None:
            # Convert y_position to screen space if needed
            if y_position > 0:  # Ahead of player
                y_progress = min(y_position / 600.0, 1.0)
                screen_y = int(self.horizon_y + (self.screen_height - self.horizon_y - 100) * (1 - y_progress))
            else:  # Behind player
                screen_y = self.screen_height - 100
            
            curve_offset_pixels = self._get_curve_offset_at_y(screen_y)
            curve_offset_normalized = curve_offset_pixels / self.screen_width
            return base_x + curve_offset_normalized
        
        return base_x
    
    def _check_hazard_collisions(self, dt: float):
        """Check for collisions between player and static hazards."""
        # Skip if in collision cooldown
        if self.collision_cooldown > 0:
            return
            
        # Get player collision rectangle
        player_collision_width = 0.02  # Smaller collision box
        player_collision_height = 0.04  # Smaller height
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
                
                # OQE Hook: Log hazard collision
                if hasattr(self, 'traffic_hooks'):
                    self.traffic_hooks.on_collision()
                
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
        road_center = self.screen_width // 2 + int(self.road_curve * 200)  # Increased curve effect for visibility
        
        # Apply multiple layers of variation for realistic road
        base_width_variation = int(self.width_oscillation)  # Primary width changes
        surface_variation = int(self.surface_noise)  # Micro road texture
        current_width = self.road_width + base_width_variation + surface_variation
        
        # Pole Position style scanline-based road rendering
        road_color = (60, 60, 60)
        grass_color_light = (34, 139, 34)
        grass_color_dark = (28, 120, 28)
        rumble_strip_red = (255, 0, 0)
        rumble_strip_white = (255, 255, 255)
        
        # Draw road scanline by scanline for authentic retro effect
        for y in range(self.horizon_y, self.screen_height):
            # Calculate distance factor (0 at bottom, 1 at horizon)
            screen_factor = (y - self.horizon_y) / (self.screen_height - self.horizon_y)
            distance_factor = 1.0 - screen_factor  # Inverted for perspective
            
            # Pole Position style curve calculation
            # More curve at distance, multiple curve components
            curve_intensity = distance_factor * distance_factor  # Squared for more dramatic effect
            
            # Calculate horizontal offset for this scanline
            # Combine turn curve and gentle freeway curves
            scanline_curve = int(self.road_curve * 300 * curve_intensity)
            
            # Add subtle S-curve oscillation for more dynamic feel
            road_phase = self.road_position * 0.01
            s_curve = math.sin(road_phase + distance_factor * 3) * 50 * curve_intensity
            
            # Total horizontal offset
            total_offset = scanline_curve + int(s_curve)
            
            # Calculate road center for this scanline
            line_center = self.screen_width // 2 + total_offset
            
            # Calculate road width with perspective
            perspective_width = 0.2 + 0.8 * screen_factor  # 20% at horizon, 100% at bottom
            line_width = int(current_width * perspective_width)
            
            # Draw grass background with alternating colors for texture
            if int(y + self.road_position * 10) % 4 < 2:
                grass_color = grass_color_light
            else:
                grass_color = grass_color_dark
            pygame.draw.line(screen, grass_color, (0, y), (self.screen_width, y), 1)
            
            # Draw road
            road_left = line_center - line_width // 2
            road_right = line_center + line_width // 2
            pygame.draw.line(screen, road_color, (road_left, y), (road_right, y), 1)
            
            # Draw rumble strips on edges (classic racing game style)
            if int(y + self.road_position * 20) % 8 < 4:
                # Left rumble strip
                pygame.draw.line(screen, rumble_strip_red, (road_left - 5, y), (road_left - 2, y), 1)
                pygame.draw.line(screen, rumble_strip_white, (road_left - 2, y), (road_left, y), 1)
                # Right rumble strip  
                pygame.draw.line(screen, rumble_strip_white, (road_right, y), (road_right + 2, y), 1)
                pygame.draw.line(screen, rumble_strip_red, (road_right + 2, y), (road_right + 5, y), 1)
        
        # Draw lane markings Pole Position style
        line_color = COLOR_YELLOW
        road_marking_white = COLOR_WHITE
        
        # Draw lane lines scanline by scanline
        for y in range(self.horizon_y, self.screen_height):
            screen_factor = (y - self.horizon_y) / (self.screen_height - self.horizon_y)
            distance_factor = 1.0 - screen_factor
            curve_intensity = distance_factor * distance_factor
            
            # Calculate positions
            scanline_curve = int(self.road_curve * 300 * curve_intensity)
            road_phase = self.road_position * 0.01
            s_curve = math.sin(road_phase + distance_factor * 3) * 50 * curve_intensity
            total_offset = scanline_curve + int(s_curve)
            line_center = self.screen_width // 2 + total_offset
            perspective_width = 0.2 + 0.8 * screen_factor
            line_width = int(current_width * perspective_width)
            
            # Center line (dashed white)
            if int(y + self.road_position * 30) % 40 < 20:
                pygame.draw.line(screen, road_marking_white, 
                               (line_center - 2, y), (line_center + 2, y), 1)
            
            # Lane dividers (dashed yellow) 
            if int(y + self.road_position * 30) % 60 < 20:
                # Left lane divider
                left_lane_x = line_center - line_width // 4
                pygame.draw.line(screen, line_color,
                               (left_lane_x - 1, y), (left_lane_x + 1, y), 1)
                
                # Right lane divider
                right_lane_x = line_center + line_width // 4
                pygame.draw.line(screen, line_color,
                               (right_lane_x - 1, y), (right_lane_x + 1, y), 1)
        
        # Note: Road edges are now drawn as part of the scanline rendering above
                               
    def _draw_road_edges_legacy(self, screen, road_center: int, road_width: int):
        """Legacy road edge drawing - replaced by Pole Position style rendering."""
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
            # Keep hazards on the road (below horizon)
            # Map hazard.y (0-600) to screen space (horizon_y to screen_height)
            if hazard.y > 0:
                # Hazards ahead of player
                hazard_progress = min(hazard.y / 600.0, 1.0)  # Normalize to 0-1
                hazard_screen_y = int(self.horizon_y + (self.screen_height - self.horizon_y) * (1 - hazard_progress))
            else:
                # Hazards behind player
                hazard_screen_y = self.screen_height - 100
            
            # Get the x position - either from lane or direct x coordinate
            if hazard.lane > 0:
                # Lane-based hazard - get lane position with curve compensation
                hazard_x = self._get_lane_x_position(hazard.lane, hazard.y)
                # For lane-based hazards, curve offset is already included
                hazard_screen_x = int(hazard_x * self.screen_width)
            else:
                # Free-positioned hazard - apply curve offset manually
                hazard_x = hazard.x
                curve_offset = self._get_curve_offset_at_y(hazard_screen_y)
                hazard_screen_x = int(hazard_x * self.screen_width) + curve_offset
            
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
            # Use perspective mapping to keep cars on road
            if car.y > 0:
                # Cars ahead of player
                car_progress = min(car.y / 600.0, 1.0)  # Normalize to 0-1
                car_screen_y = int(self.horizon_y + (self.screen_height - self.horizon_y - 100) * (1 - car_progress))
            else:
                # Cars behind player
                car_screen_y = self.screen_height - 100 + int(abs(car.y) * 0.5)
            
            # Apply curve offset to maintain alignment with road curves
            # All traffic cars need curve offset applied during rendering
            curve_offset = self._get_curve_offset_at_y(car_screen_y)
            car_screen_x = int(car.x * self.screen_width) + curve_offset
            
            # Only draw if vehicle is visible on screen
            if -50 <= car_screen_y <= self.screen_height + 50:
                # Draw vehicle rectangle based on type
                car_rect = pygame.Rect(
                    car_screen_x - car.width // 2,
                    car_screen_y - car.height // 2,
                    car.width,
                    car.height
                )
                
                # Try to use sprite, fallback to rectangles if not available
                if car.sprite_name and car.sprite_name in self.traffic_sprites:
                    sprite = self.traffic_sprites[car.sprite_name]
                    
                    # Flip sprite vertically for oncoming traffic
                    if car.direction == -1:
                        sprite = pygame.transform.flip(sprite, False, True)
                    
                    # Apply rotation based on trajectory
                    if abs(car.rotation) > 0.1:  # Only rotate if there's meaningful rotation
                        rotated_sprite = pygame.transform.rotate(sprite, -car.rotation)  # Negative for correct direction
                        sprite_rect = rotated_sprite.get_rect(center=car_rect.center)
                        screen.blit(rotated_sprite, sprite_rect)
                    else:
                        # Draw sprite without rotation for straight movement
                        sprite_rect = sprite.get_rect(center=car_rect.center)
                        screen.blit(sprite, sprite_rect)
                else:
                    # Fallback to rectangle rendering
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
            # Always apply rotation if there's any slip spin
            if abs(total_rotation) > 0.1 or self.slip_spin_angle > 0:
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
        
        # Debug: Show road curve value (temporary)
        if abs(self.road_curve) > 0.01:
            curve_text = f"Road Curve: {self.road_curve:.2f}"
            curve_surface = self.font_small.render(curve_text, True, COLOR_WHITE)
            screen.blit(curve_surface, (20, 200))
        
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
            
            # Position near the car but ensure it stays on screen
            car_screen_x = int(self.player_x * self.screen_width)
            bubble_x = car_screen_x + 50
            
            # Keep bubble in the road area (below horizon but above car)
            bubble_y = self.horizon_y + 150  # Below sky, in road area
            
            # Measure text for bubble size - use smaller font
            text_surface = self.font_small.render(self.current_comic_text, True, COLOR_BLACK)
            text_rect = text_surface.get_rect()
            
            # Create bubble background with smaller padding
            bubble_padding = 15
            bubble_rect = text_rect.inflate(bubble_padding * 2, bubble_padding)
            bubble_rect.center = (bubble_x, bubble_y)
            
            # Keep bubble on screen
            if bubble_rect.right > self.screen_width - 20:
                bubble_rect.right = self.screen_width - 20
            if bubble_rect.left < 20:
                bubble_rect.left = 20
            
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
            
        # Draw BMP rhythmic visual effects
        # TODO: Fix BMP drawing methods
        # self.bmp_system.draw_rhythm_effects(screen)
        
        # Draw BMP overlay if enabled
        if self.bmp_overlay_visible:
            self._draw_bmp_overlay(screen)
            
    def _draw_bmp_overlay(self, screen):
        """Draw BMP synchronization overlay and debugging information."""
        stats = self.bmp_system.get_current_stats()
        
        # Create overlay background
        overlay_width = 300
        overlay_height = 200
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Position overlay in top-left corner
        overlay_rect = pygame.Rect(10, 10, overlay_width, overlay_height)
        screen.blit(overlay_surface, overlay_rect)
        
        # Draw overlay border
        pygame.draw.rect(screen, COLOR_GREEN, overlay_rect, 2)
        
        # BMP information
        y_offset = 25
        line_height = 20
        
        # Title
        title_text = self.font_small.render("BMP SYNC", True, COLOR_GREEN)
        screen.blit(title_text, (20, y_offset))
        y_offset += line_height + 5
        
        # Current BMP info
        if 'bmp_tracker' in stats:
            bmp_info = stats['bmp_tracker']
            current_bpm = stats.get('integration_state', {}).get('current_bpm', 120)
            beat_count = stats.get('integration_state', {}).get('beat_count', 0)
            
            bpm_text = f"BPM: {current_bpm:.1f}"
            beat_text = f"Beats: {beat_count}"
            
            bpm_surface = self.font_small.render(bpm_text, True, COLOR_WHITE)
            beat_surface = self.font_small.render(beat_text, True, COLOR_WHITE)
            
            screen.blit(bpm_surface, (20, y_offset))
            y_offset += line_height
            screen.blit(beat_surface, (20, y_offset))
            y_offset += line_height + 5
        
        # Rhythm intensity
        rhythm_intensity = stats.get('integration_state', {}).get('rhythm_intensity', 0.7)
        intensity_text = f"Intensity: {rhythm_intensity:.1f}"
        intensity_surface = self.font_small.render(intensity_text, True, COLOR_YELLOW)
        screen.blit(intensity_surface, (20, y_offset))
        y_offset += line_height
        
        # Traffic sync stats
        if 'traffic_controller' in stats:
            traffic_stats = stats['traffic_controller']
            sync_text = f"Traffic Synced: {len(self.npc_cars)}"
            sync_surface = self.font_small.render(sync_text, True, COLOR_WHITE)
            screen.blit(sync_surface, (20, y_offset))
            y_offset += line_height
            
        # Beat indicator (visual pulse)
        beat_progress = getattr(self.bmp_system.bmp_tracker, 'get_beat_progress', lambda: 0.0)()
        if hasattr(self.bmp_system.bmp_tracker, 'get_beat_info'):
            beat_info = self.bmp_system.bpm_tracker.get_beat_info()
            if beat_info.is_beat:
                # Draw beat flash
                pulse_radius = int(15 + 10 * beat_info.beat_strength)
                pulse_color = (0, 255, 0) if beat_info.is_downbeat else (255, 255, 0)
                pygame.draw.circle(screen, pulse_color, (overlay_width - 30, 40), pulse_radius)
        
        # Instructions
        y_offset += 10
        help_text = "Press B to toggle"
        help_surface = self.font_small.render(help_text, True, COLOR_YELLOW)
        screen.blit(help_surface, (20, y_offset))
            
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
            
        # Skip saving vehicle selection for now
        # The save manager doesn't have vehicle support yet
            
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
        
        # Initialize BMP system with selected track
        if self.selected_track:
            self.bmp_system.initialize_for_track(self.selected_track)
            print(f"BMP system initialized for track: {self.selected_track.display_name}")
        
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
        
        # Cleanup BMP system
        self.bmp_system.cleanup()
        
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
        # CRITICAL FIX: Stop any existing music from previous scenes (like hub music)
        # This prevents music bleed-through and crashes
        pygame.mixer.music.stop()
        self.scene_manager.sound_manager.stop_music(fade_ms=500)
        
        # Load previously selected vehicle from save
        # Load previously selected vehicle from save
        # For now, we'll skip this since the save manager doesn't have vehicle support yet
        
        # Start with music selection if no track selected
        if not self.selected_track:
            self.state = self.STATE_MUSIC_SELECT
        else:
            self.state = self.STATE_READY
            
    def on_exit(self):
        """Called when leaving this scene."""
        # Stop any playing music
        self.race_music_manager.stop_race_music(fade_out_ms=500)
        
        # Force stop all pygame music to prevent bleed-through
        pygame.mixer.music.stop()
        
        # Clean up any ongoing sounds
        if hasattr(self, 'music_selector') and hasattr(self.music_selector, '_stop_preview'):
            self.music_selector._stop_preview()
            
        return {}