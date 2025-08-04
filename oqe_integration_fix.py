#!/usr/bin/env python3
"""
OQE Integration Fix for Drive Scene
==================================

This script contains the exact code modifications needed to make OQE logging 
work correctly in the Drive scene.

Based on analysis:
1. OQE framework imports and initialization ✓
2. Basic traffic hooks exist ✓  
3. Helper method added ✓
4. Missing: F-key handlers for OQE session management
5. Missing: Traffic scan and lane change logging
6. Missing: F9 export integration with game logger
"""

def get_missing_event_handler():
    """Returns the missing event handler code for Drive scene"""
    return '''
    def handle_event(self, event) -> Optional[str]:
        """Handle input events."""
        # Handle scene-specific events first
        if self.state == self.STATE_MUSIC_SELECTION:
            result = self.music_selector.handle_event(event)
            if result == "MUSIC_SELECTED":
                selected_music = self.music_selector.get_selected_track()
                if selected_music:
                    self._start_racing_with_music(selected_music)
                return None
            elif result == "EXIT":
                return SCENE_HUB_WORLD
                
        elif self.state == self.STATE_VEHICLE_SELECTION:
            result = self.vehicle_selector.handle_event(event)
            if result == "VEHICLE_SELECTED":
                selected_vehicle = self.vehicle_selector.get_selected_vehicle()
                if selected_vehicle:
                    self._start_racing_with_vehicle(selected_vehicle)
                return None
            elif result == "EXIT":
                return SCENE_HUB_WORLD
        
        # Handle all keyboard events
        if event.type == pygame.KEYDOWN:
            # OQE Testing Controls (F11/F10/F9)
            if event.key == pygame.K_F11:
                # Toggle OQE baseline mode (AI disabled for testing)
                self.oqe_baseline_mode = not self.oqe_baseline_mode
                mode_name = "BASELINE (AI disabled)" if self.oqe_baseline_mode else "NORMAL (AI enabled)"
                print(f"OQE Testing Mode: {mode_name}")
                # Log mode change
                self._log_oqe_event("mode_change", {
                    "new_mode": "baseline" if self.oqe_baseline_mode else "ai_enabled",
                    "timestamp": time.time()
                })
                
            elif event.key == pygame.K_F10:
                # Start new OQE session
                if hasattr(self, 'traffic_hooks'):
                    self.oqe_session_start_time = time.time()
                    self.oqe_metrics = SimulationMetrics()  # Reset metrics
                    self.traffic_hooks.metrics = self.oqe_metrics
                    self.oqe_frame_count = 0  # Reset frame counter
                    session_type = "baseline" if self.oqe_baseline_mode else "ai_enabled"
                    print(f"OQE Session Started: {session_type}")
                    # Log session start
                    self._log_oqe_event("session_start", {
                        "session_type": session_type,
                        "timestamp": self.oqe_session_start_time,
                        "baseline_mode": self.oqe_baseline_mode
                    })
                    
            elif event.key == pygame.K_F9:
                # Export current OQE session
                if hasattr(self, 'traffic_hooks') and self.oqe_session_start_time:
                    session_duration = time.time() - self.oqe_session_start_time
                    session_type = "baseline" if self.oqe_baseline_mode else "ai_enabled"
                    report = self.traffic_hooks.generate_session_report(session_type, session_duration)
                    
                    # Save report to file (existing functionality)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"oqe_session_{session_type}_{timestamp}.json"
                    os.makedirs("pipeline_reports", exist_ok=True)
                    filepath = os.path.join("pipeline_reports", filename)
                    
                    with open(filepath, 'w') as f:
                        json.dump(report, f, indent=2)
                    
                    print(f"OQE Session Report saved: {filepath}")
                    print(f"Duration: {session_duration:.1f}s, Passes: {self.oqe_metrics.total_passes_completed}")
                    
                    # NEW: Also log the complete report to game logger
                    self._log_oqe_event("session_export", {
                        "session_type": session_type,
                        "duration_seconds": session_duration,
                        "total_passes": self.oqe_metrics.total_passes_completed,
                        "avg_fps": sum(self.oqe_metrics.fps_samples) / len(self.oqe_metrics.fps_samples) if self.oqe_metrics.fps_samples else 0,
                        "avg_scan_time_ms": sum(self.oqe_metrics.scan_times_ms) / len(self.oqe_metrics.scan_times_ms) if self.oqe_metrics.scan_times_ms else 0,
                        "file_saved": filepath,
                        "report_summary": report.get("summary", {}),
                        "pass_criteria": report["oqe_evidence"]["pass_criteria"]
                    })
                    
                    # Reset session
                    self.oqe_session_start_time = None
                else:
                    print("No active OQE session to export. Press F10 to start a session first.")
            
            # Other key handlers...
            elif event.key == pygame.K_ESCAPE:
                if self.state == self.STATE_RACING:
                    return SCENE_HUB_WORLD
                elif self.state in [self.STATE_MUSIC_SELECTION, self.STATE_VEHICLE_SELECTION]:
                    return SCENE_HUB_WORLD
                    
            elif event.key == pygame.K_b:
                # Toggle BMP overlay
                self.bmp_overlay_visible = not self.bmp_overlay_visible
                print(f"BMP overlay {'enabled' if self.bmp_overlay_visible else 'disabled'}")
        
        return None
'''


