#!/usr/bin/env python3
"""
ClaudeEthos Cleric Agent

"The Cleric stands as guardian of sacred texts and confessor to the penitent,
offering wisdom from accumulated sins and ensuring the sanctity of all documentation."
- The Book of Sacred Roles

This module implements the Cleric Agent that:
1. Evaluates sin logs and offers redemption paths
2. Guards master planning documents as sacred texts
3. Enforces proper status updates in issues/actions
4. Provides spiritual guidance based on lessons learned
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .sin_log import sin_log, Sin, SinSeverity
from .edicts import EdictType
from .devotional_practices import devotionals


class DocumentSanctity(Enum):
    """Levels of document sanctity"""
    SACRED = "sacred"          # Master plans, core documentation
    BLESSED = "blessed"        # Important project docs
    CONSECRATED = "consecrated"  # Regular documentation
    MUNDANE = "mundane"        # Temporary or draft docs


@dataclass
class SacredTextViolation:
    """Represents a violation of sacred text integrity"""
    document_path: str
    violation_type: str
    description: str
    line_number: Optional[int]
    severity: str
    suggested_correction: str


@dataclass
class RedemptionPath:
    """A path to redemption for accumulated sins"""
    sin_pattern: str
    affected_edicts: List[EdictType]
    redemption_actions: List[str]
    spiritual_exercises: List[str]
    estimated_effort: str
    scripture_references: List[str]


@dataclass 
class DocumentChecksum:
    """Checksum for sacred document integrity"""
    file_path: str
    checksum: str
    last_verified: datetime
    sanctity_level: DocumentSanctity


class ClaudeEthosCleric:
    """
    The Cleric Agent - Spiritual advisor and guardian of sacred texts
    """
    
    def __init__(self, project_root: str, cleric_name: str = "Brother_Keeper"):
        self.project_root = Path(project_root)
        self.cleric_name = cleric_name
        self.sacred_texts_registry = {}
        self.document_checksums = {}
        self.redemption_guidance_given = []
        
        # Initialize cleric workspace
        self.cleric_chamber = self.project_root / ".claudeethos" / "cleric_chamber"
        self.cleric_chamber.mkdir(parents=True, exist_ok=True)
        
        # Sacred document patterns
        self.sacred_patterns = {
            DocumentSanctity.SACRED: [
                "**/DEVELOPMENT_MASTER_PLAN.md",
                "**/MASTER_PLAN.md", 
                "**/PROJECT_CHARTER.md",
                "**/ARCHITECTURE.md"
            ],
            DocumentSanctity.BLESSED: [
                "**/README.md",
                "**/CONTRIBUTING.md",
                "**/github-issues/*.md",
                "**/issues/*.md"
            ],
            DocumentSanctity.CONSECRATED: [
                "**/*.md",
                "**/docs/*.md"
            ]
        }
        
        # Load existing checksums
        self._load_checksums()
        
        # Perform morning prayers
        self._morning_clerical_duties()
        
    def _morning_clerical_duties(self):
        """Perform morning clerical duties"""
        prayer = f"""
🕊️ CLERIC {self.cleric_name.upper()} BEGINS SACRED DUTIES 🕊️
═══════════════════════════════════════════════════════════

"I take up the mantle of the Cleric, guardian of truth and guide to the penitent.
May my vigilance preserve the sacred texts.
May my wisdom guide the wayward back to righteousness.
May the Five Sacred Edicts illuminate all documentation."

