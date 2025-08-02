"""Enhanced Hacker Typing Challenge scene."""

import pygame
from typing import Any, Optional

from src.scenes.base_scene import Scene
from src.config.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from .hacker_typing.hacker_typing_scene import HackerTypingScene as EnhancedHackerTyping


class HackerTypingScene(Scene):
    """Wrapper scene for the enhanced hacker typing mini-game."""
    
    def __init__(self, game):
        """Initialize the hacker typing scene wrapper.
        
        Args:
            game: Game instance with scene_manager
        """
        self.game = game
        self.scene_manager = game  # For compatibility
        
        # Create the enhanced typing scene
        self.typing_scene = EnhancedHackerTyping(self)
        
        # Proxy properties for compatibility
        self.screen = pygame.display.get_surface()
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input events.
        
        Args:
            event: Pygame event
            
        Returns:
            Scene name to switch to, or None
        """
        # Let the enhanced scene handle events
        self.typing_scene.handle_event(event)
        
        # Check if we should return to hub
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.typing_scene.state == self.typing_scene.GameState.MENU:
                return "hub"
        
        return None
    
    def update(self, dt: float) -> None:
        """Update the scene.
        
        Args:
            dt: Delta time in seconds
        """
        self.typing_scene.update(dt)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the scene.
        
        Args:
            screen: Surface to draw on
        """
        self.typing_scene.draw(screen)
    
    def on_enter(self, previous_scene: Optional[str] = None, 
                 data: Optional[dict[str, Any]] = None) -> None:
        """Called when entering the scene.
        
        Args:
            previous_scene: Name of the previous scene
            data: Optional data from previous scene
        """
        self.typing_scene.enter()
    
    def on_exit(self) -> dict[str, Any]:
        """Called when leaving the scene.
        
        Returns:
            Data to pass to next scene
        """
        self.typing_scene.exit()
        return {"from_scene": "hacker_typing"}