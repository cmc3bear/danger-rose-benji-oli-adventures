import pygame
import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.asset_paths import get_danger_sprite, get_rose_sprite
from utils.sprite_loader import load_character_animations


class TestSpriteCutting:
    @classmethod
    def setup_class(cls):
        """Initialize pygame for testing."""
        pygame.init()

    def test_sprite_sheet_dimensions(self):
        """Test to understand the actual sprite sheet dimensions."""
        danger_path = get_danger_sprite()
        rose_path = get_rose_sprite()

        print("\n=== SPRITE SHEET ANALYSIS ===")
        print(f"Danger sprite path: {danger_path}")
        print(f"Rose sprite path: {rose_path}")

        # Check if files exist
        print(f"Danger file exists: {os.path.exists(danger_path)}")
        print(f"Rose file exists: {os.path.exists(rose_path)}")

        if os.path.exists(danger_path):
            danger_sheet = pygame.image.load(danger_path)
            print(
                f"Danger sheet dimensions: {danger_sheet.get_width()}x{danger_sheet.get_height()}"
            )

        if os.path.exists(rose_path):
            rose_sheet = pygame.image.load(rose_path)
            print(
                f"Rose sheet dimensions: {rose_sheet.get_width()}x{rose_sheet.get_height()}"
            )

    def test_sprite_cutting_visualization(self):
        """Generate individual sprite images to visualize how they're being cut."""
        danger_path = get_danger_sprite()
        rose_path = get_rose_sprite()

        # Create output directory for test images
        output_dir = Path(__file__).parent.parent / "test-artifacts" / "sprite_output"
        output_dir.mkdir(exist_ok=True)

        for character_name, sprite_path in [
            ("danger", danger_path),
            ("rose", rose_path),
        ]:
            if not os.path.exists(sprite_path):
                print(f"Skipping {character_name} - file not found")
                continue

            print(f"\n=== CUTTING {character_name.upper()} SPRITE SHEET ===")

            # Load the original sprite sheet
            original_sheet = pygame.image.load(sprite_path)
            sheet_width = original_sheet.get_width()
            sheet_height = original_sheet.get_height()

            print(f"Original sheet: {sheet_width}x{sheet_height}")

            # Save original sheet for reference
            pygame.image.save(
                original_sheet, str(output_dir / f"{character_name}_original.png")
            )

            # Test different frame sizes
            frame_sizes = [
                (64, 64),  # Current assumption
                (32, 32),  # Smaller
                (48, 48),  # Medium
                (
                    sheet_width // 4,
                    sheet_height // 3,
                ),  # Calculated based on 4 cols, 3 rows
                (
                    sheet_width // 3,
                    sheet_height // 3,
                ),  # Calculated based on 3 cols, 3 rows
            ]

            for frame_width, frame_height in frame_sizes:
                print(f"\nTesting frame size: {frame_width}x{frame_height}")

                # Create output directory for this frame size
                frame_dir = (
                    output_dir / f"{character_name}_{frame_width}x{frame_height}"
                )
                frame_dir.mkdir(exist_ok=True)

                # Cut sprites using current logic
                frame_count = 0
                for row in range(3):  # 3 rows
                    for col in range(4):  # Assume 4 columns max
                        x = col * frame_width
                        y = row * frame_height

                        # Skip if we'd go outside the sheet
                        if (
                            x + frame_width > sheet_width
                            or y + frame_height > sheet_height
                        ):
                            continue

                        # Extract frame
                        frame = pygame.Surface(
                            (frame_width, frame_height), pygame.SRCALPHA
                        )
                        frame.blit(
                            original_sheet, (0, 0), (x, y, frame_width, frame_height)
                        )

                        # Save frame
                        frame_filename = f"row{row}_col{col}_frame{frame_count}.png"
                        pygame.image.save(frame, str(frame_dir / frame_filename))

                        frame_count += 1

                print(
                    f"Generated {frame_count} frames for {frame_width}x{frame_height}"
                )

    def test_current_animation_loading(self):
        """Test the current animation loading system."""
        print("\n=== CURRENT ANIMATION LOADING TEST ===")

        for character_name, sprite_path in [
            ("danger", get_danger_sprite()),
            ("rose", get_rose_sprite()),
        ]:
            if not os.path.exists(sprite_path):
                print(f"Skipping {character_name} - file not found")
                continue

            print(f"\nLoading {character_name} animations...")

            # Load animations using current system
            animations = load_character_animations(sprite_path, 64, 64)

            print(f"Walking frames: {len(animations['walking'])}")
            print(f"Jumping frames: {len(animations['jumping'])}")
            print(f"Attacking frames: {len(animations['attacking'])}")

            # Save animation frames
            output_dir = (
                Path(__file__).parent.parent
                / "test-artifacts"
                / "sprite_output"
                / f"{character_name}_current_system"
            )
            output_dir.mkdir(exist_ok=True, parents=True)

            for anim_name, frames in animations.items():
                for i, frame in enumerate(frames):
                    filename = f"{anim_name}_frame_{i}.png"
                    pygame.image.save(frame, str(output_dir / filename))

            print(f"Saved animation frames to: {output_dir}")

    def test_calculate_optimal_frame_size(self):
        """Try to calculate the optimal frame size based on sprite sheet dimensions."""
        print("\n=== CALCULATING OPTIMAL FRAME SIZE ===")

        for character_name, sprite_path in [
            ("danger", get_danger_sprite()),
            ("rose", get_rose_sprite()),
        ]:
            if not os.path.exists(sprite_path):
                print(f"Skipping {character_name} - file not found")
                continue

            sheet = pygame.image.load(sprite_path)
            width, height = sheet.get_width(), sheet.get_height()

            print(f"\n{character_name.upper()} sprite sheet: {width}x{height}")

            # Try different grid assumptions
            grid_options = [
                (
                    4,
                    3,
                    "4 cols, 3 rows",
                ),  # 4 walking, 4 jumping, 3 attacking + 1 effect
                (3, 3, "3 cols, 3 rows"),  # 3 frames each
                (4, 4, "4 cols, 4 rows"),  # 4x4 grid
            ]

            for cols, rows, description in grid_options:
                frame_width = width // cols
                frame_height = height // rows
                print(f"  {description}: {frame_width}x{frame_height} per frame")

                # Check if this gives us reasonable frame sizes
                if 16 <= frame_width <= 128 and 16 <= frame_height <= 128:
                    print("    ^ This looks reasonable!")


if __name__ == "__main__":
    # Run the tests directly
    test = TestSpriteCutting()
    test.setup_class()
    test.test_sprite_sheet_dimensions()
    test.test_sprite_cutting_visualization()
    test.test_current_animation_loading()
    test.test_calculate_optimal_frame_size()
    print("\n=== TEST COMPLETE ===")
    print("Check the 'tests/sprite_output' directory for visual results!")
