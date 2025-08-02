import pygame
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.attack_character import AttackCharacter
from utils.asset_paths import get_danger_sprite, get_rose_sprite


def test_attack_character_loading():
    """Test that attack characters load correctly."""
    pygame.init()
    # Create a display surface for proper image conversion
    screen = pygame.display.set_mode((100, 100))

    output_dir = (
        Path(__file__).parent.parent / "test-artifacts" / "attack_character_test"
    )
    output_dir.mkdir(exist_ok=True)

    for character_name, sprite_path in [
        ("danger", get_danger_sprite()),
        ("rose", get_rose_sprite()),
    ]:
        print(f"\n=== TESTING {character_name.upper()} ATTACK CHARACTER ===")

        # Create attack character
        attack_char = AttackCharacter(character_name, sprite_path, (128, 128))

        print(f"Frame count: {attack_char.get_frame_count()}")
        print(f"Animation info: {attack_char.get_animation_info()}")

        # Save each frame
        char_dir = output_dir / character_name
        char_dir.mkdir(exist_ok=True)

        for i in range(attack_char.get_frame_count()):
            attack_char.current_frame = i
            frame = attack_char.get_current_sprite()
            frame_path = char_dir / f"attack_frame_{i}.png"
            pygame.image.save(frame, str(frame_path))
            print(f"  Saved frame {i} to {frame_path}")

        # Test animation cycling
        print("  Testing animation cycling...")
        for step in range(6):  # Test 6 updates
            attack_char.update()
            info = attack_char.get_animation_info()
            print(f"    Step {step}: {info}")


if __name__ == "__main__":
    test_attack_character_loading()
    print("\nCheck 'tests/attack_character_test' for results!")
