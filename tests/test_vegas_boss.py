import math
from unittest.mock import MagicMock

import pygame
import pytest

from src.entities.vegas_boss import BossPhase, Projectile, VegasBoss


class TestVegasBoss:
    """Test suite for Vegas boss functionality."""

    @pytest.fixture
    def boss(self):
        """Create a boss instance for testing."""
        pygame.init()
        return VegasBoss(640, 300)

    def test_boss_initialization(self, boss):
        """Test boss is initialized correctly."""
        assert boss.x == 640
        assert boss.y == 300
        assert boss.health == boss.max_health
        assert boss.phase == BossPhase.PHASE_1_HAPPY
        assert not boss.invulnerable
        assert len(boss.projectiles) == 0

    def test_phase_transitions(self, boss):
        """Test boss phases change based on health."""
        # Phase 2 at 66% health (198/300)
        boss.take_damage(102)  # Should be at 198/300 health
        assert boss.phase == BossPhase.PHASE_2_ANGRY
        assert boss.invulnerable  # Should be invulnerable during transition

        # Phase 3 at 33% health (99/300)
        boss.invulnerable = False  # Reset invulnerability
        boss.take_damage(99)  # Should be at 99/300 health
        assert boss.phase == BossPhase.PHASE_3_DIZZY

        # Defeated at 0 health
        boss.invulnerable = False
        boss.take_damage(100)
        assert boss.phase == BossPhase.DEFEATED

    def test_damage_and_invulnerability(self, boss):
        """Test damage mechanics and invulnerability."""
        initial_health = boss.health

        # Normal damage
        boss.take_damage(50)
        assert boss.health == initial_health - 50

        # No damage when invulnerable
        boss.invulnerable = True
        boss.take_damage(50)
        assert boss.health == initial_health - 50  # Health unchanged

        # No damage when defeated
        boss.invulnerable = False
        boss.phase = BossPhase.DEFEATED
        boss.take_damage(50)
        assert boss.health == initial_health - 50  # Health unchanged

    def test_projectile_spawning_phase_1(self, boss):
        """Test projectile patterns in phase 1."""
        boss.spawn_projectiles(500, 400)

        # Phase 1 spawns 8 projectiles in radial pattern
        assert len(boss.projectiles) == 8

        # Check projectiles are spread evenly
        angles = []
        for proj in boss.projectiles:
            angle = math.atan2(proj.vy, proj.vx)
            angles.append(angle)

        # Angles should be evenly distributed
        angles.sort()
        for i in range(1, len(angles)):
            diff = angles[i] - angles[i - 1]
            assert abs(diff - math.pi / 4) < 0.1  # Should be ~45 degrees apart

    def test_projectile_spawning_phase_2(self, boss):
        """Test projectile patterns in phase 2."""
        boss.phase = BossPhase.PHASE_2_ANGRY
        player_x, player_y = 500, 400
        boss.spawn_projectiles(player_x, player_y)

        # Phase 2 spawns 3 targeted projectiles
        assert len(boss.projectiles) == 3

        # Middle projectile should aim at player
        middle_proj = boss.projectiles[1]
        dx = player_x - boss.x
        dy = player_y - boss.y
        expected_angle = math.atan2(dy, dx)
        actual_angle = math.atan2(middle_proj.vy, middle_proj.vx)

        assert abs(expected_angle - actual_angle) < 0.1

    def test_projectile_spawning_phase_3(self, boss):
        """Test projectile patterns in phase 3."""
        boss.phase = BossPhase.PHASE_3_DIZZY
        boss.pattern_timer = 1.0  # Set specific time for predictable pattern
        boss.spawn_projectiles(500, 400)

        # Phase 3 spawns 4 projectiles in spiral
        assert len(boss.projectiles) == 4

    def test_movement_patterns(self, boss):
        """Test boss movement in different phases."""
        dt = 0.016  # 60 FPS

        # Phase 1 - gentle movement
        initial_x = boss.x
        boss.update_movement(dt, 500)
        assert abs(boss.x - initial_x) < 2  # Small movement

        # Phase 2 - tracks player
        boss.phase = BossPhase.PHASE_2_ANGRY
        boss.x = 100
        player_x = 500
        boss.update_movement(dt, player_x)
        assert boss.x > 100  # Should move towards player

        # Phase 3 - chaotic movement
        boss.phase = BossPhase.PHASE_3_DIZZY
        boss.float_time = 0
        initial_x = boss.x
        initial_y = boss.y
        boss.update_movement(dt * 10, 500)  # Larger time step
        assert boss.x != initial_x or boss.y != initial_y  # Should move

    def test_defeated_state(self, boss):
        """Test boss behavior when defeated."""
        boss.phase = BossPhase.DEFEATED
        initial_y = boss.y

        boss.update(0.1, 500, 400)

        # Should fall when defeated
        assert boss.y > initial_y
        assert boss.vy > 0  # Positive velocity (falling)

    def test_invulnerability_timer(self, boss):
        """Test invulnerability timer counts down."""
        boss.invulnerable = True
        boss.invuln_timer = 1.0

        boss.update(0.5, 500, 400)
        assert boss.invuln_timer == 0.5
        assert boss.invulnerable

        boss.update(0.6, 500, 400)
        assert boss.invuln_timer <= 0
        assert not boss.invulnerable

    def test_projectile_lifecycle(self):
        """Test projectile update and deactivation."""
        proj = Projectile(100, 100, 50, 0, (255, 0, 0))

        # Normal update
        proj.update(0.1)
        assert proj.x == 105  # 100 + 50 * 0.1
        assert proj.active

        # Deactivate when off screen
        proj.x = -100
        proj.update(0.1)
        assert not proj.active

        # Deactivate when too old
        proj2 = Projectile(100, 100, 0, 0, (255, 0, 0))
        proj2.lifetime = 11
        proj2.update(0.1)
        assert not proj2.active

    def test_particle_effects(self, boss):
        """Test particle effects spawn on hit."""
        initial_particles = len(boss.particles)

        boss.take_damage(10)

        # Should spawn particles when hit
        assert len(boss.particles) > initial_particles

        # Particles should have correct properties
        for particle in boss.particles:
            assert "x" in particle
            assert "y" in particle
            assert "vx" in particle
            assert "vy" in particle
            assert "lifetime" in particle
            assert "color" in particle

    def test_attack_timing(self, boss):
        """Test attack cooldown mechanics."""
        # Phase 1 attack rate
        boss.attack_timer = 0
        boss.update(2.5, 500, 400)  # Should trigger attack
        assert len(boss.projectiles) > 0
        assert boss.attack_timer == 0  # Reset after attack

        # Clear projectiles
        boss.projectiles.clear()

        # Not enough time for another attack
        boss.update(1.0, 500, 400)
        assert len(boss.projectiles) == 0  # No new projectiles

    def test_phase_colors(self, boss):
        """Test each phase has distinct color."""
        colors = {}

        for phase in [
            BossPhase.PHASE_1_HAPPY,
            BossPhase.PHASE_2_ANGRY,
            BossPhase.PHASE_3_DIZZY,
            BossPhase.DEFEATED,
        ]:
            boss.phase = phase
            color = boss.get_phase_color()
            assert color not in colors.values()  # Each color should be unique
            colors[phase] = color

    def test_projectile_rect_updates(self):
        """Test projectile rect updates with position."""
        proj = Projectile(100, 100, 10, 0, (255, 0, 0), 20)

        # Initial rect position
        assert proj.rect.centerx == 100
        assert proj.rect.centery == 100

        # Update position
        proj.update(1.0)

        # Rect should follow position
        assert proj.rect.centerx == 110  # 100 + 10*1
        assert proj.rect.centery == 100

    def test_boss_rect_follows_position(self, boss):
        """Test boss collision rect follows boss position."""
        initial_x = boss.rect.centerx
        initial_y = boss.rect.centery

        # Move boss
        boss.x += 50
        boss.y += 30
        boss.update_rect()

        # Rect should update
        assert boss.rect.centerx == initial_x + 50
        assert boss.rect.centery == initial_y + 30

    def test_boss_draw_methods(self, boss):
        """Test boss drawing methods don't crash."""
        mock_screen = MagicMock()

        # Test main draw
        boss.draw(mock_screen, 0)

        # Test health bar draw
        boss.draw_health_bar(mock_screen, 100, 50)

        # Test face drawing for each phase
        for phase in [
            BossPhase.PHASE_1_HAPPY,
            BossPhase.PHASE_2_ANGRY,
            BossPhase.PHASE_3_DIZZY,
        ]:
            boss.phase = phase
            boss.draw_face(mock_screen, 400, 300, 100)
