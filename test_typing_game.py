#!/usr/bin/env python3
"""Simple test script for the Hacker Typing Challenge."""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.scenes.hacker_typing.hacker_typing_scene import HackerTypingScene
from src.config.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class MockSceneManager:
    """Mock scene manager for testing."""
    def switch_scene(self, scene_name):
        print(f"Would switch to scene: {scene_name}")


def main():
    """Run the typing game test."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hacker Typing Challenge - Test")
    clock = pygame.time.Clock()
    
    # Create mock game object
    mock_game = MockSceneManager()
    
    # Create typing scene
    typing_scene = HackerTypingScene(mock_game)
    typing_scene.enter()
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and event.mod & pygame.KMOD_ALT:
                    running = False
                else:
                    typing_scene.handle_event(event)
        
        # Update
        typing_scene.update(dt)
        
        # Draw
        screen.fill((0, 0, 0))
        typing_scene.draw(screen)
        
        # Instructions
        font = pygame.font.Font(None, 24)
        instructions = [
            "Hacker Typing Challenge Test",
            "Press 1-2 to select level (only levels 1-2 have content)",
            "ESC to return to menu, ALT+F4 to quit"
        ]
        
        y = 10
        for text in instructions:
            surface = font.render(text, True, (255, 255, 255))
            screen.blit(surface, (10, y))
            y += 25
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()