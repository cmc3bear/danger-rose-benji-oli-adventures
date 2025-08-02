# Issue #25: Traffic and Hazards Need to Follow Road Curves

## Problem
Traffic vehicles and hazards were not following the Pole Position style road curves, making them appear to float off the road when the road curved.

## Solution Implemented
1. Created centralized `_get_curve_offset_at_y()` helper method for consistent curve calculations
2. Updated both `_draw_npc_cars()` and `_draw_hazards()` methods to use this helper
3. Fixed hazard positioning to correctly handle lane-based vs free-positioned hazards

```python
def _get_curve_offset_at_y(self, y_position: float) -> int:
    """Get the horizontal curve offset in pixels for a given Y position."""
    # Ensure Y is within screen bounds
    if y_position < self.horizon_y:
        return 0
        
    # Calculate distance factor (0 at player, 1 at horizon)
    screen_factor = (y_position - self.horizon_y) / (self.screen_height - self.horizon_y)
    screen_factor = max(0, min(1, screen_factor))
    distance_factor = 1.0 - screen_factor
    
    # Apply curve intensity (stronger curves in distance)
    curve_intensity = distance_factor * distance_factor
    scanline_curve = int(self.road_curve * 300 * curve_intensity)
    
    # S-curve calculation for smooth transitions
    s_curve_factor = (distance_factor - 0.5) * 2.0
    s_curve = s_curve_factor * s_curve_factor * s_curve_factor * 50
    
    return scanline_curve + int(s_curve)
```

## Key Fixes
1. **Centralized curve calculation** - Ensures all elements use identical curve math
2. **Lane-based hazard positioning** - Hazards in lanes now correctly get lane X positions before curve offset
3. **Consistent coordinate systems** - Fixed mixing of normalized (0-1) and pixel coordinates

## Technical Details
- Uses the same curve calculation as the road rendering
- Applies perspective-based curve intensity (stronger curves in the distance)
- Includes S-curve calculation for smooth transitions
- Ensures all road elements (road lines, traffic, hazards) curve together

## Files Modified
- `src/scenes/drive.py`: 
  - Added `_get_curve_offset_at_y()` helper method
  - Updated `_draw_npc_cars()` to use helper
  - Updated `_draw_hazards()` to use helper and handle lane-based positioning

## Testing
- Verify traffic stays centered in lanes during curves
- Check hazards align with road surface
- Test with different curve intensities
- Ensure smooth visual continuity
- Verify lane-based hazards follow their lanes correctly

## Status
✅ Implemented with improvements based on testing feedback