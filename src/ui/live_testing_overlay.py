"""
Live Testing Overlay - Real-time test procedure display and validation.

This module provides a minimal, non-intrusive overlay that displays current
test procedures during gameplay for live validation and evidence collection.

Features:
- Display up to 3 active test procedures
- Real-time test completion tracking
- Manual and automatic test step completion
- Hotkey controls for test management
- Visual indicators for pass/fail states
- Minimal performance impact design
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import pygame


class TestStatus(Enum):
    """Test procedure status states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepStatus(Enum):
    """Individual test step status."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TestStep:
    """Individual step within a test procedure."""
    step_number: int
    action: str
    expected_result: str
    status: StepStatus = StepStatus.PENDING
    completion_time: Optional[float] = None
    actual_result: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    auto_detect_pattern: Optional[str] = None


@dataclass
class TestProcedure:
    """Complete test procedure with steps and metadata."""
    id: str
    title: str
    description: str
    issue_number: Optional[int] = None
    category: str = "manual"
    priority: str = "medium"
    steps: List[TestStep] = field(default_factory=list)
    status: TestStatus = TestStatus.PENDING
    current_step: int = 0
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    auto_detect: bool = False
    oqe_requirements: Dict[str, Any] = field(default_factory=dict)
    
    def get_current_step(self) -> Optional[TestStep]:
        """Get the currently active step."""
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def advance_step(self) -> bool:
        """Advance to next step. Returns True if test is complete."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            return False
        else:
            self.status = TestStatus.PASSED
            self.completion_time = time.time()
            return True
    
    def fail_current_step(self, reason: str = ""):
        """Mark current step as failed."""
        current_step = self.get_current_step()
        if current_step:
            current_step.status = StepStatus.FAILED
            current_step.actual_result = reason
        self.status = TestStatus.FAILED


