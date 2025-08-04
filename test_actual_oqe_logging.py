#!/usr/bin/env python3
"""
Test actual OQE logging behavior by running a minimal Drive scene simulation
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_oqe_metrics_collection():
    """Test that OQE metrics are being collected properly"""
    print("Testing OQE Metrics Collection...")
    
    try:
        from src.testing.traffic_simulation_framework import TrafficSimulationHooks, SimulationMetrics
        
        # Create fresh metrics
        metrics = SimulationMetrics()
        hooks = TrafficSimulationHooks(metrics)
        
        print(f"Initial state - Passes: {metrics.total_passes_completed}")
        print(f"Initial state - FPS samples: {len(metrics.fps_samples)}")
        print(f"Initial state - Scan times: {len(metrics.scan_times_ms)}")
        
        # Simulate some traffic activity
        print("Simulating traffic activity...")
        
        # Frame updates (every 60 frames = 1 second of samples)
        for i in range(120):  # 2 seconds worth
            if i % 60 == 0:
                hooks.on_frame_start(58.5)
        
        # Traffic scans
        for i in range(20):
            hooks.on_traffic_scan(2.5 + i * 0.1)  # Increasing scan times
        
        # Lane changes
        personalities = ["aggressive", "cautious", "normal"]
        for i in range(5):
            hooks.on_lane_change_complete(personalities[i % 3])
        
        print(f"After simulation - Passes: {metrics.total_passes_completed}")
        print(f"After simulation - FPS samples: {len(metrics.fps_samples)}")
        print(f"After simulation - Scan times: {len(metrics.scan_times_ms)}")
        
        # Generate report
        report = hooks.generate_session_report("test_logging", 30.0)
        
        print("Generated report keys:", list(report.keys()))
        print("OQE evidence keys:", list(report["oqe_evidence"].keys()))
        
        measurements = report["oqe_evidence"]["measurements"]
        print(f"Report total passes: {measurements['total_passes']}")
        print(f"Report avg FPS: {measurements['avg_fps']}")
        print(f"Report avg scan time: {measurements['avg_scan_time_ms']}")
        
        if measurements["total_passes"] > 0:
            print("[PASS] OQE metrics collection is working")
            return True, report
        else:
            print("[FAIL] No passes recorded")
            return False, None
            
    except Exception as e:
        print(f"[FAIL] Metrics collection error: {e}")
        return False, None

def test_game_logger_oqe_integration():
    """Test if we can log OQE events to game logger"""
    print("Testing Game Logger OQE Integration...")
    
    try:
        from src.systems.game_state_logger import GameStateLogger
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create game logger
            logger = GameStateLogger(
                log_dir=temp_dir,
                session_id="oqe_test_session"
            )
            
            # Log some OQE-style events
            logger.log_system_event("oqe_traffic", "session_start", {
                "session_type": "baseline",
                "timestamp": time.time()
            })
            
            logger.log_system_event("oqe_traffic", "frame_update", {
                "fps": 58.5,
                "frame_time_ms": 16.8
            })
            
            logger.log_system_event("oqe_traffic", "traffic_scan", {
                "scan_time_ms": 2.5,
                "cars_detected": 3,
                "scan_result": "normal"
            })
            
            logger.log_system_event("oqe_traffic", "lane_change_complete", {
                "personality": "aggressive",
                "duration_ms": 2500,
                "success": True
            })
            
            logger.log_system_event("oqe_traffic", "session_end", {
                "total_passes": 5,
                "avg_fps": 58.2,
                "session_duration": 30.0
            })
            
            # Export session
            summary = logger.export_session_summary()
            
            # Find OQE events
            oqe_events = [e for e in summary["system_events"] 
                         if e.get("system", "").startswith("oqe")]
            
            print(f"Found {len(oqe_events)} OQE events in game log")
            
            for event in oqe_events:
                print(f"  - {event['system']}: {event['event']}")
            
            logger.end_session()
            
            if len(oqe_events) > 0:
                print("[PASS] Game logger can handle OQE events")
                return True
            else:
                print("[FAIL] No OQE events found in game log")
                return False
                
    except Exception as e:
        print(f"[FAIL] Game logger integration error: {e}")
        return False

def create_oqe_logging_fix():
    """Create the code that fixes OQE -> game logger integration"""
    print("Creating OQE Logging Integration Fix...")
    
    fix_code = '''
# Add this to Drive scene __init__ method after OQE initialization:
# Store reference to game logger for OQE events
self.oqe_game_logger = None

# Add this method to Drive scene class:
def _log_oqe_event(self, event_type: str, data: dict):
    """Log OQE events to both console and game logger"""
    if hasattr(self.scene_manager, 'game_logger') and self.scene_manager.game_logger:
        self.scene_manager.game_logger.log_system_event("oqe_traffic", event_type, data)

# Modify traffic hooks to include game logger calls:

# In _update_racing method after self.traffic_hooks.on_frame_start(fps):
if self.frame_count % 300 == 0:  # Every 5 seconds
    self._log_oqe_event("performance_sample", {
        "fps": fps,
        "frame_time_ms": frame_time * 1000,
        "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
    })

# In traffic scan areas after self.traffic_hooks.on_traffic_scan(scan_time_ms):
self._log_oqe_event("traffic_scan", {
    "scan_time_ms": scan_time_ms,
    "cars_scanned": len(self.npc_cars),
    "scan_quality": "normal" if scan_time_ms < 5.0 else "slow"
})

# In lane change completion after self.traffic_hooks.on_lane_change_complete:
self._log_oqe_event("lane_change_complete", {
    "personality": car_personality,
    "lane_from": getattr(car, 'previous_lane', 0),
    "lane_to": car.road_pos.lane,
    "duration_ms": getattr(car, 'lane_change_duration', 0) * 1000
})

# In F9 export handler after json.dump(report, f, indent=2):
# Also log the complete report to game logger
self._log_oqe_event("session_export", {
    "session_type": session_type,
    "duration_seconds": session_duration,
    "total_passes": self.oqe_metrics.total_passes_completed,
    "avg_fps": sum(self.oqe_metrics.fps_samples) / len(self.oqe_metrics.fps_samples) if self.oqe_metrics.fps_samples else 0,
    "file_saved": filepath,
    "report_summary": report.get("summary", {})
})
'''
    
    print("Fix code generated. Key integration points:")
    print("1. Add _log_oqe_event helper method")
    print("2. Call it after each traffic_hooks method")
    print("3. Include F9 export in game logger")
    print("4. Sample performance data periodically")
    
    return fix_code

def main():
    print("OQE Logging Analysis")
    print("=" * 50)
    
    # Test current metrics collection
    success1, report = test_oqe_metrics_collection()
    print()
    
    # Test game logger capability
    success2 = test_game_logger_oqe_integration()
    print()
    
    # Generate fix
    fix_code = create_oqe_logging_fix()
    
    print("\n" + "=" * 50)
    print("DIAGNOSIS")
    print("=" * 50)
    
    if success1 and success2:
        print("ROOT CAUSE IDENTIFIED:")
        print("- OQE metrics collection is working correctly")
        print("- Game logger can handle OQE events")
        print("- MISSING: Connection between OQE hooks and game logger")
        print()
        print("SOLUTION:")
        print("- Add _log_oqe_event() method to Drive scene")
        print("- Call it after each traffic_hooks method call")
        print("- Include OQE session exports in game logs")
        print()
        print("This will make OQE events visible in game logs while")
        print("preserving the existing file export functionality.")
        
        return True
    else:
        print("Issues found with basic functionality")
        return False

if __name__ == "__main__":
    main()