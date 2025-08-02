"""Tests for the BPM-synchronized traffic system."""

import pytest
import time
from unittest.mock import Mock, MagicMock

from src.systems import (
    BPMTracker,
    RhythmicTrafficController,
    RhythmEventSystem,
    RhythmVisualFeedback,
    RhythmConfiguration,
    BPMTrafficIntegration,
    BeatEvent,
    BeatStrength,
    DifficultyLevel,
    RhythmIntensity
)


class TestBPMTracker:
    """Test the BPM tracking functionality."""
    
    def test_bpm_tracker_initialization(self):
        """Test BPM tracker initializes correctly."""
        sound_manager = Mock()
        tracker = BPMTracker(sound_manager)
        
        assert tracker.current_bpm == 120.0
        assert not tracker.is_tracking
        assert tracker.current_beat == 0
        
    def test_start_tracking(self):
        """Test starting BPM tracking."""
        sound_manager = Mock()
        tracker = BPMTracker(sound_manager)
        
        tracker.start_tracking(track_bpm=140.0, beat_offset=0.5)
        
        assert tracker.current_bpm == 140.0
        assert tracker.beat_offset == 0.5
        assert tracker.is_tracking
        
    def test_beat_interval_calculation(self):
        """Test beat interval is calculated correctly."""
        sound_manager = Mock()
        tracker = BPMTracker(sound_manager)
        
        tracker.start_tracking(track_bpm=120.0)
        assert tracker.beat_interval == 0.5  # 60/120 = 0.5 seconds per beat
        
        tracker.start_tracking(track_bpm=60.0)
        assert tracker.beat_interval == 1.0  # 60/60 = 1.0 seconds per beat
        
    def test_beat_progress(self):
        """Test beat progress calculation."""
        sound_manager = Mock()
        tracker = BPMTracker(sound_manager)
        
        # Mock time to test progress calculation
        with pytest.MonkeyPatch().context() as m:
            start_time = 1000.0
            m.setattr(time, 'time', lambda: start_time)
            
            tracker.start_tracking(track_bpm=120.0)
            
            # Test at quarter beat
            m.setattr(time, 'time', lambda: start_time + 0.125)
            assert abs(tracker.get_beat_progress() - 0.25) < 0.01
            
            # Test at half beat
            m.setattr(time, 'time', lambda: start_time + 0.25)
            assert abs(tracker.get_beat_progress() - 0.5) < 0.01


class TestRhythmicTrafficController:
    """Test the rhythmic traffic controller."""
    
    def test_traffic_controller_initialization(self):
        """Test traffic controller initializes correctly."""
        bpm_tracker = Mock()
        controller = RhythmicTrafficController(bpm_tracker, 1280, 720)
        
        assert controller.rhythm_intensity == 0.7
        assert controller.base_spawn_rate == 0.4
        assert len(controller.spawn_probability) == 4  # Four beat strengths
        
    def test_spawn_probability_calculation(self):
        """Test spawn probability varies by beat strength."""
        bpm_tracker = Mock()
        controller = RhythmicTrafficController(bpm_tracker, 1280, 720)
        
        # Downbeats should have higher probability than weak beats
        downbeat_prob = controller.spawn_probability[BeatStrength.DOWNBEAT]
        weak_prob = controller.spawn_probability[BeatStrength.WEAK]
        
        assert downbeat_prob > weak_prob
        
    def test_bpm_modifier_calculation(self):
        """Test BPM affects spawn rate modifier."""
        bpm_tracker = Mock()
        bpm_tracker.current_bpm = 60.0  # Slow music
        controller = RhythmicTrafficController(bpm_tracker, 1280, 720)
        
        controller._update_bpm_modifiers()
        assert controller.bpm_spawn_modifier < 1.0  # Should reduce spawning
        
        bpm_tracker.current_bpm = 160.0  # Fast music
        controller._update_bpm_modifiers()
        assert controller.bpm_spawn_modifier > 1.0  # Should increase spawning


class TestRhythmConfiguration:
    """Test the rhythm configuration system."""
    
    def test_difficulty_settings(self):
        """Test difficulty settings are correctly configured."""
        config = RhythmConfiguration()
        
        easy_settings = config.difficulty_settings[DifficultyLevel.EASY]
        hard_settings = config.difficulty_settings[DifficultyLevel.HARD]
        
        # Easy should be more forgiving
        assert easy_settings.beat_tolerance > hard_settings.beat_tolerance
        assert easy_settings.base_traffic_density < hard_settings.base_traffic_density
        
    def test_bpm_modifier_calculation(self):
        """Test BPM modifier calculation."""
        config = RhythmConfiguration()
        
        # Test different BPM ranges
        slow_modifier = config.get_bpm_modifier(80.0)  # Slow music
        normal_modifier = config.get_bpm_modifier(120.0)  # Normal music  
        fast_modifier = config.get_bpm_modifier(160.0)  # Fast music
        
        assert slow_modifier < normal_modifier < fast_modifier
        
    def test_traffic_density_calculation(self):
        """Test traffic density calculation based on BPM."""
        config = RhythmConfiguration()
        
        density_slow = config.get_traffic_density(80.0)
        density_fast = config.get_traffic_density(160.0)
        
        # Fast music should generally have more traffic
        assert density_fast >= density_slow
        
    def test_spawn_probability_by_beat_strength(self):
        """Test spawn probability varies correctly by beat strength."""
        config = RhythmConfiguration()
        
        weak_prob = config.get_spawn_probability(BeatStrength.WEAK, 120.0)
        strong_prob = config.get_spawn_probability(BeatStrength.STRONG, 120.0)
        downbeat_prob = config.get_spawn_probability(BeatStrength.DOWNBEAT, 120.0)
        
        assert weak_prob < strong_prob < downbeat_prob


