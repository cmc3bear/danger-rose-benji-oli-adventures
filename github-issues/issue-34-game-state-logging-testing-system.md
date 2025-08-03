# Issue #34: Dynamic Game State Logging and Live Testing System

## 🎯 Overview
Implement a comprehensive game state logging mechanism that tracks player actions, scene transitions, and system events across the hub and all minigames. Include a dynamic live testing overlay that displays current test procedures and allows real-time validation during gameplay.

## 🔍 Problem Statement
Currently, testing and debugging game issues requires:
- Manual recreation of specific scenarios
- Guesswork about what happened during crashes or bugs
- No visibility into test plan compliance during live gameplay
- Difficulty correlating user actions with system events
- No systematic way to verify test procedures are being followed

## 🎯 Solution Requirements

### Core Logging System
1. **Comprehensive State Tracking**
   - Player position, health, score in all scenes
   - Scene transitions with timestamps
   - Input events (keyboard, mouse) with context
   - Audio events (music start/stop, volume changes)
   - Collision events and physics interactions
   - Performance metrics (FPS, memory usage)
   - Error events and exception handling

2. **Structured Log Format**
   - JSON-based log entries for easy parsing
   - Hierarchical organization by scene/system
   - Searchable tags and categories
   - Performance impact measurement
   - Session correlation IDs

3. **Live Testing Overlay**
   - Display current active test procedures (max 3)
   - Real-time test completion tracking
   - Dynamic test plan switching
   - Visual indicators for pass/fail states
   - Minimal performance impact

## 🏗️ Technical Architecture

### 1. Game State Logger (`src/systems/game_state_logger.py`)

```python
@dataclass
class GameEvent:
    """Represents a single game event for logging"""
    timestamp: float
    session_id: str
    scene: str
    event_type: str  # "input", "state_change", "audio", "collision", "performance"
    event_data: Dict[str, Any]
    test_context: Optional[str] = None  # Current test being executed
    tags: List[str] = field(default_factory=list)

class GameStateLogger:
    """Centralized logging system for all game events"""
    
    def __init__(self, project_root: str, enable_live_overlay: bool = True):
        self.session_id = self._generate_session_id()
        self.log_file = f"logs/game_session_{self.session_id}.jsonl"
        self.current_scene = "unknown"
        self.current_test_context = None
        self.live_overlay = enable_live_overlay
        
    def log_scene_transition(self, from_scene: str, to_scene: str, data: dict):
        """Log scene transition events"""
        
    def log_player_action(self, action: str, scene: str, details: dict):
        """Log player input and resulting actions"""
        
    def log_system_event(self, system: str, event: str, data: dict):
        """Log system-level events (audio, physics, etc.)"""
        
    def log_performance_metric(self, metric_name: str, value: float, context: dict):
        """Log performance measurements"""
        
    def set_test_context(self, test_issue: str, test_procedure: str):
        """Set current testing context for log correlation"""
```

### 2. Live Testing Overlay (`src/ui/live_testing_overlay.py`)

```python
class TestProcedure:
    """Represents a single test procedure"""
    id: str
    title: str
    description: str
    steps: List[str]
    current_step: int = 0
    status: str = "pending"  # pending, in_progress, passed, failed
    auto_detect: bool = False  # Can system auto-detect completion?

class LiveTestingOverlay:
    """Real-time testing overlay for live gameplay validation"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.active_procedures: List[TestProcedure] = []
        self.max_displayed = 3
        self.overlay_enabled = True
        self.position = (10, 10)  # Top-left corner
        
    def load_test_procedures(self, issue_number: int):
        """Load test procedures for specific GitHub issue"""
        
    def update_procedure_status(self, procedure_id: str, step: int, status: str):
        """Update test procedure progress"""
        
    def draw_overlay(self, screen: pygame.Surface):
        """Draw testing overlay on game screen"""
        
    def handle_manual_completion(self, event) -> bool:
        """Handle manual test step completion via hotkeys"""
```

### 3. Test Plan Integration (`src/testing/test_plan_loader.py`)

```python
class TestPlanLoader:
    """Loads and manages test procedures from GitHub issues"""
    
    def __init__(self, project_root: str):
        self.test_plans_dir = os.path.join(project_root, "test_plans")
        self.procedures_cache = {}
        
    def load_issue_test_plan(self, issue_number: int) -> List[TestProcedure]:
        """Load test procedures for specific issue"""
        
    def generate_from_oqe_report(self, oqe_report: dict) -> List[TestProcedure]:
        """Generate test procedures from OQE compliance reports"""
        
    def validate_test_completion(self, procedure_id: str, game_logs: List[GameEvent]) -> bool:
        """Validate if test was completed based on game logs"""
```

## 📋 Implementation Plan

### Phase 1: Core Logging System (Week 1-2)

#### Sprint 1.1: Basic Logging Infrastructure
- [ ] Create `GameStateLogger` class with JSON logging
- [ ] Implement session management and log rotation
- [ ] Add basic event types (scene, input, system)
- [ ] Create log file organization structure
- [ ] Add performance impact measurement

