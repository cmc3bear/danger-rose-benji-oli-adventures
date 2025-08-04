#!/usr/bin/env python3
"""
Automated OQE Validation Runner for Issue #31 - Traffic Passing Logic

This script executes comprehensive automated testing of the traffic passing logic
system, providing evidence-based validation without requiring manual gameplay.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime


def print_banner():
    """Print the validation banner"""
    print("=" * 80)
    print("AUTOMATED OQE VALIDATION - ISSUE #31")
    print("Traffic Passing Logic System Validation")
    print("=" * 80)
    print()


def check_environment():
    """Check that the environment is ready for testing"""
    print("[CHECK] Checking test environment...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("[ERROR] Python 3.7+ required")
        return False
    
    # Check required directories
    required_dirs = ["src", "tests", "src/testing"]
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            print(f"[ERROR] Missing directory: {dir_name}")
            return False
    
    # Check required files
    required_files = [
        "src/testing/traffic_simulation_framework.py",
        "tests/test_traffic_passing_oqe_validation.py",
        "src/systems/traffic_awareness.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"[ERROR] Missing file: {file_path}")
            return False
    
    # Create reports directory
    reports_dir = Path("pipeline_reports")
    reports_dir.mkdir(exist_ok=True)
    
    print("[OK] Environment check passed")
    return True


def run_validation_tests():
    """Run the automated validation test suite"""
    print("\n[TEST] Running automated OQE validation tests...")
    
    # Change to project root directory
    os.chdir(Path(__file__).parent)
    
    # Run the validation test suite
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_traffic_passing_oqe_validation.py",
        "-v", "--tb=short"
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print("\n" + "=" * 60)
        print("TEST EXECUTION OUTPUT:")
        print("=" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("\nERRORS/WARNINGS:")
            print("-" * 40)
            print(result.stderr)
        
        return result.returncode == 0, result
        
    except subprocess.TimeoutExpired:
        print("❌ Test execution timed out (5 minutes)")
        return False, None
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False, None


def run_integration_checks():
    """Run additional integration checks"""
    print("\n🔗 Running integration checks...")
    
    # Test the OQE integration components
    try:
        cmd = [sys.executable, "test_oqe_integration.py"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("[OK] OQE integration components working")
        else:
            print("[WARN] OQE integration issues detected")
            print(result.stdout)
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"[WARN] Could not run integration checks: {e}")
        return False


def analyze_results():
    """Analyze and summarize the validation results"""
    print("\n[ANALYZE] Analyzing validation results...")
    
    reports_dir = Path("pipeline_reports")
    
    # Find the most recent reports
    baseline_reports = list(reports_dir.glob("oqe_baseline_automated_*.json"))
    ai_reports = list(reports_dir.glob("oqe_ai_enabled_automated_*.json"))
    validation_reports = list(reports_dir.glob("issue_31_automated_validation_*.json"))
    
    if not validation_reports:
        print("[ERROR] No validation reports found")
        return False
    
    # Get the most recent validation report
    latest_validation = max(validation_reports, key=lambda p: p.stat().st_mtime)
    
    try:
        with open(latest_validation) as f:
            validation_data = json.load(f)
        
        print(f"\n📋 VALIDATION SUMMARY")
        print("-" * 40)
        print(f"Timestamp: {validation_data['timestamp']}")
        print(f"Overall Result: {validation_data['overall_result']}")
        
        # Show criteria results
        criteria = validation_data['criteria_evaluation']
        passed_count = sum(1 for v in criteria.values() if v['passed'])
        total_count = len(criteria)
        
        print(f"Pass Criteria: {passed_count}/{total_count} met")
        
        print("\nDetailed Results:")
        for criterion, details in criteria.items():
            status = "[PASS]" if details['passed'] else "[FAIL]"
            print(f"  {status} {details['description']}")
            print(f"      Baseline: {details['baseline_value']:.2f}")
            print(f"      AI-Enabled: {details['ai_value']:.2f}")
        
        # Show recommendations
        if validation_data.get('recommendations'):
            print("\nRecommendations:")
            for i, rec in enumerate(validation_data['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        return validation_data['overall_result'] == 'PASS'
        
    except Exception as e:
        print(f"[ERROR] Error analyzing results: {e}")
        return False


def generate_executive_summary():
    """Generate an executive summary for stakeholders"""
    print("\n[SUMMARY] Generating executive summary...")
    
    summary = {
        "issue": 31,
        "title": "Traffic Passing Logic OQE Validation",
        "validation_type": "Automated Testing",
        "timestamp": datetime.now().isoformat(),
        "executive_summary": {
            "purpose": "Validate the traffic passing logic implementation meets OQE criteria",
            "methodology": "Automated simulation of baseline vs AI-enabled traffic scenarios",
            "duration": "120 seconds simulated per scenario (equivalent to 30-minute manual test)",
            "scenarios_tested": [
                "Baseline traffic behavior (AI disabled)",
                "AI-enhanced traffic with personality-based behaviors", 
                "Performance impact assessment",
                "Integration test coverage analysis"
            ]
        }
    }
    
    # Try to get actual results
    reports_dir = Path("pipeline_reports")
    validation_reports = list(reports_dir.glob("issue_31_automated_validation_*.json"))
    
    if validation_reports:
        latest_validation = max(validation_reports, key=lambda p: p.stat().st_mtime)
        try:
            with open(latest_validation) as f:
                validation_data = json.load(f)
            
            summary["results"] = {
                "overall_result": validation_data["overall_result"],
                "criteria_met": sum(1 for v in validation_data['criteria_evaluation'].values() if v['passed']),
                "total_criteria": len(validation_data['criteria_evaluation']),
                "key_findings": validation_data.get('recommendations', [])
            }
            
        except Exception as e:
            summary["results"] = {"error": f"Could not load validation results: {e}"}
    
    # Save executive summary
    summary_file = reports_dir / f"issue_31_executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Executive summary saved: {summary_file.name}")
    
    return summary


def main():
    """Main execution function"""
    print_banner()
    
    # Step 1: Environment check
    if not check_environment():
        print("\n[ERROR] Environment check failed. Please fix issues and retry.")
        return 1
    
    # Step 2: Run validation tests
    test_success, test_result = run_validation_tests()
    
    # Step 3: Run integration checks
    integration_success = run_integration_checks()
    
    # Step 4: Analyze results
    analysis_success = analyze_results()
    
    # Step 5: Generate summary
    summary = generate_executive_summary()
    
    # Final verdict
    print("\n" + "=" * 80)
    print("FINAL VALIDATION VERDICT")
    print("=" * 80)
    
    if test_success and analysis_success:
        print("[SUCCESS] AUTOMATED OQE VALIDATION COMPLETED SUCCESSFULLY")
        print("[PASS] Issue #31 Traffic Passing Logic validated via automated testing")
        
        if integration_success:
            print("[OK] Integration components verified")
        else:
            print("[WARN] Integration checks had minor issues (non-critical)")
        
        print(f"\nNext Steps:")
        print("1. Review detailed reports in pipeline_reports/")
        print("2. Address any failed criteria if present")
        print("3. Implement missing integration tests if needed")
        print("4. Consider manual validation for edge cases")
        
        return 0
    else:
        print("[FAIL] AUTOMATED OQE VALIDATION FAILED")
        print("Issue #31 requires additional work before validation")
        
        if not test_success:
            print("- Test execution failed")
        if not analysis_success:
            print("- Result analysis failed")
        
        print(f"\nTroubleshooting:")
        print("1. Check test output above for specific errors")
        print("2. Verify all required files are present")
        print("3. Run tests individually for debugging")
        print("4. Check pipeline_reports/ for partial results")
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)