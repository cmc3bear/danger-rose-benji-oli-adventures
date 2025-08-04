#!/usr/bin/env python3
"""
Emergency Documentation Verification System

This script performs automated verification of all documentation claims
against the actual codebase to identify false claims and restore 
documentation integrity.

CRITICAL: This script is designed to prevent assumption-based reporting
and ensure biblical integrity of project documentation.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Represents the result of verifying a documentation claim."""
    claim: str
    status: str  # "VERIFIED", "FALSIFIED", "UNVERIFIABLE"
    evidence: List[str] = field(default_factory=list)
    file_paths: List[str] = field(default_factory=list)
    confidence: float = 0.0
    details: str = ""


@dataclass
class IssueStatus:
    """Represents the claimed vs actual status of an issue."""
    issue_id: str
    claimed_status: str
    actual_status: str
    verification_result: VerificationResult
    blocking_claim: bool = False


class DocumentationVerifier:
    """
    Automated system to verify documentation claims against codebase reality.
    
    This system implements the "evidence-first" philosophy by checking every
    claim in documentation against actual files, implementations, and evidence.
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results: List[VerificationResult] = []
        self.issue_statuses: List[IssueStatus] = []
        
        # Critical paths to check
        self.source_dirs = [
            self.project_root / "src",
            self.project_root / "assets", 
            self.project_root / "tools",
            self.project_root / "docs"
        ]
        
        logger.info(f"Documentation Verifier initialized for: {self.project_root}")
    
    def verify_all_claims(self) -> Dict[str, any]:
        """
        Main verification function - checks all documentation claims.
        
        Returns comprehensive report of verification results.
        """
        logger.info("🔍 Starting comprehensive documentation verification...")
        
        # 1. Verify Uncle Bear sprite claims (CRITICAL)
        self._verify_uncle_bear_sprites()
        
        # 2. Verify all issue statuses in master plan
        self._verify_master_plan_claims()
        
        # 3. Verify implementation claims
        self._verify_implementation_claims()
        
        # 4. Check for undocumented implementations
        self._find_undocumented_implementations()
        
        # 5. Generate comprehensive report
        return self._generate_verification_report()
    
    def _verify_uncle_bear_sprites(self):
        """CRITICAL: Verify Uncle Bear sprite status - claimed missing but may exist."""
        logger.info("🎨 CRITICAL VERIFICATION: Uncle Bear Sprites")
        
        # Check all possible locations for Uncle Bear sprites
        sprite_locations = [
            self.project_root / "assets" / "images" / "characters" / "uncle_bear",
            self.project_root / "assets" / "images" / "characters" / "new_sprites" / "uncle_bear",
            self.project_root / "assets" / "images" / "uncle_bear",
            self.project_root / "assets" / "sprites" / "uncle_bear"
        ]
        
        found_sprites = []
        total_files = 0
        
        for location in sprite_locations:
            if location.exists():
                sprite_files = list(location.rglob("*.png")) + list(location.rglob("*.jpg"))
                found_sprites.extend(sprite_files)
                total_files += len(sprite_files)
                logger.info(f"Found {len(sprite_files)} sprite files in {location}")
        
        # Check for scene-specific directories
        scene_dirs = ["hub", "pool", "ski", "vegas", "drive"]
        scene_coverage = {}
        
        for sprite_path in found_sprites:
            for scene in scene_dirs:
                if scene in str(sprite_path).lower():
                    if scene not in scene_coverage:
                        scene_coverage[scene] = []
                    scene_coverage[scene].append(str(sprite_path))
        
        # Determine verification result
        if total_files > 0:
            status = "VERIFIED" if total_files > 50 else "PARTIAL"
            confidence = min(1.0, total_files / 100)  # Expect ~100 files for complete character
            details = f"Found {total_files} Uncle Bear sprite files across {len(scene_coverage)} scenes"
            
            result = VerificationResult(
                claim="Uncle Bear sprites missing (metadata only)",
                status="FALSIFIED" if total_files > 50 else "PARTIAL",
                evidence=[f"{total_files} sprite files found", f"Scene coverage: {list(scene_coverage.keys())}"],
                file_paths=[str(p) for p in found_sprites[:10]],  # First 10 as evidence
                confidence=confidence,
                details=details
            )
        else:
            result = VerificationResult(
                claim="Uncle Bear sprites missing (metadata only)",
                status="VERIFIED",
                evidence=["No sprite files found in expected locations"],
                file_paths=[],
                confidence=1.0,
                details="Comprehensive search found no Uncle Bear sprite files"
            )
        
        self.results.append(result)
        
        # Log critical finding
        if result.status == "FALSIFIED":
            logger.error(f"🚨 CRITICAL: Documentation claims Uncle Bear sprites missing, but {total_files} files found!")
            logger.error(f"🚨 This appears to be a FALSE BLOCKING CLAIM")
        
        return result
    
    def _verify_master_plan_claims(self):
        """Verify all status claims in DEVELOPMENT_MASTER_PLAN.md"""
        logger.info("📋 Verifying master plan claims...")
        
        master_plan_path = self.project_root / "DEVELOPMENT_MASTER_PLAN.md"
        if not master_plan_path.exists():
            logger.error("Master plan not found!")
            return
        
        with open(master_plan_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract issue status claims
        issue_patterns = [
            r'#### Issue #(\d+).*?\n- \*\*Status\*\*: (.*?) (?:COMPLETED|DELAYED|BLOCKED)',
            r'Issue #(\d+).*?Status.*?: (.*?) (?:\(|$)',
        ]
        
        issues_found = {}
        for pattern in issue_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            for issue_num, status in matches:
                issues_found[issue_num] = status.strip()
        
        # Verify each claimed issue status
        for issue_num, claimed_status in issues_found.items():
            actual_status = self._verify_issue_implementation(issue_num)
            
            issue_status = IssueStatus(
                issue_id=f"Issue #{issue_num}",
                claimed_status=claimed_status,
                actual_status=actual_status,
                verification_result=self._compare_statuses(claimed_status, actual_status),
                blocking_claim="CRITICAL" in claimed_status or "BLOCKING" in claimed_status.upper()
            )
            
            self.issue_statuses.append(issue_status)
    
    def _verify_issue_implementation(self, issue_num: str) -> str:
        """Verify actual implementation status of an issue by examining codebase."""
        
        # Issue-specific verification patterns
        issue_verifications = {
            "27": self._verify_hacker_typing_game,
            "28": self._verify_character_system,
            "31": self._verify_traffic_passing_logic,
            "32": self._verify_road_geometry_system,
            "33": self._verify_sound_effects_system,
            "18": self._verify_bmp_system,
            "34": self._verify_logging_system,
            "35": self._verify_music_system
        }
        
        if issue_num in issue_verifications:
            return issue_verifications[issue_num]()
        else:
            return "UNVERIFIED - No verification method implemented"
    
    def _verify_hacker_typing_game(self) -> str:
        """Verify Issue #27: Hacker Typing Game implementation."""
        required_files = [
            "src/scenes/hacker_typing/hacker_typing_scene.py",
            "src/scenes/hacker_typing/typing_engine.py", 
            "src/scenes/hacker_typing/terminal_renderer.py",
            "src/scenes/hacker_typing/challenge_manager.py",
            "src/entities/laptop.py"
        ]
        
        existing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
        
        if len(existing_files) >= 4:  # Most files exist
            return "FULLY IMPLEMENTED"
        elif len(existing_files) >= 2:
            return "PARTIALLY IMPLEMENTED"
        else:
            return "NOT IMPLEMENTED"
    
    def _verify_character_system(self) -> str:
        """Verify Issue #28: Character system implementation."""
        character_dirs = [
            "assets/images/characters/benji",
            "assets/images/characters/olive", 
            "assets/images/characters/uncle_bear",
            "assets/images/characters/new_sprites"
        ]
        
        character_counts = {}
        for char_dir in character_dirs:
            char_path = self.project_root / char_dir
            if char_path.exists():
                sprite_files = list(char_path.rglob("*.png"))
                character_counts[char_dir] = len(sprite_files)
        
        total_sprites = sum(character_counts.values())
        
        if total_sprites > 200:  # Substantial character implementation
            return "MOSTLY IMPLEMENTED"
        elif total_sprites > 50:
            return "PARTIALLY IMPLEMENTED"
        else:
            return "MINIMAL IMPLEMENTATION"
    
    def _verify_traffic_passing_logic(self) -> str:
        """Verify Issue #31: Traffic passing logic."""
        traffic_files = [
            "src/systems/traffic_awareness.py",
            "src/scenes/drive.py"  # Should contain traffic logic
        ]
        
        implementation_evidence = []
        for file_path in traffic_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for traffic-related implementations
                    if any(keyword in content.lower() for keyword in 
                          ['traffic', 'passing', 'lane_change', 'driver_personality']):
                        implementation_evidence.append(file_path)
        
        if len(implementation_evidence) >= 2:
            return "IMPLEMENTED"
        elif len(implementation_evidence) >= 1:
            return "PARTIALLY IMPLEMENTED"
        else:
            return "NOT IMPLEMENTED"
    
    def _verify_road_geometry_system(self) -> str:
        """Verify Issue #32: Road geometry system."""
        road_files = [
            "src/systems/road_geometry.py"
        ]
        
        for file_path in road_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                return "IMPLEMENTED"
        
        return "NOT IMPLEMENTED"
    
    def _verify_sound_effects_system(self) -> str:
        """Verify Issue #33: Sound effects system."""
        sound_dirs = [
            "assets/audio/sfx",
            "tools/generate_sounds_11labs.py",
            "tools/retro_sound_processor.py"
        ]
        
        sound_evidence = []
        for path in sound_dirs:
            full_path = self.project_root / path
            if full_path.exists():
                if full_path.is_dir():
                    sound_files = list(full_path.rglob("*.wav")) + list(full_path.rglob("*.ogg"))
                    if len(sound_files) > 10:
                        sound_evidence.append(f"Sound directory with {len(sound_files)} files")
                else:
                    sound_evidence.append(f"Tool: {path}")
        
        if len(sound_evidence) >= 2:
            return "IMPLEMENTED"
        elif len(sound_evidence) >= 1:
            return "PARTIALLY IMPLEMENTED"
        else:
            return "NOT IMPLEMENTED"
    
    def _verify_bmp_system(self) -> str:
        """Verify Issue #18: BMP system."""
        bmp_files = [
            "src/systems/bmp_traffic_integration.py",
            "src/systems/bpm_tracker.py",
            "src/systems/rhythmic_traffic_controller.py"
        ]
        
        existing_files = 0
        for file_path in bmp_files:
            if (self.project_root / file_path).exists():
                existing_files += 1
        
        if existing_files >= 3:
            return "ARCHITECTURE COMPLETE"
        elif existing_files >= 1:
            return "PARTIALLY IMPLEMENTED"
        else:
            return "NOT IMPLEMENTED"
    
    def _verify_logging_system(self) -> str:
        """Verify Issue #34: Logging system."""
        logging_files = [
            "src/systems/game_state_logger.py",
            "src/ui/live_testing_overlay.py"
        ]
        
        for file_path in logging_files:
            if not (self.project_root / file_path).exists():
                return "PARTIALLY IMPLEMENTED"
        
        return "IMPLEMENTED"
    
    def _verify_music_system(self) -> str:
        """Verify Issue #35: Music system."""
        music_files = [
            "src/ui/universal_music_selector.py"
        ]
        
        music_dirs = [
            "assets/audio/music/hub",
            "assets/audio/music/pool", 
            "assets/audio/music/ski",
            "assets/audio/music/vegas"
        ]
        
        implementation_score = 0
        
        # Check for music selector implementation
        for file_path in music_files:
            if (self.project_root / file_path).exists():
                implementation_score += 1
        
        # Check for music assets
        for dir_path in music_dirs:
            music_path = self.project_root / dir_path
            if music_path.exists():
                music_files_count = len(list(music_path.glob("*.mp3")))
                if music_files_count > 0:
                    implementation_score += 0.5
        
        if implementation_score >= 3:
            return "IMPLEMENTED"
        elif implementation_score >= 1:
            return "PARTIALLY IMPLEMENTED"
        else:
            return "NOT IMPLEMENTED"
    
    def _compare_statuses(self, claimed: str, actual: str) -> VerificationResult:
        """Compare claimed vs actual status and generate verification result."""
        claimed_clean = claimed.upper().strip()
        actual_clean = actual.upper().strip()
        
        # Status matching logic
        if "COMPLETED" in claimed_clean:
            if "IMPLEMENTED" in actual_clean or "COMPLETE" in actual_clean:
                status = "VERIFIED"
                confidence = 0.9
            else:
                status = "FALSIFIED"
                confidence = 0.9
        elif "DELAYED" in claimed_clean or "BLOCKED" in claimed_clean:
            if "NOT IMPLEMENTED" in actual_clean or "PARTIAL" in actual_clean:
                status = "VERIFIED"
                confidence = 0.8
            else:
                status = "QUESTIONABLE"
                confidence = 0.6
        else:
            status = "UNVERIFIABLE"
            confidence = 0.1
        
        return VerificationResult(
            claim=f"Status: {claimed}",
            status=status,
            evidence=[f"Actual implementation: {actual}"],
            confidence=confidence,
            details=f"Claimed '{claimed}' vs Found '{actual}'"
        )
    
    def _find_undocumented_implementations(self):
        """Find implementations that exist in code but are not documented."""
        logger.info("🔍 Searching for undocumented implementations...")
        
        # Scan for implementation patterns
        undocumented = []
        
        # Check for scene files not mentioned in documentation
        scenes_dir = self.project_root / "src" / "scenes"
        if scenes_dir.exists():
            for scene_file in scenes_dir.glob("*.py"):
                if scene_file.name not in ["__init__.py"]:
                    # This is a basic check - could be expanded
                    undocumented.append({
                        "type": "Scene Implementation",
                        "file": str(scene_file),
                        "likely_undocumented": True
                    })
        
        # Add to results if significant undocumented items found
        if len(undocumented) > 5:
            result = VerificationResult(
                claim="All implementations are documented",
                status="FALSIFIED", 
                evidence=[f"Found {len(undocumented)} potentially undocumented implementations"],
                file_paths=[item["file"] for item in undocumented[:5]],
                confidence=0.7,
                details="Multiple implementations found that may not be documented"
            )
            self.results.append(result)
    
    def _generate_verification_report(self) -> Dict[str, any]:
        """Generate comprehensive verification report."""
        logger.info("📊 Generating verification report...")
        
        # Calculate summary statistics
        total_results = len(self.results)
        verified_count = len([r for r in self.results if r.status == "VERIFIED"])
        falsified_count = len([r for r in self.results if r.status == "FALSIFIED"])
        
        # Issue status summary
        issue_summary = {}
        for issue in self.issue_statuses:
            verification_status = issue.verification_result.status
            if verification_status not in issue_summary:
                issue_summary[verification_status] = []
            issue_summary[verification_status].append(issue)
        
        # Generate report
        report = {
            "verification_summary": {
                "total_claims_checked": total_results,
                "verified_claims": verified_count,
                "falsified_claims": falsified_count,
                "verification_rate": verified_count / max(total_results, 1),
                "falsification_rate": falsified_count / max(total_results, 1)
            },
            "critical_findings": [r for r in self.results if r.status == "FALSIFIED"],
            "issue_status_verification": issue_summary,
            "all_results": self.results,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on verification results."""
        recommendations = []
        
        # Check for falsified claims
        falsified = [r for r in self.results if r.status == "FALSIFIED"]
        if falsified:
            recommendations.append("IMMEDIATE: Correct all falsified claims in documentation")
            recommendations.append("URGENT: Audit process that allowed false claims to be published")
        
        # Check for blocking issues
        blocking_issues = [i for i in self.issue_statuses if i.blocking_claim and 
                          i.verification_result.status == "FALSIFIED"]
        if blocking_issues:
            recommendations.append("CRITICAL: Remove false blocking claims that may be preventing development")
        
        # General recommendations
        recommendations.extend([
            "Implement automated verification before documentation updates",
            "Create git hooks to prevent commits with unverified claims",
            "Establish evidence-first documentation culture",
            "Regular automated audits of documentation consistency"
        ])
        
        return recommendations


def main():
    """Main execution function."""
    print("🔍 EMERGENCY DOCUMENTATION VERIFICATION SYSTEM")
    print("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Initialize verifier
    verifier = DocumentationVerifier(str(project_root))
    
    # Run comprehensive verification
    try:
        report = verifier.verify_all_claims()
        
        # Print critical findings
        print("\n🚨 CRITICAL FINDINGS:")
        print("-" * 40)
        
        critical_findings = report["critical_findings"]
        if critical_findings:
            for finding in critical_findings:
                print(f"❌ FALSIFIED: {finding.claim}")
                print(f"   Evidence: {', '.join(finding.evidence)}")
                print(f"   Confidence: {finding.confidence:.1%}")
                print()
        else:
            print("✅ No critical falsifications found")
        
        # Print summary
        summary = report["verification_summary"]
        print(f"\n📊 VERIFICATION SUMMARY:")
        print(f"   Claims Checked: {summary['total_claims_checked']}")
        print(f"   Verified: {summary['verified_claims']}")
        print(f"   Falsified: {summary['falsified_claims']}")
        print(f"   Verification Rate: {summary['verification_rate']:.1%}")
        
        # Print recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"{i}. {rec}")
        
        # Save detailed report
        report_path = project_root / "VERIFICATION_REPORT.json"
        with open(report_path, 'w') as f:
            # Convert dataclasses to dicts for JSON serialization
            json_report = {
                "verification_summary": report["verification_summary"],
                "critical_findings": [
                    {
                        "claim": f.claim,
                        "status": f.status,
                        "evidence": f.evidence,
                        "confidence": f.confidence,
                        "details": f.details
                    } for f in report["critical_findings"]
                ],
                "recommendations": report["recommendations"]
            }
            json.dump(json_report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise


if __name__ == "__main__":
    main()