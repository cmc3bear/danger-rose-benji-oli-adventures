# Traffic Spawning Clarification - Issue #31

## Important Note: Top of Road = Horizon Line

### Current Understanding (To Be Updated)
The current implementation assumes:
- "Top of road" = Further ahead on the road (positive Y values)
- "Bottom of road" = Behind the player (negative Y values)

### Correct Understanding
Per user clarification:
- **"Top of road" = Horizon line** (where road meets sky)
- **"Bottom of road" = Bottom of screen** (closest to player)

### Required Changes (DO NOT IMPLEMENT YET)
1. **Slower traffic (< 100% speed)**:
   - Should spawn at the horizon line
   - Will appear far in the distance
   - Player will gradually catch up to them

2. **Faster traffic (> 100% speed)**:
   - Should spawn at bottom of screen (behind player POV)
   - Will catch up to and pass the player

3. **Oncoming traffic**:
   - Always spawns at horizon (top)
   - Approaches player from the distance

### Visual Reference
```
Screen Layout:
┌─────────────────────────┐
│ SKY                     │
│ ═══════ HORIZON ═══════ │ ← Top of road (spawn slow cars here)
│         Road            │
│        /    \           │
│       /      \          │
│      /        \         │
│     /          \        │
│    /            \       │
│   / Player Car  \      │
│  /              \      │
│ /                \     │
└─────────────────────────┘ ← Bottom of screen (spawn fast cars here)
```

### Implementation Notes
- Horizon Y coordinate is typically around `screen_height / 2`
- Bottom of screen is `screen_height`
- Adjust spawn positions accordingly when implementing

### Related Code Sections
- `_spawn_npc_car()` method in `src/scenes/drive.py`
- Y position calculations for traffic spawning
- Perspective calculations for road rendering

---

**Status**: Documented for future implementation
**Priority**: Low (cosmetic/realism improvement)
**Impact**: Visual realism of traffic flow