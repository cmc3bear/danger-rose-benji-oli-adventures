"""Mock SoundManager for testing without audio hardware."""

from unittest.mock import Mock


class MockSoundManager:
    """Mock implementation of SoundManager for testing."""

    def __init__(self, *args, **kwargs):
        """Initialize mock sound manager."""
        self.is_initialized = True
        self.master_volume = 1.0
        self.music_volume = 1.0
        self.sfx_volume = 1.0
        self.current_music = None
        self.music_playing = False

        # Mock all methods
        self.play_music = Mock()
        self.play_sfx = Mock()
        self.stop_music = Mock()
        self.pause_music = Mock()
        self.unpause_music = Mock()
        self.set_master_volume = Mock(side_effect=self._set_master_volume)
        self.set_music_volume = Mock(side_effect=self._set_music_volume)
        self.set_sfx_volume = Mock(side_effect=self._set_sfx_volume)
        self.get_master_volume = Mock(side_effect=lambda: self.master_volume)
        self.get_music_volume = Mock(side_effect=lambda: self.music_volume)
        self.get_sfx_volume = Mock(side_effect=lambda: self.sfx_volume)
        self.crossfade_music = Mock()
        self.is_music_playing = Mock(side_effect=lambda: self.music_playing)
        self.cleanup = Mock()

    def _set_master_volume(self, volume):
        """Mock setting master volume."""
        self.master_volume = max(0.0, min(1.0, volume))

    def _set_music_volume(self, volume):
        """Mock setting music volume."""
        self.music_volume = max(0.0, min(1.0, volume))

    def _set_sfx_volume(self, volume):
        """Mock setting SFX volume."""
        self.sfx_volume = max(0.0, min(1.0, volume))