class LiveTestingOverlay:
    """
    Real-time testing overlay for live gameplay validation.
    
    This overlay displays active test procedures in a minimal, non-intrusive
    way that allows testers to track progress and validate functionality
    during normal gameplay.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize the testing overlay.
        
        Args:
            screen_width: Game screen width
            screen_height: Game screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Display configuration
        self.max_displayed_procedures = 3
        self.overlay_enabled = True
        self.position = (10, 10)  # Top-left corner
        self.width = 350
        self.height = 200
        
        # Active test procedures
        self.active_procedures: List[TestProcedure] = []
        self.completed_procedures: List[TestProcedure] = []
        
        # UI styling
        self.colors = {
            "background": (0, 0, 0, 180),  # Semi-transparent black
            "border": (100, 100, 100, 200),
            "text_primary": (255, 255, 255),
            "text_secondary": (200, 200, 200),
            "status_pending": (255, 255, 0),     # Yellow
            "status_active": (0, 255, 255),      # Cyan
            "status_passed": (0, 255, 0),        # Green
            "status_failed": (255, 0, 0),        # Red
            "status_skipped": (128, 128, 128)    # Gray
        }
        
        # Font setup
        pygame.font.init()
        self.fonts = {
            "title": pygame.font.Font(None, 18),
            "body": pygame.font.Font(None, 14),
            "small": pygame.font.Font(None, 12)
        }
        
        # Event callbacks
        self.on_test_completed: Optional[Callable[[TestProcedure], None]] = None
        self.on_step_completed: Optional[Callable[[TestProcedure, TestStep], None]] = None
        
        # Auto-detection patterns
        self.detection_patterns: Dict[str, Callable[[Any], bool]] = {}
        
        # Hotkey configuration
        self.hotkeys = {
            pygame.K_F12: self.toggle_overlay,
            pygame.K_F11: self.next_procedure,
            pygame.K_F10: self.previous_procedure,
            pygame.K_F9: self.advance_current_step,
            pygame.K_F8: self.fail_current_step
        }
        
        # Performance tracking
        self.render_time_samples: List[float] = []
        self.max_render_samples = 60
    
    def add_test_procedure(self, procedure: TestProcedure):
        """
        Add a test procedure to the active list.
        
        Args:
            procedure: Test procedure to add
        """
        if len(self.active_procedures) >= self.max_displayed_procedures:
            # Move oldest to completed if it's done, otherwise skip
            oldest = self.active_procedures[0]
            if oldest.status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.SKIPPED]:
                self.completed_procedures.append(self.active_procedures.pop(0))
            else:
                return  # Don't add if we're at max and oldest isn't complete
        
        procedure.start_time = time.time()
        procedure.status = TestStatus.IN_PROGRESS
        if procedure.steps:
            procedure.steps[0].status = StepStatus.ACTIVE
        
        self.active_procedures.append(procedure)
    
    def remove_test_procedure(self, procedure_id: str) -> bool:
        """
        Remove a test procedure by ID.
        
        Args:
            procedure_id: ID of procedure to remove
            
        Returns:
            True if procedure was found and removed
        """
        for i, proc in enumerate(self.active_procedures):
            if proc.id == procedure_id:
                self.completed_procedures.append(self.active_procedures.pop(i))
                return True
        return False
    
    def update_procedure_status(self, procedure_id: str, step: int, status: StepStatus,
                              evidence: Dict[str, Any] = None) -> bool:
        """
        Update test procedure progress.
        
        Args:
            procedure_id: ID of procedure to update
            step: Step number to update
            status: New status for the step
            evidence: Optional evidence data
            
        Returns:
            True if update was successful
        """
        procedure = self.get_procedure_by_id(procedure_id)
        if not procedure or step >= len(procedure.steps):
            return False
        
        step_obj = procedure.steps[step]
        step_obj.status = status
        step_obj.completion_time = time.time()
        
        if evidence:
            step_obj.evidence.update(evidence)
        
        # Handle step completion
        if status == StepStatus.COMPLETED:
            if self.on_step_completed:
                self.on_step_completed(procedure, step_obj)
            
            # Auto-advance if this was the current step
            if step == procedure.current_step:
                is_complete = procedure.advance_step()
                if is_complete and self.on_test_completed:
                    self.on_test_completed(procedure)
        
        elif status == StepStatus.FAILED:
            procedure.status = TestStatus.FAILED
            if self.on_test_completed:
                self.on_test_completed(procedure)
        
        return True
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events for overlay control.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled by overlay
        """
        if not self.overlay_enabled:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key in self.hotkeys:
                self.hotkeys[event.key]()
                return True
        
        return False
    
    def update(self, dt: float, game_events: List[Any] = None):
        """
        Update overlay state and check for auto-completion.
        
        Args:
            dt: Delta time in seconds
            game_events: List of recent game events for auto-detection
        """
        if not self.overlay_enabled:
            return
        
        # Check auto-detection patterns
        if game_events:
            self._check_auto_detection(game_events)
        
        # Update procedure timings
        current_time = time.time()
        for procedure in self.active_procedures:
            if procedure.status == TestStatus.IN_PROGRESS:
                current_step = procedure.get_current_step()
                if current_step and current_step.status == StepStatus.PENDING:
                    current_step.status = StepStatus.ACTIVE
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the testing overlay on the game screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.overlay_enabled or not self.active_procedures:
            return
        
        render_start = time.perf_counter()
        
        # Create overlay surface with per-pixel alpha
        overlay_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(overlay_surface, self.colors["background"], 
                        (0, 0, self.width, self.height))
        pygame.draw.rect(overlay_surface, self.colors["border"], 
                        (0, 0, self.width, self.height), 2)
        
        # Draw header
        header_text = self.fonts["title"].render("🧪 Live Testing", True, self.colors["text_primary"])
        overlay_surface.blit(header_text, (8, 8))
        
        # Draw active procedures
        y_offset = 30
        for i, procedure in enumerate(self.active_procedures[:self.max_displayed_procedures]):
            if y_offset + 60 > self.height:
                break
            
            self._draw_procedure(overlay_surface, procedure, y_offset)
            y_offset += 50
        
        # Draw controls hint
        if y_offset + 20 < self.height:
            controls_text = self.fonts["small"].render("[F12] Toggle | [F9] Next Step", True, 
                                                     self.colors["text_secondary"])
            overlay_surface.blit(controls_text, (8, self.height - 15))
        
        # Blit to main screen
        screen.blit(overlay_surface, self.position)
        
        # Track render performance
        render_time = (time.perf_counter() - render_start) * 1000
        self.render_time_samples.append(render_time)
        if len(self.render_time_samples) > self.max_render_samples:
            self.render_time_samples = self.render_time_samples[-self.max_render_samples:]
    
    def _draw_procedure(self, surface: pygame.Surface, procedure: TestProcedure, y_offset: int):
        """Draw a single test procedure."""
        # Status indicator
        status_color = self.colors.get(f"status_{procedure.status.value}", self.colors["text_primary"])
        status_icon = self._get_status_icon(procedure.status)
        
        # Procedure title
        title_text = f"{status_icon} Issue #{procedure.issue_number or '??'}: {procedure.title[:30]}"
        if len(procedure.title) > 30:
            title_text += "..."
        
        title_surface = self.fonts["body"].render(title_text, True, status_color)
        surface.blit(title_surface, (8, y_offset))
        
        # Current step
        current_step = procedure.get_current_step()
        if current_step:
            step_text = f"  Step {procedure.current_step + 1}/{len(procedure.steps)}: {current_step.action[:35]}"
            if len(current_step.action) > 35:
                step_text += "..."
            
            step_surface = self.fonts["small"].render(step_text, True, self.colors["text_secondary"])
            surface.blit(step_surface, (8, y_offset + 15))
            
            # Step status indicator
            step_status_color = self.colors.get(f"status_{current_step.status.value}", 
                                              self.colors["text_secondary"])
            step_icon = self._get_step_status_icon(current_step.status)
            
            icon_surface = self.fonts["small"].render(step_icon, True, step_status_color)
            surface.blit(icon_surface, (self.width - 25, y_offset + 15))
        
        # Progress bar
        if procedure.steps:
            progress = procedure.current_step / len(procedure.steps)
            bar_width = self.width - 20
            bar_height = 3
            
            # Background
            pygame.draw.rect(surface, self.colors["border"], 
                           (8, y_offset + 35, bar_width, bar_height))
            
            # Progress
            if progress > 0:
                progress_width = int(bar_width * progress)
                pygame.draw.rect(surface, status_color, 
                               (8, y_offset + 35, progress_width, bar_height))
    
    def _get_status_icon(self, status: TestStatus) -> str:
        """Get icon for test status."""
        icons = {
            TestStatus.PENDING: "⚪",
            TestStatus.IN_PROGRESS: "⏳",
            TestStatus.PASSED: "✅",
            TestStatus.FAILED: "❌", 
            TestStatus.SKIPPED: "⏭️"
        }
        return icons.get(status, "❓")
    
    def _get_step_status_icon(self, status: StepStatus) -> str:
        """Get icon for step status."""
        icons = {
            StepStatus.PENDING: "⚪",
            StepStatus.ACTIVE: "▶️",
            StepStatus.COMPLETED: "✅",
            StepStatus.FAILED: "❌"
        }
        return icons.get(status, "❓")
    
    def _check_auto_detection(self, game_events: List[Any]):
        """Check for auto-detection patterns in game events."""
        for procedure in self.active_procedures:
            if procedure.status != TestStatus.IN_PROGRESS:
                continue
            
            current_step = procedure.get_current_step()
            if not current_step or not current_step.auto_detect_pattern:
                continue
            
            # Check if pattern matches recent events
            pattern = current_step.auto_detect_pattern
            if pattern in self.detection_patterns:
                detector = self.detection_patterns[pattern]
                if detector(game_events):
                    self.update_procedure_status(procedure.id, procedure.current_step, 
                                               StepStatus.COMPLETED)
    
    def register_auto_detection(self, pattern: str, detector: Callable[[Any], bool]):
        """
        Register an auto-detection pattern.
        
        Args:
            pattern: Pattern identifier
            detector: Function that returns True when pattern is detected
        """
        self.detection_patterns[pattern] = detector
    
    def get_procedure_by_id(self, procedure_id: str) -> Optional[TestProcedure]:
        """Get procedure by ID from active list."""
        for procedure in self.active_procedures:
            if procedure.id == procedure_id:
                return procedure
        return None
    
    def toggle_overlay(self):
        """Toggle overlay visibility."""
        self.overlay_enabled = not self.overlay_enabled
    
    def next_procedure(self):
        """Cycle to next procedure (for focus/highlighting)."""
        if len(self.active_procedures) > 1:
            # Move first to end
            procedure = self.active_procedures.pop(0)
            self.active_procedures.append(procedure)
    
    def previous_procedure(self):
        """Cycle to previous procedure."""
        if len(self.active_procedures) > 1:
            # Move last to front
            procedure = self.active_procedures.pop()
            self.active_procedures.insert(0, procedure)
    
    def advance_current_step(self):
        """Manually advance current step of first active procedure."""
        if self.active_procedures:
            procedure = self.active_procedures[0]
            if procedure.status == TestStatus.IN_PROGRESS:
                self.update_procedure_status(procedure.id, procedure.current_step, 
                                           StepStatus.COMPLETED)
    
    def fail_current_step(self):
        """Manually fail current step of first active procedure."""
        if self.active_procedures:
            procedure = self.active_procedures[0]
            if procedure.status == TestStatus.IN_PROGRESS:
                self.update_procedure_status(procedure.id, procedure.current_step, 
                                           StepStatus.FAILED)
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get overlay rendering performance statistics."""
        if not self.render_time_samples:
            return {"avg_render_time_ms": 0.0, "max_render_time_ms": 0.0}
        
        avg_time = sum(self.render_time_samples) / len(self.render_time_samples)
        max_time = max(self.render_time_samples)
        
        return {
            "avg_render_time_ms": round(avg_time, 3),
            "max_render_time_ms": round(max_time, 3),
            "sample_count": len(self.render_time_samples)
        }
    
    def export_test_results(self) -> Dict[str, Any]:
        """Export complete test results for reporting."""
        all_procedures = self.active_procedures + self.completed_procedures
        
        results = {
            "session_summary": {
                "total_procedures": len(all_procedures),
                "passed": len([p for p in all_procedures if p.status == TestStatus.PASSED]),
                "failed": len([p for p in all_procedures if p.status == TestStatus.FAILED]),
                "in_progress": len([p for p in all_procedures if p.status == TestStatus.IN_PROGRESS]),
                "skipped": len([p for p in all_procedures if p.status == TestStatus.SKIPPED])
            },
            "procedures": [],
            "performance_stats": self.get_performance_stats()
        }
        
        for procedure in all_procedures:
            proc_data = {
                "id": procedure.id,
                "title": procedure.title,
                "issue_number": procedure.issue_number,
                "status": procedure.status.value,
                "start_time": procedure.start_time,
                "completion_time": procedure.completion_time,
                "duration_s": (procedure.completion_time - procedure.start_time) 
                             if procedure.completion_time and procedure.start_time else None,
                "steps": []
            }
            
            for step in procedure.steps:
                step_data = {
                    "step_number": step.step_number,
                    "action": step.action,
                    "expected_result": step.expected_result,
                    "actual_result": step.actual_result,
                    "status": step.status.value,
                    "completion_time": step.completion_time,
                    "evidence": step.evidence
                }
                proc_data["steps"].append(step_data)
            
            results["procedures"].append(proc_data)
        
        return results