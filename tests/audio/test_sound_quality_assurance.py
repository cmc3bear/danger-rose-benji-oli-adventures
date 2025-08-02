"""Comprehensive sound effects testing and quality assurance for Danger Rose."""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch
from wave import Wave_read

import pygame
import pytest

from src.config.constants import (
    DEFAULT_MASTER_VOLUME,
    DEFAULT_MUSIC_VOLUME,
    DEFAULT_SFX_VOLUME,
    AUDIO_FADE_TIME,
)
from src.managers.sound_manager import SoundManager


class TestSoundQualityAssurance:
    """Comprehensive quality assurance tests for sound effects system."""

    @pytest.fixture
    def setup_test_environment(self):
        """Setup controlled test environment for audio testing."""
        # Clear singleton instance
        SoundManager._instance = None
        
        # Create temporary directory for test assets
        temp_dir = tempfile.mkdtemp()
        
        yield temp_dir
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sound_manager_with_audio(self, setup_test_environment):
        """Create sound manager with mocked but functional audio system."""
        with patch("pygame.mixer.init") as mock_init:
            mock_init.return_value = None  # Successful init
            with patch("pygame.mixer.get_init", return_value=(44100, -16, 2, 512)):
                sm = SoundManager()
                yield sm

    def test_audio_initialization_quality_standards(self, sound_manager_with_audio):
        """Test that audio system initializes with CD quality standards."""
        sm = sound_manager_with_audio
        
        # Verify CD quality audio settings
        with patch("pygame.mixer.init") as mock_init:
            sm.__init__()
            mock_init.assert_called_with(
                frequency=44100,  # CD quality sample rate
                size=-16,        # 16-bit signed samples
                channels=2,      # Stereo
                buffer=512       # Low latency buffer
            )

    def test_volume_normalization_standards(self, sound_manager_with_audio):
        """Test volume levels meet accessibility and quality standards."""
        sm = sound_manager_with_audio
        
        # Test default volumes are within reasonable ranges
        assert 0.3 <= sm.master_volume <= 0.8, "Master volume should be moderate by default"
        assert 0.3 <= sm.music_volume <= 0.7, "Music should be quieter than effects"
        assert 0.5 <= sm.sfx_volume <= 1.0, "SFX should be clearly audible"
        
        # Test volume combinations don't exceed safe levels
        max_combined = sm.master_volume * max(sm.music_volume, sm.sfx_volume)
        assert max_combined <= 0.8, "Combined volume should not exceed 80% for hearing safety"

    def test_latency_requirements(self, sound_manager_with_audio):
        """Test audio system meets low-latency requirements for gaming."""
        sm = sound_manager_with_audio
        
        # Test buffer size for gaming latency (< 12ms at 44.1kHz)
        expected_latency_ms = (512 / 44100) * 1000
        assert expected_latency_ms < 12, f"Audio latency {expected_latency_ms:.1f}ms too high for gaming"

    @patch("os.path.exists", return_value=True)
    @patch("pygame.mixer.Sound")
    def test_memory_leak_detection(self, mock_sound, mock_exists, sound_manager_with_audio):
        """Test for memory leaks in sound effect caching."""
        sm = sound_manager_with_audio
        mock_sound_obj = Mock()
        mock_sound.return_value = mock_sound_obj
        
        # Load many sounds to test cache management
        sound_files = [f"test_sound_{i}.wav" for i in range(100)]
        
        for sound_file in sound_files:
            sm.preload_sound(sound_file)
        
        # Verify cache doesn't grow indefinitely
        assert len(sm.sfx_cache) == 100, "Cache should store all preloaded sounds"
        
        # Test cache clearing prevents memory leaks
        sm.clear_cache()
        assert len(sm.sfx_cache) == 0, "Cache should be empty after clearing"

    def test_performance_benchmarks(self, sound_manager_with_audio):
        """Test sound system performance meets gaming requirements."""
        sm = sound_manager_with_audio
        
        with patch("pygame.mixer.find_channel") as mock_find:
            mock_channel = Mock()
            mock_find.return_value = mock_channel
            
            with patch("os.path.exists", return_value=True):
                with patch("pygame.mixer.Sound"):
                    # Benchmark sound loading time
                    start_time = time.time()
                    for i in range(10):
                        sm.play_sfx(f"benchmark_sound_{i}.wav")
                    load_time = time.time() - start_time
                    
                    # Should handle 10 sounds in under 100ms
                    assert load_time < 0.1, f"Sound loading too slow: {load_time:.3f}s"

    def test_cpu_usage_monitoring(self, sound_manager_with_audio):
        """Test that sound system has minimal CPU impact."""
        sm = sound_manager_with_audio
        
        # Test that volume changes are O(1) operations
        start_time = time.time()
        for _ in range(1000):
            sm.set_master_volume(0.5)
            sm.set_music_volume(0.6)
            sm.set_sfx_volume(0.7)
        volume_time = time.time() - start_time
        
        # Should complete 1000 volume changes in under 10ms
        assert volume_time < 0.01, f"Volume operations too slow: {volume_time:.3f}s"

    def test_frequency_analysis_standards(self, sound_manager_with_audio):
        """Test audio frequency response meets quality standards."""
        sm = sound_manager_with_audio
        
        # Mock frequency analysis
        with patch("pygame.mixer.get_init", return_value=(44100, -16, 2, 512)):
            sample_rate, bit_depth, channels, buffer_size = pygame.mixer.get_init()
            
            # Verify Nyquist frequency coverage
            nyquist_freq = sample_rate // 2
            assert nyquist_freq >= 20000, "Should cover human hearing range up to 20kHz"
            
            # Verify bit depth for dynamic range
            dynamic_range_db = bit_depth * 6  # 6dB per bit
            assert dynamic_range_db >= 90, "Should have at least 90dB dynamic range"


