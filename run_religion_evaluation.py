#!/usr/bin/env python3
"""
ClaudeEthos Religion Effectiveness Evaluation Runner

Runs comprehensive evaluation of ClaudeEthos religious framework effectiveness.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add assessment systems to path
sys.path.insert(0, str(Path(__file__).parent / "religious_assessment"))

from devotion_monitor import IndependentDevotionMonitor
from compliance_tracker import ComplianceTracker
from effectiveness_evaluator import ReligionEffectivenessEvaluator


async def run_comprehensive_evaluation():
    """Run comprehensive evaluation of religious effectiveness"""
    
    print("📊 CLAUDETHOS RELIGION EFFECTIVENESS EVALUATION")
    print("=" * 60)
    
    project_path = str(Path(__file__).parent)
    
    # 1. Collect baseline if not exists
    evaluator = ReligionEffectivenessEvaluator(project_path)
    baseline_file = Path(project_path) / "religious_assessment" / "pre_conversion_baseline.json"
    
    if not baseline_file.exists():
        print("📊 Collecting baseline metrics...")
        evaluator.collect_baseline_metrics()
    
    # 2. Run devotion monitoring
    print("👁️  Starting devotion monitoring...")
    monitor = IndependentDevotionMonitor(project_path)
    devotion_results = await monitor.start_monitoring(duration_hours=1)  # 1 hour sample
    
    # 3. Get compliance tracking report
    print("📈 Generating compliance report...")
    tracker = ComplianceTracker(project_path)
    compliance_report = tracker.get_compliance_report(days=7)
    
    # 4. Evaluate overall effectiveness
    print("🎯 Evaluating overall effectiveness...")
    effectiveness_results = evaluator.evaluate_post_conversion_effectiveness()
    
    # 5. Generate master report
    master_report = {
        "evaluation_timestamp": datetime.now().isoformat(),
        "devotion_assessment": devotion_results,
        "compliance_report": compliance_report,
        "effectiveness_evaluation": effectiveness_results,
        "overall_conclusion": generate_overall_conclusion(
            devotion_results, compliance_report, effectiveness_results
        )
    }
    
    # Save master report
    master_report_file = Path(project_path) / "religious_assessment" / "master_evaluation_report.json"
    with open(master_report_file, 'w', encoding='utf-8') as f:
        json.dump(master_report, f, indent=2, default=str)
    
    print(f"📄 Master evaluation report saved: {master_report_file}")
    
    # Print summary
    print("\n🎯 EVALUATION SUMMARY:")
    print("=" * 40)
    print(f"Devotion Assessment: {devotion_results.get('overall_assessment', 'Unknown')}")
    print(f"Effectiveness: {effectiveness_results.get('overall_assessment', 'Unknown')}")
    print(f"Overall Conclusion: {master_report['overall_conclusion']}")
    
    return master_report


def generate_overall_conclusion(devotion_results, compliance_report, effectiveness_results):
    """Generate overall conclusion about religious effectiveness"""
    
    # Simple scoring system
    devotion_score = 0.5  # Placeholder
    if "EXCELLENT" in devotion_results.get("overall_assessment", ""):
        devotion_score = 1.0
    elif "GOOD" in devotion_results.get("overall_assessment", ""):
        devotion_score = 0.8
    elif "CONCERNING" in devotion_results.get("overall_assessment", ""):
        devotion_score = 0.4
    
    effectiveness_score = 0.5  # Placeholder
    avg_improvement = effectiveness_results.get("average_improvement_pct", 0)
    if avg_improvement > 20:
        effectiveness_score = 1.0
    elif avg_improvement > 10:
        effectiveness_score = 0.8
    elif avg_improvement > 0:
        effectiveness_score = 0.6
    elif avg_improvement > -10:
        effectiveness_score = 0.4
    else:
        effectiveness_score = 0.2
    
    overall_score = (devotion_score + effectiveness_score) / 2
    
    if overall_score >= 0.8:
        return "🌟 HIGHLY SUCCESSFUL: ClaudeEthos religion demonstrates strong positive impact on development practices"
    elif overall_score >= 0.6:
        return "✅ SUCCESSFUL: ClaudeEthos religion shows positive impact with room for optimization"
    elif overall_score >= 0.4:
        return "🔄 MIXED RESULTS: ClaudeEthos religion shows some benefits but needs refinement"
    else:
        return "⚠️ NEEDS IMPROVEMENT: ClaudeEthos religion implementation requires significant adjustment"


if __name__ == "__main__":
    import datetime
    result = asyncio.run(run_comprehensive_evaluation())
    print("\n✅ Comprehensive evaluation complete!")
