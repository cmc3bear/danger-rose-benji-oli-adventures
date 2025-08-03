import math
import random
import time
from datetime import datetime

import pygame

from src.config.constants import (
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_WATER_SPLASH,
    COLOR_WHITE,
    FONT_HUGE,
    FONT_LARGE,
    FONT_SMALL,
    GRAVITY,
    SCENE_HUB_WORLD,
    SCENE_NAME_ENTRY,
    SPRITE_DISPLAY_SIZE,
    UI_INSTRUCTION_START_Y,
)
from src.entities.pool_targets import (
    BeachBallTarget,
    DonutFloatTarget,
    DuckTarget,
    PoolTarget,
)
from src.entities.powerup import (
    ActivePowerUp,
    HomingPowerUp,
    PowerUp,
    RapidFirePowerUp,
    TripleShotPowerUp,
)
from src.entities.target_particles import TargetDestroyEffect
from src.ui.drawing_helpers import (
    draw_instructions,
    draw_progress_bar,
    draw_text_with_background,
)
from src.utils.asset_paths import get_sfx_path
from src.utils.attack_character import AnimatedCharacter
from src.utils.high_score_manager import HighScoreManager, ScoreEntry


class PoolPlayer:
    """Player character for the pool minigame."""

    def __init__(self, x: int, y: int, character_name: str):
        self.x = x
        self.y = y
        self.character_name = character_name

        # Create animated character using new individual file system
        self.sprite = AnimatedCharacter(
            character_name.lower(), "pool", (SPRITE_DISPLAY_SIZE, SPRITE_DISPLAY_SIZE)
        )
        # Set to idle animation for pool game
        self.sprite.set_animation("idle", loop=True)

        # Collision rect
        self.rect = pygame.Rect(x - 32, y - 32, 64, 64)

    def update(self, dt: float):
        # Update animation
        self.sprite.update()

        # Update rect position
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def draw(self, screen):
        sprite = self.sprite.get_current_sprite()
        sprite_rect = sprite.get_rect(center=(self.x, self.y))
        screen.blit(sprite, sprite_rect)


class WaterBalloon:
    """Water balloon projectile with physics."""

    def __init__(
        self,
        start_x: float,
        start_y: float,
        target_x: float,
        target_y: float,
        launch_speed: float = 800,
        is_homing: bool = False,
    ):
        self.x = float(start_x)
        self.y = float(start_y)
        self.start_x = start_x
        self.start_y = start_y

        # Calculate launch angle and velocity
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            # Normalize direction
            self.vx = (dx / distance) * launch_speed
            self.vy = (dy / distance) * launch_speed

            # Add upward arc to make it more realistic
            self.vy -= 300  # Initial upward velocity
        else:
            self.vx = 0
            self.vy = -launch_speed

        # Visual properties
        self.radius = 8
        self.color = COLOR_BLUE
        self.trail = []  # For trail effect
        self.max_trail_length = 10

        # Physics properties
        self.gravity = GRAVITY * 0.5  # Reduced gravity for better arc
        self.active = True

        # Homing properties
        self.is_homing = is_homing
        self.homing_strength = 300.0  # Acceleration towards target
        self.max_speed = 1000.0

        # Collision rect
        self.rect = pygame.Rect(
            self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2
        )

    def update(self, dt: float, targets: list[PoolTarget] = None):
        """Update projectile physics."""
        if not self.active:
            return

        # Store trail position
        if len(self.trail) < self.max_trail_length:
            self.trail.append((self.x, self.y))
        else:
            self.trail.pop(0)
            self.trail.append((self.x, self.y))

        # Apply homing if enabled and targets exist
        if self.is_homing and targets:
            # Find nearest target
            nearest_target = None
            min_distance = float("inf")

            for target in targets:
                if target.active:
                    distance = math.sqrt(
                        (target.x - self.x) ** 2 + (target.y - self.y) ** 2
                    )
                    if distance < min_distance:
                        min_distance = distance
                        nearest_target = target

            # Apply homing force towards nearest target
            if nearest_target and min_distance < 300:  # Homing range
                dx = nearest_target.x - self.x
                dy = nearest_target.y - self.y
                distance = math.sqrt(dx**2 + dy**2)

                if distance > 0:
                    # Acceleration towards target
                    ax = (dx / distance) * self.homing_strength
                    ay = (dy / distance) * self.homing_strength

                    # Apply acceleration
                    self.vx += ax * dt
                    self.vy += ay * dt

                    # Limit speed
                    speed = math.sqrt(self.vx**2 + self.vy**2)
                    if speed > self.max_speed:
                        self.vx = (self.vx / speed) * self.max_speed
                        self.vy = (self.vy / speed) * self.max_speed

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Apply gravity
        self.vy += self.gravity * dt

        # Update collision rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Deactivate if off screen or hits water
        if self.y > 600 or self.x < -50 or self.x > 1350:
            self.active = False

    def draw(self, screen):
        """Draw the water balloon with trail effect."""
        if not self.active:
            return

        # Draw trail (simplified without creating surfaces)
        for i, (tx, ty) in enumerate(self.trail):
            trail_radius = int(self.radius * (i / len(self.trail)))
            if trail_radius > 0:
                # Simple fading trail without per-pixel alpha
                fade_factor = i / len(self.trail)
                faded_color = tuple(int(c * fade_factor) for c in self.color)
                pygame.draw.circle(
                    screen, faded_color, (int(tx), int(ty)), trail_radius
                )

        # Draw main balloon
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, COLOR_WHITE, (int(self.x - 2), int(self.y - 2)), 3)


