"""
OQE Metric Collector - Objective Qualified Evidence collection system.

This module provides precise measurement capabilities for collecting
quantifiable evidence to support test validation and compliance.

Key features:
- FPS measurement with statistical analysis
- Memory usage tracking with delta calculations
- Response time measurement for user interactions
- Accuracy calculations for comparison operations
- Performance impact measurement
- Evidence correlation for test validation
"""

import time
import threading
import statistics
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
import psutil
import pygame


@dataclass
class PerformanceSample:
    """Single performance measurement sample."""
    timestamp: float
    metric_name: str
    value: float
    context: Dict[str, Any]
    scene: str


@dataclass
class OQEEvidence:
    """Structured evidence package for OQE compliance."""
    test_id: str
    measurement_type: str
    preconditions: Dict[str, Any]
    measurements: Dict[str, Any]
    postconditions: Dict[str, Any]
    statistical_analysis: Dict[str, Any]
    compliance_score: float
    evidence_quality: str  # "high", "medium", "low"


class OQEMetricCollector:
    """
    Collects objective metrics for test evidence and compliance validation.
    
    This class provides precise measurement capabilities with statistical
    analysis to support OQE (Objective Qualified Evidence) requirements.
    """
    
    def __init__(self, sample_window_size: int = 60):
        """
        Initialize the metric collector.
        
        Args:
            sample_window_size: Number of samples to keep for statistical analysis
        """
        self.sample_window_size = sample_window_size
        self.samples: List[PerformanceSample] = []
        self.measurement_lock = threading.Lock()
        
        # System monitoring
        self.process = psutil.Process()
        self.clock = pygame.time.Clock()
        
        # Baseline measurements
        self.baseline_memory_mb = self.process.memory_info().rss / 1024 / 1024
        self.baseline_timestamp = time.time()
        
        # FPS tracking
        self.fps_history: List[float] = []
        self.frame_times: List[float] = []
        self.last_frame_time = time.time()
        
        # Response time tracking
        self.active_timers: Dict[str, float] = {}
        
        # Statistical thresholds for quality assessment
        self.quality_thresholds = {
            "high": {"cv_max": 0.05, "sample_min": 30, "accuracy_min": 0.95},
            "medium": {"cv_max": 0.15, "sample_min": 10, "accuracy_min": 0.85},
            "low": {"cv_max": 0.30, "sample_min": 5, "accuracy_min": 0.70}
        }
    
    def start_timer(self, timer_id: str) -> float:
        """
        Start a timer for measuring response times.
        
        Args:
            timer_id: Unique identifier for this timing measurement
            
        Returns:
            Start timestamp for reference
        """
        start_time = time.perf_counter()
        self.active_timers[timer_id] = start_time
        return start_time
    
    def stop_timer(self, timer_id: str) -> Optional[float]:
        """
        Stop a timer and return elapsed time in milliseconds.
        
        Args:
            timer_id: Identifier for the timer to stop
            
        Returns:
            Elapsed time in milliseconds, or None if timer not found
        """
        if timer_id not in self.active_timers:
            return None
        
        end_time = time.perf_counter()
        elapsed_ms = (end_time - self.active_timers[timer_id]) * 1000
        del self.active_timers[timer_id]
        
        return elapsed_ms
    
    def measure_fps(self, scene: str = "unknown") -> Dict[str, float]:
        """
        Measure current FPS with statistical analysis.
        
        Args:
            scene: Current scene name for context
            
        Returns:
            Dictionary with FPS measurements and statistics
        """
        current_time = time.time()
        
        # Calculate frame time
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Calculate instantaneous FPS
        if frame_time > 0:
            current_fps = 1.0 / frame_time
            self.fps_history.append(current_fps)
            self.frame_times.append(frame_time * 1000)  # Store in milliseconds
        else:
            current_fps = 0.0
        
        # Maintain rolling window
        if len(self.fps_history) > self.sample_window_size:
            self.fps_history = self.fps_history[-self.sample_window_size:]
            self.frame_times = self.frame_times[-self.sample_window_size:]
        
        # Calculate statistics
        if len(self.fps_history) >= 2:
            stats = self._calculate_statistics(self.fps_history)
        else:
            stats = {"mean": current_fps, "std": 0.0, "cv": 0.0, "min": current_fps, "max": current_fps}
        
        # Record sample
        sample = PerformanceSample(
            timestamp=current_time,
            metric_name="fps",
            value=current_fps,
            context={"statistics": stats, "frame_time_ms": frame_time * 1000},
            scene=scene
        )
        
        with self.measurement_lock:
            self.samples.append(sample)
            self._maintain_sample_window()
        
        return {
            "current_fps": round(current_fps, 2),
            "avg_fps": round(stats["mean"], 2),
            "min_fps": round(stats["min"], 2),
            "max_fps": round(stats["max"], 2),
            "fps_stability": round(100 - (stats["cv"] * 100), 2),
            "frame_time_ms": round(frame_time * 1000, 2),
            "sample_count": len(self.fps_history)
        }
    
    def measure_memory(self, scene: str = "unknown") -> Dict[str, float]:
        """
        Measure current memory usage with delta calculations.
        
        Args:
            scene: Current scene name for context
            
        Returns:
            Dictionary with memory measurements
        """
        try:
            memory_info = self.process.memory_info()
            current_memory_mb = memory_info.rss / 1024 / 1024
            memory_delta_mb = current_memory_mb - self.baseline_memory_mb
            
            # Virtual memory info
            vmem_info = self.process.memory_full_info()
            virtual_memory_mb = vmem_info.vms / 1024 / 1024
            
            # System memory
            system_memory = psutil.virtual_memory()
            system_memory_percent = system_memory.percent
            
            result = {
                "current_memory_mb": round(current_memory_mb, 2),
                "baseline_memory_mb": round(self.baseline_memory_mb, 2),
                "memory_delta_mb": round(memory_delta_mb, 2),
                "virtual_memory_mb": round(virtual_memory_mb, 2),
                "system_memory_percent": round(system_memory_percent, 2),
                "memory_efficiency": round((self.baseline_memory_mb / current_memory_mb) * 100, 2) if current_memory_mb > 0 else 100
            }
            
            # Record sample
            sample = PerformanceSample(
                timestamp=time.time(),
                metric_name="memory",
                value=current_memory_mb,
                context=result,
                scene=scene
            )
            
            with self.measurement_lock:
                self.samples.append(sample)
                self._maintain_sample_window()
            
            return result
            
        except Exception as e:
            return {
                "current_memory_mb": 0.0,
                "baseline_memory_mb": self.baseline_memory_mb,
                "memory_delta_mb": 0.0,
                "error": str(e)
            }
    
    def measure_response_time(self, event_name: str, action_start_time: float) -> float:
        """
        Measure time between input and response.
        
        Args:
            event_name: Name of the event being measured
            action_start_time: Timestamp when action was initiated
            
        Returns:
            Response time in milliseconds
        """
        current_time = time.perf_counter()
        response_time_ms = (current_time - action_start_time) * 1000
        
        # Record sample
        sample = PerformanceSample(
            timestamp=time.time(),
            metric_name="response_time",
            value=response_time_ms,
            context={"event_name": event_name},
            scene="unknown"
        )
        
        with self.measurement_lock:
            self.samples.append(sample)
            self._maintain_sample_window()
        
        return response_time_ms
    
    def calculate_accuracy(self, expected: Any, actual: Any, tolerance: float = 0.01) -> float:
        """
        Calculate accuracy percentage for comparisons.
        
        Args:
            expected: Expected value
            actual: Actual value
            tolerance: Tolerance for numerical comparisons
            
        Returns:
            Accuracy as percentage (0-100)
        """
        if expected == actual:
            return 100.0
        
        # Numerical comparison with tolerance
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            if expected == 0:
                return 0.0 if actual != 0 else 100.0
            
            relative_error = abs((actual - expected) / expected)
            if relative_error <= tolerance:
                return 100.0
            else:
                accuracy = max(0, (1 - relative_error) * 100)
                return round(accuracy, 2)
        
        # String comparison
        if isinstance(expected, str) and isinstance(actual, str):
            if expected.lower() == actual.lower():
                return 100.0
            
            # Use Levenshtein distance for partial matching
            distance = self._levenshtein_distance(expected.lower(), actual.lower())
            max_length = max(len(expected), len(actual))
            if max_length == 0:
                return 100.0
            
            similarity = (1 - distance / max_length) * 100
            return round(max(0, similarity), 2)
        
        # List/tuple comparison
        if isinstance(expected, (list, tuple)) and isinstance(actual, (list, tuple)):
            if len(expected) == 0 and len(actual) == 0:
                return 100.0
            
            matches = sum(1 for e, a in zip(expected, actual) if e == a)
            total = max(len(expected), len(actual))
            return round((matches / total) * 100, 2) if total > 0 else 0.0
        
        # Boolean comparison
        if isinstance(expected, bool) and isinstance(actual, bool):
            return 100.0 if expected == actual else 0.0
        
        # Default: exact match only
        return 100.0 if expected == actual else 0.0
    
    def collect_performance_baseline(self, duration_seconds: float = 10.0, scene: str = "baseline") -> Dict[str, Any]:
        """
        Collect performance baseline measurements.
        
        Args:
            duration_seconds: How long to collect baseline data
            scene: Scene name for context
            
        Returns:
            Baseline performance metrics
        """
        start_time = time.time()
        baseline_samples = {
            "fps": [],
            "memory": [],
            "frame_time": []
        }
        
        while (time.time() - start_time) < duration_seconds:
            # Measure FPS
            fps_data = self.measure_fps(scene)
            baseline_samples["fps"].append(fps_data["current_fps"])
            baseline_samples["frame_time"].append(fps_data["frame_time_ms"])
            
            # Measure memory every 1 second
            if len(baseline_samples["memory"]) == 0 or (time.time() - start_time) % 1.0 < 0.1:
                memory_data = self.measure_memory(scene)
                baseline_samples["memory"].append(memory_data["current_memory_mb"])
            
            time.sleep(0.016)  # ~60 FPS sampling rate
        
        # Calculate baseline statistics
        baseline_stats = {}
        for metric, samples in baseline_samples.items():
            if samples:
                baseline_stats[metric] = self._calculate_statistics(samples)
        
        return {
            "baseline_duration_s": duration_seconds,
            "sample_counts": {k: len(v) for k, v in baseline_samples.items()},
            "statistics": baseline_stats,
            "timestamp": time.time()
        }
    
    def generate_oqe_evidence(self, test_id: str, measurement_type: str, 
                             preconditions: Dict[str, Any], 
                             measurements: Dict[str, Any],
                             postconditions: Dict[str, Any]) -> OQEEvidence:
        """
        Generate structured OQE evidence package.
        
        Args:
            test_id: Unique test identifier
            measurement_type: Type of measurement being validated
            preconditions: Initial conditions before test
            measurements: Measured values during test
            postconditions: Final conditions after test
            
        Returns:
            Structured OQE evidence package
        """
        # Perform statistical analysis on measurements
        statistical_analysis = {}
        for key, value in measurements.items():
            if isinstance(value, list) and len(value) > 1:
                statistical_analysis[key] = self._calculate_statistics(value)
            elif isinstance(value, (int, float)):
                statistical_analysis[key] = {
                    "value": value,
                    "type": "scalar",
                    "unit": self._infer_unit(key)
                }
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(
            measurement_type, preconditions, measurements, postconditions
        )
        
        # Determine evidence quality
        evidence_quality = self._assess_evidence_quality(statistical_analysis, len(measurements))
        
        return OQEEvidence(
            test_id=test_id,
            measurement_type=measurement_type,
            preconditions=preconditions,
            measurements=measurements,
            postconditions=postconditions,
            statistical_analysis=statistical_analysis,
            compliance_score=compliance_score,
            evidence_quality=evidence_quality
        )
    
    def get_measurement_summary(self, metric_name: str = None, scene: str = None) -> Dict[str, Any]:
        """
        Get summary of measurements for analysis.
        
        Args:
            metric_name: Filter by specific metric name
            scene: Filter by specific scene
            
        Returns:
            Summary of measurements with statistics
        """
        with self.measurement_lock:
            filtered_samples = self.samples.copy()
        
        # Apply filters
        if metric_name:
            filtered_samples = [s for s in filtered_samples if s.metric_name == metric_name]
        if scene:
            filtered_samples = [s for s in filtered_samples if s.scene == scene]
        
        if not filtered_samples:
            return {"error": "No samples found matching criteria"}
        
        # Group by metric
        metrics_data = {}
        for sample in filtered_samples:
            if sample.metric_name not in metrics_data:
                metrics_data[sample.metric_name] = []
            metrics_data[sample.metric_name].append(sample.value)
        
        # Calculate statistics for each metric
        summary = {}
        for metric, values in metrics_data.items():
            summary[metric] = self._calculate_statistics(values)
            summary[metric]["sample_count"] = len(values)
            summary[metric]["time_span_s"] = filtered_samples[-1].timestamp - filtered_samples[0].timestamp
        
        return {
            "summary": summary,
            "total_samples": len(filtered_samples),
            "time_range": {
                "start": filtered_samples[0].timestamp,
                "end": filtered_samples[-1].timestamp
            }
        }
    
    def _calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calculate comprehensive statistics for a list of values."""
        if not values:
            return {}
        
        if len(values) == 1:
            return {
                "mean": values[0],
                "std": 0.0,
                "cv": 0.0,
                "min": values[0],
                "max": values[0],
                "median": values[0]
            }
        
        mean = statistics.mean(values)
        std = statistics.stdev(values)
        cv = std / mean if mean > 0 else 0.0
        
        return {
            "mean": mean,
            "std": std,
            "cv": cv,  # Coefficient of variation
            "min": min(values),
            "max": max(values),
            "median": statistics.median(values)
        }
    
    def _maintain_sample_window(self):
        """Maintain sample window size to prevent memory bloat."""
        if len(self.samples) > self.sample_window_size * 2:
            self.samples = self.samples[-self.sample_window_size:]
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _calculate_compliance_score(self, measurement_type: str, preconditions: Dict, 
                                  measurements: Dict, postconditions: Dict) -> float:
        """Calculate OQE compliance score based on measurement quality."""
        score_components = []
        
        # Check preconditions completeness
        if preconditions:
            score_components.append(min(len(preconditions) / 3, 1.0) * 25)  # Up to 25 points
        
        # Check measurements quality
        if measurements:
            measurement_quality = 0
            for key, value in measurements.items():
                if isinstance(value, (int, float)) and value >= 0:
                    measurement_quality += 1
                elif isinstance(value, list) and len(value) > 0:
                    measurement_quality += 1
            
            score_components.append(min(measurement_quality / len(measurements), 1.0) * 35)  # Up to 35 points
        
        # Check postconditions completeness
        if postconditions:
            score_components.append(min(len(postconditions) / 3, 1.0) * 25)  # Up to 25 points
        
        # Statistical validity (coefficient of variation)
        cv_scores = []
        for key, value in measurements.items():
            if isinstance(value, list) and len(value) > 1:
                stats = self._calculate_statistics(value)
                cv_score = max(0, 1 - stats["cv"]) * 15  # Up to 15 points for low CV
                cv_scores.append(cv_score)
        
        if cv_scores:
            score_components.append(statistics.mean(cv_scores))
        else:
            score_components.append(10)  # Default score for scalar measurements
        
        return min(100.0, sum(score_components))
    
    def _assess_evidence_quality(self, statistical_analysis: Dict, measurement_count: int) -> str:
        """Assess the quality of evidence based on statistical properties."""
        # Calculate average coefficient of variation
        cv_values = []
        for key, stats in statistical_analysis.items():
            if isinstance(stats, dict) and "cv" in stats:
                cv_values.append(stats["cv"])
        
        avg_cv = statistics.mean(cv_values) if cv_values else 0.0
        
        # Check against thresholds
        for quality, thresholds in self.quality_thresholds.items():
            if (avg_cv <= thresholds["cv_max"] and 
                measurement_count >= thresholds["sample_min"]):
                return quality
        
        return "low"
    
    def _infer_unit(self, metric_name: str) -> str:
        """Infer measurement unit from metric name."""
        unit_mappings = {
            "fps": "frames_per_second",
            "memory": "megabytes",
            "response_time": "milliseconds",
            "frame_time": "milliseconds",
            "cpu": "percent",
            "accuracy": "percent",
            "temperature": "celsius"
        }
        
        metric_lower = metric_name.lower()
        for key, unit in unit_mappings.items():
            if key in metric_lower:
                return unit
        
        return "units"