"""
Example test file showing evidence-based testing approach
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import time
from src.testing.evidence_based_output import (
    EvidenceBasedTestCase, EvidenceCollector, pytest_evidence_decorator
)
from src.metrics.ai_development_metrics import (
    AIDevMetricsTracker, track_test_with_evidence
)


class TestCharacterSelectionWithEvidence(EvidenceBasedTestCase):
    """Test character selection with objective evidence"""
    
    def setUp(self):
        super().setUp()
        pygame.init()
        self.metrics_tracker = AIDevMetricsTracker(os.path.dirname(os.path.dirname(__file__)))
    
    def test_all_six_characters_selectable(self):
        """Verify all 6 characters can be selected with performance metrics"""
        
        # Record preconditions
        self.evidence.record_precondition("pygame_initialized", pygame.get_init())
        self.evidence.record_precondition("expected_character_count", 6)
        self.evidence.record_precondition("character_names", [
            "Danger", "Rose", "Dad", "Benji", "Olive", "Uncle Bear"
        ])
        
        # Import and test character buttons
        from src.scenes.title_screen import CharacterButton
        
        characters_tested = []
        performance_metrics = {}
        
        # Test each character
        for i, (name, ability) in enumerate([
            ("Danger", "Speed Burst"),
            ("Rose", "Precision"),
            ("Dad", "Experience"),
            ("Benji", "Tech Boost"),
            ("Olive", "Nature's Blessing"),
            ("Uncle Bear", "Bear Strength")
        ]):
            # Measure character button creation time
            def create_button():
                return CharacterButton(0, 0, name, "", ability)
            
            start_time = time.time()
            button = self.measure_operation(
                create_button,
                f"Create_{name}_Button"
            )
            creation_time = (time.time() - start_time) * 1000
            
            # Record action
            self.evidence.record_action(
                f"Created {name} button",
                character_name=button.character_name,
                ability_name=button.ability_name,
                creation_time_ms=creation_time
            )
            
            # Verify button properties
            self.assert_equals_with_evidence(
                name, button.character_name,
                f"{name} character name matches"
            )
            self.assert_equals_with_evidence(
                ability, button.ability_name,
                f"{name} ability name matches"
            )
            
            # Test animation loading
            self.assert_true_with_evidence(
                button.animated_character is not None,
                f"{name} has animated character"
            )
            
            # Record performance
            performance_metrics[name] = creation_time
            characters_tested.append(name)
        
        # Record postconditions
        self.evidence.record_postcondition("all_characters_created", len(characters_tested) == 6)
        self.evidence.record_postcondition("characters_tested", characters_tested)
        self.evidence.record_postcondition("average_creation_time_ms", 
                                         sum(performance_metrics.values()) / len(performance_metrics))
        
        # Verify all characters tested
        self.assert_equals_with_evidence(
            6, len(characters_tested),
            "All 6 characters tested"
        )
        
        # Generate evidence report
        evidence = self.generate_evidence_report("test_all_six_characters_selectable")
        
        # Track in metrics system
        track_test_with_evidence(
            self.metrics_tracker,
            "test_all_six_characters_selectable",
            "PASS",
            evidence.measurements,
            test_type="integration",
            assertions=evidence.assertions_passed + evidence.assertions_failed,
            coverage=85.0,  # Example coverage
            execution_time=evidence.execution_time_ms
        )
        
        # Print report
        print("\n" + evidence.to_markdown())


class TestSoundIntegrationWithEvidence(EvidenceBasedTestCase):
    """Test sound integration with objective evidence"""
    
    def setUp(self):
        super().setUp()
        self.metrics_tracker = AIDevMetricsTracker(os.path.dirname(os.path.dirname(__file__)))
    
    def test_scene_specific_sounds_exist(self):
        """Verify scene-specific sounds are properly configured"""
        
        # Record preconditions
        self.evidence.record_precondition("scenes_to_test", ["pool", "ski", "vegas"])
        self.evidence.record_precondition("sound_categories", {
            "pool": ["shot", "hit", "bullseye", "miss", "powerup", "perfect"],
            "ski": ["swoosh", "turn", "snow_spray", "tree_hit", "checkpoint", "speed_boost", "finish_line"],
            "vegas": ["coin", "slot", "dice", "card", "jackpot", "boss_appear", "special"]
        })
        
        import os
        from src.utils.asset_paths import get_sfx_path
        
        missing_sounds = []
        existing_sounds = []
        
        # Test Pool sounds
        pool_sounds = {
            'shot': get_sfx_path("pool/impact/pool_shot.mp3"),
            'hit': get_sfx_path("pool/impact/target_hit.mp3"),
            'bullseye': get_sfx_path("pool/impact/bullseye.mp3"),
            'miss': get_sfx_path("pool/impact/target_miss.mp3"),
            'powerup': get_sfx_path("pool/impact/powerup_collect.mp3"),
            'perfect': get_sfx_path("pool/impact/perfect_round.mp3")
        }
        
        for sound_name, sound_path in pool_sounds.items():
            exists = os.path.exists(sound_path)
            self.evidence.record_action(
                f"Check Pool {sound_name} sound",
                path=sound_path,
                exists=exists
            )
            if exists:
                existing_sounds.append(f"pool/{sound_name}")
            else:
                missing_sounds.append(f"pool/{sound_name}")
        
        # Test Ski sounds
        ski_sounds = {
            'swoosh': get_sfx_path("ski/movement/ski_swoosh.mp3"),
            'turn': get_sfx_path("ski/movement/ski_turn.mp3"),
            'snow_spray': get_sfx_path("ski/movement/snow_spray.mp3"),
            'tree_hit': get_sfx_path("ski/movement/tree_hit.mp3"),
            'checkpoint': get_sfx_path("ski/movement/checkpoint.mp3"),
            'speed_boost': get_sfx_path("ski/movement/speed_boost.mp3"),
            'finish_line': get_sfx_path("ski/movement/finish_line.mp3")
        }
        
        for sound_name, sound_path in ski_sounds.items():
            exists = os.path.exists(sound_path)
            self.evidence.record_action(
                f"Check Ski {sound_name} sound",
                path=sound_path,
                exists=exists
            )
            if exists:
                existing_sounds.append(f"ski/{sound_name}")
            else:
                missing_sounds.append(f"ski/{sound_name}")
        
        # Record measurements
        self.evidence.record_measurement("total_sounds_checked", 
                                       len(pool_sounds) + len(ski_sounds), "sounds")
        self.evidence.record_measurement("existing_sounds", 
                                       len(existing_sounds), "sounds")
        self.evidence.record_measurement("missing_sounds", 
                                       len(missing_sounds), "sounds")
        self.evidence.record_measurement("sound_availability_rate",
                                       (len(existing_sounds) / (len(pool_sounds) + len(ski_sounds))) * 100, "%")
        
        # Record postconditions
        self.evidence.record_postcondition("all_sounds_exist", len(missing_sounds) == 0)
        self.evidence.record_postcondition("existing_sound_list", existing_sounds)
        self.evidence.record_postcondition("missing_sound_list", missing_sounds)
        
        # Generate report
        evidence = self.generate_evidence_report("test_scene_specific_sounds_exist")
        
        # Track in metrics
        track_test_with_evidence(
            self.metrics_tracker,
            "test_scene_specific_sounds_exist",
            "PASS" if len(missing_sounds) == 0 else "FAIL",
            evidence.measurements,
            test_type="integration",
            assertions=evidence.assertions_passed + evidence.assertions_failed,
            execution_time=evidence.execution_time_ms
        )
        
        print("\n" + evidence.to_markdown())


@pytest_evidence_decorator
def test_performance_measurement_example():
    """Example of performance testing with evidence"""
    collector = test_performance_measurement_example._evidence_collector
    
    # Record test parameters
    collector.record_precondition("operation", "sprite_loading")
    collector.record_precondition("expected_max_time_ms", 100)
    
    # Simulate sprite loading
    def load_sprite():
        time.sleep(0.05)  # 50ms
        return {"width": 128, "height": 128, "format": "RGBA"}
    
    # Measure operation
    start = time.time()
    result = load_sprite()
    duration = (time.time() - start) * 1000
    
    # Record measurements
    collector.record_measurement("sprite_load_time", duration, "ms")
    collector.record_measurement("sprite_dimensions", 
                               f"{result['width']}x{result['height']}", "pixels")
    
    # Assert performance
    assert duration < 100, f"Sprite loading took {duration:.2f}ms, expected < 100ms"
    
    collector.record_postcondition("sprite_loaded", True)
    collector.record_postcondition("sprite_properties", result)


if __name__ == "__main__":
    print("Running Evidence-Based Tests Example")
    print("=" * 80)
    
    # Run character selection test
    test1 = TestCharacterSelectionWithEvidence()
    test1.setUp()
    test1.test_all_six_characters_selectable()
    
    print("\n" + "=" * 80 + "\n")
    
    # Run sound integration test
    test2 = TestSoundIntegrationWithEvidence()
    test2.setUp()
    test2.test_scene_specific_sounds_exist()
    
    print("\n" + "=" * 80 + "\n")
    
    # Run performance test
    test_performance_measurement_example()
    
    # Generate metrics report
    tracker = AIDevMetricsTracker(os.path.dirname(os.path.dirname(__file__)))
    print("\n" + "=" * 80)
    print("METRICS SUMMARY")
    print("=" * 80)
    print(tracker.generate_report())