def get_traffic_scan_integration():
    """Returns code to integrate traffic scanning with OQE logging"""
    return '''
    # Add this to _update_npc_ai method where traffic scanning happens:
    
    def _update_npc_ai_with_oqe(self, car: NPCCar, dt: float):
        """Update NPC car AI behavior with OQE logging integration."""
        # Update lane change timer
        car.lane_change_timer += dt
        
        # Skip AI for crashed cars
        if car.ai_state == "crashed" or car.ai_state == "stopped":
            return
            
        # Perform traffic scan with timing
        scan_start_time = time.time()
        scan = self.traffic_awareness.scan_surrounding_traffic(car, self.npc_cars)
        scan_time_ms = (time.time() - scan_start_time) * 1000
        
        # OQE Hook: Traffic scan timing
        if hasattr(self, 'traffic_hooks'):
            self.traffic_hooks.on_traffic_scan(scan_time_ms)
            
            # Log to game logger (sample every 10th scan to avoid spam)
            if random.randint(1, 10) == 1:  
                self._log_oqe_event("traffic_scan", {
                    "scan_time_ms": scan_time_ms,
                    "cars_detected": len([c for c in [scan.ahead_same_lane, scan.behind_same_lane, scan.ahead_left_lane, scan.ahead_right_lane] if c]),
                    "car_personality": car.personality.value,
                    "scan_quality": "normal" if scan_time_ms < 5.0 else "slow"
                })
        
        # Continue with existing AI logic...
        # (Rest of existing _update_npc_ai code)
'''


def get_lane_change_integration():
    """Returns code to integrate lane change completion with OQE logging"""
    return '''
    # Add this where lane changes complete in _update_npc_ai:
    
    # When a lane change completes:
    if car.ai_state == "changing_lanes" and car.lane_change_progress >= 1.0:
        # Lane change completed
        car.ai_state = "cruising"
        car.lane_change_progress = 0.0
        previous_lane = getattr(car, 'previous_lane', car.road_pos.lane)
        
        # OQE Hook: Lane change completed
        if hasattr(self, 'traffic_hooks'):
            self.traffic_hooks.on_lane_change_complete(car.personality.value)
            
            # Log to game logger
            self._log_oqe_event("lane_change_complete", {
                "personality": car.personality.value,
                "lane_from": previous_lane,
                "lane_to": car.road_pos.lane,
                "duration_ms": getattr(car, 'lane_change_start_time', 0),
                "success": True
            })
'''


def get_complete_integration_summary():
    """Returns summary of all required changes"""
    return '''
COMPLETE OQE LOGGING INTEGRATION SUMMARY
=======================================

FILES TO MODIFY:
1. src/scenes/drive.py

CHANGES NEEDED:

1. ✓ DONE: OQE framework import (line 39)
2. ✓ DONE: OQE initialization (lines 309-321)  
3. ✓ DONE: _log_oqe_event helper method (lines 509-512)
4. ✓ DONE: Performance sampling in _update_racing (lines 528-538)

5. TODO: Add handle_event method with F11/F10/F9 handlers
6. TODO: Add traffic scan OQE logging to _update_npc_ai
7. TODO: Add lane change completion OQE logging
8. TODO: Add missing imports (time, random if not present)

TESTING PROCEDURE:
1. Run game and enter Drive scene
2. Press F10 to start OQE session
3. Drive for 30+ seconds to generate traffic
4. Press F9 to export session
5. Check both:
   - File saved to pipeline_reports/
   - Events logged to game logger

EXPECTED GAME LOGGER EVENTS:
- oqe_traffic.mode_change (when pressing F11)
- oqe_traffic.session_start (when pressing F10)  
- oqe_traffic.performance_sample (every 5 seconds)
- oqe_traffic.traffic_scan (sample of scans)
- oqe_traffic.lane_change_complete (when cars change lanes)
- oqe_traffic.session_export (when pressing F9)

This will make OQE events visible in game logs while preserving
the existing file-based reporting system.
'''


def main():
    print("OQE Integration Fix Generator")
    print("=" * 50)
    
    print("1. Event Handler Code:")
    print(get_missing_event_handler())
    
    print("\n2. Traffic Scan Integration:")
    print(get_traffic_scan_integration())
    
    print("\n3. Lane Change Integration:")
    print(get_lane_change_integration())
    
    print("\n4. Complete Integration Summary:")
    print(get_complete_integration_summary())


if __name__ == "__main__":
    main()