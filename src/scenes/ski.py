import random
import time
from datetime import datetime

import pygame

from src.config.constants import (
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_SKY_BLUE,
    COLOR_SNOW_ALT,
    COLOR_SNOW_WHITE,
    COLOR_WHITE,
    FLASH_INVINCIBILITY_RATE,
    FONT_HUGE,
    FONT_LARGE,
    FONT_SMALL,
    GAME_DURATION,
    OVERLAY_GAME_OVER_ALPHA,
    PLAYER_COLLISION_HEIGHT,
    PLAYER_COLLISION_OFFSET,
    PLAYER_COLLISION_WIDTH,
    PLAYER_INVINCIBILITY_DURATION,
    PLAYER_SKI_DIAGONAL_SPEED,
    PLAYER_SKI_SPEED,
    SCENE_HUB_WORLD,
    SCENE_LEADERBOARD,
    SKI_CRASH_DURATION,
    SKI_DAD_OFFSET_X,
    SKI_MAX_LIVES,
    SKI_PLAYER_Y_OFFSET,
    SKI_SCROLL_SPEED,
    SKI_SNOW_PARTICLE_COUNT,
    SKI_SNOWFLAKE_POINTS,
    SPRITE_DISPLAY_SIZE,
    UI_BIG_TEXT_Y,
    UI_INSTRUCTION_LINE_HEIGHT,
    UI_INSTRUCTION_START_Y,
    UI_SCORE_PADDING,
    UI_TIMER_BORDER,
)
from src.entities.dad_ai import DadAI
from src.entities.snowflake import SnowflakeEffect
from src.scenes.slope_generator import SlopeGenerator
from src.ui.drawing_helpers import (
    draw_instructions,
    draw_lives,
    draw_text_with_background,
)
from src.utils.asset_paths import get_sfx_path
from src.utils.attack_character import AnimatedCharacter
from src.utils.high_score_manager import HighScoreManager, ScoreEntry


class SkiPlayer:
    def __init__(self, x: int, y: int, character_name: str):
        self.x = x
        self.y = y
        self.character_name = character_name

        # Movement
        self.speed = PLAYER_SKI_SPEED
        self.diagonal_speed = PLAYER_SKI_DIAGONAL_SPEED  # Slower when moving diagonally

        # Create animated character using new individual file system
        self.sprite = AnimatedCharacter(
            character_name.lower(), "ski", (SPRITE_DISPLAY_SIZE, SPRITE_DISPLAY_SIZE)
        )
        # Set to walk animation for skiing
        self.sprite.set_animation("walk", loop=True)

        # Collision rect - smaller than sprite for more forgiving collisions
        self.rect = pygame.Rect(
            x - PLAYER_COLLISION_OFFSET,
            y - PLAYER_COLLISION_OFFSET,
            PLAYER_COLLISION_WIDTH,
            PLAYER_COLLISION_HEIGHT,
        )

        # Crash state
        self.is_crashing = False
        self.crash_time = 0
        self.invincible = False
        self.invincible_time = 0

    def handle_input(self, keys, screen_width):
        # Only allow movement if not crashing
        if self.is_crashing:
            return

        # Horizontal movement
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed

        # Update position
        self.x += dx

        # Keep player on screen
        self.x = max(32, min(self.x, screen_width - 32))

        # Update rect
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def update(self, dt: float):
        # Update crash state
        if self.is_crashing:
            self.crash_time -= dt
            if self.crash_time <= 0:
                self.is_crashing = False
                self.invincible = True
                self.invincible_time = PLAYER_INVINCIBILITY_DURATION

        # Update invincibility
        if self.invincible:
            self.invincible_time -= dt
            if self.invincible_time <= 0:
                self.invincible = False

        # Update animation
        self.sprite.update()

    def crash(self):
        """Trigger crash state."""
        if not self.invincible and not self.is_crashing:
            self.is_crashing = True
            self.crash_time = SKI_CRASH_DURATION
            return True
        return False

    def draw(self, screen):
        sprite = self.sprite.get_current_sprite()

        # Flash during invincibility
        if (
            self.invincible
            and int(self.invincible_time * FLASH_INVINCIBILITY_RATE) % 2 == 0
        ):
            # Make sprite semi-transparent
            sprite = sprite.copy()
            sprite.set_alpha(128)

        # Tint red during crash
        if self.is_crashing:
            sprite = sprite.copy()
            sprite.fill((255, 100, 100), special_flags=pygame.BLEND_MULT)

        sprite_rect = sprite.get_rect(center=(self.x, self.y))
        screen.blit(sprite, sprite_rect)


