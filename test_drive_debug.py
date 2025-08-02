#!/usr/bin/env python3
"""Test The Drive with debug output."""

import os
import sys
import time

# Set the start scene environment variable
os.environ['DANGER_ROSE_START_SCENE'] = 'drive_game'

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Starting The Drive minigame with debug output...")
print("=" * 50)

# Import pygame to simulate key presses
import pygame

# Import and run the main game
from src.main import game

# Run in a separate thread so we can control it
import threading

game_thread = threading.Thread(target=game)
game_thread.daemon = True
game_thread.start()

# Give the game time to start
time.sleep(3)

print("\nGame should be running. Check the window.")
print("Debug messages will appear here.")
print("\nPress Ctrl+C to stop.")

try:
    # Keep the main thread alive
    while game_thread.is_alive():
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopping game...")
    pygame.quit()
    sys.exit(0)