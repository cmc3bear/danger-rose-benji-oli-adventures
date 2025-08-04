#!/usr/bin/env python3
"""
Debug test for overlay functionality
"""

import pygame
import sys
from src.ui.live_testing_overlay import LiveTestingOverlay, TestProcedure, TestStep, TestStatus, StepStatus

def debug_overlay():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Debug Testing Overlay - Press F12")
    clock = pygame.time.Clock()
    
    # Create overlay
    overlay = LiveTestingOverlay(800, 600)
    
    # Add a simple test procedure
    procedure = TestProcedure(
        id="debug_test",
        title="Debug Test Procedure",
        description="Testing overlay display",
        steps=[
            TestStep(step_number=1, action="Check overlay visibility", expected_result="Overlay appears"),
            TestStep(step_number=2, action="Press F12 to toggle", expected_result="Overlay toggles on/off"),
            TestStep(step_number=3, action="Press F9 to advance", expected_result="Step advances")
        ],
        status=TestStatus.PENDING
    )
    
    overlay.add_test_procedure(procedure)
    
    print("=== DEBUG OVERLAY TEST ===")
    print("Controls:")
    print("- F12: Toggle overlay")
    print("- F9: Next step")
    print("- ESC: Exit")
    print(f"Overlay enabled: {overlay.overlay_enabled}")
    print(f"Active procedures: {len(overlay.active_procedures)}")
    
    running = True
    frame_count = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F12:
                    overlay.toggle_overlay()
                    print(f"F12 pressed - Overlay enabled: {overlay.overlay_enabled}")
                elif event.key == pygame.K_F9:
                    success = overlay.advance_current_step()
                    print(f"F9 pressed - Advanced step: {success}")
        
        # Fill screen with blue
        screen.fill((50, 50, 100))
        
        # Draw frame counter
        font = pygame.font.Font(None, 36)
        text = font.render(f"Frame: {frame_count}", True, (255, 255, 255))
        screen.blit(text, (50, 50))
        
        # Draw instructions
        small_font = pygame.font.Font(None, 24)
        instructions = [
            "F12: Toggle overlay",
            "F9: Next step", 
            "ESC: Exit",
            f"Overlay: {'ON' if overlay.overlay_enabled else 'OFF'}",
            f"Procedures: {len(overlay.active_procedures)}"
        ]
        
        for i, instruction in enumerate(instructions):
            text = small_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (50, 100 + i * 25))
        
        # Update and draw overlay
        try:
            overlay.update(clock.get_time() / 1000.0)
            overlay.draw(screen)
        except Exception as e:
            print(f"ERROR in overlay: {e}")
            import traceback
            traceback.print_exc()
            # Continue without overlay
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    
    print("Debug test complete")
    pygame.quit()

if __name__ == "__main__":
    debug_overlay()