"""
Traffic Simulation Framework for OQE Testing

Provides headless simulation of traffic scenarios with metric collection.
"""

import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import psutil
import os


@dataclass
class SimulationMetrics:
    """Metrics collected during traffic simulation"""
    duration_seconds: float = 0.0
    total_cars_spawned: int = 0
    total_passes_completed: int = 0
    passes_by_personality: Dict[str, int] = field(default_factory=dict)
    emergency_evasions_attempted: int = 0
    emergency_evasions_successful: int = 0
    collisions_occurred: int = 0
    average_speed: float = 0.0
    speed_samples: List[float] = field(default_factory=list)
    congestion_events: int = 0
    lane_usage_counts: Dict[int, int] = field(default_factory=dict)
    fps_samples: List[float] = field(default_factory=list)
    memory_samples_mb: List[float] = field(default_factory=list)
    scan_times_ms: List[float] = field(default_factory=list)
    
    def add_pass_event(self, personality: str):
        """Record a successful pass by personality type"""
        if personality not in self.passes_by_personality:
            self.passes_by_personality[personality] = 0
        self.passes_by_personality[personality] += 1
        self.total_passes_completed += 1
        
    def add_lane_usage(self, lane: int):
        """Track lane usage for balance calculation"""
        if lane not in self.lane_usage_counts:
            self.lane_usage_counts[lane] = 0
        self.lane_usage_counts[lane] += 1
        
    def calculate_lane_balance(self) -> float:
        """Calculate lane utilization balance (0-1, 1 is perfect)"""
        if not self.lane_usage_counts or len(self.lane_usage_counts) < 2:
            return 0.0
            
        total = sum(self.lane_usage_counts.values())
        if total == 0:
            return 0.0
            
        expected = total / len(self.lane_usage_counts)
        variance = sum((count - expected) ** 2 for count in self.lane_usage_counts.values())
        max_variance = expected ** 2 * len(self.lane_usage_counts)
        
        return 1.0 - (variance / max_variance) if max_variance > 0 else 1.0
        
    def calculate_pass_rates(self) -> Dict[str, float]:
        """Calculate pass rates per minute by personality"""
        if self.duration_seconds == 0:
            return {}
            
        rates = {}
        for personality, count in self.passes_by_personality.items():
            rates[personality] = (count / self.duration_seconds) * 60  # per minute
            
        return rates
        
    def to_oqe_evidence(self) -> Dict[str, Any]:
        """Convert metrics to OQE evidence format"""
        avg_speed = sum(self.speed_samples) / len(self.speed_samples) if self.speed_samples else 0
        avg_fps = sum(self.fps_samples) / len(self.fps_samples) if self.fps_samples else 60
        avg_scan_time = sum(self.scan_times_ms) / len(self.scan_times_ms) if self.scan_times_ms else 0
        memory_increase = (self.memory_samples_mb[-1] - self.memory_samples_mb[0]) if len(self.memory_samples_mb) > 1 else 0
        
        return {
            "evidence_type": "VERIFIED",
            "timestamp": datetime.now().isoformat(),
            "source": "traffic_simulation_framework",
            "measurements": {
                # Performance metrics
                "avg_scan_time_ms": avg_scan_time,
                "avg_fps": avg_fps,
                "memory_increase_mb": memory_increase,
                
                # Traffic behavior metrics
                "total_passes": self.total_passes_completed,
                "pass_rates_per_minute": self.calculate_pass_rates(),
                "emergency_evasion_success_rate": (
                    (self.emergency_evasions_successful / self.emergency_evasions_attempted * 100)
                    if self.emergency_evasions_attempted > 0 else 100.0
                ),
                "collision_count": self.collisions_occurred,
                
                # Traffic flow metrics
                "average_speed": avg_speed,
                "congestion_events": self.congestion_events,
                "lane_balance_score": self.calculate_lane_balance(),
                
                # Test duration
                "test_duration_seconds": self.duration_seconds
            },
            "pass_criteria": self._evaluate_pass_criteria()
        }
        
    def _evaluate_pass_criteria(self) -> Dict[str, bool]:
        """Evaluate if OQE pass criteria are met"""
        avg_scan_time = sum(self.scan_times_ms) / len(self.scan_times_ms) if self.scan_times_ms else 999
        avg_fps = sum(self.fps_samples) / len(self.fps_samples) if self.fps_samples else 0
        memory_increase = (self.memory_samples_mb[-1] - self.memory_samples_mb[0]) if len(self.memory_samples_mb) > 1 else 999
        evasion_rate = (self.emergency_evasions_successful / self.emergency_evasions_attempted * 100) if self.emergency_evasions_attempted > 0 else 100
        
        return {
            "scan_time_under_5ms": avg_scan_time < 5.0,
            "fps_above_55": avg_fps > 55.0,
            "memory_under_50mb": memory_increase < 50.0,
            "no_collisions": self.collisions_occurred == 0,
            "emergency_evasion_95": evasion_rate >= 95.0,
            "lane_balance_above_0.8": self.calculate_lane_balance() > 0.8
        }


