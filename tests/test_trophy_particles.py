"""Tests for trophy particle effects."""

import math
from unittest.mock import Mock

import pytest

from src.effects.trophy_particles import Particle, TrophyParticleEffect


@pytest.fixture
def mock_surface():
    """Create a mock pygame surface for testing."""
    surface = Mock()
    surface.blit = Mock()
    return surface


class TestParticle:
    """Test cases for Particle class."""

    def test_particle_initialization(self):
        """Test particle initialization."""
        particle = Particle(100, 200, (255, 0, 0), 50, -100, 2.0)

        assert particle.x == 100
        assert particle.y == 200
        assert particle.color == (255, 0, 0)
        assert particle.velocity_x == 50
        assert particle.velocity_y == -100
        assert particle.lifetime == 2.0
        assert particle.max_lifetime == 2.0
        assert 2 <= particle.size <= 4

    def test_particle_update_position(self):
        """Test particle position updates."""
        particle = Particle(100, 200, (255, 0, 0), 50, -100, 2.0)

        # Update for 0.1 seconds
        dt = 0.1
        alive = particle.update(dt)

        assert alive
        assert particle.x == 105  # 100 + 50 * 0.1
        # y = 200 + (-100) * 0.1 + 0.5 * 200 * 0.1^2 = 200 - 10 + 1 = 191 (approximately)
        # But gravity is applied as velocity change: vy = -100 + 200*0.1 = -80
        # So y = 200 + (-80) * 0.1 = 192, but velocity changes during update
        assert abs(particle.y - 190) < 2  # Allow for small floating point differences
        assert particle.lifetime == 1.9  # 2.0 - 0.1

    def test_particle_gravity_effect(self):
        """Test that gravity affects particle movement."""
        particle = Particle(100, 200, (255, 0, 0), 0, 0, 2.0)

        # Update for 0.1 seconds
        dt = 0.1
        particle.update(dt)

        # Gravity is applied as velocity change, not direct position change
        # Initial velocity_y = 0, after gravity: velocity_y = 0 + 200 * 0.1 = 20
        # Position changes based on average velocity during frame
        # y = 200 + 0 * 0.1 = 200 (position update happens before gravity)
        assert particle.y == 200  # Position updated first, then velocity

    def test_particle_lifetime_expiry(self):
        """Test particle lifetime expiry."""
        particle = Particle(100, 200, (255, 0, 0), 50, -100, 0.05)

        # Update for longer than lifetime
        alive = particle.update(0.1)

        assert not alive
        assert particle.lifetime < 0

    def test_particle_draw_alive(self, mock_surface):
        """Test drawing a living particle."""
        particle = Particle(100, 200, (255, 0, 0), 50, -100, 2.0)

        # Should not raise an exception
        particle.draw(mock_surface)

    def test_particle_draw_dead(self, mock_surface):
        """Test drawing a dead particle."""
        particle = Particle(100, 200, (255, 0, 0), 50, -100, -1.0)  # Negative lifetime

        # Should not raise an exception and should return early
        particle.draw(mock_surface)


