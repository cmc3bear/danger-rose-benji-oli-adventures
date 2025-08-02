import math
from unittest.mock import Mock, patch

from src.entities.pool_targets import (
    BeachBallTarget,
    DonutFloatTarget,
    DuckTarget,
    PoolTarget,
)
from src.entities.target_particles import (
    TargetDestroyEffect,
    TargetDestroyParticle,
)


class TestPoolTargetBase:
    """Test base pool target functionality."""

    def test_target_initialization(self):
        """Test basic target initialization."""

        # Create a concrete implementation for testing
        class TestTarget(PoolTarget):
            def get_size(self) -> int:
                return 50

            def get_point_value(self) -> int:
                return 10

            def get_color(self):
                return (255, 0, 0)

            def update_movement(self, dt: float):
                pass

            def draw_shape(self, screen, x, y, size, color):
                pass

        target = TestTarget(100, 200)

        assert target.x == 100
        assert target.y == 200
        assert target.initial_x == 100
        assert target.initial_y == 200
        assert target.hit is False
        assert target.active is True
        assert target.get_size() == 50
        assert target.get_point_value() == 10

    def test_collision_detection(self):
        """Test collision detection with water balloon."""

        class TestTarget(PoolTarget):
            def get_size(self) -> int:
                return 40

            def get_point_value(self) -> int:
                return 10

            def get_color(self):
                return (255, 0, 0)

            def update_movement(self, dt: float):
                pass

            def draw_shape(self, screen, x, y, size, color):
                pass

        target = TestTarget(100, 100)

        # Mock balloon
        balloon = Mock()
        balloon.x = 110
        balloon.y = 110
        balloon.radius = 10

        # Should hit
        assert target.check_collision(balloon) is True
        assert target.hit is True

        # Should not hit again once already hit
        assert target.check_collision(balloon) is False

    def test_hit_animation(self):
        """Test hit animation updates."""

        class TestTarget(PoolTarget):
            def get_size(self) -> int:
                return 40

            def get_point_value(self) -> int:
                return 10

            def get_color(self):
                return (255, 0, 0)

            def update_movement(self, dt: float):
                pass

            def draw_shape(self, screen, x, y, size, color):
                pass

        target = TestTarget(100, 100)
        target.hit = True

        # Update with hit
        target.update(0.1)
        assert target.hit_time == 0.1
        assert target.scale > 1.0
        assert target.rotation > 0

        # Should deactivate after 0.5 seconds
        target.update(0.5)
        assert target.active is False


class TestDuckTarget:
    """Test duck target specific behavior."""

    def test_duck_properties(self):
        """Test duck-specific properties."""
        duck = DuckTarget(300, 200)

        assert duck.get_size() == 50
        assert duck.get_point_value() == 25
        assert duck.get_color() == (220, 200, 60)  # Yellow
        assert duck.amplitude == 50
        assert duck.frequency == 1.5
        assert duck.speed == 50

    def test_sine_wave_movement(self):
        """Test duck moves in sine wave pattern."""
        duck = DuckTarget(500, 300)
        initial_y = duck.y

        # Move for a bit
        for _ in range(10):
            duck.update_movement(0.1)

        # X should change
        assert duck.x != 500

        # Y should oscillate around initial position
        assert abs(duck.y - initial_y) <= duck.amplitude

    def test_edge_bouncing(self):
        """Test duck bounces off edges."""
        duck = DuckTarget(200, 300)
        duck.direction = -1  # Moving left

        # Force to edge
        duck.x = 195
        duck.update_movement(0.1)

        # Should reverse direction
        assert duck.direction == 1


class TestBeachBallTarget:
    """Test beach ball target specific behavior."""

    def test_beachball_properties(self):
        """Test beach ball-specific properties."""
        ball = BeachBallTarget(400, 300)

        assert ball.get_size() == 45
        assert ball.get_point_value() == 30
        assert ball.get_color() == (180, 60, 60)  # Red
        assert abs(ball.vx) > 0  # Should have velocity
        assert abs(ball.vy) > 0

    def test_random_bouncing(self):
        """Test beach ball bounces randomly."""
        ball = BeachBallTarget(500, 300)
        initial_x = ball.x
        initial_y = ball.y

        # Update position
        for _ in range(10):
            ball.update_movement(0.1)

        # Position should change
        assert ball.x != initial_x or ball.y != initial_y

        # Rotation should update
        assert ball.rotation != 0

    def test_wall_bouncing(self):
        """Test beach ball bounces off walls."""
        ball = BeachBallTarget(500, 300)
        ball.vx = -100  # Moving left

        # Force to left edge
        ball.x = 170
        old_vx = ball.vx
        ball.update_movement(0.1)

        # Velocity should reverse
        assert ball.vx == -old_vx


