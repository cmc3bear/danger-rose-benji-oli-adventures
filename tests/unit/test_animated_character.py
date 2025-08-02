"""Unit tests for AnimatedCharacter class.

Tests character animation system with multiple animation states.
"""

from unittest.mock import Mock, patch

from src.config.constants import ANIMATION_DEFAULT_DURATION
from src.utils.animated_character import AnimatedCharacter


class TestAnimatedCharacterInitialization:
    """Tests for AnimatedCharacter initialization."""

    @patch("src.utils.animated_character.load_character_animations")
    @patch("src.utils.animated_character.time.time")
    def test_init_loads_animations(self, mock_time, mock_load_animations):
        """AnimatedCharacter should load animations on initialization."""
        # Arrange
        mock_time.return_value = 0.0
        mock_animations = {
            "walking": [Mock() for _ in range(4)],
            "jumping": [Mock() for _ in range(4)],
            "attacking": [Mock() for _ in range(3)],
        }
        mock_load_animations.return_value = mock_animations

        # Act
        character = AnimatedCharacter("test_char", "test.png", (128, 128))

        # Assert
        mock_load_animations.assert_called_once_with("test.png", scale=(128, 128))
        assert character.character_name == "test_char"
        assert character.scale == (128, 128)
        assert character.animations == mock_animations
        assert character.current_animation == "walking"
        assert character.current_frame == 0

    @patch("src.utils.animated_character.load_character_animations")
    @patch("src.utils.animated_character.time.time")
    def test_init_sets_animation_parameters(self, mock_time, mock_load_animations):
        """AnimatedCharacter should initialize animation parameters correctly."""
        # Arrange
        mock_time.return_value = 1.5
        mock_load_animations.return_value = {"walking": [Mock()]}

        # Act
        character = AnimatedCharacter("test", "test.png")

        # Assert
        assert (
            character.animation_speed == ANIMATION_DEFAULT_DURATION / 1000.0
        )  # Convert ms to seconds
        assert character.last_frame_time == 1.5
        assert character.animation_cycle == ["walking", "jumping", "attacking"]
        assert character.current_cycle_index == 0
        assert character.animation_hold_time == 2.0
        assert character.animation_start_time == 1.5


class TestAnimationUpdate:
    """Tests for animation update logic."""

    @patch("src.utils.animated_character.load_character_animations")
    @patch("src.utils.animated_character.time.time")
    def test_update_advances_frame_after_animation_speed(
        self, mock_time, mock_load_animations
    ):
        """update should advance frame when animation_speed time has passed."""
        # Arrange
        mock_animations = {
            "walking": [Mock() for _ in range(4)],
            "jumping": [Mock() for _ in range(4)],
            "attacking": [Mock() for _ in range(3)],
        }
        mock_load_animations.return_value = mock_animations
        mock_time.return_value = 0.0
        character = AnimatedCharacter("test", "test.png")

        # Advance time by animation_speed
        mock_time.return_value = 0.3  # More than 0.2 animation_speed

        # Act
        character.update()

        # Assert
        assert character.current_frame == 1
        assert character.last_frame_time == 0.3

    @patch("src.utils.animated_character.load_character_animations")
    @patch("src.utils.animated_character.time.time")
    def test_update_wraps_frame_at_animation_end(self, mock_time, mock_load_animations):
        """update should wrap frame to 0 when reaching end of animation."""
        # Arrange
        mock_animations = {
            "walking": [Mock() for _ in range(4)],
            "jumping": [Mock() for _ in range(4)],
            "attacking": [Mock() for _ in range(3)],
        }
        mock_load_animations.return_value = mock_animations
        mock_time.return_value = 0.0
        character = AnimatedCharacter("test", "test.png")
        character.current_frame = 3  # Last frame of walking animation

        # Advance time
        mock_time.return_value = 0.3

        # Act
        character.update()

        # Assert
        assert character.current_frame == 0  # Wrapped around

    @patch("src.utils.animated_character.load_character_animations")
    @patch("src.utils.animated_character.time.time")
    def test_update_cycles_animations_after_hold_time(
        self, mock_time, mock_load_animations
    ):
        """update should cycle to next animation after hold_time."""
        # Arrange
        mock_animations = {
            "walking": [Mock() for _ in range(4)],
            "jumping": [Mock() for _ in range(4)],
            "attacking": [Mock() for _ in range(3)],
        }
        mock_load_animations.return_value = mock_animations
        mock_time.return_value = 0.0
        character = AnimatedCharacter("test", "test.png")

        # Advance time past hold_time
        mock_time.return_value = 2.5  # More than 2.0 hold_time

        # Act
        character.update()

        # Assert
        assert character.current_animation == "jumping"  # Next in cycle
        assert character.current_cycle_index == 1
        assert character.current_frame == 0  # Reset to first frame
        assert character.animation_start_time == 2.5

    @patch("src.utils.animated_character.load_character_animations")
    @patch("src.utils.animated_character.time.time")
    def test_update_wraps_animation_cycle(self, mock_time, mock_load_animations):
        """update should wrap animation cycle back to beginning."""
        # Arrange
        mock_animations = {
            "walking": [Mock()],
            "jumping": [Mock()],
            "attacking": [Mock()],
        }
        mock_load_animations.return_value = mock_animations
        mock_time.return_value = 0.0
        character = AnimatedCharacter("test", "test.png")
        character.current_cycle_index = 2  # Last animation
        character.current_animation = "attacking"

        # Advance time past hold_time
        mock_time.return_value = 2.5

        # Act
        character.update()

        # Assert
        assert character.current_animation == "walking"  # Back to first
        assert character.current_cycle_index == 0


