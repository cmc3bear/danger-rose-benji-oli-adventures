"""Generate placeholder audio files for testing."""

import math
import struct
import wave
from pathlib import Path


def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.3):
    """Generate a sine wave."""
    num_samples = int(sample_rate * duration)
    wave_data = []

    for i in range(num_samples):
        t = i / sample_rate
        value = amplitude * math.sin(frequency * 2 * math.pi * t)
        wave_data.append(value)

    return wave_data


def save_wav(filename, audio_data, sample_rate=44100):
    """Save audio data as WAV file."""
    with wave.open(str(filename), "w") as wav_file:
        # Configure WAV file
        nchannels = 1  # Mono
        sampwidth = 2  # 2 bytes per sample
        framerate = sample_rate
        nframes = len(audio_data)

        wav_file.setparams((nchannels, sampwidth, framerate, nframes, "NONE", "NONE"))

        # Convert float audio data to int16
        for sample in audio_data:
            int_sample = int(sample * 32767)
            # Clamp to int16 range
            int_sample = max(-32768, min(32767, int_sample))
            wav_file.writeframes(struct.pack("<h", int_sample))


def create_placeholder_music():
    """Create placeholder music tracks."""
    music_dir = Path("assets/audio/music")
    music_dir.mkdir(parents=True, exist_ok=True)

    # Title theme - calm, pleasant
    print("Creating title_theme.wav...")
    title_audio = generate_sine_wave(440, 3.0)  # A4 note, 3 seconds
    save_wav(music_dir / "title_theme.wav", title_audio)

    # Hub theme - homey feeling
    print("Creating hub_theme.wav...")
    hub_audio = generate_sine_wave(523.25, 3.0)  # C5 note, 3 seconds
    save_wav(music_dir / "hub_theme.wav", hub_audio)

    # Ski theme - energetic
    print("Creating ski_theme.wav...")
    ski_audio = generate_sine_wave(659.25, 3.0)  # E5 note, 3 seconds
    save_wav(music_dir / "ski_theme.wav", ski_audio)

    # Pool theme - playful
    print("Creating pool_theme.wav...")
    pool_audio = generate_sine_wave(587.33, 3.0)  # D5 note, 3 seconds
    save_wav(music_dir / "pool_theme.wav", pool_audio)

    # Vegas theme - exciting
    print("Creating vegas_theme.wav...")
    vegas_audio = generate_sine_wave(698.46, 3.0)  # F5 note, 3 seconds
    save_wav(music_dir / "vegas_theme.wav", vegas_audio)


def create_placeholder_sfx():
    """Create placeholder sound effects."""
    sfx_dir = Path("assets/audio/sfx")
    sfx_dir.mkdir(parents=True, exist_ok=True)

    # Menu select
    print("Creating menu_select.wav...")
    select_audio = generate_sine_wave(880, 0.1)  # A5 note, 0.1 seconds
    save_wav(sfx_dir / "menu_select.wav", select_audio)

    # Menu navigate
    print("Creating menu_navigate.wav...")
    nav_audio = generate_sine_wave(660, 0.05)  # E5 note, 0.05 seconds
    save_wav(sfx_dir / "menu_navigate.wav", nav_audio)

    # Door open
    print("Creating door_open.wav...")
    door_audio = generate_sine_wave(220, 0.3)  # A3 note, 0.3 seconds
    save_wav(sfx_dir / "door_open.wav", door_audio)

    # Collect item
    print("Creating collect_item.wav...")
    collect_audio = generate_sine_wave(1046.5, 0.2)  # C6 note, 0.2 seconds
    save_wav(sfx_dir / "collect_item.wav", collect_audio)

    # Player hurt
    print("Creating player_hurt.wav...")
    hurt_audio = generate_sine_wave(110, 0.2)  # A2 note, 0.2 seconds
    save_wav(sfx_dir / "player_hurt.wav", hurt_audio)

    # Victory
    print("Creating victory.wav...")
    # Create a simple victory fanfare (ascending notes)
    victory_audio = []
    victory_audio.extend(generate_sine_wave(523.25, 0.2))  # C5
    victory_audio.extend(generate_sine_wave(659.25, 0.2))  # E5
    victory_audio.extend(generate_sine_wave(783.99, 0.4))  # G5
    save_wav(sfx_dir / "victory.wav", victory_audio)

    # Jump
    print("Creating jump.wav...")
    jump_audio = generate_sine_wave(440, 0.15, amplitude=0.2)  # A4 note
    save_wav(sfx_dir / "jump.wav", jump_audio)

    # Splash (for pool game)
    print("Creating splash.wav...")
    splash_audio = generate_sine_wave(150, 0.3, amplitude=0.25)  # Low frequency
    save_wav(sfx_dir / "splash.wav", splash_audio)


def main():
    """Generate all placeholder audio files."""
    print("Generating placeholder audio files...")
    print("=" * 40)

    create_placeholder_music()
    print("\nMusic files created!")

    print("\n" + "=" * 40)

    create_placeholder_sfx()
    print("\nSound effect files created!")

    print("\n" + "=" * 40)
    print("All placeholder audio files generated successfully!")
    print("\nFiles created in:")
    print("  - assets/audio/music/")
    print("  - assets/audio/sfx/")


if __name__ == "__main__":
    main()
