"""
Kid-Friendly Error Messages System
Strategy #4 from the Twenty Sacred Strategies

As proclaimed by Agent_GameDesigner_001:
"Our errors terrify children! 'Null pointer exception' makes them cry!"

This module transforms scary technical errors into friendly, helpful messages
that encourage players rather than frighten them.
"""

import os
import random
from typing import Dict, List, Optional


class KidFriendlyErrorHandler:
    """Transform scary errors into encouraging messages for young players"""
    
    def __init__(self):
        self.kid_mode = os.getenv("KID_MODE", "false").lower() == "true"
        self.error_translations = self._load_error_translations()
        self.encouragement_phrases = self._load_encouragement_phrases()
    
    def _load_error_translations(self) -> Dict[str, List[str]]:
        """Load translations from technical errors to kid-friendly messages"""
        return {
            # File/Asset Errors
            "FileNotFoundError": [
                "Oops! {character} is looking for a file that went on vacation! 🏖️",
                "Looks like a game file is playing hide and seek! 🙈",
                "Uh oh! We can't find one of our game pieces! 🧩"
            ],
            "pygame.error": [
                "The game sprites are having a little trouble getting dressed! 👔",
                "Our graphics engine needs a quick coffee break! ☕",
                "The pixels are being a bit shy today! 😊"
            ],
            "AttributeError": [
                "Whoops! {character} tried to use a superpower they don't have yet! 🦸",
                "Someone forgot to teach our character a new trick! 🎪",
                "Our game character is still learning new abilities! 📚"
            ],
            "IndexError": [
                "Oh no! Someone tried to grab item #{index} but we only have {max} items! 🎁",
                "Looks like we're trying to reach too far in our toy box! 🧸",
                "We need more items before we can pick that one! 📦"
            ],
            "KeyError": [
                "We're looking for '{key}' but it's not in our treasure chest! 🗝️",
                "That secret code isn't in our special book yet! 📖",
                "We need to add '{key}' to our collection first! 💎"
            ],
            "ValueError": [
                "{character} got confused by a number! Numbers can be tricky! 🔢",
                "Someone gave us a puzzle piece that doesn't quite fit! 🧩",
                "The math elves are scratching their heads on this one! 🧮"
            ],
            "TypeError": [
                "We tried to mix things that don't go together - like putting socks on a fish! 🐟🧦",
                "Our code characters are speaking different languages! 🗣️",
                "Someone tried to use a hammer as a spoon! 🔨🥄"
            ],
            "ZeroDivisionError": [
                "Whoa! We can't divide by zero - that would break math itself! ➗",
                "The math wizards say dividing by zero is against the rules! 🧙‍♂️",
                "Zero doesn't like being divided - it makes them sad! 😢"
            ],
            "ConnectionError": [
                "The internet tubes are a bit clogged right now! 🌐",
                "Our message couldn't reach its destination - maybe try again? 📮",
                "The digital carrier pigeons are taking a break! 🐦"
            ],
            "MemoryError": [
                "Our computer's brain is a bit full right now! 🧠",
                "We need to clean up some digital toys to make room! 🧹",
                "The memory elves are organizing - give them a moment! 🧝"
            ]
        }
    
    def _load_encouragement_phrases(self) -> List[str]:
        """Load encouraging phrases to help kids feel better about errors"""
        return [
            "Don't worry - even the best programmers see messages like this! 💪",
            "This is how we learn - one helpful message at a time! 📚",
            "Bugs are just puzzles waiting to be solved! 🧩",
            "Every error makes us smarter developers! 🧠",
            "Heroes always face challenges - you've got this! 🦸",
            "Mistakes are just opportunities to make things better! ✨",
            "Even video game characters need practice! 🎮",
            "This is your game learning how to be awesome! 🌟",
            "Debugging is like being a detective - so cool! 🕵️",
            "Every fix makes our game more amazing! 🚀"
        ]
    
    def translate_error(self, error: Exception, context: Optional[Dict] = None) -> str:
        """
        Translate a technical error into a kid-friendly message
        
        Args:
            error: The original exception
            context: Additional context (character name, values, etc.)
            
        Returns:
            Kid-friendly error message
        """
        if not self.kid_mode:
            # In normal mode, return technical details
            return f"{type(error).__name__}: {str(error)}"
        
        context = context or {}
        error_type = type(error).__name__
        
        # Get base translations
        translations = self.error_translations.get(error_type, [
            f"Something unexpected happened, but don't worry! 🤔",
            f"Our game hit a little bump, but we can fix it! 🛠️",
            f"Oops! Let's try that again! ✨"
        ])
        
        # Pick a random translation
        base_message = random.choice(translations)
        
        # Fill in context variables
        try:
            # Create a safe context dict without duplicating keys
            safe_context = {
                'character': context.get('character', 'our hero'),
                'key': context.get('key', 'unknown'),
                'index': context.get('index', '?'),
                'max': context.get('max', '?')
            }
            # Add other context items that don't conflict
            for k, v in context.items():
                if k not in safe_context:
                    safe_context[k] = v
                    
            formatted_message = base_message.format(**safe_context)
        except (KeyError, ValueError):
            # If formatting fails, use the base message
            formatted_message = base_message
        
        # Add encouragement
        encouragement = random.choice(self.encouragement_phrases)
        
        # Add helpful action if provided
        action_hint = context.get('action_hint', 'Try pressing SPACE to continue!')
        
        return f"{formatted_message}\n\n{encouragement}\n\n💡 {action_hint}"
    
    def create_error_dialog(self, error: Exception, context: Optional[Dict] = None) -> Dict:
        """
        Create a complete error dialog with title, message, and actions
        
        Returns:
            Dictionary with dialog components
        """
        context = context or {}
        
        if self.kid_mode:
            title = "Oops! Adventure Pause! 🎮"
            message = self.translate_error(error, context)
            
            # Kid-friendly button options
            buttons = [
                {"text": "Try Again! 🔄", "action": "retry"},
                {"text": "Get Help 🆘", "action": "help"},
                {"text": "Take a Break ☕", "action": "pause"}
            ]
            
            # Add character-specific comfort
            character = context.get('character', 'hero')
            comfort_message = f"{character} believes in you! Never give up! 💪"
            
        else:
            # Technical mode for developers
            title = f"Error: {type(error).__name__}"
            message = str(error)
            buttons = [
                {"text": "Retry", "action": "retry"},
                {"text": "Debug", "action": "debug"},
                {"text": "Exit", "action": "exit"}
            ]
            comfort_message = "Check logs for detailed information."
        
        return {
            "title": title,
            "message": message,
            "buttons": buttons,
            "comfort": comfort_message,
            "icon": "🎮" if self.kid_mode else "⚠️"
        }
    
    def log_friendly_error(self, error: Exception, context: Optional[Dict] = None):
        """Log error in both technical and friendly formats"""
        # Always log technical details for developers
        technical_log = f"TECHNICAL: {type(error).__name__}: {str(error)}"
        
        # Add friendly version if in kid mode
        if self.kid_mode:
            friendly_message = self.translate_error(error, context)
            kid_log = f"KID-FRIENDLY: {friendly_message}"
            print(f"{technical_log}\n{kid_log}")
        else:
            print(technical_log)


