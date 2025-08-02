import pygame
import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.asset_paths import get_danger_sprite, get_rose_sprite
from utils.attack_character import AttackCharacter


def test_upward_fix():
    """Test the corrected upward positioning to fix head cutoff."""
    pygame.init()
    screen = pygame.display.set_mode((100, 100))

    output_dir = Path(__file__).parent.parent / "test-artifacts" / "upward_fix_test"
    output_dir.mkdir(exist_ok=True)

    for character_name, sprite_path in [
        ("danger", get_danger_sprite()),
        ("rose", get_rose_sprite()),
    ]:
        if not os.path.exists(sprite_path):
            continue

        print(f"\n=== TESTING UPWARD FIX FOR {character_name.upper()} ===")

        sheet = pygame.image.load(sprite_path).convert_alpha()

        # Test positioning progression
        frame_width = 256
        frame_height = 341
        attack_row = 2

        # Original positioning (3x4 grid baseline)
        original_y = attack_row * frame_height  # 682

        # Previous wrong fix (moved down - this was wrong!)
        wrong_y_offset = frame_height // 3  # 113
        wrong_y = original_y + wrong_y_offset  # 795

        # Correct fix (move up to show heads)
        correct_y_offset = frame_height // 3  # 113
        correct_y = original_y - correct_y_offset  # 569

        print(f"Original y position: {original_y}")
        print(f"Wrong fix (down): {wrong_y}")
        print(f"Correct fix (up): {correct_y} (shifted up by {correct_y_offset})")

        # Create comparison directory
        comp_dir = output_dir / character_name
        comp_dir.mkdir(exist_ok=True)

        # Extract frames using all three methods
        for method, y_start in [
            ("original", original_y),
            ("wrong_down", wrong_y),
            ("correct_up", correct_y),
        ]:
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
            color = (
                (255, 0, 0)
                if method == "wrong_down"
                else (0, 255, 0)
                if method == "correct_up"
                else (0, 0, 255)
            )
            pygame.draw.rect(
                viz, color, (0, y_start, sheet.get_width(), frame_height), 4
            )
            pygame.image.save(viz, str(method_dir / "extraction_area.png"))

        # Test using the actual AttackCharacter class (should use correct_up now)
        print(
            "\n  Testing AttackCharacter class (should use correct upward positioning):"
        )
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
    test_upward_fix()
    print("\nCheck 'tests/upward_fix_test' to see the corrected positioning!")
