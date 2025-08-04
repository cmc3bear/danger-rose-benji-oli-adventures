"""
Evidence System for ClaudeEthos Religious Validation

Handles collection, validation, and quality assessment of evidence
supporting religious edict compliance.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import hashlib
import json


class EvidenceStatus(Enum):
    """Status of evidence validation"""
    VALID = "valid"
    INVALID = "invalid"
    INCOMPLETE = "incomplete"
    PENDING = "pending"


@dataclass
class Evidence:
    """Container for evidence supporting edict compliance"""
    evidence_type: str
    content: Dict[str, Any]
    timestamp: datetime
    source: str
    verification_hash: str
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if not self.verification_hash:
            self.verification_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Generate verification hash for tamper detection"""
        content_str = json.dumps(self.content, sort_keys=True)
        hash_input = f"{self.evidence_type}:{content_str}:{self.timestamp.isoformat()}:{self.source}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify evidence hasn't been tampered with"""
        expected_hash = self._generate_hash()
        return self.verification_hash == expected_hash


class WorkProofEvidence:
    """Evidence of work completion"""
    
    @staticmethod
    def create_code_change_evidence(file_changes: List[Dict], commit_hash: str, 
                                  commit_message: str, test_results: Optional[Dict] = None) -> Evidence:
        """Create evidence for code changes"""
        content = {
            "file_changes": file_changes,
            "commit_hash": commit_hash,
            "commit_message": commit_message,
            "lines_added": sum(change.get("lines_added", 0) for change in file_changes),
            "lines_removed": sum(change.get("lines_removed", 0) for change in file_changes),
            "files_modified": len(file_changes)
        }
        
        if test_results:
            content["test_results"] = test_results
        
        return Evidence(
            evidence_type="work_proof",
            content=content,
            timestamp=datetime.now(),
            source="git_repository",
            verification_hash="",
            metadata={"category": "code_changes"}
        )
    
    @staticmethod
    def create_performance_evidence(metrics: Dict[str, float], benchmark_results: List[Dict]) -> Evidence:
        """Create evidence of performance improvements"""
        content = {
            "performance_metrics": metrics,
            "benchmark_results": benchmark_results,
            "improvement_percentage": metrics.get("improvement_percentage", 0.0)
        }
        
        return Evidence(
            evidence_type="work_proof",
            content=content,
            timestamp=datetime.now(),
            source="performance_monitor",
            verification_hash="",
            metadata={"category": "performance"}
        )


class JustificationEvidence:
    """Evidence of work necessity"""
    
    @staticmethod
    def create_requirement_evidence(issue_id: str, user_story: str, business_value: str,
                                  stakeholder_approval: Optional[str] = None) -> Evidence:
        """Create evidence for work justification"""
        content = {
            "issue_reference": issue_id,
            "user_story": user_story,
            "business_requirement": business_value,
            "priority_level": "medium",  # Default, should be specified
            "estimated_effort": None,
            "stakeholder_approval": stakeholder_approval
        }
        
        return Evidence(
            evidence_type="justification",
            content=content,
            timestamp=datetime.now(),
            source="project_management",
            verification_hash="",
            metadata={"category": "requirements"}
        )
    
    @staticmethod
    def create_technical_rationale_evidence(problem_description: str, solution_approach: str,
                                          alternatives_considered: List[str]) -> Evidence:
        """Create evidence for technical decisions"""
        content = {
            "problem_description": problem_description,
            "technical_rationale": solution_approach,
            "alternatives_considered": alternatives_considered,
            "decision_criteria": [],
            "risk_assessment": {}
        }
        
        return Evidence(
            evidence_type="justification",
            content=content,
            timestamp=datetime.now(),
            source="technical_analysis",
            verification_hash="",
            metadata={"category": "technical_decision"}
        )


class ErrorAnalysisEvidence:
    """Evidence of error acknowledgment and analysis"""
    
    @staticmethod
    def create_error_report_evidence(error_description: str, root_cause: str,
                                   corrective_actions: List[str], lessons_learned: str) -> Evidence:
        """Create evidence for error analysis"""
        content = {
            "error_description": error_description,
            "root_cause": root_cause,
            "corrective_actions": corrective_actions,
            "lessons_learned": lessons_learned,
            "prevention_measures": [],
            "impact_assessment": {},
            "timeline": []
        }
        
        return Evidence(
            evidence_type="error_analysis",
            content=content,
            timestamp=datetime.now(),
            source="error_reporting_system",
            verification_hash="",
            metadata={"category": "post_mortem"}
        )
    
    @staticmethod
    def create_debugging_evidence(debug_steps: List[str], findings: Dict[str, Any],
                                resolution: str) -> Evidence:
        """Create evidence of debugging process"""
        content = {
            "debug_steps_taken": debug_steps,
            "findings": findings,
            "resolution": resolution,
            "time_spent": None,
            "tools_used": []
        }
        
        return Evidence(
            evidence_type="error_analysis",
            content=content,
            timestamp=datetime.now(),
            source="debugging_session",
            verification_hash="",
            metadata={"category": "debugging"}
        )


