# 🚀 Danger Rose Development Continuation Prompt

## Quick Context Setup

I'm continuing work on the Danger Rose game project. Here's the current state:

### Project Location & Version
- **Working Directory**: `C:\dev\danger-rose`
- **Current Version**: v0.1.3-alpha (just released)
- **Repository**: https://github.com/cmc3bear/danger-rose-benji-oli-adventures
- **Main Feature Just Completed**: Highway Drive minigame with Pole Position style curves

### Recent Work Completed (v0.1.3)
1. **Highway Drive Enhancement**:
   - Implemented authentic Pole Position style road curves
   - Added 11 AI-generated traffic sprites via DALL-E
   - Created dynamic hazard system (oil slicks with 360° spin, debris)
   - Added comic-style taunt system
   - Fixed traffic/hazard alignment with centralized curve calculations
   - Secured all API keys in vault system outside repository

2. **Repository Updates**:
   - Updated README with v0.1.3 features
   - Created comprehensive release notes
   - Cleaned git history of API keys
   - Fixed all GitHub repository references

### Current Issue Status

**✅ Completed Issues**:
- Issues #10-17: All Drive enhancement features
- Issue #25: Road curve alignment fix (documented)
- Issue #26: Missing EV sprites fix (documented)

**📋 Ready for Development**:
- **Issue #28**: Add 3 new characters (Benji, Olive, Uncle Bear)
- **Issue #29**: Character abilities system
- **Issue #30**: Abilities scene integration
- **Issue #18**: BPM-synchronized traffic
- **Issue #19**: Dynamic sky system with DALL-E
- **Issue #27**: Typing Tutor minigame

### Key Technical Details

**API Key Management**:
- Keys stored in: `C:\dev\api-key-forge\vault\{OPENAI|GITHUB|SUNO}`
- Access via: `scripts/vault_utils.py`
- Never hardcode keys in repository

**Character System**:
- Current: 3 characters (Danger, Rose, Dad)
- Planned: 6 characters total (adding Benji, Olive, Uncle Bear)
- Animation structure: `assets/images/characters/new_sprites/{character}/{scene}/{animation}_{frame}.png`
- Each character needs: idle, walk, jump, victory, hurt, action animations

**Scene Registration**:
- Drive minigame is now properly integrated
- Access from hub world via purple door
- Scene constant: `SCENE_DRIVE_GAME = "drive_game"`

### Next Priority Tasks

1. **Start Character Expansion (Issue #28)**:
   - Create character sprites using DALL-E
   - Expand selection screen from 3 to 6 characters
   - Implement character-specific abilities

2. **Research BPM Detection (Issue #18)**:
   - Investigate music analysis libraries
   - Plan traffic synchronization approach
   - Create testing overlay

3. **Continue Following Master Plan**:
   - See `DEVELOPMENT_MASTER_PLAN.md` for full roadmap
   - Check `github-issues/` for detailed specifications

### Important Files to Reference
- `DEVELOPMENT_MASTER_PLAN.md` - Overall project roadmap
- `github-issues/issue-28-new-characters-benji-olive-uncle-bear.md` - Character specs
- `github-issues/issue-29-character-abilities-system.md` - Ability system design
- `github-issues/issue-30-character-abilities-scene-integration.md` - Integration plan
- `src/scenes/drive.py` - Latest minigame implementation example
- `scripts/vault_utils.py` - API key management

### Current Working State
- All tests passing
- Game runs smoothly at 60 FPS
- v0.1.3-alpha is live on GitHub
- Repository is clean (no API keys in history)
- Ready to begin next feature development

### Commands to Get Started
```bash
# Run the game
make run

# Run in debug mode
make debug

# Run tests
make test

# Start specific scene (for testing)
set DANGER_ROSE_START_SCENE=drive_game
make run
```

Please continue with the character expansion feature (Issue #28) or help with any other priority items from the master plan.