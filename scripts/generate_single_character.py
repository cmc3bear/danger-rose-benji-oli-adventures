"""Generate sprites for a single character using DALL-E 3 API."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.generate_character_sprites import generate_character_set

def main():
    """Generate sprites for just Benji as a test."""
    print("Generating sprites for Benji only...")
    generate_character_set("benji", scenes=["hub"])
    print("Benji sprite generation complete!")

if __name__ == "__main__":
    main()