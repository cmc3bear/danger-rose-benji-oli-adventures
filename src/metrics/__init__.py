"""
AI-Driven Development Metrics Package

Provides metrics tracking for Claude-driven development that focuses on
meaningful progress indicators rather than time-based metrics.
"""

from .ai_development_metrics import (
    AIDevMetricsTracker,
    FeatureMetric,
    TestEvidence,
    CodeQualityMetric,
    SessionMetric,
    MetricType,
    track_feature_completion,
    track_test_with_evidence
)

__all__ = [
    'AIDevMetricsTracker',
    'FeatureMetric', 
    'TestEvidence',
    'CodeQualityMetric',
    'SessionMetric',
    'MetricType',
    'track_feature_completion',
    'track_test_with_evidence'
]