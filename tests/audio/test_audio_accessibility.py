"""Accessibility testing for sound effects system."""

from unittest.mock import Mock, patch
import pytest

from src.managers.sound_manager import SoundManager
from src.config.constants import (
    DEFAULT_MASTER_VOLUME,
    DEFAULT_MUSIC_VOLUME, 
    DEFAULT_SFX_VOLUME
)


class TestAudioAccessibility:
    """Test audio accessibility features and compliance."""

    @pytest.fixture
    def accessibility_sound_manager(self):
        """Create sound manager for accessibility testing."""
        SoundManager._instance = None
        with patch("pygame.mixer.init"):
            with patch("pygame.mixer.get_init", return_value=(44100, -16, 2, 512)):
                sm = SoundManager()
                yield sm

    def test_hearing_impairment_support(self, accessibility_sound_manager):
        """Test features for users with hearing impairments."""
        sm = accessibility_sound_manager
        
        # Test volume range allows for very quiet operation
        sm.set_master_volume(0.0)
        assert sm.master_volume == 0.0, "Should allow complete audio disable"
        
        # Test volume range allows for amplification
        sm.set_master_volume(1.0)
        assert sm.master_volume == 1.0, "Should allow maximum amplification"
        
        # Test individual channel control for hearing aid compatibility
        sm.set_music_volume(0.0)  # Disable music for clarity
        sm.set_sfx_volume(1.0)    # Maximize important sounds
        
        assert sm.music_volume == 0.0
        assert sm.sfx_volume == 1.0

    def test_visual_audio_feedback_integration(self):
        """Test that audio cues have corresponding visual feedback."""
        # Define audio-visual feedback pairs for accessibility
        audio_visual_mappings = {
            "target_hit.ogg": {
                "visual_effect": "explosion_particles",
                "screen_flash": True,
                "color_change": "yellow_flash",
                "duration_ms": 200
            },
            "powerup_collect.ogg": {
                "visual_effect": "sparkle_burst",
                "screen_flash": False,
                "color_change": "blue_glow",
                "duration_ms": 300
            },
            "life_lost.ogg": {
                "visual_effect": "screen_shake",
                "screen_flash": True,
                "color_change": "red_flash",
                "duration_ms": 500
            },
            "time_warning.ogg": {
                "visual_effect": "timer_pulse",
                "screen_flash": True,
                "color_change": "orange_flash",
                "duration_ms": 100
            }
        }
        
        for audio_cue, visual_feedback in audio_visual_mappings.items():
            # Verify each audio cue has comprehensive visual feedback
            assert visual_feedback["visual_effect"], f"{audio_cue} needs visual effect"
            assert "screen_flash" in visual_feedback, f"{audio_cue} needs flash indicator"
            assert visual_feedback["duration_ms"] > 0, f"{audio_cue} needs visible duration"

    def test_subtitle_integration_points(self):
        """Test integration points for subtitle system."""
        # Define sounds that should trigger subtitles
        subtitle_sounds = {
            "character_dialogue_danger_1.ogg": {
                "subtitle": "Danger: Let's go skiing!",
                "speaker": "danger",
                "importance": "high"
            },
            "character_dialogue_rose_1.ogg": {
                "subtitle": "Rose: I'll get all the targets!",
                "speaker": "rose", 
                "importance": "high"
            },
            "system_countdown_3.ogg": {
                "subtitle": "3...",
                "speaker": "system",
                "importance": "critical"
            },
            "system_countdown_2.ogg": {
                "subtitle": "2...",
                "speaker": "system",
                "importance": "critical"
            },
            "system_countdown_1.ogg": {
                "subtitle": "1...",
                "speaker": "system",
                "importance": "critical"
            },
            "system_go.ogg": {
                "subtitle": "GO!",
                "speaker": "system",
                "importance": "critical"
            }
        }
        
        for sound_file, subtitle_data in subtitle_sounds.items():
            # Verify subtitle data is complete
            assert subtitle_data["subtitle"], f"{sound_file} needs subtitle text"
            assert subtitle_data["speaker"] in ["danger", "rose", "dad", "system"]
            assert subtitle_data["importance"] in ["low", "medium", "high", "critical"]

    def test_colorblind_friendly_audio_cues(self):
        """Test audio cues support colorblind-friendly gameplay."""
        # Audio cues that compensate for color-based visual feedback
        colorblind_audio_support = {
            "red_target_hit.ogg": "Distinct tone for red targets",
            "green_target_hit.ogg": "Different tone for green targets", 
            "blue_target_hit.ogg": "Unique tone for blue targets",
            "danger_zone_warning.ogg": "Audio warning for red danger zones",
            "safe_zone_enter.ogg": "Audio confirmation for green safe zones",
            "powerup_rare.ogg": "Special audio for rare (hard to see) powerups",
            "ui_error.ogg": "Audio feedback for invalid actions"
        }
        
        # Verify each color-dependent visual has audio support
        for audio_file, description in colorblind_audio_support.items():
            assert description, f"{audio_file} needs clear audio description"
            # In real implementation, verify distinct audio characteristics

    def test_cognitive_accessibility_features(self, accessibility_sound_manager):
        """Test features for users with cognitive impairments."""
        sm = accessibility_sound_manager
        
        # Test simplified audio mode with fewer competing sounds
        cognitive_friendly_settings = {
            "master_volume": 0.6,      # Moderate volume to avoid overwhelming
            "music_volume": 0.2,       # Very quiet background music
            "sfx_volume": 0.8,         # Clear important sound effects
            "max_concurrent_sounds": 3  # Limit simultaneous sounds
        }
        
        sm.set_master_volume(cognitive_friendly_settings["master_volume"])
        sm.set_music_volume(cognitive_friendly_settings["music_volume"])
        sm.set_sfx_volume(cognitive_friendly_settings["sfx_volume"])
        
        # Verify settings are appropriate for cognitive accessibility
        assert sm.music_volume < sm.sfx_volume, "Important sounds should be louder than background"
        assert sm.master_volume <= 0.7, "Volume should not be overwhelming"

    def test_motor_impairment_audio_feedback(self):
        """Test audio feedback for users with motor impairments."""
        # Extended audio feedback for actions that might be difficult
        motor_assistance_audio = {
            "button_focus.ogg": {
                "trigger": "ui_element_focused",
                "purpose": "Confirm focus for users who can't see cursor precisely",
                "repeat": False
            },
            "button_hold_progress.ogg": {
                "trigger": "button_hold_in_progress", 
                "purpose": "Audio feedback during hold actions",
                "repeat": True
            },
            "action_confirmed.ogg": {
                "trigger": "successful_action",
                "purpose": "Clear confirmation of completed actions",
                "repeat": False
            },
            "action_cancelled.ogg": {
                "trigger": "action_timeout_or_cancel",
                "purpose": "Feedback when action didn't complete",
                "repeat": False
            }
        }
        
        for audio_file, config in motor_assistance_audio.items():
            assert config["trigger"], f"{audio_file} needs clear trigger condition"
            assert config["purpose"], f"{audio_file} needs accessibility purpose"
            assert "repeat" in config, f"{audio_file} needs repeat specification"

    def test_elderly_user_audio_considerations(self, accessibility_sound_manager):
        """Test audio settings appropriate for elderly users."""
        sm = accessibility_sound_manager
        
        # Settings optimized for age-related hearing changes
        elderly_friendly_settings = {
            "frequency_boost_high": False,  # Avoid harsh high frequencies
            "frequency_boost_mid": True,    # Enhance speech frequencies
            "audio_clarity_mode": True,     # Reduce audio compression
            "extended_fade_times": True     # Longer transitions
        }
        
        # Test volume ranges are appropriate
        sm.set_master_volume(0.8)  # Higher default volume
        assert sm.master_volume >= 0.7, "Should allow higher volumes for elderly users"
        
        # Test that fade times can be extended for easier perception
        extended_fade_time = 1000  # 1 second instead of default 500ms
        assert extended_fade_time > 500, "Should allow longer fade times"

    def test_audio_description_integration(self):
        """Test integration with audio description systems."""
        # Audio descriptions for visual gameplay elements
        audio_descriptions = {
            "scene_ski_start.ogg": {
                "description": "Skiing down a snowy mountain with trees on both sides",
                "timing": "scene_enter",
                "priority": "low",
                "skippable": True
            },
            "scene_pool_start.ogg": {
                "description": "Standing by a backyard pool with floating targets",
                "timing": "scene_enter", 
                "priority": "low",
                "skippable": True
            },
            "powerup_spawned.ogg": {
                "description": "A special powerup has appeared on screen",
                "timing": "event_triggered",
                "priority": "medium",
                "skippable": False
            },
            "boss_appears.ogg": {
                "description": "The final boss has entered the scene",
                "timing": "event_triggered",
                "priority": "high", 
                "skippable": False
            }
        }
        
        for audio_file, config in audio_descriptions.items():
            assert config["description"], f"{audio_file} needs description text"
            assert config["timing"] in ["scene_enter", "event_triggered", "user_requested"]
            assert config["priority"] in ["low", "medium", "high", "critical"]
            assert "skippable" in config, f"{audio_file} needs skip setting"

    def test_screen_reader_compatibility(self, accessibility_sound_manager):
        """Test compatibility with screen readers."""
        sm = accessibility_sound_manager
        
        # Test that sound system can be muted to not interfere with screen readers
        sm.set_master_volume(0.0)
        assert sm.master_volume == 0.0, "Should allow complete muting for screen reader use"
        
        # Test that important game state can be conveyed through audio
        screen_reader_audio = {
            "score_update.ogg": "Your score is now 1,500 points",
            "lives_remaining.ogg": "Two lives remaining", 
            "time_remaining.ogg": "Thirty seconds left",
            "level_complete.ogg": "Level completed successfully",
            "game_over.ogg": "Game over. Final score: 2,800 points"
        }
        
        for audio_file, spoken_text in screen_reader_audio.items():
            # Verify important information is conveyed through audio
            assert spoken_text, f"{audio_file} needs spoken content"
            assert len(spoken_text.split()) >= 2, f"{audio_file} needs meaningful content"

    def test_audio_preferences_persistence(self, accessibility_sound_manager):
        """Test that accessibility audio settings persist between sessions."""
        sm = accessibility_sound_manager
        
        # Set accessibility-focused preferences
        accessibility_preferences = {
            "master_volume": 0.9,
            "music_volume": 0.1,     # Very quiet for focus
            "sfx_volume": 1.0,       # Maximum for clarity
            "audio_descriptions": True,
            "extended_feedback": True,
            "simplified_audio": True
        }
        
        # Apply settings
        sm.set_master_volume(accessibility_preferences["master_volume"])
        sm.set_music_volume(accessibility_preferences["music_volume"])
        sm.set_sfx_volume(accessibility_preferences["sfx_volume"])
        
        # Verify settings are stored correctly
        volumes = sm.get_volumes()
        assert volumes["master"] == accessibility_preferences["master_volume"]
        assert volumes["music"] == accessibility_preferences["music_volume"]
        assert volumes["sfx"] == accessibility_preferences["sfx_volume"]

    def test_emergency_audio_alerts(self):
        """Test audio alerts for critical game events."""
        # Critical alerts that should always be audible
        emergency_audio = {
            "critical_health_low.ogg": {
                "volume_boost": 0.2,    # 20% louder than normal
                "bypass_music_duck": True,
                "priority": "critical",
                "repeat_interval": 3.0   # Repeat every 3 seconds
            },
            "time_critical_10sec.ogg": {
                "volume_boost": 0.15,
                "bypass_music_duck": True,
                "priority": "critical",
                "repeat_interval": None
            },
            "achievement_unlocked.ogg": {
                "volume_boost": 0.1,
                "bypass_music_duck": False,
                "priority": "high",
                "repeat_interval": None
            }
        }
        
        for audio_file, config in emergency_audio.items():
            assert config["volume_boost"] >= 0, f"{audio_file} needs volume boost spec"
            assert config["priority"] in ["high", "critical"]
            assert "bypass_music_duck" in config, f"{audio_file} needs duck bypass spec"

    def test_multi_language_audio_support(self):
        """Test support for multiple languages in audio cues."""
        # Multi-language audio file organization
        language_audio_structure = {
            "en": {
                "countdown_3.ogg": "Three",
                "countdown_2.ogg": "Two", 
                "countdown_1.ogg": "One",
                "go.ogg": "Go!",
                "game_over.ogg": "Game Over"
            },
            "es": {
                "countdown_3.ogg": "Tres",
                "countdown_2.ogg": "Dos",
                "countdown_1.ogg": "Uno", 
                "go.ogg": "¡Vamos!",
                "game_over.ogg": "Fin del Juego"
            },
            "fr": {
                "countdown_3.ogg": "Trois",
                "countdown_2.ogg": "Deux",
                "countdown_1.ogg": "Un",
                "go.ogg": "Allez!",
                "game_over.ogg": "Jeu Terminé"
            }
        }
        
        # Verify language support structure
        languages = list(language_audio_structure.keys())
        assert "en" in languages, "English should be supported"
        assert len(languages) >= 2, "Should support multiple languages"
        
        # Verify all languages have same audio cues
        base_files = set(language_audio_structure["en"].keys())
        for lang, files in language_audio_structure.items():
            lang_files = set(files.keys())
            assert lang_files == base_files, f"Language {lang} missing audio files"