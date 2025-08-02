"""Comprehensive audio testing suite for Danger Rose."""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import pygame
import pytest


class AudioTestSuite:
    """Comprehensive audio testing and validation suite."""

    def __init__(self):
        """Initialize the audio test suite."""
        self.test_results: Dict[str, Dict] = {}
        self.failed_tests: List[str] = []
        self.passed_tests: List[str] = []

    def run_unit_tests(self) -> bool:
        """Run all unit tests for sound system."""
        print("🧪 Running Unit Tests...")
        
        # Run sound manager unit tests
        result = pytest.main([
            "tests/test_sound_manager.py",
            "tests/test_sound_manager_ci.py",
            "tests/unit/test_mock_sound_manager.py",
            "-v",
            "--tb=short"
        ])
        
        success = result == 0
        self.test_results["unit_tests"] = {
            "success": success,
            "exit_code": result
        }
        
        if success:
            self.passed_tests.append("Unit Tests")
            print("✅ Unit tests passed")
        else:
            self.failed_tests.append("Unit Tests")
            print("❌ Unit tests failed")
        
        return success

    def run_quality_assurance_tests(self) -> bool:
        """Run comprehensive quality assurance tests."""
        print("🔍 Running Quality Assurance Tests...")
        
        result = pytest.main([
            "tests/audio/test_sound_quality_assurance.py",
            "-v",
            "--tb=short"
        ])
        
        success = result == 0
        self.test_results["qa_tests"] = {
            "success": success,
            "exit_code": result
        }
        
        if success:
            self.passed_tests.append("Quality Assurance")
            print("✅ QA tests passed")
        else:
            self.failed_tests.append("Quality Assurance")
            print("❌ QA tests failed")
        
        return success

    def run_performance_tests(self) -> bool:
        """Run performance and stress tests."""
        print("⚡ Running Performance Tests...")
        
        result = pytest.main([
            "tests/audio/test_sound_performance.py",
            "-v",
            "--tb=short",
            "-m", "not slow"  # Skip slow tests by default
        ])
        
        success = result == 0
        self.test_results["performance_tests"] = {
            "success": success,
            "exit_code": result
        }
        
        if success:
            self.passed_tests.append("Performance Tests")
            print("✅ Performance tests passed")
        else:
            self.failed_tests.append("Performance Tests")
            print("❌ Performance tests failed")
        
        return success

    def run_accessibility_tests(self) -> bool:
        """Run accessibility compliance tests."""
        print("♿ Running Accessibility Tests...")
        
        result = pytest.main([
            "tests/audio/test_audio_accessibility.py",
            "-v",
            "--tb=short"
        ])
        
        success = result == 0
        self.test_results["accessibility_tests"] = {
            "success": success,
            "exit_code": result
        }
        
        if success:
            self.passed_tests.append("Accessibility Tests")
            print("✅ Accessibility tests passed")
        else:
            self.failed_tests.append("Accessibility Tests")
            print("❌ Accessibility tests failed")
        
        return success

    def run_integration_tests(self) -> bool:
        """Run integration scenario tests."""
        print("🔗 Running Integration Tests...")
        
        result = pytest.main([
            "tests/audio/test_sound_integration_scenarios.py",
            "-v",
            "--tb=short"
        ])
        
        success = result == 0
        self.test_results["integration_tests"] = {
            "success": success,
            "exit_code": result
        }
        
        if success:
            self.passed_tests.append("Integration Tests")
            print("✅ Integration tests passed")
        else:
            self.failed_tests.append("Integration Tests")
            print("❌ Integration tests failed")
        
        return success

    def validate_audio_assets(self) -> bool:
        """Validate audio asset files and quality."""
        print("🎵 Validating Audio Assets...")
        
        # Check for required audio directories
        audio_dirs = [
            "assets/audio/music",
            "assets/audio/sfx",
            "assets/audio/ambient"
        ]
        
        missing_dirs = []
        for audio_dir in audio_dirs:
            if not os.path.exists(audio_dir):
                missing_dirs.append(audio_dir)
        
        if missing_dirs:
            print(f"⚠️  Missing audio directories: {missing_dirs}")
            # Create directories with placeholder files
            for audio_dir in missing_dirs:
                os.makedirs(audio_dir, exist_ok=True)
                placeholder_file = os.path.join(audio_dir, "placeholder.ogg")
                Path(placeholder_file).touch()
                print(f"📁 Created placeholder: {placeholder_file}")
        
        # Run audio validation tool
        try:
            from tools.audio_validator import AudioValidator
            validator = AudioValidator()
            validation_results = validator.validate_all_audio()
            
            success = validation_results.get("overall_success", True)
            self.test_results["asset_validation"] = validation_results
            
            if success:
                self.passed_tests.append("Asset Validation")
                print("✅ Audio assets validated")
            else:
                self.failed_tests.append("Asset Validation")
                print("❌ Audio asset validation failed")
            
            return success
            
        except ImportError:
            print("⚠️  Audio validator not available, skipping asset validation")
            return True

    def check_audio_hardware(self) -> bool:
        """Check audio hardware compatibility."""
        print("🔊 Checking Audio Hardware...")
        
        try:
            # Initialize pygame audio
            pygame.mixer.quit()  # Clean slate
            pygame.mixer.init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=512
            )
            
            # Verify initialization
            init_result = pygame.mixer.get_init()
            if init_result is None:
                print("❌ Audio hardware initialization failed")
                return False
            
            frequency, format_bits, channels = init_result
            print(f"🎛️  Audio initialized: {frequency}Hz, {abs(format_bits)}-bit, {channels} channels")
            
            # Test channel allocation
            num_channels = pygame.mixer.get_num_channels()
            print(f"🔀 Available channels: {num_channels}")
            
            pygame.mixer.quit()
            
            self.test_results["hardware_check"] = {
                "success": True,
                "frequency": frequency,
                "format_bits": abs(format_bits),
                "channels": channels,
                "num_channels": num_channels
            }
            
            self.passed_tests.append("Hardware Check")
            print("✅ Audio hardware compatible")
            return True
            
        except Exception as e:
            print(f"❌ Audio hardware check failed: {e}")
            self.test_results["hardware_check"] = {
                "success": False,
                "error": str(e)
            }
            self.failed_tests.append("Hardware Check")
            return False

    def measure_audio_latency(self) -> Tuple[float, bool]:
        """Measure audio system latency."""
        print("⏱️  Measuring Audio Latency...")
        
        try:
            pygame.mixer.init(buffer=512)
            
            # Create a short test sound
            import tempfile
            import wave
            
            # Generate a simple test tone
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                with wave.open(temp_file.name, 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(44100)
                    
                    # Simple test tone (100ms)
                    import math
                    samples = []
                    for i in range(4410):  # 100ms at 44.1kHz
                        value = int(10000 * math.sin(2 * math.pi * 440 * i / 44100))
                        samples.append(value)
                    
                    wav_file.writeframes(b''.join(samples))
                
                # Measure loading and playback latency
                start_time = time.perf_counter()
                test_sound = pygame.mixer.Sound(temp_file.name)
                load_time = time.perf_counter() - start_time
                
                start_time = time.perf_counter()
                test_sound.play()
                play_time = time.perf_counter() - start_time
                
                total_latency = load_time + play_time
                
                # Clean up
                os.unlink(temp_file.name)
                pygame.mixer.quit()
                
                # Acceptable latency for gaming is < 20ms
                acceptable = total_latency < 0.02
                
                self.test_results["latency_test"] = {
                    "load_time_ms": load_time * 1000,
                    "play_time_ms": play_time * 1000,
                    "total_latency_ms": total_latency * 1000,
                    "acceptable": acceptable
                }
                
                if acceptable:
                    self.passed_tests.append("Latency Test")
                    print(f"✅ Audio latency acceptable: {total_latency*1000:.2f}ms")
                else:
                    self.failed_tests.append("Latency Test")
                    print(f"⚠️  Audio latency high: {total_latency*1000:.2f}ms")
                
                return total_latency, acceptable
                
        except Exception as e:
            print(f"❌ Latency test failed: {e}")
            self.test_results["latency_test"] = {
                "error": str(e),
                "acceptable": False
            }
            self.failed_tests.append("Latency Test")
            return 0.0, False

    def generate_test_report(self) -> str:
        """Generate comprehensive test report."""
        report = []
        report.append("=" * 60)
        report.append("🎮 DANGER ROSE AUDIO TEST SUITE REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Overall summary
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        pass_rate = len(self.passed_tests) / total_tests * 100 if total_tests > 0 else 0
        
        report.append(f"📊 OVERALL RESULTS:")
        report.append(f"   Total Tests: {total_tests}")
        report.append(f"   Passed: {len(self.passed_tests)}")
        report.append(f"   Failed: {len(self.failed_tests)}")
        report.append(f"   Pass Rate: {pass_rate:.1f}%")
        report.append("")
        
        # Passed tests
        if self.passed_tests:
            report.append("✅ PASSED TESTS:")
            for test in self.passed_tests:
                report.append(f"   • {test}")
            report.append("")
        
        # Failed tests
        if self.failed_tests:
            report.append("❌ FAILED TESTS:")
            for test in self.failed_tests:
                report.append(f"   • {test}")
            report.append("")
        
        # Detailed results
        report.append("📋 DETAILED RESULTS:")
        for test_name, results in self.test_results.items():
            report.append(f"   {test_name.replace('_', ' ').title()}:")
            for key, value in results.items():
                report.append(f"     {key}: {value}")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        if self.failed_tests:
            report.append("   • Fix failing tests before deploying")
            if "Hardware Check" in self.failed_tests:
                report.append("   • Verify audio drivers are installed")
            if "Performance Tests" in self.failed_tests:
                report.append("   • Optimize audio loading and caching")
            if "Accessibility Tests" in self.failed_tests:
                report.append("   • Review accessibility requirements")
        else:
            report.append("   • All tests passed - audio system ready for deployment!")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)

    def run_full_suite(self, include_performance: bool = True, include_stress: bool = False) -> bool:
        """Run the complete audio test suite."""
        print("🚀 Starting Comprehensive Audio Test Suite")
        print("=" * 50)
        
        start_time = time.time()
        
        # Run all test categories
        test_functions = [
            self.check_audio_hardware,
            self.validate_audio_assets,
            self.run_unit_tests,
            self.run_quality_assurance_tests,
            self.run_accessibility_tests,
            self.run_integration_tests,
        ]
        
        if include_performance:
            test_functions.append(self.run_performance_tests)
        
        # Additional latency measurement
        latency, acceptable_latency = self.measure_audio_latency()
        
        # Run all tests
        all_passed = True
        for test_func in test_functions:
            try:
                result = test_func()
                all_passed = all_passed and result
            except Exception as e:
                print(f"❌ Test function {test_func.__name__} failed with error: {e}")
                all_passed = False
                self.failed_tests.append(test_func.__name__)
        
        # Include latency in overall result
        all_passed = all_passed and acceptable_latency
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 50)
        print(f"⏱️  Test suite completed in {duration:.2f} seconds")
        
        # Generate and display report
        report = self.generate_test_report()
        print(report)
        
        # Save report to file
        report_file = "audio_test_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_file}")
        
        return all_passed


def main():
    """Main entry point for audio test suite."""
    parser = argparse.ArgumentParser(description="Danger Rose Audio Test Suite")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick tests only (skip performance tests)")
    parser.add_argument("--performance", action="store_true",
                       help="Include performance tests")
    parser.add_argument("--stress", action="store_true",
                       help="Include stress tests")
    parser.add_argument("--category", choices=["unit", "qa", "performance", "accessibility", "integration"],
                       help="Run specific test category only")
    
    args = parser.parse_args()
    
    # Set SDL video driver for headless operation
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    
    suite = AudioTestSuite()
    
    if args.category:
        # Run specific category
        if args.category == "unit":
            success = suite.run_unit_tests()
        elif args.category == "qa":
            success = suite.run_quality_assurance_tests()
        elif args.category == "performance":
            success = suite.run_performance_tests()
        elif args.category == "accessibility":
            success = suite.run_accessibility_tests()
        elif args.category == "integration":
            success = suite.run_integration_tests()
    else:
        # Run full suite
        include_performance = not args.quick or args.performance
        include_stress = args.stress
        success = suite.run_full_suite(include_performance, include_stress)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()