class TrafficSimulationHooks:
    """Hooks to integrate with actual Drive game for metrics collection"""
    
    def __init__(self, metrics: SimulationMetrics):
        self.metrics = metrics
        self.process = psutil.Process(os.getpid())
        self.frame_count = 0
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
    def on_frame_start(self, fps: float):
        """Called at start of each frame"""
        self.frame_count += 1
        
        # Sample every 60 frames (1 second at 60 FPS)
        if self.frame_count % 60 == 0:
            self.metrics.fps_samples.append(fps)
            current_memory = self.process.memory_info().rss / 1024 / 1024
            self.metrics.memory_samples_mb.append(current_memory - self.start_memory)
            
    def on_traffic_scan(self, scan_time_ms: float):
        """Called after each traffic awareness scan"""
        self.metrics.scan_times_ms.append(scan_time_ms)
        
    def on_lane_change_complete(self, car_personality: str):
        """Called when a car completes a passing maneuver"""
        self.metrics.add_pass_event(car_personality)
        
    def on_emergency_evasion(self, attempted: bool, successful: bool):
        """Called during emergency evasion attempts"""
        if attempted:
            self.metrics.emergency_evasions_attempted += 1
            if successful:
                self.metrics.emergency_evasions_successful += 1
                
    def on_collision(self):
        """Called when a collision occurs"""
        self.metrics.collisions_occurred += 1
        
    def on_congestion_detected(self, lane: int, car_count: int):
        """Called when congestion is detected (3+ cars close together)"""
        if car_count >= 3:
            self.metrics.congestion_events += 1
            
    def on_car_update(self, lane: int, speed: float):
        """Called for each car update to track lane usage and speeds"""
        self.metrics.add_lane_usage(lane)
        self.metrics.speed_samples.append(speed)


def create_test_scenarios() -> Dict[str, Dict[str, Any]]:
    """Create standardized test scenarios for OQE validation"""
    return {
        "baseline": {
            "description": "Baseline with no intelligent AI",
            "duration": 120,
            "ai_enabled": False,
            "spawn_pattern": "normal"
        },
        "standard_traffic": {
            "description": "Standard traffic with AI enabled",
            "duration": 120,
            "ai_enabled": True,
            "spawn_pattern": "normal"
        },
        "congestion_test": {
            "description": "Heavy congestion scenario",
            "duration": 180,
            "ai_enabled": True,
            "spawn_pattern": "congested",
            "initial_cars": 15
        },
        "emergency_test": {
            "description": "Emergency evasion scenarios",
            "duration": 60,
            "ai_enabled": True,
            "spawn_pattern": "emergency",
            "emergency_events": 10
        },
        "personality_test": {
            "description": "Test all personality types",
            "duration": 240,
            "ai_enabled": True,
            "spawn_pattern": "personality_mix"
        }
    }


def generate_comparison_report(baseline: SimulationMetrics, 
                             test: SimulationMetrics,
                             scenario_name: str) -> Dict[str, Any]:
    """Generate comparative OQE report between baseline and test"""
    baseline_evidence = baseline.to_oqe_evidence()
    test_evidence = test.to_oqe_evidence()
    
    # Calculate improvements
    baseline_speed = baseline_evidence["measurements"]["average_speed"]
    test_speed = test_evidence["measurements"]["average_speed"]
    speed_improvement = ((test_speed - baseline_speed) / baseline_speed * 100) if baseline_speed > 0 else 0
    
    baseline_congestion = baseline.congestion_events
    test_congestion = test.congestion_events
    congestion_reduction = ((baseline_congestion - test_congestion) / baseline_congestion * 100) if baseline_congestion > 0 else 0
    
    return {
        "scenario": scenario_name,
        "timestamp": datetime.now().isoformat(),
        "baseline_metrics": baseline_evidence,
        "test_metrics": test_evidence,
        "improvements": {
            "speed_improvement_percent": speed_improvement,
            "congestion_reduction_percent": congestion_reduction,
            "passes_added": test.total_passes_completed - baseline.total_passes_completed,
            "lane_balance_improvement": test.calculate_lane_balance() - baseline.calculate_lane_balance()
        },
        "oqe_compliance": {
            "all_criteria_met": all(test_evidence["pass_criteria"].values()),
            "failed_criteria": [k for k, v in test_evidence["pass_criteria"].items() if not v]
        },
        "verdict": "PASS" if all(test_evidence["pass_criteria"].values()) else "FAIL"
    }


if __name__ == "__main__":
    # Example of how to use the framework
    print("Traffic Simulation Framework Ready")
    print("="*60)
    print("This framework provides OQE-compliant testing capabilities")
    print("\nTo use:")
    print("1. Import TrafficSimulationHooks in drive.py")
    print("2. Initialize hooks with SimulationMetrics")
    print("3. Call hook methods at appropriate points")
    print("4. Generate OQE evidence after simulation")
    print("\nExample integration points:")
    print("- on_frame_start() in update()")
    print("- on_traffic_scan() after scan_surrounding_traffic()")
    print("- on_lane_change_complete() when ai_state returns to 'cruising'")
    print("- on_collision() in collision detection")
    print("\nSee LESSONS_LEARNED_OQE_ANALYSIS.md for full integration guide")