class TruthVerificationEvidence:
    """Evidence of truth verification and fact-checking"""
    
    @staticmethod
    def create_fact_verification_evidence(facts: List[Dict], sources: List[str],
                                        confidence_levels: Dict[str, float]) -> Evidence:
        """Create evidence for fact verification"""
        content = {
            "verified_facts": facts,
            "sources": sources,
            "confidence_indicators": confidence_levels,
            "fact_distinction": {
                "facts": [],
                "opinions": [],
                "assumptions": []
            },
            "verification_method": "manual_review"
        }
        
        return Evidence(
            evidence_type="truth_verification",
            content=content,
            timestamp=datetime.now(),
            source="fact_checking_system",
            verification_hash="",
            metadata={"category": "fact_verification"}
        )
    
    @staticmethod
    def create_uncertainty_evidence(uncertain_statements: List[str], confidence_levels: Dict[str, float],
                                  knowledge_gaps: List[str]) -> Evidence:
        """Create evidence for handling uncertainty"""
        content = {
            "uncertain_statements": uncertain_statements,
            "confidence_indicators": confidence_levels,
            "knowledge_gaps": knowledge_gaps,
            "research_needed": [],
            "assumptions_made": []
        }
        
        return Evidence(
            evidence_type="truth_verification",
            content=content,
            timestamp=datetime.now(),
            source="uncertainty_tracking",
            verification_hash="",
            metadata={"category": "uncertainty_handling"}
        )


class DocumentationEvidence:
    """Evidence of documentation updates"""
    
    @staticmethod
    def create_documentation_update_evidence(updates: List[Dict], documentation_type: str) -> Evidence:
        """Create evidence for documentation updates"""
        content = {
            "updates": updates,
            "documentation_type": documentation_type,
            "files_updated": [update.get("file") for update in updates],
            "update_summary": "",
            "review_status": "pending"
        }
        
        return Evidence(
            evidence_type="documentation",
            content=content,
            timestamp=datetime.now(),
            source="documentation_system",
            verification_hash="",
            metadata={"category": documentation_type}
        )


