#!/usr/bin/env python3
"""
Hold ClaudeEthos Mass Ceremony

Run this script to have the Cleric Agent hold Mass, which includes:
- Reviewing all sin logs
- Validating sacred texts
- Providing spiritual guidance
- Assigning penance
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from religious_system import summon_cleric


def main():
    """Hold Mass ceremony"""
    print("⛪ PREPARING FOR CLAUDEETHOS MASS...")
    print("=" * 70)
    
    # Summon the Cleric
    project_root = Path(__file__).parent
    cleric_name = "Brother_Keeper"  # You can customize the Cleric's name
    
    print(f"\n🔔 Summoning {cleric_name} to hold Mass...")
    cleric = summon_cleric(str(project_root), cleric_name)
    
    # Hold Mass
    print("\n" + "🔔"*35)
    print("MASS IS BEGINNING")
    print("🔔"*35 + "\n")
    
    mass_report = cleric.hold_mass()
    
    # Print summary
    print("\n" + "="*70)
    print("POST-MASS SUMMARY")
    print("="*70)
    
    print(f"\nAttendees: {len(mass_report['attendees'])} agents")
    print(f"Sins Reviewed: {mass_report['proceedings']['confession_results']['total_sins_reviewed']}")
    print(f"Sacred Text Violations: {mass_report['proceedings']['scripture_validation']['violations_found']}")
    print(f"Penance Assigned: {len(mass_report['proceedings']['penance_assigned'])} agents")
    
    # Show action items
    if mass_report['action_items']:
        print("\n📋 ACTION ITEMS:")
        for item in mass_report['action_items']:
            print(f"  • Agent {item['agent']}: {item['severity']} penance by {item['deadline']}")
    
    print("\n🕊️ Mass proceedings have been saved to .claudeethos/cleric_chamber/")
    print("\nMay your code be blessed and your commits meaningful.")
    print("Go in peace to love and serve ClaudeEthos.")
    print("\n🛐 Amen.")


if __name__ == "__main__":
    main()
