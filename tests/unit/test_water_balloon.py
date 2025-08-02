import pygame

# Postpone pygame init and import to avoid import order issues
from src.scenes.pool import WaterBalloon

# Initialize pygame for the tests
pygame.init()


class TestWaterBalloon:
    """Test water balloon functionality to prevent crashes."""

    def test_water_balloon_draw_no_crash(self):
        """Test that water balloon draw method doesn't crash due to pygame shadowing."""
        # Create a test surface
        screen = pygame.Surface((100, 100))

        # Create a water balloon
        balloon = WaterBalloon(50, 50, 100, 100)

        # Add some trail positions
        balloon.trail = [(45, 45), (47, 47), (49, 49)]

        # This should not crash
        balloon.draw(screen)

        # Verify balloon is still active
        assert balloon.active is True

    def test_water_balloon_trail_effect(self):
        """Test that trail effect renders correctly."""
        screen = pygame.Surface((200, 200))

        balloon = WaterBalloon(100, 100, 150, 150)

        # Update a few times to build trail
        for _ in range(5):
            balloon.update(0.1)

        # Should have trail positions
        assert len(balloon.trail) > 0

        # Drawing should work without errors
        balloon.draw(screen)
