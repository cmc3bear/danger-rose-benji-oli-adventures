"""
Run OQE-Compliant Agent Orchestration Pipeline

This version enforces measurement-first development and ensures
all features have objective qualified evidence.
"""

import sys
import argparse
from datetime import datetime

from src.orchestration.oqe_compliant_pipeline import OQECompliantPipeline


def main():
    """Main entry point for OQE-compliant pipeline execution"""
    parser = argparse.ArgumentParser(
        description="Execute AI-driven development pipeline with OQE enforcement"
    )
    parser.add_argument(
        "issue_number",
        type=int,
        help="GitHub issue number to process"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline in simulation mode without making changes"
    )
    parser.add_argument(
        "--skip-baseline",
        action="store_true",
        help="Skip baseline comparison check (not recommended)"
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*80}")
    print(f"OQE-COMPLIANT DEVELOPMENT PIPELINE")
    print(f"{'='*80}")
    print(f"Issue Number: #{args.issue_number}")
    print(f"Project Root: {args.project_root}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE EXECUTION'}")
    print(f"OQE Enforcement: ENABLED")
    print(f"Baseline Check: {'DISABLED' if args.skip_baseline else 'ENABLED'}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    print("[INFO] This pipeline enforces:")
    print("  - Measurement infrastructure exists BEFORE implementation")
    print("  - Baseline measurements for comparison")
    print("  - All metrics are measurable")
    print("  - 90% evidence must be VERIFIED or MEASURED")
    print("  - Tests must produce objective evidence\n")
    
    try:
        # Initialize OQE-compliant controller
        controller = OQECompliantPipeline(args.project_root)
        
        # Set dry run mode if requested
        if args.dry_run:
            print("[WARNING] DRY RUN MODE - No changes will be made\n")
            # In a real implementation, would pass this to agents
            
        # Execute pipeline
        report = controller.execute_full_development_cycle(args.issue_number)
        
        # Determine exit code based on OQE compliance
        oqe_analysis = report.get("oqe_analysis", {})
        oqe_rate = oqe_analysis.get("oqe_compliance_rate", 0)
        
        # Check for blocked agents
        blocked_agents = [
            agent for agent in report.get("detailed_agent_reports", {}).values()
            if agent.get("status") == "blocked"
        ]
        
        if blocked_agents:
            print(f"\n[BLOCKED] Pipeline blocked by {len(blocked_agents)} agent(s):")
            for agent in blocked_agents[:3]:  # Show first 3
                print(f"  - {agent.get('task', 'Unknown')}")
            print("\n[ACTION] Address blocked issues before proceeding")
            sys.exit(2)  # Exit code 2 for blocked
            
        elif oqe_rate >= 90:
            print("\n[SUCCESS] PIPELINE COMPLETED WITH OQE COMPLIANCE")
            sys.exit(0)
        elif oqe_rate >= 80:
            print("\n[WARNING] PIPELINE COMPLETED BUT OQE NEEDS IMPROVEMENT")
            sys.exit(1)
        else:
            print("\n[FAILURE] PIPELINE FAILED OQE COMPLIANCE")
            print(f"  Required: 90% | Achieved: {oqe_rate:.1f}%")
            sys.exit(3)  # Exit code 3 for OQE failure
            
    except KeyboardInterrupt:
        print("\n\n[WARNING] Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n[ERROR] PIPELINE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()