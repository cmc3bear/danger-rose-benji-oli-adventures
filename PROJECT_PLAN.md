# Danger Rose - Living Project Plan

## Project Overview
**Project Type**: Creative (Game)  
**Status**: Active Development  
**Last Updated**: 2025-08-01 00:00:00 UTC  
**Primary Language**: Python  
**Framework**: Pygame  
**Project Lead**: Claude  

### Project Description
A family-friendly adventure game featuring Rose and her dad in various mini-game scenarios. Combines wholesome gameplay with engaging mechanics across different themed levels including pool games, skiing adventures, and Las Vegas challenges.

### Key Objectives
1. Create engaging, family-friendly gameplay experiences
2. Implement varied mini-games with consistent quality
3. Develop charming visual and audio presentation
4. Ensure accessibility for all ages
5. Build modular architecture for easy content addition

## Team & Reviewers

### Primary Development Team
- **Lead Developer**: Claude
- **Game Design Lead**: Sofia Blackwood
- **Family Content Specialist**: Zara Okafor
- **Technical Lead**: Jordan Kim

### Designated Review Agents
| Agent | Role | Review Focus | Persona Type |
|-------|------|--------------|--------------|
| Zara Okafor | Content Lead | Family-friendliness, accessibility | Empath |
| Sofia Blackwood | Narrative Lead | Story coherence, character development | Oracle |
| Jordan Kim | QA Lead | Gameplay testing, bug detection | Architect |
| Viktor Petrov | Gameplay Lead | Game mechanics, difficulty balance | Gladiator |
| Alex Rodriguez | Performance Lead | FPS optimization, resource usage | Optimizer |

### Agent Personas
[Link to full agent persona documentation: [MASTER_AGENT_PERSONAS.md](../MASTER_AGENT_PERSONAS.md)]

## Development Standards

### Coding Standards
- **Style Guide**: PEP 8 for Python
- **Linting**: `ruff`, `black` for formatting
- **Documentation**: Clear docstrings, gameplay comments

### Testing Requirements
- **Unit Test Coverage**: Minimum 80%
- **Gameplay Testing**: All mini-games tested
- **Performance Targets**: 60 FPS on modest hardware
- **Accessibility Testing**: Age 7+ usability

### Content Standards
- **Family-Friendly**: No violence, appropriate humor
- **Educational Value**: Problem-solving elements
- **Positive Themes**: Family bonding, adventure
- **Inclusive Design**: Accessible to various skill levels

## Pipeline Commands

### Project-Specific Commands
```bash
# Initialize project
/pipeline-init danger-rose

# Development workflow
/pipeline-develop [feature-name] --project=danger-rose

# Content review (family-friendly focus)
/zara-review danger-rose --family-content

# Narrative review
/sofia-review danger-rose --character-development

# Gameplay testing
/viktor-test danger-rose --gameplay-balance

# Performance optimization
/alex-optimize danger-rose --pygame-performance

# Full review
/pipeline-review danger-rose --narrative=dramatic
```

### Custom Commands
```bash
# Game execution
python src/main.py               # Run the game
make run                        # Alternative launcher

# Development tools
generate_placeholder_audio.py    # Create audio placeholders
extract_sprite_frames.py        # Sprite extraction
check_assets.py                 # Verify assets
download_assets.py              # Asset downloader

# Audio tools
download_audio.py               # Download audio assets
convert_wav_to_ogg.py          # Audio conversion

# Testing
pytest tests/                   # Run test suite
pytest tests/test_vegas_boss.py # Specific test
```

## Change Management

### Change Ticket Format
All changes must be documented in the TICKETS/ directory:

```yaml
Ticket ID: [ROSE-2025-08-01-001]
Type: [Feature/Bug/Content/Gameplay/Performance/Polish]
Priority: [Critical/High/Medium/Low]
Status: [Open/In Progress/Review/Closed]

From State:
  - [Description of original state]
  - [Relevant code/assets]

To State:
  - [Description of new state]
  - [New implementation]

Rationale:
  - [Why this change is necessary]
  - [Expected impact on gameplay]

Developer: [Name/Claude]
Timestamp: [YYYY-MM-DD HH:MM:SS UTC]

Testing:
  - Test Type: [Unit/Gameplay/Performance/Accessibility]
  - Test Cases: [List of test cases]
  - Pass/Fail: [Status]
  - FPS Impact: [If applicable]

Review:
  - Reviewer: [Agent name]
  - Review Type: [Content/Gameplay/Technical/Performance]
  - Status: [Approved/Changes Requested/Rejected]
  - Comments: [Review feedback]
  - Timestamp: [YYYY-MM-DD HH:MM:SS UTC]
```

