"""Unit tests for AttackCharacter class.

Tests sprite animation system with proper mocking of pygame and time functions.
"""

from unittest.mock import Mock, patch

from src.config.constants import COLOR_PLACEHOLDER
from src.utils.attack_character import AttackCharacter


class TestAttackCharacterInitialization:
    """Tests for AttackCharacter initialization."""

    @patch("src.utils.attack_character.load_character_individual_files")
    def test_init_with_valid_sprite_path(self, mock_load_files):
        """AttackCharacter should initialize with valid sprite path."""
        # Arrange
        mock_frames = [Mock() for _ in range(6)]
        mock_load_files.return_value = {
            "idle": [Mock() for _ in range(4)],
            "walk": [Mock() for _ in range(5)],
            "attack": mock_frames,
            "jump": [Mock() for _ in range(3)],
            "hurt": [Mock() for _ in range(2)],
            "victory": [Mock() for _ in range(4)],
        }

        # Act
        character = AttackCharacter("test_char", "test.png", (128, 128))

        # Assert
        assert character.character_name == "test_char"
        assert character.scale == (128, 128)
        assert character.current_frame == 0
        assert character.current_animation == "attack"  # Should start with attack
        assert len(character.animations["attack"]) == 6

    @patch("src.utils.attack_character.load_character_individual_files")
    def test_init_with_empty_sprite_path(self, mock_load_files):
        """AttackCharacter should handle empty sprite path."""
        # Arrange - Return empty animations to trigger placeholder
        mock_load_files.return_value = {}

        # Act
        character = AttackCharacter("test_char", "", (128, 128))

        # Assert
        assert character.character_name == "test_char"
        # Should have placeholder animations
        assert "attack" in character.animations
        assert len(character.animations["attack"]) > 0

    @patch("src.utils.attack_character.load_character_individual_files")
    def test_init_handles_loading_error(self, mock_load_files):
        """AttackCharacter should handle loading errors gracefully."""
        # Arrange
        mock_load_files.side_effect = Exception("Loading error")

        # Act
        character = AttackCharacter("test_char", "error.png", (128, 128))

        # Assert
        assert character.character_name == "test_char"
        # Should have placeholder animations - AttackCharacter uses "attacking" not "attack"
        assert "attacking" in character.animations
        assert len(character.animations["attacking"]) > 0


class TestAttackFrameProperty:
    """Tests for the attack_frames property."""

    @patch("src.utils.attack_character.load_character_individual_files")
    def test_attack_frames_property(self, mock_load_files):
        """attack_frames property should return attack animation frames."""
        # Arrange
        attack_frames = [Mock() for _ in range(6)]
        mock_load_files.return_value = {
            "attack": attack_frames,
            "idle": [Mock() for _ in range(4)],
        }

        # Act
        character = AttackCharacter("test_char", "test.png")

        # Assert
        assert character.attack_frames == attack_frames


class TestAnimationUpdate:
    """Tests for animation update functionality."""

    @patch("time.time")
    @patch("src.utils.attack_character.load_character_individual_files")
    def test_update_advances_frame_after_animation_speed(
        self, mock_load_files, mock_time
    ):
        """Update should advance frame after animation speed duration."""
        # Arrange
        mock_load_files.return_value = {
            "attack": [Mock() for _ in range(6)],
            "idle": [Mock() for _ in range(4)],
        }

        # Set up time mock before creating character
        mock_time.return_value = 0
        character = AttackCharacter("test_char", "test.png")

        # Mock time progression - advance time by more than animation_speed
        mock_time.return_value = 0.1

        # Act
        character.update()

        # Assert
        assert character.current_frame == 1

    @patch("time.time")
    @patch("src.utils.attack_character.load_character_individual_files")
    def test_update_wraps_around_at_end(self, mock_load_files, mock_time):
        """Update should wrap to frame 0 when reaching end of animation."""
        # Arrange
        mock_load_files.return_value = {
            "attack": [Mock() for _ in range(3)],
            "idle": [Mock() for _ in range(4)],
        }

        # Set up time mock before creating character
        mock_time.return_value = 0
        character = AttackCharacter("test_char", "test.png")
        character.current_frame = 2  # Last frame
        character.loop_animation = True

        # Mock time progression
        mock_time.return_value = 0.1

        # Act
        character.update()

        # Assert
        assert character.current_frame == 0

    @patch("time.time")
    @patch("src.utils.attack_character.load_character_individual_files")
    def test_update_does_not_advance_before_animation_speed(
        self, mock_load_files, mock_time
    ):
        """Update should not advance frame before animation speed duration."""
        # Arrange
        mock_load_files.return_value = {
            "attack": [Mock() for _ in range(6)],
            "idle": [Mock() for _ in range(4)],
        }

        # Set up time mock before creating character
        mock_time.return_value = 0
        character = AttackCharacter("test_char", "test.png")

        # Mock time with minimal progression (less than animation_speed)
        # Attack animation speed is ANIMATION_ATTACK_DURATION/1000/6 = 50/1000/6 ≈ 0.0083
        mock_time.return_value = 0.005  # Less than attack animation speed

        # Act
        character.update()

        # Assert
        assert character.current_frame == 0


