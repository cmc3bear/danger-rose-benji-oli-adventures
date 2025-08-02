from unittest.mock import Mock, patch

import pygame
import pytest

from src.entities.pool_targets import DuckTarget
from src.scenes.pool import PoolGame, PoolPlayer, SplashEffect, WaterBalloon


class TestPoolPlayer:
    """Test the PoolPlayer class."""

    def test_init(self):
        """Test player initialization."""
        player = PoolPlayer(100, 200, "Danger")
        assert player.x == 100
        assert player.y == 200
        assert player.character_name == "Danger"
        assert player.rect.centerx == 100
        assert player.rect.centery == 200

    def test_update(self):
        """Test player update."""
        player = PoolPlayer(100, 200, "Danger")
        player.sprite.update = Mock()

        player.update(0.016)

        player.sprite.update.assert_called_once()
        assert player.rect.centerx == player.x
        assert player.rect.centery == player.y


class TestWaterBalloon:
    """Test the WaterBalloon class."""

    def test_init_with_target(self):
        """Test balloon initialization with target."""
        balloon = WaterBalloon(100, 100, 200, 100, 800)

        assert balloon.x == 100
        assert balloon.y == 100
        assert balloon.vx > 0  # Moving right
        assert balloon.vy < 0  # Initial upward arc
        assert balloon.active
        assert balloon.radius == 8

    def test_init_straight_up(self):
        """Test balloon initialization straight up."""
        balloon = WaterBalloon(100, 100, 100, 100, 800)

        assert balloon.vx == 0
        assert balloon.vy == -800

    def test_update_physics(self):
        """Test balloon physics update."""
        balloon = WaterBalloon(100, 100, 200, 100, 800)
        initial_vy = balloon.vy

        balloon.update(0.1)

        assert balloon.x > 100  # Moved horizontally
        assert balloon.vy > initial_vy  # Gravity applied
        assert len(balloon.trail) == 1  # Trail point added

    def test_deactivate_off_screen(self):
        """Test balloon deactivates when off screen."""
        balloon = WaterBalloon(100, 500, 100, 700, 800)
        balloon.y = 700  # Force off screen

        balloon.update(0.1)

        assert not balloon.active


class TestTarget:
    """Test the Target class."""

    def test_init(self):
        """Test target initialization."""
        target = DuckTarget(300, 200)

        assert target.x == 300
        assert target.y == 200
        assert target.get_size() == 50  # DuckTarget has fixed size
        assert target.get_point_value() == 25  # DuckTarget point value
        assert not target.hit
        assert target.active

    def test_collision_detection(self):
        """Test target collision with balloon."""
        target = DuckTarget(300, 200)
        balloon = WaterBalloon(280, 200, 400, 200)

        # Test hit
        hit = target.check_collision(balloon)
        assert hit
        assert target.hit

        # Test no double hits
        hit2 = target.check_collision(balloon)
        assert not hit2

    def test_hit_reset(self):
        """Test target hit animation reset."""
        target = DuckTarget(300, 200)
        target.hit = True

        # Update for hit animation time
        target.update(0.6)

        # After 0.5s, target becomes inactive, not reset
        assert not target.active
        assert target.hit_time > 0.5


class TestSplashEffect:
    """Test the SplashEffect class."""

    def test_init(self):
        """Test splash effect initialization."""
        splash = SplashEffect(100, 200)

        assert splash.x == 100
        assert splash.y == 200
        assert splash.active
        assert len(splash.particles) == 12

    def test_update(self):
        """Test splash effect update."""
        splash = SplashEffect(100, 200)

        splash.update(0.1)

        # Check particles moved
        for particle in splash.particles:
            assert particle["x"] != 100 or particle["y"] != 200
            assert particle["size"] < 3 + 3  # Size decreased

    def test_deactivate(self):
        """Test splash effect deactivation."""
        splash = SplashEffect(100, 200)

        splash.update(0.6)  # Past max time

        assert not splash.active


