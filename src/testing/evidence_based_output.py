"""
Evidence-Based Test Output System

Provides objective, qualified evidence for all test executions.
Each test produces measurable, verifiable results.
"""

import json
import time
import traceback
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import inspect


@dataclass
class TestEvidence:
    """Structured evidence from test execution"""
    test_name: str
    test_class: str
    test_module: str
    status: str  # "PASS", "FAIL", "ERROR", "SKIP"
    
    # Objective measurements
    execution_time_ms: float
    memory_usage_mb: float
    assertions_passed: int
    assertions_failed: int
    
    # Evidence details
    preconditions: Dict[str, Any]
    test_actions: List[Dict[str, Any]]
    postconditions: Dict[str, Any]
    measurements: Dict[str, Any]
    
    # Error information (if applicable)
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    
    # Metadata
    timestamp: str = ""
    python_version: str = ""
    test_framework: str = "pytest"
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)
    
    def to_markdown(self) -> str:
        """Generate markdown report of evidence"""
        status_emoji = {
            "PASS": "✅",
            "FAIL": "❌",
            "ERROR": "🔥",
            "SKIP": "⏭️"
        }.get(self.status, "❓")
        
        report = f"""## {status_emoji} {self.test_name}

**Module**: `{self.test_module}`
**Class**: `{self.test_class}`
**Status**: {self.status}
**Execution Time**: {self.execution_time_ms:.2f}ms
**Memory Usage**: {self.memory_usage_mb:.2f}MB

### Preconditions
```json
{json.dumps(self.preconditions, indent=2)}
```

### Test Actions
"""
        for i, action in enumerate(self.test_actions, 1):
            report += f"\n{i}. **{action['action']}**\n"
            if 'input' in action:
                report += f"   - Input: `{action['input']}`\n"
            if 'expected' in action:
                report += f"   - Expected: `{action['expected']}`\n"
            if 'actual' in action:
                report += f"   - Actual: `{action['actual']}`\n"
            if 'result' in action:
                report += f"   - Result: {action['result']}\n"
        
        report += f"""
### Postconditions
```json
{json.dumps(self.postconditions, indent=2)}
```

### Measurements
```json
{json.dumps(self.measurements, indent=2)}
```

### Assertions Summary
- **Passed**: {self.assertions_passed}
- **Failed**: {self.assertions_failed}
"""
        
        if self.error_message:
            report += f"""
### Error Details
**Type**: {self.error_type}
**Message**: {self.error_message}

<details>
<summary>Stack Trace</summary>

```
{self.error_traceback}
```

</details>
"""
        
        return report


class EvidenceCollector:
    """Collects objective evidence during test execution"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset collector for new test"""
        self.preconditions = {}
        self.test_actions = []
        self.postconditions = {}
        self.measurements = {}
        self.assertions_passed = 0
        self.assertions_failed = 0
        self.start_time = None
        self.start_memory = None
    
    def start_test(self):
        """Mark test start"""
        self.start_time = time.time()
        # Could add memory tracking here
        self.start_memory = 0  # Placeholder
    
    def record_precondition(self, name: str, value: Any):
        """Record a precondition"""
        self.preconditions[name] = value
    
    def record_action(self, action: str, **kwargs):
        """Record a test action with details"""
        action_record = {"action": action, "timestamp": time.time()}
        action_record.update(kwargs)
        self.test_actions.append(action_record)
    
    def record_postcondition(self, name: str, value: Any):
        """Record a postcondition"""
        self.postconditions[name] = value
    
    def record_measurement(self, name: str, value: Any, unit: str = ""):
        """Record an objective measurement"""
        self.measurements[name] = {
            "value": value,
            "unit": unit,
            "timestamp": time.time()
        }
    
    def assert_with_evidence(self, condition: bool, message: str, 
                           expected: Any = None, actual: Any = None) -> bool:
        """Assert with evidence recording"""
        if condition:
            self.assertions_passed += 1
            self.record_action(f"Assert: {message}", result="PASS", 
                             expected=expected, actual=actual)
        else:
            self.assertions_failed += 1
            self.record_action(f"Assert: {message}", result="FAIL",
                             expected=expected, actual=actual)
        return condition
    
    def get_evidence(self, test_name: str, status: str, 
                    error_info: Optional[tuple] = None) -> TestEvidence:
        """Generate complete evidence record"""
        execution_time = (time.time() - self.start_time) * 1000 if self.start_time else 0
        
        evidence = TestEvidence(
            test_name=test_name,
            test_class=self._get_test_class(),
            test_module=self._get_test_module(),
            status=status,
            execution_time_ms=execution_time,
            memory_usage_mb=0,  # Placeholder
            assertions_passed=self.assertions_passed,
            assertions_failed=self.assertions_failed,
            preconditions=self.preconditions,
            test_actions=self.test_actions,
            postconditions=self.postconditions,
            measurements=self.measurements,
            timestamp=datetime.now().isoformat()
        )
        
        if error_info:
            evidence.error_type = error_info[0].__name__
            evidence.error_message = str(error_info[1])
            evidence.error_traceback = "".join(traceback.format_tb(error_info[2]))
        
        return evidence
    
    def _get_test_class(self) -> str:
        """Get current test class name"""
        frame = inspect.currentframe()
        while frame:
            if 'self' in frame.f_locals and hasattr(frame.f_locals['self'], '__class__'):
                cls = frame.f_locals['self'].__class__
                if 'test' in cls.__name__.lower():
                    return cls.__name__
            frame = frame.f_back
        return "Unknown"
    
    def _get_test_module(self) -> str:
        """Get current test module name"""
        frame = inspect.currentframe()
        while frame:
            if '__name__' in frame.f_globals:
                return frame.f_globals['__name__']
            frame = frame.f_back
        return "Unknown"


