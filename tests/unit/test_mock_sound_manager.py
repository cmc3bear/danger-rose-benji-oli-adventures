"""Tests for MockSoundManager to ensure it behaves like the real SoundManager."""

from tests.mocks.mock_sound_manager import MockSoundManager


class TestMockSoundManager:
    """Test that MockSoundManager provides the expected interface."""

    def test_initialization(self):
        """MockSoundManager should initialize with default values."""
        # Act
        sound_manager = MockSoundManager()

        # Assert
        assert sound_manager.is_initialized is True
        assert sound_manager.master_volume == 1.0
        assert sound_manager.music_volume == 1.0
        assert sound_manager.sfx_volume == 1.0
        assert sound_manager.current_music is None
        assert sound_manager.music_playing is False

    def test_volume_setters_clamp_values(self):
        """Volume setters should clamp values between 0 and 1."""
        # Arrange
        sound_manager = MockSoundManager()

        # Test clamping high values
        sound_manager.set_master_volume(2.0)
        assert sound_manager.master_volume == 1.0

        sound_manager.set_music_volume(1.5)
        assert sound_manager.music_volume == 1.0

        sound_manager.set_sfx_volume(10.0)
        assert sound_manager.sfx_volume == 1.0

        # Test clamping low values
        sound_manager.set_master_volume(-0.5)
        assert sound_manager.master_volume == 0.0

        sound_manager.set_music_volume(-1.0)
        assert sound_manager.music_volume == 0.0

        sound_manager.set_sfx_volume(-0.1)
        assert sound_manager.sfx_volume == 0.0

    def test_volume_getters_return_current_values(self):
        """Volume getters should return current volume values."""
        # Arrange
        sound_manager = MockSoundManager()
        sound_manager.set_master_volume(0.5)
        sound_manager.set_music_volume(0.7)
        sound_manager.set_sfx_volume(0.3)

        # Act & Assert
        assert sound_manager.get_master_volume() == 0.5
        assert sound_manager.get_music_volume() == 0.7
        assert sound_manager.get_sfx_volume() == 0.3

    def test_all_methods_are_mocked(self):
        """All required methods should be mocked."""
        # Arrange
        sound_manager = MockSoundManager()

        # Assert all methods exist and are callable
        methods = [
            "play_music",
            "play_sfx",
            "stop_music",
            "pause_music",
            "unpause_music",
            "crossfade_music",
            "is_music_playing",
            "cleanup",
        ]

        for method_name in methods:
            assert hasattr(sound_manager, method_name)
            method = getattr(sound_manager, method_name)
            assert callable(method)

    def test_mock_methods_can_be_called(self):
        """Mock methods should be callable without errors."""
        # Arrange
        sound_manager = MockSoundManager()

        # Act - call all methods
        sound_manager.play_music("test.wav")
        sound_manager.play_sfx("effect.wav")
        sound_manager.stop_music()
        sound_manager.pause_music()
        sound_manager.unpause_music()
        sound_manager.crossfade_music("new.wav", duration_ms=1000)
        sound_manager.is_music_playing()
        sound_manager.cleanup()

        # Assert - methods were called (using Mock's built-in tracking)
        sound_manager.play_music.assert_called_with("test.wav")
        sound_manager.play_sfx.assert_called_with("effect.wav")
        sound_manager.stop_music.assert_called()
        sound_manager.pause_music.assert_called()
        sound_manager.unpause_music.assert_called()
        sound_manager.crossfade_music.assert_called_with("new.wav", duration_ms=1000)
        sound_manager.is_music_playing.assert_called()
        sound_manager.cleanup.assert_called()
