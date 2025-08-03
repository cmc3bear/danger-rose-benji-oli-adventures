"""
Test script to run the game with system monitoring
Watches for potential issues that could cause system-wide problems
"""

import sys
import os
import pygame
import time
import psutil
import threading
import signal

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class SystemMonitor:
    """Monitor system resources during game execution"""
    
    def __init__(self):
        self.monitoring = True
        self.start_time = time.time()
        self.log_interval = 5  # seconds
        self.max_cpu_percent = 0
        self.max_memory_mb = 0
        self.keyboard_events = 0
        self.warnings = []
        
    def start_monitoring(self):
        """Start system monitoring in background thread"""
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        last_log = time.time()
        
        while self.monitoring:
            try:
                # Get current process
                process = psutil.Process()
                
                # Monitor CPU usage
                cpu_percent = process.cpu_percent()
                self.max_cpu_percent = max(self.max_cpu_percent, cpu_percent)
                
                # Monitor memory usage
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                self.max_memory_mb = max(self.max_memory_mb, memory_mb)
                
                # Monitor system-wide resources
                system_cpu = psutil.cpu_percent()
                system_mem = psutil.virtual_memory().percent
                
                # Check for concerning patterns
                if cpu_percent > 50:
                    self.warnings.append(f"High process CPU: {cpu_percent:.1f}%")
                    
                if system_cpu > 90:
                    self.warnings.append(f"High system CPU: {system_cpu:.1f}%")
                    
                if memory_mb > 500:
                    self.warnings.append(f"High memory usage: {memory_mb:.1f}MB")
                
                # Log periodically
                if time.time() - last_log >= self.log_interval:
                    elapsed = time.time() - self.start_time
                    print(f"[Monitor {elapsed:.0f}s] Process: {cpu_percent:.1f}% CPU, {memory_mb:.1f}MB RAM | System: {system_cpu:.1f}% CPU, {system_mem:.1f}% RAM")
                    last_log = time.time()
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(1)
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        
    def get_report(self):
        """Get monitoring report"""
        elapsed = time.time() - self.start_time
        return {
            "duration_seconds": elapsed,
            "max_cpu_percent": self.max_cpu_percent,
            "max_memory_mb": self.max_memory_mb,
            "keyboard_events": self.keyboard_events,
            "warnings": self.warnings
        }


def test_game_with_monitoring():
    """Run the game with system monitoring"""
    
    print("=== Game Test with System Monitoring ===")
    print("Monitoring for potential system-wide issues...")
    print("Press Ctrl+C to stop safely")
    print()
    
    monitor = SystemMonitor()
    monitor.start_monitoring()
    
    try:
        # Initialize pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
        
        print("1. Pygame initialized")
        
        # Create a simple test window
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("System Monitoring Test")
        clock = pygame.time.Clock()
        
        print("2. Display created")
        
        # Test basic game loop
        print("3. Starting monitored game loop...")
        print("   (Will run for 30 seconds or until Ctrl+C)")
        
        start_time = time.time()
        frame_count = 0
        last_keyboard_check = time.time()
        
        running = True
        while running and (time.time() - start_time) < 30:  # 30 second limit
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.KEYDOWN:
                    monitor.keyboard_events += 1
                    print(f"   Keyboard event detected: {pygame.key.name(event.key)}")
                    
                    # Test specific keys that might cause issues
                    if event.key == pygame.K_ESCAPE:
                        print("   ESC pressed - stopping test")
                        running = False
            
            # Check keyboard responsiveness
            if time.time() - last_keyboard_check >= 5:
                keys = pygame.key.get_pressed()
                key_count = sum(keys)
                if key_count > 0:
                    print(f"   Keys currently pressed: {key_count}")
                last_keyboard_check = time.time()
            
            # Simple rendering
            screen.fill((50, 50, 100))
            
            # Draw simple test pattern
            pygame.draw.circle(screen, (255, 255, 255), (400, 300), 50)
            
            pygame.display.flip()
            clock.tick(60)  # 60 FPS
            
            frame_count += 1
            
            # Check for warnings every 5 seconds
            if frame_count % 300 == 0:  # Every 5 seconds at 60fps
                if monitor.warnings:
                    print(f"   WARNING: {monitor.warnings[-1]}")
        
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed
        
        print(f"\n4. Game loop completed:")
        print(f"   Duration: {elapsed:.1f} seconds")
        print(f"   Frames: {frame_count}")
        print(f"   Average FPS: {avg_fps:.1f}")
        print(f"   Keyboard events: {monitor.keyboard_events}")
        
        return True
        
    except KeyboardInterrupt:
        print("\n   Test interrupted by user (Ctrl+C)")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Game test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        monitor.stop_monitoring()
        
        # Get monitoring report
        report = monitor.get_report()
        
        print(f"\n=== System Monitoring Report ===")
        print(f"Test Duration: {report['duration_seconds']:.1f} seconds")
        print(f"Max CPU Usage: {report['max_cpu_percent']:.1f}%")
        print(f"Max Memory Usage: {report['max_memory_mb']:.1f} MB")
        print(f"Keyboard Events: {report['keyboard_events']}")
        
        if report['warnings']:
            print(f"\nWarnings ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"  - {warning}")
        else:
            print("\nNo system warnings detected!")
            
        # Check for concerning patterns
        concerning_issues = []
        
        if report['max_cpu_percent'] > 80:
            concerning_issues.append(f"High CPU usage: {report['max_cpu_percent']:.1f}%")
            
        if report['max_memory_mb'] > 400:
            concerning_issues.append(f"High memory usage: {report['max_memory_mb']:.1f} MB")
            
        if len(report['warnings']) > 10:
            concerning_issues.append(f"Many warnings: {len(report['warnings'])}")
            
        if concerning_issues:
            print(f"\n*** CONCERNING ISSUES DETECTED ***")
            for issue in concerning_issues:
                print(f"  ! {issue}")
            print("These could potentially cause system-wide problems.")
        else:
            print(f"\n*** NO CONCERNING ISSUES DETECTED ***")
            print("Game appears to be running safely.")
        
        try:
            pygame.quit()
        except:
            pass


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\nReceived interrupt signal - stopping test safely...")
    sys.exit(0)


if __name__ == "__main__":
    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("System Monitoring Game Test")
    print("=" * 40)
    print("This will run the game with resource monitoring")
    print("to check for potential system-wide impact issues.")
    print()
    print("The test will:")
    print("- Monitor CPU and memory usage")
    print("- Track keyboard event handling")
    print("- Watch for resource leaks")
    print("- Run for 30 seconds max")
    print()
    
    try:
        success = test_game_with_monitoring()
        
        if success:
            print("\n[RESULT] Test completed successfully")
            print("No obvious causes for system-wide keyboard freeze detected.")
        else:
            print("\n[RESULT] Test encountered issues")
            print("Check the error messages above for potential causes.")
            
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nTest finished. Check the monitoring report above.")
    print("If keyboard freezes persist, it may be a system/driver issue.")