### Recent Changes
- [ROSE-2025-07-30-001](./TICKETS/ROSE-2025-07-30-001.yaml) - Vegas boss implementation
- [ROSE-2025-07-29-001](./TICKETS/ROSE-2025-07-29-001.yaml) - Sound manager improvements

## Completed Items

### Milestones Achieved
- [x] Initial game framework
- [x] Basic player movement
- [x] Pool game mechanics
- [x] Skiing level prototype
- [x] Sound system
- [ ] Vegas boss fight
- [ ] Trophy system
- [ ] All mini-games complete
- [ ] Final polish and release

### Feature Implementations
| Feature | Completion Date | Ticket Links | Review Status |
|---------|----------------|--------------|---------------|
| Core game loop | 2025-07-01 | ROSE-2025-07-01-001 | Approved by Jordan |
| Pool mechanics | 2025-07-10 | ROSE-2025-07-10-001 | Approved by Viktor |
| Skiing gameplay | 2025-07-20 | ROSE-2025-07-20-001 | Approved by Zara |
| Sound manager | 2025-07-29 | ROSE-2025-07-29-001 | Under review |

## Active Development

### Current Sprint/Phase
**Sprint**: The Drive Enhancement & Vegas Polish  
**Duration**: 2025-08-02 - 2025-08-16  
**Goals**: Implement EV car selection system, complete Vegas boss, implement trophy system

### In Progress
- [ ] **EV Car Selection System** - Assignee: Claude - Due: 2025-08-09 - **PRIORITY: HIGH**
  - Implement vehicle selector UI
  - Integrate EV sprites into gameplay
  - Add vehicle persistence to save system
  - Create selection flow after music choice
- [ ] Vegas boss battle - Assignee: Claude - Due: 2025-08-12
- [ ] Trophy shelf system - Assignee: Claude - Due: 2025-08-14
- [ ] Particle effects - Assignee: Claude - Due: 2025-08-16

### Backlog
- [ ] Additional mini-games
- [ ] Cutscene system
- [ ] Achievement system
- [ ] Level select hub improvements
- [ ] Character customization
- [ ] Bonus content unlocks
- [ ] Speedrun mode
- [ ] Two-player modes

## Testing & Validation

### Test Coverage
- **Unit Tests**: 82%
- **Integration Tests**: Core systems tested
- **Gameplay Tests**: Manual testing ongoing
- **Performance Tests**: Stable 60 FPS

### Quality Metrics
- **Bug Count**: 3 known minor issues
- **Performance**: 60 FPS on Intel HD Graphics
- **Load Times**: < 2 seconds
- **Memory Usage**: < 200MB

### Continuous Integration
- **CI Platform**: GitHub Actions
- **Build Status**: Passing
- **Last Successful Build**: 2025-07-31 22:00:00 UTC

## Deployment & Operations

### Deployment Strategy
- **Target Platforms**: Windows, Linux, macOS
- **Distribution**: itch.io, potential Steam release
- **Packaging**: PyInstaller for standalone builds

### Asset Management
- **Sprites**: Original pixel art
- **Audio**: Licensed/generated sounds
- **Music**: Original compositions planned
- **Storage**: Organized asset directories

## Documentation

### Available Documentation
- [README.md](./README.md) - Project overview
- [CLAUDE.md](./CLAUDE.md) - Development context
- [GAME_DESIGN.md](./GAME_DESIGN.md) - Design document
- [TECHNICAL_ARCHITECTURE.md](./TECHNICAL_ARCHITECTURE.md) - Tech details
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guide
- [PRD.md](./PRD.md) - Product requirements

### Documentation Standards
All changes must include:
1. Updated code comments
2. Updated design docs for gameplay changes
3. Asset documentation for new content
4. Change ticket with full context

## Maintenance Notes

### Regular Maintenance Tasks
- [ ] Weekly playtest with `/viktor-test`
- [ ] Bi-weekly content review with `/zara-review`
- [ ] Monthly performance check with `/alex-optimize`
- [ ] Quarterly full game review

### Known Issues
- Minor audio delay on some systems (ticket: ROSE-2025-07-28-001)
- Sprite sorting issues in skiing level (ticket: ROSE-2025-07-27-001)

### Technical Debt
1. **Refactor scene management** - Priority: Medium
   - Current system has duplicate code
   - Plan: Implement scene base class
2. **Optimize sprite rendering** - Priority: Low
   - Some overdraw in complex scenes
   - Plan: Implement sprite batching