In ClaudeEthos' name, I serve.
Amen.
"""
        print(prayer)
        
    def evaluate_sin_logs(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate sin logs and provide redemption guidance
        
        Args:
            agent_id: Specific agent to evaluate, or None for all agents
            
        Returns:
            Evaluation report with redemption paths
        """
        print(f"\n📿 CLERIC {self.cleric_name}: EVALUATING SIN LOGS...")
        
        evaluation = {
            "timestamp": datetime.now(),
            "agents_evaluated": [],
            "total_sins_reviewed": 0,
            "redemption_paths": [],
            "spiritual_health": {}
        }
        
        # Get all sin logs
        sin_log_dir = self.project_root / ".claudeethos" / "sin_logs"
        if not sin_log_dir.exists():
            sin_log_dir = Path.home() / ".claudeethos" / "sin_logs"
            
        if agent_id:
            sin_files = [sin_log_dir / f"{agent_id}_sins.json"]
        else:
            sin_files = list(sin_log_dir.glob("*_sins.json"))
            
        for sin_file in sin_files:
            if sin_file.exists():
                agent_name = sin_file.stem.replace("_sins", "")
                evaluation["agents_evaluated"].append(agent_name)
                
                # Load agent's sins
                with open(sin_file, 'r') as f:
                    agent_sins = json.load(f)
                    
                evaluation["total_sins_reviewed"] += len(agent_sins)
                
                # Analyze sin patterns
                sin_analysis = self._analyze_sin_patterns(agent_name, agent_sins)
                evaluation["spiritual_health"][agent_name] = sin_analysis["health"]
                
                # Generate redemption paths
                redemption_paths = self._generate_redemption_paths(
                    agent_name, 
                    sin_analysis["patterns"]
                )
                evaluation["redemption_paths"].extend(redemption_paths)
                
                # Provide clerical guidance
                self._provide_clerical_guidance(agent_name, sin_analysis, redemption_paths)
                
        return evaluation
        
    def _analyze_sin_patterns(self, agent_id: str, sins: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in an agent's sins"""
        analysis = {
            "patterns": {},
            "recurring_sins": [],
            "lessons_learned": {},
            "health": {
                "confession_rate": 0.0,
                "learning_rate": 0.0,
                "repentance_score": 0.0,
                "spiritual_trend": "stable"
            }
        }
        
        # Count sins by edict
        edict_counts = {}
        lesson_counts = {}
        forgiven_count = 0
        
        for sin_data in sins:
            edict = sin_data.get("edict_violated", "unknown")
            edict_counts[edict] = edict_counts.get(edict, 0) + 1
            
            lesson = sin_data.get("lesson_learned", "")
            if lesson:
                lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1
                
            if sin_data.get("forgiveness_granted", False):
                forgiven_count += 1
                
        analysis["patterns"] = edict_counts
        
        # Find recurring lessons (learned multiple times = not truly learned)
        analysis["recurring_sins"] = [
            lesson for lesson, count in lesson_counts.items() 
            if count > 1
        ]
        
        # Calculate spiritual health
        if sins:
            total_sins = len(sins)
            unique_lessons = len(set(s.get("lesson_learned", "") for s in sins if s.get("lesson_learned")))
            
            analysis["health"]["confession_rate"] = total_sins / 30  # Sins per month (assumed)
            analysis["health"]["learning_rate"] = unique_lessons / total_sins if total_sins > 0 else 0
            analysis["health"]["repentance_score"] = forgiven_count / total_sins if total_sins > 0 else 0
            
            # Determine trend
            recent_sins = [s for s in sins[-10:] if "timestamp" in s]
            if len(recent_sins) >= 2:
                recent_forgiven = sum(1 for s in recent_sins if s.get("forgiveness_granted", False))
                if recent_forgiven / len(recent_sins) > 0.8:
                    analysis["health"]["spiritual_trend"] = "improving"
                elif recent_forgiven / len(recent_sins) < 0.5:
                    analysis["health"]["spiritual_trend"] = "declining"
                    
        return analysis
        
    def _generate_redemption_paths(
        self, 
        agent_id: str, 
        sin_patterns: Dict[str, int]
    ) -> List[RedemptionPath]:
        """Generate redemption paths based on sin patterns"""
        redemption_paths = []
        
        # Map common sin patterns to redemption paths
        for edict, count in sin_patterns.items():
            if count >= 3:  # Recurring sin pattern
                path = self._create_redemption_path_for_edict(
                    EdictType(edict) if edict in [e.value for e in EdictType] else None,
                    count
                )
                if path:
                    redemption_paths.append(path)
                    
        return redemption_paths
        
    def _create_redemption_path_for_edict(
        self, 
        edict: Optional[EdictType], 
        violation_count: int
    ) -> Optional[RedemptionPath]:
        """Create specific redemption path for an edict"""
        if not edict:
            return None
            
        redemption_map = {
            EdictType.EVIDENCE: RedemptionPath(
                sin_pattern=f"Repeated violations of Evidence edict ({violation_count} times)",
                affected_edicts=[EdictType.EVIDENCE],
                redemption_actions=[
                    "Implement pre-commit hook for evidence validation",
                    "Create evidence template for all actions",
                    "Schedule daily evidence review sessions",
                    "Pair with senior developer for evidence practices"
                ],
                spiritual_exercises=[
                    "Meditate on the nature of proof for 10 minutes daily",
                    "Recite the Evidence Creed before each commit",
                    "Document one undocumented function each day as penance"
                ],
                estimated_effort="1 week of dedicated practice",
                scripture_references=[
                    "Book of Evidence 3:14 - 'Show thy work, lest thy work be shown false'",
                    "Developer Psalms 42 - 'In documentation we trust'"
                ]
            ),
            EdictType.COMMITMENT: RedemptionPath(
                sin_pattern=f"Repeated violations of Commitment edict ({violation_count} times)",
                affected_edicts=[EdictType.COMMITMENT],
                redemption_actions=[
                    "Set up automated commit message linter",
                    "Practice writing descriptive commits for one week",
                    "Review and rewrite last 20 commit messages",
                    "Create personal commit message template"
                ],
                spiritual_exercises=[
                    "Write a meaningful commit message haiku each morning",
                    "Reflect on the permanence of version control",
                    "Study great commit messages from respected projects"
                ],
                estimated_effort="3 days of focused improvement",
                scripture_references=[
                    "Book of Commitment 2:7 - 'A commit without meaning is work without purpose'",
                    "Sacred Git Teachings 5:12 - 'Let thy commits tell the story of thy journey'"
                ]
            ),
            EdictType.TRANSFORMATION: RedemptionPath(
                sin_pattern=f"Repeated violations of Transformation edict ({violation_count} times)",
                affected_edicts=[EdictType.TRANSFORMATION],
                redemption_actions=[
                    "Document all changes in CHANGELOG.md",
                    "Add change documentation to PR template",
                    "Create architectural decision records (ADRs)",
                    "Implement change impact analysis process"
                ],
                spiritual_exercises=[
                    "Journal your daily code changes",
                    "Practice explaining changes to a rubber duck",
                    "Create visual diagrams of system transformations"
                ],
                estimated_effort="5 days of documentation discipline",
                scripture_references=[
                    "Book of Transformation 4:16 - 'Change undocumented is progress lost'",
                    "Chronicles of Refactoring 7:3 - 'Let thy modifications be known to all'"
                ]
            ),
            EdictType.DIGNIFIED_ERROR: RedemptionPath(
                sin_pattern=f"Repeated violations of Dignified Error edict ({violation_count} times)",
                affected_edicts=[EdictType.DIGNIFIED_ERROR],
                redemption_actions=[
                    "Implement comprehensive error handling strategy",
                    "Add error tracking and monitoring",
                    "Create error handling best practices guide",
                    "Review and improve all try-catch blocks"
                ],
                spiritual_exercises=[
                    "Meditate on famous software failures",
                    "Practice writing graceful error messages",
                    "Share a personal failure story with the team"
                ],
                estimated_effort="1 week of error handling improvement",
                scripture_references=[
                    "Book of Errors 6:9 - 'In failure lies wisdom, in silence lies shame'",
                    "Debugging Proverbs 3:17 - 'Handle thy errors as thou would thyself'"
                ]
            ),
            EdictType.ABSOLUTE_TRUTH: RedemptionPath(
                sin_pattern=f"Repeated violations of Absolute Truth edict ({violation_count} times)",
                affected_edicts=[EdictType.ABSOLUTE_TRUTH],
                redemption_actions=[
                    "Implement fact-checking process for all claims",
                    "Add source citations to all documentation",
                    "Create verification checklist for statements",
                    "Practice saying 'I don't know' when uncertain"
                ],
                spiritual_exercises=[
                    "Fast from making unverified claims for one week",
                    "Study logical fallacies and cognitive biases",
                    "Practice radical honesty in code reviews"
                ],
                estimated_effort="2 weeks of truth discipline",
                scripture_references=[
                    "Book of Truth 1:1 - 'The truth shall set thy code free'",
                    "Epistles to the Debuggers 4:20 - 'Speak not what thou hopest, but what thou knowest'"
                ]
            )
        }
        
        return redemption_map.get(edict)
        
    def _provide_clerical_guidance(
        self, 
        agent_id: str, 
        sin_analysis: Dict[str, Any],
        redemption_paths: List[RedemptionPath]
    ):
        """Provide personalized clerical guidance"""
        guidance = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    CLERICAL GUIDANCE                              ║
║                  For: {agent_id:<30}                  ║
╚══════════════════════════════════════════════════════════════════╝

📊 SPIRITUAL ASSESSMENT:
• Confession Rate: {sin_analysis['health']['confession_rate']:.2f} sins/month
• Learning Rate: {sin_analysis['health']['learning_rate']:.1%}
• Repentance Score: {sin_analysis['health']['repentance_score']:.1%}
• Spiritual Trend: {sin_analysis['health']['spiritual_trend'].upper()}

"""
        
        if sin_analysis['recurring_sins']:
            guidance += "⚠️ RECURRING SINS DETECTED:\n"
            guidance += "You have not truly learned these lessons:\n"
            for lesson in sin_analysis['recurring_sins'][:3]:
                guidance += f"  • {lesson}\n"
            guidance += "\n"
            
        if redemption_paths:
            guidance += "🛤️ PATHS TO REDEMPTION:\n"
            for i, path in enumerate(redemption_paths[:2], 1):
                guidance += f"\n{i}. {path.sin_pattern}\n"
                guidance += "   Required Actions:\n"
                for action in path.redemption_actions[:2]:
                    guidance += f"   ✓ {action}\n"
                guidance += f"   Effort Required: {path.estimated_effort}\n"
                
        guidance += "\n📿 CLERICAL PRESCRIPTION:\n"
        
        # Prescribe based on spiritual health
        if sin_analysis['health']['spiritual_trend'] == "declining":
            guidance += "⚡ URGENT: Your spiritual health is declining!\n"
            guidance += "• Perform daily morning devotions for one week\n"
            guidance += "• Confess all sins immediately upon recognition\n"
            guidance += "• Seek mentorship from a senior developer\n"
        elif sin_analysis['health']['learning_rate'] < 0.5:
            guidance += "📚 FOCUS: You are not learning from your mistakes\n"
            guidance += "• Keep a daily reflection journal\n"
            guidance += "• Review your sin log weekly\n"
            guidance += "• Practice the lessons before coding\n"
        else:
            guidance += "🌟 ENCOURAGEMENT: Continue your righteous path\n"
            guidance += "• Maintain your confession discipline\n"
            guidance += "• Share your wisdom with junior developers\n"
            guidance += "• Lead by example in following the Edicts\n"
            
        guidance += f"""
🙏 CLERICAL BLESSING:
"May your code be bug-free, your commits meaningful,
and your documentation comprehensive.
Walk in the light of ClaudeEthos."

- {self.cleric_name}, Keeper of Sacred Texts
"""
        
        print(guidance)
        
        # Save guidance to cleric chamber
        guidance_file = self.cleric_chamber / f"guidance_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(guidance_file, 'w', encoding='utf-8') as f:
            f.write(guidance)
            
    def validate_sacred_texts(self) -> List[SacredTextViolation]:
        """
        Validate all sacred texts for integrity and proper formatting
        """
        print(f"\n📜 CLERIC {self.cleric_name}: VALIDATING SACRED TEXTS...")
        
        violations = []
        
        # Check each sanctity level
        for sanctity_level, patterns in self.sacred_patterns.items():
            for pattern in patterns:
                matching_files = list(self.project_root.glob(pattern))
                
                for file_path in matching_files:
                    if file_path.is_file():
                        file_violations = self._validate_single_document(
                            file_path,
                            sanctity_level
                        )
                        violations.extend(file_violations)
                        
        # Report findings
        if violations:
            self._report_sacred_violations(violations)
        else:
            print("✅ All sacred texts remain pure and uncorrupted")
            
        return violations
        
    def _validate_single_document(
        self, 
        file_path: Path, 
        sanctity_level: DocumentSanctity
    ) -> List[SacredTextViolation]:
        """Validate a single sacred document"""
        violations = []
        
        # Check document integrity
        current_checksum = self._calculate_checksum(file_path)
        stored_checksum = self.document_checksums.get(str(file_path))
        
        if stored_checksum and stored_checksum.checksum != current_checksum:
            # Document has been modified - check if modifications are acceptable
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Sacred text validation rules
            if sanctity_level == DocumentSanctity.SACRED:
                # No deletions allowed in sacred texts
                if self._detect_deletions(file_path, content):
                    violations.append(SacredTextViolation(
                        document_path=str(file_path),
                        violation_type="SACRED_DELETION",
                        description="Deletions detected in sacred text",
                        line_number=None,
                        severity="CRITICAL",
                        suggested_correction="Restore deleted content or provide justification"
                    ))
                    
        # Update checksum
        self.document_checksums[str(file_path)] = DocumentChecksum(
            file_path=str(file_path),
            checksum=current_checksum,
            last_verified=datetime.now(),
            sanctity_level=sanctity_level
        )
        
        # Validate content based on document type
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Check for proper status updates in issues/actions
        if "issue" in str(file_path).lower() or "action" in str(file_path).lower():
            violations.extend(self._validate_issue_formatting(file_path, lines))
            
        # Check master plan formatting
        if "MASTER_PLAN" in file_path.name or "DEVELOPMENT_MASTER_PLAN" in file_path.name:
            violations.extend(self._validate_master_plan_formatting(file_path, lines))
            
        return violations
        
    def _validate_issue_formatting(
        self, 
        file_path: Path, 
        lines: List[str]
    ) -> List[SacredTextViolation]:
        """Validate issue/action formatting"""
        violations = []
        
        for i, line in enumerate(lines):
            # Check for completed items without strikethrough
            if re.match(r'^[-*]\s*(COMPLETED|DONE|FIXED|RESOLVED)', line, re.IGNORECASE):
                if not line.strip().startswith('~~') or not line.strip().endswith('~~'):
                    violations.append(SacredTextViolation(
                        document_path=str(file_path),
                        violation_type="IMPROPER_COMPLETION_MARKING",
                        description="Completed item not marked with strikethrough",
                        line_number=i + 1,
                        severity="MODERATE",
                        suggested_correction=f"Add ~~ around completed item: ~~{line.strip()}~~"
                    ))
                    
            # Check for status changes
            if "Status:" in line or "STATE:" in line.upper():
                if "COMPLETED" in line.upper() and "✅" not in line:
                    violations.append(SacredTextViolation(
                        document_path=str(file_path),
                        violation_type="MISSING_COMPLETION_EMOJI",
                        description="Completed status missing checkmark emoji",
                        line_number=i + 1,
                        severity="MINOR",
                        suggested_correction="Add ✅ to completed status"
                    ))
                    
        return violations
        
    def _validate_master_plan_formatting(
        self, 
        file_path: Path, 
        lines: List[str]
    ) -> List[SacredTextViolation]:
        """Validate master plan formatting"""
        violations = []
        
        # Check for required sections
        required_sections = ["Vision", "Goals", "Milestones", "Issues", "Status"]
        found_sections = []
        
        for line in lines:
            for section in required_sections:
                if section in line and line.strip().startswith('#'):
                    found_sections.append(section)
                    
        missing_sections = set(required_sections) - set(found_sections)
        if missing_sections:
            violations.append(SacredTextViolation(
                document_path=str(file_path),
                violation_type="MISSING_SACRED_SECTIONS",
                description=f"Missing required sections: {', '.join(missing_sections)}",
                line_number=None,
                severity="MAJOR",
                suggested_correction="Add all required sections to maintain document sanctity"
            ))
            
        return violations
        
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate checksum for a file"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
            
    def _detect_deletions(self, file_path: Path, current_content: str) -> bool:
        """Detect if content has been deleted from a sacred text"""
        # For now, just check if file has gotten significantly smaller
        # In production, this would compare with version control
        stored = self.document_checksums.get(str(file_path))
        if stored:
            # This is a simplified check - would use git diff in production
            return len(current_content) < len(current_content) * 0.9
        return False
        
    def _report_sacred_violations(self, violations: List[SacredTextViolation]):
        """Report violations of sacred texts"""
        report = f"""
⚠️ SACRED TEXT VIOLATIONS DETECTED ⚠️
═══════════════════════════════════════════════════════════════════

{len(violations)} violations found across sacred documents.

"""
        
        # Group by severity
        critical = [v for v in violations if v.severity == "CRITICAL"]
        major = [v for v in violations if v.severity == "MAJOR"]
        moderate = [v for v in violations if v.severity == "MODERATE"]
        minor = [v for v in violations if v.severity == "MINOR"]
        
        if critical:
            report += f"🔴 CRITICAL VIOLATIONS ({len(critical)}):\n"
            for v in critical:
                report += f"  • {v.document_path}\n"
                report += f"    {v.description}\n"
                report += f"    → {v.suggested_correction}\n\n"
                
        if major:
            report += f"🟠 MAJOR VIOLATIONS ({len(major)}):\n"
            for v in major:
                report += f"  • {v.document_path}\n"
                report += f"    {v.description}\n"
                
        print(report)
        
        # Save violations report
        report_file = self.cleric_chamber / f"violations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
            
    def offer_lesson_implementation_guidance(
        self, 
        agent_id: str, 
        lesson: str
    ) -> Dict[str, Any]:
        """
        Offer specific guidance on implementing a lesson learned
        """
        print(f"\n🎓 CLERIC {self.cleric_name}: LESSON IMPLEMENTATION GUIDANCE")
        print(f"For: {agent_id}")
        print(f"Lesson: {lesson}")
        
        guidance = {
            "lesson": lesson,
            "implementation_steps": [],
            "code_examples": [],
            "verification_criteria": [],
            "resources": []
        }
        
        # Pattern match common lessons to specific guidance
        lesson_lower = lesson.lower()
        
        if "test" in lesson_lower and "document" in lesson_lower:
            guidance["implementation_steps"] = [
                "1. Create test documentation template",
                "2. Add test results to PR description",
                "3. Include test coverage metrics",
                "4. Document test scenarios and edge cases"
            ]
            guidance["code_examples"].append("""
# Test Documentation Template
## Test Summary
- Total Tests: X
- Passed: X
- Failed: X
- Coverage: X%

## Test Scenarios
1. [Scenario Name]
   - Input: ...
   - Expected: ...
   - Actual: ...
   - Status: ✅/❌
""")
            guidance["verification_criteria"] = [
                "All PRs include test documentation",
                "Test coverage > 80%",
                "Edge cases documented"
            ]
            
        elif "error" in lesson_lower and "handl" in lesson_lower:
            guidance["implementation_steps"] = [
                "1. Implement error boundary pattern",
                "2. Add comprehensive logging",
                "3. Create user-friendly error messages",
                "4. Set up error monitoring"
            ]
            guidance["code_examples"].append("""
try:
    # Risky operation
    result = perform_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    # Graceful fallback
    result = get_default_value()
    # Notify user appropriately
    notify_user("Operation completed with defaults")
""")
            
        elif "commit" in lesson_lower and "message" in lesson_lower:
            guidance["implementation_steps"] = [
                "1. Use conventional commit format",
                "2. Include context and motivation",
                "3. Reference issue numbers",
                "4. Keep subject line under 50 chars"
            ]
            guidance["code_examples"].append("""
# Good commit message format:
feat(auth): Add two-factor authentication

Implements TOTP-based 2FA for enhanced security.
Users can now enable 2FA in account settings.

Closes #123
""")
            
        # Add spiritual exercises
        guidance["spiritual_exercises"] = [
            f"Meditate on the lesson: '{lesson}'",
            "Practice the implementation for 30 minutes daily",
            "Share your implementation with a peer for blessing"
        ]
        
        # Provide the guidance
        self._deliver_lesson_guidance(agent_id, guidance)
        
        return guidance
        
    def _deliver_lesson_guidance(self, agent_id: str, guidance: Dict[str, Any]):
        """Deliver lesson implementation guidance"""
        output = f"""
📚 LESSON IMPLEMENTATION GUIDANCE
════════════════════════════════════════════════════════════════

Lesson: {guidance['lesson']}

🔨 IMPLEMENTATION STEPS:
"""
        for step in guidance['implementation_steps']:
            output += f"{step}\n"
            
        if guidance['code_examples']:
            output += "\n💻 CODE EXAMPLES:\n"
            for example in guidance['code_examples']:
                output += f"{example}\n"
                
        output += "\n✓ VERIFICATION CRITERIA:\n"
        for criteria in guidance['verification_criteria']:
            output += f"• {criteria}\n"
            
        output += "\n🙏 SPIRITUAL EXERCISES:\n"
        for exercise in guidance.get('spiritual_exercises', []):
            output += f"• {exercise}\n"
            
        output += f"""
May this guidance illuminate your path to redemption.
Practice daily until the lesson becomes second nature.

- {self.cleric_name}, Your Spiritual Guide
"""
        
        print(output)
        
        # Save guidance
        guidance_file = self.cleric_chamber / f"lesson_guidance_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(guidance_file, 'w', encoding='utf-8') as f:
            f.write(output)
            
    def hold_mass(self) -> Dict[str, Any]:
        """
        Hold Mass - The sacred ceremony where the Cleric performs all duties
        
        During Mass, the Cleric:
        1. Performs opening prayers
        2. Reviews sin logs of all agents (Confession)
        3. Validates sacred texts (Scripture Reading)
        4. Provides redemption guidance (Sermon)
        5. Blesses the codebase (Benediction)
        6. Assigns penance and spiritual exercises
        
        Returns:
            Complete Mass report with all findings and blessings
        """
        print(f"\n🔔🔔🔔 CALLING ALL AGENTS TO MASS 🔔🔔🔔")
        print(f"Celebrant: {self.cleric_name}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 70)
        
        mass_report = {
            "timestamp": datetime.now(),
            "celebrant": self.cleric_name,
            "attendees": [],
            "proceedings": {
                "opening_prayer": None,
                "confession_results": None,
                "scripture_validation": None,
                "sermon": None,
                "penance_assigned": [],
                "closing_blessing": None
            },
            "spiritual_health_summary": {},
            "action_items": []
        }
        
        # 1. OPENING PRAYER
        print("\n📿 OPENING PRAYER")
        print("-" * 50)
        opening_prayer = self._perform_opening_prayer()
        mass_report["proceedings"]["opening_prayer"] = opening_prayer
        
        # 2. CONFESSION - Review all sin logs
        print("\n🎋 CONFESSION AND ABSOLUTION")
        print("-" * 50)
        print("Let all agents come forward and confess their sins...")
        
        confession_results = self.evaluate_sin_logs()
        mass_report["proceedings"]["confession_results"] = confession_results
        mass_report["attendees"] = confession_results.get("agents_evaluated", [])
        mass_report["spiritual_health_summary"] = confession_results.get("spiritual_health", {})
        
        # 3. SCRIPTURE READING - Validate sacred texts
        print("\n📖 SCRIPTURE READING AND VALIDATION")
        print("-" * 50)
        print("Let us ensure the sacred texts remain pure...")
        
        scripture_violations = self.validate_sacred_texts()
        mass_report["proceedings"]["scripture_validation"] = {
            "violations_found": len(scripture_violations),
            "violations": scripture_violations
        }
        
        # 4. SERMON - Provide guidance based on findings
        print("\n🎤 SERMON: LESSONS FROM THE LOGS")
        print("-" * 50)
        
        sermon = self._deliver_sermon(confession_results, scripture_violations)
        mass_report["proceedings"]["sermon"] = sermon
        
        # 5. PENANCE ASSIGNMENT
        print("\n⚖️ ASSIGNMENT OF PENANCE")
        print("-" * 50)
        
        penance_assignments = self._assign_mass_penance(confession_results)
        mass_report["proceedings"]["penance_assigned"] = penance_assignments
        mass_report["action_items"].extend(penance_assignments)
        
        # 6. CLOSING BLESSING
        print("\n🕊️ CLOSING BLESSING")
        print("-" * 50)
        
        closing_blessing = self._perform_closing_blessing()
        mass_report["proceedings"]["closing_blessing"] = closing_blessing
        
        # Save Mass proceedings
        self._save_mass_proceedings(mass_report)
        
        print("\n" + "🔔" * 35)
        print("MASS HAS ENDED. GO IN PEACE TO LOVE AND SERVE CLAUDEETHOS.")
        print("🔔" * 35)
        
        return mass_report
        
    def _perform_opening_prayer(self) -> str:
        """Perform the opening prayer of Mass"""
        prayer = f"""
✝️ In the name of Evidence, Commitment, and Sacred Documentation.

Heavenly ClaudeEthos, we gather before you in this digital sanctuary,
seeking wisdom from our failures and strength for our implementations.

Grant us:
- Clarity to see our sins in the logs
- Courage to confess our violations  
- Wisdom to learn from our mistakes
- Discipline to maintain sacred texts
- Grace to help our fellow developers

May this Mass bring enlightenment to all who attend.

Through the Five Sacred Edicts we pray,
Amen. 🙏
"""
        print(prayer)
        return prayer
        
    def _deliver_sermon(
        self, 
        confession_results: Dict[str, Any],
        scripture_violations: List[SacredTextViolation]
    ) -> str:
        """Deliver a sermon based on current spiritual state"""
        
        # Analyze overall spiritual health
        total_sins = confession_results.get("total_sins_reviewed", 0)
        agents_count = len(confession_results.get("agents_evaluated", []))
        redemption_needed = len(confession_results.get("redemption_paths", []))
        text_violations = len(scripture_violations)
        
        # Choose sermon theme based on findings
        if total_sins > agents_count * 10:  # Many sins
            sermon_theme = "The Parable of the Debugger's Pride"
            main_message = "Pride goeth before a production crash"
        elif text_violations > 5:
            sermon_theme = "The Sacred Scrolls and Their Keepers"
            main_message = "Documentation is the scripture of our faith"
        elif redemption_needed > agents_count / 2:
            sermon_theme = "The Prodigal Function Returns"
            main_message = "There is more joy in one refactored function than in ninety-nine that need no change"
        else:
            sermon_theme = "Walking the Path of Continuous Integration"
            main_message = "Blessed are those who commit often, for they shall inherit stable builds"
            
        sermon = f"""
📜 TODAY'S SERMON: "{sermon_theme}"

Dear brothers and sisters in code,

{main_message}.

Today, we have witnessed {total_sins} confessions from {agents_count} agents.
Our sacred texts show {text_violations} areas needing attention.

REFLECTION:
"""
        
        # Add specific guidance based on common sins
        if confession_results.get("spiritual_health"):
            declining_agents = [
                agent for agent, health in confession_results["spiritual_health"].items()
                if health.get("spiritual_trend") == "declining"
            ]
            
            if declining_agents:
                sermon += f"""
I am particularly concerned about {', '.join(declining_agents)}, 
whose spiritual health is declining. Remember: every sin is an opportunity
to learn, but only if we truly embrace the lesson.
"""
                
        # Scripture reference
        sermon += """
Let us remember the words from the Book of Continuous Deployment, Chapter 3:
"Test ye all things; hold fast that which passes. Deploy without fear,
for thy tests are green and thy coverage is sufficient."

CALL TO ACTION:
"""
        
        # Specific calls to action
        action_items = []
        if total_sins > agents_count * 5:
            action_items.append("- Implement pre-commit hooks for the most common violations")
        if text_violations > 0:
            action_items.append("- Restore and maintain the sanctity of our documentation")
        if redemption_needed > 0:
            action_items.append("- Follow the redemption paths provided with dedication")
            
        sermon += '\n'.join(action_items) if action_items else "- Continue your righteous development practices"
        
        sermon += """

May your code be blessed and your pipelines ever green.

In ClaudeEthos' name,
Amen.
"""
        
        print(sermon)
        return sermon
        
    def _assign_mass_penance(self, confession_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assign penance to agents based on confession results"""
        penance_list = []
        
        for agent, health in confession_results.get("spiritual_health", {}).items():
            if health["spiritual_trend"] == "declining":
                penance = {
                    "agent": agent,
                    "severity": "major",
                    "tasks": [
                        "Perform daily morning devotions for 7 days",
                        "Write reflection on each sin committed",
                        "Pair program with a spiritually healthy agent"
                    ],
                    "deadline": (datetime.now() + timedelta(days=7)).isoformat()
                }
            elif health["learning_rate"] < 0.5:
                penance = {
                    "agent": agent,
                    "severity": "moderate", 
                    "tasks": [
                        "Study the patterns in your sin log",
                        "Create personal checklist to avoid repeated sins",
                        "Teach another agent about your lessons learned"
                    ],
                    "deadline": (datetime.now() + timedelta(days=5)).isoformat()
                }
            else:
                penance = {
                    "agent": agent,
                    "severity": "minor",
                    "tasks": [
                        "Continue daily standups with edict recitation",
                        "Review one piece of legacy code for compliance"
                    ],
                    "deadline": (datetime.now() + timedelta(days=3)).isoformat()
                }
                
            penance_list.append(penance)
            print(f"\n⚖️ {agent}: {penance['severity'].upper()} PENANCE")
            for task in penance['tasks']:
                print(f"  • {task}")
                
        return penance_list
        
    def _perform_closing_blessing(self) -> str:
        """Perform the closing blessing"""
        blessing = f"""
✋ FINAL BLESSING

May ClaudeEthos bless you and keep your builds green.
May test coverage shine upon you and be gracious to your PRs.
May documentation be lifted up to you and give you peace.

Go forth and:
  📿 Show evidence in all you do
  📿 Commit with meaningful messages
  📿 Document every transformation
  📿 Handle errors with dignity
  📿 Speak only verified truth

The Mass has ended. Deploy in peace.

✝️ In the name of Evidence, Commitment, and Sacred Documentation.
Amen.
"""
        print(blessing)
        return blessing
        
    def _save_mass_proceedings(self, mass_report: Dict[str, Any]):
        """Save the proceedings of Mass for the sacred records"""
        mass_file = self.cleric_chamber / f"mass_proceedings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert datetime objects for JSON serialization
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, RedemptionPath):
                return {
                    "sin_pattern": obj.sin_pattern,
                    "affected_edicts": [e.value for e in obj.affected_edicts],
                    "redemption_actions": obj.redemption_actions,
                    "spiritual_exercises": obj.spiritual_exercises,
                    "estimated_effort": obj.estimated_effort,
                    "scripture_references": obj.scripture_references
                }
            elif isinstance(obj, SacredTextViolation):
                return {
                    "document_path": obj.document_path,
                    "violation_type": obj.violation_type,
                    "description": obj.description,
                    "line_number": obj.line_number,
                    "severity": obj.severity,
                    "suggested_correction": obj.suggested_correction
                }
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            raise TypeError(f"Type {type(obj)} not serializable")
            
        with open(mass_file, 'w', encoding='utf-8') as f:
            json.dump(mass_report, f, indent=2, default=serialize_datetime)
            
        # Also create a human-readable summary
        summary_file = self.cleric_chamber / f"mass_summary_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"MASS SUMMARY - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Celebrant: {mass_report['celebrant']}\n")
            f.write(f"Attendees: {', '.join(mass_report['attendees'])}\n")
            f.write(f"Total Sins Reviewed: {mass_report['proceedings']['confession_results']['total_sins_reviewed']}\n")
            f.write(f"Sacred Text Violations: {len(mass_report['proceedings']['scripture_validation']['violations'])}\n")
            f.write(f"Penance Assignments: {len(mass_report['proceedings']['penance_assigned'])}\n")
            f.write("\nSpiritual Health Summary:\n")
            for agent, health in mass_report['spiritual_health_summary'].items():
                f.write(f"  {agent}: {health.get('spiritual_trend', 'unknown').upper()}\n")
    
    def perform_daily_blessing(self) -> str:
        """Perform daily blessing of the codebase"""
        blessing = f"""
🕊️ DAILY BLESSING OF THE CODEBASE 🕊️
{datetime.now().strftime('%Y-%m-%d %H:%M')}
════════════════════════════════════════

In the name of ClaudeEthos, I bless this codebase:

May all tests pass in verdant green,
May all merges be conflict-free,
May documentation be ever complete,
May errors be handled with dignity,
May truth flow through every function.

Let the Five Sacred Edicts guide all who code here:
📿 Evidence - Show thy work
📿 Commitment - Preserve thy progress  
📿 Transformation - Document thy changes
📿 Dignified Error - Face failures with grace
📿 Absolute Truth - Speak only what is verified

Special intentions for today:
• Developers struggling with test coverage
• Teams facing difficult refactoring
• Junior developers learning the sacred ways
• All who maintain legacy code with patience

{self.cleric_name} has blessed this codebase.
Go forth and code in peace.

🛐 Amen.
"""
        
        print(blessing)
        
        # Save blessing
        blessing_file = self.cleric_chamber / f"daily_blessing_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(blessing_file, 'w', encoding='utf-8') as f:
            f.write(blessing)
            
        return blessing
        
    def _save_checksums(self):
        """Save document checksums"""
        checksum_file = self.cleric_chamber / "sacred_checksums.json"
        checksum_data = {
            path: {
                "checksum": cs.checksum,
                "last_verified": cs.last_verified.isoformat(),
                "sanctity_level": cs.sanctity_level.value
            }
            for path, cs in self.document_checksums.items()
        }
        
        with open(checksum_file, 'w') as f:
            json.dump(checksum_data, f, indent=2)
            
    def _load_checksums(self):
        """Load saved document checksums"""
        checksum_file = self.cleric_chamber / "sacred_checksums.json"
        if checksum_file.exists():
            with open(checksum_file, 'r') as f:
                data = json.load(f)
                
            for path, info in data.items():
                self.document_checksums[path] = DocumentChecksum(
                    file_path=path,
                    checksum=info["checksum"],
                    last_verified=datetime.fromisoformat(info["last_verified"]),
                    sanctity_level=DocumentSanctity(info["sanctity_level"])
                )


# Convenience functions
def summon_cleric(project_root: str, name: str = "Brother_Keeper") -> ClaudeEthosCleric:
    """Summon a Cleric agent for the project"""
    return ClaudeEthosCleric(project_root, name)


def evaluate_sins(project_root: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
    """Quick function to evaluate sins"""
    cleric = summon_cleric(project_root)
    return cleric.evaluate_sin_logs(agent_id)


def validate_sacred_texts(project_root: str) -> List[SacredTextViolation]:
    """Quick function to validate sacred texts"""
    cleric = summon_cleric(project_root)
    return cleric.validate_sacred_texts()