"""
Evidence-Based Testing Package

Provides tools for generating objective, qualified evidence from test executions.
"""

from .evidence_based_output import (
    EvidenceBasedTestCase,
    EvidenceCollector,
    TestEvidence,
    pytest_evidence_decorator
)

__all__ = [
    'EvidenceBasedTestCase',
    'EvidenceCollector',
    'TestEvidence',
    'pytest_evidence_decorator'
]