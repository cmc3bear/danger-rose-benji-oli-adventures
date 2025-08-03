import pygame

from src.config.constants import (
    COLOR_BLACK,
    COLOR_BUILDING_DARK,
    COLOR_GOLD,
    COLOR_NIGHT_PURPLE,
    COLOR_NIGHT_SKY,
    COLOR_PLACEHOLDER,
    COLOR_RED,
    COLOR_STREET_GRAY,
    COLOR_STREET_LINE,
    COLOR_WHITE,
    FLASH_HIT_RATE,
    FLASH_INVINCIBILITY_RATE,
    FONT_LARGE,
    FONT_SMALL,
    OVERLAY_GAME_OVER_ALPHA,
    OVERLAY_PAUSE_ALPHA,
    PLAYER_ATTACK_COOLDOWN,
    PLAYER_HIT_FLASH_DURATION,
    PLAYER_INVINCIBILITY_DURATION,
    PLAYER_VEGAS_COLLISION_HEIGHT,
    PLAYER_VEGAS_COLLISION_WIDTH,
    PLAYER_VEGAS_GRAVITY,
    PLAYER_VEGAS_JUMP_POWER,
    PLAYER_VEGAS_MAX_FALL_SPEED,
    SCENE_HUB_WORLD,
    SPRITE_DISPLAY_SIZE,
    VEGAS_BOSS_ARENA_OFFSET,
    VEGAS_BOSS_ATTACK_RANGE,
    VEGAS_BOSS_DAMAGE,
    VEGAS_BOSS_START_Y,
    VEGAS_BUILDING_HEIGHTS,
    VEGAS_BUILDING_SPACING,
    VEGAS_BUILDING_WIDTHS,
    VEGAS_FAR_BG_PARALLAX,
    VEGAS_GROUND_OFFSET,
    VEGAS_LEVEL_WIDTH,
    VEGAS_NEAR_BG_PARALLAX,
    VEGAS_STAR_COUNT,
    VEGAS_VICTORY_HEALTH_BONUS,
    VEGAS_VICTORY_SCORE_BASE,
)
from src.entities.vegas_boss import BossPhase, VegasBoss
from src.managers.sound_manager import SoundManager
from src.utils.asset_paths import get_vegas_bg
from src.utils.attack_character import AnimatedCharacter
from src.utils.sprite_loader import load_image


class Camera:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def apply(self, rect):
        return rect.move(-self.x, -self.y)

    def update(self, target_rect, level_width):
        # Center camera on target
        self.x = target_rect.centerx - self.width // 2

        # Keep camera within level bounds
        self.x = max(0, min(self.x, level_width - self.width))

    def apply_to_pos(self, x, y):
        return x - self.x, y - self.y