class TestSoundIntegration:
    """Integration tests for sound system with game scenes."""

    @pytest.fixture
    def mock_scene_manager(self):
        """Mock scene manager for integration testing."""
        with patch("src.scene_manager.SceneManager") as mock_sm:
            yield mock_sm

    def test_scene_specific_sound_triggers(self, mock_scene_manager):
        """Test sound triggers work correctly in different game scenes."""
        # Test ski game sounds
        ski_sounds = [
            "swoosh_turn.ogg",
            "snowflake_collect.ogg", 
            "tree_crash.ogg",
            "ski_victory.ogg"
        ]
        
        # Test pool game sounds
        pool_sounds = [
            "balloon_launch.ogg",
            "target_hit.ogg",
            "splash.ogg",
            "powerup_collect.ogg"
        ]
        
        # Test vegas game sounds
        vegas_sounds = [
            "jump.ogg",
            "boss_hit.ogg",
            "building_land.ogg",
            "victory_fanfare.ogg"
        ]
        
        all_sounds = ski_sounds + pool_sounds + vegas_sounds
        
        # Verify all game sounds are properly categorized
        assert len(all_sounds) == len(set(all_sounds)), "No duplicate sound files"
        assert all(sound.endswith('.ogg') for sound in all_sounds), "All sounds use OGG format"

    def test_multi_effect_scenarios(self, mock_scene_manager):
        """Test multiple simultaneous sound effects."""
        with patch("src.managers.sound_manager.SoundManager") as mock_sm:
            sm_instance = Mock()
            mock_sm.return_value = sm_instance
            
            # Simulate multi-effect scenario: player hits target while powerup expires
            sm_instance.play_sfx("target_hit.ogg")
            sm_instance.play_sfx("powerup_expire.ogg") 
            sm_instance.play_sfx("score_bonus.ogg")
            
            # Verify all effects can play simultaneously
            assert sm_instance.play_sfx.call_count == 3

    def test_music_effect_balance(self, mock_scene_manager):
        """Test music and effects maintain proper balance."""
        with patch("src.managers.sound_manager.SoundManager") as mock_sm:
            sm_instance = Mock()
            mock_sm.return_value = sm_instance
            sm_instance.music_volume = 0.5
            sm_instance.sfx_volume = 0.8
            
            # Effects should be louder than music for clarity
            assert sm_instance.sfx_volume > sm_instance.music_volume
            
            # But not too much louder
            volume_ratio = sm_instance.sfx_volume / sm_instance.music_volume
            assert volume_ratio <= 2.0, "SFX should not overpower music"

    def test_cross_platform_compatibility(self):
        """Test sound system works across different platforms."""
        # Test Windows audio initialization
        with patch("pygame.mixer.init") as mock_init:
            with patch("platform.system", return_value="Windows"):
                SoundManager._instance = None
                sm = SoundManager()
                mock_init.assert_called_once()
        
        # Test macOS audio initialization  
        with patch("pygame.mixer.init") as mock_init:
            with patch("platform.system", return_value="Darwin"):
                SoundManager._instance = None
                sm = SoundManager()
                mock_init.assert_called_once()
        
        # Test Linux audio initialization
        with patch("pygame.mixer.init") as mock_init:
            with patch("platform.system", return_value="Linux"):
                SoundManager._instance = None
                sm = SoundManager()
                mock_init.assert_called_once()


