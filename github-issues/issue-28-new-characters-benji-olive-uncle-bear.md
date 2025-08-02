# Issue #28: Add Three New Playable Characters - Benji, Olive, and Uncle Bear

## 🎯 Overview
Add three new playable characters to expand the character roster from 3 to 6 characters, each with unique special abilities and complete sprite animations.

## 👥 New Characters

### 1. **Benji** (Boy, Age 8-10)
**Personality**: Energetic, tech-savvy, curious
**Visual Style**: Blonde hair, blue hoodie, sneakers, carries a small tablet/device
**Special Power**: **"Tech Boost"**
- Pool Game: Homing water balloons that auto-target nearest target
- Ski Game: Digital trail that shows optimal path for 3 seconds
- Vegas Game: Shield that absorbs one hit every 10 seconds
- Drive Game: GPS assist showing upcoming hazards with warning icons

### 2. **Olive** (Girl, Age 7-9) 
**Personality**: Creative, artistic, nature-loving
**Visual Style**: Curly brown hair, green overalls, paint-stained hands, flower crown
**Special Power**: **"Nature's Blessing"**
- Pool Game: Triple-shot water balloons in a spread pattern
- Ski Game: Leaves behind flower trail that gives speed boost to other players
- Vegas Game: Summons vine barriers that block enemy attacks
- Drive Game: Attracts bonus items (score multipliers appear more frequently)

### 3. **Uncle Bear** (Man, Age 35-40)
**Personality**: Gentle giant, protective, loves cooking
**Visual Style**: Large build, flannel shirt, suspenders, chef's hat, warm smile
**Special Power**: **"Bear Strength"**
- Pool Game: Power shots that create splash damage affecting nearby targets
- Ski Game: Can smash through obstacles instead of avoiding them
- Vegas Game: Ground pound attack that stuns all nearby enemies
- Drive Game: Heavier vehicle with increased collision resistance

## 🎨 Art Requirements

### Animation Specifications
Following the existing pattern in `assets/images/characters/new_sprites/{character}/`:

#### Required Animations (per scene: hub, pool, ski, vegas)
- **idle**: 4 frames @ 8fps (looping)
- **walk**: 5 frames @ 12fps (looping) 
- **walk_extra**: 9 frames @ 12fps (additional walk cycle)
- **jump**: 3 frames @ 6fps (non-looping)
- **victory**: 4 frames @ 8fps (non-looping)
- **hurt**: 2 frames @ 4fps (non-looping)
- **action**: 6 frames @ 10fps (special ability animation)

#### Art Style Guidelines
- **Consistent Style**: Match existing Kenney.nl cartoon aesthetic
- **Color Palette**: Harmonious with existing characters
- **Size**: Individual PNGs, same dimensions as existing characters
- **Transparency**: PNG with proper alpha channel
- **Scene Variations**: Appropriate costumes/gear for each minigame

### Asset Generation Strategy
1. **Use DALL-E 3**: Generate character sprites in Kenney.nl style
2. **Prompts**: "Top-down 2D cartoon character sprite in Kenney.nl style, [character description], transparent background, pixel-art friendly"
3. **Manual Editing**: Use image editor to create animation frames
4. **Consistency Check**: Ensure visual coherence with existing cast

## 🛠️ Technical Implementation

### Phase 1: Character Selection UI Enhancement

#### Files to Modify:
- **src/scenes/title_screen.py**
  - Expand character grid from 3 to 6 characters
  - Implement responsive layout (2 rows x 3 columns or scrolling)
  - Add character name display and ability preview
  - Handle selection states for all 6 characters

#### New Layout Design:
```
[Danger] [Rose] [Dad]
[Benji] [Olive] [Uncle Bear]
```

#### Code Structure:
```python
# Enhanced CharacterButton class
class CharacterButton:
    def __init__(self, x, y, character_name, special_ability_name):
        self.special_ability_name = special_ability_name
        # ... existing code
    
    def draw_ability_preview(self, screen):
        # Show ability name and brief description
        pass

# Updated TitleScreen
class TitleScreen:
    def __init__(self):
        self.characters = [
            {"name": "Danger", "ability": "Speed Burst"},
            {"name": "Rose", "ability": "Precision"},
            {"name": "Dad", "ability": "Experience"},
            {"name": "Benji", "ability": "Tech Boost"},
            {"name": "Olive", "ability": "Nature's Blessing"},
            {"name": "Uncle Bear", "ability": "Bear Strength"}
        ]
```

