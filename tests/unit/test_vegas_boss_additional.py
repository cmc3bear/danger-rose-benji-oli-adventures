"""Additional tests for Vegas boss to improve coverage."""

import pygame
import pytest

from src.entities.vegas_boss import BossPhase, Projectile, VegasBoss


class TestVegasBossAdditional:
    """Additional Vegas boss tests for coverage."""

    @pytest.fixture
    def boss(self):
        """Create a boss instance for testing."""
        pygame.init()
        return VegasBoss(640, 300)

    def test_boss_rect_updates_with_movement(self, boss):
        """Test boss rect updates when boss moves."""
        initial_x = boss.rect.centerx
        boss.x = 500
        boss.y = 400
        boss.update(0.1, 600, 400)  # This should update the rect

        assert boss.rect.centerx != initial_x  # Rect should have moved

    def test_projectile_draw(self):
        """Test projectile drawing."""
        proj = Projectile(100, 100, 0, 0, (255, 0, 0))
        screen = pygame.Surface((800, 600))

        # Active projectile should draw without crashing
        proj.draw(screen, 0)

        # Inactive projectile should also not crash
        proj.active = False
        proj.draw(screen, 0)

    def test_boss_phase_transition_effects(self, boss):
        """Test phase transition visual effects."""
        boss.transitioning = True
        boss.phase_transition_time = 0.5

        boss.update(0.1, 500, 400)

        # Scale should change during transition
        assert boss.scale != 1.0

    def test_boss_particle_cleanup(self, boss):
        """Test particle system cleanup."""
        # Add some particles
        for i in range(5):
            boss.particles.append(
                {
                    "x": 100,
                    "y": 100,
                    "vx": 10,
                    "vy": -10,
                    "lifetime": i * 0.3,
                    "color": (255, 0, 0),
                }
            )

        # Update to clean old particles
        boss.update(0.1, 500, 400)

        # Particles with lifetime > 1.0 should be removed
        assert len(boss.particles) < 5

    def test_boss_draw_with_effects(self, boss):
        """Test boss drawing with various effects."""
        screen = pygame.Surface((800, 600))

        # Test with hit flash
        boss.hit_flash_timer = 0.2
        boss.draw(screen, 0)

        # Test when invulnerable
        boss.invulnerable = True
        boss.draw(screen, 0)

        # Test when defeated and off screen
        boss.phase = BossPhase.DEFEATED
        boss.y = 900
        boss.draw(screen, 0)
        # Should not crash when fallen off screen

    def test_projectile_lifetime(self):
        """Test projectile deactivation by lifetime."""
        proj = Projectile(100, 100, 0, 0, (255, 0, 0))
        proj.lifetime = 11  # Over max lifetime

        proj.update(0.1)

        assert not proj.active

    def test_boss_movement_phase_specific(self, boss):
        """Test phase-specific movement patterns."""
        # Test phase 1 movement
        boss.phase = BossPhase.PHASE_1_HAPPY
        initial_x = boss.x
        boss.update_movement(0.1, 500)
        # Should have gentle movement
        assert abs(boss.x - initial_x) < 10

        # Test phase 3 chaotic movement
        boss.phase = BossPhase.PHASE_3_DIZZY
        boss.float_time = 0
        boss.update_movement(0.1, 500)
        # Rotation should increase significantly
        assert boss.rotation > 0
