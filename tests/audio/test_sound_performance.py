"""Performance testing for sound effects system."""

import time
import threading
from unittest.mock import Mock, patch
import psutil
import pytest

from src.managers.sound_manager import SoundManager


class TestSoundPerformance:
    """Performance benchmarks and stress tests for sound system."""

    @pytest.fixture
    def performance_sound_manager(self):
        """Create sound manager for performance testing."""
        SoundManager._instance = None
        with patch("pygame.mixer.init"):
            with patch("pygame.mixer.get_init", return_value=(44100, -16, 2, 512)):
                sm = SoundManager()
                yield sm

    def test_sound_loading_performance(self, performance_sound_manager):
        """Benchmark sound loading times under various conditions."""
        sm = performance_sound_manager
        
        with patch("os.path.exists", return_value=True):
            with patch("pygame.mixer.Sound") as mock_sound:
                mock_sound_obj = Mock()
                mock_sound.return_value = mock_sound_obj
                
                # Test single sound loading time
                start_time = time.perf_counter()
                sm.play_sfx("test_sound.ogg")
                single_load_time = time.perf_counter() - start_time
                
                assert single_load_time < 0.001, f"Single sound load too slow: {single_load_time:.4f}s"
                
                # Test batch loading performance
                start_time = time.perf_counter()
                for i in range(100):
                    sm.preload_sound(f"batch_sound_{i}.ogg")
                batch_load_time = time.perf_counter() - start_time
                
                assert batch_load_time < 0.1, f"Batch loading too slow: {batch_load_time:.3f}s"

    def test_concurrent_playback_performance(self, performance_sound_manager):
        """Test performance with multiple simultaneous sound effects."""
        sm = performance_sound_manager
        
        with patch("pygame.mixer.find_channel") as mock_find:
            mock_channels = [Mock() for _ in range(8)]
            mock_find.side_effect = lambda: mock_channels[mock_find.call_count % 8]
            
            with patch("os.path.exists", return_value=True):
                with patch("pygame.mixer.Sound"):
                    # Test playing maximum concurrent sounds
                    start_time = time.perf_counter()
                    for i in range(8):
                        sm.play_sfx(f"concurrent_sound_{i}.ogg")
                    concurrent_time = time.perf_counter() - start_time
                    
                    assert concurrent_time < 0.01, f"Concurrent playback too slow: {concurrent_time:.4f}s"

    def test_memory_usage_under_load(self, performance_sound_manager):
        """Test memory usage during heavy sound operations."""
        sm = performance_sound_manager
        
        # Get baseline memory usage
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch("os.path.exists", return_value=True):
            with patch("pygame.mixer.Sound") as mock_sound:
                # Create mock sound objects that simulate memory usage
                mock_sound_obj = Mock()
                mock_sound_obj.get_length.return_value = 2.0  # 2-second sound
                mock_sound.return_value = mock_sound_obj
                
                # Load many sounds to test memory scaling
                for i in range(200):
                    sm.preload_sound(f"memory_test_sound_{i}.ogg")
                
                # Check memory usage after loading
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - baseline_memory
                
                # Should not use excessive memory (allow 100MB for 200 sounds)
                assert memory_increase < 100, f"Memory usage too high: {memory_increase:.1f}MB"

    def test_cpu_usage_monitoring(self, performance_sound_manager):
        """Monitor CPU usage during sound operations."""
        sm = performance_sound_manager
        
        # Monitor CPU usage during operations
        def cpu_intensive_sound_operations():
            with patch("os.path.exists", return_value=True):
                with patch("pygame.mixer.Sound"):
                    with patch("pygame.mixer.find_channel", return_value=Mock()):
                        for i in range(1000):
                            sm.play_sfx(f"cpu_test_sound_{i % 10}.ogg")
                            sm.set_master_volume(0.5 + (i % 100) / 200)
        
        # Measure CPU usage
        start_cpu = psutil.cpu_percent(interval=None)
        start_time = time.perf_counter()
        
        cpu_intensive_sound_operations()
        
        end_time = time.perf_counter()
        end_cpu = psutil.cpu_percent(interval=None)
        
        operation_time = end_time - start_time
        
        # Operations should complete quickly
        assert operation_time < 0.1, f"CPU-intensive operations too slow: {operation_time:.3f}s"

    def test_audio_latency_measurement(self, performance_sound_manager):
        """Test audio system latency for real-time gaming."""
        sm = performance_sound_manager
        
        with patch("pygame.mixer.find_channel") as mock_find:
            mock_channel = Mock()
            mock_find.return_value = mock_channel
            
            with patch("os.path.exists", return_value=True):
                with patch("pygame.mixer.Sound"):
                    # Measure time from play_sfx call to channel.play call
                    latencies = []
                    
                    for _ in range(10):
                        start_time = time.perf_counter()
                        sm.play_sfx("latency_test.ogg")
                        end_time = time.perf_counter()
                        latencies.append(end_time - start_time)
                    
                    avg_latency = sum(latencies) / len(latencies)
                    max_latency = max(latencies)
                    
                    # Audio latency should be minimal for gaming
                    assert avg_latency < 0.001, f"Average latency too high: {avg_latency:.4f}s"
                    assert max_latency < 0.002, f"Maximum latency too high: {max_latency:.4f}s"

    def test_cache_performance_scaling(self, performance_sound_manager):
        """Test sound cache performance with increasing size."""
        sm = performance_sound_manager
        
        with patch("os.path.exists", return_value=True):
            with patch("pygame.mixer.Sound") as mock_sound:
                mock_sound.return_value = Mock()
                
                # Test cache lookup performance at different sizes
                cache_sizes = [10, 50, 100, 200]
                lookup_times = []
                
                for cache_size in cache_sizes:
                    # Fill cache to target size
                    sm.clear_cache()
                    for i in range(cache_size):
                        sm.preload_sound(f"cache_test_{i}.ogg")
                    
                    # Measure cache lookup time
                    start_time = time.perf_counter()
                    for _ in range(100):
                        # Lookup existing cached sound
                        sound_key = f"cache_test_{cache_size // 2}.ogg"
                        _ = sm.sfx_cache.get(sound_key)
                    lookup_time = time.perf_counter() - start_time
                    lookup_times.append(lookup_time)
                
                # Cache lookup should not degrade significantly with size
                for i in range(1, len(lookup_times)):
                    ratio = lookup_times[i] / lookup_times[0]
                    assert ratio < 2.0, f"Cache lookup degraded too much at size {cache_sizes[i]}: {ratio:.2f}x slower"

    def test_threading_performance(self, performance_sound_manager):
        """Test sound system performance with multiple threads."""
        sm = performance_sound_manager
        
        results = []
        errors = []
        
        def thread_sound_operations(thread_id):
            try:
                with patch("os.path.exists", return_value=True):
                    with patch("pygame.mixer.Sound"):
                        with patch("pygame.mixer.find_channel", return_value=Mock()):
                            start_time = time.perf_counter()
                            
                            for i in range(50):
                                sm.play_sfx(f"thread_{thread_id}_sound_{i}.ogg")
                                sm.set_master_volume(0.5)
                            
                            end_time = time.perf_counter()
                            results.append(end_time - start_time)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(4):
            thread = threading.Thread(target=thread_sound_operations, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Threading errors: {errors}"
        
        # Verify all threads completed in reasonable time
        assert len(results) == 4, "All threads should complete"
        max_thread_time = max(results)
        assert max_thread_time < 0.1, f"Thread operations too slow: {max_thread_time:.3f}s"

    def test_garbage_collection_impact(self, performance_sound_manager):
        """Test impact of garbage collection on sound performance."""
        sm = performance_sound_manager
        
        import gc
        
        with patch("os.path.exists", return_value=True):
            with patch("pygame.mixer.Sound") as mock_sound:
                mock_sound.return_value = Mock()
                
                # Create and destroy many sound references
                for cycle in range(5):
                    # Create temporary sound cache
                    temp_sounds = []
                    for i in range(100):
                        sound_file = f"gc_test_{cycle}_{i}.ogg"
                        sm.preload_sound(sound_file)
                        temp_sounds.append(sound_file)
                    
                    # Measure performance before GC
                    start_time = time.perf_counter()
                    sm.play_sfx(temp_sounds[0])
                    pre_gc_time = time.perf_counter() - start_time
                    
                    # Force garbage collection
                    sm.clear_cache()
                    gc.collect()
                    
                    # Measure performance after GC
                    sm.preload_sound(temp_sounds[0])
                    start_time = time.perf_counter()
                    sm.play_sfx(temp_sounds[0])
                    post_gc_time = time.perf_counter() - start_time
                    
                    # Performance should not degrade significantly after GC
                    if pre_gc_time > 0:
                        ratio = post_gc_time / pre_gc_time
                        assert ratio < 3.0, f"Performance degraded too much after GC: {ratio:.2f}x slower"


class TestSoundStressTesting:
    """Stress tests to verify system stability under extreme conditions."""

    @pytest.fixture
    def stress_sound_manager(self):
        """Create sound manager for stress testing."""
        SoundManager._instance = None
        with patch("pygame.mixer.init"):
            with patch("pygame.mixer.get_init", return_value=(44100, -16, 2, 512)):
                sm = SoundManager()
                yield sm

    def test_rapid_fire_sound_playback(self, stress_sound_manager):
        """Test system stability with rapid sound playback."""
        sm = stress_sound_manager
        
        with patch("pygame.mixer.find_channel") as mock_find:
            mock_channels = [Mock() for _ in range(8)]
            mock_find.side_effect = lambda: mock_channels[mock_find.call_count % 8]
            
            with patch("os.path.exists", return_value=True):
                with patch("pygame.mixer.Sound"):
                    # Play sounds as fast as possible
                    start_time = time.perf_counter()
                    for i in range(1000):
                        sm.play_sfx(f"rapid_fire_{i % 10}.ogg")
                    
                    end_time = time.perf_counter()
                    total_time = end_time - start_time
                    
                    # Should handle 1000 rapid plays without crashing
                    assert total_time < 1.0, f"Rapid fire playback too slow: {total_time:.3f}s"

    def test_volume_change_stress(self, stress_sound_manager):
        """Test system stability with rapid volume changes."""
        sm = stress_sound_manager
        
        # Rapidly change volumes
        start_time = time.perf_counter()
        for i in range(10000):
            volume = (i % 100) / 100.0
            sm.set_master_volume(volume)
            sm.set_music_volume(volume * 0.8)
            sm.set_sfx_volume(volume * 0.9)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Should handle rapid volume changes
        assert total_time < 0.1, f"Volume change stress test too slow: {total_time:.3f}s"

    def test_cache_overflow_handling(self, stress_sound_manager):
        """Test system behavior when cache grows very large."""
        sm = stress_sound_manager
        
        with patch("os.path.exists", return_value=True):
            with patch("pygame.mixer.Sound") as mock_sound:
                mock_sound.return_value = Mock()
                
                # Load an excessive number of sounds
                for i in range(1000):
                    sm.preload_sound(f"overflow_test_{i}.ogg")
                
                # System should still function
                assert len(sm.sfx_cache) == 1000
                
                # Should still be able to play sounds
                with patch("pygame.mixer.find_channel", return_value=Mock()):
                    result = sm.play_sfx("overflow_test_500.ogg")
                    assert result is not None

    def test_error_recovery_stress(self, stress_sound_manager):
        """Test system recovery from various error conditions."""
        sm = stress_sound_manager
        
        # Test recovery from file not found errors
        for i in range(100):
            with patch("os.path.exists", return_value=False):
                result = sm.play_sfx(f"missing_file_{i}.ogg")
                assert result is None  # Should handle gracefully
        
        # Test recovery from pygame errors
        with patch("pygame.mixer.Sound", side_effect=Exception("Test error")):
            with patch("os.path.exists", return_value=True):
                for i in range(50):
                    result = sm.play_sfx(f"error_file_{i}.ogg")
                    assert result is None  # Should handle gracefully
        
        # System should still work after errors
        with patch("os.path.exists", return_value=True):
            with patch("pygame.mixer.Sound") as mock_sound:
                with patch("pygame.mixer.find_channel", return_value=Mock()):
                    mock_sound.return_value = Mock()
                    result = sm.play_sfx("recovery_test.ogg")
                    assert result is not None  # Should work after recovery

    def test_long_running_stability(self, stress_sound_manager):
        """Test system stability over extended periods."""
        sm = stress_sound_manager
        
        with patch("os.path.exists", return_value=True):
            with patch("pygame.mixer.Sound") as mock_sound:
                with patch("pygame.mixer.find_channel") as mock_find:
                    mock_sound.return_value = Mock()
                    mock_find.return_value = Mock()
                    
                    # Simulate extended gameplay session
                    for minute in range(10):  # Simulate 10 minutes
                        for second in range(60):  # 60 seconds per minute
                            # Simulate typical sound activity per second
                            if second % 5 == 0:  # Sound effect every 5 seconds
                                sm.play_sfx(f"gameplay_sound_{second % 10}.ogg")
                            
                            if second % 30 == 0:  # Volume change every 30 seconds
                                sm.set_master_volume(0.5 + (second % 20) / 40)
                    
                    # System should still be responsive
                    start_time = time.perf_counter()
                    sm.play_sfx("responsiveness_test.ogg")
                    response_time = time.perf_counter() - start_time
                    
                    assert response_time < 0.001, f"System became unresponsive: {response_time:.4f}s"