class Player:
    def __init__(self, x: int, y: int, character_name: str):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = True
        self.character_name = character_name

        # Player physics constants
        self.speed = 5
        self.jump_power = PLAYER_VEGAS_JUMP_POWER
        self.gravity = PLAYER_VEGAS_GRAVITY
        self.max_fall_speed = PLAYER_VEGAS_MAX_FALL_SPEED

        # Create animated character using new individual file system
        self.sprite = AnimatedCharacter(
            character_name.lower(), "vegas", (SPRITE_DISPLAY_SIZE, SPRITE_DISPLAY_SIZE)
        )
        # Set to idle animation by default
        self.sprite.set_animation("idle", loop=True)
        self.facing_right = True

        # Collision rect (smaller than sprite for better feel)
        self.rect = pygame.Rect(
            x, y, PLAYER_VEGAS_COLLISION_WIDTH, PLAYER_VEGAS_COLLISION_HEIGHT
        )

        # Player state
        self.health = 3  # 3 hits
        self.invulnerable = False
        self.invuln_timer = 0
        self.hit_flash_timer = 0
        self.attack_cooldown = 0

    def handle_input(self, keys):
        # Horizontal movement
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.facing_right = True

        # Jumping
        if (
            keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        ) and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False
            self.sprite.set_animation("jump", loop=False)

    def update(self, dt: float, ground_y: int):
        # Apply gravity
        if not self.on_ground:
            self.vy += self.gravity
            self.vy = min(self.vy, self.max_fall_speed)

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Ground collision (simple for now)
        if self.y + self.rect.height >= ground_y:
            self.y = ground_y - self.rect.height
            self.vy = 0
            self.on_ground = True

        # Update rect position
        self.rect.x = self.x
        self.rect.y = self.y

        # Update animation state
        if self.on_ground:
            if abs(self.vx) > 0:
                self.sprite.set_animation("walk", loop=True)
            else:
                self.sprite.set_animation("idle", loop=True)

        # Update animation
        self.sprite.update()

        # Update invulnerability
        if self.invulnerable:
            self.invuln_timer -= dt
            if self.invuln_timer <= 0:
                self.invulnerable = False

        # Update hit flash
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def draw(self, screen, camera):
        sprite = self.sprite.get_current_sprite()

        # Flip sprite if facing left
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)

        screen_x, screen_y = camera.apply_to_pos(self.x, self.y)

        # Apply flash effect when hit
        if (
            self.hit_flash_timer > 0
            and int(self.hit_flash_timer * FLASH_HIT_RATE) % 2 == 0
        ):
            # Flash white
            flash_sprite = sprite.copy()
            flash_sprite.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
            sprite = flash_sprite

        # Blink when invulnerable
        if (
            self.invulnerable
            and int(self.invuln_timer * FLASH_INVINCIBILITY_RATE) % 2 == 0
        ):
            return  # Don't draw every other frame

        # Center sprite on player rect
        sprite_rect = sprite.get_rect(
            center=(screen_x + self.rect.width // 2, screen_y + self.rect.height // 2)
        )
        screen.blit(sprite, sprite_rect)

    def take_damage(self):
        """Apply damage to player."""
        if not self.invulnerable and self.health > 0:
            self.health -= 1
            self.invulnerable = True
            self.invuln_timer = PLAYER_INVINCIBILITY_DURATION
            self.hit_flash_timer = PLAYER_HIT_FLASH_DURATION

            # Play hurt sound
            sound_manager = SoundManager()
            sound_manager.play_sfx("assets/audio/sfx/player_hurt.wav")


class VegasGame:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.screen_width = scene_manager.screen_width
        self.screen_height = scene_manager.screen_height

        # Level dimensions
        self.level_width = VEGAS_LEVEL_WIDTH  # Extended level width for side-scrolling
        self.ground_y = self.screen_height - VEGAS_GROUND_OFFSET

        # Initialize camera
        self.camera = Camera(self.screen_width, self.screen_height)

        # Initialize player
        character_name = scene_manager.game_data.get("selected_character") or "Danger"
        self.player = Player(100, self.ground_y - VEGAS_GROUND_OFFSET, character_name)

        # Background layers for parallax
        self.init_backgrounds()

        # UI elements
        self.font = pygame.font.Font(None, FONT_SMALL)
        self.big_font = pygame.font.Font(None, FONT_LARGE)

        # Game state
        self.reached_boss = False
        self.boss_fight_started = False
        self.paused = False
        self.game_over = False
        self.victory = False

        # Boss
        self.boss = None
        self.boss_arena_x = (
            self.level_width - VEGAS_BOSS_ARENA_OFFSET
        )  # Boss arena center

        # Sound manager
        self.sound_manager = SoundManager()

        # Scene-specific sounds
        self.vegas_sounds = {
            'coin': "assets/audio/sfx/vegas/casino/coin_collect.mp3",
            'slot': "assets/audio/sfx/vegas/casino/slot_machine.mp3",
            'dice': "assets/audio/sfx/vegas/casino/dice_roll.mp3",
            'card': "assets/audio/sfx/vegas/casino/card_flip.mp3",
            'jackpot': "assets/audio/sfx/vegas/casino/jackpot.mp3",
            'boss_appear': "assets/audio/sfx/vegas/casino/boss_appear.mp3",
            'special': "assets/audio/sfx/vegas/casino/special_attack.mp3"
        }

        # Start Vegas theme music
        vegas_music = "assets/audio/music/vegas_theme.ogg"
        self.sound_manager.play_music(vegas_music, fade_ms=1000)

    def init_backgrounds(self):
        # Try to load Vegas background, use placeholder if not found
        bg_image = load_image(get_vegas_bg(), (self.screen_width, self.screen_height))

        # Check if it's a placeholder (magenta color)
        if bg_image.get_at((0, 0))[:3] == COLOR_PLACEHOLDER:
            # Create custom backgrounds
            self.bg_far = pygame.Surface((self.screen_width, self.screen_height))
            self.bg_far.fill(COLOR_NIGHT_SKY)  # Dark purple night sky

            # Add some "stars" to the far background
            import random

            for _ in range(VEGAS_STAR_COUNT):
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)
                pygame.draw.circle(self.bg_far, (255, 255, 255), (x, y), 1)

            self.bg_near = pygame.Surface((self.screen_width, self.screen_height))
            self.bg_near.fill(COLOR_NIGHT_PURPLE)  # Lighter purple for buildings

            # Add simple building silhouettes
            building_heights = VEGAS_BUILDING_HEIGHTS
            x = 0
            for i, height in enumerate(building_heights):
                width = VEGAS_BUILDING_WIDTHS[i]
                pygame.draw.rect(
                    self.bg_near,
                    COLOR_BUILDING_DARK,
                    (x, self.screen_height - height, width, height),
                )
                x += width + VEGAS_BUILDING_SPACING
        else:
            self.bg_far = bg_image
            self.bg_near = bg_image.copy()

        # Ground/street layer
        self.ground_surface = pygame.Surface((self.level_width, 100))
        self.ground_surface.fill(COLOR_STREET_GRAY)  # Dark gray street

        # Add some street lines
        for x in range(0, self.level_width, 200):
            pygame.draw.rect(self.ground_surface, COLOR_STREET_LINE, (x, 45, 100, 10))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused

            # Return to hub on Q
            if event.key == pygame.K_q:
                # Stop music when leaving
                self.sound_manager.stop_music(fade_ms=500)
                return SCENE_HUB_WORLD

        return None

    def update(self, dt: float):
        if self.paused or self.game_over:
            return

        # Handle input
        keys = pygame.key.get_pressed()

        # Only allow movement if not in boss fight or boss is defeated
        if not self.boss_fight_started or (
            self.boss and self.boss.phase == BossPhase.DEFEATED
        ):
            self.player.handle_input(keys)

        # Update player
        self.player.update(dt, self.ground_y)

        # Update camera to follow player (lock during boss fight)
        if not self.boss_fight_started:
            self.camera.update(self.player.rect, self.level_width)

        # Check if reached boss arena
        if self.player.x >= self.boss_arena_x and not self.reached_boss:
            self.reached_boss = True
            self.start_boss_fight()

        # Update boss fight
        if self.boss:
            self.boss.update(dt, self.player.x, self.player.y)

            # Check projectile collisions
            if not self.player.invulnerable:
                for projectile in self.boss.projectiles:
                    if projectile.active and self.player.rect.colliderect(
                        projectile.rect
                    ):
                        self.player.take_damage()
                        projectile.active = False

                        if self.player.health <= 0:
                            self.game_over = True

            # Check boss defeat
            if self.boss.phase == BossPhase.DEFEATED and self.boss.y > 800:
                self.victory = True
                self.game_over = True

        # Handle player attack on boss (spacebar during boss fight)
        if (
            self.boss_fight_started
            and self.boss
            and keys[pygame.K_SPACE]
            and self.player.attack_cooldown <= 0
        ):
            # Simple attack: damage boss if close enough
            dx = abs(self.player.x - self.boss.x)
            dy = abs(self.player.y - self.boss.y)
            if (
                dx < VEGAS_BOSS_ATTACK_RANGE and dy < VEGAS_BOSS_ATTACK_RANGE
            ):  # Close range attack
                self.boss.take_damage(VEGAS_BOSS_DAMAGE)  # Small damage per hit
                self.player.attack_cooldown = PLAYER_ATTACK_COOLDOWN
                # Play attack sound
                self.sound_manager.play_sfx(self.vegas_sounds['special'])

    def start_boss_fight(self):
        """Initialize the boss fight."""
        self.boss_fight_started = True

        # Create boss
        self.boss = VegasBoss(self.boss_arena_x, VEGAS_BOSS_START_Y)
        
        # Play boss appear sound
        self.sound_manager.play_sfx(self.vegas_sounds['boss_appear'])

        # Lock camera on boss arena
        self.camera.x = self.boss_arena_x - self.screen_width // 2

        # Play boss music (could use a boss theme here, but we'll intensify Vegas theme)
        # Duck the audio briefly for dramatic effect
        self.sound_manager.duck_audio(0.3, 500)
        pygame.time.wait(500)
        self.sound_manager.restore_audio_levels()

    def draw(self, screen):
        # Clear screen
        screen.fill((10, 5, 20))  # Very dark purple

        # Draw parallax backgrounds
        # Far background (moves slower)
        far_offset = -self.camera.x * VEGAS_FAR_BG_PARALLAX
        screen.blit(self.bg_far, (far_offset % self.screen_width, 0))
        screen.blit(
            self.bg_far, ((far_offset % self.screen_width) - self.screen_width, 0)
        )

        # Near background (moves medium speed)
        near_offset = -self.camera.x * VEGAS_NEAR_BG_PARALLAX
        screen.blit(self.bg_near, (near_offset % self.screen_width, 0))
        screen.blit(
            self.bg_near, ((near_offset % self.screen_width) - self.screen_width, 0)
        )

        # Draw ground
        ground_rect = self.ground_surface.get_rect(topleft=(0, self.ground_y))
        screen.blit(self.ground_surface, self.camera.apply(ground_rect))

        # Draw player
        self.player.draw(screen, self.camera)

        # Draw boss
        if self.boss:
            self.boss.draw(screen, self.camera.x)

        # Draw UI
        self.draw_ui(screen)

        # Draw boss health bar
        if (
            self.boss_fight_started
            and self.boss
            and self.boss.phase != BossPhase.DEFEATED
        ):
            self.boss.draw_health_bar(screen, self.screen_width // 2 - 200, 50)

            # Draw attack indicator if in range
            dx = abs(self.player.x - self.boss.x)
            dy = abs(self.player.y - self.boss.y)
            if (
                dx < VEGAS_BOSS_ATTACK_RANGE
                and dy < VEGAS_BOSS_ATTACK_RANGE
                and self.player.attack_cooldown <= 0
            ):
                # Draw "Press SPACE to attack!" text
                attack_text = self.font.render(
                    "Press SPACE to attack!", True, COLOR_WHITE
                )
                attack_rect = attack_text.get_rect(center=(self.screen_width // 2, 150))
                screen.blit(attack_text, attack_rect)

        # Draw pause overlay
        if self.paused:
            self.draw_pause_overlay(screen)

        # Draw boss arena reached message (only if boss not started)
        if self.reached_boss and not self.boss_fight_started:
            self.draw_boss_message(screen)

        # Draw game over screen
        if self.game_over:
            self.draw_game_over_screen(screen)

    def draw_ui(self, screen):
        # Instructions
        instructions = [
            "Arrow Keys/WASD: Move",
            "Space/Up/W: Jump" + (" / Attack" if self.boss_fight_started else ""),
            "ESC: Pause",
            "Q: Return to Hub",
        ]

        y = 10
        for instruction in instructions:
            text = self.font.render(instruction, True, COLOR_WHITE)
            screen.blit(text, (10, y))
            y += 30

        # Player health
        health_text = "Health: "
        health_surface = self.font.render(health_text, True, COLOR_WHITE)
        screen.blit(health_surface, (10, y))

        # Draw hearts for health
        heart_x = 100
        for i in range(3):
            color = COLOR_RED if i < self.player.health else (50, 50, 50)
            # Simple heart shape
            pygame.draw.circle(screen, color, (heart_x, y + 10), 8)
            pygame.draw.circle(screen, color, (heart_x + 12, y + 10), 8)
            pygame.draw.polygon(
                screen,
                color,
                [(heart_x - 8, y + 12), (heart_x + 20, y + 12), (heart_x + 6, y + 25)],
            )
            heart_x += 30

        # Progress indicator (only if not in boss fight)
        if not self.boss_fight_started:
            progress = min(self.player.x / self.level_width, 1.0)
            progress_text = self.font.render(
                f"Progress: {int(progress * 100)}%", True, COLOR_WHITE
            )
            screen.blit(progress_text, (self.screen_width - 200, 10))

    def draw_pause_overlay(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(OVERLAY_PAUSE_ALPHA)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))

        # Pause text
        pause_text = self.big_font.render("PAUSED", True, COLOR_WHITE)
        pause_rect = pause_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2)
        )
        screen.blit(pause_text, pause_rect)

    def draw_boss_message(self, screen):
        boss_text = self.big_font.render("Boss Arena Reached!", True, (255, 100, 100))
        boss_rect = boss_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2)
        )
        screen.blit(boss_text, boss_rect)

        sub_text = self.font.render("Prepare for battle!", True, COLOR_WHITE)
        sub_rect = sub_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 50)
        )
        screen.blit(sub_text, sub_rect)

    def draw_game_over_screen(self, screen):
        """Draw game over or victory screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(OVERLAY_GAME_OVER_ALPHA)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))

        if self.victory:
            # Victory screen
            title_text = self.big_font.render("VICTORY!", True, COLOR_GOLD)  # Gold
            title_rect = title_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 - 50)
            )
            screen.blit(title_text, title_rect)

            sub_text = self.font.render(
                "You defeated the Vegas Sphere!", True, COLOR_WHITE
            )
            sub_rect = sub_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2)
            )
            screen.blit(sub_text, sub_rect)

            # Score
            score = VEGAS_VICTORY_SCORE_BASE + (
                self.player.health * VEGAS_VICTORY_HEALTH_BONUS
            )  # Bonus for remaining health
            score_text = self.font.render(f"Score: {score}", True, COLOR_WHITE)
            score_rect = score_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 + 40)
            )
            screen.blit(score_text, score_rect)
        else:
            # Game over screen
            title_text = self.big_font.render("GAME OVER", True, COLOR_RED)
            title_rect = title_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 - 50)
            )
            screen.blit(title_text, title_rect)

            sub_text = self.font.render(
                "The Vegas Sphere was too powerful!", True, COLOR_WHITE
            )
            sub_rect = sub_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2)
            )
            screen.blit(sub_text, sub_rect)

        # Instructions
        instruction_text = self.font.render(
            "Press Q to return to Hub World", True, COLOR_WHITE
        )
        instruction_rect = instruction_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 100)
        )
        screen.blit(instruction_text, instruction_rect)
