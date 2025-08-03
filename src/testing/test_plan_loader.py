"""
Test Plan Loader - Dynamic test procedure management system.

This module provides functionality to load, validate, and manage test procedures
from various sources including JSON files, GitHub issues, and OQE reports.

Features:
- Load test procedures from JSON format
- Generate procedures from OQE compliance reports
- Validate test completion based on game logs
- Auto-detection pattern management
- Test plan caching and optimization
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import asdict

from src.ui.live_testing_overlay import TestProcedure, TestStep, TestStatus, StepStatus
from src.systems.game_state_logger import GameEvent

logger = logging.getLogger(__name__)


class TestPlanValidationError(Exception):
    """Raised when test plan validation fails."""
    pass


class TestPlanLoader:
    """
    Loads and manages test procedures from various sources.
    
    This class handles loading test procedures from JSON files, GitHub issues,
    and OQE reports, providing validation and auto-detection capabilities.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize the test plan loader.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.test_plans_dir = self.project_root / "test_plans"
        self.templates_dir = self.test_plans_dir / "templates"
        self.procedures_cache: Dict[str, TestProcedure] = {}
        
        # Ensure directories exist
        self.test_plans_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Auto-detection pattern registry
        self.detection_patterns: Dict[str, Dict[str, Any]] = {}
        
        # Load built-in patterns
        self._load_builtin_patterns()
        
        logger.info(f"TestPlanLoader initialized with root: {project_root}")
    
    def load_issue_test_plan(self, issue_number: int) -> List[TestProcedure]:
        """
        Load test procedures for a specific GitHub issue.
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            List of test procedures for the issue
            
        Raises:
            TestPlanValidationError: If test plan is invalid
        """
        test_plan_file = self.test_plans_dir / f"issue_{issue_number}.json"
        
        if not test_plan_file.exists():
            logger.warning(f"No test plan found for issue #{issue_number}")
            return []
        
        try:
            with open(test_plan_file, 'r', encoding='utf-8') as f:
                test_plan_data = json.load(f)
            
            procedures = self._parse_test_plan(test_plan_data, issue_number)
            
            # Cache procedures
            for procedure in procedures:
                self.procedures_cache[procedure.id] = procedure
            
            logger.info(f"Loaded {len(procedures)} procedures for issue #{issue_number}")
            return procedures
            
        except Exception as e:
            raise TestPlanValidationError(f"Failed to load test plan for issue #{issue_number}: {e}")
    
    def load_test_plan_from_file(self, file_path: Union[str, Path]) -> List[TestProcedure]:
        """
        Load test procedures from a specific file.
        
        Args:
            file_path: Path to the test plan JSON file
            
        Returns:
            List of test procedures
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise TestPlanValidationError(f"Test plan file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                test_plan_data = json.load(f)
            
            # Extract issue number from filename if available
            issue_number = None
            if match := re.search(r'issue_(\d+)', file_path.name):
                issue_number = int(match.group(1))
            
            return self._parse_test_plan(test_plan_data, issue_number)
            
        except Exception as e:
            raise TestPlanValidationError(f"Failed to load test plan from {file_path}: {e}")
    
    def generate_from_oqe_report(self, oqe_report: Dict[str, Any]) -> List[TestProcedure]:
        """
        Generate test procedures from OQE compliance reports.
        
        Args:
            oqe_report: OQE compliance report data
            
        Returns:
            List of generated test procedures
        """
        procedures = []
        
        # Extract issue information
        issue_number = oqe_report.get("issue_number")
        feature_name = oqe_report.get("feature_name", "Unknown Feature")
        
        # Generate performance validation procedure
        if "performance_requirements" in oqe_report:
            perf_proc = self._generate_performance_procedure(
                oqe_report["performance_requirements"], 
                issue_number, 
                feature_name
            )
            procedures.append(perf_proc)
        
        # Generate functional validation procedures
        if "acceptance_criteria" in oqe_report:
            func_procs = self._generate_functional_procedures(
                oqe_report["acceptance_criteria"], 
                issue_number, 
                feature_name
            )
            procedures.extend(func_procs)
        
        # Generate OQE compliance procedure
        compliance_proc = self._generate_oqe_compliance_procedure(
            oqe_report, 
            issue_number, 
            feature_name
        )
        procedures.append(compliance_proc)
        
        logger.info(f"Generated {len(procedures)} procedures from OQE report")
        return procedures
    
    def validate_test_completion(self, procedure_id: str, game_logs: List[GameEvent]) -> bool:
        """
        Validate if test was completed based on game logs.
        
        Args:
            procedure_id: ID of the test procedure
            game_logs: List of game events to analyze
            
        Returns:
            True if test completion can be validated from logs
        """
        if procedure_id not in self.procedures_cache:
            logger.warning(f"Procedure {procedure_id} not found in cache")
            return False
        
        procedure = self.procedures_cache[procedure_id]
        
        # Check if logs contain evidence of test completion
        test_events = [event for event in game_logs if event.test_context == procedure_id]
        
        if not test_events:
            return False
        
        # Validate each step has corresponding evidence
        completed_steps = 0
        for step in procedure.steps:
            if self._validate_step_completion(step, test_events):
                completed_steps += 1
        
        # Test is complete if all steps have evidence
        completion_ratio = completed_steps / len(procedure.steps) if procedure.steps else 0
        return completion_ratio >= 0.8  # 80% completion threshold
    
    def create_test_procedure_from_template(self, template_name: str, 
                                          customization: Dict[str, Any]) -> TestProcedure:
        """
        Create a test procedure from a template.
        
        Args:
            template_name: Name of the template to use
            customization: Custom values to apply to template
            
        Returns:
            Customized test procedure
        """
        template_file = self.templates_dir / f"{template_name}.json"
        
        if not template_file.exists():
            raise TestPlanValidationError(f"Template not found: {template_name}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        # Apply customizations
        self._apply_template_customizations(template_data, customization)
        
        # Parse into procedure
        procedures = self._parse_test_plan(template_data)
        return procedures[0] if procedures else None
    
    def register_detection_pattern(self, pattern_id: str, pattern_config: Dict[str, Any]):
        """
        Register a new auto-detection pattern.
        
        Args:
            pattern_id: Unique identifier for the pattern
            pattern_config: Pattern configuration with detection rules
        """
        self.detection_patterns[pattern_id] = pattern_config
        logger.info(f"Registered detection pattern: {pattern_id}")
    
    def get_detection_patterns_for_procedure(self, procedure_id: str) -> Dict[str, Any]:
        """
        Get applicable detection patterns for a procedure.
        
        Args:
            procedure_id: Test procedure ID
            
        Returns:
            Dictionary of applicable detection patterns
        """
        if procedure_id not in self.procedures_cache:
            return {}
        
        procedure = self.procedures_cache[procedure_id]
        applicable_patterns = {}
        
        for step in procedure.steps:
            if step.auto_detect_pattern and step.auto_detect_pattern in self.detection_patterns:
                applicable_patterns[step.auto_detect_pattern] = self.detection_patterns[step.auto_detect_pattern]
        
        return applicable_patterns
    
    def export_test_plan(self, procedures: List[TestProcedure], output_file: Path):
        """
        Export test procedures to a JSON file.
        
        Args:
            procedures: List of procedures to export
            output_file: Output file path
        """
        test_plan_data = {
            "test_plan_metadata": {
                "version": "1.0",
                "created_at": time.time(),
                "total_procedures": len(procedures)
            },
            "procedures": []
        }
        
        for procedure in procedures:
            proc_data = asdict(procedure)
            # Convert enums to strings
            proc_data["status"] = procedure.status.value
            for step_data in proc_data["steps"]:
                step_data["status"] = StepStatus(step_data["status"]).value
            
            test_plan_data["procedures"].append(proc_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_plan_data, f, indent=2, default=str)
        
        logger.info(f"Exported {len(procedures)} procedures to {output_file}")
    
    def _parse_test_plan(self, test_plan_data: Dict[str, Any], issue_number: int = None) -> List[TestProcedure]:
        """Parse test plan JSON into TestProcedure objects."""
        procedures = []
        
        # Handle both single procedure and multiple procedures format
        if "procedures" in test_plan_data:
            procedures_data = test_plan_data["procedures"]
        else:
            procedures_data = [test_plan_data]
        
        for proc_data in procedures_data:
            try:
                # Create test steps
                steps = []
                for i, step_data in enumerate(proc_data.get("steps", [])):
                    step = TestStep(
                        step_number=i + 1,
                        action=step_data.get("action", ""),
                        expected_result=step_data.get("expected_result", ""),
                        auto_detect_pattern=step_data.get("auto_detect_pattern")
                    )
                    steps.append(step)
                
                # Create procedure
                procedure = TestProcedure(
                    id=proc_data.get("id", f"proc_{len(procedures)}"),
                    title=proc_data.get("title", "Untitled Test"),
                    description=proc_data.get("description", ""),
                    issue_number=issue_number or proc_data.get("issue_number"),
                    category=proc_data.get("category", "manual"),
                    priority=proc_data.get("priority", "medium"),
                    steps=steps,
                    auto_detect=proc_data.get("auto_detect", False),
                    oqe_requirements=proc_data.get("oqe_requirements", {})
                )
                
                procedures.append(procedure)
                
            except Exception as e:
                logger.error(f"Failed to parse procedure: {e}")
                continue
        
        return procedures
    
    def _generate_performance_procedure(self, perf_requirements: Dict[str, Any], 
                                      issue_number: int, feature_name: str) -> TestProcedure:
        """Generate performance validation procedure."""
        steps = []
        
        # FPS requirement step
        if "fps_min" in perf_requirements:
            steps.append(TestStep(
                step_number=len(steps) + 1,
                action=f"Measure FPS during {feature_name} usage",
                expected_result=f"FPS >= {perf_requirements['fps_min']}",
                auto_detect_pattern="fps_measurement"
            ))
        
        # Memory requirement step
        if "memory_max_mb" in perf_requirements:
            steps.append(TestStep(
                step_number=len(steps) + 1,
                action=f"Monitor memory usage during {feature_name}",
                expected_result=f"Memory increase <= {perf_requirements['memory_max_mb']}MB",
                auto_detect_pattern="memory_measurement"
            ))
        
        # Load time requirement step
        if "load_time_max_ms" in perf_requirements:
            steps.append(TestStep(
                step_number=len(steps) + 1,
                action=f"Measure {feature_name} initialization time",
                expected_result=f"Load time <= {perf_requirements['load_time_max_ms']}ms",
                auto_detect_pattern="load_time_measurement"
            ))
        
        return TestProcedure(
            id=f"perf_validation_{issue_number}",
            title=f"Performance Validation - {feature_name}",
            description=f"Validate performance requirements for {feature_name}",
            issue_number=issue_number,
            category="performance",
            priority="high",
            steps=steps,
            auto_detect=True,
            oqe_requirements=perf_requirements
        )
    
    def _generate_functional_procedures(self, acceptance_criteria: List[str], 
                                      issue_number: int, feature_name: str) -> List[TestProcedure]:
        """Generate functional validation procedures."""
        procedures = []
        
        for i, criterion in enumerate(acceptance_criteria):
            steps = [
                TestStep(
                    step_number=1,
                    action=f"Execute functionality: {criterion}",
                    expected_result="Functionality works as expected",
                    auto_detect_pattern="functional_validation"
                ),
                TestStep(
                    step_number=2,
                    action="Verify no errors or exceptions",
                    expected_result="No errors logged",
                    auto_detect_pattern="error_check"
                )
            ]
            
            procedure = TestProcedure(
                id=f"func_test_{issue_number}_{i}",
                title=f"Functional Test {i+1}: {criterion[:50]}",
                description=f"Validate acceptance criterion: {criterion}",
                issue_number=issue_number,
                category="functional",
                priority="high",
                steps=steps,
                auto_detect=True
            )
            
            procedures.append(procedure)
        
        return procedures
    
    def _generate_oqe_compliance_procedure(self, oqe_report: Dict[str, Any], 
                                         issue_number: int, feature_name: str) -> TestProcedure:
        """Generate OQE compliance validation procedure."""
        steps = [
            TestStep(
                step_number=1,
                action="Collect precondition evidence",
                expected_result="All preconditions documented with measurements",
                auto_detect_pattern="evidence_collection"
            ),
            TestStep(
                step_number=2,
                action="Execute test with measurement collection",
                expected_result="All required metrics captured",
                auto_detect_pattern="metric_collection"
            ),
            TestStep(
                step_number=3,
                action="Validate postconditions",
                expected_result="All postconditions verified with evidence",
                auto_detect_pattern="postcondition_validation"
            ),
            TestStep(
                step_number=4,
                action="Generate OQE compliance report",
                expected_result="Compliance score >= 90%",
                auto_detect_pattern="compliance_report"
            )
        ]
        
        return TestProcedure(
            id=f"oqe_compliance_{issue_number}",
            title=f"OQE Compliance - {feature_name}",
            description=f"Validate OQE compliance for {feature_name}",
            issue_number=issue_number,
            category="compliance",
            priority="high",
            steps=steps,
            auto_detect=True,
            oqe_requirements=oqe_report.get("oqe_requirements", {})
        )
    
    def _validate_step_completion(self, step: TestStep, events: List[GameEvent]) -> bool:
        """Validate if a test step was completed based on events."""
        # Look for events that match the step's expected behavior
        step_events = []
        
        # If step has auto-detection pattern, look for matching events
        if step.auto_detect_pattern:
            pattern_events = [e for e in events if step.auto_detect_pattern in e.tags]
            step_events.extend(pattern_events)
        
        # Look for explicit test events for this step
        test_events = [e for e in events if e.event_type == "test" and 
                      str(step.step_number) in str(e.event_data)]
        step_events.extend(test_events)
        
        return len(step_events) > 0
    
    def _apply_template_customizations(self, template_data: Dict[str, Any], 
                                     customization: Dict[str, Any]):
        """Apply customizations to template data."""
        for key, value in customization.items():
            if key in template_data:
                if isinstance(template_data[key], dict) and isinstance(value, dict):
                    template_data[key].update(value)
                else:
                    template_data[key] = value
    
    def _load_builtin_patterns(self):
        """Load built-in auto-detection patterns."""
        builtin_patterns = {
            "scene_transition": {
                "description": "Detect scene transitions",
                "event_types": ["scene_transition"],
                "validation": lambda events: any(e.event_type == "scene_transition" for e in events)
            },
            "fps_measurement": {
                "description": "Detect FPS measurements",
                "event_types": ["performance"],
                "validation": lambda events: any(
                    e.event_type == "performance" and "fps" in e.event_data.get("metric", "")
                    for e in events
                )
            },
            "memory_measurement": {
                "description": "Detect memory measurements",
                "event_types": ["performance"],
                "validation": lambda events: any(
                    e.event_type == "performance" and "memory" in e.event_data.get("metric", "")
                    for e in events
                )
            },
            "audio_event": {
                "description": "Detect audio events",
                "event_types": ["audio"],
                "validation": lambda events: any(e.event_type == "audio" for e in events)
            },
            "player_action": {
                "description": "Detect player actions",
                "event_types": ["player_action"],
                "validation": lambda events: any(e.event_type == "player_action" for e in events)
            }
        }
        
        self.detection_patterns.update(builtin_patterns)
        logger.info(f"Loaded {len(builtin_patterns)} built-in detection patterns")