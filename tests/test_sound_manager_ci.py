"""Tests for SoundManager in CI environments without audio."""

from unittest.mock import Mock, patch

import pygame

from src.managers.sound_manager import SoundManager


class TestSoundManagerCI:
    """Test SoundManager handles missing audio gracefully."""

    def test_sound_manager_handles_no_audio_device(self):
        """Test SoundManager initializes without crashing when no audio device."""
        # Mock pygame.mixer.init to raise error
        with patch("pygame.mixer.init", side_effect=pygame.error("No audio device")):
            # Should not crash
            sm = SoundManager()
            assert sm is not None

    def test_sound_manager_methods_safe_without_mixer(self):
        """Test all methods handle uninitialized mixer gracefully."""
        # Mock get_init to return None (not initialized)
        with patch("pygame.mixer.get_init", return_value=None):
            sm = SoundManager()

            # These should all return safely without crashing
            sm.play_music("test.ogg")
            sm.stop_music()
            sm.pause_music()
            sm.unpause_music()
            result = sm.play_sfx("test.wav")
            assert result is None
            sm.duck_audio()
            sm.restore_audio_levels()

    def test_sound_manager_singleton(self):
        """Test SoundManager maintains singleton pattern."""
        sm1 = SoundManager()
        sm2 = SoundManager()
        assert sm1 is sm2

    def test_volume_methods(self):
        """Test volume methods work without mixer."""
        with patch("pygame.mixer.get_init", return_value=None):
            sm = SoundManager()

            # Should handle volume changes
            sm.set_master_volume(0.5)
            assert sm.master_volume == 0.5

            sm.set_music_volume(0.7)
            assert sm.music_volume == 0.7

            sm.set_sfx_volume(0.3)
            assert sm.sfx_volume == 0.3

            volumes = sm.get_volumes()
            assert volumes["master"] == 0.5
            assert volumes["music"] == 0.7
            assert volumes["sfx"] == 0.3

    def test_crossfade_music(self):
        """Test crossfade music method."""
        with patch("pygame.mixer.get_init", return_value=True):
            with patch("pygame.time.wait"):
                sm = SoundManager()
                sm.current_music = "old.ogg"

                # Should handle crossfade
                sm.crossfade_music("new.ogg", 1000)

    def test_stop_sfx(self):
        """Test stopping sound effects."""
        with patch("pygame.mixer.get_init", return_value=None):
            sm = SoundManager()

            # Should handle without error
            sm.stop_sfx()
            sm.stop_sfx(None)

    def test_preload_sound(self):
        """Test preloading sounds."""
        with patch("os.path.exists", return_value=True):
            with patch("pygame.mixer.Sound"):
                sm = SoundManager()

                # Should cache the sound
                sm.preload_sound("test.wav")
                assert "test.wav" in sm.sfx_cache

    def test_clear_cache(self):
        """Test clearing sound cache."""
        sm = SoundManager()
        sm.sfx_cache["test.wav"] = Mock()

        sm.clear_cache()
        assert len(sm.sfx_cache) == 0

    def test_shutdown(self):
        """Test shutdown method."""
        with patch("pygame.mixer.quit") as mock_quit:
            sm = SoundManager()
            sm.shutdown()
            mock_quit.assert_called_once()

    def test_setup_channels_with_mixer(self):
        """Test channel setup when mixer is initialized."""
        with patch("pygame.mixer.get_init", return_value=True):
            with patch("pygame.mixer.set_reserved") as mock_reserved:
                with patch("pygame.mixer.Channel") as mock_channel:
                    sm = SoundManager()
                    sm.sfx_channels = []
                    sm._setup_channels()

                    mock_reserved.assert_called_with(8)
                    assert mock_channel.call_count == 8

    def test_play_sfx_with_cache(self):
        """Test playing cached sound effect."""
        with patch("pygame.mixer.get_init", return_value=True):
            with patch("pygame.mixer.find_channel") as mock_find:
                mock_channel = Mock()
                mock_find.return_value = mock_channel

                sm = SoundManager()
                mock_sound = Mock()
                sm.sfx_cache["cached.wav"] = mock_sound

                result = sm.play_sfx("cached.wav")
                assert result == mock_channel
                mock_channel.play.assert_called_once()

    def test_music_pause_unpause(self):
        """Test pause/unpause with initialized mixer."""
        with patch("pygame.mixer.get_init", return_value=True):
            with patch("pygame.mixer.music.pause") as mock_pause:
                with patch("pygame.mixer.music.unpause") as mock_unpause:
                    sm = SoundManager()
                    sm.current_music = "test.ogg"

                    sm.pause_music()
                    assert sm.music_paused
                    mock_pause.assert_called_once()

                    sm.unpause_music()
                    assert not sm.music_paused
                    mock_unpause.assert_called_once()
