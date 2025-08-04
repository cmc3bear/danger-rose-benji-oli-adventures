#!/usr/bin/env python3
"""Test script to validate EV vehicle sprite loading."""

import pygame
import sys
import os

# Add src to path
sys.path.append('src')

def test_vehicle_sprites():
    """Test vehicle sprite loading functionality."""
    pygame.init()
    
    from src.ui.vehicle_selector import VehicleSelector
    from src.managers.sound_manager import SoundManager
    
    try:
        # Create a minimal sound manager for testing
        sound_manager = SoundManager()
        vehicle_selector = VehicleSelector(800, 600, sound_manager)
        
        print("=== VEHICLE SELECTOR TEST ===")
        print(f"Available vehicles: {len(vehicle_selector.vehicles)}")
        print()
        
        for i, vehicle in enumerate(vehicle_selector.vehicles):
            print(f"Vehicle {i+1}: {vehicle.name}")
            print(f"  ID: {vehicle.id}")
            print(f"  Sprite name: {vehicle.sprite_name}")
            print(f"  Description: {vehicle.description}")
            
            # Check sprite loading
            if vehicle.sprite:
                size = vehicle.sprite.get_size()
                is_placeholder = size == (64, 64)
                print(f"  Sprite loaded: YES, size: {size}, placeholder: {is_placeholder}")
            else:
                print(f"  Sprite loaded: NO")
                
            # Check preview sprite
            if vehicle.preview_sprite:
                size = vehicle.preview_sprite.get_size()
                print(f"  Preview sprite: YES, size: {size}")
            else:
                print(f"  Preview sprite: NO")
            print()
            
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_sprite_loading():
    """Test direct sprite loading via sprite_loader."""
    from src.utils.sprite_loader import load_vehicle_sprite
    
    print("=== DIRECT SPRITE LOADING TEST ===")
    vehicles = ['professional', 'kids_drawing']
    
    for vehicle in vehicles:
        try:
            sprite = load_vehicle_sprite(vehicle)
            size = sprite.get_size()
            is_placeholder = size == (64, 64)
            print(f"{vehicle}: Loaded, size: {size}, placeholder: {is_placeholder}")
        except Exception as e:
            print(f"{vehicle}: ERROR - {e}")

def test_file_existence():
    """Test if the actual sprite files exist."""
    print("=== FILE EXISTENCE TEST ===")
    vehicles = ['professional', 'kids_drawing']
    
    for vehicle in vehicles:
        path = f"assets/images/vehicles/ev_{vehicle}.png"
        exists = os.path.exists(path)
        if exists:
            # Check file size
            size = os.path.getsize(path)
            print(f"{path}: EXISTS ({size} bytes)")
        else:
            print(f"{path}: MISSING")

if __name__ == "__main__":
    print("INVESTIGATION: EV Vehicle Sprites in Drive Game")
    print("=" * 50)
    print()
    
    test_file_existence()
    print()
    test_direct_sprite_loading()
    print()
    test_vehicle_sprites()
    
    pygame.quit()