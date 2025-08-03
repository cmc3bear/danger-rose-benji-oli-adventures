#!/usr/bin/env python3
"""
Generate scene-specific sound effects for Pool, Ski, and Vegas minigames.
Uses 11labs API and applies retro processing for authentic 8-bit feel.
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.generate_sounds_11labs import ElevenLabsSoundGenerator, load_api_key
from tools.retro_sound_processor import RetroSoundProcessor


class MinigameSoundGenerator(ElevenLabsSoundGenerator):
    """Specialized sound generator for minigame-specific effects."""
    
    def get_minigame_sounds(self) -> Dict[str, List[Dict]]:
        """Get minigame-specific sound definitions.
        
        Returns:
            Dictionary of minigame sound categories and their definitions
        """
        return {
            "pool_minigame": [
                {"name": "pool_shot", "text": "[8-bit shooting sound effect, like classic arcade target practice]", "voice": "narrator"},
                {"name": "target_hit", "text": "[Retro target hit sound, satisfying ding like classic arcade games]", "voice": "narrator"},
                {"name": "bullseye", "text": "[Triumphant 8-bit bullseye sound with rising pitch celebration]", "voice": "narrator"},
                {"name": "target_miss", "text": "[Gentle whoosh sound for missed shot, not harsh or disappointing]", "voice": "narrator"},
                {"name": "powerup_collect", "text": "[Classic arcade power-up collection sound, cheerful and rewarding]", "voice": "narrator"},
                {"name": "perfect_round", "text": "[Victory fanfare for perfect round, 8-bit celebration jingle]", "voice": "narrator"},
            ],
            "ski_minigame": [
                {"name": "ski_swoosh", "text": "[Retro skiing swoosh sound, like classic winter sports games]", "voice": "narrator"},
                {"name": "ski_turn", "text": "[Sharp 8-bit turn sound with snow spray effect]", "voice": "narrator"},
                {"name": "snow_spray", "text": "[Light snow spraying sound effect, retro winter game style]", "voice": "narrator"},
                {"name": "tree_hit", "text": "[Gentle bump sound for hitting tree, not scary - like cartoon bonk]", "voice": "narrator"},
                {"name": "checkpoint", "text": "[Classic checkpoint passing chime, encouraging and positive]", "voice": "narrator"},
                {"name": "speed_boost", "text": "[Exciting speed boost sound with rising pitch, arcade style]", "voice": "narrator"},
                {"name": "finish_line", "text": "[Triumphant finish line crossing fanfare, 8-bit victory sound]", "voice": "narrator"},
            ],
            "vegas_minigame": [
                {"name": "coin_collect", "text": "[Classic coin collection sound, like Mario but with casino flair]", "voice": "narrator"},
                {"name": "slot_machine", "text": "[Retro slot machine spinning sound, 8-bit mechanical whirring]", "voice": "narrator"},
                {"name": "dice_roll", "text": "[Classic dice rolling sound effect, arcade game style]", "voice": "narrator"},
                {"name": "card_flip", "text": "[Simple card flipping sound, light and crisp retro effect]", "voice": "narrator"},
                {"name": "jackpot", "text": "[Big celebration jackpot sound, 8-bit fanfare with coins falling]", "voice": "narrator"},
                {"name": "boss_appear", "text": "[Dramatic but kid-friendly boss appearance sound, exciting not scary]", "voice": "narrator"},
                {"name": "special_attack", "text": "[Cool special ability sound with whoosh and sparkle effects]", "voice": "narrator"},
            ]
        }
    
    def generate_minigame_sounds(self, apply_retro: bool = True, preset: str = "arcade"):
        """Generate all minigame-specific sounds.
        
        Args:
            apply_retro: Whether to apply retro processing
            preset: Retro processing preset to use
        """
        sounds = self.get_minigame_sounds()
        total_sounds = sum(len(category) for category in sounds.values())
        
        print(f"\n>>> Generating {total_sounds} minigame sound effects...")
        print(f"   Retro processing: {'Yes' if apply_retro else 'No'}")
        if apply_retro:
            print(f"   Preset: {preset}")
        
        generated = 0
        failed = 0
        processed = 0
        
        # Initialize retro processor if needed
        processor = RetroSoundProcessor() if apply_retro else None
        
        for category, sound_list in sounds.items():
            print(f"\n[Category: {category.replace('_', ' ').title()}]")
            
            # Determine output directory
            game_name = category.split('_')[0]  # pool, ski, vegas
            if game_name == "pool":
                subdir = self.output_base / "pool" / "impact"
            elif game_name == "ski":
                subdir = self.output_base / "ski" / "movement"
            elif game_name == "vegas":
                subdir = self.output_base / "vegas" / "casino"
            else:
                subdir = self.output_base / "sfx" / game_name
                
            # Create subdirectory
            subdir.mkdir(parents=True, exist_ok=True)
            
            for sound in sound_list:
                print(f"  >> Generating: {sound['name']}...", end="", flush=True)
                
                # Generate base sound
                base_output = subdir / f"{sound['name']}_raw.mp3"
                voice_id = self.voice_presets.get(sound['voice'], self.voice_presets['narrator'])
                
                success = self.generate_sound(sound['text'], voice_id, base_output)
                
                if success:
                    print(" [OK]", end="", flush=True)
                    generated += 1
                    
                    if apply_retro and processor and processor.ffmpeg_available:
                        # Apply retro processing
                        final_output = subdir / f"{sound['name']}.mp3"
                        retro_success = processor.process_sound(base_output, final_output, preset)
                        
                        if retro_success:
                            print(" [RETRO]")
                            processed += 1
                            # Remove raw file
                            if base_output.exists():
                                base_output.unlink()
                        else:
                            print(" (retro failed)")
                            # Rename raw to final
                            base_output.rename(final_output)
                    else:
                        # Just rename to final name
                        final_output = subdir / f"{sound['name']}.mp3"
                        base_output.rename(final_output)
                        print(" [OK]")
                else:
                    print(" [FAIL]")
                    failed += 1
                    
                # Rate limiting
                time.sleep(0.5)
        
        print(f"\n=== Generation Complete! ===")
        print(f"   Generated: {generated} sounds")
        print(f"   Retro processed: {processed} sounds") 
        print(f"   Failed: {failed} sounds")
        
        return generated, processed, failed


def main():
    """Main function to generate minigame sounds."""
    print("*** Danger Rose Minigame Sound Generator ***")
    print("==========================================\n")
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("\n[ERROR] Cannot proceed without API key")
        print("Please ensure 11labs API key is in the vault:")
        print("  C:/dev/api-key-forge/vault/11LABS/api_key.txt")
        return 1
    
    # Initialize generator
    generator = MinigameSoundGenerator(api_key)
    
    # Setup directories
    generator.setup_directories()
    
    # Check for retro processing availability
    processor = RetroSoundProcessor()
    if processor.ffmpeg_available:
        print("* ffmpeg available - will apply retro processing")
        apply_retro = True
        preset = "arcade"  # Good for game sounds
    else:
        print("* ffmpeg not found - generating raw sounds only")
        print("   Install ffmpeg for retro 8-bit processing")
        apply_retro = False
        preset = None
    
    # Generate minigame sounds
    generated, processed, failed = generator.generate_minigame_sounds(
        apply_retro=apply_retro, 
        preset=preset
    )
    
    # Show file locations
    print(f"\n=== Sound files created in: ===")
    print(f"   Pool: {generator.output_base}/pool/impact/")
    print(f"   Ski:  {generator.output_base}/ski/movement/")  
    print(f"   Vegas: {generator.output_base}/vegas/casino/")
    
    # Summary
    if failed == 0:
        print(f"\n=== All sounds generated successfully! ===")
        if apply_retro:
            print(f"   {processed} sounds processed with {preset} retro effects")
    else:
        print(f"\n=== {failed} sounds failed to generate ===")
        
    print("\n=== Ready to enhance your minigames with awesome sound effects! ===")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())