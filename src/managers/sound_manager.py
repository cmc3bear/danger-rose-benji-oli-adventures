"""Centralized sound manager for music and sound effects."""

import os

import pygame

from src.config.constants import (
    AUDIO_FADE_TIME,
    DEFAULT_MASTER_VOLUME,
    DEFAULT_MUSIC_VOLUME,
    DEFAULT_SFX_VOLUME,
)


class SoundManager:
    """Singleton sound manager for handling all game audio."""

    _instance = None

    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the sound manager."""
        if hasattr(self, "_initialized"):
            return

        self._initialized = True

        # Initialize pygame mixer
        try:
            pygame.mixer.init(
                frequency=44100,  # CD quality
                size=-16,  # 16-bit signed samples
                channels=2,  # Stereo
                buffer=512,  # Lower buffer for less latency
            )
        except pygame.error as e:
            print(f"Warning: Could not initialize audio: {e}")
            # Continue without audio - useful for CI/testing environments

        # Volume settings
        self.master_volume = DEFAULT_MASTER_VOLUME
        self.music_volume = DEFAULT_MUSIC_VOLUME
        self.sfx_volume = DEFAULT_SFX_VOLUME

        # Track currently playing music
        self.current_music = None
        self.music_paused = False

        # Sound effect channels and cache
        self.sfx_channels = []
        self.sfx_cache: dict[str, pygame.mixer.Sound] = {}

        # Setup channels for sound effects
        self._setup_channels()

        # Apply initial volume settings
        self._apply_music_volume()

    def _setup_channels(self):
        """Setup dedicated channels for sound effects."""
        if not pygame.mixer.get_init():
            return

        # Reserve channels 0-7 for sound effects
        pygame.mixer.set_reserved(8)

        # Create channel objects
        for i in range(8):
            self.sfx_channels.append(pygame.mixer.Channel(i))

    def _apply_music_volume(self):
        """Apply the current music volume setting."""
        if not pygame.mixer.get_init():
            return
        effective_volume = self.master_volume * self.music_volume
        pygame.mixer.music.set_volume(effective_volume)

    def _apply_sfx_volume(self, sound: pygame.mixer.Sound) -> pygame.mixer.Sound:
        """Apply volume to a sound effect."""
        effective_volume = self.master_volume * self.sfx_volume
        sound.set_volume(effective_volume)
        return sound

    def play_music(self, music_file: str, loops: int = -1, fade_ms: int = 0):
        """Play background music.

        Args:
            music_file: Path to the music file
            loops: Number of loops (-1 for infinite)
            fade_ms: Fade in duration in milliseconds
        """
        print(f"[SoundManager] play_music called with: {music_file}")
        
        # Check if mixer is initialized
        if not pygame.mixer.get_init():
            print("[SoundManager] Mixer not initialized!")
            return

        try:
            # Check if file exists
            if not os.path.exists(music_file):
                print(f"[SoundManager] Warning: Music file not found: {music_file}")
                return
            else:
                print(f"[SoundManager] Music file exists: {music_file}")

            # Stop current music if playing
            if self.current_music:
                self.stop_music(fade_ms=AUDIO_FADE_TIME)

            # Load and play new music
            pygame.mixer.music.load(music_file)
            print(f"[SoundManager] Music loaded successfully")

            # Set volume before playing
            effective_volume = self.master_volume * self.music_volume
            pygame.mixer.music.set_volume(effective_volume)
            print(f"[SoundManager] Set volume to: {effective_volume} (master: {self.master_volume}, music: {self.music_volume})")

            if fade_ms > 0:
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
                print(f"[SoundManager] Started music with fade-in: {fade_ms}ms")
            else:
                pygame.mixer.music.play(loops)
                print(f"[SoundManager] Started music immediately")

            self.current_music = music_file
            self.music_paused = False
            
            # Verify it's playing
            import time
            time.sleep(0.1)
            if pygame.mixer.music.get_busy():
                print(f"[SoundManager] Music is playing!")
            else:
                print(f"[SoundManager] WARNING: Music is NOT playing!")

        except pygame.error as e:
            print(f"Error playing music {music_file}: {e}")

    def stop_music(self, fade_ms: int = 0):
        """Stop the currently playing music.

        Args:
            fade_ms: Fade out duration in milliseconds
        """
        if not pygame.mixer.get_init():
            return

        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()

        self.current_music = None
        self.music_paused = False

    def pause_music(self):
        """Pause the currently playing music."""
        if not pygame.mixer.get_init():
            return
        if self.current_music and not self.music_paused:
            pygame.mixer.music.pause()
            self.music_paused = True

    def unpause_music(self):
        """Unpause the music."""
        if not pygame.mixer.get_init():
            return
        if self.current_music and self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False

    def crossfade_music(self, new_music: str, duration_ms: int = 1000):
        """Crossfade from current music to new music.

        Args:
            new_music: Path to the new music file
            duration_ms: Duration of the crossfade
        """
        # Fade out current music
        if self.current_music:
            self.stop_music(fade_ms=duration_ms // 2)

        # Wait a moment then fade in new music
        # Note: In a real implementation, this would use a timer
        pygame.time.wait(duration_ms // 2)
        self.play_music(new_music, fade_ms=duration_ms // 2)

    def play_sfx(
        self, sound_file: str, loops: int = 0, maxtime: int = 0
    ) -> pygame.mixer.Channel | None:
        """Play a sound effect.

        Args:
            sound_file: Path to the sound file
            loops: Number of extra loops (0 for play once)
            maxtime: Maximum time to play in milliseconds (0 for full)

        Returns:
            Channel the sound is playing on, or None if failed
        """
        if not pygame.mixer.get_init():
            return None

        try:
            # Check cache first
            if sound_file not in self.sfx_cache:
                # Check if file exists
                if not os.path.exists(sound_file):
                    print(f"Warning: Sound file not found: {sound_file}")
                    return None

                # Load and cache the sound
                sound = pygame.mixer.Sound(sound_file)
                self.sfx_cache[sound_file] = sound
            else:
                sound = self.sfx_cache[sound_file]

            # Apply volume
            sound = self._apply_sfx_volume(sound)

            # Find available channel
            channel = pygame.mixer.find_channel()
            if channel is None:
                # Force use first channel if all busy
                channel = self.sfx_channels[0]

            # Play the sound
            channel.play(sound, loops=loops, maxtime=maxtime)
            return channel

        except pygame.error as e:
            print(f"Error playing sound {sound_file}: {e}")
            return None

    def stop_sfx(self, channel: pygame.mixer.Channel | None = None):
        """Stop sound effects.

        Args:
            channel: Specific channel to stop, or None to stop all
        """
        if channel:
            channel.stop()
        else:
            # Stop all SFX channels
            for ch in self.sfx_channels:
                ch.stop()

    def duck_audio(self, duck_level: float = 0.3, duration_ms: int = 500):
        """Temporarily lower audio volume for important sounds.

        Args:
            duck_level: Volume multiplier during duck (0.0-1.0)
            duration_ms: How long to maintain ducked volume
        """
        if not pygame.mixer.get_init():
            return

        # Store original volumes
        original_music = pygame.mixer.music.get_volume()

        # Duck the audio
        pygame.mixer.music.set_volume(original_music * duck_level)

        # Note: In real implementation, use a timer to restore
        # For now, caller must call restore_audio_levels()

    def restore_audio_levels(self):
        """Restore audio levels after ducking."""
        self._apply_music_volume()

    def set_master_volume(self, volume: float):
        """Set master volume (0.0-1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
        self._apply_music_volume()

        # Update all cached sounds
        for sound in self.sfx_cache.values():
            self._apply_sfx_volume(sound)

    def set_music_volume(self, volume: float):
        """Set music volume (0.0-1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        self._apply_music_volume()

    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0-1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))

        # Update all cached sounds
        for sound in self.sfx_cache.values():
            self._apply_sfx_volume(sound)

    def get_volumes(self) -> dict[str, float]:
        """Get current volume settings."""
        return {
            "master": self.master_volume,
            "music": self.music_volume,
            "sfx": self.sfx_volume,
        }

    def preload_sound(self, sound_file: str):
        """Preload a sound effect into cache.

        Args:
            sound_file: Path to the sound file
        """
        if sound_file not in self.sfx_cache and os.path.exists(sound_file):
            try:
                sound = pygame.mixer.Sound(sound_file)
                self.sfx_cache[sound_file] = sound
            except pygame.error as e:
                print(f"Error preloading sound {sound_file}: {e}")

    def clear_cache(self):
        """Clear the sound effect cache."""
        self.sfx_cache.clear()

    def shutdown(self):
        """Shutdown the sound system cleanly."""
        self.stop_music()
        self.stop_sfx()
        self.clear_cache()
        pygame.mixer.quit()
