import os
import sys
from pathlib import Path
from unittest.mock import patch

import pygame
import pytest

from tests.mocks.mock_sound_manager import MockSoundManager

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session", autouse=True)
def init_pygame_headless():
    """Initialize pygame in headless mode for CI/CD environments."""
    # Set SDL to use dummy video driver for headless operation
    os.environ["SDL_VIDEODRIVER"] = "dummy"

    # Initialize pygame modules
    pygame.init()

    # Set a dummy display for tests that require it
    try:
        pygame.display.set_mode((1, 1))
    except pygame.error:
        # If dummy driver fails, we're likely in a real headless environment
        pass

    yield

    pygame.quit()


@pytest.fixture
def mock_pygame_display():
    """Mock pygame display for tests that need display but shouldn't create windows."""
    with patch("pygame.display.set_mode") as mock_display:
        mock_surface = pygame.Surface((100, 100))
        mock_display.return_value = mock_surface
        yield mock_display


@pytest.fixture
def suppress_pygame_output():
    """Suppress pygame welcome message and other output during tests."""
    import os
    import sys

    # Redirect stdout to devnull during pygame import
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")

    yield

    sys.stdout.close()
    sys.stdout = original_stdout


@pytest.fixture
def mock_sound_manager():
    """Mock SoundManager for all tests that need it."""
    # Create a mock sprite surface
    mock_surface = pygame.Surface((128, 128))

    # Patch at the source - where SoundManager is defined
    with patch("src.managers.sound_manager.SoundManager", MockSoundManager):
        # Also patch where it's imported
        with patch("src.scene_manager.SoundManager", MockSoundManager):
            # Mock sprite loading functions to avoid file dependencies
            with patch("src.utils.sprite_loader.load_image", return_value=mock_surface):
                with patch(
                    "src.utils.sprite_loader.load_sprite_sheet",
                    return_value=[mock_surface] * 4,
                ):
                    with patch(
                        "src.utils.sprite_loader.load_character_animations"
                    ) as mock_animations:
                        with patch("pygame.image.load", return_value=mock_surface):
                            # Return animations dict with mock surfaces
                            mock_animations.return_value = {
                                "walking": [mock_surface] * 4,
                                "jumping": [mock_surface] * 4,
                                "idle": [mock_surface] * 4,
                                "attacking": [mock_surface] * 4,
                            }
                            yield
