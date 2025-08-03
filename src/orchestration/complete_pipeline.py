"""
Complete Agent Orchestration Pipeline

This integrates all specialized agents and provides the full automated
development pipeline with OQE at every step.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from .agent_pipeline import (
    OrchestrationController, AgentType, AgentReport, 
    MasterPlanAuditor, TestPlanDeveloper, SolutionResearcher, ImpactAnalyzer
)
from .specialized_agents import (
    TestExecutor, ImplementationValidator, DocumentationAgent,
    GitHubSynchronizer, ExecutiveReporter
)


class CompleteOrchestrationController(OrchestrationController):
    """Extended orchestration controller with all agents"""
    
    def _initialize_agents(self) -> Dict[AgentType, Any]:
        """Initialize all agent instances including specialized ones"""
        agents = super()._initialize_agents()
        
        # Add specialized agents
        agents.update({
            AgentType.TEST_EXECUTOR: TestExecutor(self.project_root),
            AgentType.IMPLEMENTATION_AGENT: ImplementationValidator(self.project_root),
            AgentType.DOCUMENTATION_AGENT: DocumentationAgent(self.project_root),
            AgentType.GITHUB_SYNCHRONIZER: GitHubSynchronizer(self.project_root),
            AgentType.EXECUTIVE_REPORTER: ExecutiveReporter(self.project_root)
        })
        
        return agents
    
    def execute_full_development_cycle(self, issue_number: int) -> Dict[str, Any]:
        """Execute complete development cycle for an issue"""
        print(f"\n{'='*80}")
        print(f"INITIATING FULL DEVELOPMENT CYCLE FOR ISSUE #{issue_number}")
        print(f"{'='*80}\n")
        
        context = {
            "issue_number": issue_number,
            "start_time": datetime.now().isoformat(),
            "project_root": self.project_root
        }
        
        # Execute pipeline
        summary = self.execute_pipeline(context)
        
        # Generate comprehensive report
        full_report = self._generate_comprehensive_report(summary)
        
        # Save report
        self._save_execution_report(full_report, issue_number)
        
        # Display executive summary
        self._display_executive_summary(full_report)
        
        return full_report
    
    def _generate_comprehensive_report(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive execution report"""
        report = {
            "execution_summary": summary,
            "timestamp": datetime.now().isoformat(),
            "detailed_agent_reports": {},
            "oqe_analysis": self._analyze_oqe_compliance(),
            "development_metrics": self._calculate_development_metrics(),
            "critical_findings": [],
            "action_items": []
        }
        
        # Extract detailed reports
        for log_entry in self.execution_log:
            agent_name = log_entry.agent_type.value
            report["detailed_agent_reports"][agent_name] = {
                "task": log_entry.task,
                "status": log_entry.status,
                "evidence_count": len(log_entry.evidence),
                "oqe_score": log_entry.get_oqe_score(),
                "warnings": log_entry.warnings,
                "recommendations": log_entry.recommendations
            }
            
            # Collect critical findings
            if log_entry.warnings:
                for warning in log_entry.warnings:
                    if "CRITICAL" in warning or "FAILURE" in warning:
                        report["critical_findings"].append({
                            "agent": agent_name,
                            "finding": warning
                        })
            
            # Collect action items
            report["action_items"].extend([
                {"agent": agent_name, "action": rec} 
                for rec in log_entry.recommendations
            ])
        
        return report
    
    def _analyze_oqe_compliance(self) -> Dict[str, Any]:
        """Detailed OQE compliance analysis"""
        total_evidence = 0
        qualified_evidence = 0
        evidence_by_type = {
            "verified": 0,
            "measured": 0,
            "documented": 0,
            "assumed": 0
        }
        
        for log_entry in self.execution_log:
            for evidence in log_entry.evidence:
                total_evidence += 1
                if evidence.is_qualified():
                    qualified_evidence += 1
                evidence_by_type[evidence.evidence_type.value] += 1
        
        return {
            "total_evidence_items": total_evidence,
            "qualified_evidence_items": qualified_evidence,
            "oqe_compliance_rate": (qualified_evidence / total_evidence * 100) if total_evidence > 0 else 0,
            "evidence_distribution": evidence_by_type,
            "recommendation": "IMPROVE" if (qualified_evidence / total_evidence) < 0.9 else "ACCEPTABLE"
        }
    
    def _calculate_development_metrics(self) -> Dict[str, Any]:
        """Calculate development metrics based on execution"""
        metrics = {
            "agents_executed": len(self.execution_log),
            "successful_agents": sum(1 for log in self.execution_log if log.status == "success"),
            "blocked_agents": sum(1 for log in self.execution_log if log.status == "blocked"),
            "failed_agents": sum(1 for log in self.execution_log if log.status == "failure"),
            "total_warnings": sum(len(log.warnings) for log in self.execution_log),
            "total_recommendations": sum(len(log.recommendations) for log in self.execution_log)
        }
        
        metrics["success_rate"] = (metrics["successful_agents"] / metrics["agents_executed"] * 100) if metrics["agents_executed"] > 0 else 0
        
        return metrics
    
    def _save_execution_report(self, report: Dict[str, Any], issue_number: int):
        """Save execution report to file"""
        report_dir = os.path.join(self.project_root, "pipeline_reports")
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(
            report_dir, 
            f"issue_{issue_number}_pipeline_report_{timestamp}.json"
        )
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"\nReport saved to: {report_path}")
    
    def _display_executive_summary(self, report: Dict[str, Any]):
        """Display executive summary with brutal honesty"""
        print("\n" + "="*80)
        print("EXECUTIVE SUMMARY - DEVELOPMENT PIPELINE EXECUTION")
        print("="*80)
        
        # Overall status
        metrics = report["development_metrics"]
        status_text = "[SUCCESS]" if metrics["success_rate"] == 100 else "[WARNING]" if metrics["success_rate"] >= 80 else "[FAILURE]"
        print(f"\nOVERALL STATUS: {status_text} {metrics['success_rate']:.1f}% Success Rate")
        
        # OQE Compliance
        oqe = report["oqe_analysis"]
        oqe_text = "[PASS]" if oqe["oqe_compliance_rate"] >= 90 else "[WARN]" if oqe["oqe_compliance_rate"] >= 80 else "[FAIL]"
        print(f"OQE COMPLIANCE: {oqe_text} {oqe['oqe_compliance_rate']:.1f}%")
        
        # Agent execution checklist
        print("\n[LIST] AGENT EXECUTION CHECKLIST:")
        for agent_name, details in report["detailed_agent_reports"].items():
            status_icon = "[OK]" if details["status"] == "success" else "[X]"
            oqe_icon = "[OK]" if details["oqe_score"] >= 80 else "[!]"
            print(f"  {status_icon} {agent_name}: {details['task']}")
            print(f"     -- OQE Score: {oqe_icon} {details['oqe_score']:.1f}%")
        
        # Critical findings
        if report["critical_findings"]:
            print(f"\n[ALERT] CRITICAL FINDINGS ({len(report['critical_findings'])}):")
            for finding in report["critical_findings"][:5]:  # Top 5
                print(f"  - [{finding['agent']}] {finding['finding']}")
        
        # Evidence summary
        print(f"\n[DATA] EVIDENCE SUMMARY:")
        print(f"  - Total Evidence Items: {oqe['total_evidence_items']}")
        print(f"  - Verified Evidence: {oqe['evidence_distribution']['verified']}")
        print(f"  - Measured Evidence: {oqe['evidence_distribution']['measured']}")
        print(f"  - Documented Only: {oqe['evidence_distribution']['documented']}")
        print(f"  - Assumed (No Evidence): {oqe['evidence_distribution']['assumed']}")
        
        # Development velocity
        print(f"\n[SPEED] DEVELOPMENT METRICS:")
        print(f"  - Agents Executed: {metrics['agents_executed']}")
        print(f"  - Successful: {metrics['successful_agents']}")
        print(f"  - Blocked: {metrics['blocked_agents']}")
        print(f"  - Failed: {metrics['failed_agents']}")
        
        # Next actions
        print(f"\n[PIN] TOP ACTION ITEMS:")
        for i, action in enumerate(report["action_items"][:5], 1):
            print(f"  {i}. [{action['agent']}] {action['action']}")
        
        # Brutal honesty verdict
        print(f"\n[EXAMINE] BRUTAL HONESTY VERDICT:")
        if metrics["success_rate"] == 100 and oqe["oqe_compliance_rate"] >= 90:
            print("  [OK] EXCELLENT: Pipeline executed flawlessly with high-quality evidence")
        elif metrics["success_rate"] >= 80 and oqe["oqe_compliance_rate"] >= 80:
            print("  [!] ACCEPTABLE: Pipeline succeeded but evidence quality needs improvement")
        else:
            print("  [X] UNACCEPTABLE: Pipeline has failures and/or poor evidence quality")
            print("     This is not ready for production and requires immediate attention")
        
        # Master plan adherence
        print(f"\n[RULER] MASTER PLAN ADHERENCE:")
        if self._check_master_plan_adherence(report):
            print("  [OK] Development aligns with master plan objectives")
        else:
            print("  [X] WARNING: Development may be deviating from master plan")
            print("     Review scope and ensure no 'pie in the sky' features")
    
    def _check_master_plan_adherence(self, report: Dict[str, Any]) -> bool:
        """Check if development adheres to master plan"""
        # Check for scope creep indicators
        warnings = []
        for details in report["detailed_agent_reports"].values():
            warnings.extend(details.get("warnings", []))
            
        scope_creep_indicators = [
            "out-of-scope", "pie in the sky", "blockchain", 
            "multiplayer", "cloud", "microservices"
        ]
        
        for warning in warnings:
            if any(indicator in warning.lower() for indicator in scope_creep_indicators):
                return False
                
        return True


# Example usage and testing
def demonstrate_pipeline():
    """Demonstrate the complete pipeline"""
    
    # Initialize controller
    controller = CompleteOrchestrationController(".")
    
    # Execute for character abilities system (Issue #29)
    report = controller.execute_full_development_cycle(issue_number=29)
    
    # The pipeline will:
    # 1. Audit master plan and GitHub status
    # 2. Develop comprehensive test plan with OQE
    # 3. Research multiple implementation approaches
    # 4. Analyze codebase impact
    # 5. Validate implementation
    # 6. Execute tests with evidence
    # 7. Create documentation
    # 8. Sync with GitHub
    # 9. Generate executive summary
    
    return report


if __name__ == "__main__":
    # Run demonstration
    demonstrate_pipeline()