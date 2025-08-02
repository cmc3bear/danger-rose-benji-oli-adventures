"""Unit tests to verify the refactored constants are properly defined."""

from src.config.constants import (
    COLOR_BOSS_HEALTH,
    COLOR_BUILDING_DARK,
    COLOR_GOLD,
    COLOR_NIGHT_PURPLE,
    COLOR_NIGHT_SKY,
    COLOR_OVERLAY_GRAY,
    COLOR_PLACEHOLDER,
    # Colors
    COLOR_SKY_BLUE,
    COLOR_SNOW_ALT,
    COLOR_SNOW_WHITE,
    COLOR_STREET_GRAY,
    COLOR_STREET_LINE,
    COLOR_WATER_SPLASH,
    FLASH_HIT_RATE,
    # Animation Flash
    FLASH_INVINCIBILITY_RATE,
    FLASH_POWERUP_WARNING_RATE,
    FLASH_POWERUP_WARNING_TIME,
    FONT_HUGE,
    FONT_LARGE,
    # Font Sizes
    FONT_SMALL,
    # Game Timings
    GAME_DURATION,
    OVERLAY_GAME_OVER_ALPHA,
    # Overlay Alpha
    OVERLAY_PAUSE_ALPHA,
    PLAYER_ATTACK_COOLDOWN,
    PLAYER_COLLISION_HEIGHT,
    PLAYER_COLLISION_OFFSET,
    PLAYER_COLLISION_SIZE,
    # Collision
    PLAYER_COLLISION_WIDTH,
    PLAYER_HIT_FLASH_DURATION,
    PLAYER_INVINCIBILITY_DURATION,
    PLAYER_SKI_DIAGONAL_SPEED,
    # Player Movement
    PLAYER_SKI_SPEED,
    PLAYER_VEGAS_COLLISION_HEIGHT,
    PLAYER_VEGAS_COLLISION_WIDTH,
    PLAYER_VEGAS_GRAVITY,
    PLAYER_VEGAS_JUMP_POWER,
    PLAYER_VEGAS_MAX_FALL_SPEED,
    POOL_AMMO_CAPACITY,
    POOL_BALLOON_HOMING_RANGE,
    POOL_BALLOON_HOMING_STRENGTH,
    POOL_BALLOON_LAUNCH_SPEED,
    POOL_BALLOON_MAX_SPEED,
    # Pool Game
    POOL_BALLOON_RADIUS,
    POOL_BALLOON_TRAIL_LENGTH,
    POOL_BALLOON_UPWARD_ARC,
    POOL_MAX_POWERUPS,
    POOL_MAX_TARGETS,
    POOL_POOL_BOTTOM_MARGIN,
    POOL_POOL_MARGIN,
    POOL_RELOAD_DURATION,
    POOL_RELOAD_TIME,
    POOL_SPLASH_BASE_SPEED,
    POOL_SPLASH_DURATION,
    POOL_SPLASH_GRAVITY,
    POOL_SPLASH_PARTICLE_COUNT,
    POOL_SPLASH_SHRINK_RATE,
    POOL_SPLASH_SPEED_VARIANCE,
    POOL_TRIPLE_SHOT_SPREAD,
    POOL_WATER_ALPHA,
    POOL_WATER_SPEED,
    POOL_WATER_WAVE_AMPLITUDE,
    POOL_WATER_WAVE_FREQUENCY,
    POOL_WATER_WAVE_SPACING,
    POWERUP_FIRST_SPAWN_TIME,
    POWERUP_SPAWN_INTERVAL,
    SKI_CRASH_DURATION,
    SKI_DAD_OFFSET_X,
    SKI_MAX_LIVES,
    SKI_PLAYER_Y_OFFSET,
    # Ski Game
    SKI_SCROLL_SPEED,
    SKI_SNOW_PARTICLE_COUNT,
    SKI_SNOWFLAKE_POINTS,
    # Display
    SPRITE_DISPLAY_SIZE,
    TARGET_SPAWN_INTERVAL,
    UI_BIG_TEXT_Y,
    UI_HEART_SIZE,
    UI_HEART_SPACING,
    UI_INSTRUCTION_LINE_HEIGHT,
    UI_INSTRUCTION_START_Y,
    UI_POWERUP_BAR_HEIGHT,
    UI_POWERUP_BAR_WIDTH,
    UI_POWERUP_DISPLAY_X,
    UI_POWERUP_ICON_SIZE,
    UI_POWERUP_ITEM_HEIGHT,
    UI_SCORE_PADDING,
    UI_TIMER_BORDER,
    # UI Layout
    UI_TIMER_PADDING,
    VEGAS_BOSS_ARENA_OFFSET,
    VEGAS_BOSS_ATTACK_RANGE,
    VEGAS_BOSS_DAMAGE,
    VEGAS_BOSS_START_Y,
    VEGAS_BUILDING_HEIGHTS,
    VEGAS_BUILDING_SPACING,
    VEGAS_BUILDING_WIDTHS,
    VEGAS_FAR_BG_PARALLAX,
    VEGAS_GROUND_OFFSET,
    # Vegas Game
    VEGAS_LEVEL_WIDTH,
    VEGAS_NEAR_BG_PARALLAX,
    VEGAS_STAR_COUNT,
    VEGAS_VICTORY_HEALTH_BONUS,
    VEGAS_VICTORY_SCORE_BASE,
)


