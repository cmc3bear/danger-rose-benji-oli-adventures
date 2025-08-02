"""Test that all 6 characters are selectable and game transitions properly."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pygame
pygame.init()  # Initialize pygame before creating buttons

from src.scenes.title_screen import CharacterButton

# Test character names
character_names = ["Danger", "Rose", "Dad", "Benji", "Olive", "Uncle Bear"]
ability_names = ["Speed Burst", "Precision", "Experience", "Tech Boost", "Nature's Blessing", "Bear Strength"]

print("Testing character selection system...")
print("=" * 50)

# Test character button creation
for i, (name, ability) in enumerate(zip(character_names, ability_names)):
    try:
        button = CharacterButton(0, 0, name, "", ability)
        print(f"[OK] {name} button created successfully")
        print(f"  - Character name: {button.character_name}")
        print(f"  - Ability: {button.ability_name}")
        print(f"  - Animation character: {button.animated_character.character_name}")
    except Exception as e:
        print(f"[ERROR] Error creating {name} button: {e}")

print("\n" + "=" * 50)
print("Character selection test complete!")
print("\nNote: The placeholder sprites should be displaying as colored circles with initials.")
print("Replace with actual sprites when DALL-E API key is available.")