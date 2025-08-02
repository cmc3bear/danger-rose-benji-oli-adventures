"""Unit tests for the configuration system."""

import tempfile
from pathlib import Path

import pytest

from src.config.constants import (
    DEFAULT_MASTER_VOLUME,
    DEFAULT_MUSIC_VOLUME,
    DEFAULT_SFX_VOLUME,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from src.config.env_config import get_env, is_debug, is_development, load_env_config
from src.config.game_config import GameConfig


class TestConstants:
    """Test that constants are properly defined."""

    def test_screen_constants(self):
        """Test screen-related constants."""
        assert SCREEN_WIDTH == 1280
        assert SCREEN_HEIGHT == 720
        assert FPS == 60

    def test_audio_constants(self):
        """Test audio-related constants."""
        assert 0.0 <= DEFAULT_MASTER_VOLUME <= 1.0
        assert 0.0 <= DEFAULT_MUSIC_VOLUME <= 1.0
        assert 0.0 <= DEFAULT_SFX_VOLUME <= 1.0


class TestGameConfig:
    """Test the GameConfig class."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_config_initialization(self, temp_config_dir):
        """Test config initializes with defaults."""
        config = GameConfig(config_dir=temp_config_dir)

        assert not config.fullscreen
        assert config.master_volume == DEFAULT_MASTER_VOLUME
        assert config.music_volume == DEFAULT_MUSIC_VOLUME
        assert config.sfx_volume == DEFAULT_SFX_VOLUME

    def test_config_save_and_load(self, temp_config_dir):
        """Test saving and loading configuration."""
        config = GameConfig(config_dir=temp_config_dir)

        # Modify settings
        config.fullscreen = True
        config.master_volume = 0.5
        config.set("gameplay.difficulty", "hard")

        # Save
        assert config.save()

        # Create new config instance and verify it loads saved settings
        config2 = GameConfig(config_dir=temp_config_dir)
        assert config2.fullscreen
        assert config2.master_volume == 0.5
        assert config2.get("gameplay.difficulty") == "hard"

    def test_config_get_set(self, temp_config_dir):
        """Test getting and setting config values."""
        config = GameConfig(config_dir=temp_config_dir)

        # Test nested key access
        config.set("audio.test_value", 42)
        assert config.get("audio.test_value") == 42

        # Test default value
        assert config.get("nonexistent.key", "default") == "default"

    def test_config_reset(self, temp_config_dir):
        """Test resetting configuration."""
        config = GameConfig(config_dir=temp_config_dir)

        # Modify settings
        config.master_volume = 0.3
        config.set("debug.show_fps", True)

        # Reset all
        config.reset_to_defaults()
        assert config.master_volume == DEFAULT_MASTER_VOLUME
        assert not config.get("debug.show_fps")

    def test_config_reset_category(self, temp_config_dir):
        """Test resetting a specific category."""
        config = GameConfig(config_dir=temp_config_dir)

        # Modify settings in different categories
        config.master_volume = 0.3
        config.set("debug.show_fps", True)

        # Reset only audio
        config.reset_category("audio")
        assert config.master_volume == DEFAULT_MASTER_VOLUME
        assert config.get("debug.show_fps")  # Should remain unchanged

    def test_volume_clamping(self, temp_config_dir):
        """Test that volume values are clamped to 0.0-1.0."""
        config = GameConfig(config_dir=temp_config_dir)

        # Test clamping
        config.master_volume = 1.5
        assert config.master_volume == 1.0

        config.music_volume = -0.5
        assert config.music_volume == 0.0

    def test_is_modified_tracking(self, temp_config_dir):
        """Test modification tracking."""
        config = GameConfig(config_dir=temp_config_dir)

        assert not config.is_modified()

        config.fullscreen = True
        assert config.is_modified()

        config.save()
        assert not config.is_modified()


class TestEnvConfig:
    """Test environment variable configuration."""

    def test_get_env_with_defaults(self):
        """Test get_env function with defaults."""
        # Test non-existent env var returns default
        assert get_env("NONEXISTENT_VAR", "default") == "default"

        # Test type casting
        assert get_env("NONEXISTENT_VAR", 42, int) == 42
        assert get_env("NONEXISTENT_VAR", 3.14, float) == 3.14

    def test_get_env_bool_conversion(self, monkeypatch):
        """Test boolean conversion from env vars."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("anything_else", False),
        ]

        for value, expected in test_cases:
            monkeypatch.setenv("TEST_BOOL", value)
            assert get_env("TEST_BOOL", False, bool) == expected

    def test_load_env_config(self, monkeypatch):
        """Test loading configuration from environment."""
        # Set some env vars
        monkeypatch.setenv("DANGER_ROSE_DEBUG", "true")
        monkeypatch.setenv("DANGER_ROSE_FULLSCREEN", "true")
        monkeypatch.setenv("DANGER_ROSE_FPS_LIMIT", "120")
        monkeypatch.setenv("DANGER_ROSE_MASTER_VOLUME", "0.5")

        config = load_env_config()

        assert config["debug"]["enabled"]
        assert config["display"]["fullscreen"]
        assert config["performance"]["fps_limit"] == 120
        assert config["audio"]["master_volume"] == 0.5

        # Test that unset env vars are not included
        monkeypatch.delenv("DANGER_ROSE_FULLSCREEN")
        config2 = load_env_config()
        assert "fullscreen" not in config2.get("display", {})

    def test_is_development(self, monkeypatch):
        """Test development mode detection."""
        # Test default (production)
        monkeypatch.delenv("DANGER_ROSE_ENV", raising=False)
        assert not is_development()

        # Test development mode
        monkeypatch.setenv("DANGER_ROSE_ENV", "development")
        assert is_development()

        monkeypatch.setenv("DANGER_ROSE_ENV", "dev")
        assert is_development()

        monkeypatch.setenv("DANGER_ROSE_ENV", "production")
        assert not is_development()

    def test_is_debug(self, monkeypatch):
        """Test debug mode detection."""
        # Test default (no debug)
        monkeypatch.delenv("DANGER_ROSE_DEBUG", raising=False)
        monkeypatch.delenv("DEBUG", raising=False)
        assert not is_debug()

        # Test DANGER_ROSE_DEBUG
        monkeypatch.setenv("DANGER_ROSE_DEBUG", "true")
        assert is_debug()

        # Test generic DEBUG
        monkeypatch.delenv("DANGER_ROSE_DEBUG", raising=False)
        monkeypatch.setenv("DEBUG", "true")
        assert is_debug()


class TestConfigIntegration:
    """Test integration between GameConfig and environment variables."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_env_overrides_config(self, temp_config_dir, monkeypatch):
        """Test that environment variables override config file values."""
        # Set env vars
        monkeypatch.setenv("DANGER_ROSE_DEBUG", "true")
        monkeypatch.setenv("DANGER_ROSE_SHOW_FPS", "true")
        monkeypatch.setenv("DANGER_ROSE_FULLSCREEN", "true")

        # Create config
        config = GameConfig(config_dir=temp_config_dir)

        # Check that env vars overrode defaults
        assert config.get("debug.enabled")
        assert config.get("debug.show_fps")
        assert config.get("display.fullscreen")