class TestColorConstants:
    """Test that all color constants are properly defined as RGB tuples."""

    def test_color_constants_are_tuples(self):
        """Verify all color constants are 3-element tuples."""
        colors = [
            COLOR_SKY_BLUE,
            COLOR_SNOW_WHITE,
            COLOR_SNOW_ALT,
            COLOR_GOLD,
            COLOR_NIGHT_SKY,
            COLOR_NIGHT_PURPLE,
            COLOR_BUILDING_DARK,
            COLOR_STREET_GRAY,
            COLOR_STREET_LINE,
            COLOR_WATER_SPLASH,
            COLOR_PLACEHOLDER,
            COLOR_OVERLAY_GRAY,
            COLOR_BOSS_HEALTH,
        ]

        for color in colors:
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert all(isinstance(c, int) and 0 <= c <= 255 for c in color)

    def test_placeholder_color_is_magenta(self):
        """Verify placeholder color is magenta."""
        assert COLOR_PLACEHOLDER == (255, 0, 255)


class TestNumericConstants:
    """Test that numeric constants have reasonable values."""

    def test_player_movement_constants(self):
        """Test player movement constants are positive."""
        assert PLAYER_SKI_SPEED > 0
        assert PLAYER_SKI_DIAGONAL_SPEED > 0
        assert PLAYER_SKI_DIAGONAL_SPEED < PLAYER_SKI_SPEED
        assert PLAYER_VEGAS_JUMP_POWER < 0  # Negative for upward
        assert PLAYER_VEGAS_GRAVITY > 0
        assert PLAYER_VEGAS_MAX_FALL_SPEED > 0
        assert PLAYER_INVINCIBILITY_DURATION > 0
        assert PLAYER_HIT_FLASH_DURATION > 0
        assert PLAYER_ATTACK_COOLDOWN > 0

    def test_collision_constants(self):
        """Test collision constants are positive."""
        assert PLAYER_COLLISION_WIDTH > 0
        assert PLAYER_COLLISION_HEIGHT > 0
        assert PLAYER_COLLISION_OFFSET > 0
        assert PLAYER_COLLISION_SIZE > 0
        assert PLAYER_VEGAS_COLLISION_WIDTH > 0
        assert PLAYER_VEGAS_COLLISION_HEIGHT > 0

    def test_game_timing_constants(self):
        """Test game timing constants."""
        assert GAME_DURATION == 60.0  # Standard 60 second games
        assert SKI_CRASH_DURATION > 0
        assert POOL_RELOAD_TIME > 0
        assert POOL_RELOAD_DURATION > POOL_RELOAD_TIME
        assert POOL_AMMO_CAPACITY > 0
        assert TARGET_SPAWN_INTERVAL > 0
        assert POWERUP_SPAWN_INTERVAL > 0
        assert POWERUP_FIRST_SPAWN_TIME > 0

    def test_ui_layout_constants(self):
        """Test UI layout constants."""
        assert UI_TIMER_PADDING > 0
        assert UI_TIMER_BORDER > 0
        assert UI_HEART_SIZE > 0
        assert UI_HEART_SPACING > 0
        assert UI_SCORE_PADDING > 0
        assert UI_INSTRUCTION_LINE_HEIGHT > 0
        assert UI_INSTRUCTION_START_Y > 0
        assert UI_BIG_TEXT_Y > 0
        assert UI_POWERUP_DISPLAY_X > 0
        assert UI_POWERUP_ITEM_HEIGHT > 0
        assert UI_POWERUP_ICON_SIZE > 0
        assert UI_POWERUP_BAR_WIDTH > 0
        assert UI_POWERUP_BAR_HEIGHT > 0

    def test_pool_game_constants(self):
        """Test pool game specific constants."""
        assert POOL_BALLOON_RADIUS > 0
        assert POOL_BALLOON_LAUNCH_SPEED > 0
        assert POOL_BALLOON_UPWARD_ARC > 0
        assert POOL_BALLOON_TRAIL_LENGTH > 0
        assert POOL_BALLOON_HOMING_STRENGTH > 0
        assert POOL_BALLOON_MAX_SPEED > 0
        assert POOL_BALLOON_HOMING_RANGE > 0
        assert POOL_SPLASH_PARTICLE_COUNT > 0
        assert POOL_SPLASH_DURATION > 0
        assert POOL_SPLASH_BASE_SPEED > 0
        assert POOL_SPLASH_SPEED_VARIANCE > 0
        assert POOL_SPLASH_GRAVITY > 0
        assert 0 < POOL_SPLASH_SHRINK_RATE < 1  # Shrink rate between 0 and 1
        assert POOL_POOL_MARGIN > 0
        assert POOL_POOL_BOTTOM_MARGIN > 0
        assert POOL_WATER_WAVE_SPACING > 0
        assert POOL_WATER_WAVE_AMPLITUDE > 0
        assert POOL_WATER_WAVE_FREQUENCY > 0
        assert POOL_WATER_SPEED > 0
        assert 0 < POOL_WATER_ALPHA <= 255
        assert POOL_TRIPLE_SHOT_SPREAD > 0
        assert POOL_MAX_TARGETS > 0
        assert POOL_MAX_POWERUPS > 0

    def test_ski_game_constants(self):
        """Test ski game specific constants."""
        assert SKI_SCROLL_SPEED > 0
        assert SKI_SNOWFLAKE_POINTS > 0
        assert SKI_MAX_LIVES > 0
        assert SKI_SNOW_PARTICLE_COUNT > 0
        assert SKI_DAD_OFFSET_X > 0
        assert SKI_PLAYER_Y_OFFSET > 0

    def test_vegas_game_constants(self):
        """Test Vegas game specific constants."""
        assert VEGAS_LEVEL_WIDTH > 0
        assert VEGAS_GROUND_OFFSET > 0
        assert VEGAS_BOSS_ARENA_OFFSET > 0
        assert VEGAS_BOSS_START_Y > 0
        assert VEGAS_BOSS_ATTACK_RANGE > 0
        assert VEGAS_BOSS_DAMAGE > 0
        assert 0 < VEGAS_FAR_BG_PARALLAX < 1
        assert 0 < VEGAS_NEAR_BG_PARALLAX < 1
        assert VEGAS_FAR_BG_PARALLAX < VEGAS_NEAR_BG_PARALLAX
        assert VEGAS_STAR_COUNT > 0
        assert isinstance(VEGAS_BUILDING_WIDTHS, list)
        assert isinstance(VEGAS_BUILDING_HEIGHTS, list)
        assert len(VEGAS_BUILDING_WIDTHS) == len(VEGAS_BUILDING_HEIGHTS)
        assert all(w > 0 for w in VEGAS_BUILDING_WIDTHS)
        assert all(h > 0 for h in VEGAS_BUILDING_HEIGHTS)
        assert VEGAS_BUILDING_SPACING > 0
        assert VEGAS_VICTORY_SCORE_BASE > 0
        assert VEGAS_VICTORY_HEALTH_BONUS > 0

    def test_font_size_constants(self):
        """Test font size constants."""
        assert FONT_SMALL > 0
        assert FONT_LARGE > FONT_SMALL
        assert FONT_HUGE > FONT_LARGE

    def test_overlay_alpha_constants(self):
        """Test overlay alpha constants."""
        assert 0 < OVERLAY_PAUSE_ALPHA <= 255
        assert 0 < OVERLAY_GAME_OVER_ALPHA <= 255

    def test_animation_flash_constants(self):
        """Test animation flash timing constants."""
        assert FLASH_INVINCIBILITY_RATE > 0
        assert FLASH_HIT_RATE > 0
        assert FLASH_POWERUP_WARNING_TIME > 0
        assert FLASH_POWERUP_WARNING_RATE > 0


class TestConstantRelationships:
    """Test relationships between related constants."""

    def test_collision_size_relationships(self):
        """Test that collision sizes make sense relative to each other."""
        # Collision box should be smaller than the display size for forgiveness
        assert PLAYER_COLLISION_WIDTH < SPRITE_DISPLAY_SIZE
        assert PLAYER_COLLISION_HEIGHT < SPRITE_DISPLAY_SIZE

        # Vegas collision box is different (taller)
        assert PLAYER_VEGAS_COLLISION_HEIGHT > PLAYER_COLLISION_HEIGHT

    def test_timing_relationships(self):
        """Test timing relationships."""
        # Powerups should spawn during the game
        assert POWERUP_FIRST_SPAWN_TIME < GAME_DURATION
        assert POWERUP_SPAWN_INTERVAL < GAME_DURATION

        # Flash warning should be shorter than powerup duration
        assert FLASH_POWERUP_WARNING_TIME < POWERUP_SPAWN_INTERVAL