class SkiGame:
    """Ski minigame scene with 60-second timed runs."""

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
        self.game_duration = GAME_DURATION
        self.time_remaining = self.game_duration
        self.start_time = None

        # Initialize player
        character_name = scene_manager.game_data.get("selected_character") or "Danger"
        self.player = SkiPlayer(
            self.screen_width // 2,
            self.screen_height - SKI_PLAYER_Y_OFFSET,
            character_name,
        )

        # Initialize Dad AI
        self.dad = DadAI(
            self.screen_width // 2
            - SKI_DAD_OFFSET_X,  # Start slightly to the left of player
            self.screen_height - SKI_PLAYER_Y_OFFSET,
            self.screen_width,
        )

        # Lives system
        self.lives = SKI_MAX_LIVES
        self.max_lives = SKI_MAX_LIVES

        # Score system
        self.score = 0
        self.snowflakes_collected = 0
        self.points_per_snowflake = SKI_SNOWFLAKE_POINTS

        # High score tracking
        self.high_score_manager = HighScoreManager()
        self.is_new_high_score = False
        self.final_time = 0.0
        self.difficulty = "normal"  # Could be set based on game settings

        # Visual elements
        self.scroll_speed = SKI_SCROLL_SPEED  # Base scrolling speed
        self.scroll_offset = 0

        # Effects
        self.active_effects = []

        # UI fonts
        self.font = pygame.font.Font(None, FONT_SMALL)
        self.big_font = pygame.font.Font(None, FONT_LARGE)
        self.huge_font = pygame.font.Font(None, FONT_HUGE)

        # Create slope generator
        self.slope_generator = SlopeGenerator(self.screen_width, self.screen_height)

        # Sound manager from scene manager
        self.sound_manager = scene_manager.sound_manager

        # Scene-specific sounds
        self.ski_sounds = {
            'swoosh': get_sfx_path("ski/movement/ski_swoosh.mp3"),
            'turn': get_sfx_path("ski/movement/ski_turn.mp3"),
            'snow_spray': get_sfx_path("ski/movement/snow_spray.mp3"),
            'tree_hit': get_sfx_path("ski/movement/tree_hit.mp3"),
            'checkpoint': get_sfx_path("ski/movement/checkpoint.mp3"),
            'speed_boost': get_sfx_path("ski/movement/speed_boost.mp3"),
            'finish_line': get_sfx_path("ski/movement/finish_line.mp3")
        }

        # Create simple snow texture for background
        self.create_snow_texture()

    def create_snow_texture(self):
        """Create a simple snow texture for the background."""
        self.snow_surface = pygame.Surface((self.screen_width, self.screen_height * 2))
        self.snow_surface.fill(COLOR_WHITE)

        # Add some snow texture details
        for _ in range(SKI_SNOW_PARTICLE_COUNT):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height * 2)
            radius = random.randint(1, 3)
            color = COLOR_SNOW_WHITE if random.random() > 0.5 else COLOR_SNOW_ALT
            pygame.draw.circle(self.snow_surface, color, (x, y), radius)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == self.STATE_READY:
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_ESCAPE:
                    return SCENE_HUB_WORLD

            elif self.state == self.STATE_PLAYING:
                if event.key == pygame.K_ESCAPE:
                    # Return to hub (could add pause later)
                    return SCENE_HUB_WORLD

            elif self.state == self.STATE_GAME_OVER:
                if event.key == pygame.K_SPACE:
                    # Restart
                    self.reset_game()
                elif event.key == pygame.K_l:
                    # View leaderboard
                    return SCENE_LEADERBOARD
                elif event.key == pygame.K_ESCAPE:
                    return SCENE_HUB_WORLD

        return None

    def start_game(self):
        """Start the game timer and transition to playing state."""
        self.state = self.STATE_PLAYING
        self.start_time = time.time()
        self.time_remaining = self.game_duration

    def reset_game(self):
        """Reset the game to ready state."""
        self.state = self.STATE_READY
        self.time_remaining = self.game_duration
        self.scroll_offset = 0
        self.player.x = self.screen_width // 2
        self.player.is_crashing = False
        self.player.invincible = False
        self.player.invincible_time = 0
        self.lives = self.max_lives
        self.score = 0
        self.snowflakes_collected = 0
        self.is_new_high_score = False
        self.active_effects.clear()
        self.slope_generator.reset()

        # Reset Dad position
        self.dad.x = self.screen_width // 2 - SKI_DAD_OFFSET_X
        self.dad.is_celebrating = False

    def update(self, dt: float):
        if self.state == self.STATE_PLAYING:
            # Update timer
            elapsed = 0
            if self.start_time:
                elapsed = time.time() - self.start_time
                self.time_remaining = max(0, self.game_duration - elapsed)

                # Check for game over
                if self.time_remaining <= 0:
                    self.state = self.STATE_GAME_OVER
                    self.final_time = elapsed
                    # Make Dad celebrate
                    self.dad.start_celebration()
                    # Submit high score
                    self._submit_high_score()

            # Handle player input
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys, self.screen_width)

            # Update player
            self.player.update(dt)

            # Update Dad AI
            obstacles = self.slope_generator.get_obstacles()
            self.dad.update(dt, self.player.x, obstacles)

            # Check for collisions
            self.check_collisions()

            # Check for snowflake collection
            self.check_snowflake_collection()

            # Update scrolling
            self.scroll_offset += self.scroll_speed * dt
            if self.scroll_offset >= self.screen_height:
                self.scroll_offset -= self.screen_height

            # Update slope generator
            self.slope_generator.update(self.scroll_speed, dt, elapsed)

            # Update effects
            self.update_effects(dt)

    def check_collisions(self):
        """Check for collisions between player and obstacles."""
        obstacles = self.slope_generator.get_obstacles()

        for obstacle in obstacles:
            if self.player.rect.colliderect(obstacle.rect):
                # Try to crash the player
                if self.player.crash():
                    self.lives -= 1

                    # Play crash sound (if available)
                    try:
                        self.sound_manager.play_sfx(self.ski_sounds['tree_hit'])
                    except Exception:
                        pass  # Sound file not available yet

                    # Check for game over
                    if self.lives <= 0:
                        self.state = self.STATE_GAME_OVER
                        self.final_time = (
                            time.time() - self.start_time if self.start_time else 0
                        )
                        # Submit high score
                        self._submit_high_score()
                    break

    def check_snowflake_collection(self):
        """Check for snowflake collection."""
        snowflake_pool = self.slope_generator.get_snowflake_pool()
        collected_snowflakes = snowflake_pool.check_collection(self.player.rect)

        for snowflake in collected_snowflakes:
            # Update score
            self.score += self.points_per_snowflake
            self.snowflakes_collected += 1

            # Create sparkle effect
            effect = SnowflakeEffect(snowflake.rect.centerx, snowflake.rect.centery)
            self.active_effects.append(effect)

            # Play collection sound
            try:
                self.sound_manager.play_sfx(
                    self.ski_sounds['speed_boost'], volume=0.5
                )
            except Exception:
                pass  # Sound file not available yet

            # Despawn collected snowflake
            snowflake_pool.despawn_snowflake(snowflake)

    def update_effects(self, dt: float):
        """Update all active effects."""
        for effect in self.active_effects[:]:
            if not effect.update(dt):
                self.active_effects.remove(effect)

    def draw(self, screen):
        # Clear screen with sky color
        screen.fill(COLOR_SKY_BLUE)

        # Draw scrolling slope
        self.draw_slope(screen)

        # Draw Dad (behind player)
        self.dad.draw(screen)

        # Draw player
        self.player.draw(screen)

        # Draw effects
        for effect in self.active_effects:
            effect.draw(screen)

        # Draw UI based on state
        if self.state == self.STATE_READY:
            self.draw_ready_screen(screen)
        elif self.state == self.STATE_PLAYING:
            self.draw_game_ui(screen)
        elif self.state == self.STATE_GAME_OVER:
            self.draw_game_over_screen(screen)

    def draw_slope(self, screen):
        """Draw the scrolling slope effect."""
        # Draw snow texture background
        y_offset = int(self.scroll_offset)
        screen.blit(self.snow_surface, (0, y_offset - self.screen_height))
        screen.blit(self.snow_surface, (0, y_offset - self.screen_height * 2))

        # Draw obstacles
        self.slope_generator.draw(screen)

    def draw_ready_screen(self, screen):
        """Draw the ready state UI."""
        # Title
        title_text = self.huge_font.render("SKI GAME", True, COLOR_BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, UI_BIG_TEXT_Y))
        screen.blit(title_text, title_rect)

        # Instructions
        instructions = [
            "Race down the mountain for 60 seconds!",
            "Dad will follow you on his snowboard!",
            "",
            "Arrow Keys or A/D to move",
            "Press SPACE to start",
            "Press ESC to return to hub",
        ]

        draw_instructions(
            screen,
            instructions,
            self.font,
            self.screen_width // 2,
            UI_INSTRUCTION_START_Y,
            UI_INSTRUCTION_LINE_HEIGHT,
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

        # Score display
        self.draw_score(screen)

        # Lives display
        self.draw_lives(screen)

        # Controls reminder
        controls = self.font.render("ESC: Return to Hub", True, COLOR_BLACK)
        screen.blit(controls, (10, 10))

    def draw_lives(self, screen):
        """Draw the lives indicator."""
        draw_lives(screen, self.lives, self.max_lives)

    def draw_score(self, screen):
        """Draw the score display."""
        # Score text
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, COLOR_BLACK)
        score_rect = score_surface.get_rect(left=20, top=50)

        # Score background
        bg_rect = score_rect.inflate(UI_SCORE_PADDING, UI_TIMER_BORDER)
        pygame.draw.rect(screen, COLOR_WHITE, bg_rect)
        pygame.draw.rect(screen, COLOR_BLACK, bg_rect, 2)

        screen.blit(score_surface, score_rect)

        # Snowflake counter
        snowflake_text = f"❄ {self.snowflakes_collected}"
        snowflake_surface = self.font.render(snowflake_text, True, COLOR_BLUE)
        snowflake_rect = snowflake_surface.get_rect(left=20, top=100)

        # Snowflake background
        bg_rect = snowflake_rect.inflate(UI_SCORE_PADDING, UI_TIMER_BORDER)
        pygame.draw.rect(screen, COLOR_WHITE, bg_rect)
        pygame.draw.rect(screen, COLOR_BLUE, bg_rect, 2)

        screen.blit(snowflake_surface, snowflake_rect)

    def draw_game_over_screen(self, screen):
        """Draw the game over state UI."""
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(OVERLAY_GAME_OVER_ALPHA)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))

        # Game over text based on reason
        if self.lives <= 0:
            game_over_text = self.huge_font.render("CRASHED OUT!", True, COLOR_RED)
            score_msg = self.big_font.render(
                "Try to avoid the obstacles!", True, COLOR_WHITE
            )
        else:
            game_over_text = self.huge_font.render("TIME'S UP!", True, COLOR_WHITE)
            score_msg = self.big_font.render(
                f"Final Score: {self.score}", True, COLOR_GREEN
            )

        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, 250))
        screen.blit(game_over_text, game_over_rect)

        # Score/message
        score_rect = score_msg.get_rect(center=(self.screen_width // 2, 350))
        screen.blit(score_msg, score_rect)

        # Show snowflakes collected
        snowflake_text = self.font.render(
            f"Snowflakes Collected: {self.snowflakes_collected}", True, COLOR_BLUE
        )
        snowflake_rect = snowflake_text.get_rect(center=(self.screen_width // 2, 400))
        screen.blit(snowflake_text, snowflake_rect)

        # Show if new high score
        if self.is_new_high_score:
            high_score_text = self.big_font.render("NEW HIGH SCORE!", True, COLOR_GREEN)
            high_score_rect = high_score_text.get_rect(
                center=(self.screen_width // 2, 440)
            )
            screen.blit(high_score_text, high_score_rect)
            y_start = 490
        else:
            y_start = 470

        # Options
        options = [
            "Press SPACE to play again",
            "Press L to view leaderboard",
            "Press ESC to return to hub",
        ]

        draw_instructions(
            screen,
            options,
            self.font,
            self.screen_width // 2,
            y_start,
            35,
            COLOR_WHITE,
        )

    def on_enter(self, previous_scene, data):
        """Called when entering this scene."""
        # Reset to ready state when entering
        self.reset_game()

    def on_exit(self):
        """Called when leaving this scene."""
        return {}

    def _submit_high_score(self):
        """Submit the current score as a high score."""
        # For ski game, the score is the time taken (lower is better)
        # Only submit if the game was completed (not crashed out)
        if self.lives > 0 and self.final_time > 0:
            character_name = self.scene_manager.game_data.get(
                "selected_character", "Danger"
            )

            # Create score entry
            score_entry = ScoreEntry(
                player_name=character_name,  # Could prompt for player name
                score=self.final_time,
                character=character_name.lower(),
                game_mode="ski",
                difficulty=self.difficulty,
                date=datetime.now(),
                time_elapsed=self.final_time,
            )

            # Submit and check if it's a high score
            self.is_new_high_score = self.high_score_manager.submit_score(score_entry)