#### Sprint 1.2: Scene Integration
- [ ] Integrate logger into `SceneManager`
- [ ] Add logging to all scene transitions
- [ ] Log player actions in Hub World
- [ ] Log audio events (music start/stop/volume)
- [ ] Add error and exception logging

### Phase 2: Live Testing Overlay (Week 3)

#### Sprint 2.1: Overlay System
- [ ] Create `LiveTestingOverlay` UI component
- [ ] Design overlay visual style (minimal, non-intrusive)
- [ ] Implement test procedure display (max 3)
- [ ] Add hotkey controls for manual test completion
- [ ] Create toggle mechanism (F12 key)

#### Sprint 2.2: Test Plan Integration
- [ ] Create `TestPlanLoader` for GitHub issue integration
- [ ] Design test procedure JSON format
- [ ] Implement dynamic test plan switching
- [ ] Add auto-detection for common test scenarios
- [ ] Create test completion validation

### Phase 3: Minigame Integration (Week 4)

#### Sprint 3.1: Drive Minigame Logging
- [ ] Log race start/end events
- [ ] Track music selection and playback
- [ ] Log collision and obstacle events
- [ ] Monitor performance during gameplay
- [ ] Add race-specific test procedures

#### Sprint 3.2: Pool & Ski Minigames
- [ ] Implement logging for Pool minigame mechanics
- [ ] Add Ski minigame event tracking
- [ ] Create minigame-specific test procedures
- [ ] Add score and achievement logging
- [ ] Test cross-scene log correlation

### Phase 4: Advanced Features (Week 5)

#### Sprint 4.1: Analytics and Reporting
- [ ] Create log analysis tools
- [ ] Generate test completion reports
- [ ] Add performance trend analysis
- [ ] Create debugging assistance features
- [ ] Implement log search and filtering

#### Sprint 4.2: OQE Integration
- [ ] Connect with existing OQE pipeline
- [ ] Auto-generate test procedures from OQE reports
- [ ] Validate OQE compliance through logs
- [ ] Create evidence collection from game logs
- [ ] Generate OQE-compliant test reports

## 🎮 Live Testing Overlay Design

### Visual Layout
```
┌─ Game Screen (1024x768) ─────────────────────────────┐
│ ┌─ Testing Overlay (300x150) ─┐                      │
│ │ 🧪 Issue #28: Character UI  │                      │
│ │ ✅ Select 6 characters       │                      │
│ │ ⏳ Test grid layout         │                      │
│ │ ⚪ Verify persistence       │                      │
│ │                             │                      │
│ │ 🎯 Issue #34: Audio Fix     │                      │
│ │ ✅ Enter drive scene        │                      │
│ │ ⏳ Start race music         │                      │
│ │                             │                      │
│ │ [F12] Toggle | [F11] Next   │                      │
│ └─────────────────────────────┘                      │
│                                                      │
│                    Game Content                      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Test Procedure Format
```json
{
  "issue_number": 28,
  "title": "Character Selection UI - 6 Characters",
  "procedures": [
    {
      "id": "char_select_display",
      "title": "Display 6 characters",
      "description": "Verify all 6 characters appear in selection screen",
      "steps": [
        "Navigate to character selection",
        "Count visible characters",
        "Verify 2x3 grid layout"
      ],
      "auto_detect": true,
      "detection_events": ["scene_transition:title_screen", "ui_render:character_buttons:6"]
    },
    {
      "id": "char_select_persist",
      "title": "Selection persistence",
      "description": "Selected character persists across scenes",
      "steps": [
        "Select a character",
        "Enter hub world",
        "Verify character matches selection"
      ],
      "auto_detect": true,
      "detection_events": ["player_action:character_select", "scene_transition:hub", "player_spawn"]
    }
  ]
}
```

## 🔧 Logging Event Categories

### 1. Scene Events
```json
{
  "event_type": "scene_transition",
  "event_data": {
    "from_scene": "hub_world",
    "to_scene": "drive_minigame",
    "transition_data": {"selected_character": "Danger"},
    "load_time_ms": 1250
  },
  "tags": ["navigation", "performance"]
}
```

### 2. Player Actions
```json
{
  "event_type": "player_action",
  "event_data": {
    "action": "character_select",
    "character": "Uncle Bear",
    "input_method": "mouse_click",
    "response_time_ms": 45
  },
  "tags": ["ui", "character_selection"]
}
```

### 3. Audio Events
```json
{
  "event_type": "audio",
  "event_data": {
    "action": "music_start",
    "track": "highway_dreams.mp3",
    "volume": 0.7,
    "fade_in_ms": 1000,
    "success": true
  },
  "tags": ["music", "drive_scene"]
}
```

### 4. Performance Metrics
```json
{
  "event_type": "performance",
  "event_data": {
    "metric": "fps",
    "value": 58.3,
    "scene": "drive_minigame",
    "context": "racing_active"
  },
  "tags": ["performance", "fps"]
}
```

## 🎯 Testing Integration Examples

### Drive Scene Audio Fix (Issue #33)
```python
# Test procedures for Drive scene audio fix
drive_audio_tests = [
    {
        "id": "hub_music_stops",
        "title": "Hub music stops on drive entry",
        "auto_detect": True,
        "detection": ["scene_transition:drive", "audio:music_stop"]
    },
    {
        "id": "race_music_starts", 
        "title": "Race music starts without crash",
        "auto_detect": True,
        "detection": ["player_action:spacebar", "audio:music_start", "state:racing"]
    },
    {
        "id": "volume_control_works",
        "title": "Volume controls work during preview",
        "auto_detect": False,
        "manual_steps": ["Select track", "Adjust volume", "Verify audio level"]
    }
]
```

### Character Selection UI (Issue #28)
```python
character_ui_tests = [
    {
        "id": "six_characters_display",
        "title": "6 characters display in grid",
        "auto_detect": True,
        "detection": ["scene:title_screen", "ui_render:character_buttons:6"]
    },
    {
        "id": "grid_layout_correct",
        "title": "2x3 grid layout is correct",
        "auto_detect": True,
        "detection": ["ui_measurement:grid_positioning:>95%"]
    },
    {
        "id": "selection_persists",
        "title": "Character selection persists",
        "auto_detect": True,
        "detection": ["character_select", "scene_transition", "character_match"]
    }
]
```

## 🛠️ Development Tools

### Log Analysis Script (`tools/analyze_game_logs.py`)
```python
def analyze_test_completion(log_file: str, issue_number: int):
    """Analyze logs to determine test completion status"""
    
