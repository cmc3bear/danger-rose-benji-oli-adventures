# Issue #31: Implement Intelligent Traffic Passing Logic

## Summary
Add sophisticated AI logic for NPC vehicles to make intelligent decisions about when to pass slower vehicles, creating more realistic highway traffic behavior.

## Current State
- Traffic cars have varied speeds
- Cars can change lanes randomly
- No decision-making based on surrounding traffic
- No consideration of safe passing distances

## Desired State
- Cars should evaluate whether to pass based on:
  - Speed differential with car ahead
  - Available space in adjacent lane
  - Oncoming traffic (for 2-lane sections)
  - Safe following distances
- Different vehicle personalities (cautious, normal, aggressive)
- Trucks should pass less frequently
- Emergency lane changes for collision avoidance

## Technical Requirements

### 1. Traffic Awareness System
```python
class TrafficAwareness:
    def scan_surrounding_traffic(self, car: NPCCar) -> Dict:
        """Scan for nearby vehicles in all lanes"""
        return {
            "ahead_same_lane": Vehicle or None,
            "ahead_left_lane": Vehicle or None,
            "ahead_right_lane": Vehicle or None,
            "behind_left_lane": Vehicle or None,
            "behind_right_lane": Vehicle or None,
            "safe_to_change_left": bool,
            "safe_to_change_right": bool
        }
```

### 2. Passing Decision Logic
```python
def should_attempt_pass(self, car: NPCCar, traffic_scan: Dict) -> bool:
    """Determine if car should attempt to pass"""
    # Factors to consider:
    # - Speed differential > threshold
    # - Safe gap in target lane
    # - Driver personality (aggressive vs cautious)
    # - Vehicle type (trucks pass less)
    # - Current speed vs desired speed
```

### 3. Lane Change Execution
```python
def execute_lane_change(self, car: NPCCar, target_lane: int):
    """Smooth lane change with turn signals"""
    # - Activate turn signal
    # - Gradual lane transition
    # - Maintain safe speed during change
    # - Complete maneuver or abort if unsafe
```

## Implementation Plan

### Phase 1: Traffic Scanning
- [ ] Implement surrounding traffic detection
- [ ] Calculate relative speeds and distances
- [ ] Determine safe gaps for lane changes

### Phase 2: Decision Making
- [ ] Create driver personality profiles
- [ ] Implement passing decision algorithm
- [ ] Add vehicle-type specific behaviors

### Phase 3: Safe Execution
- [ ] Smooth lane change animations
- [ ] Turn signal system
- [ ] Abort mechanism for unsafe situations

### Phase 4: Testing & Tuning
- [ ] Test various traffic densities
- [ ] Tune passing frequencies
- [ ] Ensure no deadlocks or traffic jams

## Success Criteria
- [ ] Cars pass slower traffic naturally
- [ ] No unrealistic lane changes
- [ ] Traffic flows smoothly
- [ ] Different driver behaviors visible
- [ ] Safe following distances maintained

## Dependencies
- Requires Issue #32 (Road-locked tracking) for proper lane positioning

## Estimated Effort
- 3-4 hours implementation
- 1-2 hours testing and tuning

## Notes
- Consider adding turn signals as visual feedback
- May need to adjust spawn rates to prevent congestion
- Could add "road rage" behavior for very aggressive drivers