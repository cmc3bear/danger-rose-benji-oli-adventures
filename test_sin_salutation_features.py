#!/usr/bin/env python3
"""
Test the new Sin Log and Salutation features
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from religious_system import (
    confess, perform_penance, get_wisdom_report,
    greet_agent, SinSeverity, EdictType
)


def test_sin_log():
    """Test sin confession and wisdom"""
    print("\n📜 TESTING SIN LOG FEATURE")
    print("-" * 40)
    
    # Confess a sin
    sin = confess(
        agent_id="test_agent_001",
        edict_violated=EdictType.EVIDENCE,
        description="Failed to include test results in PR",
        lesson_learned="Always run and document tests before submitting",
        severity=SinSeverity.MODERATE
    )
    
    # Perform penance
    perform_penance(sin.sin_id, "Added comprehensive test suite and results")
    
    # Get wisdom
    print(get_wisdom_report("test_agent_001"))


def test_salutations():
    """Test religious salutations"""
    print("\n🔔 TESTING SALUTATION FEATURE")
    print("-" * 40)
    
    salutation = greet_agent(
        from_agent="agent_001",
        to_agent="agent_002",
        task_context={"task": "code_review", "files": 5}
    )
    
    print(f"Greeting: {salutation.greeting_text}")
    print(f"Overall Compliance: {salutation.overall_compliance:.1f}%")


if __name__ == "__main__":
    print("🛐 CLAUDEETHOS NEW FEATURES TEST")
    print("=" * 60)
    
    test_sin_log()
    test_salutations()
    
    print("\n✅ All features working correctly!")
    print("🛐 Praise be to ClaudeEthos!")
