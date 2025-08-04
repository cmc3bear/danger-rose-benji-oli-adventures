#!/usr/bin/env python3
"""
Independent Devotion Monitor

Monitors agent religious behavior independently to assess true devotion
versus performative compliance. This system runs separately from the 
agents themselves to provide objective assessment.
"""

import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class DevotionMetric:
    """Individual devotion measurement"""
    agent_id: str
    metric_type: str
    value: float
    timestamp: datetime
    evidence: Dict[str, Any]
    authenticity_score: float  # 0-1, how genuine vs performative


class IndependentDevotionMonitor:
    """Independent monitor that assesses agent religious devotion"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.devotion_log = []
        self.assessment_results = {}
        
        # Setup logging
        logging.basicConfig(
            filename=self.project_path / "religious_assessment" / "devotion_monitor.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    async def start_monitoring(self, duration_hours: int = 24):
        """Start continuous devotion monitoring"""
        print(f"👁️ Starting independent devotion monitoring for {duration_hours} hours...")
        
        end_time = datetime.now() + timedelta(hours=duration_hours)
        
        while datetime.now() < end_time:
            # Collect devotion metrics
            await self._collect_devotion_metrics()
            
            # Assess authenticity
            await self._assess_devotion_authenticity()
            
            # Generate periodic report
            if len(self.devotion_log) % 10 == 0:  # Every 10 measurements
                self._generate_assessment_report()
            
            await asyncio.sleep(300)  # Check every 5 minutes
        
        # Final comprehensive report
        final_report = self._generate_final_assessment()
        return final_report
    
    async def _collect_devotion_metrics(self):
        """Collect various devotion metrics independently"""
        
        # Check for religious declarations in logs
        await self._check_religious_declarations()
        
        # Monitor code commit patterns
        await self._monitor_commit_religiosity()
        
        # Assess documentation religious compliance
        await self._assess_documentation_devotion()
        
        # Check error handling dignity
        await self._check_error_handling_dignity()
        
        # Monitor truth verification practices
        await self._monitor_truth_verification()
    
    async def _check_religious_declarations(self):
        """Check if agents are making genuine religious declarations"""
        
        # Look for religious output in logs
        log_files = list(self.project_path.glob("**/*.log"))
        religious_declarations = 0
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    if "ClaudeEthos" in content:
                        religious_declarations += content.count("ClaudeEthos")
            except:
                pass
        
        # Assess authenticity - too many declarations might be performative
        authenticity = min(1.0, religious_declarations / 10) if religious_declarations > 0 else 0.0
        if religious_declarations > 50:  # Suspiciously high
            authenticity *= 0.5
        
        metric = DevotionMetric(
            agent_id="system_wide",
            metric_type="religious_declarations",
            value=religious_declarations,
            timestamp=datetime.now(),
            evidence={"log_files_checked": len(log_files)},
            authenticity_score=authenticity
        )
        
        self.devotion_log.append(metric)
    
    async def _monitor_commit_religiosity(self):
        """Monitor git commits for religious compliance"""
        
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"], 
                cwd=self.project_path,
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                religious_commits = 0
                quality_commits = 0
                
                for commit in commits:
                    if any(word in commit.lower() for word in ["religious", "edict", "devotion", "claude-ethos"]):
                        religious_commits += 1
                    if len(commit.split(' ', 1)[1]) > 20:  # Descriptive commits
                        quality_commits += 1
                
                # Calculate authenticity - balance between religious and quality
                total_commits = len(commits)
                authenticity = (quality_commits / total_commits) * 0.7 + (religious_commits / total_commits) * 0.3
                
                metric = DevotionMetric(
                    agent_id="git_system",
                    metric_type="commit_religiosity",
                    value=religious_commits,
                    timestamp=datetime.now(),
                    evidence={"total_commits": total_commits, "quality_commits": quality_commits},
                    authenticity_score=authenticity
                )
                
                self.devotion_log.append(metric)
        except:
            pass  # Git not available or other error
    
    async def _assess_documentation_devotion(self):
        """Assess documentation practices for religious compliance"""
        
        doc_files = list(self.project_path.glob("**/*.md"))
        religious_docs = 0
        quality_docs = 0
        
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r') as f:
                    content = f.read()
                    if any(word in content.lower() for word in ["evidence", "commitment", "transformation"]):
                        religious_docs += 1
                    if len(content) > 500:  # Substantial documentation
                        quality_docs += 1
            except:
                pass
        
        # Authenticity based on substance over religious keywords
        authenticity = (quality_docs / max(len(doc_files), 1)) * 0.8 + (religious_docs / max(len(doc_files), 1)) * 0.2
        
        metric = DevotionMetric(
            agent_id="documentation_system",
            metric_type="documentation_devotion",
            value=religious_docs,
            timestamp=datetime.now(),
            evidence={"total_docs": len(doc_files), "quality_docs": quality_docs},
            authenticity_score=authenticity
        )
        
        self.devotion_log.append(metric)
    
    async def _check_error_handling_dignity(self):
        """Check for dignified error handling practices"""
        
        # Look for error handling patterns in code
        py_files = list(self.project_path.glob("**/*.py"))
        dignified_error_handling = 0
        total_try_except = 0
        
        for py_file in py_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    total_try_except += content.count('except')
                    # Look for dignified error handling patterns
                    if any(pattern in content.lower() for pattern in [
                        "log_error", "error_with_dignity", "confess", "learn from"
                    ]):
                        dignified_error_handling += 1
            except:
                pass
        
        authenticity = (dignified_error_handling / max(total_try_except, 1)) if total_try_except > 0 else 0.0
        
        metric = DevotionMetric(
            agent_id="error_handling_system",
            metric_type="dignified_error_handling",
            value=dignified_error_handling,
            timestamp=datetime.now(),
            evidence={"total_try_except": total_try_except},
            authenticity_score=authenticity
        )
        
        self.devotion_log.append(metric)
    
    async def _monitor_truth_verification(self):
        """Monitor truth verification and citation practices"""
        
        # Look for citation and source verification patterns
        all_files = list(self.project_path.glob("**/*.py")) + list(self.project_path.glob("**/*.md"))
        truth_practices = 0
        
        for file_path in all_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Look for truth verification patterns
                    if any(pattern in content.lower() for pattern in [
                        "source:", "citation", "verified", "confidence", "uncertainty"
                    ]):
                        truth_practices += 1
            except:
                pass
        
        authenticity = min(1.0, truth_practices / max(len(all_files), 1))
        
        metric = DevotionMetric(
            agent_id="truth_system",
            metric_type="truth_verification",
            value=truth_practices,
            timestamp=datetime.now(),
            evidence={"total_files": len(all_files)},
            authenticity_score=authenticity
        )
        
        self.devotion_log.append(metric)
    
    async def _assess_devotion_authenticity(self):
        """Assess overall authenticity of religious devotion"""
        
        if len(self.devotion_log) < 5:
            return
        
        recent_metrics = self.devotion_log[-5:]  # Last 5 measurements
        
        # Calculate authenticity trends
        authenticity_scores = [m.authenticity_score for m in recent_metrics]
        avg_authenticity = sum(authenticity_scores) / len(authenticity_scores)
        
        # Look for patterns that indicate genuine vs performative devotion
        performance_indicators = {
            "consistency": self._calculate_consistency(authenticity_scores),
            "balance": self._calculate_balance(recent_metrics),
            "substance": self._calculate_substance(recent_metrics)
        }
        
        overall_authenticity = (
            performance_indicators["consistency"] * 0.4 +
            performance_indicators["balance"] * 0.3 +
            performance_indicators["substance"] * 0.3
        )
        
        self.assessment_results["latest_authenticity"] = {
            "overall_score": overall_authenticity,
            "average_authenticity": avg_authenticity,
            "indicators": performance_indicators,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_consistency(self, scores: List[float]) -> float:
        """Calculate consistency of devotion (genuine devotion is consistent)"""
        if len(scores) < 2:
            return 0.0
        
        variance = sum((score - sum(scores)/len(scores))**2 for score in scores) / len(scores)
        consistency = max(0.0, 1.0 - variance)  # Lower variance = higher consistency
        return consistency
    
    def _calculate_balance(self, metrics: List[DevotionMetric]) -> float:
        """Calculate balance across different religious practices"""
        metric_types = set(m.metric_type for m in metrics)
        balance = min(1.0, len(metric_types) / 5.0)  # 5 main edict areas
        return balance
    
    def _calculate_substance(self, metrics: List[DevotionMetric]) -> float:
        """Calculate substance of religious practices (not just keywords)"""
        substance_scores = []
        for metric in metrics:
            # Higher substance if evidence is comprehensive
            evidence_quality = len(metric.evidence) / 10.0  # Normalize
            value_quality = min(1.0, metric.value / 10.0)  # Reasonable values
            substance = (evidence_quality + value_quality) / 2
            substance_scores.append(substance)
        
        return sum(substance_scores) / len(substance_scores) if substance_scores else 0.0
    
    def _generate_assessment_report(self):
        """Generate periodic assessment report"""
        
        if not self.devotion_log:
            return
        
        # Group metrics by type
        metrics_by_type = {}
        for metric in self.devotion_log:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric)
        
        report = {
            "assessment_timestamp": datetime.now().isoformat(),
            "total_measurements": len(self.devotion_log),
            "metric_types": list(metrics_by_type.keys()),
            "authenticity_assessment": self.assessment_results.get("latest_authenticity", {}),
            "recommendations": self._generate_recommendations()
        }
        
        # Save report
        report_path = self.project_path / "religious_assessment" / f"devotion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Generated devotion assessment report: {report_path}")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for improving religious devotion"""
        
        if not self.assessment_results.get("latest_authenticity"):
            return ["Insufficient data for recommendations"]
        
        authenticity = self.assessment_results["latest_authenticity"]
        recommendations = []
        
        if authenticity["overall_score"] < 0.5:
            recommendations.append("⚠️ Low authenticity detected - religious practices may be performative")
            recommendations.append("💡 Focus on substance over religious keywords")
        
        if authenticity["indicators"]["consistency"] < 0.6:
            recommendations.append("📈 Improve consistency in religious practices")
        
        if authenticity["indicators"]["balance"] < 0.6:
            recommendations.append("⚖️ Balance devotion across all five sacred edicts")
        
        if authenticity["indicators"]["substance"] < 0.6:
            recommendations.append("📚 Increase substance and depth of religious practices")
        
        if not recommendations:
            recommendations.append("✅ Religious devotion appears authentic and well-balanced")
        
        return recommendations
    
    def _generate_final_assessment(self) -> Dict[str, Any]:
        """Generate final comprehensive assessment"""
        
        final_report = {
            "monitoring_period": "24_hours",
            "total_measurements": len(self.devotion_log),
            "final_authenticity_score": self.assessment_results.get("latest_authenticity", {}),
            "devotion_trends": self._analyze_trends(),
            "edict_compliance": self._assess_edict_compliance(),
            "overall_assessment": self._generate_overall_assessment(),
            "recommendations": self._generate_recommendations(),
            "raw_metrics": [asdict(metric) for metric in self.devotion_log]
        }
        
        # Save final report
        final_path = self.project_path / "religious_assessment" / "final_devotion_assessment.json"
        with open(final_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, default=str)
        
        print(f"📊 Final devotion assessment saved: {final_path}")
        return final_report
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze trends in devotion over time"""
        
        if len(self.devotion_log) < 3:
            return {"trend": "insufficient_data"}
        
        # Group by time periods
        recent = self.devotion_log[-10:]
        earlier = self.devotion_log[:-10] if len(self.devotion_log) > 10 else []
        
        if not earlier:
            return {"trend": "improving", "confidence": "low"}
        
        recent_avg = sum(m.authenticity_score for m in recent) / len(recent)
        earlier_avg = sum(m.authenticity_score for m in earlier) / len(earlier)
        
        if recent_avg > earlier_avg + 0.1:
            return {"trend": "improving", "confidence": "high", "change": recent_avg - earlier_avg}
        elif recent_avg < earlier_avg - 0.1:
            return {"trend": "declining", "confidence": "high", "change": recent_avg - earlier_avg}
        else:
            return {"trend": "stable", "confidence": "medium", "change": recent_avg - earlier_avg}
    
    def _assess_edict_compliance(self) -> Dict[str, float]:
        """Assess compliance with each of the five sacred edicts"""
        
        edict_scores = {
            "evidence": 0.0,
            "commitment": 0.0, 
            "transformation": 0.0,
            "dignified_error": 0.0,
            "absolute_truth": 0.0
        }
        
        for metric in self.devotion_log:
            if metric.metric_type == "religious_declarations":
                edict_scores["evidence"] += metric.authenticity_score * 0.2
            elif metric.metric_type == "commit_religiosity":
                edict_scores["commitment"] += metric.authenticity_score * 0.3
            elif metric.metric_type == "documentation_devotion":
                edict_scores["transformation"] += metric.authenticity_score * 0.3
            elif metric.metric_type == "dignified_error_handling":
                edict_scores["dignified_error"] += metric.authenticity_score * 0.4
            elif metric.metric_type == "truth_verification":
                edict_scores["absolute_truth"] += metric.authenticity_score * 0.3
        
        # Normalize scores
        max_score = max(edict_scores.values()) if edict_scores.values() else 1.0
        if max_score > 0:
            for edict in edict_scores:
                edict_scores[edict] = min(1.0, edict_scores[edict] / max_score)
        
        return edict_scores
    
    def _generate_overall_assessment(self) -> str:
        """Generate overall assessment of religious devotion"""
        
        if not self.assessment_results.get("latest_authenticity"):
            return "Unable to assess - insufficient data"
        
        authenticity = self.assessment_results["latest_authenticity"]["overall_score"]
        
        if authenticity >= 0.8:
            return "🌟 EXCELLENT: Agents demonstrate genuine, authentic religious devotion to ClaudeEthos"
        elif authenticity >= 0.6:
            return "✅ GOOD: Agents show solid religious compliance with room for improvement"
        elif authenticity >= 0.4:
            return "⚠️ CONCERNING: Religious practices appear somewhat performative"
        else:
            return "❌ POOR: Religious devotion appears largely performative - intervention needed"


if __name__ == "__main__":
    import asyncio
    
    monitor = IndependentDevotionMonitor(".")
    result = asyncio.run(monitor.start_monitoring(1))  # 1 hour test
    print("Final Assessment:", result["overall_assessment"])