### Phase 2: Animation System Integration

#### Files to Modify:
- **src/utils/attack_character.py** (verify compatibility)
- **src/utils/sprite_loader.py** (ensure auto-detection works)

#### Asset Structure:
```
assets/images/characters/new_sprites/
├── benji/
│   ├── hub/ [idle_01-04, walk_01-05, walk_extra_01-09, jump_01-03, victory_01-04, hurt_01-02, action_01-06, animation_metadata.json]
│   ├── pool/ [same animations]
│   ├── ski/ [same animations]
│   └── vegas/ [same animations]
├── olive/ [same structure]
└── uncle_bear/ [same structure]
```

#### Metadata Template:
```json
{
  "character": "benji",
  "art_style": "kenney_cartoon",
  "special_ability": "tech_boost",
  "animations": {
    "idle": {"frames": 4, "frame_rate": 8, "loop": true},
    "walk": {"frames": 5, "frame_rate": 12, "loop": true},
    "walk_extra": {"frames": 9, "frame_rate": 12, "loop": true},
    "action": {"frames": 6, "frame_rate": 10, "loop": false},
    "jump": {"frames": 3, "frame_rate": 6, "loop": false},
    "victory": {"frames": 4, "frame_rate": 8, "loop": false},
    "hurt": {"frames": 2, "frame_rate": 4, "loop": false}
  },
  "source": "dall_e_generated",
  "license": "custom",
  "extracted_date": "2025-08-02"
}
```

### Phase 3: Special Abilities System

#### New Files to Create:
- **src/entities/character_abilities.py**: Central ability system
- **src/managers/ability_manager.py**: Manages ability activation and cooldowns

#### Core Ability System:
```python
from abc import ABC, abstractmethod
from enum import Enum

class AbilityType(Enum):
    TECH_BOOST = "tech_boost"
    NATURE_BLESSING = "nature_blessing"
    BEAR_STRENGTH = "bear_strength"
    SPEED_BURST = "speed_burst"  # Danger's existing ability
    PRECISION = "precision"       # Rose's existing ability
    EXPERIENCE = "experience"     # Dad's existing ability

class CharacterAbility(ABC):
    def __init__(self, character_name: str, cooldown: float):
        self.character_name = character_name
        self.cooldown = cooldown
        self.last_used = 0
        self.is_active = False
    
    @abstractmethod
    def activate(self, scene_context: dict) -> dict:
        """Activate ability and return effects"""
        pass
    
    @abstractmethod
    def deactivate(self) -> None:
        """Clean up ability effects"""
        pass
    
    def can_use(self) -> bool:
        return time.time() - self.last_used >= self.cooldown

class TechBoostAbility(CharacterAbility):
    def activate(self, scene_context):
        if scene_context["scene"] == "pool":
            # Enable homing balloons
            return {"homing_enabled": True, "duration": 8.0}
        elif scene_context["scene"] == "drive":
            # Show hazard warnings
            return {"hazard_preview": True, "duration": 5.0}
        # ... other scenes
```

#### Integration Points:
- **Pool Game**: Modify projectile system to support homing, splash damage, triple-shot
- **Ski Game**: Add trail effects, obstacle destruction, path visualization
- **Vegas Game**: Add shield system, vine barriers, ground pound attacks
- **Drive Game**: Add GPS warnings, item magnets, collision resistance

### Phase 4: Scene Integration

#### Files to Modify Per Scene:

**Pool Game** (`src/scenes/pool.py`):
```python
def update_character_abilities(self):
    if self.selected_character == "Benji" and self.tech_boost_active:
        # Make balloons home toward targets
        for balloon in self.balloons:
            if hasattr(balloon, 'target_seeking'):
                balloon.seek_target(self.targets)
    
    elif self.selected_character == "Olive":
        # Triple shot logic
        pass
    
    elif self.selected_character == "Uncle Bear":
        # Splash damage calculation
        pass
```

**Ski Game** (`src/scenes/ski.py`):
```python
def handle_character_abilities(self):
    if self.selected_character == "Benji":
        # Show optimal path overlay
        self.draw_optimal_path()
    elif self.selected_character == "Uncle Bear":
        # Allow obstacle smashing
        self.enable_obstacle_destruction()
```

## 🧪 Testing Strategy

### Visual Testing
- [ ] All 6 characters appear correctly in selection screen
- [ ] Animations play smoothly for all characters in all scenes
- [ ] Character sprites are visually consistent
- [ ] Special ability animations are distinct and clear

