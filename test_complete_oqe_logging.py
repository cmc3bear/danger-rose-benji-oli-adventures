#!/usr/bin/env python3
"""
Test script to validate complete OQE logging integration.
This verifies all hooks are properly connected and functional.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.testing.traffic_simulation_framework import SimulationMetrics, TrafficSimulationHooks
import json
from datetime import datetime

def test_complete_oqe_integration():
    """Test all OQE hooks are working properly."""
    print("Testing Complete OQE Integration...")
    print("=" * 50)
    
    # Create metrics and hooks
    metrics = SimulationMetrics()
    hooks = TrafficSimulationHooks(metrics)
    
    # Test 1: Frame tracking
    print("\n1. Testing Frame Tracking:")
    for i in range(3):
        hooks.on_frame_start(60.0)
    print(f"   [OK] Frame count: {hooks.frame_count}")
    
    # Test 2: Traffic scans
    print("\n2. Testing Traffic Scans:")
    hooks.on_traffic_scan(3.5)
    hooks.on_traffic_scan(4.2)
    print(f"   [OK] Scan times: {metrics.scan_times_ms}")
    
    # Test 3: Lane changes
    print("\n3. Testing Lane Changes:")
    hooks.on_lane_change_complete("Aggressive")
    hooks.on_lane_change_complete("Normal")
    print(f"   [OK] Total passes: {metrics.total_passes_completed}")
    print(f"   [OK] By personality: {metrics.passes_by_personality}")
    
    # Test 4: Collisions (NEW)
    print("\n4. Testing Collision Tracking:")
    initial_collisions = metrics.collisions_occurred
    hooks.on_collision()
    hooks.on_collision()
    print(f"   [OK] Collisions recorded: {metrics.collisions_occurred}")
    
    # Test 5: Emergency evasions (NEW)
    print("\n5. Testing Emergency Evasions:")
    hooks.on_emergency_evasion(attempted=True, successful=True)
    hooks.on_emergency_evasion(attempted=True, successful=False)
    hooks.on_emergency_evasion(attempted=True, successful=True)
    print(f"   [OK] Attempts: {metrics.emergency_evasions_attempted}")
    print(f"   [OK] Successful: {metrics.emergency_evasions_successful}")
    print(f"   [OK] Success rate: {(metrics.emergency_evasions_successful/metrics.emergency_evasions_attempted*100):.1f}%")
    
    # Test 6: Congestion detection (NEW)
    print("\n6. Testing Congestion Detection:")
    hooks.on_congestion_detected(lane=3, car_count=4)
    hooks.on_congestion_detected(lane=4, car_count=3)
    print(f"   [OK] Congestion events: {metrics.congestion_events}")
    
    # Test 7: Car updates (NEW)
    print("\n7. Testing Car Updates:")
    for lane in [3, 3, 4, 3, 4, 4]:
        hooks.on_car_update(lane, speed=0.8)
    print(f"   [OK] Lane usage: {metrics.lane_usage_counts}")
    print(f"   [OK] Speed samples collected: {len(metrics.speed_samples)}")
    
    # Test 8: Generate session report
    print("\n8. Testing Session Report Generation:")
    report = hooks.generate_session_report("test_complete", 60.0)
    evidence = report['oqe_evidence']
    
    print(f"\n   OQE Pass Criteria Results:")
    for criterion, passed in evidence['pass_criteria'].items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"   {status} {criterion}")
    
    # Verify all hooks are functional
    print("\n" + "=" * 50)
    print("COMPLETE OQE INTEGRATION TEST RESULTS:")
    print("=" * 50)
    
    all_hooks_working = True
    hook_status = {
        "Frame tracking": hooks.frame_count > 0,
        "Traffic scans": len(metrics.scan_times_ms) > 0,
        "Lane changes": metrics.total_passes_completed > 0,
        "Collisions": metrics.collisions_occurred > 0,
        "Emergency evasions": metrics.emergency_evasions_attempted > 0,
        "Congestion detection": metrics.congestion_events > 0,
        "Car updates": len(metrics.lane_usage_counts) > 0
    }
    
    for hook_name, is_working in hook_status.items():
        status = "[OK]" if is_working else "[FAIL]"
        print(f"{status} {hook_name}")
        if not is_working:
            all_hooks_working = False
    
    print("\n" + "=" * 50)
    if all_hooks_working:
        print("[SUCCESS] All OQE hooks are functional!")
        print("\nThe OQE logging system is now complete and ready for validation testing.")
    else:
        print("[FAILURE] Some hooks are not working properly!")
    
    return all_hooks_working

if __name__ == "__main__":
    test_complete_oqe_integration()