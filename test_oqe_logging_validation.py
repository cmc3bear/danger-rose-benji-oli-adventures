#!/usr/bin/env python3
"""
OQE Logging System Validation Test
==================================

This test validates that the OQE (Objective Qualified Evidence) system
is properly integrated with the Drive scene and game state logger.

Test Areas:
1. OQE hook integration verification
2. F11/F10/F9 key bindings functionality
3. Game state logger connection
4. Metrics collection and persistence
5. Report generation validation
"""

import json
import os
import sys
import time
import tempfile
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_oqe_framework_imports():
    """Test 1: Verify OQE framework can be imported properly"""
    print("Test 1: OQE Framework Import Validation")
    print("=" * 50)
    
    try:
        from src.testing.traffic_simulation_framework import TrafficSimulationHooks, SimulationMetrics
        print("[PASS] Successfully imported TrafficSimulationHooks and SimulationMetrics")
        
        # Test metric creation
        metrics = SimulationMetrics()
        hooks = TrafficSimulationHooks(metrics)
        print("✅ Successfully created OQE metric and hook objects")
        
        # Test basic hook functionality
        hooks.on_frame_start(60.0)
        hooks.on_traffic_scan(2.5)
        hooks.on_lane_change_complete("aggressive")
        
        print("✅ Basic hook method calls work correctly")
        
        # Test report generation
        report = hooks.generate_session_report("test", 10.0)
        assert "session_info" in report
        assert "oqe_evidence" in report
        print("✅ Session report generation works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import or initialize OQE framework: {e}")
        return False


def test_drive_scene_oqe_integration():
    """Test 2: Verify Drive scene OQE integration without running the game"""
    print("\nTest 2: Drive Scene OQE Integration")
    print("=" * 50)
    
    try:
        # We can't easily test the full Drive scene without pygame display
        # But we can verify the import structure and key components
        
        from src.scenes.drive import DriveScene
        print("✅ Drive scene imports successfully")
        
        # Check if the necessary imports are present in the file
        drive_file = Path("src/scenes/drive.py")
        if not drive_file.exists():
            print("❌ Drive scene file not found")
            return False
            
        with open(drive_file, 'r') as f:
            content = f.read()
            
        # Check for required imports
        required_imports = [
            "from src.testing.traffic_simulation_framework import TrafficSimulationHooks, SimulationMetrics",
            "from datetime import datetime"
        ]
        
        for import_stmt in required_imports:
            if import_stmt in content:
                print(f"✅ Found required import: {import_stmt}")
            else:
                print(f"❌ Missing import: {import_stmt}")
                return False
        
        # Check for OQE initialization code
        oqe_patterns = [
            "self.oqe_metrics = SimulationMetrics()",
            "self.traffic_hooks = TrafficSimulationHooks(self.oqe_metrics)",
            "self.oqe_baseline_mode = False",
            "self.oqe_session_start_time = None"
        ]
        
        for pattern in oqe_patterns:
            if pattern in content:
                print(f"✅ Found OQE initialization: {pattern}")
            else:
                print(f"❌ Missing OQE initialization: {pattern}")
                return False
        
        # Check for hook integration points
        hook_patterns = [
            "self.traffic_hooks.on_frame_start(fps)",
            "self.traffic_hooks.on_traffic_scan(scan_time_ms)",
            "self.traffic_hooks.on_lane_change_complete("
        ]
        
        for pattern in hook_patterns:
            if pattern in content:
                print(f"✅ Found hook integration: {pattern}")
            else:
                print(f"❌ Missing hook integration: {pattern}")
                return False
                
        # Check for F-key bindings
        fkey_patterns = [
            "pygame.K_F11",
            "pygame.K_F10", 
            "pygame.K_F9"
        ]
        
        for pattern in fkey_patterns:
            if pattern in content:
                print(f"✅ Found F-key binding: {pattern}")
            else:
                print(f"❌ Missing F-key binding: {pattern}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Drive scene OQE integration test failed: {e}")
        return False


