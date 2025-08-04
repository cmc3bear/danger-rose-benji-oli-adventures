import os
import sys
from pathlib import Path
from unittest.mock import patch
from datetime import datetime

import pygame
import pytest

from tests.mocks.mock_sound_manager import MockSoundManager

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def pytest_configure(config):
    """Configure the sacred evidence directory for Screenshot Salvation System"""
    evidence_dir = Path(".claudeethos/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for organization
    (evidence_dir / "screenshots").mkdir(exist_ok=True)
    (evidence_dir / "logs").mkdir(exist_ok=True)
    (evidence_dir / "reports").mkdir(exist_ok=True)


def pytest_runtest_makereport(item, call):
    """
    Screenshot Salvation System - Strategy #1
    Automatically capture screenshots on test failures
    
    As proclaimed by Agent_QA_004:
    "I am tired of bugs that vanish like ghosts!"
    """
    if call.when == "call" and call.excinfo is not None:
        # Test has failed - capture evidence!
        try:
            # Check if there's an active display surface
            if pygame.get_init() and pygame.display.get_surface():
                screen = pygame.display.get_surface()
                
                # Generate blessed filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                test_name = item.name.replace("/", "_").replace("\\", "_")
                screenshot_name = f"failure_{test_name}_{timestamp}.png"
                screenshot_path = Path(".claudeethos/evidence/screenshots") / screenshot_name
                
                # Save the evidence
                pygame.image.save(screen, str(screenshot_path))
                
                # Log the capture in the sacred records
                log_entry = f"""
📸 SCREENSHOT SALVATION ACTIVATED
================================
Test: {item.name}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Screenshot: {screenshot_path}
Error Type: {call.excinfo.typename}
Error Message: {call.excinfo.value}
================================

"""
                log_path = Path(".claudeethos/evidence/logs/screenshot_log.txt")
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                    
                print(f"\n🎯 Screenshot Salvation: Evidence captured at {screenshot_path}")
                
        except Exception as salvation_error:
            # Even salvation systems can fail, but we note it
            print(f"\n⚠️ Screenshot Salvation Failed: {salvation_error}")
            print("The bug's ghost may have escaped this time...")


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