def generate_test_report(session_id: str) -> dict:
    """Generate comprehensive test report from session logs"""
    
def find_performance_issues(log_file: str) -> List[dict]:
    """Identify performance bottlenecks from logs"""
```

### Live Testing Dashboard (`tools/testing_dashboard.html`)
- Real-time log streaming
- Test completion visualization
- Performance monitoring
- Issue correlation tracking

## 📊 Success Metrics

### Logging System
- **Coverage**: 100% of game events logged
- **Performance Impact**: <2% FPS reduction
- **Log Size**: <10MB per hour of gameplay
- **Search Time**: <1 second for any query

### Testing System
- **Test Visibility**: 90% of tests have live overlay support
- **Auto-Detection**: 70% of tests can be auto-validated
- **Manual Efficiency**: 50% reduction in manual testing time
- **Bug Correlation**: 95% of issues can be traced through logs

## 🔗 Integration Points

### Existing Systems
- **OQE Pipeline**: Auto-generate test procedures from OQE reports
- **Scene Manager**: Integrate logging into scene lifecycle
- **Sound Manager**: Add audio event logging
- **Performance Metrics**: Connect with existing metrics system

### External Tools
- **GitHub Issues**: Load test procedures from issue descriptions
- **CI/CD**: Generate test reports for automated builds
- **Debugging Tools**: Provide log context for crash analysis

## 🎯 Acceptance Criteria

### Core Functionality
- [ ] All game events are logged with structured format
- [ ] Live testing overlay displays without impacting gameplay
- [ ] Test procedures can be loaded dynamically from GitHub issues
- [ ] Performance impact is under 2% FPS reduction
- [ ] Logs can be analyzed for test completion validation

### User Experience
- [ ] Overlay can be toggled on/off with F12 key
- [ ] Maximum 3 test procedures displayed at once
- [ ] Test status updates in real-time during gameplay
- [ ] Manual test completion works with hotkeys
- [ ] Overlay is visually non-intrusive

### Technical Requirements
- [ ] Logs are stored in structured JSON format
- [ ] Session correlation works across scene transitions
- [ ] Auto-detection works for common test scenarios
- [ ] Integration with existing OQE pipeline
- [ ] Log rotation and cleanup mechanisms

### Testing Validation
- [ ] Issue #28 (Character Selection) test procedures work
- [ ] Issue #33 (Drive Audio) test procedures work
- [ ] Performance metrics are captured accurately
- [ ] Test completion can be validated from logs
- [ ] Reports can be generated for OQE compliance

---

## 🚀 Implementation Priority

**High Priority**: Core logging system and basic overlay
**Medium Priority**: Auto-detection and GitHub integration  
**Low Priority**: Advanced analytics and dashboard

This system will revolutionize our testing and debugging capabilities, providing real-time visibility into game state and systematic validation of test procedures during live gameplay.

## 🔗 Related Issues

- Issue #28: Character Selection UI (test procedures needed)
- Issue #33: Drive Audio Fix (validation needed)  
- OQE Pipeline: Integration for evidence collection
- Performance Optimization: Metrics collection integration

**Estimated Development Time**: 4-5 weeks
**Team Impact**: High (affects all future testing and debugging)
**User Impact**: Minimal (optional overlay, no gameplay changes)