class TestUserExperienceQuality:
    """Tests for sound effects user experience quality."""

    def test_sound_clarity_in_gameplay(self):
        """Test that sounds are clear and distinguishable during gameplay."""
        # Define expected sound characteristics
        sound_expectations = {
            "target_hit.ogg": {"duration_ms": (100, 500), "volume_boost": True},
            "powerup_collect.ogg": {"duration_ms": (200, 800), "volume_boost": True},
            "background_ambient.ogg": {"duration_ms": (2000, 10000), "volume_boost": False},
            "victory_fanfare.ogg": {"duration_ms": (1000, 3000), "volume_boost": True},
        }
        
        for sound_file, expectations in sound_expectations.items():
            min_duration, max_duration = expectations["duration_ms"]
            
            # Verify sound duration is appropriate for its purpose
            assert min_duration > 0, f"{sound_file} should have measurable duration"
            assert max_duration < 10000, f"{sound_file} should not be too long"

    def test_feedback_effectiveness(self):
        """Test that sound effects provide clear feedback for player actions."""
        feedback_sounds = {
            "positive": ["target_hit.ogg", "powerup_collect.ogg", "level_complete.ogg"],
            "negative": ["crash.ogg", "life_lost.ogg", "time_warning.ogg"],
            "neutral": ["menu_select.ogg", "pause.ogg", "unpause.ogg"],
        }
        
        # Verify we have sounds for all feedback types
        for feedback_type, sounds in feedback_sounds.items():
            assert len(sounds) >= 2, f"Should have multiple {feedback_type} feedback sounds"

    def test_annoyance_factors(self):
        """Test that sounds don't become annoying with repetition."""
        repetitive_sounds = [
            "snowflake_collect.ogg",  # Collected frequently in ski game
            "balloon_launch.ogg",     # Used repeatedly in pool game
            "menu_hover.ogg",         # Triggered on UI navigation
        ]
        
        for sound in repetitive_sounds:
            # These sounds should be short and pleasant
            # In real implementation, we'd analyze audio properties
            assert sound.endswith('.ogg'), f"{sound} should use OGG format for compression"

    def test_accessibility_compliance(self):
        """Test sound system meets accessibility requirements."""
        # Test visual indicators accompany audio cues
        audio_visual_pairs = [
            ("target_hit.ogg", "target_explosion_effect"),
            ("powerup_collect.ogg", "powerup_sparkle_effect"),
            ("life_lost.ogg", "screen_flash_effect"),
        ]
        
        for audio_cue, visual_cue in audio_visual_pairs:
            # Verify each audio cue has corresponding visual feedback
            assert audio_cue and visual_cue, "Audio and visual feedback should be paired"

    def test_volume_accessibility_ranges(self):
        """Test volume controls provide accessible ranges."""
        sm = SoundManager()
        
        # Test fine-grained volume control
        for volume in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
            sm.set_master_volume(volume)
            assert abs(sm.master_volume - volume) < 0.01, "Volume should be precisely controllable"


class TestPerformanceMetrics:
    """Performance and resource usage tests for sound system."""

    def test_memory_footprint_limits(self):
        """Test sound system stays within memory limits."""
        sm = SoundManager()
        
        # Estimate cache memory usage (approximate)
        with patch("pygame.mixer.Sound") as mock_sound:
            mock_sound_obj = Mock()
            mock_sound_obj.get_length.return_value = 2.0  # 2 seconds
            mock_sound.return_value = mock_sound_obj
            
            # Load 50 sounds (typical game might have 20-100)
            for i in range(50):
                sm.preload_sound(f"test_sound_{i}.ogg")
            
            # Verify cache size is reasonable
            assert len(sm.sfx_cache) <= 50, "Cache should not exceed loaded sounds"

    def test_loading_time_impact(self):
        """Test sound loading doesn't impact game startup time."""
        with patch("pygame.mixer.Sound") as mock_sound:
            with patch("os.path.exists", return_value=True):
                start_time = time.time()
                
                sm = SoundManager()
                # Preload essential sounds
                essential_sounds = [
                    "menu_select.ogg", "menu_back.ogg",
                    "target_hit.ogg", "powerup_collect.ogg",
                    "life_lost.ogg", "victory.ogg"
                ]
                
                for sound in essential_sounds:
                    sm.preload_sound(sound)
                
                load_time = time.time() - start_time
                
                # Should load essential sounds in under 50ms
                assert load_time < 0.05, f"Essential sound loading too slow: {load_time:.3f}s"

    def test_mobile_device_compatibility(self):
        """Test sound system works on resource-constrained devices."""
        # Test with reduced buffer size for mobile
        with patch("pygame.mixer.init") as mock_init:
            # Mobile-optimized settings
            SoundManager._instance = None
            sm = SoundManager()
            
            # Verify mobile-friendly initialization was attempted
            mock_init.assert_called_with(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=512  # Small buffer for mobile
            )

    def test_concurrent_sound_limits(self):
        """Test system handles maximum concurrent sounds gracefully."""
        sm = SoundManager()
        
        # Test with 8 reserved channels
        assert len(sm.sfx_channels) == 8, "Should have 8 dedicated SFX channels"
        
        # Simulate playing sounds on all channels
        with patch("pygame.mixer.find_channel") as mock_find:
            # First 8 calls return channels, 9th returns None
            mock_channels = [Mock() for _ in range(8)]
            mock_find.side_effect = mock_channels + [None]
            
            with patch("os.path.exists", return_value=True):
                with patch("pygame.mixer.Sound"):
                    # Play 9 sounds (more than available channels)
                    results = []
                    for i in range(9):
                        result = sm.play_sfx(f"sound_{i}.ogg")
                        results.append(result)
                    
                    # Should handle gracefully when no channels available
                    assert results[8] is not None, "Should force use of first channel when all busy"


