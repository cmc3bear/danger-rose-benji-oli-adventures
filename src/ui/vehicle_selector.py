"""Vehicle selector UI component for The Drive minigame."""

import pygame
import math
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from src.utils.sprite_loader import load_vehicle_sprite
from src.managers.sound_manager import SoundManager
from src.config.constants import (
    COLOR_WHITE,
    COLOR_BLACK,
    COLOR_YELLOW,
    COLOR_GREEN,
    COLOR_RED,
    FONT_SMALL,
    FONT_LARGE,
    FONT_HUGE,
)


class Vehicle:
    """Represents a selectable vehicle option."""
    
    def __init__(self, id: str, name: str, sprite_name: str, description: str = ""):
        self.id = id
        self.name = name
        self.sprite_name = sprite_name
        self.description = description
        self.sprite = None
        self.preview_sprite = None


class VehicleSelector:
    """UI component for selecting vehicles before racing."""
    
    def __init__(self, screen_width: int, screen_height: int, sound_manager: SoundManager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sound_manager = sound_manager
        
        # Initialize vehicles
        self.vehicles = [
            Vehicle(
                "professional",
                "Professional EV",
                "professional",
                "Sleek and modern electric vehicle"
            ),
            Vehicle(
                "kids_drawing",
                "Kid's Drawing",
                "kids_drawing",
                "Charming crayon-style artwork"
            )
        ]
        
        # UI state
        self.selected_index = 0
        self.state = "selecting"  # selecting, confirmed
        self.animation_time = 0
        self.confirm_animation_time = 0
        
        # Colors
        self.bg_color = (20, 20, 40)
        self.card_color = (40, 40, 60)
        self.selected_color = (60, 60, 100)
        self.text_color = COLOR_WHITE
        self.highlight_color = COLOR_YELLOW
        
        # Layout
        self.card_width = 300
        self.card_height = 400
        self.card_spacing = 50
        self.cards_y = screen_height // 2 - self.card_height // 2
        
        # Fonts
        try:
            self.title_font = pygame.font.Font(None, FONT_HUGE)
            self.name_font = pygame.font.Font(None, FONT_LARGE)
            self.desc_font = pygame.font.Font(None, FONT_SMALL)
            self.instruction_font = pygame.font.Font(None, FONT_SMALL)
        except pygame.error:
            # Fallback to default font
            self.title_font = pygame.font.SysFont("Arial", FONT_HUGE)
            self.name_font = pygame.font.SysFont("Arial", FONT_LARGE)
            self.desc_font = pygame.font.SysFont("Arial", FONT_SMALL)
            self.instruction_font = pygame.font.SysFont("Arial", FONT_SMALL)
        
        # Load vehicle sprites
        self._load_sprites()
        
    def _load_sprites(self):
        """Load vehicle sprites for preview."""
        for vehicle in self.vehicles:
            try:
                # Load the full sprite
                vehicle.sprite = load_vehicle_sprite(vehicle.sprite_name)
                
                # Create preview sprite (scaled down for cards)
                preview_width = 200
                preview_height = int(preview_width * 1.5)  # Maintain aspect ratio
                vehicle.preview_sprite = pygame.transform.scale(
                    vehicle.sprite,
                    (preview_width, preview_height)
                )
            except Exception as e:
                print(f"[ERROR] Failed to load vehicle sprite {vehicle.sprite_name}: {e}")
                # Create placeholder
                vehicle.sprite = pygame.Surface((128, 192))
                vehicle.sprite.fill(COLOR_RED)
                vehicle.preview_sprite = pygame.Surface((200, 300))
                vehicle.preview_sprite.fill(COLOR_RED)
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input events.
        
        Returns:
            "vehicle_selected" when vehicle is confirmed
            "cancelled" when selection is cancelled
            None otherwise
        """
        if self.state == "confirmed":
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._select_previous()
                return None
            elif event.key == pygame.K_RIGHT:
                self._select_next()
                return None
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._confirm_selection()
                return "vehicle_selected"
            elif event.key == pygame.K_ESCAPE:
                return "cancelled"
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if click is on a vehicle card
                mouse_x, mouse_y = event.pos
                for i, card_x in enumerate(self._get_card_positions()):
                    card_rect = pygame.Rect(
                        card_x, self.cards_y,
                        self.card_width, self.card_height
                    )
                    if card_rect.collidepoint(mouse_x, mouse_y):
                        if i == self.selected_index:
                            # Double-click to confirm
                            self._confirm_selection()
                            return "vehicle_selected"
                        else:
                            self.selected_index = i
                            try:
                                self.sound_manager.play_sfx("menu_move.ogg")
                            except Exception:
                                pass  # Sound file might not be available
                            
        return None
    
    def _select_previous(self):
        """Select the previous vehicle."""
        if self.selected_index > 0:
            self.selected_index -= 1
            try:
                self.sound_manager.play_sfx("menu_move.ogg")
            except Exception:
                pass  # Sound file might not be available
    
    def _select_next(self):
        """Select the next vehicle."""
        if self.selected_index < len(self.vehicles) - 1:
            self.selected_index += 1
            try:
                self.sound_manager.play_sfx("menu_move.ogg")
            except Exception:
                pass  # Sound file might not be available
    
    def _confirm_selection(self):
        """Confirm the current selection."""
        self.state = "confirmed"
        self.confirm_animation_time = 0
        try:
            self.sound_manager.play_sfx("menu_select.ogg")
        except Exception:
            pass  # Sound file might not be available
    
    def get_selected_vehicle(self) -> str:
        """Get the ID of the selected vehicle."""
        return self.vehicles[self.selected_index].id
    
    def _get_card_positions(self) -> list[int]:
        """Calculate x positions for vehicle cards."""
        total_width = len(self.vehicles) * self.card_width + (len(self.vehicles) - 1) * self.card_spacing
        start_x = (self.screen_width - total_width) // 2
        
        positions = []
        for i in range(len(self.vehicles)):
            x = start_x + i * (self.card_width + self.card_spacing)
            positions.append(x)
            
        return positions
    
    def update(self, dt: float):
        """Update animations."""
        self.animation_time += dt
        
        if self.state == "confirmed":
            self.confirm_animation_time += dt
    
    def draw(self, screen: pygame.Surface):
        """Draw the vehicle selector UI."""
        # Background
        screen.fill(self.bg_color)
        
        # Title
        title_text = self.title_font.render("Select Your Vehicle", True, self.text_color)
        title_rect = title_text.get_rect(centerx=self.screen_width // 2, y=50)
        screen.blit(title_text, title_rect)
        
        # Vehicle cards
        card_positions = self._get_card_positions()
        
        for i, (vehicle, x) in enumerate(zip(self.vehicles, card_positions)):
            # Card background
            is_selected = i == self.selected_index
            card_color = self.selected_color if is_selected else self.card_color
            
            # Add glow effect for selected card
            if is_selected:
                glow_offset = int(math.sin(self.animation_time * 3) * 5 + 5)
                glow_rect = pygame.Rect(
                    x - glow_offset, self.cards_y - glow_offset,
                    self.card_width + glow_offset * 2,
                    self.card_height + glow_offset * 2
                )
                pygame.draw.rect(screen, self.highlight_color, glow_rect, 3, border_radius=10)
            
            # Draw card
            card_rect = pygame.Rect(x, self.cards_y, self.card_width, self.card_height)
            pygame.draw.rect(screen, card_color, card_rect, border_radius=10)
            pygame.draw.rect(screen, self.text_color, card_rect, 2, border_radius=10)
            
            # Vehicle name
            name_color = self.highlight_color if is_selected else self.text_color
            name_text = self.name_font.render(vehicle.name, True, name_color)
            name_rect = name_text.get_rect(centerx=x + self.card_width // 2, y=self.cards_y + 20)
            screen.blit(name_text, name_rect)
            
            # Vehicle sprite
            if vehicle.preview_sprite:
                sprite_rect = vehicle.preview_sprite.get_rect(
                    centerx=x + self.card_width // 2,
                    centery=self.cards_y + self.card_height // 2
                )
                
                # Bounce animation for selected vehicle
                if is_selected:
                    bounce = math.sin(self.animation_time * 2) * 5
                    sprite_rect.y += int(bounce)
                
                screen.blit(vehicle.preview_sprite, sprite_rect)
            
            # Description
            desc_lines = self._wrap_text(vehicle.description, self.desc_font, self.card_width - 40)
            y_offset = self.cards_y + self.card_height - 80
            for line in desc_lines:
                desc_text = self.desc_font.render(line, True, self.text_color)
                desc_rect = desc_text.get_rect(centerx=x + self.card_width // 2, y=y_offset)
                screen.blit(desc_text, desc_rect)
                y_offset += 25
        
        # Instructions
        if self.state == "selecting":
            instructions = [
                "LEFT/RIGHT - Select Vehicle",
                "ENTER/SPACE - Confirm Selection",
                "ESC - Back"
            ]
            y_offset = self.screen_height - 100
            for instruction in instructions:
                inst_text = self.instruction_font.render(instruction, True, self.text_color)
                inst_rect = inst_text.get_rect(centerx=self.screen_width // 2, y=y_offset)
                screen.blit(inst_text, inst_rect)
                y_offset += 25
        
        # Confirmation animation
        if self.state == "confirmed" and self.confirm_animation_time < 1.0:
            alpha = int(255 * (1 - self.confirm_animation_time))
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.set_alpha(alpha)
            flash_surface.fill(self.highlight_color)
            screen.blit(flash_surface, (0, 0))
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        """Wrap text to fit within a given width."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines