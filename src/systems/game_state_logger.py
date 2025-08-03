"""
Game State Logger - Comprehensive event logging system with OQE compliance.

This module provides centralized logging for all game events including:
- Scene transitions
- Player actions
- Audio events
- Performance metrics
- System events

Design goals:
- Minimal performance impact (<2% FPS)
- Structured JSON logging
- Session management
- Test context tracking
- OQE compliance
"""

import json
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from queue import Queue
import psutil
import pygame


logger = logging.getLogger(__name__)


@dataclass
class GameEvent:
    """Represents a single game event with OQE metadata."""
    timestamp: float
    session_id: str
    scene: str
    event_type: str  # "input", "state_change", "audio", "collision", "performance", "test"
    event_data: Dict[str, Any]
    test_context: Optional[str] = None
    oqe_metrics: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_json(self) -> str:
        """Convert to JSON with OQE compliance."""
        return json.dumps({
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "scene": self.scene,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "test_context": self.test_context,
            "oqe_metrics": self.oqe_metrics,
            "tags": self.tags
        }, default=str)


class GameStateLogger:
    """
    Centralized logging system for all game events.
    
    Features:
    - Asynchronous logging to prevent game lag
    - Session management with unique IDs
    - Log rotation (10MB files, keep last 5 sessions)
    - Performance tracking for overhead measurement
    - Test context correlation
    """
    
    def __init__(self, project_root: str, enable_live_overlay: bool = True):
        self.project_root = Path(project_root)
        self.session_id = self._generate_session_id()
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Current session log file
        self.log_file = self.logs_dir / f"game_session_{self.session_id}.jsonl"
        
        # State tracking
        self.current_scene = "unknown"
        self.current_test_context = None
        self.start_time = time.time()
        self.last_performance_check = time.time()
        
        # Performance tracking
        self.events_logged = 0
        self.logging_overhead_ms = 0.0
        self.performance_samples = []
        
        # Async logging setup
        self.log_queue = Queue()
        self.logging_thread = None
        self.shutdown_requested = False
        
        # Process monitoring
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Start async logging thread
        self._start_logging_thread()
        
        # Log session start
        self._log_session_start()
        
        # Cleanup old logs
        self._cleanup_old_logs()
        
        logger.info(f"GameStateLogger initialized for session {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = int(time.time())
        unique_part = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_part}"
    
    def _start_logging_thread(self):
        """Start the asynchronous logging thread."""
        self.logging_thread = threading.Thread(target=self._async_log_worker, daemon=True)
        self.logging_thread.start()
    
    def _async_log_worker(self):
        """Worker thread for asynchronous logging."""
        while not self.shutdown_requested:
            try:
                # Wait for events with timeout to allow periodic cleanup
                if not self.log_queue.empty():
                    event = self.log_queue.get(timeout=0.1)
                    self._write_event_to_file(event)
                    self.log_queue.task_done()
                else:
                    time.sleep(0.01)  # Prevent busy waiting
            except Exception as e:
                logger.error(f"Error in logging thread: {e}")
    
    def _write_event_to_file(self, event: GameEvent):
        """Write event to log file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(event.to_json() + '\n')
        except Exception as e:
            logger.error(f"Failed to write event to log: {e}")
    
    def _log_session_start(self):
        """Log session initialization."""
        event = GameEvent(
            timestamp=time.time(),
            session_id=self.session_id,
            scene="system",
            event_type="session",
            event_data={
                "action": "session_start",
                "project_root": str(self.project_root),
                "log_file": str(self.log_file),
                "python_version": f"{__import__('sys').version}",
                "pygame_version": pygame.version.ver,
                "initial_memory_mb": self.initial_memory
            },
            tags=["system", "session_management"]
        )
        self._queue_event(event)
    
    def _queue_event(self, event: GameEvent):
        """Queue event for asynchronous logging."""
        start_time = time.perf_counter()
        self.log_queue.put(event)
        self.events_logged += 1
        
        # Track logging overhead
        overhead = (time.perf_counter() - start_time) * 1000
        self.logging_overhead_ms += overhead
    
    def log_scene_transition(self, from_scene: str, to_scene: str, data: Dict[str, Any] = None):
        """Log scene transition events."""
        transition_start = time.time()
        
        # Update current scene
        old_scene = self.current_scene
        self.current_scene = to_scene
        
        event_data = {
            "from_scene": from_scene,
            "to_scene": to_scene,
            "transition_time_ms": 0,  # Will be updated below
            "data": data or {}
        }
        
        # Add memory usage if available
        try:
            current_memory = self.process.memory_info().rss / 1024 / 1024
            event_data["memory_before_mb"] = current_memory
            event_data["memory_delta_mb"] = current_memory - self.initial_memory
        except Exception:
            pass
        
        # Calculate transition time
        event_data["transition_time_ms"] = (time.time() - transition_start) * 1000
        
        event = GameEvent(
            timestamp=time.time(),
            session_id=self.session_id,
            scene=to_scene,
            event_type="scene_transition",
            event_data=event_data,
            test_context=self.current_test_context,
            tags=["scene", "navigation"]
        )
        
        self._queue_event(event)
        logger.debug(f"Logged scene transition: {from_scene} -> {to_scene}")
    
    def log_player_action(self, action: str, scene: str = None, details: Dict[str, Any] = None):
        """Log player input and resulting actions."""
        scene = scene or self.current_scene
        
        event_data = {
            "action": action,
            "details": details or {},
            "input_timestamp": time.time()
        }
        
        # Add response time if this is a UI interaction
        if "response_time_ms" not in event_data and details:
            if "start_time" in details:
                event_data["response_time_ms"] = (time.time() - details["start_time"]) * 1000
        
        event = GameEvent(
            timestamp=time.time(),
            session_id=self.session_id,
            scene=scene,
            event_type="player_action",
            event_data=event_data,
            test_context=self.current_test_context,
            tags=["player", "input", action]
        )
        
        self._queue_event(event)
    
    def log_audio_event(self, audio_action: str, track: str = None, volume: float = None, details: Dict[str, Any] = None):
        """Log audio system events."""
        event_data = {
            "action": audio_action,
            "track": track,
            "volume": volume,
            "details": details or {}
        }
        
        event = GameEvent(
            timestamp=time.time(),
            session_id=self.session_id,
            scene=self.current_scene,
            event_type="audio",  
            event_data=event_data,
            test_context=self.current_test_context,
            tags=["audio", audio_action]
        )
        
        self._queue_event(event)
    
    def log_system_event(self, system: str, event: str, data: Dict[str, Any] = None):
        """Log system-level events (physics, rendering, etc.)."""
        event_data = {
            "system": system,
            "event": event,
            "data": data or {}
        }
        
        event_obj = GameEvent(
            timestamp=time.time(),
            session_id=self.session_id,
            scene=self.current_scene,
            event_type="system",
            event_data=event_data,
            test_context=self.current_test_context,
            tags=["system", system]
        )
        
        self._queue_event(event_obj)
    
    def log_performance_metric(self, metric_name: str, value: float, context: Dict[str, Any] = None):
        """Log performance measurements."""
        event_data = {
            "metric": metric_name,
            "value": value,
            "unit": self._get_metric_unit(metric_name),
            "context": context or {}
        }
        
        # Add to performance samples for trend analysis
        self.performance_samples.append({
            "timestamp": time.time(),
            "metric": metric_name,
            "value": value,
            "scene": self.current_scene
        })
        
        # Keep only last 1000 samples to prevent memory bloat
        if len(self.performance_samples) > 1000:
            self.performance_samples = self.performance_samples[-1000:]
        
        event = GameEvent(
            timestamp=time.time(),
            session_id=self.session_id,
            scene=self.current_scene,
            event_type="performance",
            event_data=event_data,
            test_context=self.current_test_context,
            tags=["performance", metric_name]
        )
        
        self._queue_event(event)
    
    def log_test_event(self, test_id: str, test_action: str, result: Any = None, evidence: Dict[str, Any] = None):
        """Log test-specific events with OQE evidence."""
        event_data = {
            "test_id": test_id,
            "action": test_action,
            "result": result,
            "evidence": evidence or {}
        }
        
        event = GameEvent(
            timestamp=time.time(),
            session_id=self.session_id,
            scene=self.current_scene,
            event_type="test",
            event_data=event_data,
            test_context=self.current_test_context,
            oqe_metrics=evidence or {},
            tags=["test", test_id, test_action]
        )
        
        self._queue_event(event)
    
    def set_test_context(self, test_issue_or_id: str, test_procedure: str = None):
        """Set current testing context for log correlation."""
        if test_procedure:
            self.current_test_context = f"{test_issue_or_id}:{test_procedure}"
        else:
            self.current_test_context = test_issue_or_id
        
        # Log context change
        self.log_system_event("testing", "context_change", {
            "test_context": self.current_test_context,
            "previous_context": getattr(self, '_previous_test_context', None)
        })
        
        self._previous_test_context = self.current_test_context
        logger.info(f"Test context set to: {self.current_test_context}")
    
    def clear_test_context(self):
        """Clear current test context."""
        old_context = self.current_test_context
        self.current_test_context = None
        
        self.log_system_event("testing", "context_cleared", {
            "cleared_context": old_context
        })
        
        logger.info("Test context cleared")
    
    def get_performance_impact(self) -> Dict[str, float]:
        """Calculate current performance impact of logging system."""
        current_time = time.time()
        session_duration = current_time - self.start_time
        
        if self.events_logged == 0:
            return {"impact_percentage": 0.0, "overhead_ms_per_event": 0.0}
        
        avg_overhead_per_event = self.logging_overhead_ms / self.events_logged
        total_overhead_seconds = self.logging_overhead_ms / 1000
        
        # Calculate as percentage of total runtime
        impact_percentage = (total_overhead_seconds / session_duration) * 100 if session_duration > 0 else 0
        
        return {
            "impact_percentage": round(impact_percentage, 3),
            "overhead_ms_per_event": round(avg_overhead_per_event, 3),
            "total_events": self.events_logged,
            "session_duration_s": round(session_duration, 2),
            "total_overhead_ms": round(self.logging_overhead_ms, 2)
        }
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get comprehensive session statistics."""
        current_memory = self.process.memory_info().rss / 1024 / 1024
        
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "current_scene": self.current_scene,
            "events_logged": self.events_logged,
            "memory_usage": {
                "initial_mb": self.initial_memory,
                "current_mb": current_memory,
                "delta_mb": current_memory - self.initial_memory
            },
            "performance_impact": self.get_performance_impact(),
            "log_file_size_kb": self._get_log_file_size(),
            "queue_size": self.log_queue.qsize()
        }
    
    def _get_metric_unit(self, metric_name: str) -> str:
        """Get appropriate unit for metric."""
        unit_map = {
            "fps": "frames_per_second",
            "frame_time": "milliseconds",
            "memory": "megabytes",
            "cpu": "percent",
            "response_time": "milliseconds",
            "load_time": "milliseconds"
        }
        
        for key, unit in unit_map.items():
            if key in metric_name.lower():
                return unit
        
        return "units"
    
    def _get_log_file_size(self) -> float:
        """Get current log file size in KB."""
        try:
            return os.path.getsize(self.log_file) / 1024
        except Exception:
            return 0.0
    
    def _cleanup_old_logs(self):
        """Remove old log files to prevent disk bloat."""
        try:
            log_files = list(self.logs_dir.glob("game_session_*.jsonl"))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the 5 most recent log files
            for old_file in log_files[5:]:
                old_file.unlink()
                logger.info(f"Cleaned up old log file: {old_file.name}")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup old logs: {e}")
    
    def export_session_summary(self) -> Dict[str, Any]:
        """Export comprehensive session summary for analysis."""
        stats = self.get_session_stats()
        
        # Add performance trend analysis
        if self.performance_samples:
            fps_samples = [s for s in self.performance_samples if s["metric"] == "fps"]
            if fps_samples:
                fps_values = [s["value"] for s in fps_samples]
                stats["performance_trends"] = {
                    "avg_fps": sum(fps_values) / len(fps_values),
                    "min_fps": min(fps_values),
                    "max_fps": max(fps_values),
                    "fps_stability": self._calculate_stability(fps_values)
                }
        
        return stats
    
    def _calculate_stability(self, values: List[float]) -> float:
        """Calculate stability score (lower variance = higher stability)."""
        if len(values) < 2:
            return 100.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        coefficient_of_variation = (variance ** 0.5) / mean if mean > 0 else 0
        
        # Convert to stability score (0-100, higher is more stable)
        return max(0, 100 - (coefficient_of_variation * 100))
    
    def shutdown(self):
        """Gracefully shutdown the logging system."""
        logger.info("Shutting down GameStateLogger...")
        
        # Log session end
        self.log_system_event("session", "session_end", {
            "session_stats": self.export_session_summary(),
            "shutdown_reason": "normal"
        })
        
        # Wait for queue to empty
        self.log_queue.join()
        
        # Signal shutdown to thread
        self.shutdown_requested = True
        
        # Wait for thread to finish
        if self.logging_thread and self.logging_thread.is_alive():
            self.logging_thread.join(timeout=2.0)
        
        logger.info(f"GameStateLogger shutdown complete. Session: {self.session_id}")
    
    def __del__(self):
        """Ensure proper cleanup on object destruction."""
        if hasattr(self, 'shutdown_requested') and not self.shutdown_requested:
            self.shutdown()


# Global logger instance (initialized by game)
_global_logger: Optional[GameStateLogger] = None


def initialize_global_logger(project_root: str, enable_live_overlay: bool = True) -> GameStateLogger:
    """Initialize the global game state logger."""
    global _global_logger
    if _global_logger is None:
        _global_logger = GameStateLogger(project_root, enable_live_overlay)
    return _global_logger


def get_global_logger() -> Optional[GameStateLogger]:
    """Get the global game state logger instance."""
    return _global_logger


def shutdown_global_logger():
    """Shutdown the global logger."""
    global _global_logger
    if _global_logger:
        _global_logger.shutdown()
        _global_logger = None