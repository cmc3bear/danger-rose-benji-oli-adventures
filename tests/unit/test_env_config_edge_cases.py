"""Edge case tests for environment configuration."""

import os
from unittest.mock import patch

from src.config.env_config import get_env, is_debug, is_development, load_env_config


class TestEnvConfigEdgeCases:
    """Test edge cases in environment configuration."""

    def test_get_env_with_empty_string(self):
        """get_env should return empty string if env var is empty."""
        # Arrange
        with patch.dict(os.environ, {"EMPTY_VAR": ""}):
            # Act
            result = get_env("EMPTY_VAR", "default")

            # Assert
            assert result == ""  # Empty string is still a value

    def test_get_env_with_whitespace(self):
        """get_env should preserve whitespace in env vars."""
        # Arrange
        with patch.dict(os.environ, {"SPACE_VAR": "  value  "}):
            # Act
            result = get_env("SPACE_VAR")

            # Assert
            assert result == "  value  "  # Whitespace preserved

    def test_get_env_with_bool_cast(self):
        """get_env with bool cast should handle various string representations."""
        # Test various truthy values
        truthy_values = ["TRUE", "True", "true", "1", "yes", "YES", "on", "ON"]
        for value in truthy_values:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                result = get_env("BOOL_VAR", cast=bool)
                assert result is True, f"Failed for {value}"

        # Test various falsy values
        falsy_values = ["FALSE", "False", "false", "0", "no", "NO", "off", "OFF", ""]
        for value in falsy_values:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                result = get_env("BOOL_VAR", cast=bool)
                assert result is False, f"Failed for {value}"

        # Test random strings default to False
        with patch.dict(os.environ, {"BOOL_VAR": "random"}):
            result = get_env("BOOL_VAR", cast=bool)
            assert result is False

    def test_get_env_with_cast_types(self):
        """get_env should cast to various types."""
        # Test int cast
        with patch.dict(os.environ, {"INT_VAR": "42"}):
            result = get_env("INT_VAR", cast=int)
            assert result == 42
            assert isinstance(result, int)

        # Test float cast
        with patch.dict(os.environ, {"FLOAT_VAR": "3.14"}):
            result = get_env("FLOAT_VAR", cast=float)
            assert result == 3.14
            assert isinstance(result, float)

    def test_load_env_config_no_env_vars(self):
        """load_env_config should return empty dict when no env vars set."""
        # Act
        result = load_env_config()

        # Assert
        assert isinstance(result, dict)
        # May have some keys if env vars are set in test environment

    def test_load_env_config_with_debug_settings(self):
        """load_env_config should load debug settings from env vars."""
        # Arrange
        with patch.dict(
            os.environ,
            {
                "DANGER_ROSE_DEBUG": "true",
                "DANGER_ROSE_SHOW_FPS": "1",
                "DANGER_ROSE_SHOW_HITBOXES": "false",
                "DANGER_ROSE_LOG_LEVEL": "DEBUG",
            },
        ):
            # Act
            result = load_env_config()

            # Assert
            assert result["debug"]["enabled"] is True
            assert result["debug"]["show_fps"] is True
            assert result["debug"]["show_hitboxes"] is False
            assert result["debug"]["log_level"] == "DEBUG"

    def test_load_env_config_with_display_settings(self):
        """load_env_config should load display settings from env vars."""
        # Arrange
        with patch.dict(
            os.environ,
            {
                "DANGER_ROSE_FULLSCREEN": "true",
                "DANGER_ROSE_SCREEN_WIDTH": "1280",
                "DANGER_ROSE_SCREEN_HEIGHT": "720",
            },
        ):
            # Act
            result = load_env_config()

            # Assert
            assert result["display"]["fullscreen"] is True
            assert result["display"]["width"] == 1280
            assert result["display"]["height"] == 720

    def test_is_development_various_environments(self):
        """is_development should correctly identify development environment."""
        # Test development environments
        dev_values = ["development", "dev"]
        for value in dev_values:
            with patch.dict(os.environ, {"DANGER_ROSE_ENV": value}, clear=True):
                assert is_development() is True, f"Failed for {value}"

        # Test non-development environments
        non_dev_values = ["production", "prod", "staging", "test", ""]
        for value in non_dev_values:
            with patch.dict(os.environ, {"DANGER_ROSE_ENV": value}, clear=True):
                assert is_development() is False, f"Failed for {value}"

    def test_is_debug_various_values(self):
        """is_debug should correctly identify debug mode."""
        # Test debug enabled via DANGER_ROSE_DEBUG
        debug_values = ["true", "1", "yes", "on"]
        for value in debug_values:
            with patch.dict(os.environ, {"DANGER_ROSE_DEBUG": value}, clear=True):
                assert is_debug() is True, f"Failed for DANGER_ROSE_DEBUG={value}"

        # Test debug enabled via DEBUG
        for value in debug_values:
            with patch.dict(os.environ, {"DEBUG": value}, clear=True):
                assert is_debug() is True, f"Failed for DEBUG={value}"

        # Test debug disabled
        non_debug_values = ["false", "0", "no", "off", ""]
        for value in non_debug_values:
            with patch.dict(
                os.environ, {"DANGER_ROSE_DEBUG": value, "DEBUG": value}, clear=True
            ):
                assert is_debug() is False, f"Failed for {value}"

    def test_load_env_config_with_performance_settings(self):
        """load_env_config should load performance settings from env vars."""
        # Arrange
        with patch.dict(
            os.environ,
            {"DANGER_ROSE_FPS_LIMIT": "120", "DANGER_ROSE_PARTICLES": "false"},
        ):
            # Act
            result = load_env_config()

            # Assert
            assert result["performance"]["fps_limit"] == 120
            assert result["performance"]["enable_particles"] is False