class TestSpriteRetrieval:
    """Tests for getting current sprite."""

    @patch("src.utils.animated_character.load_character_animations")
    @patch("src.utils.animated_character.pygame.Surface")
    def test_get_current_sprite_returns_correct_frame(
        self, mock_surface_class, mock_load_animations
    ):
        """get_current_sprite should return current frame of current animation."""
        # Arrange
        mock_frame = Mock()
        mock_animations = {
            "walking": [mock_frame, Mock(), Mock()],
            "jumping": [Mock()],
            "attacking": [Mock()],
        }
        mock_load_animations.return_value = mock_animations
        character = AnimatedCharacter("test", "test.png")
        character.current_animation = "walking"
        character.current_frame = 0

        # Act
        result = character.get_current_sprite()

        # Assert
        assert result == mock_frame

    @patch("src.utils.animated_character.load_character_animations")
    @patch("src.utils.animated_character.pygame.Surface")
    def test_get_current_sprite_fallback_to_walking(
        self, mock_surface_class, mock_load_animations
    ):
        """get_current_sprite should fallback to walking animation if current is invalid."""
        # Arrange
        mock_walking_frame = Mock()
        mock_animations = {
            "walking": [mock_walking_frame],
            "jumping": [],  # Empty
            "attacking": [],
        }
        mock_load_animations.return_value = mock_animations
        character = AnimatedCharacter("test", "test.png")
        character.current_animation = "jumping"  # Has no frames

        # Act
        result = character.get_current_sprite()

        # Assert
        assert result == mock_walking_frame

    @patch("src.utils.animated_character.load_character_animations")
    @patch("src.utils.animated_character.pygame.Surface")
    def test_get_current_sprite_ultimate_fallback(
        self, mock_surface_class, mock_load_animations
    ):
        """get_current_sprite should create placeholder if no animations available."""
        # Arrange
        mock_fallback = Mock()
        mock_surface_class.return_value = mock_fallback
        mock_animations = {
            "walking": [],  # Empty
            "jumping": [],
            "attacking": [],
        }
        mock_load_animations.return_value = mock_animations
        character = AnimatedCharacter("test", "test.png", (64, 64))

        # Act
        result = character.get_current_sprite()

        # Assert
        mock_surface_class.assert_called_once_with((64, 64))
        mock_fallback.fill.assert_called_once_with((255, 0, 255))
        assert result == mock_fallback


class TestAnimationControl:
    """Tests for animation control methods."""

    @patch("src.utils.animated_character.load_character_animations")
    @patch("src.utils.animated_character.time.time")
    def test_set_animation_changes_current_animation(
        self, mock_time, mock_load_animations
    ):
        """set_animation should change current animation and reset frame."""
        # Arrange
        mock_animations = {
            "walking": [Mock()],
            "jumping": [Mock()],
            "attacking": [Mock()],
        }
        mock_load_animations.return_value = mock_animations
        mock_time.return_value = 0.0
        character = AnimatedCharacter("test", "test.png")
        character.current_frame = 2

        # Set new time for animation change
        mock_time.return_value = 5.0

        # Act
        character.set_animation("jumping")

        # Assert
        assert character.current_animation == "jumping"
        assert character.current_frame == 0
        assert character.animation_start_time == 5.0

    @patch("src.utils.animated_character.load_character_animations")
    def test_set_animation_ignores_invalid_animation(self, mock_load_animations):
        """set_animation should ignore invalid animation names."""
        # Arrange
        mock_animations = {
            "walking": [Mock()],
            "jumping": [Mock()],
            "attacking": [Mock()],
        }
        mock_load_animations.return_value = mock_animations
        character = AnimatedCharacter("test", "test.png")
        original_animation = character.current_animation

        # Act
        character.set_animation("invalid_animation")

        # Assert
        assert character.current_animation == original_animation  # Unchanged

    @patch("src.utils.animated_character.load_character_animations")
    def test_get_animation_info(self, mock_load_animations):
        """get_animation_info should return formatted animation info."""
        # Arrange
        mock_animations = {
            "walking": [Mock() for _ in range(4)],
            "jumping": [Mock()],
            "attacking": [Mock()],
        }
        mock_load_animations.return_value = mock_animations
        character = AnimatedCharacter("test", "test.png")
        character.current_animation = "walking"
        character.current_frame = 2

        # Act
        result = character.get_animation_info()

        # Assert
        assert result == "Walking (Frame 3/4)"  # 1-indexed display