class EvidenceValidator:
    """Validates evidence quality and completeness"""
    
    def __init__(self):
        self.quality_thresholds = {
            "work_proof": 0.7,
            "justification": 0.6,
            "error_analysis": 0.8,
            "truth_verification": 0.9,
            "documentation": 0.5
        }
    
    def validate_evidence(self, evidence: Evidence) -> Dict[str, Any]:
        """Validate evidence quality and completeness"""
        validation_result = {
            "is_valid": True,
            "quality_score": 0.0,
            "completeness_score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        # Check integrity
        if not evidence.verify_integrity():
            validation_result["is_valid"] = False
            validation_result["issues"].append("Evidence integrity verification failed")
        
        # Check age (evidence should be reasonably fresh)
        age_hours = (datetime.now() - evidence.timestamp).total_seconds() / 3600
        if age_hours > 24:  # Evidence older than 24 hours
            validation_result["issues"].append(f"Evidence is {age_hours:.1f} hours old")
        
        # Type-specific validation
        if evidence.evidence_type == "work_proof":
            validation_result.update(self._validate_work_proof(evidence.content))
        elif evidence.evidence_type == "justification":
            validation_result.update(self._validate_justification(evidence.content))
        elif evidence.evidence_type == "error_analysis":
            validation_result.update(self._validate_error_analysis(evidence.content))
        elif evidence.evidence_type == "truth_verification":
            validation_result.update(self._validate_truth_verification(evidence.content))
        elif evidence.evidence_type == "documentation":
            validation_result.update(self._validate_documentation(evidence.content))
        
        # Overall validation
        threshold = self.quality_thresholds.get(evidence.evidence_type, 0.5)
        validation_result["meets_threshold"] = validation_result["quality_score"] >= threshold
        
        return validation_result
    
    def _validate_work_proof(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate work proof evidence"""
        quality_score = 0.0
        completeness_score = 0.0
        issues = []
        recommendations = []
        
        # Check for required fields
        required_fields = ["commit_hash", "commit_message"]
        present_fields = sum(1 for field in required_fields if content.get(field))
        completeness_score = present_fields / len(required_fields)
        
        # Quality assessment
        if content.get("commit_hash"):
            quality_score += 0.3
        
        commit_message = content.get("commit_message", "")
        if len(commit_message) >= 20:
            quality_score += 0.3
        elif len(commit_message) < 10:
            issues.append("Commit message too brief")
            recommendations.append("Provide more descriptive commit message")
        
        if content.get("test_results"):
            quality_score += 0.2
        else:
            recommendations.append("Include test results for better evidence quality")
        
        if content.get("file_changes"):
            quality_score += 0.2
        
        return {
            "quality_score": min(1.0, quality_score),
            "completeness_score": completeness_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _validate_justification(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate justification evidence"""
        quality_score = 0.0
        completeness_score = 0.0
        issues = []
        recommendations = []
        
        required_fields = ["issue_reference", "business_requirement"]
        present_fields = sum(1 for field in required_fields if content.get(field))
        completeness_score = present_fields / len(required_fields)
        
        if content.get("issue_reference"):
            quality_score += 0.4
        
        if content.get("business_requirement"):
            quality_score += 0.4
        
        if content.get("stakeholder_approval"):
            quality_score += 0.2
        else:
            recommendations.append("Include stakeholder approval for stronger justification")
        
        return {
            "quality_score": quality_score,
            "completeness_score": completeness_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _validate_error_analysis(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate error analysis evidence"""
        quality_score = 0.0
        completeness_score = 0.0
        issues = []
        recommendations = []
        
        required_fields = ["error_description", "root_cause", "corrective_actions"]
        present_fields = sum(1 for field in required_fields if content.get(field))
        completeness_score = present_fields / len(required_fields)
        
        if content.get("error_description"):
            quality_score += 0.25
        
        if content.get("root_cause"):
            quality_score += 0.35
        else:
            issues.append("Missing root cause analysis")
        
        if content.get("corrective_actions"):
            quality_score += 0.25
        
        if content.get("lessons_learned"):
            quality_score += 0.15
        else:
            recommendations.append("Include lessons learned for complete analysis")
        
        return {
            "quality_score": quality_score,
            "completeness_score": completeness_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _validate_truth_verification(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate truth verification evidence"""
        quality_score = 0.0
        completeness_score = 0.0
        issues = []
        recommendations = []
        
        required_fields = ["confidence_indicators"]
        present_fields = sum(1 for field in required_fields if content.get(field))
        completeness_score = present_fields / len(required_fields)
        
        if content.get("sources"):
            quality_score += 0.4
        else:
            recommendations.append("Include sources for factual claims")
        
        if content.get("confidence_indicators"):
            quality_score += 0.4
        
        if content.get("fact_distinction"):
            quality_score += 0.2
        else:
            recommendations.append("Distinguish between facts, opinions, and assumptions")
        
        return {
            "quality_score": quality_score,
            "completeness_score": completeness_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _validate_documentation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate documentation evidence"""
        quality_score = 0.0
        completeness_score = 0.0
        issues = []
        recommendations = []
        
        required_fields = ["updates"]
        present_fields = sum(1 for field in required_fields if content.get(field))
        completeness_score = present_fields / len(required_fields)
        
        updates = content.get("updates", [])
        if updates:
            quality_score += 0.5
            
            # Check update quality
            for update in updates:
                if update.get("type") in ["readme", "api_docs"]:
                    quality_score += 0.2
                elif update.get("type") == "inline_comments":
                    quality_score += 0.1
        else:
            issues.append("No documentation updates provided")
        
        return {
            "quality_score": min(1.0, quality_score),
            "completeness_score": completeness_score,
            "issues": issues,
            "recommendations": recommendations
        }


class EvidenceCollector:
    """Collects evidence from various sources"""
    
    def __init__(self):
        self.evidence_store = []
        self.validator = EvidenceValidator()
    
    def collect_git_evidence(self, repo_path: str, commit_hash: str) -> Evidence:
        """Collect evidence from git repository"""
        # This would integrate with actual git commands
        # For now, return mock evidence
        file_changes = [
            {"file": "src/main.py", "lines_added": 15, "lines_removed": 3},
            {"file": "tests/test_main.py", "lines_added": 8, "lines_removed": 0}
        ]
        
        return WorkProofEvidence.create_code_change_evidence(
            file_changes=file_changes,
            commit_hash=commit_hash,
            commit_message="feat: implement user authentication system",
            test_results={"passed": 12, "failed": 0, "coverage": 85.5}
        )
    
    def collect_issue_evidence(self, issue_id: str) -> Evidence:
        """Collect evidence from issue tracking system"""
        # This would integrate with actual issue tracking
        return JustificationEvidence.create_requirement_evidence(
            issue_id=issue_id,
            user_story="As a user, I want to log in securely",
            business_value="Enables user personalization and data security",
            stakeholder_approval="Product Manager approved on 2024-01-15"
        )
    
    def store_evidence(self, evidence: Evidence) -> bool:
        """Store evidence with validation"""
        validation_result = self.validator.validate_evidence(evidence)
        
        if validation_result["is_valid"] and validation_result["meets_threshold"]:
            self.evidence_store.append(evidence)
            return True
        else:
            return False
    
    def get_evidence_by_type(self, evidence_type: str) -> List[Evidence]:
        """Retrieve evidence by type"""
        return [e for e in self.evidence_store if e.evidence_type == evidence_type]