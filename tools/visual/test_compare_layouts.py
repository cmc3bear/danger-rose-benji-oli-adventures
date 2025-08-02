import pygame
import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.asset_paths import get_danger_sprite


def test_layout_comparison():
    """Compare the old 4x4 layout vs new 3x4 layout for attack animations."""
    pygame.init()
    screen = pygame.display.set_mode((100, 100))

    output_dir = Path(__file__).parent.parent / "test-artifacts" / "layout_comparison"
    output_dir.mkdir(exist_ok=True)

    for character_name, sprite_path in [
        ("danger", get_danger_sprite())
    ]:  # Just test one for now
        if not os.path.exists(sprite_path):
            continue

        print(f"\n=== COMPARING LAYOUTS FOR {character_name.upper()} ===")

        sheet = pygame.image.load(sprite_path).convert_alpha()

        # Old layout: 4x4 grid (256x256 frames)
        old_frame_width = 256
        old_frame_height = 256
        old_attack_row = 2
        old_y_start = old_attack_row * old_frame_height  # y = 512

        print(
            f"Old layout (4x4): {old_frame_width}x{old_frame_height}, attack row at y={old_y_start}"
        )

        # New layout: 3x4 grid (256x341 frames)
        new_frame_width = 256
        new_frame_height = 341
        new_attack_row = 2
        new_y_start = new_attack_row * new_frame_height  # y = 682

        print(
            f"New layout (3x4): {new_frame_width}x{new_frame_height}, attack row at y={new_y_start}"
        )

        # Extract attack frames using both methods
        for layout_name, frame_width, frame_height, y_start in [
            ("old_4x4", old_frame_width, old_frame_height, old_y_start),
            ("new_3x4", new_frame_width, new_frame_height, new_y_start),
        ]:
            layout_dir = output_dir / f"{character_name}_{layout_name}"
            layout_dir.mkdir(exist_ok=True)

            print(f"\n  Extracting {layout_name} attack frames from y={y_start}")

            for col in range(3):  # 3 attack frames
                x_start = col * frame_width

                # Extract frame
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (x_start, y_start, frame_width, frame_height))

                # Save full frame
                frame_filename = f"attack_frame_{col}.png"
                pygame.image.save(frame, str(layout_dir / frame_filename))

                # Also save a scaled version for easier comparison
                scaled_frame = pygame.transform.scale(frame, (128, 128))
                scaled_filename = f"attack_frame_{col}_scaled.png"
                pygame.image.save(scaled_frame, str(layout_dir / scaled_filename))

                print(f"    Frame {col}: ({x_start}, {y_start}) -> {frame_filename}")

            # Create visualization showing the extraction area
            viz = sheet.copy()
            pygame.draw.rect(
                viz, (255, 0, 0), (0, y_start, sheet.get_width(), frame_height), 4
            )
            pygame.image.save(viz, str(layout_dir / "extraction_area.png"))


if __name__ == "__main__":
    test_layout_comparison()
    print("\nCheck 'tests/layout_comparison' to see the difference!")
