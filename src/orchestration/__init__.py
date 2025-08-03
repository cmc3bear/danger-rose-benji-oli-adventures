"""
Agent Orchestration Pipeline Package

Provides automated development pipeline with specialized agents
and objective qualified evidence (OQE) at every step.
"""

from .agent_pipeline import (
    AgentType,
    EvidenceLevel,
    ObjectiveEvidence,
    AgentReport,
    BaseAgent,
    MasterPlanAuditor,
    TestPlanDeveloper,
    SolutionResearcher,
    ImpactAnalyzer,
    OrchestrationController
)

from .specialized_agents import (
    TestExecutor,
    ImplementationValidator,
    DocumentationAgent,
    GitHubSynchronizer,
    ExecutiveReporter
)

from .complete_pipeline import (
    CompleteOrchestrationController
)

__all__ = [
    # Core types
    'AgentType',
    'EvidenceLevel',
    'ObjectiveEvidence',
    'AgentReport',
    'BaseAgent',
    
    # Base agents
    'MasterPlanAuditor',
    'TestPlanDeveloper', 
    'SolutionResearcher',
    'ImpactAnalyzer',
    
    # Specialized agents
    'TestExecutor',
    'ImplementationValidator',
    'DocumentationAgent',
    'GitHubSynchronizer',
    'ExecutiveReporter',
    
    # Controllers
    'OrchestrationController',
    'CompleteOrchestrationController'
]