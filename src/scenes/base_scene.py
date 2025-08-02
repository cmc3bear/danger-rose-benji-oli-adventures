"""Base Scene class for all game scenes."""

from abc import ABC, abstractmethod
from typing import Any

import pygame


class Scene(ABC):
    """Abstract base class for all game scenes."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Handle input events.

        Args:
            event: Pygame event to handle

        Returns:
            Next scene name if transitioning, None otherwise
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the scene state.

        Args:
            dt: Delta time in seconds
        """
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the scene.

        Args:
            screen: Screen surface to draw on
        """
        pass

    def on_enter(
        self,
        previous_scene: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Called when entering this scene.

        Args:
            previous_scene: Name of the previous scene
            data: Optional data passed from previous scene
        """
        pass

    def on_exit(self) -> dict[str, Any]:
        """Called when leaving this scene.

        Returns:
            Any data to pass to the next scene
        """
        return {}