class TestSpriteRetrieval:
    """Tests for getting current sprite functionality."""

    @patch("src.utils.attack_character.load_character_individual_files")
    def test_get_current_sprite_returns_correct_frame(self, mock_load_files):
        """get_current_sprite should return the current frame."""
        # Arrange
        frame0 = Mock()
        frame1 = Mock()
        frame2 = Mock()
        mock_load_files.return_value = {
            "attack": [frame0, frame1, frame2],
            "idle": [Mock() for _ in range(4)],
        }
        character = AttackCharacter("test_char", "test.png")
        character.current_frame = 1

        # Act
        sprite = character.get_current_sprite()

        # Assert
        assert sprite == frame1

    @patch("src.utils.attack_character.load_character_individual_files")
    def test_get_current_sprite_handles_invalid_frame_index(self, mock_load_files):
        """get_current_sprite should handle invalid frame indices."""
        # Arrange
        mock_load_files.return_value = {
            "attack": [Mock()],
            "idle": [Mock() for _ in range(4)],
        }
        character = AttackCharacter("test_char", "test.png")
        character.current_frame = 999  # Invalid index

        # Act
        sprite = character.get_current_sprite()

        # Assert
        # Should return a surface (fallback)
        assert sprite is not None

    @patch("src.utils.attack_character.pygame.Surface")
    @patch("src.utils.attack_character.load_character_individual_files")
    def test_get_current_sprite_handles_empty_frames(
        self, mock_load_files, mock_surface
    ):
        """get_current_sprite should handle empty animation frames."""
        # Arrange
        mock_load_files.return_value = {}  # No animations
        fallback_surface = Mock()
        mock_surface.return_value = fallback_surface

        character = AttackCharacter("test_char", "test.png")

        # Act
        character.get_current_sprite()

        # Assert
        # Should create and return fallback surface
        mock_surface.assert_called()
        fallback_surface.fill.assert_called_with(COLOR_PLACEHOLDER)


class TestUtilityMethods:
    """Tests for utility methods."""

    @patch("src.utils.attack_character.load_character_individual_files")
    def test_get_frame_count(self, mock_load_files):
        """get_frame_count should return number of frames in current animation."""
        # Arrange
        mock_load_files.return_value = {
            "attack": [Mock() for _ in range(6)],
            "idle": [Mock() for _ in range(4)],
        }
        character = AttackCharacter("test_char", "test.png")

        # Act
        count = character.get_frame_count()

        # Assert
        assert count == 6

    @patch("src.utils.attack_character.load_character_individual_files")
    def test_get_animation_info(self, mock_load_files):
        """get_animation_info should return formatted animation info."""
        # Arrange
        mock_load_files.return_value = {
            "attack": [Mock() for _ in range(6)],
            "idle": [Mock() for _ in range(4)],
        }
        character = AttackCharacter("test_char", "test.png")
        character.current_frame = 1

        # Act
        info = character.get_animation_info()

        # Assert
        assert info == "Attack (Frame 2/6)"
