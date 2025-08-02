# EV Car Selection Implementation Plan for The Drive Minigame

## 🎯 Project Overview

This document outlines the comprehensive implementation plan for adding EV (Electric Vehicle) car selection to The Drive racing minigame in Danger Rose. Players will be able to choose between two distinct car styles before racing, enhancing personalization and gameplay variety.

## 🚗 Available Car Options

1. **Professional EV** (`ev_professional.png`)
   - Clean, modern electric vehicle design
   - 8-bit pixel art style with smooth lines
   - Electric blue color scheme with cyan accents
   - Appeals to players who prefer sleek aesthetics

2. **Kid's Drawing EV** (`ev_kids_drawing.png`)
   - Charming crayon-style artwork
   - Deliberately imperfect with hand-drawn feel
   - Features smiley face, lightning bolts, and doodles
   - Perfect for younger players or those who enjoy whimsy

## 📋 Implementation Phases

### Phase 1: Core Infrastructure (Priority: Critical)
**Milestone 1.1: Asset Integration**
- [ ] Create vehicle sprite loader in `src/utils/sprite_loader.py`
- [ ] Add `get_vehicle_sprite_path()` function to asset paths
- [ ] Implement sprite caching for performance
- [ ] Test sprite loading with both EV variants

**Milestone 1.2: Data Structure Updates**
- [ ] Add `selected_vehicle` field to game data
- [ ] Update save/load system to persist vehicle choice
- [ ] Create vehicle configuration constants
- [ ] Define vehicle properties (speed, handling, etc.)

### Phase 2: Vehicle Selection System (Priority: High)
**Milestone 2.1: Selection UI Creation**
- [ ] Create `VehicleSelector` class similar to `MusicSelector`
- [ ] Design selection screen with preview cards
- [ ] Implement keyboard/mouse navigation
- [ ] Add vehicle preview animations

**Milestone 2.2: Integration Points**
- [ ] Add vehicle selection after music selection
- [ ] Create smooth transition between selections
- [ ] Implement "back" functionality to change choices
- [ ] Add vehicle confirmation sound effects

### Phase 3: Gameplay Integration (Priority: High)
**Milestone 3.1: Replace Placeholder Graphics**
- [ ] Remove rectangle drawing from `drive.py`
- [ ] Implement sprite-based car rendering
- [ ] Add proper scaling (128x192 → 64x96)
- [ ] Center sprite on player position

**Milestone 3.2: Vehicle-Specific Features**
- [ ] Implement unique handling for each vehicle
- [ ] Add vehicle-specific sound effects
- [ ] Create distinct particle effects
- [ ] Implement special abilities (optional)

### Phase 4: Visual Polish (Priority: Medium)
**Milestone 4.1: Animation System**
- [ ] Add turning animations (lean left/right)
- [ ] Implement boost/turbo effects
- [ ] Create crash/spin animations
- [ ] Add victory celebration animations

**Milestone 4.2: Environmental Integration**
- [ ] Add car shadows for depth
- [ ] Implement tire tracks
- [ ] Create dust/exhaust particles
- [ ] Add reflection effects on road

### Phase 5: Audio Enhancement (Priority: Medium)
**Milestone 5.1: Vehicle Sounds**
- [ ] Professional EV: Quiet hum, electronic sounds
- [ ] Kid's Drawing: Playful "vroom" sounds
- [ ] Unique horn sounds for each vehicle
- [ ] Collision sounds matching vehicle style

**Milestone 5.2: Dynamic Audio**
- [ ] Speed-based engine pitch
- [ ] Tire screech for sharp turns
- [ ] Ambient road noise
- [ ] Victory fanfare variations

### Phase 6: Testing & Balance (Priority: Critical)
**Milestone 6.1: Functionality Testing**
- [ ] Test vehicle selection persistence
- [ ] Verify sprite rendering at all positions
- [ ] Test performance with animated sprites
- [ ] Ensure save/load works correctly

**Milestone 6.2: Gameplay Balance**
- [ ] Balance vehicle stats if different
- [ ] Test with all music tracks
- [ ] Verify child-friendly difficulty
- [ ] Gather family playtesting feedback

