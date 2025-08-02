"""Settings scene for Danger Rose game.

This scene allows players to adjust game settings including
audio, display, controls, and accessibility options.
"""

from typing import Any

import pygame

from src.config.constants import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_WHITE,
    SCENE_TITLE,
)
from src.config.game_config import get_config


class SettingsScene:
    """Settings menu scene for configuring game options."""

    def __init__(self, screen_width: int, screen_height: int, sound_manager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = get_config()
        self.sound_manager = sound_manager
        self.paused_scene = None  # Track if we came from pause menu

        # UI elements
        self.font_title = pygame.font.Font(None, 72)
        self.font_label = pygame.font.Font(None, 36)
        self.font_button = pygame.font.Font(None, 32)

        # Back button
        self.back_button = pygame.Rect(50, 50, BUTTON_WIDTH, BUTTON_HEIGHT)

        # Volume sliders
        self.master_volume_rect = pygame.Rect(
            self.screen_width // 2 - 200, 200, 400, 40
        )
        self.music_volume_rect = pygame.Rect(self.screen_width // 2 - 200, 300, 400, 40)
        self.sfx_volume_rect = pygame.Rect(self.screen_width // 2 - 200, 400, 400, 40)

        # Fullscreen toggle
        self.fullscreen_rect = pygame.Rect(self.screen_width // 2 - 100, 500, 200, 50)

        # Key bindings
        self.key_binding_rects = {}
        self.key_labels = ["Up", "Down", "Left", "Right", "Jump", "Attack"]
        self.key_configs = ["up", "down", "left", "right", "jump", "attack"]

        # Create rectangles for key bindings
        start_y = 600
        for i, label in enumerate(self.key_labels):
            rect = pygame.Rect(self.screen_width // 2 - 150, start_y + i * 50, 300, 40)
            self.key_binding_rects[self.key_configs[i]] = rect

        # State
        self.dragging_slider: str | None = None
        self.rebinding_key: str | None = None  # Which key is being rebound
        self.waiting_for_key = False  # Are we waiting for a key press?
        self.selected_player = "player1"  # Currently selected player for rebinding

        # Keyboard navigation
        self.focusable_elements = [
            "master_volume",
            "music_volume",
            "sfx_volume",
            "fullscreen",
            "up",
            "down",
            "left",
            "right",
            "jump",
            "attack",
            "back",
        ]
        self.focused_element_index = 0

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Handle input events.

        Args:
            event: Pygame event to process.

        Returns:
            Scene name to transition to, or None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Check back button
            if self.back_button.collidepoint(mouse_pos):
                # Save settings before going back
                self.config.save()
                # Return to paused scene if we came from pause menu, otherwise title
                if self.paused_scene:
                    return_scene = self.paused_scene
                    self.paused_scene = None  # Reset for next time
                    return return_scene
                return SCENE_TITLE

            # Check fullscreen toggle
            if self.fullscreen_rect.collidepoint(mouse_pos):
                self.config.fullscreen = not self.config.fullscreen
                # Note: Actual fullscreen toggle would require recreating the display

            # Check key binding buttons
            if not self.waiting_for_key:
                for key, rect in self.key_binding_rects.items():
                    if rect.collidepoint(mouse_pos):
                        self.rebinding_key = key
                        self.waiting_for_key = True
                        break

            # Check volume sliders
            if self.master_volume_rect.collidepoint(mouse_pos):
                self.dragging_slider = "master"
            elif self.music_volume_rect.collidepoint(mouse_pos):
                self.dragging_slider = "music"
            elif self.sfx_volume_rect.collidepoint(mouse_pos):
                self.dragging_slider = "sfx"

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_slider = None

        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            # Update volume based on mouse position
            mouse_x = event.pos[0]

            if self.dragging_slider == "master":
                relative_x = mouse_x - self.master_volume_rect.x
                volume = max(0.0, min(1.0, relative_x / self.master_volume_rect.width))
                self.config.master_volume = volume
                self.sound_manager.set_master_volume(volume)

            elif self.dragging_slider == "music":
                relative_x = mouse_x - self.music_volume_rect.x
                volume = max(0.0, min(1.0, relative_x / self.music_volume_rect.width))
                self.config.music_volume = volume
                self.sound_manager.set_music_volume(volume)

            elif self.dragging_slider == "sfx":
                relative_x = mouse_x - self.sfx_volume_rect.x
                volume = max(0.0, min(1.0, relative_x / self.sfx_volume_rect.width))
                self.config.sfx_volume = volume
                self.sound_manager.set_sfx_volume(volume)

        elif event.type == pygame.KEYDOWN:
            if self.waiting_for_key:
                # Cancel rebinding on ESC
                if event.key == pygame.K_ESCAPE:
                    self.waiting_for_key = False
                    self.rebinding_key = None
                else:
                    # Set the new key binding
                    key_name = pygame.key.name(event.key)
                    control_path = (
                        f"controls.{self.selected_player}.{self.rebinding_key}"
                    )
                    self.config.set(control_path, key_name)
                    self.waiting_for_key = False
                    self.rebinding_key = None
            elif event.key == pygame.K_ESCAPE:
                self.config.save()
                return SCENE_TITLE
            elif event.key == pygame.K_TAB:
                # Navigate through focusable elements
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.focused_element_index = (self.focused_element_index - 1) % len(
                        self.focusable_elements
                    )
                else:
                    self.focused_element_index = (self.focused_element_index + 1) % len(
                        self.focusable_elements
                    )
            elif event.key in [pygame.K_UP, pygame.K_DOWN]:
                # Navigate vertically
                if event.key == pygame.K_UP:
                    self.focused_element_index = (self.focused_element_index - 1) % len(
                        self.focusable_elements
                    )
                else:
                    self.focused_element_index = (self.focused_element_index + 1) % len(
                        self.focusable_elements
                    )
            elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                # Adjust volume sliders or toggle fullscreen
                focused = self.focusable_elements[self.focused_element_index]
                if focused == "master_volume":
                    delta = 0.05 if event.key == pygame.K_RIGHT else -0.05
                    self.config.master_volume = max(
                        0.0, min(1.0, self.config.master_volume + delta)
                    )
                    self.sound_manager.set_master_volume(self.config.master_volume)
                elif focused == "music_volume":
                    delta = 0.05 if event.key == pygame.K_RIGHT else -0.05
                    self.config.music_volume = max(
                        0.0, min(1.0, self.config.music_volume + delta)
                    )
                    self.sound_manager.set_music_volume(self.config.music_volume)
                elif focused == "sfx_volume":
                    delta = 0.05 if event.key == pygame.K_RIGHT else -0.05
                    self.config.sfx_volume = max(
                        0.0, min(1.0, self.config.sfx_volume + delta)
                    )
                    self.sound_manager.set_sfx_volume(self.config.sfx_volume)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                # Activate focused element
                focused = self.focusable_elements[self.focused_element_index]
                if focused == "fullscreen":
                    self.config.fullscreen = not self.config.fullscreen
                elif focused in self.key_configs:
                    self.rebinding_key = focused
                    self.waiting_for_key = True
                elif focused == "back":
                    self.config.save()
                    if self.paused_scene:
                        return_scene = self.paused_scene
                        self.paused_scene = None
                        return return_scene
                    return SCENE_TITLE

        return None

    def update(self, dt: float = 0.0) -> None:
        """Update scene state.

        Args:
            dt: Time delta in seconds (optional, defaults to 0.0).
        """
        # Settings scene doesn't need animation updates
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the settings scene.

        Args:
            screen: Surface to draw on.
        """
        # Clear screen
        screen.fill(COLOR_BLACK)

        # Title
        title_surface = self.font_title.render("Settings", True, COLOR_WHITE)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title_surface, title_rect)

        # Volume controls
        focused_element = self.focusable_elements[self.focused_element_index]
        self._draw_volume_slider(
            screen,
            "Master Volume",
            self.master_volume_rect,
            self.config.master_volume,
            150,
            focused_element == "master_volume",
        )
        self._draw_volume_slider(
            screen,
            "Music Volume",
            self.music_volume_rect,
            self.config.music_volume,
            250,
            focused_element == "music_volume",
        )
        self._draw_volume_slider(
            screen,
            "SFX Volume",
            self.sfx_volume_rect,
            self.config.sfx_volume,
            350,
            focused_element == "sfx_volume",
        )

        # Fullscreen toggle
        fullscreen_text = "Fullscreen: " + ("ON" if self.config.fullscreen else "OFF")
        fullscreen_surface = self.font_label.render(fullscreen_text, True, COLOR_WHITE)
        fullscreen_rect = fullscreen_surface.get_rect(
            center=(self.screen_width // 2, 525)
        )
        screen.blit(fullscreen_surface, fullscreen_rect)
        fullscreen_border_color = (
            (255, 255, 100) if focused_element == "fullscreen" else COLOR_WHITE
        )
        pygame.draw.rect(
            screen,
            fullscreen_border_color,
            self.fullscreen_rect,
            3 if focused_element == "fullscreen" else 2,
        )

        # Key bindings section
        controls_title = self.font_label.render(
            "Key Bindings (Player 1)", True, COLOR_WHITE
        )
        controls_rect = controls_title.get_rect(center=(self.screen_width // 2, 580))
        screen.blit(controls_title, controls_rect)

        # Draw key binding buttons
        for i, (key, label) in enumerate(
            zip(self.key_configs, self.key_labels, strict=False)
        ):
            rect = self.key_binding_rects[key]

            # Highlight if this key is being rebound
            if self.waiting_for_key and self.rebinding_key == key:
                pygame.draw.rect(screen, (100, 100, 255), rect)
                key_text = "Press any key..."
            else:
                pygame.draw.rect(screen, (60, 60, 60), rect)
                # Get current key binding
                current_key = self.config.get(
                    f"controls.{self.selected_player}.{key}", "?"
                )
                key_text = f"{label}: {current_key.upper()}"

            border_color = (255, 255, 100) if focused_element == key else COLOR_WHITE
            pygame.draw.rect(
                screen, border_color, rect, 3 if focused_element == key else 2
            )

            # Draw the label and key
            text_surface = self.font_button.render(key_text, True, COLOR_WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)

        # Back button
        back_color = (100, 150, 255) if focused_element == "back" else COLOR_BLUE
        pygame.draw.rect(screen, back_color, self.back_button)
        back_border_color = (
            (255, 255, 100) if focused_element == "back" else COLOR_WHITE
        )
        pygame.draw.rect(
            screen,
            back_border_color,
            self.back_button,
            3 if focused_element == "back" else 2,
        )
        back_text = self.font_button.render("Back", True, COLOR_WHITE)
        back_rect = back_text.get_rect(center=self.back_button.center)
        screen.blit(back_text, back_rect)

    def _draw_volume_slider(
        self,
        screen: pygame.Surface,
        label: str,
        rect: pygame.Rect,
        value: float,
        y_pos: int,
        is_focused: bool = False,
    ) -> None:
        """Draw a volume slider.

        Args:
            screen: Surface to draw on.
            label: Label for the slider.
            rect: Rectangle for the slider track.
            value: Current value (0.0 to 1.0).
            y_pos: Y position for the label.
        """
        # Label
        label_surface = self.font_label.render(label, True, COLOR_WHITE)
        label_rect = label_surface.get_rect(center=(self.screen_width // 2, y_pos))
        screen.blit(label_surface, label_rect)

        # Slider track
        pygame.draw.rect(screen, (60, 60, 60), rect)
        border_color = (255, 255, 100) if is_focused else COLOR_WHITE
        pygame.draw.rect(screen, border_color, rect, 3 if is_focused else 2)

        # Slider fill
        fill_width = int(rect.width * value)
        fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
        pygame.draw.rect(screen, COLOR_BLUE, fill_rect)

        # Slider handle
        handle_x = rect.x + fill_width
        handle_rect = pygame.Rect(handle_x - 5, rect.y - 5, 10, rect.height + 10)
        pygame.draw.rect(screen, COLOR_WHITE, handle_rect)

        # Value text
        value_text = f"{int(value * 100)}%"
        value_surface = self.font_button.render(value_text, True, COLOR_WHITE)
        value_rect = value_surface.get_rect(midleft=(rect.right + 20, rect.centery))
        screen.blit(value_surface, value_rect)

    def on_enter(
        self, previous_scene: str | None, data: dict[str, Any] | None = None
    ) -> None:
        """Called when entering this scene.

        Args:
            previous_scene: Name of the previous scene.
            data: Optional data passed from previous scene.
        """
        # Reload config in case it was changed elsewhere
        self.config = get_config()

    def on_exit(self) -> dict[str, Any]:
        """Called when leaving this scene.

        Returns:
            Data to pass to the next scene.
        """
        # Save any pending changes
        if self.config.is_modified():
            self.config.save()
        return {}