class SplashEffect:
    """Visual splash effect when balloon hits something."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.time = 0
        self.max_time = 0.5
        self.active = True
        self.particles = []

        # Create splash particles
        for i in range(12):
            angle = (math.pi * 2 * i) / 12
            speed = 100 + random.random() * 50
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed - 50,
                    "size": 3 + random.random() * 3,
                }
            )

    def update(self, dt: float):
        """Update splash animation."""
        self.time += dt
        if self.time >= self.max_time:
            self.active = False
            return

        # Update particles
        for particle in self.particles:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["vy"] += 300 * dt  # Gravity
            particle["size"] *= 0.95  # Shrink

    def draw(self, screen):
        """Draw splash effect."""
        if not self.active:
            return

        for particle in self.particles:
            if particle["size"] > 0.5:
                color = (100, 150, 255)
                size = int(particle["size"])
                pygame.draw.circle(
                    screen, color, (int(particle["x"]), int(particle["y"])), size
                )


class PoolGame:
    """Pool/water balloon minigame scene."""

    # Game states
    STATE_READY = "ready"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"

    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.screen_width = scene_manager.screen_width
        self.screen_height = scene_manager.screen_height

        # Game state
        self.state = self.STATE_READY
        self.game_duration = 60.0  # 60 seconds
        self.time_remaining = self.game_duration
        self.start_time = None
        self.score = 0

        # High score tracking
        self.high_score_manager = HighScoreManager(scene_manager.save_manager)
        self.is_new_high_score = False
        self.score_submitted = False

        # Initialize player
        character_name = scene_manager.game_data.get("selected_character") or "Danger"
        self.player = PoolPlayer(
            self.screen_width // 2, self.screen_height - 100, character_name
        )

        # Projectiles
        self.projectiles: list[WaterBalloon] = []

        # Targets
        self.targets: list[PoolTarget] = []
        self.target_spawn_timer = 0
        self.target_spawn_interval = 3.0  # Spawn new target every 3 seconds
        self.max_targets = 8  # Maximum targets on screen

        # Effects
        self.splash_effects: list[SplashEffect] = []
        self.particle_effects: list[TargetDestroyEffect] = []

        # Power-ups
        self.powerups: list[PowerUp] = []
        self.active_powerups: list[ActivePowerUp] = []
        self.next_powerup_spawn = (
            self.game_duration - 8.0
        )  # First power-up after 8 seconds (52s remaining)
        self.powerup_spawn_interval = 12.0  # Spawn every 12 seconds
        self.max_powerups_on_field = 2  # Maximum power-ups on field at once

        # Power-up effects flags
        self.triple_shot_active = False
        self.rapid_fire_active = False
        self.homing_active = False
        self.original_reload_time = 0.5
        self.original_reload_duration = 2.0

        # Mouse aiming
        self.mouse_x = 0
        self.mouse_y = 0
        self.show_aim_line = False

        # Reload/cooldown system
        self.reload_time = 0.5  # Half second between shots
        self.time_since_last_shot = 0
        self.can_shoot = True
        self.ammo_capacity = 5
        self.current_ammo = self.ammo_capacity
        self.reload_duration = 2.0  # 2 seconds to reload all ammo
        self.is_reloading = False
        self.reload_progress = 0

        # UI fonts
        self.font = pygame.font.Font(None, FONT_SMALL)
        self.big_font = pygame.font.Font(None, FONT_LARGE)
        self.huge_font = pygame.font.Font(None, FONT_HUGE)

        # Pool visual elements
        self.create_pool_visual()

        # Scene-specific sounds
        self.pool_sounds = {
            'shot': get_sfx_path("pool/impact/pool_shot.mp3"),
            'hit': get_sfx_path("pool/impact/target_hit.mp3"),
            'bullseye': get_sfx_path("pool/impact/bullseye.mp3"),
            'miss': get_sfx_path("pool/impact/target_miss.mp3"),
            'powerup': get_sfx_path("pool/impact/powerup_collect.mp3"),
            'perfect': get_sfx_path("pool/impact/perfect_round.mp3")
        }

    def create_pool_visual(self):
        """Create visual elements for the pool scene."""
        # Pool area dimensions
        self.pool_rect = pygame.Rect(
            100, 100, self.screen_width - 200, self.screen_height - 250
        )

        # Water surface effect
        self.water_offset = 0

        # Create initial targets
        self.create_targets()

    def create_targets(self):
        """Create initial targets with variety."""
        self.targets.clear()

        # Create a few initial targets of different types
        initial_targets = [
            (DuckTarget, 400, 200),
            (BeachBallTarget, 600, 300),
            (DonutFloatTarget, 800, 250),
        ]

        for TargetClass, x, y in initial_targets:
            target = TargetClass(x, y)
            self.targets.append(target)

    def spawn_target(self):
        """Spawn a new random target."""
        if len(self.targets) >= self.max_targets:
            return

        # Random target type
        target_types = [DuckTarget, BeachBallTarget, DonutFloatTarget]
        weights = [0.4, 0.35, 0.25]  # Duck most common, donut least
        TargetClass = random.choices(target_types, weights=weights)[0]

        # Random spawn position at edges
        edge = random.choice(["top", "left", "right"])
        if edge == "top":
            x = random.randint(200, 1080)
            y = 150
        elif edge == "left":
            x = 200
            y = random.randint(200, 400)
        else:  # right
            x = 1080
            y = random.randint(200, 400)

        target = TargetClass(x, y)
        self.targets.append(target)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == self.STATE_READY:
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_ESCAPE:
                    return SCENE_HUB_WORLD

            elif self.state == self.STATE_PLAYING:
                if event.key == pygame.K_ESCAPE:
                    return SCENE_HUB_WORLD
                if event.key == pygame.K_r:
                    # Manual reload
                    if self.current_ammo < self.ammo_capacity and not self.is_reloading:
                        self.start_reload()

            elif self.state == self.STATE_GAME_OVER:
                if event.key == pygame.K_SPACE:
                    if self.is_new_high_score and not self.score_submitted:
                        # Go to name entry for new high score
                        return SCENE_NAME_ENTRY
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return SCENE_HUB_WORLD

        elif event.type == pygame.MOUSEMOTION:
            self.mouse_x, self.mouse_y = event.pos
            if self.state == self.STATE_PLAYING:
                self.show_aim_line = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == self.STATE_PLAYING and event.button == 1:  # Left click
                self.shoot_balloon()

        return None

    def start_game(self):
        """Start the game timer and transition to playing state."""
        self.state = self.STATE_PLAYING
        self.start_time = time.time()
        self.time_remaining = self.game_duration
        self.score = 0

    def reset_game(self):
        """Reset the game to ready state."""
        self.state = self.STATE_READY
        self.time_remaining = self.game_duration
        self.score = 0
        self.player.x = self.screen_width // 2
        self.projectiles.clear()
        self.splash_effects.clear()
        self.particle_effects.clear()  # Clear particle effects
        self.create_targets()  # Reset targets
        self.target_spawn_timer = 0  # Reset spawn timer
        self.current_ammo = self.ammo_capacity
        self.is_reloading = False
        self.can_shoot = True

        # Clear power-ups
        self.powerups.clear()
        for active in self.active_powerups:
            active.powerup.remove_effect(self)
        self.active_powerups.clear()

        # Reset high score tracking
        self.is_new_high_score = False
        self.score_submitted = False
        self.next_powerup_spawn = self.game_duration - 8.0  # Reset spawn timer

    def shoot_balloon(self):
        """Shoot a water balloon towards the mouse position."""
        # Check if we can shoot
        if not self.can_shoot or self.is_reloading or self.current_ammo <= 0:
            return

        if self.triple_shot_active:
            # Create three balloons in a spread pattern
            spread_angle = 15  # degrees
            for i in range(3):
                angle_offset = (i - 1) * spread_angle  # -15, 0, 15 degrees

                # Calculate offset target position
                dx = self.mouse_x - self.player.x
                dy = self.mouse_y - self.player.y
                distance = math.sqrt(dx**2 + dy**2)

                if distance > 0:
                    # Rotate the direction vector
                    angle = math.atan2(dy, dx) + math.radians(angle_offset)
                    target_x = self.player.x + math.cos(angle) * distance
                    target_y = self.player.y + math.sin(angle) * distance
                else:
                    target_x = self.mouse_x
                    target_y = self.mouse_y

                balloon = WaterBalloon(
                    self.player.x,
                    self.player.y - 20,
                    target_x,
                    target_y,
                    is_homing=self.homing_active,
                )
                self.projectiles.append(balloon)
        else:
            # Single balloon
            balloon = WaterBalloon(
                self.player.x,
                self.player.y - 20,
                self.mouse_x,
                self.mouse_y,
                is_homing=self.homing_active,
            )
            self.projectiles.append(balloon)

        # Play shot sound
        self.scene_manager.sound_manager.play_sfx(self.pool_sounds['shot'])

        # Update ammo and cooldown
        self.current_ammo -= 1
        self.can_shoot = False
        self.time_since_last_shot = 0

        # Start reloading if out of ammo
        if self.current_ammo <= 0:
            self.start_reload()

    def start_reload(self):
        """Start the reload process."""
        self.is_reloading = True
        self.reload_progress = 0
        self.can_shoot = False

    def spawn_powerup(self):
        """Spawn a random power-up at a random location."""
        # Random position within pool area (avoiding edges)
        x = random.randint(200, self.screen_width - 200)
        y = random.randint(200, 400)

        # Random power-up type
        powerup_types = [TripleShotPowerUp, RapidFirePowerUp, HomingPowerUp]
        PowerUpClass = random.choice(powerup_types)

        powerup = PowerUpClass(x, y)
        self.powerups.append(powerup)

    def collect_powerup(self, powerup: PowerUp):
        """Collect a power-up and apply its effect."""
        # Remove any existing power-up of the same type
        for active in self.active_powerups[:]:
            if isinstance(active.powerup, type(powerup)):
                active.powerup.remove_effect(self)
                self.active_powerups.remove(active)

        # Apply new power-up
        powerup.apply_effect(self)
        active = ActivePowerUp(powerup)
        self.active_powerups.append(active)

        # Play collection sound (if sound manager available)
        if hasattr(self.scene_manager, "sound_manager"):
            self.scene_manager.sound_manager.play_sfx(self.pool_sounds['powerup'])

    def update(self, dt: float):
        if self.state == self.STATE_PLAYING:
            # Update timer
            if self.start_time:
                elapsed = time.time() - self.start_time
                self.time_remaining = max(0, self.game_duration - elapsed)

                # Check for game over
                if self.time_remaining <= 0:
                    self.state = self.STATE_GAME_OVER
                    self._submit_high_score()

            # Update player
            self.player.update(dt)

            # Update reload/cooldown
            if self.is_reloading:
                self.reload_progress += dt
                if self.reload_progress >= self.reload_duration:
                    # Reload complete
                    self.is_reloading = False
                    self.current_ammo = self.ammo_capacity
                    self.can_shoot = True
                    self.reload_progress = 0
            elif not self.can_shoot:
                # Update shot cooldown
                self.time_since_last_shot += dt
                if self.time_since_last_shot >= self.reload_time:
                    self.can_shoot = True

            # Update projectiles
            for balloon in self.projectiles[
                :
            ]:  # Copy list to allow removal during iteration
                old_active = balloon.active
                balloon.update(dt, self.targets)  # Pass targets for homing

                if not balloon.active:
                    # Create splash if balloon just became inactive (hit water)
                    if old_active and balloon.y > 500:
                        splash = SplashEffect(balloon.x, balloon.y)
                        self.splash_effects.append(splash)
                    self.projectiles.remove(balloon)
                else:
                    # Check collisions with targets
                    for target in self.targets:
                        if target.check_collision(balloon):
                            self.score += target.get_point_value()
                            balloon.active = False

                            # Create splash effect
                            splash = SplashEffect(balloon.x, balloon.y)
                            self.splash_effects.append(splash)

                            # Create target destruction particles
                            target_type = (
                                "duck"
                                if isinstance(target, DuckTarget)
                                else "beachball"
                                if isinstance(target, BeachBallTarget)
                                else "donut"
                                if isinstance(target, DonutFloatTarget)
                                else "default"
                            )
                            particles = TargetDestroyEffect(
                                target.x, target.y, target.get_color(), target_type
                            )
                            self.particle_effects.append(particles)

                            # Play hit sound
                            if hasattr(self.scene_manager, "sound_manager"):
                                # Check if it's a bullseye (center hit)
                                hit_distance = math.sqrt((balloon.x - target.x)**2 + (balloon.y - target.y)**2)
                                is_bullseye = hit_distance < 20  # Within 20 pixels of center
                                
                                if is_bullseye:
                                    self.scene_manager.sound_manager.play_sfx(self.pool_sounds['bullseye'])
                                else:
                                    self.scene_manager.sound_manager.play_sfx(self.pool_sounds['hit'])
                            break

            # Update targets
            for target in self.targets[:]:  # Copy to allow removal
                target.update(dt)
                if not target.active:
                    self.targets.remove(target)

            # Spawn new targets periodically
            self.target_spawn_timer += dt
            if self.target_spawn_timer >= self.target_spawn_interval:
                self.spawn_target()
                self.target_spawn_timer = 0

            # Power-up spawning
            if (
                self.time_remaining <= self.next_powerup_spawn
                and len(self.powerups) < self.max_powerups_on_field
            ):
                self.spawn_powerup()
                self.next_powerup_spawn -= self.powerup_spawn_interval

            # Update power-ups
            for powerup in self.powerups[:]:
                powerup.update(dt)

                # Check collection
                if powerup.check_collection(self.player.x, self.player.y):
                    self.collect_powerup(powerup)
                    self.powerups.remove(powerup)

            # Update active power-ups
            for active in self.active_powerups[:]:
                if active.is_expired():
                    active.powerup.remove_effect(self)
                    self.active_powerups.remove(active)

            # Update splash effects
            for splash in self.splash_effects[:]:
                splash.update(dt)
                if not splash.active:
                    self.splash_effects.remove(splash)

            # Update particle effects
            for effect in self.particle_effects[:]:
                effect.update(dt)
                if not effect.active:
                    self.particle_effects.remove(effect)

        # Always update water animation
        self.water_offset += 50 * dt
        if self.water_offset > 20:
            self.water_offset -= 20

    def draw(self, screen):
        # Clear screen with sky color
        screen.fill((135, 206, 250))  # Light sky blue

        # Draw pool area
        self.draw_pool(screen)

        # Draw targets
        for target in self.targets:
            target.draw(screen)

        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(screen)

        # Draw projectiles
        for balloon in self.projectiles:
            balloon.draw(screen)

        # Draw splash effects
        for splash in self.splash_effects:
            splash.draw(screen)

        # Draw particle effects
        for effect in self.particle_effects:
            effect.draw(screen)

        # Draw aim line if playing
        if self.state == self.STATE_PLAYING and self.show_aim_line:
            self.draw_aim_line(screen)

        # Draw player
        self.player.draw(screen)

        # Draw UI based on state
        if self.state == self.STATE_READY:
            self.draw_ready_screen(screen)
        elif self.state == self.STATE_PLAYING:
            self.draw_game_ui(screen)
        elif self.state == self.STATE_GAME_OVER:
            self.draw_game_over_screen(screen)

    def draw_pool(self, screen):
        """Draw the pool area with water effect."""
        # Pool edge
        pygame.draw.rect(screen, (200, 200, 200), self.pool_rect, 5)

        # Water
        water_surface = pygame.Surface((self.pool_rect.width, self.pool_rect.height))
        water_surface.set_alpha(100)
        water_surface.fill(COLOR_BLUE)

        # Simple water wave effect
        for x in range(0, self.pool_rect.width, 40):
            wave_y = int(math.sin((x + self.water_offset) * 0.05) * 5)
            pygame.draw.line(
                water_surface,
                COLOR_WATER_SPLASH,
                (x, wave_y + 10),
                (x + 20, wave_y + 10),
                2,
            )

        screen.blit(water_surface, self.pool_rect)

    def draw_aim_line(self, screen):
        """Draw aiming line from player to mouse."""
        # Calculate angle and distance
        dx = self.mouse_x - self.player.x
        dy = self.mouse_y - self.player.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            # Draw dotted line
            steps = int(distance / 20)
            for i in range(0, steps, 2):
                t = i / steps
                x = self.player.x + dx * t
                y = self.player.y + dy * t
                pygame.draw.circle(screen, COLOR_WHITE, (int(x), int(y)), 3)
                pygame.draw.circle(screen, COLOR_BLACK, (int(x), int(y)), 3, 1)

    def draw_ready_screen(self, screen):
        """Draw the ready state UI."""
        # Title
        title_text = self.huge_font.render("POOL GAME", True, COLOR_BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(title_text, title_rect)

        # Instructions
        instructions = [
            "Shoot water balloons at targets!",
            "",
            "Use mouse to aim",
            "Click to shoot",
            "Press R to reload (5 shots)",
            "",
            "Press SPACE to start",
            "Press ESC to return to hub",
        ]

        draw_instructions(
            screen,
            instructions,
            self.font,
            self.screen_width // 2,
            UI_INSTRUCTION_START_Y,
            40,
            COLOR_BLACK,
        )

    def draw_game_ui(self, screen):
        """Draw the playing state UI."""
        # Timer
        timer_text = f"Time: {int(self.time_remaining)}"
        draw_text_with_background(
            screen,
            timer_text,
            self.big_font,
            (self.screen_width // 2, 50),
            COLOR_BLACK,
            COLOR_WHITE,
            COLOR_BLACK,
        )

        # Score
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, COLOR_BLACK)
        score_rect = score_surface.get_rect(topleft=(10, 10))
        screen.blit(score_surface, score_rect)

        # Controls reminder
        controls = self.font.render("ESC: Return to Hub", True, COLOR_BLACK)
        controls_rect = controls.get_rect(topright=(self.screen_width - 10, 10))
        screen.blit(controls, controls_rect)

        # Ammo display
        ammo_y = self.screen_height - 50
        ammo_x = self.screen_width // 2 - 100

        if self.is_reloading:
            # Show reload progress bar
            reload_text = self.font.render("RELOADING...", True, COLOR_RED)
            reload_rect = reload_text.get_rect(
                center=(self.screen_width // 2, ammo_y - 30)
            )
            screen.blit(reload_text, reload_rect)

            # Progress bar
            bar_width = 200
            bar_height = 20
            bar_x = self.screen_width // 2 - bar_width // 2
            bar_y = ammo_y - 10

            # Draw reload progress bar
            draw_progress_bar(
                screen,
                bar_x,
                bar_y,
                bar_width,
                bar_height,
                self.reload_progress / self.reload_duration,
                None,  # No background fill
                COLOR_GREEN,
                COLOR_BLACK,
                2,
            )
        else:
            # Show ammo count
            for i in range(self.ammo_capacity):
                balloon_x = ammo_x + i * 40
                if i < self.current_ammo:
                    pygame.draw.circle(screen, COLOR_BLUE, (balloon_x, ammo_y), 15)
                    pygame.draw.circle(
                        screen, COLOR_WHITE, (balloon_x - 3, ammo_y - 3), 5
                    )
                else:
                    pygame.draw.circle(
                        screen, (200, 200, 200), (balloon_x, ammo_y), 15, 2
                    )

            # Reload hint
            if self.current_ammo < self.ammo_capacity:
                hint = self.font.render("Press R to reload", True, COLOR_BLACK)
                hint_rect = hint.get_rect(center=(self.screen_width // 2, ammo_y + 30))
                screen.blit(hint, hint_rect)

        # Draw active power-ups
        if self.active_powerups:
            powerup_y = 100
            powerup_x = self.screen_width - 250

            # Background for power-up display
            bg_height = len(self.active_powerups) * 50 + 20
            bg_rect = pygame.Rect(powerup_x - 10, powerup_y - 10, 240, bg_height)
            pygame.draw.rect(screen, COLOR_WHITE, bg_rect)
            pygame.draw.rect(screen, COLOR_BLACK, bg_rect, 2)

            for i, active in enumerate(self.active_powerups):
                y = powerup_y + i * 50

                # Power-up icon
                icon_x = powerup_x + 20
                icon_y = y + 20
                pygame.draw.circle(screen, active.color, (icon_x, icon_y), 15)
                pygame.draw.circle(screen, COLOR_WHITE, (icon_x, icon_y), 12, 2)

                # Power-up name
                name_text = self.font.render(active.name, True, COLOR_BLACK)
                screen.blit(name_text, (icon_x + 30, icon_y - 10))

                # Timer bar
                bar_x = icon_x + 30
                bar_y = icon_y + 10
                bar_width = 150
                bar_height = 8

                # Background bar
                pygame.draw.rect(
                    screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height)
                )

                # Progress bar
                progress_width = int(bar_width * active.get_progress())
                bar_color = active.color

                # Flash when almost expired
                if active.get_time_remaining() < 2.0:
                    if int(active.get_time_remaining() * 4) % 2 == 0:
                        bar_color = COLOR_RED

                pygame.draw.rect(
                    screen, bar_color, (bar_x, bar_y, progress_width, bar_height)
                )

    def draw_game_over_screen(self, screen):
        """Draw the game over state UI."""
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = self.huge_font.render("TIME'S UP!", True, COLOR_WHITE)
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, 250))
        screen.blit(game_over_text, game_over_rect)

        # Score
        score_color = COLOR_GREEN
        score_prefix = "Final Score: "
        if self.is_new_high_score:
            score_color = (255, 215, 0)  # Gold color
            score_prefix = "NEW HIGH SCORE: "

        score_text = self.big_font.render(
            f"{score_prefix}{self.score}", True, score_color
        )
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 350))
        screen.blit(score_text, score_rect)

        # New high score celebration
        if self.is_new_high_score:
            celebration_text = self.font.render("🎉 AMAZING! 🎉", True, (255, 255, 0))
            celebration_rect = celebration_text.get_rect(
                center=(self.screen_width // 2, 390)
            )
            screen.blit(celebration_text, celebration_rect)

        # Options
        if self.is_new_high_score and not self.score_submitted:
            options = ["Press SPACE to enter name", "Press ESC to return to hub"]
        else:
            options = ["Press SPACE to play again", "Press ESC to return to hub"]

        y = 450
        for option in options:
            text = self.font.render(option, True, COLOR_WHITE)
            text_rect = text.get_rect(center=(self.screen_width // 2, y))
            screen.blit(text, text_rect)
            y += 40

    def _submit_high_score(self):
        """Check if current score would be a high score."""
        if self.score_submitted:
            return

        # Get current character and difficulty
        character_name = self.player.character_name.lower()
        difficulty = "normal"  # TODO: Add difficulty selection later

        # Check if this would be a high score
        self.is_new_high_score = self.high_score_manager.is_high_score(
            float(self.score), "pool", character_name, difficulty
        )

    def submit_final_score(self, player_name: str = None):
        """Actually submit the score to the high score system."""
        if self.score_submitted:
            return False

        self.score_submitted = True

        # Get current character and difficulty
        character_name = self.player.character_name.lower()
        difficulty = "normal"  # TODO: Add difficulty selection later

        # Use provided name or default to character name
        final_player_name = player_name or character_name.title()

        # Create score entry
        score_entry = ScoreEntry(
            player_name=final_player_name,
            score=float(self.score),
            character=character_name,
            game_mode="pool",
            difficulty=difficulty,
            date=datetime.now(),
            time_elapsed=self.game_duration - self.time_remaining,
        )

        # Submit score and return if it made the leaderboard
        return self.high_score_manager.submit_score(score_entry)

    def on_enter(self, previous_scene, data):
        """Called when entering this scene."""
        # Handle returning from name entry scene
        if previous_scene == "name_entry" and data and "player_name" in data:
            # Submit the score with the entered name
            self.submit_final_score(data["player_name"])
            # Keep current game state (showing game over screen)
            return

        # Reset to ready state when entering normally
        self.reset_game()
        self.create_targets()  # Ensure we have fresh targets

    def on_exit(self):
        """Called when leaving this scene."""
        # If going to name entry, pass score data
        if self.is_new_high_score and not self.score_submitted:
            return {
                "game_mode": "pool",
                "character": self.player.character_name.lower(),
                "difficulty": "normal",
                "score": self.score,
                "callback_scene": "pool_game",  # Return to pool after name entry
            }
        return {}
