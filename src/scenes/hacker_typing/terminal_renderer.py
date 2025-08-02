"""Terminal UI renderer with Matrix-style effects for the Hacker Typing Challenge."""

import pygame
import random
import math
from typing import List, Tuple, Optional
from .typing_engine import CharacterStatus


class TerminalRenderer:
    """Renders the hacker terminal interface with CRT effects."""
    
    # Color scheme - Matrix/Terminal theme
    COLORS = {
        CharacterStatus.PENDING: (100, 100, 100),      # Dark gray
        CharacterStatus.CORRECT: (0, 255, 0),          # Bright green
        CharacterStatus.INCORRECT: (255, 0, 0),        # Red
        CharacterStatus.CURRENT: (255, 255, 0),        # Yellow/Amber
        'background': (0, 10, 0),                      # Very dark green
        'terminal_bg': (0, 20, 0),                     # Dark green
        'terminal_border': (0, 150, 0),               # Medium green
        'matrix_rain': (0, 180, 0),                    # Matrix green
        'ui_text': (0, 200, 0),                        # UI green
        'glow': (0, 255, 0),                           # Bright glow
    }
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Terminal window dimensions
        self.terminal_margin = 50
        self.terminal_rect = pygame.Rect(
            self.terminal_margin,
            self.terminal_margin,
            screen_width - (self.terminal_margin * 2),
            screen_height - (self.terminal_margin * 2)
        )
        
        # Text area within terminal
        self.text_padding = 40
        self.text_area = pygame.Rect(
            self.terminal_rect.x + self.text_padding,
            self.terminal_rect.y + self.text_padding + 100,  # Leave room for header
            self.terminal_rect.width - (self.text_padding * 2),
            self.terminal_rect.height - (self.text_padding * 2) - 150
        )
        
        # Font setup
        self.load_fonts()
        
        # Matrix rain effect
        self.matrix_columns = []
        self.init_matrix_rain()
        
        # CRT effect variables
        self.scanline_offset = 0
        self.flicker_timer = 0
        self.cursor_blink_timer = 0
        self.cursor_visible = True
        
        # UI positioning
        self.header_y = self.terminal_rect.y + 30
        self.stats_y = self.terminal_rect.bottom - 100
    
    def load_fonts(self):
        """Load fonts for the terminal interface."""
        # Try to load monospace fonts
        font_names = ['Consolas', 'Monaco', 'Courier New', 'monospace']
        
        self.main_font = None
        self.ui_font = None
        self.header_font = None
        
        for font_name in font_names:
            try:
                self.main_font = pygame.font.SysFont(font_name, 24)
                self.ui_font = pygame.font.SysFont(font_name, 18)
                self.header_font = pygame.font.SysFont(font_name, 32, bold=True)
                break
            except:
                continue
        
        # Fallback to default font
        if not self.main_font:
            self.main_font = pygame.font.Font(None, 24)
            self.ui_font = pygame.font.Font(None, 18)
            self.header_font = pygame.font.Font(None, 32)
    
    def init_matrix_rain(self):
        """Initialize the Matrix rain effect background."""
        chars = "01アイウエオカキクケコサシスセソタチツテト"
        num_columns = self.screen_width // 15
        
        for i in range(num_columns):
            self.matrix_columns.append({
                'x': i * 15,
                'y': random.randint(-self.screen_height, 0),
                'speed': random.uniform(2, 8),
                'chars': [random.choice(chars) for _ in range(random.randint(10, 30))],
                'brightness': random.uniform(0.3, 1.0)
            })
    
    def update(self, dt: float):
        """Update animation effects."""
        # Update matrix rain
        for column in self.matrix_columns:
            column['y'] += column['speed']
            if column['y'] > self.screen_height:
                column['y'] = -len(column['chars']) * 20
                column['chars'] = [random.choice("01アイウエオカキクケコ") 
                                  for _ in range(random.randint(10, 30))]
        
        # Update CRT effects
        self.scanline_offset = (self.scanline_offset + 1) % 4
        self.flicker_timer += dt
        self.cursor_blink_timer += dt
        
        if self.cursor_blink_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_timer = 0
    
    def render_background(self, screen: pygame.Surface):
        """Render the Matrix rain background effect."""
        # Dark background
        screen.fill(self.COLORS['background'])
        
        # Matrix rain effect
        for column in self.matrix_columns:
            for i, char in enumerate(column['chars']):
                y = column['y'] + i * 20
                if 0 <= y <= self.screen_height:
                    # Fade based on position
                    brightness = max(0, 1 - (i / len(column['chars'])))
                    color = tuple(int(c * brightness * column['brightness']) 
                                 for c in self.COLORS['matrix_rain'])
                    
                    char_surface = self.ui_font.render(char, True, color)
                    screen.blit(char_surface, (column['x'], y))
    
    def render_terminal_frame(self, screen: pygame.Surface):
        """Render the terminal window frame with CRT effects."""
        # Terminal background with slight transparency
        terminal_surface = pygame.Surface(
            (self.terminal_rect.width, self.terminal_rect.height),
            pygame.SRCALPHA
        )
        terminal_surface.fill((*self.COLORS['terminal_bg'], 240))
        
        # Add slight flicker effect
        if random.random() > 0.98:
            alpha = random.randint(230, 255)
            terminal_surface.set_alpha(alpha)
        
        screen.blit(terminal_surface, self.terminal_rect)
        
        # Terminal border with glow effect
        for i in range(3):
            width = 3 - i
            color = tuple(int(c * (1 - i * 0.3)) for c in self.COLORS['terminal_border'])
            pygame.draw.rect(screen, color, self.terminal_rect, width)
        
        # Scanline effect
        for y in range(self.terminal_rect.y, self.terminal_rect.bottom, 4):
            if (y + self.scanline_offset) % 4 < 2:
                pygame.draw.line(
                    screen,
                    (0, 0, 0, 30),
                    (self.terminal_rect.x, y),
                    (self.terminal_rect.right, y)
                )
    
    def render_header(self, screen: pygame.Surface, level_name: str, trace_timer: float):
        """Render the terminal header with level info and trace timer."""
        # Header text
        header_text = f">>> HACKER OS - {level_name.upper()} <<<"
        header_surface = self.header_font.render(header_text, True, self.COLORS['glow'])
        header_rect = header_surface.get_rect(centerx=self.terminal_rect.centerx, y=self.header_y)
        
        # Add glow effect
        for i in range(1, 3):
            glow_color = tuple(int(c * 0.3) for c in self.COLORS['glow'])
            glow_surface = self.header_font.render(header_text, True, glow_color)
            glow_rect = glow_surface.get_rect(center=(header_rect.centerx, header_rect.centery + i))
            screen.blit(glow_surface, glow_rect)
        
        screen.blit(header_surface, header_rect)
        
        # Trace timer
        if trace_timer > 0:
            timer_color = self.COLORS['glow'] if trace_timer > 10 else (255, 255, 0) if trace_timer > 5 else (255, 0, 0)
            timer_text = f"TRACE DETECTION IN: {trace_timer:.1f}s"
            timer_surface = self.ui_font.render(timer_text, True, timer_color)
            timer_rect = timer_surface.get_rect(right=self.terminal_rect.right - 20, y=self.header_y + 40)
            screen.blit(timer_surface, timer_rect)
    
    def render_typing_text(self, screen: pygame.Surface, segments: List[Tuple[str, CharacterStatus]], 
                          wrap_width: Optional[int] = None):
        """Render the typing challenge text with color-coded characters."""
        if not segments:
            return
        
        wrap_width = wrap_width or self.text_area.width
        x = self.text_area.x
        y = self.text_area.y
        line_height = self.main_font.get_height() + 5
        
        for char, status in segments:
            # Handle newlines
            if char == '\n':
                x = self.text_area.x
                y += line_height
                continue
            
            # Get character color
            color = self.COLORS.get(status, self.COLORS[CharacterStatus.PENDING])
            
            # Render character
            char_surface = self.main_font.render(char, True, color)
            char_width = char_surface.get_width()
            
            # Word wrap
            if x + char_width > self.text_area.x + wrap_width:
                x = self.text_area.x
                y += line_height
            
            # Draw character
            screen.blit(char_surface, (x, y))
            
            # Draw cursor on current character
            if status == CharacterStatus.CURRENT and self.cursor_visible:
                cursor_rect = pygame.Rect(x, y + line_height - 3, char_width, 3)
                pygame.draw.rect(screen, self.COLORS['glow'], cursor_rect)
            
            x += char_width
    
    def render_stats(self, screen: pygame.Surface, metrics: dict):
        """Render typing statistics at the bottom of the terminal."""
        # Background for stats
        stats_bg = pygame.Rect(
            self.terminal_rect.x + 10,
            self.stats_y - 10,
            self.terminal_rect.width - 20,
            80
        )
        pygame.draw.rect(screen, self.COLORS['terminal_bg'], stats_bg)
        pygame.draw.rect(screen, self.COLORS['terminal_border'], stats_bg, 1)
        
        # Prepare stats text
        stats = [
            f"HACKING SPEED: {metrics['wpm']:.1f} WPM",
            f"STEALTH RATING: {metrics['accuracy']:.1f}%",
            f"HACK STREAK: {metrics['combo_streak']}",
            f"TIME: {metrics['elapsed_time']:.1f}s"
        ]
        
        # Render stats in a row
        stat_spacing = self.terminal_rect.width // (len(stats) + 1)
        for i, stat in enumerate(stats):
            stat_surface = self.ui_font.render(stat, True, self.COLORS['ui_text'])
            x = self.terminal_rect.x + stat_spacing * (i + 1) - stat_surface.get_width() // 2
            y = self.stats_y + 10
            screen.blit(stat_surface, (x, y))
    
    def render_completion_screen(self, screen: pygame.Surface, metrics: dict, score: int):
        """Render the completion screen with final stats."""
        # Darken background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Success message
        success_text = ">>> SYSTEM INFILTRATION COMPLETE <<<"
        success_surface = self.header_font.render(success_text, True, self.COLORS['glow'])
        success_rect = success_surface.get_rect(centerx=self.screen_width // 2, y=200)
        screen.blit(success_surface, success_rect)
        
        # Final stats
        final_stats = [
            f"Final Hacking Speed: {metrics['wpm']:.1f} WPM",
            f"Stealth Rating: {metrics['accuracy']:.1f}%",
            f"Maximum Hack Streak: {metrics['max_combo']}",
            f"Total Time: {metrics['elapsed_time']:.1f} seconds",
            f"Infiltration Score: {score:,}"
        ]
        
        y = 300
        for stat in final_stats:
            stat_surface = self.ui_font.render(stat, True, self.COLORS['ui_text'])
            stat_rect = stat_surface.get_rect(centerx=self.screen_width // 2, y=y)
            screen.blit(stat_surface, stat_rect)
            y += 30
        
        # Press space to continue
        continue_text = "Press SPACE to return to hub"
        continue_surface = self.ui_font.render(continue_text, True, self.COLORS['ui_text'])
        continue_rect = continue_surface.get_rect(centerx=self.screen_width // 2, y=y + 50)
        
        # Blink effect
        if self.cursor_visible:
            screen.blit(continue_surface, continue_rect)