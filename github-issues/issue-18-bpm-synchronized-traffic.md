# Issue #18: BPM-Synchronized Traffic System

## Summary
Implement a rhythm-based traffic system where vehicle spawning, speeds, and behaviors synchronize with the music's BPM (beats per minute), creating a musical driving experience.

## Current State
- Fixed traffic spawn intervals (2.5 seconds)
- Static speed ranges for different driver types
- No connection between music and traffic behavior
- Existing BPM field in MusicTrack but unused

## Desired State
- Traffic spawns on musical beats
- Vehicle speeds pulse with rhythm
- Lane changes align with musical phrases
- Visual feedback for beat timing
- Difficulty scales with music tempo

## Dependencies
- **Issue #31** (Traffic Passing Logic) - Must coordinate rhythmic passing decisions
- **Issue #32** (Road-Locked Tracking) - Needed for smooth visual rhythm effects

## Technical Requirements

### 1. BPM Detection Library
**Recommended: Librosa**
```bash
pip install librosa
```

**Key Features:**
- Perfect OGG support (critical for our audio files)
- Real-time capable with audio chunks
- Easy Pygame integration
- MIT license

### 2. Core Architecture

```python
# src/systems/bpm_tracker.py
class BPMTracker:
    """Track beats and provide rhythm information"""
    def __init__(self, bpm: float):
        self.bpm = bpm
        self.beat_interval = 60.0 / bpm
        self.current_beat = 0
        self.beat_phase = 0.0  # 0.0-1.0 within beat
        
    def update(self, dt: float) -> List[BeatEvent]:
        """Update beat tracking and return beat events"""
        
    def get_next_beat_time(self) -> float:
        """Get time until next beat"""
        
    def is_downbeat(self) -> bool:
        """Check if current beat is a downbeat (1 of 4)"""

# src/systems/rhythmic_traffic_controller.py
class RhythmicTrafficController:
    """Control traffic spawning and behavior with rhythm"""
    def __init__(self, bpm_tracker: BPMTracker):
        self.bpm_tracker = bpm_tracker
        self.spawn_pattern = "downbeats"  # or "steady", "syncopated"
        
    def should_spawn_traffic(self) -> bool:
        """Check if traffic should spawn based on rhythm"""
        
    def get_speed_modifier(self) -> float:
        """Get current speed pulse modifier"""
        
    def get_lane_change_probability(self, personality: str) -> float:
        """Get rhythm-influenced lane change chance"""
```

### 3. Integration with Issue #31 (Passing Logic)

```python
class RhythmicPassingDecision:
    """Enhance passing decisions with rhythm"""
    
    def should_attempt_pass_with_rhythm(self, car: NPCCar, 
                                       traffic_scan: Dict, 
                                       beat_info: BeatInfo) -> bool:
        # Safety first
        if not self.is_safe_to_pass(car, traffic_scan):
            return False
            
        # Rhythmic preference
        return self.apply_rhythmic_bias(car, beat_info)
    
    def apply_rhythmic_bias(self, car: NPCCar, beat_info: BeatInfo) -> bool:
        """Different personalities prefer different beats"""
        if car.personality == "aggressive" and beat_info.is_downbeat:
            return True  # Aggressive drivers love dramatic timing
        elif car.personality == "cautious" and beat_info.beat_number in [2, 4]:
            return random.random() < 0.3  # Cautious prefer off-beats
        return random.random() < 0.5
```

### 4. Visual Rhythm Feedback

```python
class RhythmVisualFeedback:
    """Visual elements that pulse with music"""
    
    def render_beat_indicator(self, screen, beat_info):
        """Dashboard beat light"""
        
    def apply_road_pulse(self, road_width, beat_phase):
        """Subtle road width pulse on beats"""
        
    def flash_speed_lines(self, beat_info):
        """Speed line effects on downbeats"""
```

## Implementation Plan

### Phase 1: Core BPM System (2 hours)
- [ ] Install and test Librosa
- [ ] Create BPMTracker class
- [ ] Integrate with existing MusicTrack BPM data
- [ ] Add beat event system

### Phase 2: Traffic Integration (3 hours)
- [ ] Modify spawn timing to use beats
- [ ] Add speed pulse effects
- [ ] Create rhythm patterns (steady, syncopated, etc.)
- [ ] Test with different BPM ranges

### Phase 3: Passing Logic Integration (2 hours)
- [ ] Coordinate with Issue #31 implementation
- [ ] Add personality-based beat preferences
- [ ] Implement turn signal rhythm
- [ ] Ensure safety overrides rhythm

### Phase 4: Visual Feedback (2 hours)
- [ ] Create beat indicator UI
- [ ] Add road pulse effects
- [ ] Implement speed boost visuals
- [ ] Performance optimization

### Phase 5: Configuration & Polish (1 hour)
- [ ] Add rhythm intensity settings
- [ ] Create fallback for non-rhythmic mode
- [ ] Balance difficulty scaling
- [ ] Final testing and tuning

## Configuration Options

```python
class BPMSettings:
    rhythm_intensity: float = 0.7      # 0.0-1.0, how much rhythm affects gameplay
    enable_visual_feedback: bool = True
    spawn_pattern: str = "downbeats"   # "steady", "downbeats", "syncopated", "burst"
    difficulty_scaling: bool = True     # Scale difficulty with BPM
    accessibility_mode: bool = False    # Disable rhythm requirements
```

## Success Criteria
- [ ] Traffic spawns feel musical and intentional
- [ ] Speed variations sync with beat without feeling robotic
- [ ] Passing decisions incorporate rhythm while maintaining safety
- [ ] Visual feedback enhances rhythm without distraction
- [ ] System works with all existing music tracks (108-140 BPM)
- [ ] Performance remains stable (60 FPS)

## Testing Strategy

### Unit Tests
- BPM detection accuracy
- Beat event timing
- Rhythm pattern generation

### Integration Tests
- Traffic spawn timing with music
- Passing logic with rhythm
- Visual feedback synchronization

### Gameplay Tests
- Different BPM ranges feel good
- Difficulty scaling works properly
- Accessibility mode functions correctly

## Notes
- Safety always overrides rhythm
- Keep effects subtle to maintain family-friendly feel
- Consider colorblind-friendly visual indicators
- Ensure system works without music for testing