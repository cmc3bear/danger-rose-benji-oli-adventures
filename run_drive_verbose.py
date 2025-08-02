#!/usr/bin/env python3
"""Run The Drive with verbose audio logging."""

import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set the start scene
os.environ['DANGER_ROSE_START_SCENE'] = 'drive_game'

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== The Drive - Verbose Mode ===")
print("This will show detailed audio logging")
print()
print("Controls:")
print("  Music Selection:")
print("    - Arrow keys: Navigate tracks")
print("    - SPACE: Preview track")
print("    - ENTER: Select track")
print()
print("  After Selection:")
print("    - SPACE: Start race")
print("    - ESC: Exit")
print()
print("Watch the console for audio debug messages!")
print("=" * 50)
print()

# Import and run
from src.main import game

try:
    game()
except KeyboardInterrupt:
    print("\nGame stopped by user")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()