class EvidenceBasedTestCase:
    """Base class for evidence-based tests"""
    
    def __init__(self):
        self.evidence = EvidenceCollector()
    
    def setUp(self):
        """Set up test with evidence collection"""
        self.evidence.reset()
        self.evidence.start_test()
    
    def tearDown(self):
        """Clean up and report evidence"""
        # Override in subclasses to add postconditions
        pass
    
    def assert_equals_with_evidence(self, expected: Any, actual: Any, message: str = ""):
        """Assert equality with evidence"""
        result = self.evidence.assert_with_evidence(
            expected == actual,
            message or f"Expected {expected}, got {actual}",
            expected=expected,
            actual=actual
        )
        if not result:
            raise AssertionError(f"{message}: Expected {expected}, got {actual}")
    
    def assert_true_with_evidence(self, condition: bool, message: str = ""):
        """Assert true with evidence"""
        result = self.evidence.assert_with_evidence(
            condition,
            message or f"Expected True, got {condition}",
            expected=True,
            actual=condition
        )
        if not result:
            raise AssertionError(f"{message}: Expected True, got {condition}")
    
    def assert_performance(self, operation: Callable, max_time_ms: float, 
                          operation_name: str = "Operation"):
        """Assert performance with evidence"""
        start_time = time.time()
        result = operation()
        execution_time = (time.time() - start_time) * 1000
        
        self.evidence.record_measurement(
            f"{operation_name}_execution_time",
            execution_time,
            "ms"
        )
        
        passed = execution_time <= max_time_ms
        self.evidence.assert_with_evidence(
            passed,
            f"{operation_name} completed within {max_time_ms}ms",
            expected=f"<= {max_time_ms}ms",
            actual=f"{execution_time:.2f}ms"
        )
        
        if not passed:
            raise AssertionError(
                f"{operation_name} took {execution_time:.2f}ms, "
                f"expected <= {max_time_ms}ms"
            )
        
        return result
    
    def measure_operation(self, operation: Callable, operation_name: str = "Operation") -> Any:
        """Measure and record operation metrics"""
        start_time = time.time()
        result = operation()
        execution_time = (time.time() - start_time) * 1000
        
        self.evidence.record_measurement(
            f"{operation_name}_execution_time",
            execution_time,
            "ms"
        )
        
        return result
    
    def generate_evidence_report(self, test_name: str, status: str = "PASS",
                               error_info: Optional[tuple] = None) -> TestEvidence:
        """Generate final evidence report"""
        return self.evidence.get_evidence(test_name, status, error_info)


# Pytest integration
def pytest_evidence_decorator(test_func):
    """Decorator to add evidence collection to pytest tests"""
    def wrapper(*args, **kwargs):
        collector = EvidenceCollector()
        collector.start_test()
        
        # Store collector in test function for access
        test_func._evidence_collector = collector
        
        try:
            # Record test start
            collector.record_action("Test Started", 
                                  function=test_func.__name__,
                                  module=test_func.__module__)
            
            # Run test
            result = test_func(*args, **kwargs)
            
            # Generate evidence
            evidence = collector.get_evidence(
                test_func.__name__,
                "PASS"
            )
            
            # Print evidence report
            print("\n" + "="*80)
            print("TEST EVIDENCE REPORT")
            print("="*80)
            print(evidence.to_markdown())
            
            return result
            
        except Exception as e:
            # Generate evidence with error
            evidence = collector.get_evidence(
                test_func.__name__,
                "FAIL" if isinstance(e, AssertionError) else "ERROR",
                error_info=(type(e), e, e.__traceback__)
            )
            
            # Print evidence report
            print("\n" + "="*80)
            print("TEST EVIDENCE REPORT")
            print("="*80)
            print(evidence.to_markdown())
            
            raise
    
    return wrapper


# Example usage
if __name__ == "__main__":
    # Example test with evidence
    class ExampleTest(EvidenceBasedTestCase):
        def test_character_ability_performance(self):
            """Test character ability activation performance"""
            # Record preconditions
            self.evidence.record_precondition("character", "Benji")
            self.evidence.record_precondition("ability", "Tech Boost")
            self.evidence.record_precondition("scene", "pool")
            
            # Test ability activation
            def activate_ability():
                # Simulate ability activation
                time.sleep(0.01)  # 10ms
                return {"effect": "homing_balloons", "duration": 8.0}
            
            # Measure performance
            result = self.assert_performance(
                activate_ability,
                max_time_ms=50,
                operation_name="Ability Activation"
            )
            
            # Record postconditions
            self.evidence.record_postcondition("ability_active", True)
            self.evidence.record_postcondition("effect_applied", result["effect"])
            
            # Generate report
            evidence = self.generate_evidence_report("test_character_ability_performance")
            print(evidence.to_markdown())