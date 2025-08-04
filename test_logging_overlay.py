#!/usr/bin/env python3
"""
Quick test of the logging system and overlay functionality
"""

import pygame
import sys
import time
from src.systems.game_state_logger import GameStateLogger
from src.ui.live_testing_overlay import LiveTestingOverlay
from src.testing.test_plan_loader import TestPlanLoader

def test_logging_overlay():
    """Test the logging overlay functionality"""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Logging System Test - Press F12 to toggle overlay")
    clock = pygame.time.Clock()
    
    # Initialize systems
    logger = GameStateLogger('.')
    overlay = LiveTestingOverlay(1024, 768)
    test_loader = TestPlanLoader('.')
    
    # Load test procedures for Issue #34
    try:
        procedures = test_loader.load_issue_test_plan(34)
        overlay.active_procedures = procedures[:3]  # Show max 3
        print(f"Loaded {len(procedures)} test procedures for Issue #34")
    except Exception as e:
        print(f"Could not load test procedures: {e}")
        # Create a simple test procedure for demo
        from src.ui.live_testing_overlay import TestProcedure
        demo_procedure = TestProcedure(
            id="demo_test",
            title="Demo: Logging System Active",
            description="Verify logging system is working",
            steps=["Start game", "Check logs", "Verify performance"],
            status="in_progress"
        )
        overlay.active_procedures = [demo_procedure]
    
    # Log system start
    logger.log_system_event("test", "overlay_test_start", {
        "screen_size": (1024, 768),
        "procedures_loaded": len(overlay.active_procedures)
    })
    
    running = True
    frame_count = 0
    fps_samples = []
    
    print("=== LOGGING SYSTEM TEST ===")
    print("Instructions:")
    print("- Press F12 to toggle testing overlay")
    print("- Press F11 to mark test steps complete")
    print("- Press ESC to exit")
    print("- Watch console for logging activity")
    
    while running:
        frame_start = time.time()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F12:
                    overlay.toggle_overlay()
                    logger.log_player_action("toggle_overlay", "test", {
                        "overlay_enabled": overlay.overlay_enabled
                    })
                    print(f"Overlay {'enabled' if overlay.overlay_enabled else 'disabled'}")
                elif event.key == pygame.K_F11:
                    success = overlay.handle_manual_completion(event)
                    if success:
                        logger.log_system_event("test", "manual_completion", {
                            "procedures_active": len(overlay.active_procedures)
                        })
                        print("Manual test completion registered")
            
            # Log input events
            logger.log_player_action("input_event", "test", {
                "event_type": event.type,
                "timestamp": time.time()
            })
        
        # Fill screen
        screen.fill((50, 50, 100))  # Dark blue background
        
        # Draw simple test content
        font = pygame.font.Font(None, 36)
        title = font.render("Logging System Test", True, (255, 255, 255))
        screen.blit(title, (50, 50))
        
        info_font = pygame.font.Font(None, 24)
        instructions = [
            "F12: Toggle testing overlay",
            "F11: Complete test step", 
            "ESC: Exit test",
            f"Frame: {frame_count}",
            f"FPS: {clock.get_fps():.1f}"
        ]
        
        for i, instruction in enumerate(instructions):
            text = info_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (50, 100 + i * 30))
        
        # Draw the testing overlay
        overlay.draw(screen)
        
        # Update display
        pygame.display.flip()
        
        # Calculate FPS
        frame_time = time.time() - frame_start
        fps = 1.0 / frame_time if frame_time > 0 else 60.0
        fps_samples.append(fps)
        
        # Log performance every 60 frames
        if frame_count % 60 == 0 and frame_count > 0:
            avg_fps = sum(fps_samples[-60:]) / min(60, len(fps_samples))
            logger.log_performance_metric("fps", avg_fps, {
                "frame_count": frame_count,
                "scene": "test"
            })
        
        frame_count += 1
        clock.tick(60)  # Target 60 FPS
    
    # Log system shutdown
    final_fps = sum(fps_samples[-60:]) / min(60, len(fps_samples)) if fps_samples else 0
    logger.log_system_event("test", "overlay_test_end", {
        "total_frames": frame_count,
        "final_fps": final_fps,
        "overlay_state": overlay.overlay_enabled
    })
    
    print(f"\nTest completed:")
    print(f"- Total frames: {frame_count}")
    print(f"- Average FPS: {final_fps:.1f}")
    print(f"- Log file: {logger.log_file}")
    
    pygame.quit()
    logger.shutdown()

if __name__ == "__main__":
    test_logging_overlay()