"""Tests for the sound manager system."""

from unittest.mock import Mock, patch

import pygame
import pytest

from src.config.constants import (
    DEFAULT_MASTER_VOLUME,
    DEFAULT_MUSIC_VOLUME,
    DEFAULT_SFX_VOLUME,
)
from src.managers.sound_manager import SoundManager


class TestSoundManager:
    """Test the SoundManager class."""

    @pytest.fixture
    def setup_pygame(self):
        """Initialize pygame for tests."""
        pygame.init()
        pygame.mixer.quit()  # Quit mixer to let tests control it
        yield
        pygame.quit()

    @pytest.fixture
    def sound_manager(self, setup_pygame):
        """Create a fresh sound manager instance."""
        # Clear singleton instance
        SoundManager._instance = None

        # Mock all pygame.mixer methods
        with patch("pygame.mixer.init"):
            with patch("pygame.mixer.set_reserved"):
                with patch("pygame.mixer.Channel"):
                    with patch("pygame.mixer.music.set_volume"):
                        sm = SoundManager()
        return sm

    def test_singleton_pattern(self, setup_pygame):
        """Test that SoundManager follows singleton pattern."""
        SoundManager._instance = None
        with patch("pygame.mixer.init"):
            with patch("pygame.mixer.set_reserved"):
                with patch("pygame.mixer.Channel"):
                    with patch("pygame.mixer.music.set_volume"):
                        sm1 = SoundManager()
                        sm2 = SoundManager()
                        assert sm1 is sm2

    def test_initialization(self, sound_manager):
        """Test sound manager initializes with correct defaults."""
        assert sound_manager.master_volume == DEFAULT_MASTER_VOLUME
        assert sound_manager.music_volume == DEFAULT_MUSIC_VOLUME
        assert sound_manager.sfx_volume == DEFAULT_SFX_VOLUME
        assert sound_manager.current_music is None
        assert sound_manager.music_paused is False
        assert len(sound_manager.sfx_channels) == 8
        assert len(sound_manager.sfx_cache) == 0

    def test_volume_controls(self, sound_manager):
        """Test volume setting methods."""
        # Test master volume
        sound_manager.set_master_volume(0.5)
        assert sound_manager.master_volume == 0.5

        # Test clamping
        sound_manager.set_master_volume(1.5)
        assert sound_manager.master_volume == 1.0

        sound_manager.set_master_volume(-0.5)
        assert sound_manager.master_volume == 0.0

        # Test music volume
        sound_manager.set_music_volume(0.8)
        assert sound_manager.music_volume == 0.8

        # Test SFX volume
        sound_manager.set_sfx_volume(0.6)
        assert sound_manager.sfx_volume == 0.6

    def test_get_volumes(self, sound_manager):
        """Test getting current volume settings."""
        sound_manager.set_master_volume(0.9)
        sound_manager.set_music_volume(0.7)
        sound_manager.set_sfx_volume(0.5)

        volumes = sound_manager.get_volumes()
        assert volumes["master"] == 0.9
        assert volumes["music"] == 0.7
        assert volumes["sfx"] == 0.5

    @patch("pygame.mixer.music.load")
    @patch("pygame.mixer.music.play")
    @patch("os.path.exists", return_value=True)
    def test_play_music(self, mock_exists, mock_play, mock_load, sound_manager):
        """Test playing background music."""
        sound_manager.play_music("test_music.ogg")

        mock_load.assert_called_once_with("test_music.ogg")
        mock_play.assert_called_once_with(-1, fade_ms=0)
        assert sound_manager.current_music == "test_music.ogg"
        assert not sound_manager.music_paused

    @patch("pygame.mixer.music.load")
    @patch("pygame.mixer.music.play")
    @patch("os.path.exists", return_value=True)
    def test_play_music_with_fade(
        self, mock_exists, mock_play, mock_load, sound_manager
    ):
        """Test playing music with fade in."""
        sound_manager.play_music("test_music.ogg", fade_ms=1000)

        mock_play.assert_called_once_with(-1, fade_ms=1000)

    @patch("os.path.exists", return_value=False)
    def test_play_missing_music(self, mock_exists, sound_manager, capsys):
        """Test handling of missing music file."""
        sound_manager.play_music("missing.ogg")

        captured = capsys.readouterr()
        assert "Warning: Music file not found" in captured.out
        assert sound_manager.current_music is None

    @patch("pygame.mixer.music.stop")
    def test_stop_music(self, mock_stop, sound_manager):
        """Test stopping music."""
        sound_manager.current_music = "test.ogg"
        sound_manager.stop_music()

        mock_stop.assert_called_once()
        assert sound_manager.current_music is None
        assert not sound_manager.music_paused

    @patch("pygame.mixer.music.fadeout")
    def test_stop_music_with_fade(self, mock_fadeout, sound_manager):
        """Test stopping music with fade out."""
        sound_manager.current_music = "test.ogg"
        sound_manager.stop_music(fade_ms=500)

        mock_fadeout.assert_called_once_with(500)

    @patch("pygame.mixer.music.pause")
    def test_pause_music(self, mock_pause, sound_manager):
        """Test pausing music."""
        sound_manager.current_music = "test.ogg"
        sound_manager.pause_music()

        mock_pause.assert_called_once()
        assert sound_manager.music_paused

    @patch("pygame.mixer.music.unpause")
    def test_unpause_music(self, mock_unpause, sound_manager):
        """Test unpausing music."""
        sound_manager.current_music = "test.ogg"
        sound_manager.music_paused = True
        sound_manager.unpause_music()

        mock_unpause.assert_called_once()
        assert not sound_manager.music_paused

    @patch("pygame.mixer.Sound")
    @patch("pygame.mixer.find_channel")
    @patch("os.path.exists", return_value=True)
    def test_play_sfx(self, mock_exists, mock_find_channel, mock_sound, sound_manager):
        """Test playing sound effects."""
        # Setup mocks
        mock_channel = Mock()
        mock_find_channel.return_value = mock_channel
        mock_sound_obj = Mock()
        mock_sound.return_value = mock_sound_obj

        # Play sound
        channel = sound_manager.play_sfx("test_sfx.wav")

        # Verify
        mock_sound.assert_called_once_with("test_sfx.wav")
        mock_channel.play.assert_called_once_with(mock_sound_obj, loops=0, maxtime=0)
        assert channel == mock_channel
        assert "test_sfx.wav" in sound_manager.sfx_cache

    @patch("pygame.mixer.Sound")
    @patch("os.path.exists", return_value=True)
    def test_sfx_caching(self, mock_exists, mock_sound, sound_manager):
        """Test that sound effects are cached."""
        mock_sound_obj = Mock()
        mock_sound.return_value = mock_sound_obj

        # Play same sound twice
        with patch("pygame.mixer.find_channel"):
            sound_manager.play_sfx("cached.wav")
            sound_manager.play_sfx("cached.wav")

        # Sound should only be loaded once
        mock_sound.assert_called_once_with("cached.wav")

    def test_stop_sfx_single_channel(self, sound_manager):
        """Test stopping a specific sound effect channel."""
        mock_channel = Mock()
        sound_manager.stop_sfx(mock_channel)
        mock_channel.stop.assert_called_once()

    def test_stop_all_sfx(self, sound_manager):
        """Test stopping all sound effects."""
        # Create mock channels
        sound_manager.sfx_channels = [Mock() for _ in range(8)]

        sound_manager.stop_sfx()

        # All channels should be stopped
        for channel in sound_manager.sfx_channels:
            channel.stop.assert_called_once()

    @patch("pygame.mixer.music.get_volume", return_value=0.7)
    @patch("pygame.mixer.music.set_volume")
    def test_duck_audio(self, mock_set_volume, mock_get_volume, sound_manager):
        """Test audio ducking."""
        sound_manager.duck_audio(duck_level=0.3)

        # Volume should be reduced to 30%
        mock_set_volume.assert_called_once_with(0.7 * 0.3)

    @patch("pygame.mixer.music.set_volume")
    def test_restore_audio_levels(self, mock_set_volume, sound_manager):
        """Test restoring audio after ducking."""
        sound_manager.master_volume = 0.8
        sound_manager.music_volume = 0.9

        sound_manager.restore_audio_levels()

        # Should restore to master * music volume
        mock_set_volume.assert_called_once_with(0.8 * 0.9)

    def test_preload_sound(self, sound_manager):
        """Test preloading sounds into cache."""
        with patch("os.path.exists", return_value=True):
            with patch("pygame.mixer.Sound") as mock_sound:
                mock_sound_obj = Mock()
                mock_sound.return_value = mock_sound_obj

                sound_manager.preload_sound("preload.wav")

                assert "preload.wav" in sound_manager.sfx_cache
                mock_sound.assert_called_once_with("preload.wav")

    def test_clear_cache(self, sound_manager):
        """Test clearing the sound cache."""
        sound_manager.sfx_cache = {"test1.wav": Mock(), "test2.wav": Mock()}

        sound_manager.clear_cache()

        assert len(sound_manager.sfx_cache) == 0

    @patch("pygame.mixer.music.stop")
    @patch("pygame.mixer.quit")
    def test_shutdown(self, mock_quit, mock_stop, sound_manager):
        """Test clean shutdown of sound system."""
        # Add some mock data
        sound_manager.current_music = "test.ogg"
        sound_manager.sfx_cache = {"test.wav": Mock()}
        sound_manager.sfx_channels = [Mock() for _ in range(8)]

        sound_manager.shutdown()

        mock_stop.assert_called_once()
        assert len(sound_manager.sfx_cache) == 0
        mock_quit.assert_called_once()
