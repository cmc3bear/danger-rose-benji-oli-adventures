"""Performance monitoring for the audio system."""

import time
from typing import Dict, List, Any
from collections import deque
from .channel_manager import SoundCategory
from .priority_system import SoundPriority


class AudioPerformanceMonitor:
    """Monitors audio system performance and provides metrics."""
    
    def __init__(self, history_size: int = 300):
        """Initialize the performance monitor.
        
        Args:
            history_size: Number of frames to keep in history (5 seconds at 60 FPS)
        """
        self.history_size = history_size
        
        # Performance metrics
        self.sounds_played_per_second = 0
        self.memory_usage_mb = 0.0
        self.channel_utilization = 0.0
        self.cache_hit_rate = 0.0
        self.average_latency_ms = 0.0
        
        # Historical data for trend analysis
        self.sounds_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        self.channel_history = deque(maxlen=history_size)
        self.latency_history = deque(maxlen=history_size)
        
        # Counters
        self.total_sounds_played = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.sounds_this_second = 0
        self.last_second_time = time.time()
        
        # Category tracking
        self.category_usage = {category: 0 for category in SoundCategory}
        self.priority_usage = {priority: 0 for priority in SoundPriority}
        
        # Performance thresholds
        self.max_sounds_per_second = 30
        self.max_memory_mb = 100
        self.max_channel_utilization = 0.8
        self.target_latency_ms = 20.0
        
        # Warning flags
        self.performance_warnings = []
    
    def record_sound_played(self, category: SoundCategory, priority: SoundPriority):
        """Record that a sound was played.
        
        Args:
            category: Category of the sound
            priority: Priority of the sound
        """
        self.total_sounds_played += 1
        self.sounds_this_second += 1
        
        # Track category and priority usage
        self.category_usage[category] += 1
        self.priority_usage[priority] += 1
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.cache_misses += 1
    
    def record_music_change(self):
        """Record a music change event."""
        # Could track music changes for optimization
        pass
    
    def update(self, dt: float):
        """Update performance metrics (call once per frame).
        
        Args:
            dt: Delta time since last update
        """
        current_time = time.time()
        
        # Update sounds per second
        if current_time - self.last_second_time >= 1.0:
            self.sounds_played_per_second = self.sounds_this_second
            self.sounds_history.append(self.sounds_this_second)
            self.sounds_this_second = 0
            self.last_second_time = current_time
        
        # Calculate cache hit rate
        total_requests = self.cache_hits + self.cache_misses
        if total_requests > 0:
            self.cache_hit_rate = self.cache_hits / total_requests
        
        # Add current metrics to history
        self.memory_history.append(self.memory_usage_mb)
        self.channel_history.append(self.channel_utilization)
        self.latency_history.append(self.average_latency_ms)
        
        # Check for performance issues
        self._check_performance_warnings()
    
    def set_memory_usage(self, memory_mb: float):
        """Set current memory usage.
        
        Args:
            memory_mb: Memory usage in megabytes
        """
        self.memory_usage_mb = memory_mb
    
    def set_channel_utilization(self, utilization: float):
        """Set current channel utilization.
        
        Args:
            utilization: Channel utilization (0.0-1.0)
        """
        self.channel_utilization = utilization
    
    def set_average_latency(self, latency_ms: float):
        """Set average audio latency.
        
        Args:
            latency_ms: Latency in milliseconds
        """
        self.average_latency_ms = latency_ms
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            "sounds_per_second": self.sounds_played_per_second,
            "memory_usage_mb": self.memory_usage_mb,
            "channel_utilization": self.channel_utilization,
            "cache_hit_rate": self.cache_hit_rate,
            "average_latency_ms": self.average_latency_ms,
            "total_sounds_played": self.total_sounds_played,
            "performance_warnings": len(self.performance_warnings),
            "category_usage": {cat.value: count for cat, count in self.category_usage.items()},
            "priority_usage": {pri.value: count for pri, count in self.priority_usage.items()}
        }
    
    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics with history.
        
        Returns:
            Dictionary with detailed metrics
        """
        metrics = self.get_metrics()
        
        # Add historical data
        metrics.update({
            "sounds_history": list(self.sounds_history),
            "memory_history": list(self.memory_history),
            "channel_history": list(self.channel_history),
            "latency_history": list(self.latency_history),
            "active_warnings": self.performance_warnings.copy()
        })
        
        # Add trend analysis
        if len(self.sounds_history) > 10:
            recent_sounds = list(self.sounds_history)[-10:]
            metrics["sounds_trend"] = sum(recent_sounds) / len(recent_sounds)
        
        if len(self.memory_history) > 10:
            recent_memory = list(self.memory_history)[-10:]
            metrics["memory_trend"] = sum(recent_memory) / len(recent_memory)
        
        return metrics
    
    def should_reduce_quality(self) -> bool:
        """Determine if audio quality should be reduced for performance.
        
        Returns:
            True if quality should be reduced
        """
        # Check multiple performance indicators
        performance_issues = 0
        
        if self.sounds_played_per_second > self.max_sounds_per_second:
            performance_issues += 1
        
        if self.memory_usage_mb > self.max_memory_mb:
            performance_issues += 1
        
        if self.channel_utilization > self.max_channel_utilization:
            performance_issues += 1
        
        if self.average_latency_ms > self.target_latency_ms * 2:
            performance_issues += 1
        
        # Reduce quality if multiple issues detected
        return performance_issues >= 2
    
    def get_optimization_suggestions(self) -> List[str]:
        """Get suggestions for optimizing audio performance.
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        if self.sounds_played_per_second > self.max_sounds_per_second:
            suggestions.append("Consider reducing maximum sounds per frame")
        
        if self.memory_usage_mb > self.max_memory_mb:
            suggestions.append("Reduce sound cache size or compress audio files")
        
        if self.channel_utilization > self.max_channel_utilization:
            suggestions.append("Increase channel preemption or reduce concurrent sounds")
        
        if self.cache_hit_rate < 0.8:
            suggestions.append("Preload frequently used sounds")
        
        if self.average_latency_ms > self.target_latency_ms:
            suggestions.append("Reduce audio buffer size or compress files")
        
        # Category-specific suggestions
        max_category = max(self.category_usage.items(), key=lambda x: x[1])
        if max_category[1] > 100:
            suggestions.append(f"Consider limiting {max_category[0].value} category sounds")
        
        return suggestions
    
    def reset_metrics(self):
        """Reset all performance metrics."""
        self.total_sounds_played = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.sounds_this_second = 0
        
        # Reset category usage
        self.category_usage = {category: 0 for category in SoundCategory}
        self.priority_usage = {priority: 0 for priority in SoundPriority}
        
        # Clear warnings
        self.performance_warnings.clear()
    
    def _check_performance_warnings(self):
        """Check for performance warnings and update the list."""
        current_warnings = []
        
        if self.sounds_played_per_second > self.max_sounds_per_second:
            current_warnings.append(f"High sound rate: {self.sounds_played_per_second}/s")
        
        if self.memory_usage_mb > self.max_memory_mb:
            current_warnings.append(f"High memory usage: {self.memory_usage_mb:.1f}MB")
        
        if self.channel_utilization > self.max_channel_utilization:
            current_warnings.append(f"High channel usage: {self.channel_utilization*100:.1f}%")
        
        if self.average_latency_ms > self.target_latency_ms * 1.5:
            current_warnings.append(f"High latency: {self.average_latency_ms:.1f}ms")
        
        if self.cache_hit_rate < 0.6 and (self.cache_hits + self.cache_misses) > 50:
            current_warnings.append(f"Low cache hit rate: {self.cache_hit_rate*100:.1f}%")
        
        # Only update if warnings changed
        if current_warnings != self.performance_warnings:
            self.performance_warnings = current_warnings
    
    def get_performance_score(self) -> float:
        """Get overall performance score (0.0-1.0, higher is better).
        
        Returns:
            Performance score between 0.0 and 1.0
        """
        score = 1.0
        
        # Deduct points for performance issues
        if self.sounds_played_per_second > self.max_sounds_per_second:
            score -= 0.2
        
        if self.memory_usage_mb > self.max_memory_mb:
            score -= 0.2
        
        if self.channel_utilization > self.max_channel_utilization:
            score -= 0.2
        
        if self.average_latency_ms > self.target_latency_ms:
            score -= 0.2
        
        if self.cache_hit_rate < 0.8:
            score -= 0.2
        
        return max(0.0, score)