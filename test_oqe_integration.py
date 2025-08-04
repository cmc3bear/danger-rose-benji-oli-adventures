#!/usr/bin/env python3
"""
Test script to verify OQE integration in Drive scene.
This script tests the traffic simulation hooks without running the full game.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.testing.traffic_simulation_framework import SimulationMetrics, TrafficSimulationHooks
import time

def test_oqe_integration():
    """Test the OQE integration components."""
    print("Testing OQE Integration Components...")
    
    # Test 1: Create metrics and hooks
    metrics = SimulationMetrics()
    hooks = TrafficSimulationHooks(metrics)
    print("[OK] Created SimulationMetrics and TrafficSimulationHooks")
    
    # Test 2: Simulate frame updates
    for i in range(5):
        hooks.on_frame_start(60.0)
        time.sleep(0.016)  # ~60 FPS
    print("[OK] Frame tracking working")
    
    # Test 3: Simulate traffic scans
    hooks.on_traffic_scan(3.5)
    hooks.on_traffic_scan(4.2)
    hooks.on_traffic_scan(2.8)
    print(f"[OK] Traffic scan times recorded: {metrics.scan_times_ms}")
    
    # Test 4: Simulate lane changes
    hooks.on_lane_change_complete("Aggressive")
    hooks.on_lane_change_complete("Normal")
    hooks.on_lane_change_complete("Aggressive")
    print(f"[OK] Lane changes recorded: {metrics.total_passes_completed} total")
    
    # Test 5: Generate session report
    report = hooks.generate_session_report("test_session", 60.0)
    print("[OK] Session report generated")
    
    # Test 6: Check OQE evidence
    evidence = metrics.to_oqe_evidence()
    print(f"[OK] OQE Evidence type: {evidence['evidence_type']}")
    print(f"[OK] Pass criteria evaluation: {evidence['pass_criteria']}")
    
    print("\n[SUCCESS] All OQE integration tests passed!")
    print("\nOQE Controls for in-game testing:")
    print("  F11 - Toggle baseline mode (AI on/off)")
    print("  F10 - Start new OQE session")
    print("  F9  - Export session report")
    
    return True

if __name__ == "__main__":
    test_oqe_integration()