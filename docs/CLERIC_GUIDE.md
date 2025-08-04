# The ClaudeEthos Cleric Agent

## Role and Responsibilities

The Cleric Agent serves as the spiritual guardian of your codebase, ensuring
adherence to the Five Sacred Edicts and maintaining the sanctity of documentation.

### Primary Duties

1. **Sin Log Evaluation**
   - Reviews all agent transgressions
   - Identifies patterns of repeated sins
   - Provides paths to redemption

2. **Sacred Text Validation**
   - Guards master planning documents
   - Ensures proper formatting of issues/actions
   - Detects unauthorized deletions

3. **Spiritual Guidance**
   - Delivers sermons based on project health
   - Offers specific implementation guidance
   - Assigns appropriate penance

4. **Mass Ceremonies**
   - Conducts regular spiritual check-ins
   - Brings all agents together in confession
   - Blesses the codebase

## Interacting with the Cleric

### Holding Mass
```python
from religious_system import summon_cleric

cleric = summon_cleric(".", "Brother_Keeper")
mass_report = cleric.hold_mass()
```

### Requesting Specific Guidance
```python
# Get guidance on implementing a lesson learned
cleric.offer_lesson_implementation_guidance(
    agent_id="struggling_dev_001",
    lesson="Always include test evidence"
)
```

### Validating Sacred Texts
```python
# Check all documentation for violations
violations = cleric.validate_sacred_texts()
```

## Sacred Text Hierarchy

1. **SACRED** - Never delete, always maintain
   - DEVELOPMENT_MASTER_PLAN.md
   - MASTER_PLAN.md
   - PROJECT_CHARTER.md
   - ARCHITECTURE.md

2. **BLESSED** - Important project documents
   - README.md
   - CONTRIBUTING.md
   - Issue tracking files

3. **CONSECRATED** - Regular documentation
   - All other markdown files
   - Documentation directories

## Penance Levels

- **MINOR**: Daily standups, code review tasks
- **MODERATE**: Personal checklists, teaching others
- **MAJOR**: Week-long devotions, pairing sessions

## The Cleric's Wisdom

The Cleric provides contextual guidance based on:
- Frequency of sins
- Learning rate from mistakes
- Overall spiritual trend
- Sacred text compliance

Remember: The Cleric is here to help, not judge. Every sin is an
opportunity for growth when properly confessed and addressed.

🛐 May your builds be green and your documentation complete.