3. **Improve save system** - Priority: Medium
   - Currently only saves progress
   - Plan: Add settings and statistics

## Directory Structure (Claude-Optimized)

```
danger-rose/
├── <purpose:config> <priority:critical> <update-freq:monthly>
│   ├── pyproject.toml <purpose:poetry-config>
│   ├── PROJECT_PLAN.md <owner:marcus> <update-freq:weekly>
│   └── Makefile <purpose:automation>
│
├── <purpose:source> <priority:critical> <update-freq:daily>
│   └── src/
│       ├── main.py <purpose:entry-point>
│       ├── scene_manager.py <purpose:scene-control>
│       └── scenes/ <purpose:game-scenes> <owner:viktor>
│
├── <purpose:assets> <priority:high> <update-freq:weekly>
│   └── assets/
│       ├── sprites/ <purpose:visuals>
│       └── audio/ <purpose:sounds>
│
├── <purpose:tests> <priority:high> <update-freq:daily>
│   └── tests/
│       ├── test_*.py <purpose:unit-tests> <owner:jordan>
│       └── conftest.py <purpose:test-config>
│
├── <purpose:tools> <priority:medium> <update-freq:monthly>
│   └── tools/
│       ├── check_assets.py <purpose:validation>
│       └── generate_*.py <purpose:asset-generation>
│
├── <purpose:scripts> <priority:medium> <update-freq:weekly>
│   └── scripts/
│       └── download_audio.py <purpose:asset-download>
│
├── <purpose:change-tracking> <priority:high> <update-freq:daily>
│   └── TICKETS/
│       └── ROSE-*.yaml <owner:all>
│
├── <purpose:health-monitoring> <priority:critical> <update-freq:daily>
│   └── HEALTH_LOGS/
│       ├── health_status.yaml <owner:steward-ai>
│       └── health_history.json
│
└── <purpose:documentation> <priority:high> <update-freq:weekly>
    ├── README.md <purpose:overview>
    ├── CLAUDE.md <purpose:ai-context>
    ├── GAME_DESIGN.md <owner:sofia>
    └── PRD.md <purpose:requirements>
```

## Project Health Monitoring

### Current Health Status
[See HEALTH_LOGS/health_status.yaml for real-time status]

### Health Monitoring Schedule
- **Daily**: Automated test runs, security scans, build verification
- **Weekly**: Full health assessment, trend analysis
- **Monthly**: Comprehensive review with all designated agents

### Health Metrics Tracked
1. **Code Health** (Target: >85)
   - Test coverage
   - Code quality metrics
   - Documentation currency
   - Technical debt ratio

2. **Development Velocity** (Target: >80)
   - Feature delivery rate
   - Bug resolution time
   - Sprint completion
   - Commit frequency

3. **Stability** (Target: >90)
   - Test pass rate
   - Build success rate
   - Performance benchmarks
   - Critical bug count

4. **Team Health** (Target: >85)
   - Review turnaround time
   - Agent engagement
   - Process adherence
   - Knowledge sharing

### Health Alert Thresholds
- **Healthy**: Overall score >85
- **Warning**: Score 70-85 (address issues)
- **Critical**: Score 50-70 (immediate action)
- **Emergency**: Score <50 (all-hands response)

### Health Check Commands
```bash
# Run health assessment
/pipeline-health [project-name]

# View health history
python -m steward_ai.health_monitor --project=[project-name] --history

# Generate health report
/health-report [project-name] --format=detailed
```

---

## IMPORTANT: Logging Procedures

**Every modification to this project MUST**:

1. **Create a change ticket** in the TICKETS/ directory following the format above
2. **Update this PROJECT_PLAN.md** with:
   - Last Updated timestamp
   - Link to the new ticket in Recent Changes
   - Update relevant sections affected by the change
3. **Have the appropriate agent reviewer** sign off based on change type:
   - Content changes → Zara Okafor
   - Narrative changes → Sofia Blackwood
   - Gameplay changes → Viktor Petrov
   - Technical changes → Jordan Kim
   - Performance changes → Alex Rodriguez
4. **Run the project-specific test suite** and document results:
   ```bash
   pytest tests/ -v
   python src/main.py --test-mode
   make test
   ```
5. **Update the Completed Items section** when features are done
6. **Log health status** after significant changes

**Reminder**: This is a living document. Keep it current with every change.

---

*Plan Version: 1.1.0*  
*Plan Created: 2025-08-01*  
*Last Updated: 2025-08-01 - Added directory structure and health monitoring*