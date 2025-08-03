"""
AI-Driven Development Metrics System

Tracks meaningful metrics for Claude-driven development instead of time-based metrics.
Focuses on:
- Code quality and correctness
- Feature completion rate
- Test coverage and evidence
- Issue resolution efficiency
- Development velocity (features/session)
- Code reusability
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class MetricType(Enum):
    """Types of metrics we track"""
    FEATURE_COMPLETION = "feature_completion"
    CODE_QUALITY = "code_quality"
    TEST_COVERAGE = "test_coverage"
    ISSUE_RESOLUTION = "issue_resolution"
    DEVELOPMENT_VELOCITY = "development_velocity"
    CODE_REUSABILITY = "code_reusability"
    DOCUMENTATION_QUALITY = "documentation_quality"
    SYSTEM_HEALTH = "system_health"


@dataclass
class FeatureMetric:
    """Track feature implementation metrics"""
    feature_name: str
    issue_number: Optional[int]
    lines_of_code: int
    files_created: int
    files_modified: int
    tests_added: int
    tests_passing: int
    documentation_updated: bool
    complexity_score: float  # Cyclomatic complexity
    completion_status: str  # "planned", "in_progress", "completed", "tested"
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class TestEvidence:
    """Track objective test evidence"""
    test_name: str
    test_type: str  # "unit", "integration", "system", "performance"
    status: str  # "pass", "fail", "error"
    evidence: Dict[str, Any]  # Objective measurements
    assertions_count: int
    coverage_percentage: float
    execution_time_ms: float
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class CodeQualityMetric:
    """Track code quality indicators"""
    file_path: str
    cyclomatic_complexity: float
    maintainability_index: float
    lines_of_code: int
    comment_ratio: float
    duplicate_lines: int
    test_coverage: float
    linting_errors: int
    type_checking_errors: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class SessionMetric:
    """Track per-session development metrics"""
    session_id: str
    features_completed: int
    issues_resolved: int
    tests_added: int
    tests_passing_rate: float
    code_files_created: int
    code_files_modified: int
    documentation_files_updated: int
    total_lines_added: int
    total_lines_removed: int
    refactoring_actions: int
    bugs_fixed: int
    bugs_introduced: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class AIDevMetricsTracker:
    """Main metrics tracking system for AI-driven development"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.metrics_dir = os.path.join(project_root, "metrics")
        self.metrics_file = os.path.join(self.metrics_dir, "ai_dev_metrics.json")
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create metrics directory if it doesn't exist
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        # Load existing metrics
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict[str, List[Dict]]:
        """Load existing metrics from file"""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {
            "features": [],
            "tests": [],
            "code_quality": [],
            "sessions": [],
            "issues": []
        }
    
    def _save_metrics(self):
        """Save metrics to file"""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def track_feature(self, feature: FeatureMetric):
        """Track a feature implementation"""
        feature.session_id = self.session_id
        self.metrics["features"].append(feature.to_dict())
        self._save_metrics()
    
    def track_test(self, evidence: TestEvidence):
        """Track test execution with evidence"""
        self.metrics["tests"].append(evidence.to_dict())
        self._save_metrics()
    
    def track_code_quality(self, quality: CodeQualityMetric):
        """Track code quality metrics"""
        self.metrics["code_quality"].append(quality.to_dict())
        self._save_metrics()
    
    def end_session(self, session_metrics: SessionMetric):
        """Record end-of-session metrics"""
        session_metrics.session_id = self.session_id
        self.metrics["sessions"].append(session_metrics.to_dict())
        self._save_metrics()
    
    def get_velocity_metrics(self) -> Dict[str, float]:
        """Calculate development velocity metrics"""
        sessions = self.metrics["sessions"]
        if not sessions:
            return {}
        
        # Last 5 sessions
        recent_sessions = sessions[-5:]
        
        avg_features_per_session = sum(s["features_completed"] for s in recent_sessions) / len(recent_sessions)
        avg_issues_per_session = sum(s["issues_resolved"] for s in recent_sessions) / len(recent_sessions)
        avg_tests_per_session = sum(s["tests_added"] for s in recent_sessions) / len(recent_sessions)
        
        return {
            "avg_features_per_session": avg_features_per_session,
            "avg_issues_per_session": avg_issues_per_session,
            "avg_tests_per_session": avg_tests_per_session,
            "total_features": len(self.metrics["features"]),
            "total_tests": len(self.metrics["tests"])
        }
    
    def get_quality_trends(self) -> Dict[str, Any]:
        """Analyze code quality trends"""
        quality_metrics = self.metrics["code_quality"]
        if not quality_metrics:
            return {}
        
        # Group by file
        file_metrics = {}
        for metric in quality_metrics:
            file_path = metric["file_path"]
            if file_path not in file_metrics:
                file_metrics[file_path] = []
            file_metrics[file_path].append(metric)
        
        # Calculate trends
        trends = {}
        for file_path, metrics in file_metrics.items():
            if len(metrics) > 1:
                latest = metrics[-1]
                previous = metrics[-2]
                trends[file_path] = {
                    "complexity_change": latest["cyclomatic_complexity"] - previous["cyclomatic_complexity"],
                    "coverage_change": latest["test_coverage"] - previous["test_coverage"],
                    "maintainability_change": latest["maintainability_index"] - previous["maintainability_index"]
                }
        
        return trends
    
    def get_test_health(self) -> Dict[str, Any]:
        """Analyze test suite health"""
        test_results = self.metrics["tests"]
        if not test_results:
            return {}
        
        total_tests = len(test_results)
        passing_tests = sum(1 for t in test_results if t["status"] == "pass")
        failing_tests = sum(1 for t in test_results if t["status"] == "fail")
        
        # Group by test type
        test_types = {}
        for test in test_results:
            test_type = test["test_type"]
            if test_type not in test_types:
                test_types[test_type] = {"pass": 0, "fail": 0, "error": 0}
            test_types[test_type][test["status"]] += 1
        
        # Calculate average coverage
        coverage_values = [t["coverage_percentage"] for t in test_results if "coverage_percentage" in t]
        avg_coverage = sum(coverage_values) / len(coverage_values) if coverage_values else 0
        
        return {
            "total_tests": total_tests,
            "passing_rate": (passing_tests / total_tests * 100) if total_tests > 0 else 0,
            "failing_tests": failing_tests,
            "test_distribution": test_types,
            "average_coverage": avg_coverage
        }
    
    def generate_report(self) -> str:
        """Generate a comprehensive metrics report"""
        velocity = self.get_velocity_metrics()
        quality_trends = self.get_quality_trends()
        test_health = self.get_test_health()
        
        report = f"""
# AI Development Metrics Report
Generated: {datetime.now().isoformat()}

## Development Velocity
- Total Features Implemented: {velocity.get('total_features', 0)}
- Average Features per Session: {velocity.get('avg_features_per_session', 0):.1f}
- Average Issues Resolved per Session: {velocity.get('avg_issues_per_session', 0):.1f}
- Total Tests Written: {velocity.get('total_tests', 0)}

## Test Suite Health
- Total Tests: {test_health.get('total_tests', 0)}
- Pass Rate: {test_health.get('passing_rate', 0):.1f}%
- Average Coverage: {test_health.get('average_coverage', 0):.1f}%
- Failing Tests: {test_health.get('failing_tests', 0)}

## Code Quality Trends
"""
        
        for file_path, trend in quality_trends.items():
            report += f"\n### {file_path}\n"
            report += f"- Complexity Change: {trend['complexity_change']:+.1f}\n"
            report += f"- Coverage Change: {trend['coverage_change']:+.1f}%\n"
            report += f"- Maintainability Change: {trend['maintainability_change']:+.1f}\n"
        
        return report


