# Verbose Logging and OQE Testing Implementation Plan

## 🎯 Overview
This document outlines the implementation plan for Issue #34 - Dynamic Game State Logging and Live Testing System, with emphasis on OQE (Objective Qualified Evidence) compliance and agent pipeline integration.

## 📋 Phase 1: Core Logging Infrastructure

### 1.1 Game State Logger Architecture
```python
# src/systems/game_state_logger.py
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import json
import time
import os
from pathlib import Path

@dataclass
class GameEvent:
    """Represents a single game event with OQE metadata"""
    timestamp: float
    session_id: str
    scene: str
    event_type: str  # "input", "state_change", "audio", "collision", "performance", "test"
    event_data: Dict[str, Any]
    test_context: Optional[str] = None
    oqe_metrics: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_json(self) -> str:
        """Convert to JSON with OQE compliance"""
        return json.dumps({
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "scene": self.scene,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "test_context": self.test_context,
            "oqe_metrics": self.oqe_metrics,
            "tags": self.tags
        })
```

### 1.2 Logger Implementation Tasks
1. **Create base logger class** with session management
2. **Implement log rotation** (10MB files, keep last 5 sessions)
3. **Add performance tracking** to measure logging overhead
4. **Create event factory** for standardized event creation
5. **Implement async logging** to prevent game lag

### 1.3 OQE Metric Collection
```python
class OQEMetricCollector:
    """Collects objective metrics for test evidence"""
    
    def measure_fps(self) -> Dict[str, float]:
        """Measure current FPS with statistics"""
        
    def measure_memory(self) -> Dict[str, float]:
        """Measure memory usage and delta"""
        
    def measure_response_time(self, event: str) -> float:
        """Measure time between input and response"""
        
    def calculate_accuracy(self, expected: Any, actual: Any) -> float:
        """Calculate accuracy percentage for comparisons"""
```

## 📋 Phase 2: Scene Integration

### 2.1 SceneManager Integration
```python
# Modify src/scene_manager.py
class SceneManager:
    def __init__(self, sound_manager, game_logger):
        self.game_logger = game_logger
        # ... existing code ...
        
    def switch_scene(self, scene_name, data=None):
        # Log scene transition with OQE metrics
        transition_start = time.time()
        old_scene = self.current_scene_name
        
        # ... existing transition code ...
        
        self.game_logger.log_scene_transition(
            from_scene=old_scene,
            to_scene=scene_name,
            data={
                "transition_time_ms": (time.time() - transition_start) * 1000,
                "memory_before": self.get_memory_usage(),
                "passed_data": data
            }
        )
```

### 2.2 Input Logging
- Log all keyboard and mouse events with context
- Track response times for UI interactions
- Record input sequences for replay testing
- Measure input-to-action latency

### 2.3 Audio Event Logging
- Track all music start/stop events
- Log volume changes
- Record sound effect triggers
- Monitor audio resource usage

## 📋 Phase 3: Live Testing Overlay

### 3.1 Test Procedure Format
```json
{
  "issue_number": 34,
  "feature": "Game State Logging",
  "test_procedures": [
    {
      "id": "logging_performance",
      "title": "Verify logging has <2% FPS impact",
      "steps": [
        {
          "action": "Enable verbose logging",
          "expected": "Logging active indicator",
          "measure": ["fps_before", "fps_with_logging"]
        },
        {
          "action": "Play for 60 seconds",
          "expected": "Smooth gameplay",
          "measure": ["avg_fps", "frame_drops"]
        }
      ],
      "oqe_requirements": {
        "fps_impact": {"max": 2, "unit": "percent"},
        "frame_drops": {"max": 5, "unit": "count"}
      }
    }
  ]
}
```

### 3.2 Overlay Implementation
```python
class LiveTestingOverlay:
    """Minimal overlay for test procedure display"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.font = pygame.font.Font(None, 16)
        self.bg_color = (0, 0, 0, 180)  # Semi-transparent
        self.text_color = (255, 255, 255)
        self.active_procedures = []
        
    def draw_procedure(self, screen, procedure, y_offset):
        """Draw single test procedure with progress"""
        # Compact display: [✓] Step 1/3: Enable logging
```

### 3.3 Auto-Detection System
```python
class TestAutoDetector:
    """Automatically detect test completion from game events"""
    
    def __init__(self, game_logger):
        self.game_logger = game_logger
        self.detection_rules = {}
        
    def register_detection(self, test_id: str, event_pattern: List[str]):
        """Register event pattern for auto-detection"""
        
    def check_completion(self, recent_events: List[GameEvent]) -> Dict[str, bool]:
        """Check if any tests completed based on events"""
```

## 📋 Phase 4: OQE Integration

