#!/usr/bin/env python3
"""
Simple OQE Validation - Final Check
"""

import json
import sys
import tempfile
import time
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    print("OQE Integration - Final Validation")
    print("=" * 50)
    
    # Test 1: Check Drive scene integration
    print("1. Checking Drive Scene Integration...")
    
    drive_file = Path("src/scenes/drive.py")
    with open(drive_file, 'r') as f:
        content = f.read()
    
    key_features = [
        "_log_oqe_event",
        "pygame.K_F11",
        "pygame.K_F10", 
        "pygame.K_F9",
        'log_system_event("oqe_traffic"',
        "performance_sample",
        "session_export"
    ]
    
    all_present = True
    for feature in key_features:
        if feature in content:
            print(f"   [OK] {feature}")
        else:
            print(f"   [MISSING] {feature}")
            all_present = False
    
    # Test 2: Check OQE framework functionality
    print("\n2. Testing OQE Framework...")
    
    try:
        from src.testing.traffic_simulation_framework import SimulationMetrics, TrafficSimulationHooks
        
        metrics = SimulationMetrics()
        hooks = TrafficSimulationHooks(metrics)
        
        # Quick test
        hooks.on_frame_start(60.0)
        hooks.on_traffic_scan(2.5)
        hooks.on_lane_change_complete("aggressive")
        
        report = hooks.generate_session_report("test", 10.0)
        
        if "oqe_evidence" in report and report["oqe_evidence"]["measurements"]["total_passes"] > 0:
            print("   [OK] OQE framework working")
            framework_ok = True
        else:
            print("   [ERROR] OQE framework issues")
            framework_ok = False
            
    except Exception as e:
        print(f"   [ERROR] OQE framework failed: {e}")
        framework_ok = False
    
    # Test 3: Check game logger basic functionality
    print("\n3. Testing Game Logger...")
    
    try:
        from src.systems.game_state_logger import GameStateLogger
        
        # Use correct API
        logger = GameStateLogger(str(Path.cwd()), enable_live_overlay=False)
        
        # Test basic logging
        logger.log_system_event("oqe_traffic", "test_event", {"test": True})
        
        # End session to process events
        logger.end_session()
        print("   [OK] Game logger working")
        logger_ok = True
        
    except Exception as e:
        print(f"   [ERROR] Game logger failed: {e}")
        logger_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    if all_present and framework_ok and logger_ok:
        print("STATUS: SUCCESS - OQE logging integration is COMPLETE")
        print()
        print("Key Features Implemented:")
        print("- F11/F10/F9 key handlers with game logger integration")
        print("- Performance sampling every 5 seconds") 
        print("- Session export with dual logging (file + game logger)")
        print("- OQE metrics collection and reporting")
        print()
        print("Testing Instructions:")
        print("1. Run: make run")
        print("2. Navigate to Drive scene")
        print("3. Press F10 to start OQE session")
        print("4. Drive for 30+ seconds")
        print("5. Press F9 to export session")
        print("6. Check pipeline_reports/ for files")
        print("7. Check game logs for oqe_traffic events")
        
        return True
    else:
        print("STATUS: ISSUES DETECTED")
        print("- Drive integration:", "OK" if all_present else "MISSING FEATURES")
        print("- OQE framework:", "OK" if framework_ok else "ERROR")
        print("- Game logger:", "OK" if logger_ok else "ERROR")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)