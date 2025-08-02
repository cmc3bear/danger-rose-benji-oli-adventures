import pygame
import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.asset_paths import get_danger_sprite, get_rose_sprite


def test_sprite_sheet_layout():
    """Test different ways to cut the sprite sheet to find correct positioning."""
    pygame.init()
    screen = pygame.display.set_mode((100, 100))

    output_dir = Path(__file__).parent.parent / "test-artifacts" / "sprite_layout_test"
    output_dir.mkdir(exist_ok=True)

    for character_name, sprite_path in [
        ("danger", get_danger_sprite()),
        ("rose", get_rose_sprite()),
    ]:
        if not os.path.exists(sprite_path):
            continue

        print(f"\n=== ANALYZING {character_name.upper()} SPRITE SHEET ===")

        sheet = pygame.image.load(sprite_path).convert_alpha()
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()

        print(f"Sheet dimensions: {sheet_width}x{sheet_height}")

        # Save original sheet with grid overlay
        original_with_grid = sheet.copy()

        # Test different grid layouts
        test_cases = [
            {"rows": 3, "cols": 4, "description": "3 rows x 4 cols"},
            {"rows": 4, "cols": 4, "description": "4 rows x 4 cols"},
            {"rows": 4, "cols": 3, "description": "4 rows x 3 cols"},
        ]

        for test_case in test_cases:
            rows = test_case["rows"]
            cols = test_case["cols"]
            description = test_case["description"]

            frame_width = sheet_width // cols
            frame_height = sheet_height // rows

            print(f"\nTesting {description}")
            print(f"  Frame size: {frame_width}x{frame_height}")

            # Create test directory
            test_dir = output_dir / f"{character_name}_{rows}x{cols}"
            test_dir.mkdir(exist_ok=True)

            # Draw grid on original sheet
            grid_sheet = sheet.copy()
            for row in range(rows + 1):
                y = row * frame_height
                if y < sheet_height:
                    pygame.draw.line(
                        grid_sheet, (255, 0, 0), (0, y), (sheet_width, y), 2
                    )

            for col in range(cols + 1):
                x = col * frame_width
                if x < sheet_width:
                    pygame.draw.line(
                        grid_sheet, (255, 0, 0), (x, 0), (x, sheet_height), 2
                    )

            pygame.image.save(grid_sheet, str(test_dir / "grid_overlay.png"))

            # Extract all frames
            frame_count = 0
            for row in range(rows):
                for col in range(cols):
                    x = col * frame_width
                    y = row * frame_height

                    # Extract frame
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(sheet, (0, 0), (x, y, frame_width, frame_height))

                    # Save frame
                    frame_filename = f"row{row}_col{col}.png"
                    pygame.image.save(frame, str(test_dir / frame_filename))

                    frame_count += 1
                    print(f"    Extracted row {row}, col {col} from ({x}, {y})")

            print(f"  Total frames: {frame_count}")

            # Specifically highlight what would be the "attack" row (row 2)
            if rows > 2:
                attack_row = 2
                attack_y = attack_row * frame_height

                # Create attack row visualization
                attack_viz = sheet.copy()
                pygame.draw.rect(
                    attack_viz, (0, 255, 0), (0, attack_y, sheet_width, frame_height), 4
                )
                pygame.image.save(
                    attack_viz, str(test_dir / "attack_row_highlight.png")
                )

                print(f"  Attack row {attack_row} would be at y={attack_y}")

                # Extract just the attack row frames
                attack_dir = test_dir / "attack_frames"
                attack_dir.mkdir(exist_ok=True)

                for col in range(cols):
                    x = col * frame_width
                    y = attack_y

                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(sheet, (0, 0), (x, y, frame_width, frame_height))

                    frame_filename = f"attack_col{col}.png"
                    pygame.image.save(frame, str(attack_dir / frame_filename))


if __name__ == "__main__":
    test_sprite_sheet_layout()
    print("\nCheck 'tests/sprite_layout_test' for detailed analysis!")