class TestBPMTrafficIntegration:
    """Test the complete BPM traffic integration system."""
    
    def test_integration_initialization(self):
        """Test integration system initializes all components."""
        drive_game = Mock()
        sound_manager = Mock()
        
        integration = BPMTrafficIntegration(
            drive_game, sound_manager, 1280, 720
        )
        
        assert integration.bpm_tracker is not None
        assert integration.traffic_controller is not None
        assert integration.event_system is not None
        assert integration.visual_feedback is not None
        assert integration.config is not None
        
    def test_track_initialization(self):
        """Test initializing for a specific music track."""
        drive_game = Mock()
        sound_manager = Mock()
        
        integration = BPMTrafficIntegration(
            drive_game, sound_manager, 1280, 720
        )
        
        # Mock music track
        mock_track = Mock()
        mock_track.name = "test_track"
        mock_track.bpm = 130.0
        
        integration.initialize_for_track(mock_track)
        
        assert integration.state.is_active
        assert integration.state.current_bpm == 130.0
        
    def test_spawn_callback_registration(self):
        """Test spawn callback registration and handling."""
        drive_game = Mock()
        sound_manager = Mock()
        
        integration = BPMTrafficIntegration(
            drive_game, sound_manager, 1280, 720
        )
        
        # Register mock callback
        spawn_callback = Mock(return_value=True)
        integration.register_spawn_callback(spawn_callback)
        
        assert integration.spawn_callback == spawn_callback
        
    def test_difficulty_adjustment(self):
        """Test difficulty can be adjusted."""
        drive_game = Mock()
        sound_manager = Mock()
        
        integration = BPMTrafficIntegration(
            drive_game, sound_manager, 1280, 720
        )
        
        # Test setting difficulty
        integration.set_difficulty(DifficultyLevel.HARD)
        assert integration.config.current_difficulty == DifficultyLevel.HARD
        
    def test_rhythm_intensity_adjustment(self):
        """Test rhythm intensity can be adjusted."""
        drive_game = Mock()
        sound_manager = Mock()
        
        integration = BPMTrafficIntegration(
            drive_game, sound_manager, 1280, 720
        )
        
        # Test setting rhythm intensity
        integration.set_rhythm_intensity(RhythmIntensity.INTENSE)
        assert integration.config.gameplay_settings.rhythm_intensity == RhythmIntensity.INTENSE


class TestBeatEvent:
    """Test beat event functionality."""
    
    def test_beat_event_creation(self):
        """Test beat event is created correctly."""
        event = BeatEvent(
            beat_number=4,
            measure_number=1,
            beat_in_measure=0,
            strength=BeatStrength.DOWNBEAT,
            timestamp=1000.0,
            bpm=120.0
        )
        
        assert event.beat_number == 4
        assert event.measure_number == 1
        assert event.beat_in_measure == 0
        assert event.strength == BeatStrength.DOWNBEAT
        assert event.timestamp == 1000.0
        assert event.bpm == 120.0
        assert not event.is_predicted  # Default value


# Integration test
class TestSystemIntegration:
    """Test the complete system working together."""
    
    def test_full_system_flow(self):
        """Test complete BPM system flow."""
        # Setup mocks
        drive_game = Mock()
        sound_manager = Mock()
        
        # Create integration system
        integration = BPMTrafficIntegration(
            drive_game, sound_manager, 1280, 720
        )
        
        # Setup callbacks
        spawn_callback = Mock(return_value=True)
        speed_callback = Mock()
        integration.register_spawn_callback(spawn_callback)
        integration.register_speed_callback(speed_callback)
        
        # Initialize with track
        mock_track = Mock()
        mock_track.name = "test_track"
        mock_track.bpm = 120.0
        integration.initialize_for_track(mock_track)
        
        # Simulate update cycle
        player_state = {"x": 0.5, "speed": 1.0}
        current_traffic = []
        
        integration.update(0.016, player_state, current_traffic)  # 60 FPS
        
        # Verify system is active
        stats = integration.get_current_stats()
        assert stats["integration_state"]["is_active"]
        assert stats["integration_state"]["current_bpm"] == 120.0
        
    def test_performance_mode(self):
        """Test performance mode reduces effects."""
        drive_game = Mock()
        sound_manager = Mock()
        
        integration = BPMTrafficIntegration(
            drive_game, sound_manager, 1280, 720
        )
        
        # Enable performance mode
        integration.enable_performance_mode(True)
        
        assert not integration.state.visual_effects_active
        
        # Disable performance mode
        integration.enable_performance_mode(False)
        
        assert integration.state.visual_effects_active


if __name__ == "__main__":
    pytest.main([__file__])