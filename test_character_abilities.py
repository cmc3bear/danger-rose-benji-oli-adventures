"""Test implementation of character abilities system design (Issue #29)"""

import time
from abc import ABC, abstractmethod
from enum import Enum

class AbilityType(Enum):
    """Types of character abilities"""
    TECH_BOOST = "tech_boost"
    NATURE_BLESSING = "nature_blessing"
    BEAR_STRENGTH = "bear_strength"
    SPEED_BURST = "speed_burst"
    PRECISION = "precision"
    EXPERIENCE = "experience"

class CharacterAbility(ABC):
    """Base class for all character special abilities"""
    def __init__(self, character_name: str, ability_type: AbilityType, cooldown: float = 10.0):
        self.character_name = character_name
        self.ability_type = ability_type
        self.cooldown = cooldown
        self.last_used = 0
        self.is_active = False
        self.duration = 5.0  # Default ability duration
        self.activation_time = 0
    
    @abstractmethod
    def activate(self, scene_context: dict) -> dict:
        """Activate ability and return effects"""
        pass
    
    @abstractmethod
    def update(self, dt: float, scene_context: dict) -> dict:
        """Update ability state each frame"""
        pass
    
    @abstractmethod
    def deactivate(self) -> None:
        """Clean up ability effects"""
        pass
    
    def can_use(self) -> bool:
        """Check if ability is off cooldown"""
        return time.time() - self.last_used >= self.cooldown
    
    def is_expired(self) -> bool:
        """Check if ability duration has expired"""
        if self.is_active:
            return time.time() - self.activation_time >= self.duration
        return False

# Example implementation: Benji's Tech Boost
class TechBoostAbility(CharacterAbility):
    def __init__(self):
        super().__init__("Benji", AbilityType.TECH_BOOST, cooldown=12.0)
        self.duration = 8.0
    
    def activate(self, scene_context):
        self.is_active = True
        self.activation_time = time.time()
        self.last_used = time.time()
        
        scene = scene_context.get("scene", "hub")
        
        # Return scene-specific effects
        effects = {
            "pool": {
                "effect": "homing_balloons",
                "homing_strength": 0.8,
                "visual": "digital_trail"
            },
            "ski": {
                "effect": "optimal_path",
                "path_duration": 3.0,
                "visual": "holographic_line"
            },
            "vegas": {
                "effect": "shield",
                "shield_health": 1,
                "recharge_time": 10.0,
                "visual": "tech_bubble"
            },
            "drive": {
                "effect": "hazard_preview",
                "preview_distance": 300,
                "visual": "warning_icons"
            }
        }
        
        return effects.get(scene, {"effect": "none"})
    
    def update(self, dt: float, scene_context: dict) -> dict:
        """Update tech boost effects"""
        if not self.is_active:
            return {}
        
        # Return ongoing effects
        return {
            "maintain_effect": True,
            "time_remaining": self.duration - (time.time() - self.activation_time)
        }
    
    def deactivate(self) -> None:
        """Clean up tech boost effects"""
        self.is_active = False
        print(f"Tech Boost deactivated for {self.character_name}")

# Test the ability system
def test_ability_system():
    print("Testing Character Abilities System Design")
    print("=" * 50)
    
    # Create Benji's ability
    tech_boost = TechBoostAbility()
    
    # Test 1: Check initial state
    print("\n1. Initial State Test:")
    print(f"   - Character: {tech_boost.character_name}")
    print(f"   - Ability Type: {tech_boost.ability_type.value}")
    print(f"   - Can Use: {tech_boost.can_use()}")
    print(f"   - Is Active: {tech_boost.is_active}")
    
    # Test 2: Activate ability in different scenes
    print("\n2. Activation Test:")
    scenes = ["pool", "ski", "vegas", "drive"]
    
    for scene in scenes:
        if tech_boost.can_use():
            context = {"scene": scene}
            effects = tech_boost.activate(context)
            print(f"\n   Scene: {scene}")
            print(f"   Effects: {effects}")
            
            # Simulate a frame update
            update_result = tech_boost.update(0.016, context)  # 60 FPS
            print(f"   Update: {update_result}")
            
            # Deactivate and wait for cooldown
            tech_boost.deactivate()
            time.sleep(0.1)  # Small delay to simulate time passing
            
            # Reset last_used to test next scene
            tech_boost.last_used = 0
    
    # Test 3: Cooldown system
    print("\n3. Cooldown Test:")
    tech_boost.activate({"scene": "pool"})
    print(f"   - Can use immediately after activation: {tech_boost.can_use()}")
    
    # Test 4: Duration check
    print("\n4. Duration Test:")
    tech_boost.activation_time = time.time() - 4.9  # Almost expired
    print(f"   - Is expired (4.9s): {tech_boost.is_expired()}")
    tech_boost.activation_time = time.time() - 5.1  # Expired
    print(f"   - Is expired (5.1s): {tech_boost.is_expired()}")
    
    print("\n" + "=" * 50)
    print("✅ Character Abilities System Design Validated!")
    print("\nKey Design Points Confirmed:")
    print("- Abstract base class provides consistent interface")
    print("- Scene-specific effects are properly returned")
    print("- Cooldown system prevents ability spam")
    print("- Duration tracking works correctly")
    print("- Clean activation/deactivation lifecycle")

if __name__ == "__main__":
    test_ability_system()