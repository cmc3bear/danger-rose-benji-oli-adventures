# Issue #29: Implement Special Abilities System for All Characters

## 🎯 Overview
Create a unified special abilities system that supports unique character powers across all minigames. This is part of the new character expansion (Issue #28) but separated for focused development.

## 📋 Prerequisites
- Issue #28 Sprints 1-4 completed (characters created, animations done, selection UI updated)
- All 6 characters (Danger, Rose, Dad, Benji, Olive, Uncle Bear) are selectable
- Base animations are working in all scenes

## 🛠️ Core System Architecture

### New Files to Create

#### 1. **src/entities/character_abilities.py**
```python
from abc import ABC, abstractmethod
from enum import Enum
import time

class AbilityType(Enum):
    # New character abilities
    TECH_BOOST = "tech_boost"
    NATURE_BLESSING = "nature_blessing"
    BEAR_STRENGTH = "bear_strength"
    # Existing character abilities (to be defined)
    SPEED_BURST = "speed_burst"
    PRECISION = "precision"
    EXPERIENCE = "experience"

class CharacterAbility(ABC):
    """Base class for all character special abilities"""
    def __init__(self, character_name: str, cooldown: float = 10.0):
        self.character_name = character_name
        self.cooldown = cooldown
        self.last_used = 0
        self.is_active = False
        self.duration = 5.0  # Default ability duration
        self.activation_time = 0
    
    @abstractmethod
    def activate(self, scene_context: dict) -> dict:
        """Activate ability and return effects"""
        pass
    
    @abstractmethod
    def update(self, dt: float, scene_context: dict) -> dict:
        """Update ability state each frame"""
        pass
    
    @abstractmethod
    def deactivate(self) -> None:
        """Clean up ability effects"""
        pass
    
    def can_use(self) -> bool:
        """Check if ability is off cooldown"""
        return time.time() - self.last_used >= self.cooldown
    
    def is_expired(self) -> bool:
        """Check if ability duration has expired"""
        if self.is_active:
            return time.time() - self.activation_time >= self.duration
        return False
```

#### 2. **src/managers/ability_manager.py**
```python
class AbilityManager:
    """Manages all character abilities across scenes"""
    def __init__(self):
        self.abilities = {}
        self._register_abilities()
        self.active_ability = None
    
    def _register_abilities(self):
        """Register all character abilities"""
        self.abilities = {
            "Danger": SpeedBurstAbility(),
            "Rose": PrecisionAbility(),
            "Dad": ExperienceAbility(),
            "Benji": TechBoostAbility(),
            "Olive": NatureBlessingAbility(),
            "Uncle Bear": BearStrengthAbility()
        }
    
    def activate_ability(self, character_name: str, scene_context: dict) -> dict:
        """Activate character's special ability"""
        if character_name in self.abilities:
            ability = self.abilities[character_name]
            if ability.can_use():
                self.active_ability = ability
                return ability.activate(scene_context)
        return {}
    
    def update(self, dt: float, scene_context: dict) -> dict:
        """Update active ability"""
        if self.active_ability and self.active_ability.is_active:
            if self.active_ability.is_expired():
                self.active_ability.deactivate()
                self.active_ability = None
                return {"ability_expired": True}
            return self.active_ability.update(dt, scene_context)
        return {}
```

### Ability Implementations

#### **Tech Boost (Benji)**
```python
class TechBoostAbility(CharacterAbility):
    def __init__(self):
        super().__init__("Benji", cooldown=12.0)
        self.duration = 8.0
    
    def activate(self, scene_context):
        self.is_active = True
        self.activation_time = time.time()
        self.last_used = time.time()
        
        scene = scene_context.get("scene")
        if scene == "pool":
            return {
                "effect": "homing_balloons",
                "homing_strength": 0.8,
                "visual": "digital_trail"
            }
        elif scene == "ski":
            return {
                "effect": "optimal_path",
                "path_duration": 3.0,
                "visual": "holographic_line"
            }
        elif scene == "vegas":
            return {
                "effect": "shield",
                "shield_health": 1,
                "recharge_time": 10.0,
                "visual": "tech_bubble"
            }
        elif scene == "drive":
            return {
                "effect": "hazard_preview",
                "preview_distance": 300,
                "visual": "warning_icons"
            }
```

#### **Nature's Blessing (Olive)**
```python
class NatureBlessingAbility(CharacterAbility):
    def __init__(self):
        super().__init__("Olive", cooldown=10.0)
        self.duration = 6.0
    
    def activate(self, scene_context):
        # Implementation for nature-based abilities
        # Pool: Triple shot
        # Ski: Flower trail speed boost
        # Vegas: Vine barriers
        # Drive: Item magnetism
```

#### **Bear Strength (Uncle Bear)**
```python
class BearStrengthAbility(CharacterAbility):
    def __init__(self):
        super().__init__("Uncle Bear", cooldown=15.0)
        self.duration = 5.0
    
    def activate(self, scene_context):
        # Implementation for strength-based abilities
        # Pool: Splash damage
        # Ski: Obstacle destruction
        # Vegas: Ground pound
        # Drive: Collision resistance
```

### Existing Character Abilities (To Define)

#### **Speed Burst (Danger)**
- Pool: Rapid fire mode
- Ski: Temporary speed boost
- Vegas: Dash attack
- Drive: Nitro boost

#### **Precision (Rose)**
- Pool: Slow-motion aiming
- Ski: Perfect line bonus
- Vegas: Critical hit chance
- Drive: Tighter steering

#### **Experience (Dad)**
- Pool: Bonus points multiplier
- Ski: Obstacle warnings
- Vegas: Enemy weakness display
- Drive: Experience gauge (fills faster)

## 🎮 UI/UX Requirements

### Ability HUD Elements
```python
class AbilityHUD:
    """Display ability status and cooldown"""
    def __init__(self, ability_manager):
        self.ability_manager = ability_manager
        self.font = pygame.font.Font(None, 24)
        self.ability_icon_size = 64
        self.position = (20, 100)  # Below health/score
    
    def draw(self, screen, character_name):
        ability = self.ability_manager.abilities.get(character_name)
        if ability:
            # Draw ability icon
            # Draw cooldown overlay
            # Draw activation key hint
            # Draw active effect indicator
```

### Visual Feedback Requirements
- **Ability Ready**: Glowing border around ability icon
- **On Cooldown**: Grayed out with countdown timer
- **Active**: Pulsing effect and character aura
- **About to Expire**: Flashing warning (last 2 seconds)

## 🔧 Integration Points

### Scene Base Class Modification
```python
# In src/scenes/base_scene.py (if exists) or each scene
class Scene:
    def __init__(self):
        self.ability_manager = AbilityManager()
        self.ability_effects = {}
    
    def handle_ability_input(self, event):
        """Handle ability activation input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Or dedicated ability key
                effects = self.ability_manager.activate_ability(
                    self.selected_character,
                    self.get_scene_context()
                )
                self.apply_ability_effects(effects)
    
    def update_abilities(self, dt):
        """Update ability states"""
        effects = self.ability_manager.update(dt, self.get_scene_context())
        self.apply_ability_effects(effects)
```

### Save System Integration
```python
# In save data
{
    "character_stats": {
        "Benji": {
            "abilities_used": 0,
            "ability_effectiveness": 0.0,
            "favorite_scene": "pool"
        }
    }
}
```

## 🧪 Testing Requirements

### Unit Tests
- [ ] Each ability activates correctly
- [ ] Cooldown system works properly
- [ ] Duration tracking is accurate
- [ ] Effects are applied correctly per scene

### Integration Tests
- [ ] Abilities work across scene transitions
- [ ] Multiple abilities don't conflict
- [ ] Performance impact is acceptable
- [ ] Visual effects render correctly

### Balance Tests
- [ ] No ability is overpowered
- [ ] Cooldowns feel appropriate
- [ ] Durations are balanced
- [ ] All characters are viable

## 📋 Implementation Tasks

### Core System (Week 5)
- [ ] Create base ability classes
- [ ] Implement ability manager
- [ ] Create ability HUD system
- [ ] Add input handling for abilities

### Character Abilities (Week 5-6)
- [ ] Implement Benji's Tech Boost
- [ ] Implement Olive's Nature's Blessing
- [ ] Implement Uncle Bear's Bear Strength
- [ ] Define and implement Danger's Speed Burst
- [ ] Define and implement Rose's Precision
- [ ] Define and implement Dad's Experience

### Visual Effects (Week 6)
- [ ] Create ability activation effects
- [ ] Implement ability aura/trails
- [ ] Add cooldown visualization
- [ ] Create ability icons

### Testing & Balance (Week 6)
- [ ] Unit test all abilities
- [ ] Balance cooldowns and durations
- [ ] Performance optimization
- [ ] Bug fixes and polish

## 🎯 Acceptance Criteria

### Functionality
- [ ] All 6 characters have working abilities
- [ ] Abilities activate with consistent input
- [ ] Cooldown system prevents spam
- [ ] Visual feedback is clear

### Performance
- [ ] Ability system adds < 5ms frame time
- [ ] Effects don't cause frame drops
- [ ] Memory usage is reasonable

### User Experience
- [ ] Players understand how to use abilities
- [ ] Ability states are clearly communicated
- [ ] Effects enhance gameplay without distraction

## 🔗 Dependencies
- Issue #28 (New Characters) - Sprints 1-4 must be complete
- Existing power-up system can be referenced for implementation patterns

## 🎨 Visual Style Guide
- **Tech Effects**: Digital, holographic, blue/cyan colors
- **Nature Effects**: Organic, flowing, green/brown colors
- **Strength Effects**: Impact lines, screen shake, red/orange colors
- **Consistent Style**: Match existing game aesthetic

This focused implementation will create a robust ability system that can be extended for future characters!