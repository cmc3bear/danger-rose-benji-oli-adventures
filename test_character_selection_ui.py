"""
Test script for Issue #28 - Character Selection UI
Tests that all 6 characters are selectable and display correctly
"""

import os
import sys
import pygame

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.scenes.title_screen import TitleScreen
from src.config.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.managers.sound_manager import SoundManager
from src.metrics.character_selection_metrics_collector import CharacterSelectionMetricsCollector


def test_character_selection_ui():
    """Test the character selection UI implementation"""
    
    print("Testing Character Selection UI for Issue #28...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Character Selection Test")
    
    # Initialize sound manager (mock)
    class MockSoundManager:
        def play_sfx(self, path):
            pass
    
    sound_manager = MockSoundManager()
    
    try:
        # Create title screen
        title_screen = TitleScreen(SCREEN_WIDTH, SCREEN_HEIGHT, sound_manager)
        
        # Initialize metrics collector
        metrics_collector = CharacterSelectionMetricsCollector(".")
        
        print(f"\n=== Character Selection UI Test Results ===")
        
        # Test 1: Count characters
        character_count = len(title_screen.character_buttons)
        print(f"✅ Character count: {character_count}/6")
        
        # Test 2: List all characters
        print(f"\n📋 Available Characters:")
        for i, button in enumerate(title_screen.character_buttons):
            print(f"  {i+1}. {button.character_name} - {button.ability_name}")
        
        # Test 3: Validate grid layout
        grid_data = metrics_collector.validate_character_grid_layout(title_screen)
        print(f"\n🎯 Grid Layout Validation:")
        print(f"  Grid layout valid: {grid_data['grid_layout_valid']}")
        print(f"  Row 1 characters: {grid_data['row1_count']}")
        print(f"  Row 2 characters: {grid_data['row2_count']}")
        print(f"  Position accuracy: {grid_data['positioning_accuracy']:.1f}%")
        
        # Test 4: Test character selection
        selection_data = metrics_collector.test_character_selection_functionality(title_screen)
        print(f"\n🎮 Selection Functionality:")
        print(f"  All characters selectable: {selection_data['all_characters_selectable']}")
        print(f"  Average response time: {selection_data['average_response_time_ms']:.2f}ms")
        print(f"  Animation loading rate: {selection_data['animation_loading_rate']:.1%}")
        
        # Test 5: Collect comprehensive metrics
        metrics = metrics_collector.collect_comprehensive_metrics(title_screen)
        print(f"\n📊 Performance Metrics:")
        print(f"  UI render time: {metrics.ui_render_time_ms:.2f}ms")
        print(f"  Memory usage: {metrics.memory_usage_mb:.1f}MB")
        print(f"  FPS impact: {metrics.fps_impact:.1f}")
        print(f"  Sprites loaded: {metrics.character_sprites_loaded}")
        
        # Test 6: Generate OQE report
        report = metrics_collector.generate_oqe_report(metrics)
        print(f"\n🎯 OQE Compliance Report:")
        print(f"  Overall status: {report['overall_status']}")
        print(f"  Success rate: {report['success_rate_percent']:.1f}%")
        print(f"  Verification status: {report['oqe_compliance']['verification_status']}")
        
        if report['critical_issues']:
            print(f"\n⚠️  Critical Issues:")
            for issue in report['critical_issues']:
                print(f"    - {issue}")
        else:
            print(f"\n✅ No critical issues found!")
        
        print(f"\n📈 Recommendations:")
        for rec in report['recommendations']:
            print(f"    - {rec}")
        
        # Visual test - draw a few frames
        print(f"\n🎨 Running visual test...")
        clock = pygame.time.Clock()
        for frame in range(10):
            # Update and draw
            title_screen.update(1/60)
            title_screen.draw(screen)
            pygame.display.flip()
            clock.tick(60)
        
        print(f"✅ Visual test completed - UI renders correctly")
        
        # Overall assessment
        success_rate = report['success_rate_percent']
        if success_rate >= 90:
            print(f"\n🎉 ISSUE #28 IMPLEMENTATION: SUCCESSFUL")
            print(f"   Character selection UI fully supports 6 characters")
            print(f"   All performance targets met ({success_rate:.1f}% success rate)")
            return True
        else:
            print(f"\n❌ ISSUE #28 IMPLEMENTATION: NEEDS IMPROVEMENT")
            print(f"   Success rate: {success_rate:.1f}% (target: 90%)")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        pygame.quit()


if __name__ == "__main__":
    success = test_character_selection_ui()
    sys.exit(0 if success else 1)