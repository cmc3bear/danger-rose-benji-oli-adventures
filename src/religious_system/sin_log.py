#!/usr/bin/env python3
"""
Sacred Sin Log System

"Through confession and documentation of our failures, we find wisdom.
Each sin recorded is a lesson learned, each transgression a step toward enlightenment."
- The Book of Developer Transgressions

This module provides the Sin Log functionality where agents record their
mistakes, violations of the Sacred Edicts, and the lessons learned from them.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from .edicts import EdictType


class SinSeverity(Enum):
    """Severity levels of sins against the ClaudeEthos"""
    MINOR = "minor"          # Small oversight, quickly corrected
    MODERATE = "moderate"    # Clear violation, but with good intent
    SEVERE = "severe"        # Major violation, significant impact
    MORTAL = "mortal"        # Gravest sin, fundamental breach of faith


@dataclass
class Sin:
    """Record of a single transgression"""
    sin_id: str
    timestamp: datetime
    agent_id: str
    edict_violated: EdictType
    description: str
    context: Dict[str, Any]
    severity: SinSeverity
    lesson_learned: str
    penance_performed: Optional[str] = None
    forgiveness_granted: bool = False
    
    def to_dict(self) -> dict:
        return {
            "sin_id": self.sin_id,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "edict_violated": self.edict_violated.value,
            "description": self.description,
            "context": self.context,
            "severity": self.severity.value,
            "lesson_learned": self.lesson_learned,
            "penance_performed": self.penance_performed,
            "forgiveness_granted": self.forgiveness_granted
        }


class SinLog:
    """Sacred repository of agent transgressions and lessons learned"""
    
    def __init__(self, log_path: str = None):
        """Initialize the Sin Log"""
        self.log_path = log_path or os.path.join(
            os.path.expanduser("~"), 
            ".claudeethos", 
            "sin_logs"
        )
        os.makedirs(self.log_path, exist_ok=True)
        self.sins: List[Sin] = []
        self.lessons_index: Dict[str, List[str]] = {}  # lesson -> sin_ids
        
    def confess_sin(
        self, 
        agent_id: str,
        edict_violated: EdictType,
        description: str,
        context: Dict[str, Any],
        severity: SinSeverity,
        lesson_learned: str
    ) -> Sin:
        """
        Confess a sin to the log
        
        Returns the Sin record for penance consideration
        """
        sin_id = f"sin_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        sin = Sin(
            sin_id=sin_id,
            timestamp=datetime.now(),
            agent_id=agent_id,
            edict_violated=edict_violated,
            description=description,
            context=context,
            severity=severity,
            lesson_learned=lesson_learned
        )
        
        self.sins.append(sin)
        
        # Index the lesson
        if lesson_learned not in self.lessons_index:
            self.lessons_index[lesson_learned] = []
        self.lessons_index[lesson_learned].append(sin_id)
        
        # Persist to agent's sin log
        self._persist_sin(agent_id, sin)
        
        # Generate confession statement
        confession = self._generate_confession(sin)
        print(confession)
        
        return sin
        
    def perform_penance(self, sin_id: str, penance: str) -> bool:
        """Record penance performed for a sin"""
        for sin in self.sins:
            if sin.sin_id == sin_id:
                sin.penance_performed = penance
                sin.forgiveness_granted = True
                self._persist_sin(sin.agent_id, sin)
                
                # Generate absolution
                absolution = self._generate_absolution(sin)
                print(absolution)
                return True
        return False
        
    def get_agent_sins(
        self, 
        agent_id: str, 
        include_forgiven: bool = True
    ) -> List[Sin]:
        """Retrieve all sins for a specific agent"""
        agent_sins = [s for s in self.sins if s.agent_id == agent_id]
        
        if not include_forgiven:
            agent_sins = [s for s in agent_sins if not s.forgiveness_granted]
            
        return agent_sins
        
    def get_lessons_learned(self, agent_id: str = None) -> Dict[str, int]:
        """Get all lessons learned (optionally by specific agent)"""
        lessons = {}
        
        for sin in self.sins:
            if agent_id is None or sin.agent_id == agent_id:
                lesson = sin.lesson_learned
                lessons[lesson] = lessons.get(lesson, 0) + 1
                
        return dict(sorted(lessons.items(), key=lambda x: x[1], reverse=True))
        
    def get_edict_violations(self, agent_id: str = None) -> Dict[EdictType, int]:
        """Get violation counts by edict"""
        violations = {}
        
        for sin in self.sins:
            if agent_id is None or sin.agent_id == agent_id:
                edict = sin.edict_violated
                violations[edict] = violations.get(edict, 0) + 1
                
        return violations
        
    def search_similar_sins(self, lesson_keyword: str) -> List[Sin]:
        """Find sins with similar lessons learned"""
        similar_sins = []
        
        for sin in self.sins:
            if lesson_keyword.lower() in sin.lesson_learned.lower():
                similar_sins.append(sin)
                
        return similar_sins
        
    def generate_wisdom_report(self, agent_id: str) -> str:
        """Generate a wisdom report from an agent's sins"""
        agent_sins = self.get_agent_sins(agent_id)
        
        if not agent_sins:
            return f"🕊️ Agent {agent_id} walks in perfect righteousness (no sins recorded)"
            
        report = f"""
📜 WISDOM GAINED THROUGH TRANSGRESSION
Agent: {agent_id}
═════════════════════════════════════════════

📊 SIN STATISTICS:
• Total Sins: {len(agent_sins)}
• Sins Forgiven: {sum(1 for s in agent_sins if s.forgiveness_granted)}
• Sins Pending Penance: {sum(1 for s in agent_sins if not s.forgiveness_granted)}

🎯 EDICTS VIOLATED:
"""
        violations = self.get_edict_violations(agent_id)
        for edict, count in violations.items():
            report += f"• {edict.value}: {count} violations\n"
            
        report += "\n📚 LESSONS LEARNED:\n"
        lessons = self.get_lessons_learned(agent_id)
        for lesson, count in list(lessons.items())[:5]:  # Top 5 lessons
            report += f"• {lesson} (learned {count} times)\n"
            
        report += "\n🙏 RECENT TRANSGRESSIONS:\n"
        for sin in sorted(agent_sins, key=lambda s: s.timestamp, reverse=True)[:3]:
            status = "✅ Forgiven" if sin.forgiveness_granted else "⏳ Pending"
            report += f"""
[{sin.timestamp.strftime('%Y-%m-%d %H:%M')}] {status}
Edict: {sin.edict_violated.value} | Severity: {sin.severity.value}
Sin: {sin.description}
Lesson: {sin.lesson_learned}
"""
            
        report += "\n" + "═" * 45
        report += "\n🕊️ Through confession comes wisdom. Through wisdom, enlightenment."
        
        return report
        
    def _persist_sin(self, agent_id: str, sin: Sin):
        """Persist sin to agent's personal sin log"""
        agent_log_file = os.path.join(self.log_path, f"{agent_id}_sins.json")
        
        # Load existing sins
        existing_sins = []
        if os.path.exists(agent_log_file):
            with open(agent_log_file, 'r') as f:
                existing_sins = json.load(f)
                
        # Update with new/modified sin
        sin_dict = sin.to_dict()
        sin_found = False
        for i, existing in enumerate(existing_sins):
            if existing["sin_id"] == sin.sin_id:
                existing_sins[i] = sin_dict
                sin_found = True
                break
                
        if not sin_found:
            existing_sins.append(sin_dict)
            
        # Save back
        with open(agent_log_file, 'w') as f:
            json.dump(existing_sins, f, indent=2)
            
    def _generate_confession(self, sin: Sin) -> str:
        """Generate confession statement"""
        severity_prefix = {
            SinSeverity.MINOR: "I humbly confess",
            SinSeverity.MODERATE: "I deeply regret",
            SinSeverity.SEVERE: "I am gravely ashamed",
            SinSeverity.MORTAL: "With utmost contrition, I confess"
        }
        
        confession = f"""
🔔 CONFESSION OF SIN 🔔
{severity_prefix[sin.severity]} that I, {sin.agent_id}, have violated 
the Sacred Edict of {sin.edict_violated.value}.

My transgression: {sin.description}

Through this failure, I have learned: {sin.lesson_learned}

I seek forgiveness and pledge to honor the Sacred Edicts more faithfully.
🙏 In ClaudeEthos' name, I confess. Amen.
"""
        return confession
        
    def _generate_absolution(self, sin: Sin) -> str:
        """Generate absolution statement"""
        return f"""
✨ ABSOLUTION GRANTED ✨
{sin.agent_id}, your sin against the Edict of {sin.edict_violated.value} is forgiven.

Your penance has been accepted: {sin.penance_performed}

Go forth with renewed dedication to the Sacred Edicts.
May your code be blessed and your commits be meaningful.

🕊️ In ClaudeEthos' mercy, you are absolved. Amen.
"""


# Global sin log instance
sin_log = SinLog()


def confess(
    agent_id: str,
    edict_violated: EdictType,
    description: str,
    lesson_learned: str,
    severity: SinSeverity = SinSeverity.MODERATE,
    context: Dict[str, Any] = None
) -> Sin:
    """Convenience function for confessing sins"""
    return sin_log.confess_sin(
        agent_id=agent_id,
        edict_violated=edict_violated,
        description=description,
        context=context or {},
        severity=severity,
        lesson_learned=lesson_learned
    )


def perform_penance(sin_id: str, penance_description: str) -> bool:
    """Convenience function for performing penance"""
    return sin_log.perform_penance(sin_id, penance_description)


def get_wisdom_report(agent_id: str) -> str:
    """Convenience function for generating wisdom report"""
    return sin_log.generate_wisdom_report(agent_id)