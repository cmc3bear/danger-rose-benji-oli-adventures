"""Event system for rhythm-based game events and notifications."""

import time
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .bpm_tracker import BeatEvent


class EventPriority(Enum):
    """Priority levels for rhythm events."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class QuantizationMode(Enum):
    """Different modes for quantizing actions to beats."""
    NONE = "none"           # No quantization
    NEAREST = "nearest"     # Snap to nearest beat
    NEXT = "next"          # Wait for next beat
    STRONG_ONLY = "strong" # Only snap to strong beats
    DOWNBEAT_ONLY = "downbeat"  # Only snap to downbeats


@dataclass
class RhythmEvent:
    """A rhythm-based game event."""
    event_type: str         # Type of event ("spawn", "boost", "action", etc.)
    target_time: float      # When the event should occur
    data: Dict[str, Any]    # Event-specific data
    priority: EventPriority # Event priority
    callback: Optional[Callable] = None  # Optional callback when event fires
    is_quantized: bool = False  # Whether this event was quantized to a beat
    original_time: Optional[float] = None  # Original time before quantization


@dataclass
class ActionRequest:
    """Request to perform an action with rhythm quantization."""
    action_type: str        # Type of action
    requested_time: float   # When action was requested
    quantization: QuantizationMode  # How to quantize
    tolerance: float = 0.1  # Time tolerance for quantization
    data: Dict[str, Any] = None  # Action data
    callback: Optional[Callable] = None  # Callback when action executes


class RhythmEventSystem:
    """
    Event system that handles rhythm-based timing and quantization.
    
    Features:
    - Event scheduling with beat quantization
    - Priority-based event ordering
    - Action buffering and timing
    - Off-beat action handling
    - Performance monitoring
    """
    
    def __init__(self, bpm_tracker):
        """
        Initialize the rhythm event system.
        
        Args:
            bmp_tracker: BPMTracker instance for timing
        """
        self.bpm_tracker = bmp_tracker
        
        # Event queues
        self.pending_events: List[RhythmEvent] = []
        self.action_buffer: List[ActionRequest] = []
        
        # Event handlers by type
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Quantization settings
        self.global_quantization = QuantizationMode.NEAREST
        self.quantization_tolerance = 0.05  # 50ms default tolerance
        
        # Performance tracking
        self.events_processed = 0
        self.events_quantized = 0
        self.average_quantization_offset = 0.0
        self.timing_accuracy_history = []
        
        # Register for beat events
        self.bpm_tracker.register_beat_callback(self._on_beat_event)
        
    def schedule_event(self, 
                      event_type: str, 
                      delay: float = 0.0, 
                      data: Dict[str, Any] = None,
                      priority: EventPriority = EventPriority.NORMAL,
                      quantize: bool = True,
                      quantization_mode: QuantizationMode = None) -> RhythmEvent:
        """
        Schedule a rhythm event.
        
        Args:
            event_type: Type of event to schedule
            delay: Delay in seconds from now
            data: Event data
            priority: Event priority
            quantize: Whether to quantize to beat
            quantization_mode: How to quantize (uses global if None)
            
        Returns:
            Created RhythmEvent
        """
        current_time = time.time()
        target_time = current_time + delay
        original_time = target_time
        
        # Apply quantization if requested
        if quantize and self.bmp_tracker.is_tracking:
            if quantization_mode is None:
                quantization_mode = self.global_quantization
                
            target_time = self._quantize_time(target_time, quantization_mode)
            
        event = RhythmEvent(
            event_type=event_type,
            target_time=target_time,
            data=data or {},
            priority=priority,
            is_quantized=quantize,
            original_time=original_time if quantize else None
        )
        
        # Insert event in priority order
        self._insert_event_by_priority(event)
        
        if quantize:
            self.events_quantized += 1
            offset = abs(target_time - original_time)
            self._update_quantization_stats(offset)
            
        return event
        
    def request_action(self,
                      action_type: str,
                      quantization: QuantizationMode = None,
                      tolerance: float = None,
                      data: Dict[str, Any] = None,
                      callback: Callable = None) -> bool:
        """
        Request an action with rhythm quantization.
        
        Args:
            action_type: Type of action to perform
            quantization: How to quantize the action
            tolerance: Time tolerance for execution
            data: Action data
            callback: Callback when action executes
            
        Returns:
            True if action was scheduled, False if rejected
        """
        if quantization is None:
            quantization = self.global_quantization
        if tolerance is None:
            tolerance = self.quantization_tolerance
            
        current_time = time.time()
        
        # Handle immediate actions (no quantization)
        if quantization == QuantizationMode.NONE:
            self._execute_action(action_type, current_time, data, callback)
            return True
            
        # Check if we're already on beat (within tolerance)
        if self.bpm_tracker.is_on_beat(tolerance):
            self._execute_action(action_type, current_time, data, callback)
            return True
            
        # Buffer the action for quantization
        action_request = ActionRequest(
            action_type=action_type,
            requested_time=current_time,
            quantization=quantization,
            tolerance=tolerance,
            data=data or {},
            callback=callback
        )
        
        self.action_buffer.append(action_request)
        return True
        
    def update(self, dt: float):
        """
        Update the event system.
        
        Args:
            dt: Delta time in seconds
        """
        current_time = time.time()
        
        # Process pending events
        self._process_pending_events(current_time)
        
        # Process action buffer
        self._process_action_buffer(current_time)
        
        # Clean up old requests
        self._cleanup_old_requests(current_time)
        
    def _on_beat_event(self, beat_event: BeatEvent):
        """Handle beat events for action quantization."""
        # Process buffered actions that should execute on this beat
        actions_to_execute = []
        
        for i, action in enumerate(self.action_buffer):
            if self._should_execute_on_beat(action, beat_event):
                actions_to_execute.append((i, action))
                
        # Execute actions (reverse order to maintain indices)
        for i, action in reversed(actions_to_execute):
            self._execute_action(
                action.action_type,
                beat_event.timestamp,
                action.data,
                action.callback
            )
            del self.action_buffer[i]
            
    def _should_execute_on_beat(self, action: ActionRequest, beat_event: BeatEvent) -> bool:
        """Check if an action should execute on a specific beat."""
        if action.quantization == QuantizationMode.NEXT:
            return True  # Execute on next available beat
        elif action.quantization == QuantizationMode.STRONG_ONLY:
            return beat_event.strength in [BeatStrength.STRONG, BeatStrength.DOWNBEAT, BeatStrength.ACCENT]
        elif action.quantization == QuantizationMode.DOWNBEAT_ONLY:
            return beat_event.strength == BeatStrength.DOWNBEAT
        elif action.quantization == QuantizationMode.NEAREST:
            # Check if this is the nearest beat to the requested time
            time_diff = abs(beat_event.timestamp - action.requested_time)
            return time_diff <= action.tolerance
        else:
            return False
            
    def _quantize_time(self, target_time: float, mode: QuantizationMode) -> float:
        """Quantize a target time to the nearest appropriate beat."""
        if not self.bpm_tracker.is_tracking:
            return target_time
            
        if mode == QuantizationMode.NONE:
            return target_time
        elif mode == QuantizationMode.NEAREST:
            return self.bpm_tracker.quantize_to_beat(target_time)
        elif mode == QuantizationMode.NEXT:
            # Find next beat after target time
            predicted_beats = self.bmp_tracker.get_predicted_beats(2.0)
            for beat in predicted_beats:
                if beat.timestamp > target_time:
                    return beat.timestamp
            return target_time  # Fallback
        elif mode == QuantizationMode.STRONG_ONLY:
            # Find next strong beat
            predicted_beats = self.bpm_tracker.get_predicted_beats(4.0)
            for beat in predicted_beats:
                if (beat.timestamp > target_time and 
                    beat.strength in [BeatStrength.STRONG, BeatStrength.DOWNBEAT, BeatStrength.ACCENT]):
                    return beat.timestamp
            return target_time  # Fallback
        elif mode == QuantizationMode.DOWNBEAT_ONLY:
            # Find next downbeat
            predicted_beats = self.bpm_tracker.get_predicted_beats(8.0)
            for beat in predicted_beats:
                if beat.timestamp > target_time and beat.strength == BeatStrength.DOWNBEAT:
                    return beat.timestamp
            return target_time  # Fallback
        else:
            return target_time
            
    def _insert_event_by_priority(self, event: RhythmEvent):
        """Insert event in priority order."""
        inserted = False
        for i, existing_event in enumerate(self.pending_events):
            if (event.priority.value > existing_event.priority.value or
                (event.priority.value == existing_event.priority.value and 
                 event.target_time < existing_event.target_time)):
                self.pending_events.insert(i, event)
                inserted = True
                break
                
        if not inserted:
            self.pending_events.append(event)
            
    def _process_pending_events(self, current_time: float):
        """Process events that are ready to execute."""
        events_to_remove = []
        
        for i, event in enumerate(self.pending_events):
            if current_time >= event.target_time:
                self._execute_event(event)
                events_to_remove.append(i)
                
        # Remove processed events
        for i in reversed(events_to_remove):
            del self.pending_events[i]
            
    def _process_action_buffer(self, current_time: float):
        """Process buffered actions that may have timed out."""
        actions_to_remove = []
        
        for i, action in enumerate(self.action_buffer):
            # Remove actions that are too old
            if current_time - action.requested_time > 2.0:  # 2 second timeout
                actions_to_remove.append(i)
                
        # Remove timed out actions
        for i in reversed(actions_to_remove):
            del self.action_buffer[i]
            
    def _execute_event(self, event: RhythmEvent):
        """Execute a rhythm event."""
        self.events_processed += 1
        
        # Call registered handlers
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")
                    
        # Call event-specific callback
        if event.callback:
            try:
                event.callback(event)
            except Exception as e:
                print(f"Error in event callback: {e}")
                
    def _execute_action(self, action_type: str, timestamp: float, data: Dict[str, Any], callback: Callable):
        """Execute an action."""
        # Create and execute an immediate event
        event = RhythmEvent(
            event_type=action_type,
            target_time=timestamp,
            data=data,
            priority=EventPriority.HIGH,
            callback=callback
        )
        
        self._execute_event(event)
        
    def _cleanup_old_requests(self, current_time: float):
        """Clean up old requests and events."""
        # Remove very old events that somehow didn't get processed
        self.pending_events = [
            event for event in self.pending_events
            if current_time - event.target_time < 5.0
        ]
        
    def _update_quantization_stats(self, offset: float):
        """Update quantization performance statistics."""
        self.timing_accuracy_history.append(offset)
        
        # Keep last 100 measurements
        if len(self.timing_accuracy_history) > 100:
            self.timing_accuracy_history = self.timing_accuracy_history[-100:]
            
        # Update average
        self.average_quantization_offset = sum(self.timing_accuracy_history) / len(self.timing_accuracy_history)
        
    def register_handler(self, event_type: str, handler: Callable[[RhythmEvent], None]):
        """Register an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        if handler not in self.event_handlers[event_type]:
            self.event_handlers[event_type].append(handler)
            
    def unregister_handler(self, event_type: str, handler: Callable[[RhythmEvent], None]):
        """Unregister an event handler."""
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            
    def set_quantization_mode(self, mode: QuantizationMode):
        """Set global quantization mode."""
        self.global_quantization = mode
        
    def set_quantization_tolerance(self, tolerance: float):
        """Set quantization tolerance in seconds."""
        self.quantization_tolerance = max(0.01, min(0.5, tolerance))
        
    def get_stats(self) -> Dict[str, Any]:
        """Get event system statistics."""
        return {
            "events_processed": self.events_processed,
            "events_quantized": self.events_quantized,
            "pending_events": len(self.pending_events),
            "buffered_actions": len(self.action_buffer),
            "average_quantization_offset": self.average_quantization_offset,
            "quantization_accuracy": 1.0 - min(1.0, self.average_quantization_offset / 0.1),  # Normalized accuracy
            "global_quantization": self.global_quantization.value,
            "quantization_tolerance": self.quantization_tolerance
        }