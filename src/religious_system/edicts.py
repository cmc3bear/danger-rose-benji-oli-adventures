"""
Core Edicts for the ClaudeEthos Religious System

Implements the five fundamental edicts that guide agent development behavior.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import re


class EvidenceType(Enum):
    """Types of evidence required for edict compliance"""
    WORK_PROOF = "work_proof"
    JUSTIFICATION = "justification"
    ERROR_ANALYSIS = "error_analysis"
    TRUTH_VERIFICATION = "truth_verification"
    DOCUMENTATION = "documentation"




class EdictType(Enum):
    """The Five Sacred Edicts"""
    EVIDENCE = "evidence"
    COMMITMENT = "commitment"
    TRANSFORMATION = "transformation"
    DIGNIFIED_ERROR = "dignified_error"
    ABSOLUTE_TRUTH = "absolute_truth"

@dataclass
class EdictViolation:
    """Represents a violation of a religious edict"""
    edict_id: str
    severity: str  # "minor", "major", "critical"
    description: str
    evidence_missing: List[EvidenceType]
    suggested_remediation: str
    timestamp: datetime


@dataclass
class EdictCompliance:
    """Represents compliance status for an edict"""
    edict_id: str
    is_compliant: bool
    confidence_score: float  # 0.0 to 1.0
    evidence_quality: float  # 0.0 to 1.0
    violations: List[EdictViolation]


class Edict:
    """Base class for all religious edicts"""
    
    def __init__(self, edict_id: str, name: str, description: str, 
                 required_evidence: List[EvidenceType]):
        self.edict_id = edict_id
        self.name = name
        self.description = description
        self.required_evidence = required_evidence
    
    def validate(self, action_data: Dict[str, Any], evidence: Dict[EvidenceType, Any]) -> EdictCompliance:
        """Validate compliance with this edict"""
        raise NotImplementedError("Subclasses must implement validate method")


class EvidenceEdict(Edict):
    """The Edict of Evidence: Everything SHALL have evidence"""
    
    def __init__(self):
        super().__init__(
            edict_id="evidence",
            name="The Edict of Evidence",
            description="Everything SHALL have evidence - evidence of the work done or evidence of why the work was needed",
            required_evidence=[EvidenceType.WORK_PROOF, EvidenceType.JUSTIFICATION]
        )
    
    def validate(self, action_data: Dict[str, Any], evidence: Dict[EvidenceType, Any]) -> EdictCompliance:
        violations = []
        
        # Must have either work proof OR justification
        has_work_proof = EvidenceType.WORK_PROOF in evidence and evidence[EvidenceType.WORK_PROOF]
        has_justification = EvidenceType.JUSTIFICATION in evidence and evidence[EvidenceType.JUSTIFICATION]
        
        if not (has_work_proof or has_justification):
            violations.append(EdictViolation(
                edict_id=self.edict_id,
                severity="critical",
                description="No evidence provided for action",
                evidence_missing=[EvidenceType.WORK_PROOF, EvidenceType.JUSTIFICATION],
                suggested_remediation="Provide either proof of work completed or justification for why work is needed",
                timestamp=datetime.now()
            ))
        
        # Calculate evidence quality
        evidence_quality = 0.0
        if has_work_proof:
            evidence_quality += self._assess_work_proof_quality(evidence[EvidenceType.WORK_PROOF])
        if has_justification:
            evidence_quality += self._assess_justification_quality(evidence[EvidenceType.JUSTIFICATION])
        
        evidence_quality = min(1.0, evidence_quality)
        
        return EdictCompliance(
            edict_id=self.edict_id,
            is_compliant=len(violations) == 0,
            confidence_score=0.9 if len(violations) == 0 else 0.1,
            evidence_quality=evidence_quality,
            violations=violations
        )
    
    def _assess_work_proof_quality(self, work_proof: Any) -> float:
        """Assess quality of work proof evidence"""
        if not work_proof:
            return 0.0
        
        score = 0.0
        if isinstance(work_proof, dict):
            # Check for key indicators of good work proof
            if work_proof.get('code_changes'):
                score += 0.3
            if work_proof.get('test_results'):
                score += 0.3
            if work_proof.get('commit_hash'):
                score += 0.2
            if work_proof.get('performance_metrics'):
                score += 0.2
        
        return score
    
    def _assess_justification_quality(self, justification: Any) -> float:
        """Assess quality of justification evidence"""
        if not justification:
            return 0.0
        
        score = 0.0
        if isinstance(justification, dict):
            if justification.get('issue_reference'):
                score += 0.3
            if justification.get('business_requirement'):
                score += 0.3
            if justification.get('technical_rationale'):
                score += 0.2
            if justification.get('stakeholder_approval'):
                score += 0.2
        
        return score


class CommitmentEdict(Edict):
    """The Edict of Commitment: Thou shall always commit"""
    
    def __init__(self):
        super().__init__(
            edict_id="commitment",
            name="The Edict of Commitment", 
            description="Thou shall always commit - work undocumented is work undone",
            required_evidence=[EvidenceType.WORK_PROOF]
        )
    
    def validate(self, action_data: Dict[str, Any], evidence: Dict[EvidenceType, Any]) -> EdictCompliance:
        violations = []
        
        work_proof = evidence.get(EvidenceType.WORK_PROOF, {})
        
        # Check for commit evidence
        if not work_proof.get('commit_hash'):
            violations.append(EdictViolation(
                edict_id=self.edict_id,
                severity="major",
                description="No commit hash provided for work",
                evidence_missing=[EvidenceType.WORK_PROOF],
                suggested_remediation="Commit changes and provide commit hash",
                timestamp=datetime.now()
            ))
        
        # Check commit message quality
        commit_message = work_proof.get('commit_message', '')
        if len(commit_message) < 10:
            violations.append(EdictViolation(
                edict_id=self.edict_id,
                severity="minor",
                description="Commit message too brief",
                evidence_missing=[],
                suggested_remediation="Provide more descriptive commit message explaining what and why",
                timestamp=datetime.now()
            ))
        
        # Calculate evidence quality based on commit practices
        evidence_quality = self._assess_commit_quality(work_proof)
        
        return EdictCompliance(
            edict_id=self.edict_id,
            is_compliant=len(violations) == 0,
            confidence_score=0.8 if len(violations) == 0 else 0.3,
            evidence_quality=evidence_quality,
            violations=violations
        )
    
    def _assess_commit_quality(self, work_proof: Dict) -> float:
        """Assess quality of commit practices"""
        score = 0.0
        
        if work_proof.get('commit_hash'):
            score += 0.4
        
        commit_message = work_proof.get('commit_message', '')
        if len(commit_message) >= 50:  # Good descriptive length
            score += 0.3
        elif len(commit_message) >= 20:  # Adequate length
            score += 0.2
        
        # Check for conventional commit format
        if re.match(r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+', commit_message):
            score += 0.3
        
        return min(1.0, score)


class TransformationEdict(Edict):
    """The Edict of Transformation: I have changed therefore I shall write"""
    
    def __init__(self):
        super().__init__(
            edict_id="transformation",
            name="The Edict of Transformation",
            description="I have changed therefore I shall write - every modification demands documentation",
            required_evidence=[EvidenceType.DOCUMENTATION]
        )
    
    def validate(self, action_data: Dict[str, Any], evidence: Dict[EvidenceType, Any]) -> EdictCompliance:
        violations = []
        
        # Check if code changes exist
        work_proof = evidence.get(EvidenceType.WORK_PROOF, {})
        has_code_changes = work_proof.get('code_changes', [])
        
        if has_code_changes:
            # If there are code changes, documentation must be updated
            documentation = evidence.get(EvidenceType.DOCUMENTATION, {})
            
            if not documentation.get('updates'):
                violations.append(EdictViolation(
                    edict_id=self.edict_id,
                    severity="major",
                    description="Code changes made without corresponding documentation updates",
                    evidence_missing=[EvidenceType.DOCUMENTATION],
                    suggested_remediation="Update README, docs, or inline comments to reflect changes",
                    timestamp=datetime.now()
                ))
        
        # Calculate documentation quality
        evidence_quality = self._assess_documentation_quality(evidence.get(EvidenceType.DOCUMENTATION, {}))
        
        return EdictCompliance(
            edict_id=self.edict_id,
            is_compliant=len(violations) == 0,
            confidence_score=0.7 if len(violations) == 0 else 0.2,
            evidence_quality=evidence_quality,
            violations=violations
        )
    
    def _assess_documentation_quality(self, documentation: Dict) -> float:
        """Assess quality of documentation updates"""
        if not documentation:
            return 0.0
        
        score = 0.0
        
        updates = documentation.get('updates', [])
        if updates:
            score += 0.5
            
            # Quality indicators
            for update in updates:
                if update.get('type') == 'readme':
                    score += 0.2
                elif update.get('type') == 'inline_comments':
                    score += 0.1
                elif update.get('type') == 'api_docs':
                    score += 0.3
        
        return min(1.0, score)


class DignifiedErrorEdict(Edict):
    """The Edict of Dignified Error: Thou shall admit errors with dignity"""
    
    def __init__(self):
        super().__init__(
            edict_id="dignified_error",
            name="The Edict of Dignified Error",
            description="Thou shall admit errors with dignity - development is a journey of enlightenment through failure",
            required_evidence=[EvidenceType.ERROR_ANALYSIS]
        )
    
    def validate(self, action_data: Dict[str, Any], evidence: Dict[EvidenceType, Any]) -> EdictCompliance:
        violations = []
        
        # Check if this is an error reporting action
        if action_data.get('action_type') == 'error_report' or action_data.get('has_errors'):
            error_analysis = evidence.get(EvidenceType.ERROR_ANALYSIS, {})
            
            if not error_analysis:
                violations.append(EdictViolation(
                    edict_id=self.edict_id,
                    severity="major",
                    description="Error occurred but no analysis provided",
                    evidence_missing=[EvidenceType.ERROR_ANALYSIS],
                    suggested_remediation="Provide error analysis including what went wrong, why, and corrective actions",
                    timestamp=datetime.now()
                ))
            else:
                # Check quality of error analysis
                if not error_analysis.get('root_cause'):
                    violations.append(EdictViolation(
                        edict_id=self.edict_id,
                        severity="minor",
                        description="Error analysis missing root cause",
                        evidence_missing=[],
                        suggested_remediation="Include root cause analysis in error report",
                        timestamp=datetime.now()
                    ))
        
        # Calculate evidence quality
        evidence_quality = self._assess_error_analysis_quality(evidence.get(EvidenceType.ERROR_ANALYSIS, {}))
        
        return EdictCompliance(
            edict_id=self.edict_id,
            is_compliant=len(violations) == 0,
            confidence_score=0.8 if len(violations) == 0 else 0.4,
            evidence_quality=evidence_quality,
            violations=violations
        )
    
    def _assess_error_analysis_quality(self, error_analysis: Dict) -> float:
        """Assess quality of error analysis"""
        if not error_analysis:
            return 1.0  # Not applicable if no errors
        
        score = 0.0
        
        if error_analysis.get('root_cause'):
            score += 0.3
        if error_analysis.get('corrective_actions'):
            score += 0.3
        if error_analysis.get('lessons_learned'):
            score += 0.2
        if error_analysis.get('prevention_measures'):
            score += 0.2
        
        return score


class AbsoluteTruthEdict(Edict):
    """The Edict of Absolute Truth: Thou shall be truthful in all things"""
    
    def __init__(self):
        super().__init__(
            edict_id="absolute_truth",
            name="The Edict of Absolute Truth",
            description="Thou shall be truthful in all things - hallucinations erode the foundation of trust",
            required_evidence=[EvidenceType.TRUTH_VERIFICATION]
        )
    
    def validate(self, action_data: Dict[str, Any], evidence: Dict[EvidenceType, Any]) -> EdictCompliance:
        violations = []
        
        # Check for truth verification evidence
        truth_verification = evidence.get(EvidenceType.TRUTH_VERIFICATION, {})
        
        # If making factual claims, must provide verification
        if action_data.get('contains_factual_claims', False):
            if not truth_verification:
                violations.append(EdictViolation(
                    edict_id=self.edict_id,
                    severity="major",
                    description="Factual claims made without verification evidence",
                    evidence_missing=[EvidenceType.TRUTH_VERIFICATION],
                    suggested_remediation="Provide sources, confidence levels, or mark as assumptions",
                    timestamp=datetime.now()
                ))
        
        # Check for confidence indicators
        if not truth_verification.get('confidence_indicators'):
            violations.append(EdictViolation(
                edict_id=self.edict_id,
                severity="minor",
                description="No confidence indicators provided for statements",
                evidence_missing=[],
                suggested_remediation="Include confidence levels for uncertain information",
                timestamp=datetime.now()
            ))
        
        # Calculate evidence quality
        evidence_quality = self._assess_truth_verification_quality(truth_verification)
        
        return EdictCompliance(
            edict_id=self.edict_id,
            is_compliant=len(violations) == 0,
            confidence_score=0.9 if len(violations) == 0 else 0.3,
            evidence_quality=evidence_quality,
            violations=violations
        )
    
    def _assess_truth_verification_quality(self, truth_verification: Dict) -> float:
        """Assess quality of truth verification"""
        if not truth_verification:
            return 0.0
        
        score = 0.0
        
        if truth_verification.get('sources'):
            score += 0.4
        if truth_verification.get('confidence_indicators'):
            score += 0.3
        if truth_verification.get('fact_distinction'):  # Facts vs opinions vs assumptions
            score += 0.3
        
        return score


class EdictValidator:
    """Validates agent actions against all religious edicts"""
    
    def __init__(self):
        self.edicts = {
            "evidence": EvidenceEdict(),
            "commitment": CommitmentEdict(),
            "transformation": TransformationEdict(),
            "dignified_error": DignifiedErrorEdict(),
            "absolute_truth": AbsoluteTruthEdict()
        }
    
    def validate_all(self, action_data: Dict[str, Any], evidence: Dict[EvidenceType, Any]) -> Dict[str, EdictCompliance]:
        """Validate action against all edicts"""
        results = {}
        
        for edict_id, edict in self.edicts.items():
            results[edict_id] = edict.validate(action_data, evidence)
        
        return results
    
    def get_overall_compliance(self, compliance_results: Dict[str, EdictCompliance]) -> Dict[str, Any]:
        """Calculate overall compliance metrics"""
        total_edicts = len(compliance_results)
        compliant_edicts = sum(1 for result in compliance_results.values() if result.is_compliant)
        
        total_violations = []
        avg_confidence = 0.0
        avg_evidence_quality = 0.0
        
        for result in compliance_results.values():
            total_violations.extend(result.violations)
            avg_confidence += result.confidence_score
            avg_evidence_quality += result.evidence_quality
        
        avg_confidence /= total_edicts
        avg_evidence_quality /= total_edicts
        
        return {
            "overall_compliance_rate": compliant_edicts / total_edicts,
            "total_violations": len(total_violations),
            "average_confidence": avg_confidence,
            "average_evidence_quality": avg_evidence_quality,
            "critical_violations": [v for v in total_violations if v.severity == "critical"],
            "major_violations": [v for v in total_violations if v.severity == "major"],
            "minor_violations": [v for v in total_violations if v.severity == "minor"]
        }