class TestPoolGame:
    """Test the PoolGame scene."""

    @pytest.fixture
    def mock_scene_manager(self):
        """Create a mock scene manager."""
        manager = Mock()
        manager.screen_width = 1280
        manager.screen_height = 720
        manager.game_data = {"selected_character": "Danger"}
        return manager

    def test_init(self, mock_scene_manager):
        """Test pool game initialization."""
        game = PoolGame(mock_scene_manager)

        assert game.state == PoolGame.STATE_READY
        assert game.score == 0
        assert game.time_remaining == 60.0
        assert len(game.targets) == 15  # 3x5 grid
        assert game.current_ammo == 5
        assert game.can_shoot

    def test_start_game(self, mock_scene_manager):
        """Test starting the game."""
        game = PoolGame(mock_scene_manager)

        game.start_game()

        assert game.state == PoolGame.STATE_PLAYING
        assert game.start_time is not None
        assert game.score == 0

    def test_shoot_balloon(self, mock_scene_manager):
        """Test shooting a balloon."""
        game = PoolGame(mock_scene_manager)
        game.state = PoolGame.STATE_PLAYING
        game.mouse_x = 400
        game.mouse_y = 300

        initial_ammo = game.current_ammo
        game.shoot_balloon()

        assert len(game.projectiles) == 1
        assert game.current_ammo == initial_ammo - 1
        assert not game.can_shoot

    def test_shoot_when_reloading(self, mock_scene_manager):
        """Test shooting blocked when reloading."""
        game = PoolGame(mock_scene_manager)
        game.state = PoolGame.STATE_PLAYING
        game.is_reloading = True

        game.shoot_balloon()

        assert len(game.projectiles) == 0

    def test_manual_reload(self, mock_scene_manager):
        """Test manual reload with R key."""
        game = PoolGame(mock_scene_manager)
        game.state = PoolGame.STATE_PLAYING
        game.current_ammo = 3

        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_r

        game.handle_event(event)

        assert game.is_reloading
        assert not game.can_shoot

    def test_collision_scoring(self, mock_scene_manager):
        """Test balloon hitting target increases score."""
        game = PoolGame(mock_scene_manager)
        game.state = PoolGame.STATE_PLAYING

        # Create a balloon near a target
        target = game.targets[0]
        balloon = WaterBalloon(target.x - 10, target.y, target.x, target.y)
        game.projectiles.append(balloon)

        initial_score = game.score

        # Update to process collision
        game.update(0.016)

        assert game.score > initial_score
        assert target.hit
        assert not balloon.active

    def test_game_over(self, mock_scene_manager):
        """Test game over when time runs out."""
        game = PoolGame(mock_scene_manager)
        game.state = PoolGame.STATE_PLAYING
        game.start_time = 1000  # Set a start time

        # Mock time to simulate game duration has passed
        with patch("time.time", return_value=1061):  # 61 seconds later
            game.update(0.016)

        assert game.state == PoolGame.STATE_GAME_OVER

    def test_mouse_events(self, mock_scene_manager):
        """Test mouse movement and clicking."""
        game = PoolGame(mock_scene_manager)
        game.state = PoolGame.STATE_PLAYING

        # Test mouse motion
        motion_event = Mock()
        motion_event.type = pygame.MOUSEMOTION
        motion_event.pos = (500, 300)

        game.handle_event(motion_event)

        assert game.mouse_x == 500
        assert game.mouse_y == 300
        assert game.show_aim_line

        # Test mouse click
        click_event = Mock()
        click_event.type = pygame.MOUSEBUTTONDOWN
        click_event.button = 1

        game.handle_event(click_event)

        assert len(game.projectiles) == 1

    def test_reset_game(self, mock_scene_manager):
        """Test resetting the game."""
        game = PoolGame(mock_scene_manager)
        game.state = PoolGame.STATE_GAME_OVER
        game.score = 100
        game.projectiles.append(WaterBalloon(100, 100, 200, 200))

        game.reset_game()

        assert game.state == PoolGame.STATE_READY
        assert game.score == 0
        assert len(game.projectiles) == 0
        assert game.current_ammo == 5
        assert not game.is_reloading
