#!/usr/bin/env python3
"""
Simple OQE Integration Test - No Unicode characters for Windows compatibility
"""

import json
import os
import sys
import time
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if we can import the OQE framework"""
    print("Testing OQE Framework Imports...")
    try:
        from src.testing.traffic_simulation_framework import TrafficSimulationHooks, SimulationMetrics
        print("[PASS] OQE framework imports work")
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic OQE functionality"""
    print("Testing Basic OQE Functionality...")
    try:
        from src.testing.traffic_simulation_framework import TrafficSimulationHooks, SimulationMetrics
        
        # Test creation
        metrics = SimulationMetrics()
        hooks = TrafficSimulationHooks(metrics)
        
        # Test basic methods
        hooks.on_frame_start(60.0)
        hooks.on_traffic_scan(2.5)
        hooks.on_lane_change_complete("aggressive")
        
        # Test report generation
        report = hooks.generate_session_report("test", 10.0)
        
        if "session_info" in report and "oqe_evidence" in report:
            print("[PASS] Basic OQE functionality works")
            return True
        else:
            print("[FAIL] Report structure incorrect")
            return False
            
    except Exception as e:
        print(f"[FAIL] Basic functionality error: {e}")
        return False

def test_drive_integration():
    """Test Drive scene integration"""
    print("Testing Drive Scene Integration...")
    try:
        # Check if the Drive scene file has the right components
        drive_file = Path("src/scenes/drive.py")
        if not drive_file.exists():
            print("[FAIL] Drive scene file not found")
            return False
            
        with open(drive_file, 'r') as f:
            content = f.read()
        
        # Check for key components
        checks = [
            ("OQE import", "from src.testing.traffic_simulation_framework import"),
            ("OQE metrics init", "self.oqe_metrics = SimulationMetrics()"),
            ("Traffic hooks init", "self.traffic_hooks = TrafficSimulationHooks"),
            ("Frame hook", "self.traffic_hooks.on_frame_start"),
            ("Scan hook", "self.traffic_hooks.on_traffic_scan"),
            ("Lane change hook", "self.traffic_hooks.on_lane_change_complete"),
            ("F11 key", "pygame.K_F11"),
            ("F10 key", "pygame.K_F10"),
            ("F9 key", "pygame.K_F9"),
        ]
        
        all_good = True
        for name, pattern in checks:
            if pattern in content:
                print(f"[PASS] Found {name}")
            else:
                print(f"[FAIL] Missing {name}")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"[FAIL] Drive integration test error: {e}")
        return False

def find_missing_connections():
    """Find what's missing for game logger integration"""
    print("Analyzing Missing Game Logger Connections...")
    
    try:
        drive_file = Path("src/scenes/drive.py")
        if not drive_file.exists():
            print("[FAIL] Drive scene file not found")
            return False
            
        with open(drive_file, 'r') as f:
            content = f.read()
        
        # Look for game logger usage
        game_logger_uses = content.count("game_logger.log_system_event")
        print(f"Found {game_logger_uses} game_logger.log_system_event calls")
        
        # Check if any are OQE-related
        if "oqe" in content.lower() and "game_logger" in content:
            print("[INFO] Some OQE + game_logger integration exists")
        else:
            print("[MISSING] No OQE events logged to game_logger")
        
        # Check F9 export function
        f9_section_start = content.find("pygame.K_F9")
        if f9_section_start != -1:
            f9_section = content[f9_section_start:f9_section_start + 1000]
            if "game_logger" in f9_section:
                print("[PASS] F9 export connects to game_logger")
            else:
                print("[MISSING] F9 export doesn't log to game_logger")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Analysis error: {e}")
        return False

def main():
    print("OQE Logging System Validation")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_basic_functionality, 
        test_drive_integration,
        find_missing_connections
    ]
    
    results = []
    for test in tests:
        print()
        result = test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed < total:
        print("\nISSUES FOUND:")
        print("- OQE hooks are implemented but not connected to game_logger")
        print("- F9 export saves to files but not to game logs")
        print("- Need to add game_logger.log_system_event calls in OQE hooks")
    else:
        print("All tests passed!")
    
    return passed == total

if __name__ == "__main__":
    main()