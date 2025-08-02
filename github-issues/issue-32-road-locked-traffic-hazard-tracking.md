# Issue #32: Road-Locked Traffic and Hazard Tracking System

## Summary
Implement a system where traffic cars and hazards are properly locked to the road surface and track road curvature, creating more realistic positioning as the road turns and curves.

## Current State
- Traffic and hazards use simple x/y positioning
- Road curve offset is applied but not fully integrated
- Objects can appear to "float" off the road during curves
- Lane positions don't properly follow road geometry

## Desired State
- All traffic and hazards locked to road surface
- Objects follow road curvature naturally
- Lane positions maintained relative to road center
- Smooth tracking during turns and curves
- Proper perspective scaling with distance

## Technical Requirements

### 1. Road Geometry System
```python
class RoadGeometry:
    def get_road_position(self, y_distance: float, lane: int) -> Tuple[float, float]:
        """Get world position for a given road distance and lane"""
        # Account for:
        # - Road curvature at this distance
        # - Lane offset from center
        # - Perspective transformation
        # - Road width variations
        
    def get_road_normal(self, y_distance: float) -> float:
        """Get road surface normal/angle at distance"""
        # For proper vehicle rotation
```

### 2. Lane-Relative Positioning
```python
@dataclass
class RoadPosition:
    """Position relative to road instead of screen"""
    distance: float      # Distance along road from player
    lane: int           # Lane number (1-4)
    lane_offset: float  # Offset within lane (-0.5 to 0.5)
    
    def to_screen_pos(self, road_geometry: RoadGeometry) -> Tuple[int, int]:
        """Convert road position to screen coordinates"""
```

### 3. Update Traffic System
```python
class NPCCar:
    # Change from:
    x: float  # Screen position
    y: float  # Screen position
    
    # To:
    road_pos: RoadPosition  # Position relative to road
    screen_x: int  # Calculated screen position
    screen_y: int  # Calculated screen position
```

## Implementation Plan

### Phase 1: Road Geometry Foundation
- [ ] Create RoadGeometry class
- [ ] Implement curve calculation at any distance
- [ ] Add lane position calculations
- [ ] Test with debug visualization

### Phase 2: Convert Traffic System
- [ ] Update NPCCar to use RoadPosition
- [ ] Modify spawn system for road-relative positioning
- [ ] Update movement to follow road geometry
- [ ] Ensure smooth lane changes along curves

### Phase 3: Convert Hazard System
- [ ] Update Hazard class for road-relative positioning
- [ ] Modify hazard spawning
- [ ] Ensure hazards stick to road surface
- [ ] Test with various road configurations

### Phase 4: Visual Improvements
- [ ] Add proper perspective scaling
- [ ] Improve rotation to match road angle
- [ ] Ensure smooth transitions
- [ ] Debug and polish

## Technical Considerations

### Current Road Curve Calculation
```python
# Current simplified approach
curve_offset = self._get_curve_offset_at_y(y_position)
screen_x = int(car.x * self.screen_width) + curve_offset

# Proposed improvement
road_pos = car.road_position
screen_pos = self.road_geometry.to_screen_position(road_pos)
```

### Benefits
- More realistic traffic movement
- Easier to implement complex road shapes
- Better collision detection
- Simplified lane change logic

## Success Criteria
- [ ] Traffic stays locked to road surface during curves
- [ ] Hazards remain in proper lanes
- [ ] No floating or sliding objects
- [ ] Smooth tracking during all road conditions
- [ ] Performance remains stable

## Dependencies
- May affect Issue #31 (Traffic Passing Logic)
- Builds on existing road rendering system

## Estimated Effort
- 4-5 hours implementation
- 2 hours testing and debugging

## Notes
- Consider caching road geometry calculations
- May need to adjust spawn positions
- Could enable more complex road shapes (S-curves, elevation changes)
- Sets foundation for potential split roads or intersections