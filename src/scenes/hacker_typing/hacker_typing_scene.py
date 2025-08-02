"""Main scene for the Hacker Typing Challenge mini-game."""

import pygame
from typing import Optional, Dict
from enum import Enum

from ..base import BaseScene
from .typing_engine import TypingEngine
from .terminal_renderer import TerminalRenderer
from .challenge_manager import ChallengeManager, ChallengeType, Challenge


class GameState(Enum):
    """States of the typing game."""
    MENU = "menu"
    TYPING = "typing"
    COMPLETED = "completed"
    PAUSED = "paused"


class HackerTypingScene(BaseScene):
    """Hacker-themed typing tutor mini-game scene."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Core components
        self.typing_engine = TypingEngine()
        self.renderer = TerminalRenderer(self.game.screen.get_width(), self.game.screen.get_height())
        self.challenge_manager = ChallengeManager()
        
        # Game state
        self.state = GameState.MENU
        self.current_challenge: Optional[Challenge] = None
        self.trace_timer = 0.0
        self.score = 0
        self.session_stats = {
            "challenges_completed": 0,
            "total_score": 0,
            "best_wpm": 0,
            "best_accuracy": 0,
            "perfect_challenges": 0
        }
        
        # Sound effects (will be loaded later)
        self.sounds = {}
        self.load_sounds()
        
        # Background music
        self.music_playing = False
    
    def load_sounds(self):
        """Load sound effects for the typing game."""
        sound_files = {
            'keystroke': 'keyboard_mechanical_1.ogg',
            'correct': 'hack_success.ogg',
            'error': 'hack_fail.ogg',
            'complete': 'system_access.ogg',
            'trace_warning': 'trace_warning.ogg'
        }
        
        # Try to load each sound
        for name, filename in sound_files.items():
            try:
                filepath = f"assets/audio/sfx/{filename}"
                self.sounds[name] = pygame.mixer.Sound(filepath)
                self.sounds[name].set_volume(0.5)
            except:
                # Sound file doesn't exist yet, that's okay
                self.sounds[name] = None
    
    def play_sound(self, sound_name: str):
        """Play a sound effect if it exists."""
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()
    
    def enter(self):
        """Called when entering the scene."""
        # Reset state
        self.state = GameState.MENU
        self.current_challenge = None
        
        # Start background music
        try:
            pygame.mixer.music.load("assets/audio/music/hacker_theme_ambient.ogg")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
            self.music_playing = True
        except:
            self.music_playing = False
    
    def exit(self):
        """Called when leaving the scene."""
        # Stop music
        if self.music_playing:
            pygame.mixer.music.stop()
    
    def start_challenge(self, challenge: Challenge):
        """Start a new typing challenge."""
        self.current_challenge = challenge
        self.typing_engine.set_challenge_text(challenge.text)
        self.trace_timer = challenge.time_limit
        self.state = GameState.TYPING
        
        # Increase music intensity
        if self.music_playing:
            try:
                pygame.mixer.music.load("assets/audio/music/hacker_theme_intense.ogg")
                pygame.mixer.music.play(-1)
            except:
                pass
    
    def complete_challenge(self):
        """Handle challenge completion."""
        metrics = self.typing_engine.get_metrics()
        self.score = self.typing_engine.calculate_score(self.current_challenge.time_limit)
        
        # Update session stats
        self.session_stats["challenges_completed"] += 1
        self.session_stats["total_score"] += self.score
        self.session_stats["best_wpm"] = max(self.session_stats["best_wpm"], metrics["wpm"])
        self.session_stats["best_accuracy"] = max(self.session_stats["best_accuracy"], metrics["accuracy"])
        
        if metrics["accuracy"] == 100:
            self.session_stats["perfect_challenges"] += 1
        
        # Mark challenge as completed
        self.challenge_manager.mark_completed(self.current_challenge.id)
        
        # Check for level unlock
        if self.challenge_manager.unlock_next_level():
            self.play_sound('complete')
        
        # Play victory music
        if self.music_playing:
            try:
                pygame.mixer.music.load("assets/audio/music/hacker_theme_victory.ogg")
                pygame.mixer.music.play()
            except:
                pass
        
        self.state = GameState.COMPLETED
        self.play_sound('complete')
    
    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.MENU:
                self.handle_menu_input(event)
            elif self.state == GameState.TYPING:
                self.handle_typing_input(event)
            elif self.state == GameState.COMPLETED:
                if event.key == pygame.K_SPACE:
                    self.state = GameState.MENU
                elif event.key == pygame.K_ESCAPE:
                    self.game.scene_manager.switch_scene("hub")
    
    def handle_menu_input(self, event):
        """Handle input in menu state."""
        if event.key == pygame.K_ESCAPE:
            # Return to hub
            self.game.scene_manager.switch_scene("hub")
        elif event.key >= pygame.K_1 and event.key <= pygame.K_4:
            # Select difficulty level
            level = event.key - pygame.K_0
            if level <= self.challenge_manager.current_level:
                # Get a random challenge for this level
                challenge = self.challenge_manager.get_random_challenge(difficulty=level)
                if challenge:
                    self.start_challenge(challenge)
    
    def handle_typing_input(self, event):
        """Handle input during typing challenge."""
        if event.key == pygame.K_ESCAPE:
            # Pause/unpause
            if self.state == GameState.TYPING:
                self.state = GameState.PAUSED
            else:
                self.state = GameState.TYPING
        elif event.key == pygame.K_BACKSPACE:
            # Handle backspace
            if self.typing_engine.handle_backspace():
                self.play_sound('keystroke')
        elif event.unicode and ord(event.unicode) >= 32:
            # Regular character input
            result = self.typing_engine.process_keystroke(event.unicode)
            
            if result.get("finished"):
                if result.get("success"):
                    self.complete_challenge()
            else:
                if result.get("correct"):
                    self.play_sound('keystroke')
                else:
                    self.play_sound('error')
    
    def update(self, dt):
        """Update game logic."""
        # Update renderer animations
        self.renderer.update(dt)
        
        # Update trace timer during typing
        if self.state == GameState.TYPING and self.trace_timer > 0:
            self.trace_timer -= dt
            
            # Warning sounds
            if self.trace_timer <= 5 and int(self.trace_timer * 2) % 2 == 0:
                self.play_sound('trace_warning')
            
            # Time's up
            if self.trace_timer <= 0:
                self.state = GameState.COMPLETED
                self.score = 0  # Failed to complete in time
    
    def draw(self, screen):
        """Draw the scene."""
        # Render background
        self.renderer.render_background(screen)
        
        # Render terminal frame
        self.renderer.render_terminal_frame(screen)
        
        if self.state == GameState.MENU:
            self.draw_menu(screen)
        elif self.state in [GameState.TYPING, GameState.PAUSED]:
            self.draw_typing_game(screen)
        elif self.state == GameState.COMPLETED:
            self.draw_completion_screen(screen)
    
    def draw_menu(self, screen):
        """Draw the challenge selection menu."""
        # Header
        self.renderer.render_header(screen, "Challenge Selection", 0)
        
        # Menu options
        menu_y = self.renderer.terminal_rect.y + 150
        
        # Title
        title = ">>> SELECT INFILTRATION LEVEL <<<"
        title_surface = self.renderer.header_font.render(title, True, self.renderer.COLORS['glow'])
        title_rect = title_surface.get_rect(centerx=self.renderer.terminal_rect.centerx, y=menu_y)
        screen.blit(title_surface, title_rect)
        
        # Level options
        levels = [
            ("1. Password Cracker", "Learn the basics (15 WPM)", 1),
            ("2. Command Line Master", "Terminal commands (25 WPM)", 2),
            ("3. Script Kiddie", "Code snippets (30 WPM)", 3),
            ("4. Elite Hacker", "Full programs (40 WPM)", 4)
        ]
        
        option_y = menu_y + 80
        for name, desc, level in levels:
            # Check if unlocked
            if level <= self.challenge_manager.current_level:
                color = self.renderer.COLORS['ui_text']
                progress = self.challenge_manager.get_level_progress(level)
                status = f" [{progress['completed']}/{progress['total']}]"
            else:
                color = (50, 50, 50)
                status = " [LOCKED]"
            
            # Render option
            option_text = name + status
            option_surface = self.renderer.ui_font.render(option_text, True, color)
            option_rect = option_surface.get_rect(centerx=self.renderer.terminal_rect.centerx, y=option_y)
            screen.blit(option_surface, option_rect)
            
            # Render description
            if level <= self.challenge_manager.current_level:
                desc_surface = self.renderer.ui_font.render(desc, True, (100, 100, 100))
                desc_rect = desc_surface.get_rect(centerx=self.renderer.terminal_rect.centerx, y=option_y + 25)
                screen.blit(desc_surface, desc_rect)
            
            option_y += 70
        
        # Instructions
        inst_text = "Press 1-4 to select level, ESC to return to hub"
        inst_surface = self.renderer.ui_font.render(inst_text, True, self.renderer.COLORS['ui_text'])
        inst_rect = inst_surface.get_rect(centerx=self.renderer.terminal_rect.centerx, 
                                         bottom=self.renderer.terminal_rect.bottom - 50)
        screen.blit(inst_surface, inst_rect)
    
    def draw_typing_game(self, screen):
        """Draw the active typing game."""
        if not self.current_challenge:
            return
        
        # Header with timer
        self.renderer.render_header(screen, self.current_challenge.name, self.trace_timer)
        
        # Challenge description
        desc_surface = self.renderer.ui_font.render(self.current_challenge.description, True, 
                                                   self.renderer.COLORS['ui_text'])
        desc_rect = desc_surface.get_rect(centerx=self.renderer.terminal_rect.centerx, 
                                         y=self.renderer.terminal_rect.y + 100)
        screen.blit(desc_surface, desc_rect)
        
        # Typing text
        segments = self.typing_engine.get_display_segments()
        self.renderer.render_typing_text(screen, segments)
        
        # Stats
        metrics = self.typing_engine.get_metrics()
        self.renderer.render_stats(screen, metrics)
        
        # Pause overlay
        if self.state == GameState.PAUSED:
            overlay = pygame.Surface((screen.get_width(), screen.get_height()))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            pause_text = "PAUSED - Press ESC to resume"
            pause_surface = self.renderer.header_font.render(pause_text, True, self.renderer.COLORS['glow'])
            pause_rect = pause_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(pause_surface, pause_rect)
    
    def draw_completion_screen(self, screen):
        """Draw the challenge completion screen."""
        if self.score > 0:
            metrics = self.typing_engine.get_metrics()
            self.renderer.render_completion_screen(screen, metrics, self.score)
        else:
            # Failed screen
            fail_text = ">>> TRACE DETECTED - MISSION FAILED <<<"
            fail_surface = self.renderer.header_font.render(fail_text, True, (255, 0, 0))
            fail_rect = fail_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(fail_surface, fail_rect)
            
            continue_text = "Press SPACE to try again, ESC to return to hub"
            continue_surface = self.renderer.ui_font.render(continue_text, True, self.renderer.COLORS['ui_text'])
            continue_rect = continue_surface.get_rect(center=(screen.get_width() // 2, 
                                                            screen.get_height() // 2 + 50))
            screen.blit(continue_surface, continue_rect)