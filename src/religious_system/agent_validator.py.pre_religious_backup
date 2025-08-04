"""
Religious Agent Validator

Integrates religious edict validation into agent workflows,
providing validation, guidance, and compliance tracking.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json

from .edicts import EdictValidator, EdictCompliance, EvidenceType
from .evidence_system import EvidenceValidator, Evidence, EvidenceCollector


@dataclass
class AgentAction:
    """Represents an action taken by an agent"""
    agent_id: str
    action_type: str
    action_data: Dict[str, Any]
    timestamp: datetime
    context: Dict[str, Any]
    evidence: Dict[EvidenceType, Any]


@dataclass
class ValidationResult:
    """Result of religious validation"""
    is_compliant: bool
    overall_score: float
    edict_results: Dict[str, EdictCompliance]
    recommendations: List[str]
    required_actions: List[str]
    token_cost: int
    validation_time_ms: float


class ReligiousAgentValidator:
    """Main validator for agent actions against religious edicts"""
    
    def __init__(self, enable_async: bool = True):
        self.edict_validator = EdictValidator()
        self.evidence_validator = EvidenceValidator()
        self.evidence_collector = EvidenceCollector()
        self.enable_async = enable_async
        
        # Configuration
        self.compliance_threshold = 0.7  # Minimum score for compliance
        self.token_tracking_enabled = True
        self.performance_tracking_enabled = True
        
        # Metrics
        self.validation_history = []
        self.performance_metrics = {
            "total_validations": 0,
            "compliant_actions": 0,
            "average_validation_time": 0.0,
            "token_cost_total": 0
        }
    
    async def validate_agent_action(self, action: AgentAction) -> ValidationResult:
        """Validate an agent action against all religious edicts"""
        start_time = datetime.now()
        
        # Extract evidence from action
        evidence = self._extract_evidence(action)
        
        # Validate evidence quality first
        evidence_validation = await self._validate_evidence_quality(evidence)
        
        # Validate against edicts
        edict_results = self.edict_validator.validate_all(action.action_data, evidence)
        
        # Calculate overall compliance
        overall_metrics = self.edict_validator.get_overall_compliance(edict_results)
        
        # Generate recommendations and required actions
        recommendations = self._generate_recommendations(edict_results, evidence_validation)
        required_actions = self._generate_required_actions(edict_results)
        
        # Calculate token cost
        token_cost = self._calculate_token_cost(action, evidence, edict_results)
        
        # Calculate validation time
        validation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Create result
        result = ValidationResult(
            is_compliant=overall_metrics["overall_compliance_rate"] >= self.compliance_threshold,
            overall_score=overall_metrics["overall_compliance_rate"],
            edict_results=edict_results,
            recommendations=recommendations,
            required_actions=required_actions,
            token_cost=token_cost,
            validation_time_ms=validation_time
        )
        
        # Update metrics
        self._update_performance_metrics(result)
        
        # Store validation history
        self.validation_history.append({
            "action": action,
            "result": result,
            "timestamp": datetime.now()
        })
        
        return result
    
    def _extract_evidence(self, action: AgentAction) -> Dict[EvidenceType, Any]:
        """Extract evidence from agent action"""
        evidence = {}
        
        # Map action evidence to evidence types
        action_evidence = action.evidence
        
        if "work_proof" in action_evidence:
            evidence[EvidenceType.WORK_PROOF] = action_evidence["work_proof"]
        
        if "justification" in action_evidence:
            evidence[EvidenceType.JUSTIFICATION] = action_evidence["justification"]
        
        if "error_analysis" in action_evidence:
            evidence[EvidenceType.ERROR_ANALYSIS] = action_evidence["error_analysis"]
        
        if "truth_verification" in action_evidence:
            evidence[EvidenceType.TRUTH_VERIFICATION] = action_evidence["truth_verification"]
        
        if "documentation" in action_evidence:
            evidence[EvidenceType.DOCUMENTATION] = action_evidence["documentation"]
        
        return evidence
    
    async def _validate_evidence_quality(self, evidence: Dict[EvidenceType, Any]) -> Dict[str, Any]:
        """Validate quality of provided evidence"""
        if not self.enable_async:
            return self._validate_evidence_quality_sync(evidence)
        
        # Async validation for better performance
        validation_tasks = []
        
        for evidence_type, evidence_data in evidence.items():
            if evidence_data:
                # Create Evidence object for validation
                evidence_obj = Evidence(
                    evidence_type=evidence_type.value,
                    content=evidence_data,
                    timestamp=datetime.now(),
                    source="agent_action",
                    verification_hash="",
                    metadata={}
                )
                
                task = asyncio.create_task(
                    self._async_validate_single_evidence(evidence_obj)
                )
                validation_tasks.append((evidence_type, task))
        
        # Wait for all validations
        evidence_validation = {}
        for evidence_type, task in validation_tasks:
            evidence_validation[evidence_type.value] = await task
        
        return evidence_validation
    
    def _validate_evidence_quality_sync(self, evidence: Dict[EvidenceType, Any]) -> Dict[str, Any]:
        """Synchronous evidence validation"""
        evidence_validation = {}
        
        for evidence_type, evidence_data in evidence.items():
            if evidence_data:
                evidence_obj = Evidence(
                    evidence_type=evidence_type.value,
                    content=evidence_data,
                    timestamp=datetime.now(),
                    source="agent_action",
                    verification_hash="",
                    metadata={}
                )
                
                evidence_validation[evidence_type.value] = self.evidence_validator.validate_evidence(evidence_obj)
        
        return evidence_validation
    
    async def _async_validate_single_evidence(self, evidence: Evidence) -> Dict[str, Any]:
        """Async wrapper for evidence validation"""
        return self.evidence_validator.validate_evidence(evidence)
    
    def _generate_recommendations(self, edict_results: Dict[str, EdictCompliance], 
                                evidence_validation: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving compliance"""
        recommendations = []
        
        for edict_id, result in edict_results.items():
            if not result.is_compliant:
                for violation in result.violations:
                    recommendations.append(violation.suggested_remediation)
            
            # Evidence quality recommendations
            if result.evidence_quality < 0.7:
                recommendations.append(f"Improve evidence quality for {edict_id} edict")
        
        # Evidence validation recommendations
        for evidence_type, validation in evidence_validation.items():
            if validation.get("quality_score", 0) < 0.7:
                recommendations.extend(validation.get("recommendations", []))
        
        return list(set(recommendations))  # Remove duplicates
    
    def _generate_required_actions(self, edict_results: Dict[str, EdictCompliance]) -> List[str]:
        """Generate required actions for critical violations"""
        required_actions = []
        
        for edict_id, result in edict_results.items():
            for violation in result.violations:
                if violation.severity == "critical":
                    required_actions.append(f"CRITICAL: {violation.description}")
                elif violation.severity == "major":
                    required_actions.append(f"REQUIRED: {violation.suggested_remediation}")
        
        return required_actions
    
    def _calculate_token_cost(self, action: AgentAction, evidence: Dict[EvidenceType, Any],
                            edict_results: Dict[str, EdictCompliance]) -> int:
        """Calculate token cost of religious validation"""
        if not self.token_tracking_enabled:
            return 0
        
        # Base cost for validation process
        base_cost = 50
        
        # Cost per evidence item
        evidence_cost = len(evidence) * 30
        
        # Cost per edict validation
        edict_cost = len(edict_results) * 20
        
        # Additional cost for violations processing
        violation_cost = 0
        for result in edict_results.values():
            violation_cost += len(result.violations) * 15
        
        # Cost for generating recommendations
        recommendation_base_cost = 25
        
        total_cost = base_cost + evidence_cost + edict_cost + violation_cost + recommendation_base_cost
        
        return total_cost
    
    def _update_performance_metrics(self, result: ValidationResult) -> None:
        """Update performance tracking metrics"""
        if not self.performance_tracking_enabled:
            return
        
        self.performance_metrics["total_validations"] += 1
        
        if result.is_compliant:
            self.performance_metrics["compliant_actions"] += 1
        
        # Update average validation time
        current_avg = self.performance_metrics["average_validation_time"]
        total_validations = self.performance_metrics["total_validations"]
        new_avg = ((current_avg * (total_validations - 1)) + result.validation_time_ms) / total_validations
        self.performance_metrics["average_validation_time"] = new_avg
        
        # Update token cost
        self.performance_metrics["token_cost_total"] += result.token_cost
    
    def get_compliance_report(self, time_period_hours: int = 24) -> Dict[str, Any]:
        """Generate compliance report for specified time period"""
        cutoff_time = datetime.now() - datetime.timedelta(hours=time_period_hours)
        
        recent_validations = [
            v for v in self.validation_history 
            if v["timestamp"] >= cutoff_time
        ]
        
        if not recent_validations:
            return {"message": "No validations in specified time period"}
        
        # Calculate metrics
        total_validations = len(recent_validations)
        compliant_validations = sum(1 for v in recent_validations if v["result"].is_compliant)
        compliance_rate = compliant_validations / total_validations
        
        # Average scores by edict
        edict_scores = {}
        for validation in recent_validations:
            for edict_id, result in validation["result"].edict_results.items():
                if edict_id not in edict_scores:
                    edict_scores[edict_id] = []
                edict_scores[edict_id].append(result.confidence_score)
        
        avg_edict_scores = {
            edict_id: sum(scores) / len(scores)
            for edict_id, scores in edict_scores.items()
        }
        
        # Token efficiency
        total_tokens = sum(v["result"].token_cost for v in recent_validations)
        avg_tokens_per_validation = total_tokens / total_validations
        
        # Performance metrics
        avg_validation_time = sum(v["result"].validation_time_ms for v in recent_validations) / total_validations
        
        return {
            "time_period_hours": time_period_hours,
            "total_validations": total_validations,
            "compliance_rate": compliance_rate,
            "average_edict_scores": avg_edict_scores,
            "token_metrics": {
                "total_tokens_used": total_tokens,
                "average_tokens_per_validation": avg_tokens_per_validation,
                "tokens_per_compliant_action": total_tokens / compliant_validations if compliant_validations > 0 else 0
            },
            "performance_metrics": {
                "average_validation_time_ms": avg_validation_time,
                "validations_per_hour": total_validations / time_period_hours
            }
        }
    
    def get_edict_effectiveness_analysis(self) -> Dict[str, Any]:
        """Analyze effectiveness of each edict"""
        if not self.validation_history:
            return {"message": "No validation history available"}
        
        edict_analysis = {}
        
        for edict_id in self.edict_validator.edicts.keys():
            edict_data = {
                "total_evaluations": 0,
                "compliance_rate": 0.0,
                "average_confidence": 0.0,
                "average_evidence_quality": 0.0,
                "common_violations": [],
                "improvement_trend": 0.0
            }
            
            edict_results = []
            violation_counts = {}
            
            for validation in self.validation_history:
                result = validation["result"].edict_results.get(edict_id)
                if result:
                    edict_results.append(result)
                    edict_data["total_evaluations"] += 1
                    
                    # Count violations
                    for violation in result.violations:
                        key = violation.description
                        violation_counts[key] = violation_counts.get(key, 0) + 1
            
            if edict_results:
                compliant_count = sum(1 for r in edict_results if r.is_compliant)
                edict_data["compliance_rate"] = compliant_count / len(edict_results)
                edict_data["average_confidence"] = sum(r.confidence_score for r in edict_results) / len(edict_results)
                edict_data["average_evidence_quality"] = sum(r.evidence_quality for r in edict_results) / len(edict_results)
                
                # Most common violations
                sorted_violations = sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)
                edict_data["common_violations"] = sorted_violations[:3]
                
                # Simple trend analysis (compare first half vs second half)
                if len(edict_results) >= 4:
                    mid_point = len(edict_results) // 2
                    first_half_compliance = sum(1 for r in edict_results[:mid_point] if r.is_compliant) / mid_point
                    second_half_compliance = sum(1 for r in edict_results[mid_point:] if r.is_compliant) / (len(edict_results) - mid_point)
                    edict_data["improvement_trend"] = second_half_compliance - first_half_compliance
            
            edict_analysis[edict_id] = edict_data
        
        return edict_analysis
    
    def configure_thresholds(self, compliance_threshold: float = None, 
                           evidence_quality_threshold: float = None) -> None:
        """Configure validation thresholds"""
        if compliance_threshold is not None:
            self.compliance_threshold = max(0.0, min(1.0, compliance_threshold))
        
        if evidence_quality_threshold is not None:
            for evidence_type in self.evidence_validator.quality_thresholds:
                self.evidence_validator.quality_thresholds[evidence_type] = max(0.0, min(1.0, evidence_quality_threshold))
    
    def export_validation_data(self, file_path: str) -> bool:
        """Export validation history for analysis"""
        try:
            export_data = {
                "performance_metrics": self.performance_metrics,
                "validation_history": [
                    {
                        "timestamp": v["timestamp"].isoformat(),
                        "agent_id": v["action"].agent_id,
                        "action_type": v["action"].action_type,
                        "is_compliant": v["result"].is_compliant,
                        "overall_score": v["result"].overall_score,
                        "token_cost": v["result"].token_cost,
                        "validation_time_ms": v["result"].validation_time_ms
                    }
                    for v in self.validation_history
                ]
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
        except Exception:
            return False