def test_oqe_metrics_functionality():
    """Test 3: Verify OQE metrics collection and evidence generation"""
    print("\nTest 3: OQE Metrics Functionality")
    print("=" * 50)
    
    try:
        from src.testing.traffic_simulation_framework import SimulationMetrics, TrafficSimulationHooks
        
        # Create a realistic test scenario
        metrics = SimulationMetrics()
        hooks = TrafficSimulationHooks(metrics)
        
        # Simulate a realistic 30-second traffic scenario
        print("Simulating 30-second traffic scenario...")
        
        # Simulate frames (30 FPS for 30 seconds = 900 frames)
        for frame in range(900):
            # Every frame gets FPS tracking
            if frame % 60 == 0:  # Every second
                hooks.on_frame_start(58.0 + (frame % 10))  # Simulate FPS variation
            
            # Every 10 frames, simulate traffic scan
            if frame % 10 == 0:
                scan_time = 2.0 + (frame % 5) * 0.5  # 2-4.5ms scan times
                hooks.on_traffic_scan(scan_time)
            
            # Every 180 frames (6 seconds), simulate lane change
            if frame % 180 == 0 and frame > 0:
                personality = ["aggressive", "cautious", "normal"][frame // 180 % 3]
                hooks.on_lane_change_complete(personality)
        
        # Add some specific events
        hooks.on_emergency_evasion(True, True)  # Successful evasion
        hooks.on_emergency_evasion(True, False)  # Failed evasion
        hooks.on_congestion_detected(1, 4)  # Congestion in lane 1
        
        # Simulate car updates for lane usage
        for _ in range(100):
            hooks.on_car_update(0, 50.0)  # Lane 0, 50 km/h
            hooks.on_car_update(1, 55.0)  # Lane 1, 55 km/h
            hooks.on_car_update(2, 45.0)  # Lane 2, 45 km/h
        
        # Generate session report
        report = hooks.generate_session_report("test_scenario", 30.0)
        
        # Validate report structure
        assert "session_info" in report
        assert "oqe_evidence" in report
        assert "raw_metrics" in report
        assert "summary" in report
        
        print("✅ Session report structure is valid")
        
        # Check OQE evidence structure
        evidence = report["oqe_evidence"]
        assert "evidence_type" in evidence
        assert "measurements" in evidence
        assert "pass_criteria" in evidence
        
        print("✅ OQE evidence structure is valid")
        
        # Validate some metrics
        measurements = evidence["measurements"]
        assert measurements["total_passes"] > 0
        assert len(report["raw_metrics"]["fps_samples"]) > 0
        assert len(report["raw_metrics"]["scan_times_ms"]) > 0
        
        print(f"✅ Collected {measurements['total_passes']} passes")
        print(f"✅ Collected {len(report['raw_metrics']['fps_samples'])} FPS samples")
        print(f"✅ Collected {len(report['raw_metrics']['scan_times_ms'])} scan time samples")
        
        # Check pass criteria evaluation
        pass_criteria = evidence["pass_criteria"]
        print(f"✅ Pass criteria evaluated: {sum(pass_criteria.values())}/{len(pass_criteria)} passed")
        
        return True
        
    except Exception as e:
        print(f"❌ OQE metrics functionality test failed: {e}")
        return False


def test_report_file_generation():
    """Test 4: Verify OQE report file generation matches expected format"""
    print("\nTest 4: OQE Report File Generation")
    print("=" * 50)
    
    try:
        from src.testing.traffic_simulation_framework import SimulationMetrics, TrafficSimulationHooks
        
        # Create test data
        metrics = SimulationMetrics()
        hooks = TrafficSimulationHooks(metrics)
        
        # Add some test data
        for i in range(10):
            hooks.on_frame_start(60.0)
            hooks.on_traffic_scan(3.0)
            if i % 3 == 0:
                hooks.on_lane_change_complete("normal")
        
        # Generate report
        report = hooks.generate_session_report("baseline", 15.0)
        
        # Test file saving (mimicking F9 behavior)
        with tempfile.TemporaryDirectory() as temp_dir:
            timestamp = "20240804_120000"  # Fixed timestamp for testing
            filename = f"oqe_session_baseline_{timestamp}.json"
            filepath = os.path.join(temp_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"✅ Successfully saved report to: {filename}")
            
            # Verify file exists and is valid JSON
            assert os.path.exists(filepath)
            
            with open(filepath, 'r') as f:
                loaded_report = json.load(f)
            
            # Verify the loaded report matches the original
            assert loaded_report["session_info"]["session_type"] == "baseline"
            assert loaded_report["session_info"]["duration_seconds"] == 15.0
            
            print("✅ Report file is valid JSON and contains correct data")
            
            # Check file size (should be reasonable)
            file_size = os.path.getsize(filepath)
            print(f"✅ Report file size: {file_size} bytes")
            
            if file_size > 100000:  # 100KB
                print("⚠️  Warning: Report file is quite large, consider data reduction")
            
        return True
        
    except Exception as e:
        print(f"❌ Report file generation test failed: {e}")
        return False


def test_game_logger_integration_potential():
    """Test 5: Verify potential for game logger integration"""
    print("\nTest 5: Game Logger Integration Potential")
    print("=" * 50)
    
    try:
        from src.systems.game_state_logger import GameStateLogger
        
        # Test game logger initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = GameStateLogger(
                log_dir=temp_dir,
                session_id="test_oqe_session"
            )
            
            print("✅ Game state logger initialized successfully")
            
            # Test OQE-specific logging patterns
            logger.log_system_event("oqe", "session_start", {
                "session_type": "baseline",
                "test_duration": 120.0
            })
            
            logger.log_system_event("oqe", "traffic_scan", {
                "scan_time_ms": 2.5,
                "cars_detected": 3
            })
            
            logger.log_system_event("oqe", "lane_change", {
                "personality": "aggressive",
                "success": True
            })
            
            logger.log_system_event("oqe", "session_end", {
                "total_passes": 15,
                "avg_fps": 58.5,
                "criteria_passed": True
            })
            
            print("✅ OQE events logged successfully")
            
            # Test session export
            summary = logger.export_session_summary()
            assert "system_events" in summary
            
            # Check if OQE events are in the summary
            oqe_events = [e for e in summary["system_events"] if e.get("system") == "oqe"]
            assert len(oqe_events) == 4
            
            print(f"✅ Found {len(oqe_events)} OQE events in session summary")
            
            logger.end_session()
            
        return True
        
    except Exception as e:
        print(f"❌ Game logger integration test failed: {e}")
        return False