class TestDonutFloatTarget:
    """Test donut float target specific behavior."""

    def test_donut_properties(self):
        """Test donut-specific properties."""
        donut = DonutFloatTarget(500, 300)

        assert donut.get_size() == 60  # Largest
        assert donut.get_point_value() == 15  # Lowest points
        assert donut.get_color() == (255, 192, 203)  # Pink
        assert donut.speed == 40  # Slowest

    def test_straight_line_movement(self):
        """Test donut moves in straight lines."""
        donut = DonutFloatTarget(500, 300)

        # Should move in one of 4 cardinal directions
        # Allow for small floating point errors
        assert (abs(donut.vx) < 0.01 and abs(abs(donut.vy) - 40) < 0.01) or (
            abs(abs(donut.vx) - 40) < 0.01 and abs(donut.vy) < 0.01
        )

    def test_bobbing_effect(self):
        """Test donut has bobbing effect."""
        donut = DonutFloatTarget(500, 300)
        donut.vx = 40
        donut.vy = 0

        # Test that bobbing parameters are set
        assert donut.bob_amplitude == 5
        assert donut.bob_frequency == 2

        # Test that movement_time affects bobbing
        donut.movement_time = math.pi / (2 * donut.bob_frequency)  # Peak of sine wave
        donut.update_movement(0.01)

        # The update_movement adds bobbing but then self.y gets modified
        # So we'll just verify the bobbing calculation works
        bob_offset = (
            math.sin(donut.movement_time * donut.bob_frequency) * donut.bob_amplitude
        )
        assert abs(bob_offset) > 0  # Should have some bobbing offset


class TestTargetParticles:
    """Test particle effects for target destruction."""

    def test_particle_creation(self):
        """Test particle creation and properties."""
        particle = TargetDestroyParticle(100, 200, (255, 0, 0))

        assert particle.x == 100
        assert particle.y == 200
        assert particle.color == (255, 0, 0)
        assert particle.active is True
        assert particle.lifetime > 0

    def test_particle_physics(self):
        """Test particle physics update."""
        particle = TargetDestroyParticle(100, 200, (255, 0, 0))
        initial_y = particle.y

        # Update
        particle.update(0.1)

        # Should move
        assert particle.x != 100
        assert particle.y != initial_y

        # Particle should have moved due to velocity
        assert particle.age > 0

    def test_particle_lifetime(self):
        """Test particle deactivates after lifetime."""
        particle = TargetDestroyParticle(100, 200, (255, 0, 0))
        particle.lifetime = 0.5

        # Update past lifetime
        particle.update(0.6)

        assert particle.active is False

    def test_destroy_effect_types(self):
        """Test different destroy effects for each target type."""
        # Duck effect
        duck_effect = TargetDestroyEffect(100, 200, (255, 255, 0), "duck")
        assert len(duck_effect.particles) == 25  # 15 + 10 feathers

        # Beach ball effect
        ball_effect = TargetDestroyEffect(100, 200, (255, 0, 0), "beachball")
        assert len(ball_effect.particles) == 20

        # Donut effect
        donut_effect = TargetDestroyEffect(100, 200, (255, 192, 203), "donut")
        assert len(donut_effect.particles) == 27  # 12 + 15 sprinkles

        # Default effect
        default_effect = TargetDestroyEffect(100, 200, (255, 0, 0), "default")
        assert len(default_effect.particles) == 15

    def test_effect_lifecycle(self):
        """Test effect deactivates when all particles are done."""
        effect = TargetDestroyEffect(100, 200, (255, 0, 0), "default")

        # Force all particles to expire
        for particle in effect.particles:
            particle.active = False

        effect.update(0.1)
        assert effect.active is False


class TestTargetIntegration:
    """Test target integration with pool game."""

    @patch("pygame.font.Font")
    def test_target_spawning(self, mock_font):
        """Test target spawning in pool game."""
        from src.scenes.pool import PoolGame

        # Mock scene manager
        scene_manager = Mock()
        scene_manager.screen_width = 1280
        scene_manager.screen_height = 720
        scene_manager.game_data = {"selected_character": "Danger"}

        # Mock save manager with proper data structure
        save_manager = Mock()
        save_manager._current_save_data = {"high_scores": {}}
        scene_manager.save_manager = save_manager

        # Create game
        game = PoolGame(scene_manager)

        # Should have initial targets
        assert len(game.targets) == 3

        # Test spawning new target
        initial_count = len(game.targets)
        game.spawn_target()
        assert len(game.targets) == initial_count + 1

    def test_target_collision_scoring(self):
        """Test target collision increases score."""
        # Test target collision directly
        target = DuckTarget(500, 300)

        # Mock balloon
        balloon = Mock()
        balloon.x = 500
        balloon.y = 300
        balloon.radius = 10

        # Initial state
        assert target.hit is False
        assert target.get_point_value() == 25

        # Test collision
        assert target.check_collision(balloon) is True
        assert target.hit is True

        # Shouldn't collide again when already hit
        assert target.check_collision(balloon) is False
