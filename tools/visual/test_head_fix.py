import pygame
import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.asset_paths import get_danger_sprite, get_rose_sprite
from utils.attack_character import AttackCharacter


def test_head_fix():
    """Test the head cutoff fix by comparing before and after positioning."""
    pygame.init()
    screen = pygame.display.set_mode((100, 100))

    output_dir = Path(__file__).parent.parent / "test-artifacts" / "head_fix_test"
    output_dir.mkdir(exist_ok=True)

    for character_name, sprite_path in [
        ("danger", get_danger_sprite()),
        ("rose", get_rose_sprite()),
    ]:
        if not os.path.exists(sprite_path):
            continue

        print(f"\n=== TESTING HEAD FIX FOR {character_name.upper()} ===")

        sheet = pygame.image.load(sprite_path).convert_alpha()

        # Test both old and new positioning
        frame_width = 256
        frame_height = 341
        attack_row = 2

        # Old positioning (heads cut off)
        old_y_start = attack_row * frame_height  # 682

        # New positioning (shifted down by 1/3)
        y_offset = frame_height // 3  # 113
        new_y_start = old_y_start + y_offset  # 795

        print(f"Old y position: {old_y_start}")
        print(f"New y position: {new_y_start} (shifted down by {y_offset})")

        # Create comparison directory
        comp_dir = output_dir / character_name
        comp_dir.mkdir(exist_ok=True)

        # Extract frames using both methods
        for method, y_start in [("old", old_y_start), ("new", new_y_start)]:
            method_dir = comp_dir / method
            method_dir.mkdir(exist_ok=True)

            print(f"\n  Extracting {method} frames from y={y_start}")

            for col in range(3):  # 3 attack frames
                x_start = col * frame_width

                # Extract frame
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (x_start, y_start, frame_width, frame_height))

                # Save frame at original size
                frame_filename = f"attack_frame_{col}.png"
                pygame.image.save(frame, str(method_dir / frame_filename))

                # Save scaled version for easier viewing
                scaled_frame = pygame.transform.scale(frame, (128, 128))
                scaled_filename = f"attack_frame_{col}_scaled.png"
                pygame.image.save(scaled_frame, str(method_dir / scaled_filename))

                print(f"    Frame {col}: ({x_start}, {y_start}) -> {frame_filename}")

            # Create visualization showing extraction area
            viz = sheet.copy()
            pygame.draw.rect(
                viz, (0, 255, 0), (0, y_start, sheet.get_width(), frame_height), 4
            )
            pygame.image.save(viz, str(method_dir / "extraction_area.png"))

        # Test using the actual AttackCharacter class
        print("\n  Testing AttackCharacter class:")
        attack_char = AttackCharacter(character_name, sprite_path, (128, 128))

        class_dir = comp_dir / "attack_character_class"
        class_dir.mkdir(exist_ok=True)

        for i in range(attack_char.get_frame_count()):
            attack_char.current_frame = i
            frame = attack_char.get_current_sprite()
            frame_filename = f"class_frame_{i}.png"
            pygame.image.save(frame, str(class_dir / frame_filename))

        print(
            f"    Saved {attack_char.get_frame_count()} frames using AttackCharacter class"
        )


if __name__ == "__main__":
    test_head_fix()
    print("\nCheck 'tests/head_fix_test' to see the head cutoff fix!")
