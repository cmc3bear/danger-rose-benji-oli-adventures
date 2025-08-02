"""Game configuration management for Danger Rose.

This module provides the GameConfig class for managing game settings,
including loading/saving preferences and handling runtime configuration.
"""

import json
from pathlib import Path
from typing import Any

from .constants import (
    CONFIG_FILE,
    DEBUG_SHOW_FPS,
    DEBUG_SHOW_GRID,
    DEBUG_SHOW_HITBOXES,
    DEFAULT_MASTER_VOLUME,
    DEFAULT_MUSIC_VOLUME,
    DEFAULT_SFX_VOLUME,
    FULLSCREEN_DEFAULT,
)
from .env_config import load_env_config


class GameConfig:
    """Manages game configuration and user preferences.

    This class handles loading, saving, and accessing game settings.
    It provides default values and ensures settings persistence across sessions.
    """

    def __init__(self, config_dir: Path | None = None):
        """Initialize GameConfig with optional custom config directory.

        Args:
            config_dir: Directory to store config files. Defaults to user's home.
        """
        if config_dir is None:
            # Use user's home directory for cross-platform compatibility
            config_dir = Path.home() / ".danger_rose"

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / CONFIG_FILE

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load settings or use defaults
        self._settings = self._load_settings()

        # Track if settings have been modified
        self._modified = False

        # Apply environment variable overrides (after resetting modified flag)
        self._apply_env_overrides()

    def _get_default_settings(self) -> dict[str, Any]:
        """Return default game settings.

        Returns:
            Dictionary containing all default settings.
        """
        return {
            # Display settings
            "display": {
                "fullscreen": FULLSCREEN_DEFAULT,
                "vsync": True,
                "show_fps": False,
            },
            # Audio settings
            "audio": {
                "master_volume": DEFAULT_MASTER_VOLUME,
                "music_volume": DEFAULT_MUSIC_VOLUME,
                "sfx_volume": DEFAULT_SFX_VOLUME,
                "mute": False,
            },
            # Controls (keyboard mappings)
            "controls": {
                "player1": {
                    "up": "w",
                    "down": "s",
                    "left": "a",
                    "right": "d",
                    "jump": "space",
                    "attack": "j",
                },
                "player2": {
                    "up": "up",
                    "down": "down",
                    "left": "left",
                    "right": "right",
                    "jump": "return",
                    "attack": "rctrl",
                },
            },
            # Gameplay settings
            "gameplay": {
                "difficulty": "normal",
                "auto_save": True,
                "show_hints": True,
            },
            # Debug settings
            "debug": {
                "show_fps": DEBUG_SHOW_FPS,
                "show_hitboxes": DEBUG_SHOW_HITBOXES,
                "show_grid": DEBUG_SHOW_GRID,
                "enable_cheats": False,
            },
            # Accessibility settings
            "accessibility": {
                "colorblind_mode": "off",  # off, protanopia, deuteranopia, tritanopia
                "screen_shake": True,
                "flashing_effects": True,
                "subtitle_size": "medium",  # small, medium, large
            },
        }

    def _load_settings(self) -> dict[str, Any]:
        """Load settings from file or return defaults.

        Returns:
            Dictionary containing loaded or default settings.
        """
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    loaded_settings = json.load(f)

                # Merge with defaults to handle missing keys
                default_settings = self._get_default_settings()
                return self._deep_merge(default_settings, loaded_settings)

            except (OSError, json.JSONDecodeError) as e:
                print(f"Error loading settings: {e}")
                print("Using default settings instead.")

        return self._get_default_settings()

    def _deep_merge(
        self, base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        """Deep merge two dictionaries, with override taking precedence.

        Args:
            base: Base dictionary with default values.
            override: Dictionary with values to override.

        Returns:
            Merged dictionary.
        """
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to settings."""
        env_config = load_env_config()

        # Save current modified state
        was_modified = self._modified

        # Apply debug overrides
        if "debug" in env_config:
            for key, value in env_config["debug"].items():
                if value is not None:
                    self.set(f"debug.{key}", value)

        # Apply display overrides
        if "display" in env_config:
            for key, value in env_config["display"].items():
                if value is not None:
                    self.set(f"display.{key}", value)

        # Apply audio overrides
        if "audio" in env_config:
            for key, value in env_config["audio"].items():
                if value is not None:
                    self.set(f"audio.{key}", value)

        # Restore modified state (env overrides shouldn't mark as modified)
        self._modified = was_modified

    def save(self) -> bool:
        """Save current settings to file.

        Returns:
            True if save successful, False otherwise.
        """
        try:
            with open(self.config_file, "w") as f:
                json.dump(self._settings, f, indent=2, sort_keys=True)
            self._modified = False
            return True

        except OSError as e:
            print(f"Error saving settings: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a setting value using dot notation.

        Args:
            key_path: Dot-separated path to setting (e.g., "audio.master_volume").
            default: Default value if key not found.

        Returns:
            Setting value or default.
        """
        keys = key_path.split(".")
        value = self._settings

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set a setting value using dot notation.

        Args:
            key_path: Dot-separated path to setting (e.g., "audio.master_volume").
            value: Value to set.
        """
        keys = key_path.split(".")
        target = self._settings

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        # Set the value
        target[keys[-1]] = value
        self._modified = True

    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        self._settings = self._get_default_settings()
        self._modified = True

    def reset_category(self, category: str) -> None:
        """Reset a specific category to default values.

        Args:
            category: Category name (e.g., "audio", "controls").
        """
        defaults = self._get_default_settings()
        if category in defaults:
            self._settings[category] = defaults[category]
            self._modified = True

    def is_modified(self) -> bool:
        """Check if settings have been modified since last save.

        Returns:
            True if modified, False otherwise.
        """
        return self._modified

    def get_all_settings(self) -> dict[str, Any]:
        """Get a copy of all settings.

        Returns:
            Dictionary containing all current settings.
        """
        return self._settings.copy()

    # Convenience properties for common settings
    @property
    def fullscreen(self) -> bool:
        """Get fullscreen setting."""
        return self.get("display.fullscreen", FULLSCREEN_DEFAULT)

    @fullscreen.setter
    def fullscreen(self, value: bool) -> None:
        """Set fullscreen setting."""
        self.set("display.fullscreen", value)

    @property
    def master_volume(self) -> float:
        """Get master volume setting."""
        return self.get("audio.master_volume", DEFAULT_MASTER_VOLUME)

    @master_volume.setter
    def master_volume(self, value: float) -> None:
        """Set master volume setting."""
        self.set("audio.master_volume", max(0.0, min(1.0, value)))

    @property
    def music_volume(self) -> float:
        """Get music volume setting."""
        return self.get("audio.music_volume", DEFAULT_MUSIC_VOLUME)

    @music_volume.setter
    def music_volume(self, value: float) -> None:
        """Set music volume setting."""
        self.set("audio.music_volume", max(0.0, min(1.0, value)))

    @property
    def sfx_volume(self) -> float:
        """Get SFX volume setting."""
        return self.get("audio.sfx_volume", DEFAULT_SFX_VOLUME)

    @sfx_volume.setter
    def sfx_volume(self, value: float) -> None:
        """Set SFX volume setting."""
        self.set("audio.sfx_volume", max(0.0, min(1.0, value)))

    @property
    def show_fps(self) -> bool:
        """Get show FPS debug setting."""
        return self.get("debug.show_fps", DEBUG_SHOW_FPS)

    @show_fps.setter
    def show_fps(self, value: bool) -> None:
        """Set show FPS debug setting."""
        self.set("debug.show_fps", value)


# Global config instance
_config_instance: GameConfig | None = None


def get_config() -> GameConfig:
    """Get the global GameConfig instance.

    Returns:
        The global GameConfig instance.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = GameConfig()
    return _config_instance