def identify_missing_integrations():
    """Test 6: Identify missing integrations between OQE and game logger"""
    print("\nTest 6: Missing Integration Analysis")
    print("=" * 50)
    
    issues_found = []
    
    # Check if Drive scene connects OQE to game logger
    drive_file = Path("src/scenes/drive.py")
    if drive_file.exists():
        with open(drive_file, 'r') as f:
            content = f.read()
        
        # Check for game logger integration in OQE contexts
        if "self.scene_manager.game_logger.log_system_event" not in content:
            issues_found.append("Drive scene uses game_logger.log_system_event but only for road_geometry")
        
        # Check if F9 export connects to game logger
        if "F9" in content and "game_logger" not in content[content.find("F9"):content.find("F9")+500]:
            issues_found.append("F9 OQE export doesn't integrate with game_logger")
        
        # Check if OQE hooks call game logger
        if "traffic_hooks.on_" in content and "game_logger" not in content:
            issues_found.append("OQE hooks don't trigger game_logger events")
    
    # Analysis
    print("Missing Integration Analysis:")
    print("-" * 30)
    
    if not issues_found:
        print("✅ No obvious integration issues found")
        return True
    else:
        for i, issue in enumerate(issues_found, 1):
            print(f"❌ Issue {i}: {issue}")
        
        print(f"\n🔧 Found {len(issues_found)} integration issues that need fixing")
        return False


def main():
    """Run all OQE logging validation tests"""
    print("OQE Logging System Validation")
    print("=" * 60)
    print("Testing OQE integration in Danger Rose Drive scene")
    print("=" * 60)
    
    tests = [
        test_oqe_framework_imports,
        test_drive_scene_oqe_integration,
        test_oqe_metrics_functionality,
        test_report_file_generation,
        test_game_logger_integration_potential,
        identify_missing_integrations
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! OQE logging system is properly integrated.")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Issues need to be addressed.")
        
        print("\nNext Steps:")
        print("1. Fix missing imports or initialization")
        print("2. Connect OQE hooks to game_logger.log_system_event()")
        print("3. Ensure F9 export saves to game logs as well as files")
        print("4. Test with actual Drive scene execution")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)