# Global instance for easy access
kid_friendly_handler = KidFriendlyErrorHandler()


def show_kid_friendly_error(error: Exception, context: Optional[Dict] = None) -> str:
    """
    Convenience function to show kid-friendly error
    
    Usage:
        try:
            risky_operation()
        except FileNotFoundError as e:
            message = show_kid_friendly_error(e, {
                'character': 'Danger',
                'action_hint': 'Press SPACE to try loading again!'
            })
            display_error_dialog(message)
    """
    return kid_friendly_handler.translate_error(error, context)


def create_error_dialog(error: Exception, context: Optional[Dict] = None) -> Dict:
    """Convenience function to create complete error dialog"""
    return kid_friendly_handler.create_error_dialog(error, context)


# Example usage and testing
if __name__ == "__main__":
    # Test the error translation system
    import os
    
    print("Testing Kid-Friendly Error System")
    print("=" * 40)
    
    # Test in kid mode
    os.environ["KID_MODE"] = "true"
    handler = KidFriendlyErrorHandler()
    
    # Test different error types
    test_errors = [
        (FileNotFoundError("sprite.png not found"), {'character': 'Danger'}),
        (ValueError("invalid literal for int()"), {'character': 'Rose'}),
        (KeyError("'position'"), {'key': 'position', 'character': 'Dad'}),
        (IndexError("list index out of range"), {'index': 5, 'max': 3})
    ]
    
    for error, context in test_errors:
        print(f"\nOriginal Error: {error}")
        print("Kid-Friendly Version:")
        print(handler.translate_error(error, context))
        print("-" * 40)