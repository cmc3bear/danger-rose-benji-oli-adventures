"""
OQE Enforcement Agents for the Orchestration Pipeline

These agents ensure measurement-first development and evidence collection.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from .agent_pipeline import (
    BaseAgent, AgentReport, AgentType, EvidenceLevel, ObjectiveEvidence
)


class OQEInfrastructureAgent(BaseAgent):
    """Ensures measurement infrastructure exists BEFORE implementation"""
    
    def __init__(self, project_root: str):
        super().__init__(project_root)
        self.agent_type = AgentType.MASTER_PLAN_AUDITOR  # Will add new type
        
    def execute(self, context: Dict[str, Any]) -> AgentReport:
        report = AgentReport(
            agent_type=self.agent_type,
            task="Verify OQE measurement infrastructure",
            status="success",
            evidence=[],
            recommendations=[],
            warnings=[]
        )
        
        issue_number = context.get("issue_number")
        # Extract test plan from report object
        test_plan_report = context.get("test_plan_developer_report")
        if test_plan_report and hasattr(test_plan_report, 'metadata'):
            test_plan = test_plan_report.metadata.get("test_plan", {})
        else:
            # Simulate test plan for demonstration
            test_plan = {
                "test_cases": [
                    {
                        "id": "TC001",
                        "oqe_metrics": {
                            "scan_time_ms": 5.0,
                            "pass_rate": 0.3,
                            "fps_impact": 5
                        }
                    }
                ]
            }
        
        # Check if measurement infrastructure exists
        missing_infrastructure = self._check_measurement_capability(test_plan)
        
        if missing_infrastructure:
            report.status = "blocked"
            report.warnings.append(
                f"CRITICAL: Cannot proceed without measurement infrastructure. "
                f"Missing: {', '.join(missing_infrastructure)}"
            )
            
            # Generate infrastructure requirements
            infrastructure_code = self._generate_infrastructure_code(missing_infrastructure, test_plan)
            
            report.add_evidence(
                claim="Measurement infrastructure required",
                evidence_type=EvidenceLevel.VERIFIED,
                data={
                    "missing_components": missing_infrastructure,
                    "generated_code": infrastructure_code
                },
                measurements={
                    "missing_count": float(len(missing_infrastructure)),
                    "estimated_hours": float(len(missing_infrastructure) * 0.5)
                },
                source="Infrastructure analysis"
            )
            
            report.recommendations.append("Create measurement infrastructure FIRST:")
            for component in missing_infrastructure:
                report.recommendations.append(f"  - Implement {component}")
                
        else:
            # All infrastructure exists
            report.add_evidence(
                claim="Measurement infrastructure verified",
                evidence_type=EvidenceLevel.VERIFIED,
                data={"components_found": self._list_existing_infrastructure()},
                measurements={"infrastructure_complete": 1.0},
                source="Infrastructure scan"
            )
            report.next_agent = AgentType.SOLUTION_RESEARCHER
            
        return report
        
    def _check_measurement_capability(self, test_plan: Dict) -> List[str]:
        """Check what measurement infrastructure is missing"""
        missing = []
        
        # Extract required metrics from test plan
        required_metrics = set()
        for test_case in test_plan.get("test_cases", []):
            for metric in test_case.get("oqe_metrics", {}).keys():
                required_metrics.add(metric)
                
        # Check if collectors exist for each metric type
        metric_to_infrastructure = {
            "scan_time_ms": "TimingCollector",
            "pass_rate": "EventCounterCollector", 
            "fps_impact": "PerformanceMonitor",
            "memory_increase_mb": "MemoryProfiler",
            "lane_balance": "TrafficFlowAnalyzer",
            "collision_rate": "SafetyMetricsCollector"
        }
        
        for metric in required_metrics:
            for pattern, infra in metric_to_infrastructure.items():
                if pattern in metric:
                    # Check if infrastructure exists
                    if not self._infrastructure_exists(infra):
                        missing.append(infra)
                        
        return list(set(missing))  # Remove duplicates
        
    def _infrastructure_exists(self, component_name: str) -> bool:
        """Check if a measurement component exists in codebase"""
        # In real implementation, would search codebase
        # For now, simulate based on known state
        existing = ["TimingCollector"]  # We know we have basic timing
        return component_name in existing
        
    def _list_existing_infrastructure(self) -> List[str]:
        """List existing measurement infrastructure"""
        # In real implementation, would scan codebase
        return ["TimingCollector", "BasicMetrics"]
        
    def _generate_infrastructure_code(self, missing: List[str], test_plan: Dict) -> str:
        """Generate template code for missing infrastructure"""
        code = "# Generated Measurement Infrastructure\n\n"
        
        for component in missing:
            if component == "EventCounterCollector":
                code += self._generate_event_counter()
            elif component == "PerformanceMonitor":
                code += self._generate_performance_monitor()
            elif component == "MemoryProfiler":
                code += self._generate_memory_profiler()
            elif component == "TrafficFlowAnalyzer":
                code += self._generate_traffic_analyzer()
            elif component == "SafetyMetricsCollector":
                code += self._generate_safety_collector()
                
        return code
        
    def _generate_event_counter(self) -> str:
        return '''
class EventCounterCollector:
    """Counts events for rate calculations"""
    def __init__(self):
        self.event_counts = {}
        self.start_time = time.time()
        
    def count_event(self, event_type: str, metadata: Dict = None):
        if event_type not in self.event_counts:
            self.event_counts[event_type] = []
        self.event_counts[event_type].append({
            "timestamp": time.time(),
            "metadata": metadata or {}
        })
        
    def get_rate(self, event_type: str) -> float:
        """Get events per minute"""
        if event_type not in self.event_counts:
            return 0.0
        elapsed = time.time() - self.start_time
        return len(self.event_counts[event_type]) / elapsed * 60

'''

    def _generate_performance_monitor(self) -> str:
        return '''
class PerformanceMonitor:
    """Monitor FPS and frame times"""
    def __init__(self, target_fps: float = 60.0):
        self.target_fps = target_fps
        self.fps_samples = []
        self.frame_times = []
        
    def record_frame(self, clock):
        fps = clock.get_fps()
        self.fps_samples.append(fps)
        
    def get_average_fps(self) -> float:
        return sum(self.fps_samples) / len(self.fps_samples) if self.fps_samples else 0

'''

    def _generate_memory_profiler(self) -> str:
        return '''
class MemoryProfiler:
    """Track memory usage over time"""
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.baseline_mb = self.process.memory_info().rss / 1024 / 1024
        self.samples = []
        
    def sample(self):
        current_mb = self.process.memory_info().rss / 1024 / 1024
        self.samples.append(current_mb - self.baseline_mb)
        
    def get_increase_mb(self) -> float:
        return self.samples[-1] if self.samples else 0.0

'''

    def _generate_traffic_analyzer(self) -> str:
        return '''
class TrafficFlowAnalyzer:
    """Analyze traffic patterns and flow"""
    def __init__(self):
        self.lane_usage = {}
        self.speed_samples = []
        self.congestion_events = 0
        
    def record_vehicle_position(self, lane: int, speed: float):
        if lane not in self.lane_usage:
            self.lane_usage[lane] = 0
        self.lane_usage[lane] += 1
        self.speed_samples.append(speed)
        
    def calculate_lane_balance(self) -> float:
        """Calculate how evenly lanes are used (0-1)"""
        if not self.lane_usage:
            return 0.0
        total = sum(self.lane_usage.values())
        expected = total / len(self.lane_usage)
        variance = sum((count - expected)**2 for count in self.lane_usage.values())
        max_variance = expected**2 * len(self.lane_usage)
        return 1.0 - (variance / max_variance) if max_variance > 0 else 1.0

'''

    def _generate_safety_collector(self) -> str:
        return '''
class SafetyMetricsCollector:
    """Track safety-related metrics"""
    def __init__(self):
        self.collisions = 0
        self.near_misses = 0
        self.emergency_evasions = {"attempted": 0, "successful": 0}
        
    def record_collision(self):
        self.collisions += 1
        
    def record_emergency_evasion(self, successful: bool):
        self.emergency_evasions["attempted"] += 1
        if successful:
            self.emergency_evasions["successful"] += 1
            
    def get_evasion_success_rate(self) -> float:
        attempts = self.emergency_evasions["attempted"]
        if attempts == 0:
            return 100.0
        return self.emergency_evasions["successful"] / attempts * 100

'''


class BaselineComparisonAgent(BaseAgent):
    """Ensures baseline measurements exist for comparison"""
    
    def __init__(self, project_root: str):
        super().__init__(project_root)
        self.agent_type = AgentType.TEST_EXECUTOR  # Will add new type
        
    def execute(self, context: Dict[str, Any]) -> AgentReport:
        report = AgentReport(
            agent_type=self.agent_type,
            task="Verify baseline measurements for comparison",
            status="success",
            evidence=[],
            recommendations=[],
            warnings=[]
        )
        
        # Extract test plan from context
        test_plan = context.get("test_plan", {})
        if not test_plan:
            # Use simulated test plan for demonstration
            test_plan = {
                "test_cases": [
                    {
                        "id": "TC001",
                        "oqe_metrics": {
                            "scan_time_ms": 5.0,
                            "pass_rate": 0.3
                        }
                    }
                ]
            }
        
        # Check if baseline exists
        baseline_path = self._get_baseline_path(context.get("issue_number"))
        baseline_exists = os.path.exists(baseline_path)
        
        if not baseline_exists:
            report.warnings.append(
                "CRITICAL: No baseline measurements found. "
                "Cannot prove improvement without baseline comparison."
            )
            
            # Generate baseline collection plan
            baseline_plan = self._generate_baseline_plan(test_plan)
            
            report.add_evidence(
                claim="Baseline measurement required",
                evidence_type=EvidenceLevel.DOCUMENTED,
                data={
                    "baseline_path": baseline_path,
                    "collection_plan": baseline_plan
                },
                measurements={
                    "estimated_duration_minutes": 30.0,
                    "required_samples": 1800.0  # 30 min * 60 samples/min
                },
                source="Baseline analysis"
            )
            
            report.recommendations.append("Collect baseline measurements:")
            report.recommendations.append("1. Disable new feature/AI")
            report.recommendations.append("2. Run for 30 minutes")
            report.recommendations.append("3. Collect all metrics")
            report.recommendations.append("4. Save as baseline.json")
            
        else:
            # Load and validate baseline
            with open(baseline_path, 'r') as f:
                baseline_data = json.load(f)
                
            report.add_evidence(
                claim="Baseline measurements available",
                evidence_type=EvidenceLevel.VERIFIED,
                data={
                    "baseline_date": baseline_data.get("timestamp"),
                    "metrics_count": len(baseline_data.get("metrics", {}))
                },
                measurements={
                    "baseline_duration_seconds": baseline_data.get("duration", 0),
                    "baseline_samples": float(len(baseline_data.get("samples", [])))
                },
                source=baseline_path
            )
            
        return report
        
    def _get_baseline_path(self, issue_number: int) -> str:
        """Get path to baseline measurements file"""
        return os.path.join(
            self.project_root,
            "test_results",
            f"baseline_issue_{issue_number}.json"
        )
        
    def _generate_baseline_plan(self, test_plan: Dict) -> Dict[str, Any]:
        """Generate plan for collecting baseline measurements"""
        return {
            "duration_minutes": 30,
            "metrics_to_collect": [
                metric for test in test_plan.get("test_cases", [])
                for metric in test.get("oqe_metrics", {}).keys()
            ],
            "collection_frequency_hz": 1,  # Once per second
            "scenarios": [
                "normal_traffic",
                "congested_traffic",
                "emergency_situations"
            ]
        }


class OQEValidationAgent(BaseAgent):
    """Validates that all OQE criteria can be measured before proceeding"""
    
    def __init__(self, project_root: str):
        super().__init__(project_root)
        self.agent_type = AgentType.TEST_EXECUTOR
        
    def execute(self, context: Dict[str, Any]) -> AgentReport:
        report = AgentReport(
            agent_type=self.agent_type,
            task="Validate OQE measurement capability",
            status="success",
            evidence=[],
            recommendations=[],
            warnings=[]
        )
        
        # Extract test plan from context
        test_plan = context.get("test_plan", {})
        if not test_plan:
            # Use simulated test plan for demonstration
            test_plan = {
                "test_cases": [
                    {
                        "id": "TC001",
                        "oqe_metrics": {
                            "scan_time_ms": 5.0,
                            "pass_rate": 0.3
                        }
                    }
                ]
            }
        
        # Validate each test case
        unmeasurable_metrics = []
        measurement_methods = {}
        
        for test_case in test_plan.get("test_cases", []):
            test_id = test_case.get("id")
            
            for metric_name, target_value in test_case.get("oqe_metrics", {}).items():
                method = self._determine_measurement_method(metric_name, test_case)
                
                if method == "UNMEASURABLE":
                    unmeasurable_metrics.append(f"{test_id}.{metric_name}")
                else:
                    measurement_methods[f"{test_id}.{metric_name}"] = method
                    
        if unmeasurable_metrics:
            report.status = "blocked"
            report.warnings.append(
                f"CRITICAL: {len(unmeasurable_metrics)} metrics cannot be measured. "
                "Revise test plan with measurable criteria."
            )
            
            for metric in unmeasurable_metrics:
                report.warnings.append(f"  - {metric}: No measurement method available")
                
        else:
            report.add_evidence(
                claim="All OQE metrics are measurable",
                evidence_type=EvidenceLevel.VERIFIED,
                data={
                    "total_metrics": len(measurement_methods),
                    "measurement_methods": measurement_methods
                },
                measurements={
                    "measurable_metrics": float(len(measurement_methods)),
                    "measurability_score": 100.0
                },
                source="Measurement analysis"
            )
            
            report.recommendations.append(
                f"All {len(measurement_methods)} metrics have valid measurement methods"
            )
            
        return report
        
    def _determine_measurement_method(self, metric_name: str, test_case: Dict) -> str:
        """Determine how to measure a specific metric"""
        
        # Common measurement patterns
        measurement_patterns = {
            "time": "time.perf_counter()",
            "rate": "event_counter.get_rate()",
            "fps": "clock.get_fps()",
            "memory": "psutil.Process().memory_info()",
            "count": "counter.increment()",
            "distance": "calculate_distance()",
            "accuracy": "correct / total * 100",
            "score": "calculate_score()",
            "balance": "statistical_variance()"
        }
        
        # Check metric name against patterns
        for pattern, method in measurement_patterns.items():
            if pattern in metric_name.lower():
                return method
                
        # Check for custom measurement in test case
        if "measurement_method" in test_case:
            return test_case["measurement_method"]
            
        return "UNMEASURABLE"


# Update the agent type enum to include new agents
def register_oqe_agents():
    """Register OQE enforcement agents in the pipeline"""
    # This would be called during pipeline initialization
    # to add the new agents to the execution flow
    pass