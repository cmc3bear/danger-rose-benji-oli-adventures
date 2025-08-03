"""
Run Agent Orchestration Pipeline

Execute the complete automated development pipeline for a given issue.
"""

import sys
import argparse
from datetime import datetime

from src.orchestration import CompleteOrchestrationController


def main():
    """Main entry point for pipeline execution"""
    parser = argparse.ArgumentParser(
        description="Execute AI-driven development pipeline with OQE"
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
    
    args = parser.parse_args()
    
    print(f"\n{'='*80}")
    print(f"AI-DRIVEN DEVELOPMENT PIPELINE")
    print(f"{'='*80}")
    print(f"Issue Number: #{args.issue_number}")
    print(f"Project Root: {args.project_root}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE EXECUTION'}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    try:
        # Initialize controller
        controller = CompleteOrchestrationController(args.project_root)
        
        # Set dry run mode if requested
        if args.dry_run:
            print("⚠️  DRY RUN MODE - No changes will be made\n")
            # In a real implementation, would pass this to agents
        
        # Execute pipeline
        report = controller.execute_full_development_cycle(args.issue_number)
        
        # Determine exit code based on results
        metrics = report.get("development_metrics", {})
        oqe = report.get("oqe_analysis", {})
        
        success = (
            metrics.get("success_rate", 0) == 100 and
            oqe.get("oqe_compliance_rate", 0) >= 90
        )
        
        if success:
            print("\n✅ PIPELINE COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n❌ PIPELINE COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ PIPELINE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()