# Example usage functions
def track_feature_completion(tracker: AIDevMetricsTracker, feature_name: str, 
                           lines_added: int, tests_added: int, **kwargs):
    """Helper to track feature completion"""
    feature = FeatureMetric(
        feature_name=feature_name,
        issue_number=kwargs.get('issue_number'),
        lines_of_code=lines_added,
        files_created=kwargs.get('files_created', 0),
        files_modified=kwargs.get('files_modified', 0),
        tests_added=tests_added,
        tests_passing=kwargs.get('tests_passing', tests_added),
        documentation_updated=kwargs.get('docs_updated', False),
        complexity_score=kwargs.get('complexity', 1.0),
        completion_status="completed",
        session_id=tracker.session_id
    )
    tracker.track_feature(feature)


def track_test_with_evidence(tracker: AIDevMetricsTracker, test_name: str,
                           status: str, evidence: Dict[str, Any], **kwargs):
    """Helper to track test execution with evidence"""
    test_evidence = TestEvidence(
        test_name=test_name,
        test_type=kwargs.get('test_type', 'unit'),
        status=status,
        evidence=evidence,
        assertions_count=kwargs.get('assertions', 0),
        coverage_percentage=kwargs.get('coverage', 0.0),
        execution_time_ms=kwargs.get('execution_time', 0.0),
        error_message=kwargs.get('error_message')
    )
    tracker.track_test(test_evidence)