## 🔧 Technical Implementation Details

### Vehicle Selection Flow
```
Title Screen → Character Select → Hub World → Drive Door → Music Selection → Vehicle Selection → Race
                                                                              ↑
                                                                    [New Addition]
```

### Code Structure

#### 1. Vehicle Selector Component
```python
# src/ui/vehicle_selector.py
class VehicleSelector:
    def __init__(self, screen_width, screen_height, sound_manager):
        self.vehicles = [
            Vehicle("professional", "Professional EV", "ev_professional.png"),
            Vehicle("kids_drawing", "Kid's Drawing", "ev_kids_drawing.png")
        ]
        self.selected_index = 0
```

#### 2. Drive Scene Updates
```python
# src/scenes/drive.py
class DriveGame:
    def __init__(self, scene_manager):
        # Add after music selector
        self.vehicle_selector = VehicleSelector(...)
        self.selected_vehicle = None
        self.car_sprite = None
```

#### 3. Sprite Rendering
```python
def _draw_player_car(self, screen):
    if self.car_sprite:
        # Scale and position sprite
        scaled_sprite = pygame.transform.scale(
            self.car_sprite, 
            (self.car_width, self.car_height)
        )
        car_rect = scaled_sprite.get_rect(center=(self.player_x, self.player_y))
        screen.blit(scaled_sprite, car_rect)
```

### Data Persistence
```json
{
  "selected_character": "Danger",
  "selected_vehicle": "professional",  // New field
  "high_scores": {...}
}
```

## 📊 Development Timeline

### Week 1: Foundation
- Days 1-2: Asset integration and data structures
- Days 3-4: Vehicle selector UI
- Day 5: Basic integration testing

### Week 2: Core Implementation
- Days 1-2: Replace placeholder graphics
- Days 3-4: Vehicle-specific features
- Day 5: Polish and bug fixes

### Week 3: Enhancement
- Days 1-2: Animation system
- Days 3-4: Audio implementation
- Day 5: Final testing and balance

## 🎮 User Experience Flow

1. **Enter The Drive**: Player selects The Drive from hub world
2. **Music Selection**: Choose from 3 racing tracks (existing)
3. **Vehicle Selection**: NEW - Choose between Professional or Kid's Drawing EV
4. **Preview Mode**: See selected vehicle with stats/description
5. **Confirm & Race**: Start racing with chosen vehicle

## 🚨 Priority Considerations

### Must Have (P0)
- Vehicle selection screen
- Basic sprite rendering
- Save/load vehicle choice
- Both vehicles playable

### Should Have (P1)
- Unique sounds per vehicle
- Turning animations
- Selection preview

### Nice to Have (P2)
- Particle effects
- Vehicle-specific abilities
- Advanced animations
- Multiple color variants

## 🧪 Testing Checklist

### Functional Tests
- [ ] Vehicle selection works with keyboard
- [ ] Vehicle selection works with mouse
- [ ] Selected vehicle appears in race
- [ ] Vehicle choice persists between sessions
- [ ] Can change vehicle selection
- [ ] Both vehicles render correctly

### Performance Tests
- [ ] No FPS drop with sprites
- [ ] Smooth sprite scaling
- [ ] Quick load times
- [ ] Memory usage acceptable

### User Experience Tests
- [ ] Selection is intuitive
- [ ] Vehicles are visually distinct
- [ ] Fun for target age group
- [ ] Accessibility compliant

## 📝 Success Criteria

1. Players can choose between two EV designs
2. Selected vehicle appears correctly in gameplay
3. Choice persists across game sessions
4. Performance remains smooth (60 FPS)
5. Implementation follows Danger Rose code standards
6. Feature is fun and accessible for families

## 🔄 Future Expansions

- Additional vehicle unlocks
- Vehicle customization (colors, decals)
- Vehicle-specific race tracks
- Multiplayer vehicle selection
- Achievement system for vehicles

---

**Document Version**: 1.0  
**Last Updated**: August 2, 2025  
**Priority Level**: HIGH - Next Major Feature  
**Estimated Hours**: 40-60 hours