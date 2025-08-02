#!/usr/bin/env python3
"""Quick test script for The Drive minigame."""

import os
import sys

# Set the start scene environment variable
os.environ['DANGER_ROSE_START_SCENE'] = 'drive_game'

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the main game
from src.main import game

if __name__ == "__main__":
    print("Starting The Drive minigame...")
    print("Controls:")
    print("  - Arrow keys to select music")
    print("  - SPACE to preview")
    print("  - ENTER to confirm")
    print("  - ESC to exit")
    print()
    
    try:
        game()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()