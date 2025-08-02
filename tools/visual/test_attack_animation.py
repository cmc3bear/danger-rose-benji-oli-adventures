import pygame
import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.asset_paths import get_danger_sprite, get_rose_sprite


def test_attack_animation_cutting():
    """Test cutting just the attack animation (row 2) from sprite sheets."""
    pygame.init()

    output_dir = Path(__file__).parent.parent / "test-artifacts" / "attack_output"
    output_dir.mkdir(exist_ok=True)

    for character_name, sprite_path in [
        ("danger", get_danger_sprite()),
        ("rose", get_rose_sprite()),
    ]:
        if not os.path.exists(sprite_path):
            print(f"Skipping {character_name} - file not found")
            continue

        print(f"\n=== TESTING {character_name.upper()} ATTACK ANIMATION ===")

        # Load the original sprite sheet
        sheet = pygame.image.load(sprite_path)
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()

        print(f"Sheet dimensions: {sheet_width}x{sheet_height}")

        # Test different frame sizes for attack animation (row 2)
        frame_sizes = [
            (256, 256),  # 4x4 grid
            (256, 341),  # 4x3 grid
            (341, 256),  # 3x4 grid
            (512, 256),  # 2x4 grid
            (512, 341),  # 2x3 grid
        ]

        for frame_width, frame_height in frame_sizes:
            print(f"\nTesting frame size: {frame_width}x{frame_height}")

            # Create directory for this test
            test_dir = (
                output_dir / f"{character_name}_{frame_width}x{frame_height}_attack"
            )
            test_dir.mkdir(exist_ok=True)

            # Calculate row 2 position (attack animation)
            row = 2
            y_start = row * frame_height

            # Check if row fits in sheet
            if y_start + frame_height > sheet_height:
                print(
                    f"  Row 2 doesn't fit: {y_start} + {frame_height} = {y_start + frame_height} > {sheet_height}"
                )
                continue

            print(f"  Row 2 starts at y={y_start}")

            # Extract frames from row 2
            frames_extracted = 0
            for col in range(4):  # Try up to 4 columns
                x_start = col * frame_width

                # Check if column fits in sheet
                if x_start + frame_width > sheet_width:
                    print(
                        f"    Column {col} doesn't fit: {x_start} + {frame_width} = {x_start + frame_width} > {sheet_width}"
                    )
                    break

                # Extract frame
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (x_start, y_start, frame_width, frame_height))

                # Save frame
                frame_filename = f"attack_frame_{col}.png"
                pygame.image.save(frame, str(test_dir / frame_filename))

                frames_extracted += 1
                print(f"    Extracted frame {col} from ({x_start}, {y_start})")

            print(f"  Total frames extracted: {frames_extracted}")

            # Also save a visualization of the row boundary
            if frames_extracted > 0:
                # Create a visualization showing the row being extracted
                viz = sheet.copy()
                # Draw a red rectangle around row 2
                pygame.draw.rect(
                    viz, (255, 0, 0), (0, y_start, sheet_width, frame_height), 3
                )
                pygame.image.save(viz, str(test_dir / "row_visualization.png"))


if __name__ == "__main__":
    test_attack_animation_cutting()
    print("\nCheck 'tests/attack_output' for results!")
