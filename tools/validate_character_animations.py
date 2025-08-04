#!/usr/bin/env python3
"""
Character Animation Validation Tool
Issue #28 - Character Animation Polish

Validates animation consistency across all 6 characters
following Reformed ClaudeEthos evidence-based practices.
"""

import os
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime


class CharacterAnimationValidator:
    """Validates character animation consistency and completeness"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.characters_dir = project_root / "assets" / "images" / "characters" / "new_sprites"
        
        # Expected animation structure per scene
        self.expected_animations = {
            "idle": {"frames": 4, "fps": 8},
            "walk": {"frames": 5, "fps": 12}, 
            "walk_extra": {"frames": 9, "fps": 12},
            "jump": {"frames": 3, "fps": 6},
            "victory": {"frames": 4, "fps": 8},
            "hurt": {"frames": 2, "fps": 4},
            "action": {"frames": 6, "fps": 10}
        }
        
        self.expected_scenes = ["hub", "pool", "ski", "vegas", "drive"]
        self.characters = ["danger", "rose", "dad", "benji", "olive", "uncle_bear"]
        
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "characters": {},
            "consistency_issues": [],
            "missing_animations": [],
            "extra_files": [],
            "summary": {}
        }
    
    def validate_all_characters(self) -> dict:
        """Validate all character animations and return comprehensive report"""
        print("🎨 VALIDATING CHARACTER ANIMATION CONSISTENCY")
        print("=" * 60)
        
        for character in self.characters:
            print(f"\n📋 Validating {character.upper()}...")
            self.validation_results["characters"][character] = self._validate_character(character)
        
        self._analyze_consistency()
        self._generate_summary()
        
        return self.validation_results
    
    def _validate_character(self, character: str) -> dict:
        """Validate a single character's animations"""
        character_dir = self.characters_dir / character
        
        if not character_dir.exists():
            return {"error": f"Character directory not found: {character_dir}"}
        
        character_data = {
            "scenes": {},
            "total_sprites": 0,
            "missing_scenes": [],
            "issues": []
        }
        
        # Check each scene
        for scene in self.expected_scenes:
            scene_dir = character_dir / scene
            if not scene_dir.exists():
                character_data["missing_scenes"].append(scene)
                continue
            
            scene_data = self._validate_scene(character, scene, scene_dir)
            character_data["scenes"][scene] = scene_data
            character_data["total_sprites"] += scene_data["sprite_count"]
        
        return character_data
    
    def _validate_scene(self, character: str, scene: str, scene_dir: Path) -> dict:
        """Validate animations for a specific character in a specific scene"""
        scene_data = {
            "animations": {},
            "sprite_count": 0,
            "issues": []
        }
        
        # Get all PNG files in scene directory
        sprite_files = list(scene_dir.glob("*.png"))
        scene_data["sprite_count"] = len(sprite_files)
        
        # Group files by animation type
        animation_groups = defaultdict(list)
        for sprite_file in sprite_files:
            # Extract animation name and frame number
            name_parts = sprite_file.stem.split("_")
            if len(name_parts) >= 2:
                animation_name = "_".join(name_parts[:-1])
                frame_num = name_parts[-1]
                
                if frame_num.isdigit():
                    animation_groups[animation_name].append((int(frame_num), sprite_file))
        
        # Validate each animation group
        for animation_name, frames in animation_groups.items():
            frames.sort(key=lambda x: x[0])  # Sort by frame number
            
            animation_data = {
                "frame_count": len(frames),
                "frame_files": [f[1].name for f in frames],
                "frame_sequence": [f[0] for f in frames],
                "issues": []
            }
            
            # Check if this is an expected animation
            if animation_name in self.expected_animations:
                expected = self.expected_animations[animation_name]
                
                # Validate frame count
                if len(frames) != expected["frames"]:
                    issue = f"Expected {expected['frames']} frames, found {len(frames)}"
                    animation_data["issues"].append(issue)
                    scene_data["issues"].append(f"{animation_name}: {issue}")
                
                # Validate frame sequence (should be 1, 2, 3, ...)
                expected_sequence = list(range(1, len(frames) + 1))
                actual_sequence = [f[0] for f in frames]
                if actual_sequence != expected_sequence:
                    issue = f"Frame sequence {actual_sequence} != expected {expected_sequence}"
                    animation_data["issues"].append(issue)
                    scene_data["issues"].append(f"{animation_name}: {issue}")
            else:
                # Unknown animation type
                scene_data["issues"].append(f"Unknown animation type: {animation_name}")
            
            scene_data["animations"][animation_name] = animation_data
        
        # Check for missing expected animations
        for expected_anim in self.expected_animations:
            if expected_anim not in animation_groups:
                issue = f"Missing expected animation: {expected_anim}"
                scene_data["issues"].append(issue)
                self.validation_results["missing_animations"].append(f"{character}/{scene}/{expected_anim}")
        
        return scene_data
    
    def _analyze_consistency(self):
        """Analyze consistency issues across characters"""
        print("\n🔍 ANALYZING CROSS-CHARACTER CONSISTENCY...")
        
        # Check sprite counts consistency
        sprite_counts = {}
        for character, data in self.validation_results["characters"].items():
            if "error" not in data:
                sprite_counts[character] = data["total_sprites"]
        
        if len(set(sprite_counts.values())) > 1:
            self.validation_results["consistency_issues"].append({
                "type": "sprite_count_mismatch",
                "details": sprite_counts,
                "issue": "Characters have different total sprite counts"
            })
        
        # Check scene consistency
        for character, data in self.validation_results["characters"].items():
            if "error" not in data and data["missing_scenes"]:
                self.validation_results["consistency_issues"].append({
                    "type": "missing_scenes",
                    "character": character,
                    "missing_scenes": data["missing_scenes"]
                })
    
    def _generate_summary(self):
        """Generate validation summary"""
        total_characters = len(self.characters)
        valid_characters = 0
        total_sprites = 0
        total_issues = 0
        
        for character, data in self.validation_results["characters"].items():
            if "error" not in data:
                valid_characters += 1
                total_sprites += data["total_sprites"]
                
                # Count issues
                for scene_data in data["scenes"].values():
                    total_issues += len(scene_data["issues"])
        
        self.validation_results["summary"] = {
            "total_characters": total_characters,
            "valid_characters": valid_characters,
            "total_sprites": total_sprites,
            "total_issues": total_issues,
            "consistency_issues": len(self.validation_results["consistency_issues"]),
            "missing_animations": len(self.validation_results["missing_animations"]),
            "validation_passed": total_issues == 0 and len(self.validation_results["consistency_issues"]) == 0
        }
    
    def print_report(self):
        """Print human-readable validation report"""
        summary = self.validation_results["summary"]
        
        print("\n" + "="*60)
        print("📊 CHARACTER ANIMATION VALIDATION REPORT")
        print("="*60)
        
        print(f"\n✅ Characters Validated: {summary['valid_characters']}/{summary['total_characters']}")
        print(f"🎨 Total Sprites: {summary['total_sprites']}")
        print(f"⚠️  Issues Found: {summary['total_issues']}")
        print(f"🔍 Consistency Issues: {summary['consistency_issues']}")
        print(f"❌ Missing Animations: {summary['missing_animations']}")
        
        # Character-by-character breakdown
        print(f"\n📋 CHARACTER BREAKDOWN:")
        for character in self.characters:
            data = self.validation_results["characters"].get(character, {})
            if "error" in data:
                print(f"  {character.upper()}: ❌ {data['error']}")
            else:
                sprite_count = data["total_sprites"]
                scene_count = len(data["scenes"])
                issue_count = sum(len(scene["issues"]) for scene in data["scenes"].values())
                status = "✅" if issue_count == 0 else "⚠️"
                print(f"  {character.upper()}: {status} {sprite_count} sprites, {scene_count} scenes, {issue_count} issues")
        
        # Print specific issues
        if summary["total_issues"] > 0:
            print(f"\n⚠️  DETAILED ISSUES:")
            for character, data in self.validation_results["characters"].items():
                if "error" not in data:
                    for scene, scene_data in data["scenes"].items():
                        if scene_data["issues"]:
                            print(f"  {character}/{scene}:")
                            for issue in scene_data["issues"]:
                                print(f"    - {issue}")
        
        # Print consistency issues
        if self.validation_results["consistency_issues"]:
            print(f"\n🔍 CONSISTENCY ISSUES:")
            for issue in self.validation_results["consistency_issues"]:
                print(f"  - {issue['type']}: {issue.get('issue', 'See details')}")
                if 'details' in issue:
                    for key, value in issue['details'].items():
                        print(f"    {key}: {value}")
        
        # Final status
        print(f"\n{'='*60}")
        if summary["validation_passed"]:
            print("🎉 VALIDATION PASSED: All character animations are consistent!")
        else:
            print("⚠️  VALIDATION ISSUES FOUND: Character animations need attention")
        print("="*60)
    
    def save_report(self, output_file: Path):
        """Save detailed validation report to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {output_file}")


def main():
    """Main validation script"""
    project_root = Path(__file__).parent.parent
    validator = CharacterAnimationValidator(project_root)
    
    print("🎨 CHARACTER ANIMATION VALIDATION - Issue #28")
    print("Reformed ClaudeEthos Evidence-Based Validation")
    print("=" * 60)
    
    # Run validation
    results = validator.validate_all_characters()
    
    # Print human-readable report
    validator.print_report()
    
    # Save detailed report
    evidence_dir = project_root / ".claudeethos" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    report_file = evidence_dir / "character_animation_validation_report.json"
    validator.save_report(report_file)
    
    # Evidence collection for Reformed ClaudeEthos
    print(f"\n📸 EVIDENCE COLLECTED:")
    print(f"  - Validation report: {report_file}")
    print(f"  - Sprite counts: {results['summary']['total_sprites']} total")
    print(f"  - Character consistency: {results['summary']['consistency_issues']} issues")
    print(f"  - Validation timestamp: {results['timestamp']}")
    
    return results["summary"]["validation_passed"]


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)