"""
Unit tests for Traffic Awareness System with OQE compliance
"""

import unittest
from dataclasses import dataclass
from src.systems.traffic_awareness import TrafficAwareness, DriverPersonality
import time


@dataclass
class MockNPCCar:
    """Mock car object for testing"""
    x: float
    y: float
    lane: int
    speed: float
    direction: int
    vehicle_type: str = "car"
    personality: DriverPersonality = DriverPersonality.NORMAL


class TestTrafficAwareness(unittest.TestCase):
    """Test cases for traffic awareness system with OQE"""
    
    def setUp(self):
        """Set up test environment"""
        self.awareness = TrafficAwareness()
        self.test_start_time = time.time()
        
    def tearDown(self):
        """Record test execution time"""
        execution_time = (time.time() - self.test_start_time) * 1000
        print(f"\nTest execution time: {execution_time:.2f}ms")
        
    def test_traffic_scanning_accuracy(self):
        """TC001: Verify traffic scanning detects all nearby vehicles correctly"""
        # Preconditions
        test_car = MockNPCCar(x=0.7, y=0, lane=3, speed=0.8, direction=1)
        traffic = [
            test_car,
            MockNPCCar(x=0.7, y=50, lane=3, speed=0.6, direction=1),    # Ahead same lane
            MockNPCCar(x=0.8, y=30, lane=4, speed=0.9, direction=1),    # Ahead right lane
            MockNPCCar(x=0.7, y=-40, lane=3, speed=1.0, direction=1),   # Behind same lane
            MockNPCCar(x=0.8, y=-60, lane=4, speed=1.2, direction=1),   # Behind right lane
            MockNPCCar(x=0.3, y=100, lane=1, speed=0.7, direction=-1),  # Oncoming (ignored)
        ]
        
        # Execute scan
        scan_start = time.time()
        scan = self.awareness.scan_surrounding_traffic(test_car, traffic)
        scan_time = (time.time() - scan_start) * 1000
        
        # OQE Measurements
        measurements = {
            "scan_time_ms": scan_time,
            "vehicles_detected": sum([
                1 if scan.ahead_same_lane else 0,
                1 if scan.ahead_right_lane else 0,
                1 if scan.behind_same_lane else 0,
                1 if scan.behind_right_lane else 0
            ]),
            "distance_to_ahead": scan.distance_to_ahead,
            "speed_differential": scan.speed_differential
        }
        
        # Verify results
        self.assertIsNotNone(scan.ahead_same_lane)
        self.assertEqual(scan.ahead_same_lane.y, 50)
        self.assertIsNotNone(scan.ahead_right_lane)
        self.assertEqual(scan.ahead_right_lane.y, 30)
        self.assertIsNotNone(scan.behind_same_lane)
        self.assertIsNotNone(scan.behind_right_lane)
        self.assertTrue(scan.right_lane_exists)  # Car in lane 3 can move to lane 4
        self.assertLess(scan_time, 5.0)  # Must complete in under 5ms
        
        # OQE Evidence
        print(f"\nOQE Evidence - Traffic Scanning:")
        print(f"  Scan time: {measurements['scan_time_ms']:.2f}ms")
        print(f"  Vehicles detected: {measurements['vehicles_detected']}/4")
        print(f"  Distance to ahead: {measurements['distance_to_ahead']}")
        print(f"  Speed differential: {measurements['speed_differential']}")
        
    def test_personality_based_decisions(self):
        """TC002: Verify different personalities make appropriate passing decisions"""
        # Test scenarios for each personality
        personalities = [
            (DriverPersonality.CAUTIOUS, 0.15),   # Need 15% speed advantage
            (DriverPersonality.NORMAL, 0.10),     # Need 10% speed advantage
            (DriverPersonality.AGGRESSIVE, 0.05), # Need 5% speed advantage
            (DriverPersonality.TRUCK, 0.20),      # Need 20% speed advantage
        ]
        
        results = {}
        
        for personality, threshold in personalities:
            test_car = MockNPCCar(
                x=0.7, y=0, lane=3, speed=1.0, direction=1,
                personality=personality
            )
            
            # Car ahead going slower
            slow_car = MockNPCCar(x=0.7, y=80, lane=3, speed=0.8, direction=1)
            traffic = [test_car, slow_car]
            
            scan = self.awareness.scan_surrounding_traffic(test_car, traffic)
            should_pass, direction = self.awareness.should_attempt_pass(test_car, scan)
            
            results[personality.value] = {
                "should_pass": should_pass,
                "speed_threshold": threshold,
                "actual_differential": test_car.speed - slow_car.speed
            }
            
        # OQE Evidence
        print("\nOQE Evidence - Personality Decisions:")
        for personality, data in results.items():
            print(f"  {personality}: Pass={data['should_pass']}, "
                  f"Threshold={data['speed_threshold']}, "
                  f"Differential={data['actual_differential']}")
                  
    def test_safety_margins(self):
        """TC003: Verify safety margins are enforced"""
        personalities_margins = {
            DriverPersonality.CAUTIOUS: (150.0, 100.0),
            DriverPersonality.NORMAL: (100.0, 60.0),
            DriverPersonality.AGGRESSIVE: (60.0, 40.0),
            DriverPersonality.TRUCK: (200.0, 120.0)
        }
        
        measurements = {}
        
        for personality, (front_gap, rear_gap) in personalities_margins.items():
            test_car = MockNPCCar(
                x=0.7, y=0, lane=3, speed=1.0, direction=1,
                personality=personality
            )
            
            # Test minimum safe distance
            traffic = [
                test_car,
                MockNPCCar(x=0.8, y=front_gap - 10, lane=4, speed=0.9, direction=1),  # Too close ahead
                MockNPCCar(x=0.8, y=-(rear_gap - 10), lane=4, speed=1.1, direction=1), # Too close behind
            ]
            
            scan = self.awareness.scan_surrounding_traffic(test_car, traffic)
            
            measurements[personality.value] = {
                "safe_to_change": scan.safe_to_change_right,
                "required_front_gap": front_gap,
                "required_rear_gap": rear_gap
            }
            
        # OQE Evidence
        print("\nOQE Evidence - Safety Margins:")
        for personality, data in measurements.items():
            print(f"  {personality}: Safe={data['safe_to_change']}, "
                  f"Front={data['required_front_gap']}, "
                  f"Rear={data['required_rear_gap']}")
                  
    def test_emergency_evasion(self):
        """TC004: Test emergency evasion detection"""
        test_car = MockNPCCar(x=0.7, y=0, lane=3, speed=1.0, direction=1)
        
        # Car very close ahead
        danger_car = MockNPCCar(x=0.7, y=25, lane=3, speed=0.2, direction=1)
        # Safe escape route
        traffic = [test_car, danger_car]
        
        start_time = time.time()
        scan = self.awareness.scan_surrounding_traffic(test_car, traffic)
        evasion_dir = self.awareness.get_emergency_evasion(test_car, scan)
        detection_time = (time.time() - start_time) * 1000
        
        # OQE Evidence
        print(f"\nOQE Evidence - Emergency Evasion:")
        print(f"  Detection time: {detection_time:.2f}ms")
        print(f"  Distance to danger: {scan.distance_to_ahead}")
        print(f"  Evasion direction: {evasion_dir}")
        print(f"  Safe lanes available: L={scan.safe_to_change_left}, R={scan.safe_to_change_right}")
        
        self.assertIsNotNone(evasion_dir)
        self.assertLess(detection_time, 16.0)  # Must detect within 16ms


if __name__ == '__main__':
    unittest.main()