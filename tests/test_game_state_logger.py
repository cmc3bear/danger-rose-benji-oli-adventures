"""
Unit tests for GameStateLogger with OQE evidence collection.

This module provides comprehensive tests for the game state logging system
with emphasis on performance validation and OQE compliance.
"""

import json
import os
import tempfile
import time
import threading
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.systems.game_state_logger import GameStateLogger, GameEvent, initialize_global_logger
from src.systems.oqe_metric_collector import OQEMetricCollector


class TestGameStateLogger(unittest.TestCase):
    """Test cases for GameStateLogger with OQE evidence."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = GameStateLogger(self.temp_dir, enable_live_overlay=False)
        self.oqe_collector = OQEMetricCollector()
        
        # OQE evidence collection
        self.test_evidence = {
            "preconditions": {
                "temp_dir_created": True,
                "logger_initialized": True,
                "test_start_time": time.time()
            },
            "measurements": {},
            "postconditions": {}
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.logger.shutdown()
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Record postconditions
        self.test_evidence["postconditions"] = {
            "logger_shutdown": True,
            "temp_dir_cleaned": not Path(self.temp_dir).exists(),
            "test_end_time": time.time()
        }
    
    def test_logger_initialization_with_oqe(self):
        """Test logger initialization with OQE evidence collection."""
        # Record preconditions
        preconditions = {
            "temp_dir_exists": Path(self.temp_dir).exists(),
            "logs_dir_before": (Path(self.temp_dir) / "logs").exists()
        }
        
        # Measure initialization
        start_time = time.perf_counter()
        logger = GameStateLogger(self.temp_dir, enable_live_overlay=False)
        init_time_ms = (time.perf_counter() - start_time) * 1000
        
        # Collect measurements
        measurements = {
            "initialization_time_ms": init_time_ms,
            "session_id_format_valid": bool(logger.session_id and "_" in logger.session_id),
            "log_file_created": logger.log_file.exists(),
            "thread_started": logger.logging_thread.is_alive()
        }
        
        # Assertions with OQE validation
        self.assertIsNotNone(logger.session_id, "Session ID should be generated")
        self.assertTrue(logger.log_file.exists(), "Log file should be created")
        self.assertTrue(logger.logging_thread.is_alive(), "Logging thread should be running")
        self.assertLess(init_time_ms, 100, "Initialization should be fast (<100ms)")
        
        # Record postconditions
        postconditions = {
            "logger_ready": True,
            "logs_dir_created": (Path(self.temp_dir) / "logs").exists(),
            "performance_within_limits": init_time_ms < 100
        }
        
        # Generate OQE evidence
        evidence = self.oqe_collector.generate_oqe_evidence(
            test_id="logger_initialization",
            measurement_type="performance",
            preconditions=preconditions,
            measurements=measurements,
            postconditions=postconditions
        )
        
        self.assertGreaterEqual(evidence.compliance_score, 90, "OQE compliance should be high")
        logger.shutdown()
    
    def test_scene_transition_logging_with_performance(self):
        """Test scene transition logging with performance measurement."""
        # Preconditions
        preconditions = {
            "logger_active": self.logger.events_logged == 0,
            "initial_scene": self.logger.current_scene == "unknown"
        }
        
        # Measure scene transition logging
        start_time = time.perf_counter()
        self.logger.log_scene_transition("title", "hub", {"selected_character": "Danger"})
        logging_time_ms = (time.perf_counter() - start_time) * 1000
        
        # Wait for async logging
        time.sleep(0.1)
        self.logger.log_queue.join()
        
        # Verify log file content
        with open(self.logger.log_file, 'r') as f:
            log_lines = f.readlines()
        
        transition_events = []
        for line in log_lines:
            if line.strip():
                event_data = json.loads(line)
                if event_data.get("event_type") == "scene_transition":
                    transition_events.append(event_data)
        
        # Collect measurements
        measurements = {
            "logging_time_ms": logging_time_ms,
            "events_in_file": len(log_lines),
            "transition_events": len(transition_events),
            "current_scene_updated": self.logger.current_scene == "hub",
            "json_format_valid": len(transition_events) > 0
        }
        
        # Assertions
        self.assertEqual(len(transition_events), 1, "Should log exactly one transition event")
        self.assertEqual(transition_events[0]["event_data"]["from_scene"], "title")
        self.assertEqual(transition_events[0]["event_data"]["to_scene"], "hub")
        self.assertLess(logging_time_ms, 10, "Logging should be fast (<10ms)")
        
        # Postconditions
        postconditions = {
            "scene_updated": self.logger.current_scene == "hub",
            "event_logged": len(transition_events) == 1,
            "performance_acceptable": logging_time_ms < 10
        }
        
        # Generate OQE evidence
        evidence = self.oqe_collector.generate_oqe_evidence(
            test_id="scene_transition_logging",
            measurement_type="functional_performance",
            preconditions=preconditions,
            measurements=measurements,
            postconditions=postconditions
        )
        
        self.assertGreaterEqual(evidence.compliance_score, 85, "Scene transition logging should be compliant")
    
    def test_performance_impact_measurement(self):
        """Test logging system performance impact with OQE validation."""
        # Baseline measurement without intensive logging
        baseline_start = time.perf_counter()
        for i in range(100):
            # Simulate game operations
            time.sleep(0.001)  # 1ms per operation
        baseline_time = time.perf_counter() - baseline_start
        
        # Measurement with intensive logging
        logging_start = time.perf_counter()
        for i in range(100):
            self.logger.log_player_action(f"action_{i}", details={"index": i})
            self.logger.log_performance_metric("test_metric", i * 1.5)
            time.sleep(0.001)  # 1ms per operation
        logging_time = time.perf_counter() - logging_start
        
        # Wait for async processing
        self.logger.log_queue.join()
        
        # Calculate impact
        time_impact_percent = ((logging_time - baseline_time) / baseline_time) * 100
        performance_stats = self.logger.get_performance_impact()
        
        # Collect measurements
        measurements = {
            "baseline_time_s": baseline_time,
            "logging_time_s": logging_time,
            "time_impact_percent": time_impact_percent,
            "events_logged": self.logger.events_logged,
            "avg_overhead_ms": performance_stats["overhead_ms_per_event"],
            "total_impact_percent": performance_stats["impact_percentage"]
        }
        
        # Assertions for 2% FPS impact requirement
        self.assertLess(time_impact_percent, 5, "Time impact should be minimal (<5%)")
        self.assertLess(performance_stats["impact_percentage"], 2, "Overall impact should be <2%")
        self.assertGreater(self.logger.events_logged, 100, "Should log all events")
        
        # Generate OQE evidence for performance requirement
        evidence = self.oqe_collector.generate_oqe_evidence(
            test_id="performance_impact",
            measurement_type="performance_validation",
            preconditions={"baseline_established": True},
            measurements=measurements,
            postconditions={"impact_within_limits": time_impact_percent < 5}
        )
        
        self.assertGreaterEqual(evidence.compliance_score, 90, "Performance impact should be OQE compliant")
    
    def test_memory_usage_tracking(self):
        """Test memory usage tracking with OQE evidence."""
        import psutil
        
        # Initial memory measurement
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Generate many log events
        for i in range(1000):
            self.logger.log_player_action(f"bulk_action_{i}", details={"data": "x" * 100})
        
        # Wait for processing
        self.logger.log_queue.join()
        
        # Final memory measurement
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Get logger's own performance stats
        performance_stats = self.logger.get_performance_impact()
        session_stats = self.logger.get_session_stats()
        
        # Collect measurements
        measurements = {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": memory_increase,
            "events_logged": self.logger.events_logged,
            "log_file_size_kb": session_stats["log_file_size_kb"],
            "memory_efficiency": memory_increase / self.logger.events_logged if self.logger.events_logged > 0 else 0
        }
        
        # Assertions
        self.assertLess(memory_increase, 50, "Memory increase should be reasonable (<50MB)")
        self.assertGreater(session_stats["log_file_size_kb"], 0, "Log file should have content")
        
        # Generate OQE evidence
        evidence = self.oqe_collector.generate_oqe_evidence(
            test_id="memory_usage_tracking",
            measurement_type="resource_usage",
            preconditions={"initial_memory_recorded": True},
            measurements=measurements,
            postconditions={"memory_within_limits": memory_increase < 50}
        )
        
        self.assertGreaterEqual(evidence.compliance_score, 80, "Memory usage should be compliant")
    
    def test_concurrent_logging_thread_safety(self):
        """Test thread safety of concurrent logging operations."""
        import threading
        
        # Preconditions
        preconditions = {
            "logger_thread_active": self.logger.logging_thread.is_alive(),
            "initial_queue_size": self.logger.log_queue.qsize()
        }
        
        # Concurrent logging from multiple threads
        def log_worker(worker_id, event_count):
            for i in range(event_count):
                self.logger.log_player_action(f"worker_{worker_id}_action_{i}")
                time.sleep(0.001)  # Small delay
        
        threads = []
        events_per_worker = 50
        worker_count = 5
        
        start_time = time.perf_counter()
        
        # Start worker threads
        for worker_id in range(worker_count):
            thread = threading.Thread(target=log_worker, args=(worker_id, events_per_worker))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        concurrent_time = time.perf_counter() - start_time
        
        # Wait for all events to be processed
        self.logger.log_queue.join()
        
        # Verify all events were logged
        expected_events = worker_count * events_per_worker
        
        # Collect measurements
        measurements = {
            "concurrent_logging_time_s": concurrent_time,
            "expected_events": expected_events,
            "actual_events_logged": self.logger.events_logged,
            "thread_count": worker_count,
            "events_per_thread": events_per_worker,
            "logging_rate_events_per_second": expected_events / concurrent_time if concurrent_time > 0 else 0
        }
        
        # Postconditions
        postconditions = {
            "all_events_logged": self.logger.events_logged >= expected_events,
            "no_thread_errors": True,  # No exceptions thrown
            "queue_processed": self.logger.log_queue.qsize() == 0
        }
        
        # Assertions
        self.assertGreaterEqual(self.logger.events_logged, expected_events, 
                               "All concurrent events should be logged")
        self.assertEqual(self.logger.log_queue.qsize(), 0, "Queue should be empty after processing")
        
        # Generate OQE evidence
        evidence = self.oqe_collector.generate_oqe_evidence(
            test_id="concurrent_logging_thread_safety",
            measurement_type="concurrency_validation",
            preconditions=preconditions,
            measurements=measurements,
            postconditions=postconditions
        )
        
        self.assertGreaterEqual(evidence.compliance_score, 85, "Concurrent logging should be OQE compliant")
    
    def test_global_logger_management(self):
        """Test global logger initialization and management."""
        # Test global logger initialization
        global_logger = initialize_global_logger(self.temp_dir, enable_live_overlay=False)
        
        self.assertIsNotNone(global_logger, "Global logger should be initialized")
        self.assertEqual(global_logger, initialize_global_logger(self.temp_dir), 
                        "Subsequent calls should return same instance")
        
        # Test logging through global instance
        global_logger.log_system_event("test", "global_test", {"test": True})
        
        # Wait for processing
        global_logger.log_queue.join()
        
        # Verify event was logged
        self.assertGreater(global_logger.events_logged, 0, "Global logger should log events")
        
        # Clean up
        global_logger.shutdown()


class TestOQEMetricCollector(unittest.TestCase):
    """Test cases for OQE Metric Collector."""
    
    def setUp(self):
        """Set up test environment."""
        self.collector = OQEMetricCollector()
    
    def test_fps_measurement_accuracy(self):
        """Test FPS measurement accuracy with statistical validation."""
        # Simulate consistent frame times
        consistent_frame_times = [1/60] * 60  # 60 FPS for 60 samples
        
        fps_measurements = []
        for frame_time in consistent_frame_times:
            time.sleep(frame_time)  # Simulate frame time
            fps_data = self.collector.measure_fps("test_scene")
            fps_measurements.append(fps_data["current_fps"])
        
        # Statistical analysis
        avg_fps = sum(fps_measurements) / len(fps_measurements)
        fps_variance = sum((fps - avg_fps) ** 2 for fps in fps_measurements) / len(fps_measurements)
        fps_stability = fps_data["fps_stability"]
        
        # Measurements for OQE
        measurements = {
            "target_fps": 60,
            "measured_avg_fps": avg_fps,
            "fps_variance": fps_variance,
            "fps_stability": fps_stability,
            "sample_count": len(fps_measurements)
        }
        
        # Validation assertions
        self.assertGreater(avg_fps, 45, "Average FPS should be reasonable")
        self.assertGreater(fps_stability, 70, "FPS should be stable")
        self.assertEqual(len(fps_measurements), 60, "Should collect all samples")
        
        # Generate OQE evidence
        evidence = self.collector.generate_oqe_evidence(
            test_id="fps_measurement_accuracy",
            measurement_type="fps_validation",
            preconditions={"target_fps": 60, "sample_count": 60},
            measurements=measurements,
            postconditions={"accuracy_validated": abs(avg_fps - 60) < 15}
        )
        
        self.assertGreaterEqual(evidence.compliance_score, 80, "FPS measurement should be accurate")
    
    def test_accuracy_calculation_comprehensive(self):
        """Test accuracy calculation for various data types."""
        test_cases = [
            # (expected, actual, tolerance, expected_accuracy)
            (100, 100, 0.01, 100.0),  # Exact match
            (100, 98, 0.05, 100.0),   # Within tolerance
            (100, 95, 0.01, 95.0),    # Outside tolerance
            ("test", "test", 0.01, 100.0),  # String exact match
            ("hello", "hallo", 0.01, 80.0), # String partial match
            ([1, 2, 3], [1, 2, 3], 0.01, 100.0),  # List exact match
            ([1, 2, 3], [1, 2, 4], 0.01, 66.67),  # List partial match
            (True, True, 0.01, 100.0),  # Boolean match
            (True, False, 0.01, 0.0),   # Boolean mismatch
        ]
        
        measurements = {}
        for i, (expected, actual, tolerance, expected_accuracy) in enumerate(test_cases):
            accuracy = self.collector.calculate_accuracy(expected, actual, tolerance)
            measurements[f"test_case_{i}_accuracy"] = accuracy
            
            # Allow small floating point differences
            self.assertAlmostEqual(accuracy, expected_accuracy, places=1, 
                                 msg=f"Case {i}: expected {expected_accuracy}, got {accuracy}")
        
        # Generate OQE evidence for accuracy calculations
        evidence = self.collector.generate_oqe_evidence(
            test_id="accuracy_calculation_comprehensive",
            measurement_type="accuracy_validation",
            preconditions={"test_cases_count": len(test_cases)},
            measurements=measurements,
            postconditions={"all_cases_validated": True}
        )
        
        self.assertGreaterEqual(evidence.compliance_score, 90, "Accuracy calculations should be precise")


def run_oqe_compliant_test_suite():
    """Run the complete OQE compliant test suite."""
    import unittest
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTest(unittest.makeSuite(TestGameStateLogger))
    suite.addTest(unittest.makeSuite(TestOQEMetricCollector))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate OQE test report
    test_report = {
        "test_suite": "Game State Logging System",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success_rate": ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100 if result.testsRun > 0 else 0,
        "oqe_compliance": "PASS" if len(result.failures) == 0 and len(result.errors) == 0 else "FAIL"
    }
    
    print("\n" + "="*50)
    print("OQE TEST SUITE RESULTS")
    print("="*50)
    print(f"Tests Run: {test_report['tests_run']}")
    print(f"Failures: {test_report['failures']}")
    print(f"Errors: {test_report['errors']}")
    print(f"Success Rate: {test_report['success_rate']:.1f}%")
    print(f"OQE Compliance: {test_report['oqe_compliance']}")
    
    return test_report


if __name__ == "__main__":
    run_oqe_compliant_test_suite()