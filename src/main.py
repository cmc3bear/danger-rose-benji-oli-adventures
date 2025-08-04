import logging
import sys
from pathlib import Path

import pygame

from src.config.constants import (
    COLOR_BLACK,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WINDOW_TITLE,
)
from src.config.env_config import is_debug
from src.config.game_config import get_config
from src.scene_manager import SceneManager
from src.systems.game_state_logger import initialize_global_logger, shutdown_global_logger
from src.utils.kid_friendly_errors import kid_friendly_handler, create_error_dialog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def game():
    # Initialize Pygame
    pygame.init()
    clock = pygame.time.Clock()

    # Get configuration
    config = get_config()
    
    # Initialize game state logger
    project_root = str(Path(__file__).parent.parent)
    game_logger = initialize_global_logger(project_root, enable_live_overlay=True)
    logger.info("Game state logging system initialized")

    # Game screen setup
    if config.fullscreen:
        screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN
        )
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    # Initialize scene manager
    scene_manager = SceneManager(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Load test procedures for Issue #34 if in debug mode
    if is_debug():
        try:
            procedures = scene_manager.load_test_procedures_for_issue(34)
            logger.info(f"Loaded {len(procedures)} test procedures for Issue #34")
        except Exception as e:
            logger.warning(f"Could not load test procedures: {e}")

    # Main game loop
    while True:
        # Calculate delta time
        dt = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Shutdown logging system gracefully
                shutdown_global_logger()
                logger.info("Game state logging system shutdown")
                pygame.quit()
                sys.exit()

            # Handle scene events
            scene_manager.handle_event(event)

        # Update game state
        scene_manager.update(dt)

        # Draw everything
        screen.fill(COLOR_BLACK)  # Clear screen
        scene_manager.draw(screen)

        # Show FPS if enabled
        if config.show_fps or is_debug():
            fps = clock.get_fps()
            font = pygame.font.Font(None, 36)
            fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
            screen.blit(fps_text, (10, 10))

        pygame.display.flip()  # Update the display


if __name__ == "__main__":
    try:
        game()
    except Exception as e:
        # Use kid-friendly error handling
        error_dialog = create_error_dialog(e, {
            'character': 'the game',
            'action_hint': 'Try restarting the game or check if all files are in place!'
        })
        
        print(f"\n{error_dialog['icon']} {error_dialog['title']}")
        print("=" * 50)
        print(error_dialog['message'])
        print("-" * 50)
        print(error_dialog['comfort'])
        
        # Also log for developers
        logger.error(f"Game crashed with error: {type(e).__name__}: {e}")
        
        # Keep window open so kids can read the message
        input("\nPress Enter to close...")
        
        # Clean shutdown
        try:
            shutdown_global_logger()
            pygame.quit()
        except:
            pass
