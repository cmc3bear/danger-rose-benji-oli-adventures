import pygame

from src.config.constants import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_WHITE,
    SCENE_SETTINGS,
    SCENE_TITLE,
)
from src.utils.asset_paths import get_sfx_path


class PauseMenu:
    """Overlay pause menu that can be displayed over any game scene."""

    def __init__(self, screen_width: int, screen_height: int, sound_manager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sound_manager = sound_manager
        self.paused_scene = None
        self.paused_surface = None

        # Create semi-transparent overlay
        self.overlay = pygame.Surface((screen_width, screen_height))
        self.overlay.set_alpha(180)
        self.overlay.fill(COLOR_BLACK)

        # Font setup
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 48)

        # Title text
        self.title_surface = self.title_font.render("PAUSED", True, COLOR_WHITE)
        self.title_rect = self.title_surface.get_rect(
            center=(screen_width // 2, screen_height // 4)
        )

        # Menu buttons
        button_spacing = 70
        center_x = screen_width // 2
        start_y = screen_height // 2 - 100

        self.buttons = {
            "resume": {
                "rect": pygame.Rect(
                    center_x - BUTTON_WIDTH // 2,
                    start_y,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT,
                ),
                "text": "Resume",
                "action": "resume",
            },
            "settings": {
                "rect": pygame.Rect(
                    center_x - BUTTON_WIDTH // 2,
                    start_y + button_spacing,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT,
                ),
                "text": "Settings",
                "action": SCENE_SETTINGS,
            },
            "main_menu": {
                "rect": pygame.Rect(
                    center_x - BUTTON_WIDTH // 2,
                    start_y + button_spacing * 2,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT,
                ),
                "text": "Main Menu",
                "action": SCENE_TITLE,
            },
            "quit": {
                "rect": pygame.Rect(
                    center_x - BUTTON_WIDTH // 2,
                    start_y + button_spacing * 3,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT,
                ),
                "text": "Quit Game",
                "action": "quit",
            },
        }

        # Pre-render button text surfaces
        for button in self.buttons.values():
            button["text_surface"] = self.button_font.render(
                button["text"], True, COLOR_WHITE
            )

    def handle_event(self, event) -> str | None:
        """Handle pause menu events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC resumes the game
                self.sound_manager.play_sfx(get_sfx_path("menu_navigate.wav"))
                return "resume"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for button in self.buttons.values():
                if button["rect"].collidepoint(mouse_pos):
                    self.sound_manager.play_sfx(get_sfx_path("menu_select.wav"))
                    return button["action"]

        return None

    def update(self, dt: float):
        """Update pause menu (currently no animations)."""
        pass

    def draw(self, screen):
        """Draw the pause menu overlay."""
        # Draw the paused game scene first
        if self.paused_surface:
            screen.blit(self.paused_surface, (0, 0))

        # Draw semi-transparent overlay
        screen.blit(self.overlay, (0, 0))

        # Draw title
        screen.blit(self.title_surface, self.title_rect)

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons.values():
            # Check if mouse is hovering
            hovered = button["rect"].collidepoint(mouse_pos)
            button_color = (80, 120, 200) if hovered else COLOR_BLUE

            # Draw button background
            pygame.draw.rect(screen, button_color, button["rect"])
            pygame.draw.rect(screen, COLOR_WHITE, button["rect"], 3)

            # Draw button text
            text_rect = button["text_surface"].get_rect(center=button["rect"].center)
            screen.blit(button["text_surface"], text_rect)

    def set_paused_scene(self, scene, surface):
        """Store the paused scene and its last rendered frame."""
        self.paused_scene = scene
        self.paused_surface = surface.copy()

    def on_enter(self, previous_scene, data):
        """Called when pause menu is activated."""
        # Store reference to the paused scene if passed in data
        if data and "paused_scene" in data:
            self.paused_scene = data["paused_scene"]
        if data and "paused_surface" in data:
            self.paused_surface = data["paused_surface"]

    def on_exit(self):
        """Called when leaving pause menu."""
        return {"resumed_from_pause": True}