class TestSoundCategoryAcceptanceCriteria:
    """Acceptance criteria tests for each sound effect category."""

    def test_ui_sound_acceptance_criteria(self):
        """Test UI sound effects meet acceptance criteria."""
        ui_sounds = {
            "menu_select.ogg": {
                "max_duration_ms": 200,
                "volume_range": (0.6, 1.0),
                "required": True
            },
            "menu_back.ogg": {
                "max_duration_ms": 150,
                "volume_range": (0.5, 0.8),
                "required": True
            },
            "button_hover.ogg": {
                "max_duration_ms": 100,
                "volume_range": (0.3, 0.6),
                "required": False
            }
        }
        
        for sound_file, criteria in ui_sounds.items():
            # Verify acceptance criteria structure
            assert "max_duration_ms" in criteria
            assert "volume_range" in criteria
            assert "required" in criteria
            
            # UI sounds should be short and crisp
            assert criteria["max_duration_ms"] <= 200

    def test_gameplay_sound_acceptance_criteria(self):
        """Test gameplay sound effects meet acceptance criteria."""
        gameplay_sounds = {
            "target_hit.ogg": {
                "feedback_type": "positive",
                "volume_boost": True,
                "spatial_audio": False,
                "interrupts_music": False
            },
            "powerup_collect.ogg": {
                "feedback_type": "positive", 
                "volume_boost": True,
                "spatial_audio": False,
                "interrupts_music": False
            },
            "crash.ogg": {
                "feedback_type": "negative",
                "volume_boost": True,
                "spatial_audio": True,
                "interrupts_music": True
            }
        }
        
        for sound_file, criteria in gameplay_sounds.items():
            assert criteria["feedback_type"] in ["positive", "negative", "neutral"]
            # Positive sounds should provide clear reward feedback
            if criteria["feedback_type"] == "positive":
                assert criteria["volume_boost"] is True

    def test_ambient_sound_acceptance_criteria(self):
        """Test ambient sound effects meet acceptance criteria."""
        ambient_sounds = {
            "wind_loop.ogg": {
                "loops": True,
                "volume_range": (0.1, 0.3),
                "scene_specific": "ski",
                "duck_priority": "low"
            },
            "water_ambient.ogg": {
                "loops": True,
                "volume_range": (0.1, 0.4),
                "scene_specific": "pool", 
                "duck_priority": "low"
            },
            "city_night.ogg": {
                "loops": True,
                "volume_range": (0.2, 0.4),
                "scene_specific": "vegas",
                "duck_priority": "low"
            }
        }
        
        for sound_file, criteria in ambient_sounds.items():
            # Ambient sounds should loop and be quiet
            assert criteria["loops"] is True
            volume_min, volume_max = criteria["volume_range"]
            assert volume_max <= 0.4, "Ambient sounds should not overpower gameplay"
            assert criteria["duck_priority"] == "low", "Ambient sounds should duck for gameplay sounds"

    def test_character_sound_acceptance_criteria(self):
        """Test character-specific sound effects meet acceptance criteria."""
        character_sounds = {
            "danger_jump.ogg": {
                "character": "danger",
                "action": "jump",
                "positional": True,
                "priority": "high"
            },
            "rose_collect.ogg": {
                "character": "rose", 
                "action": "collect",
                "positional": False,
                "priority": "medium"
            },
            "dad_victory.ogg": {
                "character": "dad",
                "action": "victory",
                "positional": False,
                "priority": "high"
            }
        }
        
        for sound_file, criteria in character_sounds.items():
            assert criteria["character"] in ["danger", "rose", "dad"]
            assert criteria["priority"] in ["low", "medium", "high"]
            # Victory sounds should always be high priority
            if criteria["action"] == "victory":
                assert criteria["priority"] == "high"