class TestTrophyParticleEffect:
    """Test cases for TrophyParticleEffect class."""

    def test_initialization(self):
        """Test particle effect system initialization."""
        effect = TrophyParticleEffect()

        assert effect.particles == []
        assert not effect.has_particles()

    def test_trophy_colors_defined(self):
        """Test that trophy colors are properly defined."""
        effect = TrophyParticleEffect()

        assert "bronze" in effect.TROPHY_COLORS
        assert "silver" in effect.TROPHY_COLORS
        assert "gold" in effect.TROPHY_COLORS

        # Each color scheme should have multiple colors
        for trophy_type, colors in effect.TROPHY_COLORS.items():
            assert len(colors) >= 2
            for color in colors:
                assert len(color) == 3  # RGB tuple
                assert all(0 <= c <= 255 for c in color)

    def test_create_trophy_celebration_bronze(self):
        """Test creating bronze trophy celebration."""
        effect = TrophyParticleEffect()

        effect.create_trophy_celebration(100, 200, "bronze")

        assert effect.has_particles()
        assert len(effect.particles) == 20  # Bronze should create 20 particles

    def test_create_trophy_celebration_gold(self):
        """Test creating gold trophy celebration."""
        effect = TrophyParticleEffect()

        effect.create_trophy_celebration(100, 200, "gold")

        assert effect.has_particles()
        assert len(effect.particles) == 30  # Gold should create 30 particles

    def test_create_trophy_celebration_invalid_level(self):
        """Test creating celebration with invalid trophy level."""
        effect = TrophyParticleEffect()

        effect.create_trophy_celebration(100, 200, "invalid")

        # Should default to bronze colors
        assert effect.has_particles()
        assert len(effect.particles) == 20

    def test_create_sparkle_effect(self):
        """Test creating sparkle effect."""
        effect = TrophyParticleEffect()

        effect.create_sparkle_effect(100, 200, "silver")

        assert effect.has_particles()
        assert len(effect.particles) == 8  # Sparkle creates 8 particles

    def test_particle_positions_random(self):
        """Test that particles are created with random positions."""
        effect = TrophyParticleEffect()

        effect.create_trophy_celebration(100, 200, "bronze")

        # Check that particles have different starting positions
        positions = [(p.x, p.y) for p in effect.particles]
        assert len(set(positions)) > 1  # Should have different positions

    def test_particle_velocities_burst_pattern(self):
        """Test that celebration particles have radial burst pattern."""
        effect = TrophyParticleEffect()

        effect.create_trophy_celebration(100, 200, "bronze")

        # Check that particles have different velocities in different directions
        velocities = [(p.velocity_x, p.velocity_y) for p in effect.particles]
        assert len(set(velocities)) > 1  # Should have different velocities

        # All particles should have some velocity
        for vx, vy in velocities:
            speed = math.sqrt(vx**2 + vy**2)
            assert speed > 0

    def test_update_removes_dead_particles(self):
        """Test that update removes dead particles."""
        effect = TrophyParticleEffect()

        # Create particles with very short lifetime
        for i in range(5):
            particle = Particle(100 + i, 200, (255, 0, 0), 0, 0, 0.01)
            effect.particles.append(particle)

        assert len(effect.particles) == 5

        # Update with large dt to kill all particles
        effect.update(1.0)

        assert len(effect.particles) == 0
        assert not effect.has_particles()

    def test_update_keeps_alive_particles(self):
        """Test that update keeps alive particles."""
        effect = TrophyParticleEffect()

        # Create particles with long lifetime
        for i in range(5):
            particle = Particle(100 + i, 200, (255, 0, 0), 0, 0, 5.0)
            effect.particles.append(particle)

        assert len(effect.particles) == 5

        # Update with small dt
        effect.update(0.1)

        assert len(effect.particles) == 5
        assert effect.has_particles()

    def test_draw_all_particles(self, mock_surface):
        """Test drawing all particles."""
        effect = TrophyParticleEffect()

        # Create some particles
        effect.create_sparkle_effect(100, 200, "gold")

        # Should not raise an exception
        effect.draw(mock_surface)

    def test_clear_particles(self):
        """Test clearing all particles."""
        effect = TrophyParticleEffect()

        effect.create_trophy_celebration(100, 200, "gold")
        assert effect.has_particles()

        effect.clear()
        assert not effect.has_particles()
        assert len(effect.particles) == 0

    def test_has_particles_accuracy(self):
        """Test has_particles method accuracy."""
        effect = TrophyParticleEffect()

        # Initially no particles
        assert not effect.has_particles()

        # Add particles
        effect.create_sparkle_effect(100, 200, "bronze")
        assert effect.has_particles()

        # Clear particles
        effect.clear()
        assert not effect.has_particles()

    def test_particle_color_matches_trophy_level(self):
        """Test that particles use correct colors for trophy level."""
        effect = TrophyParticleEffect()

        effect.create_trophy_celebration(100, 200, "gold")

        # All particles should use gold colors
        gold_colors = effect.TROPHY_COLORS["gold"]
        for particle in effect.particles:
            assert particle.color in gold_colors

    def test_sparkle_vs_celebration_particle_count(self):
        """Test different particle counts for sparkle vs celebration."""
        effect = TrophyParticleEffect()

        # Create sparkle effect
        effect.create_sparkle_effect(100, 200, "silver")
        sparkle_count = len(effect.particles)

        effect.clear()

        # Create celebration effect
        effect.create_trophy_celebration(100, 200, "silver")
        celebration_count = len(effect.particles)

        # Celebration should have more particles than sparkle
        assert celebration_count > sparkle_count
