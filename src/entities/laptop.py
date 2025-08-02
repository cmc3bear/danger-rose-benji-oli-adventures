"""Interactive laptop entity for accessing the hacker typing mini-game."""

import pygame
from typing import Optional, Tuple
from src.utils.asset_paths import get_image_path
from src.config.constants import SCENE_HACKER_TYPING


class Laptop:
    """Interactive laptop on the living room table."""
    
    def __init__(self, x: int, y: int):
        """Initialize the laptop entity.
        
        Args:
            x: X position on table
            y: Y position on table
        """
        self.x = x
        self.y = y
        self.width = 64
        self.height = 48
        
        # Interaction properties
        self.is_open = False
        self.is_glowing = False
        self.interaction_range = 80
        self.interaction_cooldown = 0.0
        
        # Visual properties
        self.glow_alpha = 0
        self.glow_direction = 1
        self.screen_animation_time = 0.0
        
        # Collision rect
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Load sprites
        self._load_sprites()
        
    def _load_sprites(self):
        """Load laptop sprites or create placeholders."""
        try:
            # Try to load actual sprites
            self.sprite_closed = pygame.image.load(get_image_path("entities/laptop_closed.png"))
            self.sprite_open = pygame.image.load(get_image_path("entities/laptop_open.png"))
        except (pygame.error, FileNotFoundError):
            # Create placeholder sprites
            self._create_placeholder_sprites()
            
    def _create_placeholder_sprites(self):
        """Create placeholder laptop sprites with hacker aesthetic."""
        # Closed laptop
        self.sprite_closed = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Laptop body (dark gray)
        pygame.draw.rect(self.sprite_closed, (40, 40, 45), (0, 10, self.width, self.height - 10))
        pygame.draw.rect(self.sprite_closed, (60, 60, 65), (0, 10, self.width, self.height - 10), 2)
        
        # Laptop lid (slightly lighter)
        pygame.draw.rect(self.sprite_closed, (50, 50, 55), (2, 0, self.width - 4, 12))
        pygame.draw.rect(self.sprite_closed, (70, 70, 75), (2, 0, self.width - 4, 12), 1)
        
        # Logo/decoration
        logo_rect = pygame.Rect(self.width // 2 - 8, 2, 16, 8)
        pygame.draw.rect(self.sprite_closed, (0, 255, 0), logo_rect)
        
        # Open laptop
        self.sprite_open = pygame.Surface((self.width, self.height + 20), pygame.SRCALPHA)
        
        # Base (keyboard area)
        pygame.draw.rect(self.sprite_open, (40, 40, 45), (0, self.height - 10, self.width, 30))
        pygame.draw.rect(self.sprite_open, (60, 60, 65), (0, self.height - 10, self.width, 30), 2)
        
        # Keyboard indication
        for row in range(3):
            for col in range(10):
                key_x = 6 + col * 5
                key_y = self.height - 5 + row * 4
                pygame.draw.rect(self.sprite_open, (30, 30, 35), (key_x, key_y, 3, 3))
        
        # Screen (standing up)
        screen_rect = pygame.Rect(4, 0, self.width - 8, self.height - 12)
        pygame.draw.rect(self.sprite_open, (20, 20, 25), screen_rect)
        pygame.draw.rect(self.sprite_open, (80, 80, 85), screen_rect, 2)
        
        # Screen content (Matrix-style)
        for i in range(5):
            for j in range(8):
                if (i + j) % 3 == 0:
                    char_x = 8 + j * 6
                    char_y = 4 + i * 7
                    color = (0, 200 - i * 30, 0)
                    pygame.draw.rect(self.sprite_open, color, (char_x, char_y, 4, 5))
        
        # Glowing keyboard backlighting
        for row in range(3):
            for col in range(10):
                if (row + col) % 2 == 0:
                    key_x = 6 + col * 5
                    key_y = self.height - 5 + row * 4
                    glow_surf = pygame.Surface((5, 5), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (0, 255, 0, 50), (2, 2), 3)
                    self.sprite_open.blit(glow_surf, (key_x - 1, key_y - 1))
    
    def update(self, dt: float, player_pos: Tuple[int, int]):
        """Update laptop state.
        
        Args:
            dt: Delta time in seconds
            player_pos: Player position (x, y)
        """
        # Update cooldown
        if self.interaction_cooldown > 0:
            self.interaction_cooldown -= dt
            
        # Check if player is near
        player_x, player_y = player_pos
        distance = ((player_x - self.x - self.width // 2) ** 2 + 
                   (player_y - self.y - self.height // 2) ** 2) ** 0.5
        
        self.is_glowing = distance <= self.interaction_range
        
        # Update glow effect
        if self.is_glowing:
            self.glow_alpha += self.glow_direction * 3
            if self.glow_alpha >= 100:
                self.glow_alpha = 100
                self.glow_direction = -1
            elif self.glow_alpha <= 20:
                self.glow_alpha = 20
                self.glow_direction = 1
        else:
            self.glow_alpha = max(0, self.glow_alpha - 5)
            
        # Update screen animation
        if self.is_open:
            self.screen_animation_time += dt
    
    def handle_interaction(self) -> Optional[str]:
        """Handle player interaction with laptop.
        
        Returns:
            Scene name to transition to, or None
        """
        if self.interaction_cooldown > 0:
            return None
            
        self.interaction_cooldown = 0.5
        self.is_open = not self.is_open
        
        if self.is_open:
            # Transition to hacker typing scene
            return SCENE_HACKER_TYPING
        
        return None
    
    def draw(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Draw the laptop.
        
        Args:
            screen: Surface to draw on
            camera_offset: Camera offset for scrolling
        """
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        
        # Draw laptop sprite
        if self.is_open:
            screen.blit(self.sprite_open, (draw_x, draw_y - 20))
        else:
            screen.blit(self.sprite_closed, (draw_x, draw_y))
        
        # Draw glow effect when player is near
        if self.glow_alpha > 0:
            glow_surf = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            glow_color = (0, 255, 0, int(self.glow_alpha))
            pygame.draw.ellipse(glow_surf, glow_color, glow_surf.get_rect(), 3)
            screen.blit(glow_surf, (draw_x - 10, draw_y - 10))
            
        # Draw interaction prompt
        if self.is_glowing and not self.is_open:
            self._draw_prompt(screen, draw_x + self.width // 2, draw_y - 20)
    
    def _draw_prompt(self, screen: pygame.Surface, x: int, y: int):
        """Draw interaction prompt.
        
        Args:
            screen: Surface to draw on
            x: Center X position
            y: Center Y position
        """
        font = pygame.font.Font(None, 20)
        text = "Press E to hack"
        text_surface = font.render(text, True, (0, 255, 0))
        text_rect = text_surface.get_rect(center=(x, y))
        
        # Background
        bg_rect = text_rect.inflate(10, 5)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        
        # Text
        screen.blit(text_surface, text_rect)
    
    def get_collision_rect(self) -> pygame.Rect:
        """Get collision rectangle.
        
        Returns:
            Collision rectangle
        """
        return self.rect