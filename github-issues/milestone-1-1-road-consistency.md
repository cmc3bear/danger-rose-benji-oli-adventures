# Milestone 1.1: Road Consistency Issues

## Issue #1: Fix Road Width Oscillation

### Current State (From)
- Road width oscillates dramatically up to 75% of its size
- Creates unrealistic and jarring visual experience
- Width changes are too rapid and extreme
- Located in `src/scenes/drive.py` around lines 175-180

```python
# Current problematic code
curve_frequency = 0.3 + self.player_speed * 0.2
self.road_curve = math.sin(self.road_position * curve_frequency) * 0.5
```

### Desired State (To)
- Road width maintains consistent base size
- Subtle oscillations (±5%) to simulate movement
- Smooth, realistic width variations
- Separate width oscillation from curve calculation

### Rationale
- Current system conflates road curvature with width changes
- Real roads don't dramatically change width while driving
- Excessive oscillation breaks immersion and realism
- Players need consistent visual reference for lane positioning

### Implementation Plan
1. Separate width calculation from curve calculation
2. Implement subtle width oscillation system
3. Add configurable parameters for oscillation amount
4. Ensure smooth transitions between width changes

### Impact Analysis
**Files Affected:**
- `src/scenes/drive.py` - Main road rendering logic
- Potentially new road utilities module

**Systems Touched:**
- Road rendering system
- Visual feedback system
- Performance (minimal impact expected)

**Potential Side Effects:**
- May need to adjust other visual elements for consistency
- Existing road curve behavior may need recalibration

### Testing Plan
**Unit Tests:**
- Test width calculation function
- Verify oscillation stays within ±5% bounds
- Test smooth transition behavior

**Integration Tests:**
- Verify road renders correctly at all speeds
- Test width consistency during turns
- Ensure no visual artifacts

**Performance Benchmarks:**
- Maintain 60 FPS during road rendering
- No increase in CPU usage for width calculations

### Acceptance Criteria
- [ ] Road width oscillates only ±5% from base width
- [ ] Width changes are smooth and gradual
- [ ] No visual artifacts or sudden jumps
- [ ] Maintains 60 FPS performance
- [ ] Unit tests pass with >90% coverage

---

## Issue #2: Implement Subtle Movement Effects

### Current State (From)
- Limited visual feedback for movement sensation
- Road appears static except for dramatic width changes
- Missing subtle effects that enhance speed perception
- No variation in road surface details

### Desired State (To)
- Subtle road surface movement effects
- Enhanced perception of speed and motion
- Smooth visual transitions that don't distract
- Configurable intensity based on speed

### Rationale
- Enhance player's sense of speed and movement
- Provide visual feedback for acceleration/deceleration
- Create more immersive racing experience
- Maintain performance while adding visual interest

### Implementation Plan
1. Add subtle road surface texture movement
2. Implement speed-based visual effect intensity
3. Create smooth interpolation for effect transitions
4. Add configuration options for effect strength

### Impact Analysis
**Files Affected:**
- `src/scenes/drive.py` - Visual effects rendering
- Potentially new visual effects utilities

**Systems Touched:**
- Road rendering system
- Performance optimization
- Visual feedback system

**Potential Side Effects:**
- May impact performance if not optimized
- Could be distracting if too prominent
- May need calibration with other visual elements

### Testing Plan
**Unit Tests:**
- Test effect intensity calculations
- Verify smooth interpolation functions
- Test configuration parameter validation

**Integration Tests:**
- Verify effects enhance rather than distract
- Test performance impact under load
- Ensure effects scale properly with speed

### Acceptance Criteria
- [ ] Subtle movement effects enhance speed perception
- [ ] Effects intensity scales with vehicle speed
- [ ] No performance impact (maintains 60 FPS)
- [ ] Effects are configurable and can be disabled
- [ ] Visual effects feel natural and immersive