### 4.1 Test Evidence Collection
```python
class OQEEvidenceCollector:
    """Collects evidence for OQE compliance"""
    
    def collect_test_evidence(self, test_id: str, session_id: str) -> Dict:
        """Extract evidence from game logs"""
        return {
            "test_id": test_id,
            "session_id": session_id,
            "preconditions": self.extract_preconditions(),
            "measurements": self.extract_measurements(),
            "postconditions": self.extract_postconditions(),
            "oqe_score": self.calculate_oqe_score()
        }
```

### 4.2 Report Generation
```python
class OQEReportGenerator:
    """Generate OQE-compliant test reports"""
    
    def generate_report(self, test_results: List[Dict]) -> str:
        """Generate markdown report with evidence"""
        
    def calculate_compliance_score(self, evidence: Dict) -> float:
        """Calculate OQE compliance percentage"""
```

## 📋 Phase 5: Minigame Integration

### 5.1 Drive Minigame Logging
- Log music selection and preview events
- Track collision events with NPCs/hazards
- Record race performance metrics
- Monitor BPM system if enabled

### 5.2 Pool Minigame Logging
- Log shot attempts and accuracy
- Track ball trajectories
- Record game state changes
- Monitor physics calculations

### 5.3 Ski Minigame Logging
- Log player path and obstacles hit
- Track speed and score progression
- Record power-up usage
- Monitor rendering performance

## 🎯 Agent Pipeline Integration

### Pipeline Structure for Implementation
```yaml
agents:
  - measurement_infrastructure:
      purpose: "Build logging and metric collection"
      deliverables:
        - GameStateLogger class
        - OQEMetricCollector class
        - Performance impact measurement
        
  - test_framework:
      purpose: "Create test procedure system"
      deliverables:
        - Test procedure loader
        - Auto-detection system
        - Evidence collector
        
  - ui_implementation:
      purpose: "Build live testing overlay"
      deliverables:
        - Minimal overlay UI
        - Hotkey controls
        - Progress tracking
        
  - integration:
      purpose: "Integrate with existing systems"
      deliverables:
        - Scene manager hooks
        - Sound manager logging
        - Save system integration
```

### OQE Validation Points
1. **Pre-implementation baseline**: Current FPS, memory usage
2. **Post-implementation metrics**: Impact measurements
3. **Test coverage**: Percentage of events logged
4. **Evidence quality**: Completeness of captured data

## 🔧 Implementation Tools

### Log Analysis Script
```python
# tools/analyze_game_logs.py
def analyze_session(session_id: str):
    """Analyze complete game session"""
    
def extract_test_evidence(session_id: str, test_id: str):
    """Extract OQE evidence for specific test"""
    
def generate_performance_report(session_id: str):
    """Generate performance analysis report"""
```

### Testing Dashboard
```python
# tools/testing_dashboard.py
def create_dashboard():
    """Create real-time testing dashboard"""
    # Uses Flask/WebSocket for live updates
    # Shows current tests, completion status
    # Displays performance metrics
```

## 📊 Success Metrics

### Quantifiable Goals
1. **Performance Impact**: < 2% FPS reduction
2. **Log Completeness**: 100% of defined events
3. **Test Coverage**: 90% auto-detectable
4. **Evidence Quality**: > 95% OQE compliance
5. **File Size**: < 10MB per hour

### Validation Tests
1. Run game for 1 hour with logging enabled
2. Measure FPS impact across all scenes
3. Verify log searchability (< 1 second)
4. Test overlay in all screen resolutions
5. Validate OQE report generation

## 🚀 Implementation Priority

### Week 1: Core Infrastructure
- [ ] GameStateLogger implementation
- [ ] Basic event logging
- [ ] Performance measurement
- [ ] Log file management

### Week 2: Scene Integration
- [ ] SceneManager hooks
- [ ] Input event logging
- [ ] Audio event logging
- [ ] Save system integration

### Week 3: Testing Overlay
- [ ] Overlay UI implementation
- [ ] Test procedure loader
- [ ] Progress tracking
- [ ] Hotkey controls

### Week 4: OQE Integration
- [ ] Evidence collector
- [ ] Report generator
- [ ] Auto-detection system
- [ ] Compliance scoring

### Week 5: Polish & Testing
- [ ] Performance optimization
- [ ] Edge case handling
- [ ] Documentation
- [ ] Integration testing

## 📝 Notes for Agent Pipeline

### Key Considerations
1. **Minimize performance impact** - Use async logging
2. **Maintain game feel** - Overlay must be unobtrusive
3. **Evidence quality** - All metrics must be accurate
4. **Backwards compatibility** - Don't break existing systems

### Testing Requirements
1. Each component must have unit tests
2. Integration tests for scene transitions
3. Performance benchmarks before/after
4. OQE compliance validation

### Documentation Needs
1. Event type reference
2. Test procedure format guide
3. OQE evidence examples
4. Troubleshooting guide

---

This plan provides a comprehensive framework for implementing the verbose logging and OQE testing system through the agent pipeline, ensuring measurable success and high-quality evidence collection.