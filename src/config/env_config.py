"""Environment variable configuration support for Danger Rose.

This module provides utilities for loading configuration from environment
variables, supporting both development and production environments.
"""

import os
from typing import Any


def get_env(key: str, default: Any = None, cast: type | None = None) -> Any:
    """Get an environment variable with optional type casting.

    Args:
        key: Environment variable name.
        default: Default value if not found.
        cast: Type to cast the value to (e.g., int, float, bool).

    Returns:
        Environment variable value or default.
    """
    value = os.getenv(key)

    if value is None:
        return default

    if cast is None:
        return value

    # Handle common type conversions
    if cast is bool:
        return value.lower() in ("true", "1", "yes", "on")

    try:
        return cast(value)
    except (ValueError, TypeError):
        return default


def load_env_config() -> dict:
    """Load configuration from environment variables.

    This function checks for common game environment variables
    and returns a configuration dictionary.

    Returns:
        Dictionary with environment-based configuration.
    """
    config = {}

    # Debug settings from environment
    debug_settings = {}
    if os.getenv("DANGER_ROSE_DEBUG") is not None:
        debug_settings["enabled"] = get_env("DANGER_ROSE_DEBUG", False, bool)
    if os.getenv("DANGER_ROSE_SHOW_FPS") is not None:
        debug_settings["show_fps"] = get_env("DANGER_ROSE_SHOW_FPS", False, bool)
    if os.getenv("DANGER_ROSE_SHOW_HITBOXES") is not None:
        debug_settings["show_hitboxes"] = get_env(
            "DANGER_ROSE_SHOW_HITBOXES", False, bool
        )
    if os.getenv("DANGER_ROSE_LOG_LEVEL") is not None:
        debug_settings["log_level"] = get_env("DANGER_ROSE_LOG_LEVEL", "INFO")

    if debug_settings:
        config["debug"] = debug_settings

    # Display settings
    display_settings = {}
    if os.getenv("DANGER_ROSE_FULLSCREEN") is not None:
        display_settings["fullscreen"] = get_env("DANGER_ROSE_FULLSCREEN", False, bool)
    if os.getenv("DANGER_ROSE_SCREEN_WIDTH") is not None:
        display_settings["width"] = get_env("DANGER_ROSE_SCREEN_WIDTH", 1920, int)
    if os.getenv("DANGER_ROSE_SCREEN_HEIGHT") is not None:
        display_settings["height"] = get_env("DANGER_ROSE_SCREEN_HEIGHT", 1080, int)

    if display_settings:
        config["display"] = display_settings

    # Audio settings
    audio_settings = {}
    if os.getenv("DANGER_ROSE_AUDIO_ENABLED") is not None:
        audio_settings["enabled"] = get_env("DANGER_ROSE_AUDIO_ENABLED", True, bool)
    if os.getenv("DANGER_ROSE_MASTER_VOLUME") is not None:
        audio_settings["master_volume"] = get_env(
            "DANGER_ROSE_MASTER_VOLUME", 0.7, float
        )

    if audio_settings:
        config["audio"] = audio_settings

    # Development settings
    dev_settings = {}
    if os.getenv("DANGER_ROSE_SKIP_INTRO") is not None:
        dev_settings["skip_intro"] = get_env("DANGER_ROSE_SKIP_INTRO", False, bool)
    if os.getenv("DANGER_ROSE_START_SCENE") is not None:
        dev_settings["start_scene"] = get_env("DANGER_ROSE_START_SCENE", "title")
    if os.getenv("DANGER_ROSE_UNLIMITED_LIVES") is not None:
        dev_settings["unlimited_lives"] = get_env(
            "DANGER_ROSE_UNLIMITED_LIVES", False, bool
        )

    if dev_settings:
        config["dev"] = dev_settings

    # Performance settings
    performance_settings = {}
    if os.getenv("DANGER_ROSE_FPS_LIMIT") is not None:
        performance_settings["fps_limit"] = get_env("DANGER_ROSE_FPS_LIMIT", 60, int)
    if os.getenv("DANGER_ROSE_PARTICLES") is not None:
        performance_settings["enable_particles"] = get_env(
            "DANGER_ROSE_PARTICLES", True, bool
        )

    if performance_settings:
        config["performance"] = performance_settings

    return config


def is_development() -> bool:
    """Check if running in development mode.

    Returns:
        True if in development mode, False otherwise.
    """
    return get_env("DANGER_ROSE_ENV", "production").lower() in ("development", "dev")


def is_debug() -> bool:
    """Check if debug mode is enabled.

    Returns:
        True if debug mode is enabled, False otherwise.
    """
    return get_env("DANGER_ROSE_DEBUG", False, bool) or get_env("DEBUG", False, bool)
