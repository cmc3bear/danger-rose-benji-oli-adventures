# Issue #13: Static Hazards (Cones & Barriers)

## GitHub Issue Details
**Title**: Add static hazards and construction zones to highway  
**Status**: IN PROGRESS 🚧  
**Labels**: enhancement, phase-3.2, hazard-system  
**Milestone**: Phase 3.2 - Hazard System  

## Current State (From)
- Highway contains only traffic vehicles as obstacles
- No static hazards or construction zones
- Limited variety in obstacles to avoid
- No environmental hazards on the road

## Desired State (To)
- Traffic cones appearing in construction zones
- Concrete barriers for lane closures
- Static hazards spawn in patterns (construction areas)
- Visual warning signs before hazard zones
- Collision detection for static hazards
- Different penalty levels for different hazards

## Implementation Details

### Hazard Types
1. **Traffic Cones**
   - Size: 16x24 pixels
   - Color: Orange (255, 140, 0)
   - Collision penalty: 10% speed reduction
   - Behavior: Disappears when hit

2. **Concrete Barriers**
   - Size: 48x32 pixels
   - Color: Gray (128, 128, 128) with yellow stripes
   - Collision penalty: 30% speed reduction + damage
   - Behavior: Remains after collision

3. **Warning Signs**
   - Size: 32x32 pixels
   - Color: Yellow diamond shape
   - No collision (visual warning only)
   - Appears 100px before construction zones

### Construction Zone System
- Zones spawn every 8 seconds
- Zone length: 200-400 pixels
- Can block 1-2 adjacent lanes
- Cones placed every 40 pixels
- Barriers added for zones > 300px

### Technical Implementation
- Created `Hazard` dataclass
- Added `_update_hazards()` method
- Implemented `_spawn_construction_zone()` system
- Added collision detection in `_check_hazard_collisions()`
- Visual rendering in `_draw_hazards()`

## Progress
✅ Hazard dataclass created
✅ Hazard spawning system implemented
✅ Construction zone generation working
✅ Collision detection functional
✅ Visual rendering complete
✅ Different penalties for different hazard types

## Testing Status
- Visual inspection: Hazards spawn correctly
- Collision detection: Working for all types
- Performance impact: Minimal (<5% FPS)
- Construction zones: Proper lane blocking

**Status**: Implementation complete, pending final testing