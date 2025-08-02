"""Core typing mechanics engine for the Hacker Typing Challenge."""

import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CharacterStatus(Enum):
    """Status of each character in the typing challenge."""
    PENDING = "pending"
    CORRECT = "correct"
    INCORRECT = "incorrect"
    CURRENT = "current"


@dataclass
class TypingMetrics:
    """Container for typing performance metrics."""
    total_characters: int = 0
    correct_characters: int = 0
    incorrect_characters: int = 0
    start_time: float = 0.0
    end_time: Optional[float] = None
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time if self.start_time else 0
    
    @property
    def wpm(self) -> float:
        """Calculate words per minute (standard: 5 chars = 1 word)."""
        if self.elapsed_time <= 0:
            return 0.0
        minutes = self.elapsed_time / 60
        words = self.correct_characters / 5
        return words / minutes if minutes > 0 else 0
    
    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage."""
        if self.total_characters == 0:
            return 100.0
        return (self.correct_characters * 100) / self.total_characters


class TypingEngine:
    """Core engine for handling typing mechanics and validation."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the typing engine to initial state."""
        self.current_text = ""
        self.typed_text = ""
        self.character_statuses: List[CharacterStatus] = []
        self.current_position = 0
        self.metrics = TypingMetrics()
        self.combo_streak = 0
        self.max_combo_streak = 0
        self.last_keystroke_time = 0
        self.keystroke_times: List[float] = []
    
    def set_challenge_text(self, text: str):
        """Set the text for the current typing challenge."""
        self.reset()
        self.current_text = text
        self.character_statuses = [CharacterStatus.PENDING] * len(text)
        if text:
            self.character_statuses[0] = CharacterStatus.CURRENT
    
    def process_keystroke(self, key: str) -> Dict[str, any]:
        """Process a single keystroke and return result."""
        if not self.current_text or self.current_position >= len(self.current_text):
            return {"finished": True}
        
        # Start timing on first keystroke
        if self.metrics.start_time == 0:
            self.metrics.start_time = time.time()
        
        # Track keystroke timing for advanced metrics
        current_time = time.time()
        if self.last_keystroke_time > 0:
            self.keystroke_times.append(current_time - self.last_keystroke_time)
        self.last_keystroke_time = current_time
        
        expected_char = self.current_text[self.current_position]
        is_correct = key == expected_char
        
        # Update metrics
        self.metrics.total_characters += 1
        if is_correct:
            self.metrics.correct_characters += 1
            self.combo_streak += 1
            self.max_combo_streak = max(self.max_combo_streak, self.combo_streak)
        else:
            self.metrics.incorrect_characters += 1
            self.combo_streak = 0
        
        # Update character status
        self.character_statuses[self.current_position] = (
            CharacterStatus.CORRECT if is_correct else CharacterStatus.INCORRECT
        )
        
        # Move to next position if correct
        if is_correct:
            self.typed_text += key
            self.current_position += 1
            
            # Update current character marker
            if self.current_position < len(self.current_text):
                self.character_statuses[self.current_position] = CharacterStatus.CURRENT
            else:
                # Challenge completed
                self.metrics.end_time = time.time()
                return {
                    "finished": True,
                    "success": True,
                    "metrics": self.get_metrics()
                }
        
        return {
            "finished": False,
            "correct": is_correct,
            "expected": expected_char,
            "typed": key,
            "position": self.current_position,
            "combo": self.combo_streak
        }
    
    def handle_backspace(self) -> bool:
        """Handle backspace key - only works on incorrect characters."""
        if self.current_position > 0:
            # Check if previous character was incorrect
            prev_pos = self.current_position - 1
            if (prev_pos < len(self.character_statuses) and 
                self.character_statuses[prev_pos] == CharacterStatus.INCORRECT):
                # Allow correction
                self.character_statuses[prev_pos] = CharacterStatus.CURRENT
                self.character_statuses[self.current_position] = CharacterStatus.PENDING
                self.current_position = prev_pos
                self.typed_text = self.typed_text[:-1] if self.typed_text else ""
                return True
        return False
    
    def get_display_segments(self) -> List[Tuple[str, CharacterStatus]]:
        """Get text segments with their status for rendering."""
        segments = []
        for i, char in enumerate(self.current_text):
            status = self.character_statuses[i] if i < len(self.character_statuses) else CharacterStatus.PENDING
            segments.append((char, status))
        return segments
    
    def get_metrics(self) -> Dict[str, any]:
        """Get current typing metrics."""
        return {
            "wpm": round(self.metrics.wpm, 1),
            "accuracy": round(self.metrics.accuracy, 1),
            "correct_chars": self.metrics.correct_characters,
            "incorrect_chars": self.metrics.incorrect_characters,
            "total_chars": self.metrics.total_characters,
            "elapsed_time": round(self.metrics.elapsed_time, 1),
            "combo_streak": self.combo_streak,
            "max_combo": self.max_combo_streak,
            "avg_keystroke_time": self._calculate_avg_keystroke_time()
        }
    
    def _calculate_avg_keystroke_time(self) -> float:
        """Calculate average time between keystrokes."""
        if not self.keystroke_times:
            return 0.0
        return round(sum(self.keystroke_times) / len(self.keystroke_times), 3)
    
    def calculate_score(self, time_limit: float = 60.0) -> int:
        """Calculate infiltration score based on performance."""
        base_score = self.metrics.correct_characters * 10
        accuracy_bonus = int(base_score * (self.metrics.accuracy / 100))
        combo_bonus = self.max_combo_streak * 50
        
        # Time bonus for completing under limit
        if self.metrics.end_time:
            time_remaining = max(0, time_limit - self.metrics.elapsed_time)
            time_bonus = int(time_remaining * 10)
        else:
            time_bonus = 0
        
        # WPM bonus
        wpm_bonus = int(self.metrics.wpm * 5)
        
        return base_score + accuracy_bonus + combo_bonus + time_bonus + wpm_bonus