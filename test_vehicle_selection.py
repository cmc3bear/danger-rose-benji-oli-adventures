#!/usr/bin/env python3
"""Test script for vehicle selection system."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from src.utils.save_manager import SaveManager
from src.utils.sprite_loader import load_vehicle_sprite, get_vehicle_sprite_path


def test_vehicle_sprites():
    """Test that vehicle sprites can be loaded."""
    print("Testing vehicle sprite loading...")
    
    vehicles = ["professional", "kids_drawing"]
    
    for vehicle in vehicles:
        print(f"\nTesting {vehicle}:")
        
        # Check sprite path
        sprite_path = get_vehicle_sprite_path(vehicle)
        print(f"  Path: {sprite_path}")
        print(f"  Exists: {os.path.exists(sprite_path)}")
        
        # Try loading sprite
        try:
            sprite = load_vehicle_sprite(vehicle)
            print(f"  Loaded: {sprite.get_size()}")
        except Exception as e:
            print(f"  Error: {e}")


def test_save_system():
    """Test vehicle selection persistence."""
    print("\n\nTesting save system...")
    
    # Create test save manager
    test_dir = Path("test_saves")
    save_manager = SaveManager(test_dir)
    
    # Load save data
    save_data = save_manager.load()
    print(f"Initial vehicle: {save_data['player'].get('selected_vehicle', 'None')}")
    
    # Test setting vehicles
    for vehicle in ["professional", "kids_drawing"]:
        save_manager.set_selected_vehicle(vehicle)
        saved_vehicle = save_manager.get_selected_vehicle()
        print(f"Set to {vehicle}, got: {saved_vehicle}")
        assert saved_vehicle == vehicle, f"Expected {vehicle}, got {saved_vehicle}"
    
    # Test save and reload
    save_manager.save()
    
    # Create new manager to test loading
    new_manager = SaveManager(test_dir)
    new_manager.load()
    loaded_vehicle = new_manager.get_selected_vehicle()
    print(f"After save/load: {loaded_vehicle}")
    
    # Cleanup
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    print("\nSave system test passed!")


def main():
    """Run all tests."""
    print("=== Vehicle Selection System Test ===\n")
    
    test_vehicle_sprites()
    test_save_system()
    
    print("\n=== All tests completed! ===")


if __name__ == "__main__":
    main()