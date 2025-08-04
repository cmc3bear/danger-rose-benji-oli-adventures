#!/usr/bin/env python3
"""
Automated OQE Validation Script for Issue #31 - Traffic Passing Logic

This script provides instructions and helpers for running the required
OQE baseline testing to validate the traffic passing logic implementation.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path


def print_test_instructions():
    """Print clear instructions for running the OQE validation tests."""
    print("=" * 70)
    print("ISSUE #31 - TRAFFIC PASSING LOGIC OQE VALIDATION")
    print("=" * 70)
    print()
    print("This validation requires two 15-minute test sessions:")
    print("1. BASELINE session (AI disabled)")
    print("2. AI-ENABLED session (intelligent passing active)")
    print()
    print("CONTROLS:")
    print("  F11 - Toggle baseline mode (shows current mode)")
    print("  F10 - Start new OQE session (resets metrics)")  
    print("  F9  - Export session report (saves to pipeline_reports/)")
    print()
    print("TEST PROCEDURE:")
    print()
    print("SESSION 1 - BASELINE (15 minutes):")
    print("  1. Start the game: python -m src.main")
    print("  2. Navigate to Drive scene")
    print("  3. Press F11 to enable BASELINE mode")
    print("  4. Press F10 to start OQE session")
    print("  5. Drive normally for 15 minutes")
    print("  6. Press F9 to export baseline report")
    print()
    print("SESSION 2 - AI-ENABLED (15 minutes):")
    print("  1. Stay in Drive scene (or restart game)")
    print("  2. Press F11 to enable AI mode") 
    print("  3. Press F10 to start new OQE session")
    print("  4. Drive normally for 15 minutes")
    print("  5. Press F9 to export AI-enabled report")
    print()
    print("WHAT TO OBSERVE:")
    print("  - Traffic behavior differences")
    print("  - Lane utilization patterns")
    print("  - Passing frequency")
    print("  - Traffic flow smoothness")
    print("  - Any performance issues")
    print()
    print("Reports will be saved to: pipeline_reports/oqe_session_*.json")
    print("=" * 70)


def analyze_oqe_reports():
    """Analyze existing OQE reports and generate comparison."""
    reports_dir = Path("pipeline_reports")
    if not reports_dir.exists():
        print("No reports found. Run the test sessions first.")
        return
        
    # Find baseline and AI-enabled reports
    baseline_reports = list(reports_dir.glob("oqe_session_baseline_*.json"))
    ai_reports = list(reports_dir.glob("oqe_session_ai_enabled_*.json"))
    
    if not baseline_reports:
        print("No baseline reports found. Complete baseline session first.")
        return
        
    if not ai_reports:
        print("No AI-enabled reports found. Complete AI session first.")
        return
        
    # Use most recent reports
    latest_baseline = max(baseline_reports, key=lambda p: p.stat().st_mtime)
    latest_ai = max(ai_reports, key=lambda p: p.stat().st_mtime)
    
    print(f"\nAnalyzing reports:")
    print(f"  Baseline: {latest_baseline.name}")
    print(f"  AI-Enabled: {latest_ai.name}")
    
    # Load reports
    with open(latest_baseline) as f:
        baseline_data = json.load(f)
    with open(latest_ai) as f:
        ai_data = json.load(f)
        
    # Generate comparison
    print("\n" + "=" * 70)
    print("OQE VALIDATION RESULTS - ISSUE #31")
    print("=" * 70)
    
    # Extract key metrics
    baseline_summary = baseline_data.get("summary", {})
    ai_summary = ai_data.get("summary", {})
    
    baseline_evidence = baseline_data.get("oqe_evidence", {})
    ai_evidence = ai_data.get("oqe_evidence", {})
    
    # Performance comparison
    print("\nPERFORMANCE METRICS:")
    print(f"  Average FPS:")
    print(f"    Baseline:   {baseline_summary.get('average_fps', 0):.1f}")
    print(f"    AI-Enabled: {ai_summary.get('average_fps', 0):.1f}")
    
    print(f"  Scan Time (ms):")
    print(f"    Baseline:   {baseline_summary.get('average_scan_time_ms', 0):.2f}")
    print(f"    AI-Enabled: {ai_summary.get('average_scan_time_ms', 0):.2f}")
    
    print(f"  Memory Increase (MB):")
    print(f"    Baseline:   {baseline_summary.get('memory_increase_mb', 0):.1f}")
    print(f"    AI-Enabled: {ai_summary.get('memory_increase_mb', 0):.1f}")
    
    # Behavioral comparison
    print("\nBEHAVIORAL METRICS:")
    print(f"  Total Passes:")
    print(f"    Baseline:   {baseline_summary.get('total_passes', 0)}")
    print(f"    AI-Enabled: {ai_summary.get('total_passes', 0)}")
    
    print(f"  Pass Rate (per minute):")
    print(f"    Baseline:   {baseline_summary.get('pass_rate_per_minute', 0):.2f}")
    print(f"    AI-Enabled: {ai_summary.get('pass_rate_per_minute', 0):.2f}")
    
    # Pass criteria evaluation
    print("\nPASS CRITERIA EVALUATION:")
    baseline_criteria = baseline_evidence.get("pass_criteria", {})
    ai_criteria = ai_evidence.get("pass_criteria", {})
    
    criteria_names = {
        "scan_time_under_5ms": "Scan time < 5ms",
        "fps_above_55": "FPS > 55",
        "memory_under_50mb": "Memory increase < 50MB",
        "no_collisions": "No collisions",
        "emergency_evasion_95": "Emergency evasion > 95%",
        "lane_balance_above_0.8": "Lane balance > 0.8"
    }
    
    all_pass = True
    for key, name in criteria_names.items():
        baseline_pass = baseline_criteria.get(key, False)
        ai_pass = ai_criteria.get(key, False)
        status = "[PASS]" if ai_pass else "[FAIL]"
        all_pass = all_pass and ai_pass
        print(f"  {name}: {status}")
        
    print("\n" + "=" * 70)
    print(f"OVERALL RESULT: {'[PASS] - Issue #31 Validated!' if all_pass else '[FAIL] - Criteria not met'}")
    print("=" * 70)
    
    # Save comparison report
    comparison_report = {
        "issue": 31,
        "timestamp": datetime.now().isoformat(),
        "baseline_report": latest_baseline.name,
        "ai_report": latest_ai.name,
        "comparison": {
            "performance_impact": {
                "fps_difference": ai_summary.get('average_fps', 0) - baseline_summary.get('average_fps', 0),
                "scan_time_difference": ai_summary.get('average_scan_time_ms', 0) - baseline_summary.get('average_scan_time_ms', 0),
                "memory_difference": ai_summary.get('memory_increase_mb', 0) - baseline_summary.get('memory_increase_mb', 0)
            },
            "behavioral_improvement": {
                "pass_rate_increase": ai_summary.get('pass_rate_per_minute', 0) - baseline_summary.get('pass_rate_per_minute', 0),
                "total_passes_increase": ai_summary.get('total_passes', 0) - baseline_summary.get('total_passes', 0)
            },
            "all_criteria_met": all_pass
        }
    }
    
    comparison_file = reports_dir / f"issue_31_oqe_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(comparison_file, 'w') as f:
        json.dump(comparison_report, f, indent=2)
        
    print(f"\nComparison report saved: {comparison_file}")


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "analyze":
        analyze_oqe_reports()
    else:
        print_test_instructions()
        print("\nTo analyze results after testing, run:")
        print("  python run_issue_31_oqe_validation.py analyze")


if __name__ == "__main__":
    main()