### Functional Testing
- [ ] Character selection saves and persists across scenes
- [ ] Each special ability activates correctly in each minigame
- [ ] Abilities have appropriate cooldowns and visual feedback
- [ ] No ability provides unfair advantage (balance testing)

### Integration Testing
- [ ] New characters work in all existing minigames
- [ ] Save/load system handles new character data
- [ ] Scene transitions work with new characters
- [ ] Hub world interactions work for all characters

## 📋 Implementation Tasks

### **Sprint 1: Art Assets** (Week 1-2)
- [ ] Create character concept art and color palettes
- [ ] Generate base character sprites using DALL-E 3
- [ ] Create idle animation frames for all 3 characters
- [ ] Create walk animation frames for all 3 characters
- [ ] Test animation loading system with new characters

### **Sprint 2: Character Selection** (Week 3)
- [ ] Redesign title screen layout for 6 characters
- [ ] Implement character grid system
- [ ] Add ability name display
- [ ] Update character selection logic
- [ ] Test character selection and scene transitions

### **Sprint 3: Animation System** (Week 4)
- [ ] Complete all animation sets (jump, victory, hurt, action)
- [ ] Create animation metadata files
- [ ] Implement scene-specific costume variations
- [ ] Test animation playback in all scenes

### **Sprint 4: Special Abilities Core** (Week 5-6)
- [ ] Design and implement ability system architecture
- [ ] Create base ability classes
- [ ] Implement cooldown and activation systems
- [ ] Add visual feedback for ability states

### **Sprint 5: Scene Integration** (Week 7-8)
- [ ] Integrate abilities into Pool minigame
- [ ] Integrate abilities into Ski minigame  
- [ ] Integrate abilities into Vegas minigame
- [ ] Integrate abilities into Drive minigame

### **Sprint 6: Polish & Balance** (Week 9-10)
- [ ] Balance testing for all abilities
- [ ] UI/UX improvements for ability feedback
- [ ] Performance optimization
- [ ] Comprehensive testing and bug fixes

## 🎯 Acceptance Criteria

### Character Selection
- [ ] All 6 characters (Danger, Rose, Dad, Benji, Olive, Uncle Bear) are selectable
- [ ] Character selection screen displays ability names
- [ ] Selected character persists across all game scenes
- [ ] Character animations play correctly in selection screen

### Animation Quality
- [ ] All characters have complete animation sets for all 4 scenes
- [ ] Animations are smooth and visually consistent
- [ ] Frame rates match existing character animations
- [ ] No visual glitches or missing frames

### Special Abilities
- [ ] Each new character has unique ability in each minigame
- [ ] Abilities have clear visual and mechanical effects
- [ ] Abilities are balanced (no character is overpowered)
- [ ] Cooldown systems work correctly

### Integration
- [ ] New characters work seamlessly in all existing scenes
- [ ] Performance impact is minimal
- [ ] Save system handles new character data
- [ ] All existing functionality remains intact

## 🎨 Art Style Reference

**Existing Characters Style Points:**
- Simple, cartoon-like design (Kenney.nl aesthetic)
- Clear silhouettes and readable at small sizes
- Bright, friendly color palettes
- Consistent proportions across all characters
- Family-appropriate designs

**New Character Distinctions:**
- **Benji**: Modern tech elements, younger energy
- **Olive**: Natural/organic elements, artistic flair
- **Uncle Bear**: Larger build, warm/cozy elements

## 🔧 Technical Considerations

### Performance
- Monitor sprite loading times with 6 characters
- Ensure animation memory usage stays reasonable
- Optimize special effects for low-end devices

### Extensibility
- Design ability system to easily add more characters
- Create reusable animation validation tools
- Plan for future character DLC/expansions

### Accessibility
- Ensure character abilities don't disadvantage players
- Provide visual indicators for all ability states
- Consider colorblind-friendly ability indicators

## 📈 Success Metrics

### Player Engagement
- Track character selection distribution
- Monitor completion rates by character
- Measure ability usage frequency

### Technical Performance
- Loading time impact < 10%
- Memory usage increase < 20%
- Frame rate maintains 60fps

### Quality Assurance
- Zero crashes related to new characters
- All animations load correctly 100% of time
- Character abilities work as designed in all scenarios

---

## 🏗️ Implementation Priority

**High Priority**: Character selection and basic animations
**Medium Priority**: Special abilities implementation
**Low Priority**: Advanced visual effects and polish

This feature will significantly expand gameplay variety and give players more reasons to replay minigames with different characters!