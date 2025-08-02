import logging
import sys

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def game():
    # Initialize Pygame
    pygame.init()
    clock = pygame.time.Clock()

    # Get configuration
    config = get_config()

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

    # Main game loop
    while True:
        # Calculate delta time
        dt = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
    game()
