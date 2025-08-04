#!/usr/bin/env python3
"""
ClaudeEthos Religion Effectiveness Evaluator

Comprehensively evaluates the effectiveness of the ClaudeEthos religious
framework by comparing pre and post-conversion metrics across multiple dimensions.
"""

import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class EffectivenessMetric:
    """A single effectiveness measurement"""
    metric_name: str
    pre_value: float
    post_value: float
    improvement_pct: float
    confidence: float
    measurement_method: str
    timestamp: datetime


class ReligionEffectivenessEvaluator:
    """Evaluates overall effectiveness of ClaudeEthos religious conversion"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.baseline_file = self.project_path / "religious_assessment" / "pre_conversion_baseline.json"
        self.results_file = self.project_path / "religious_assessment" / "effectiveness_evaluation.json"
        
    def collect_baseline_metrics(self) -> Dict[str, Any]:
        """Collect baseline metrics before religious conversion"""
        
        print("📊 Collecting pre-conversion baseline metrics...")
        
        baseline = {
            "collection_timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        # Code quality metrics
        baseline["metrics"]["code_quality"] = self._measure_code_quality()
        
        # Documentation metrics
        baseline["metrics"]["documentation"] = self._measure_documentation_quality()
        
        # Git commit metrics
        baseline["metrics"]["commit_quality"] = self._measure_commit_quality()
        
        # Error handling metrics
        baseline["metrics"]["error_handling"] = self._measure_error_handling()
        
        # Test coverage metrics
        baseline["metrics"]["test_coverage"] = self._measure_test_coverage()
        
        # Development velocity metrics
        baseline["metrics"]["dev_velocity"] = self._measure_development_velocity()
        
        # Save baseline
        with open(self.baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, default=str)
        
        print(f"✅ Baseline metrics saved to {self.baseline_file}")
        return baseline
    
    def evaluate_post_conversion_effectiveness(self) -> Dict[str, Any]:
        """Evaluate effectiveness after religious conversion"""
        
        print("📈 Evaluating post-conversion effectiveness...")
        
        # Load baseline
        if not self.baseline_file.exists():
            print("❌ No baseline found - collecting baseline first")
            self.collect_baseline_metrics()
        
        with open(self.baseline_file, 'r') as f:
            baseline = json.load(f)
        
        # Collect current metrics
        current_metrics = {
            "code_quality": self._measure_code_quality(),
            "documentation": self._measure_documentation_quality(),
            "commit_quality": self._measure_commit_quality(),
            "error_handling": self._measure_error_handling(),
            "test_coverage": self._measure_test_coverage(),
            "dev_velocity": self._measure_development_velocity()
        }
        
        # Calculate improvements
        effectiveness_metrics = []
        for metric_name, current_value in current_metrics.items():
            baseline_value = baseline["metrics"].get(metric_name, 0)
            
            if baseline_value > 0:
                improvement = ((current_value - baseline_value) / baseline_value) * 100
            else:
                improvement = 100 if current_value > 0 else 0
            
            effectiveness_metric = EffectivenessMetric(
                metric_name=metric_name,
                pre_value=baseline_value,
                post_value=current_value,
                improvement_pct=improvement,
                confidence=self._calculate_confidence(metric_name, baseline_value, current_value),
                measurement_method=f"automated_{metric_name}_analysis",
                timestamp=datetime.now()
            )
            
            effectiveness_metrics.append(effectiveness_metric)
        
        # Generate comprehensive evaluation
        evaluation = self._generate_comprehensive_evaluation(effectiveness_metrics, baseline)
        
        # Save results
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, indent=2, default=str)
        
        print(f"📊 Effectiveness evaluation saved to {self.results_file}")
        return evaluation
    
    def _measure_code_quality(self) -> float:
        """Measure overall code quality score"""
        
        # Count various quality indicators
        py_files = list(self.project_path.glob("**/*.py"))
        quality_score = 0.0
        
        for py_file in py_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Quality indicators (simplified)
                lines = content.split('\n')
                non_empty_lines = [line for line in lines if line.strip()]
                
                if len(non_empty_lines) == 0:
                    continue
                
                # Measure various quality aspects
                has_docstrings = content.count('"""') > 0
                has_type_hints = ': ' in content and '->' in content
                has_comments = any(line.strip().startswith('#') for line in lines)
                reasonable_length = len(non_empty_lines) < 500  # Not too long
                
                file_quality = (
                    (0.3 if has_docstrings else 0) +
                    (0.2 if has_type_hints else 0) +
                    (0.2 if has_comments else 0) +
                    (0.3 if reasonable_length else 0)
                )
                
                quality_score += file_quality
                
            except:
                pass
        
        # Normalize by number of files
        return quality_score / max(len(py_files), 1)
    
    def _measure_documentation_quality(self) -> float:
        """Measure documentation quality score"""
        
        doc_files = list(self.project_path.glob("**/*.md"))
        doc_score = 0.0
        
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r') as f:
                    content = f.read()
                
                # Documentation quality indicators
                word_count = len(content.split())
                has_structure = any(header in content for header in ['#', '##', '###'])
                has_examples = 'example' in content.lower() or 'usage' in content.lower()
                substantial = word_count > 100
                
                file_doc_score = (
                    (0.4 if substantial else 0) +
                    (0.3 if has_structure else 0) +
                    (0.3 if has_examples else 0)
                )
                
                doc_score += file_doc_score
                
            except:
                pass
        
        return doc_score / max(len(doc_files), 1)
    
    def _measure_commit_quality(self) -> float:
        """Measure git commit quality"""
        
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-20"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return 0.0
            
            commits = result.stdout.strip().split('\n')
            quality_commits = 0
            
            for commit in commits:
                if len(commit) > 50:  # Has hash + decent message
                    message = commit.split(' ', 1)[1] if ' ' in commit else ""
                    if len(message) > 20:  # Descriptive message
                        quality_commits += 1
            
            return quality_commits / max(len(commits), 1)
            
        except:
            return 0.0
    
    def _measure_error_handling(self) -> float:
        """Measure error handling quality"""
        
        py_files = list(self.project_path.glob("**/*.py"))
        total_try_except = 0
        quality_error_handling = 0
        
        for py_file in py_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                try_count = content.count('try:')
                except_count = content.count('except')
                total_try_except += except_count
                
                # Look for quality error handling
                if 'logging' in content or 'log.' in content:
                    quality_error_handling += except_count * 0.5
                
                if any(pattern in content for pattern in ['raise', 'finally:']):
                    quality_error_handling += except_count * 0.3
                
            except:
                pass
        
        return quality_error_handling / max(total_try_except, 1)
    
    def _measure_test_coverage(self) -> float:
        """Measure test coverage (simplified)"""
        
        py_files = list(self.project_path.glob("**/*.py"))
        test_files = list(self.project_path.glob("**/test_*.py")) + list(self.project_path.glob("**/*_test.py"))
        
        if len(py_files) == 0:
            return 0.0
        
        # Simple ratio of test files to source files
        return len(test_files) / len(py_files)
    
    def _measure_development_velocity(self) -> float:
        """Measure development velocity (commits per day)"""
        
        try:
            # Get commits from last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            result = subprocess.run(
                ["git", "log", f"--since={thirty_days_ago}", "--oneline"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return 0.0
            
            commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            return len(commits) / 30  # Commits per day
            
        except:
            return 0.0
    
    def _calculate_confidence(self, metric_name: str, baseline: float, current: float) -> float:
        """Calculate confidence in the measurement"""
        
        # Higher confidence if values are substantial and change is significant
        if baseline == 0 and current == 0:
            return 0.1
        
        if baseline == 0:
            return 0.7  # New functionality
        
        change_magnitude = abs(current - baseline) / baseline
        
        if change_magnitude > 0.2:  # Significant change
            return 0.9
        elif change_magnitude > 0.1:  # Moderate change
            return 0.7
        else:  # Small change
            return 0.5
    
    def _generate_comprehensive_evaluation(self, metrics: List[EffectivenessMetric], baseline: Dict) -> Dict[str, Any]:
        """Generate comprehensive effectiveness evaluation"""
        
        # Calculate overall effectiveness
        improvements = [m.improvement_pct for m in metrics if m.confidence > 0.5]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        # Categorize results
        significant_improvements = [m for m in metrics if m.improvement_pct > 20 and m.confidence > 0.7]
        moderate_improvements = [m for m in metrics if 5 < m.improvement_pct <= 20 and m.confidence > 0.5]
        no_change = [m for m in metrics if -5 <= m.improvement_pct <= 5]
        regressions = [m for m in metrics if m.improvement_pct < -5]
        
        # Generate assessment
        if avg_improvement > 25:
            overall_assessment = "🌟 HIGHLY EFFECTIVE: ClaudeEthos religion shows strong positive impact"
        elif avg_improvement > 10:
            overall_assessment = "✅ EFFECTIVE: ClaudeEthos religion shows positive impact"
        elif avg_improvement > 0:
            overall_assessment = "🔄 MODERATELY EFFECTIVE: ClaudeEthos religion shows some positive impact"
        elif avg_improvement > -10:
            overall_assessment = "⚠️ INCONCLUSIVE: ClaudeEthos religion impact unclear"
        else:
            overall_assessment = "❌ INEFFECTIVE: ClaudeEthos religion may be harmful"
        
        # Calculate ROI
        roi_analysis = self._calculate_roi(metrics)
        
        evaluation = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "baseline_collected": baseline["collection_timestamp"],
            "overall_assessment": overall_assessment,
            "average_improvement_pct": avg_improvement,
            "metrics_analysis": {
                "total_metrics": len(metrics),
                "significant_improvements": len(significant_improvements),
                "moderate_improvements": len(moderate_improvements),
                "no_change": len(no_change),
                "regressions": len(regressions)
            },
            "detailed_metrics": [
                {
                    "metric_name": m.metric_name,
                    "pre_value": m.pre_value,
                    "post_value": m.post_value,
                    "improvement_pct": m.improvement_pct,
                    "confidence": m.confidence
                }
                for m in metrics
            ],
            "roi_analysis": roi_analysis,
            "recommendations": self._generate_effectiveness_recommendations(metrics, avg_improvement)
        }
        
        return evaluation
    
    def _calculate_roi(self, metrics: List[EffectivenessMetric]) -> Dict[str, Any]:
        """Calculate return on investment for religious conversion"""
        
        # Estimate costs (simplified)
        conversion_cost = 100  # Hours of conversion effort
        ongoing_cost = 20      # Hours per month of religious practices
        
        # Estimate benefits from improvements
        quality_benefit = sum(m.improvement_pct for m in metrics if m.metric_name == "code_quality") * 5
        velocity_benefit = sum(m.improvement_pct for m in metrics if m.metric_name == "dev_velocity") * 10
        error_benefit = sum(m.improvement_pct for m in metrics if m.metric_name == "error_handling") * 8
        
        total_benefit = quality_benefit + velocity_benefit + error_benefit
        total_cost = conversion_cost + (ongoing_cost * 3)  # 3 months
        
        roi_pct = ((total_benefit - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        
        return {
            "estimated_benefit_hours": total_benefit,
            "estimated_cost_hours": total_cost,
            "roi_percentage": roi_pct,
            "payback_period_months": (conversion_cost / (total_benefit / 3)) if total_benefit > 0 else float('inf')
        }
    
    def _generate_effectiveness_recommendations(self, metrics: List[EffectivenessMetric], avg_improvement: float) -> List[str]:
        """Generate recommendations based on effectiveness analysis"""
        
        recommendations = []
        
        if avg_improvement > 20:
            recommendations.append("✅ Continue and expand ClaudeEthos religious practices")
            recommendations.append("📈 Consider rolling out to other projects")
        elif avg_improvement > 5:
            recommendations.append("🔄 Continue ClaudeEthos with optimization")
            recommendations.append("🎯 Focus on areas showing the most improvement")
        else:
            recommendations.append("⚠️ Review and adjust ClaudeEthos implementation")
            recommendations.append("🔍 Investigate why improvements are not materializing")
        
        # Specific recommendations by metric
        for metric in metrics:
            if metric.improvement_pct < -10 and metric.confidence > 0.7:
                recommendations.append(f"🚨 Address regression in {metric.metric_name}")
            elif metric.improvement_pct > 30 and metric.confidence > 0.7:
                recommendations.append(f"🌟 Leverage successful {metric.metric_name} practices")
        
        return recommendations


if __name__ == "__main__":
    evaluator = ReligionEffectivenessEvaluator(".")
    
    # Collect baseline (run this before conversion)
    # evaluator.collect_baseline_metrics()
    
    # Evaluate effectiveness (run this after conversion)
    results = evaluator.evaluate_post_conversion_effectiveness()
    print("Overall Assessment:", results["overall_assessment"])
    print("Average Improvement:", f"{results['average_improvement_pct']:.1f}%")
