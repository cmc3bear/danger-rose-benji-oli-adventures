#!/usr/bin/env python3
"""
Generate sound effects for Danger Rose using 11labs API.
Priority focus on Hub World and Drive minigame sounds.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class ElevenLabsSoundGenerator:
    """Generate game sounds using 11labs API."""
    
    def __init__(self, api_key: str):
        """Initialize the sound generator.
        
        Args:
            api_key: 11labs API key
        """
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Output directory structure
        self.output_base = Path("assets/audio/sfx")
        self.temp_dir = Path("assets/audio/temp")
        
        # Voice IDs for different sound types
        self.voice_presets = {
            "narrator": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "young_male": "VR6AewLTigWG4xSOukaG",  # Arnold  
            "young_female": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "adult_male": "ErXwobaYiN019PkySvjV",  # Antoni
        }
        
        # Sound generation settings
        self.sound_settings = {
            "stability": 0.5,
            "similarity_boost": 0.5,
            "style": 0.0,
            "use_speaker_boost": True
        }
        
    def setup_directories(self):
        """Create directory structure for sound files."""
        directories = [
            self.output_base / "hub" / "character",
            self.output_base / "hub" / "ambient", 
            self.output_base / "hub" / "interactive",
            self.output_base / "drive" / "vehicle",
            self.output_base / "drive" / "traffic",
            self.output_base / "drive" / "collision",
            self.output_base / "ski" / "movement",
            self.output_base / "ski" / "collision",
            self.output_base / "pool" / "water",
            self.output_base / "pool" / "impact",
            self.output_base / "vegas" / "casino",
            self.output_base / "vegas" / "action",
            self.output_base / "ui" / "menu",
            self.output_base / "ui" / "feedback",
            self.temp_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        print(f"* Created directory structure under {self.output_base}")
        
    def get_priority_sounds(self) -> Dict[str, List[Dict]]:
        """Get priority sound definitions for Hub and Drive areas.
        
        Returns:
            Dictionary of sound categories and their definitions
        """
        # NOTE: Using retro-style sound descriptions for 8-bit/16-bit aesthetic
        return {
            "hub_character": [
                {"name": "danger_hello", "text": "Hey there!", "voice": "young_male"},
                {"name": "rose_hello", "text": "Hi everyone!", "voice": "young_female"},
                {"name": "dad_hello", "text": "Hello kids!", "voice": "adult_male"},
                {"name": "danger_excited", "text": "Let's go on an adventure!", "voice": "young_male"},
                {"name": "rose_excited", "text": "This is going to be fun!", "voice": "young_female"},
                {"name": "dad_concerned", "text": "Be careful out there!", "voice": "adult_male"},
                {"name": "family_cheer", "text": "Yay! We did it!", "voice": "young_female"},
            ],
            "hub_interactions": [
                {"name": "door_knock", "text": "[Retro 8-bit knocking sound effect]", "voice": "narrator"},
                {"name": "footsteps_walk", "text": "[Simple retro footstep sound, like classic RPG games]", "voice": "narrator"},
                {"name": "footsteps_run", "text": "[Quick retro footstep sounds, arcade style]", "voice": "narrator"},
                {"name": "jump_sound", "text": "[Classic video game jump sound, like Mario]", "voice": "narrator"},
                {"name": "door_open", "text": "[Simple retro door opening chime]", "voice": "narrator"},
                {"name": "door_close", "text": "[Simple retro door closing thud]", "voice": "narrator"},
                {"name": "light_switch", "text": "[Retro electronic click sound]", "voice": "narrator"},
                {"name": "tv_static", "text": "[8-bit style television static noise]", "voice": "narrator"},
                {"name": "item_pickup", "text": "[Classic arcade item collection sound]", "voice": "narrator"},
                {"name": "menu_select", "text": "[Retro menu selection beep]", "voice": "narrator"},
            ],
            "drive_vehicle": [
                {"name": "engine_start", "text": "[Retro arcade car engine startup sound]", "voice": "narrator"},
                {"name": "engine_idle", "text": "[Simple 8-bit style engine humming loop]", "voice": "narrator"},
                {"name": "engine_accelerate", "text": "[Classic racing game acceleration sound]", "voice": "narrator"},
                {"name": "engine_decelerate", "text": "[Retro racing game deceleration sound]", "voice": "narrator"},
                {"name": "brake_squeal", "text": "[Arcade style brake sound effect]", "voice": "narrator"},
                {"name": "tire_screech", "text": "[Classic racing game tire screech]", "voice": "narrator"},
                {"name": "horn_honk", "text": "[Retro car horn beep, like Pac-Man]", "voice": "narrator"},
                {"name": "gear_shift", "text": "[Simple electronic gear shift click]", "voice": "narrator"},
                {"name": "boost_powerup", "text": "[Arcade style speed boost sound]", "voice": "narrator"},
            ],
            "drive_collision": [
                {"name": "collision_soft", "text": "[Retro bump sound effect, like bumper cars]", "voice": "narrator"},
                {"name": "collision_hard", "text": "[Classic arcade crash sound]", "voice": "narrator"},
                {"name": "collision_barrier", "text": "[Metallic retro impact sound]", "voice": "narrator"},
                {"name": "collision_cone", "text": "[Light plastic bump sound, arcade style]", "voice": "narrator"},
                {"name": "damage_taken", "text": "[Classic game damage sound]", "voice": "narrator"},
                {"name": "warning_beep", "text": "[Retro warning beep, like Space Invaders]", "voice": "narrator"},
                {"name": "countdown_beep", "text": "[Classic arcade countdown beep]", "voice": "narrator"},
                {"name": "checkpoint_pass", "text": "[Retro checkpoint chime sound]", "voice": "narrator"},
            ],
            "drive_environment": [
                {"name": "wind_driving", "text": "[Simple 8-bit wind whoosh sound]", "voice": "narrator"},
                {"name": "traffic_ambience", "text": "[Retro arcade traffic background noise]", "voice": "narrator"},
                {"name": "car_pass_left", "text": "[Classic whoosh sound panning left]", "voice": "narrator"},
                {"name": "car_pass_right", "text": "[Classic whoosh sound panning right]", "voice": "narrator"},
                {"name": "tunnel_echo", "text": "[Retro echo effect, like old racing games]", "voice": "narrator"},
                {"name": "coin_collect", "text": "[Classic coin collection sound]", "voice": "narrator"},
                {"name": "finish_fanfare", "text": "[Retro victory fanfare, 8-bit style]", "voice": "narrator"},
            ],
            "retro_ui": [
                {"name": "menu_move", "text": "[Classic menu navigation beep]", "voice": "narrator"},
                {"name": "menu_select", "text": "[Retro menu selection confirm sound]", "voice": "narrator"},
                {"name": "menu_back", "text": "[Simple menu cancel sound]", "voice": "narrator"},
                {"name": "pause_game", "text": "[Classic game pause sound effect]", "voice": "narrator"},
                {"name": "unpause_game", "text": "[Classic game unpause sound effect]", "voice": "narrator"},
                {"name": "score_increment", "text": "[Retro score counting up sound]", "voice": "narrator"},
                {"name": "achievement_unlock", "text": "[8-bit achievement jingle]", "voice": "narrator"},
                {"name": "game_over", "text": "[Classic game over sound]", "voice": "narrator"},
            ]
        }
        
    def generate_sound(self, text: str, voice_id: str, output_path: Path) -> bool:
        """Generate a single sound effect using 11labs API.
        
        Args:
            text: Text prompt for sound generation
            voice_id: Voice ID to use
            output_path: Path to save the generated sound
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": self.sound_settings
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 200:
                # If ffmpeg is not available, save as MP3
                if not self._check_ffmpeg_available():
                    mp3_output = output_path.with_suffix('.mp3')
                    with open(mp3_output, 'wb') as f:
                        f.write(response.content)
                    print(f"  [OK] Saved as MP3: {mp3_output.name}")
                    return True
                else:
                    # Save as MP3 first, then convert to OGG
                    mp3_path = self.temp_dir / f"{output_path.stem}.mp3"
                    with open(mp3_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Convert to OGG
                    success = self.convert_to_ogg(mp3_path, output_path)
                    
                    # Clean up temp file
                    if mp3_path.exists():
                        mp3_path.unlink()
                        
                    return success
            else:
                print(f"[ERROR] API error for {output_path.name}: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error generating {output_path.name}: {str(e)}")
            return False
            
    def _check_ffmpeg_available(self) -> bool:
        """Check if ffmpeg is available for conversion."""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except:
            return False
            
    def convert_to_ogg(self, input_path: Path, output_path: Path) -> bool:
        """Convert MP3 to OGG using ffmpeg.
        
        Args:
            input_path: Input MP3 file
            output_path: Output OGG file
            
        Returns:
            True if successful
        """
        try:
            cmd = [
                "ffmpeg", "-i", str(input_path),
                "-c:a", "libvorbis", "-q:a", "6",
                "-ar", "44100", "-ac", "2",
                "-y", str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_path.exists():
                print(f"  [OK] Converted to OGG: {output_path.name}")
                return True
            else:
                print(f"  [ERROR] Conversion failed: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("[ERROR] ffmpeg not found. Please install ffmpeg for audio conversion.")
            return False
            
    def generate_priority_sounds(self, limit: Optional[int] = None):
        """Generate all priority sounds for Hub and Drive areas.
        
        Args:
            limit: Optional limit on number of sounds to generate
        """
        sounds = self.get_priority_sounds()
        total_sounds = sum(len(category) for category in sounds.values())
        
        print(f"\n>>> Generating {total_sounds} priority sounds for Hub and Drive areas...")
        
        generated = 0
        failed = 0
        
        for category, sound_list in sounds.items():
            print(f"\n[Category: {category}]")
            
            # Determine output subdirectory
            if category.startswith("hub_character"):
                subdir = self.output_base / "hub" / "character"
            elif category.startswith("hub_"):
                subdir = self.output_base / "hub" / "interactive"
            elif category.startswith("drive_vehicle"):
                subdir = self.output_base / "drive" / "vehicle"
            elif category.startswith("drive_collision"):
                subdir = self.output_base / "drive" / "collision"
            elif category.startswith("drive_"):
                subdir = self.output_base / "drive" / "traffic"
            else:
                subdir = self.output_base / "ui" / "feedback"
                
            for sound in sound_list:
                if limit and generated >= limit:
                    print(f"\n!!! Reached limit of {limit} sounds")
                    return
                    
                output_path = subdir / f"{sound['name']}.ogg"
                
                # Skip if already exists
                if output_path.exists():
                    print(f"  >> Skipping {sound['name']} (already exists)")
                    continue
                    
                print(f"  >> Generating: {sound['name']}...", end="", flush=True)
                
                # Get voice ID
                voice_id = self.voice_presets.get(sound['voice'], self.voice_presets['narrator'])
                
                # Generate sound
                success = self.generate_sound(sound['text'], voice_id, output_path)
                
                if success:
                    print(" [OK]")
                    generated += 1
                else:
                    print(" [FAIL]")
                    failed += 1
                    
                # Rate limiting
                time.sleep(0.5)  # Be respectful to the API
                
        print(f"\n=== Summary ===")
        print(f"  Generated: {generated} sounds")
        print(f"  Failed: {failed} sounds")
        print(f"  Total: {generated + failed} attempts")
        
    def generate_remaining_sounds(self):
        """Generate sounds for remaining game areas (Ski, Pool, Vegas)."""
        # This would contain definitions for other game areas
        # Implementation left for when Hub/Drive are complete
        pass
        
    def validate_sounds(self) -> Dict[str, bool]:
        """Validate all generated sound files.
        
        Returns:
            Dictionary mapping file paths to validation status
        """
        print("\n>>> Validating generated sounds...")
        
        results = {}
        
        for root, dirs, files in os.walk(self.output_base):
            for file in files:
                if file.endswith(('.ogg', '.mp3')):
                    file_path = Path(root) / file
                    
                    # Basic validation - file exists and has content
                    if file_path.exists() and file_path.stat().st_size > 1024:
                        results[str(file_path)] = True
                        print(f"  [OK] Valid: {file_path.relative_to(self.output_base)}")
                    else:
                        results[str(file_path)] = False
                        print(f"  [FAIL] Invalid: {file_path.relative_to(self.output_base)}")
                        
        return results
        

def load_api_key() -> Optional[str]:
    """Load 11labs API key from vault.
    
    Returns:
        API key string or None if not found
    """
    vault_paths = [
        Path("C:/dev/api-key-forge/vault/11LABS/API-KEY.txt"),
        Path("C:/dev/api-key-forge/vault/11LABS/api_key.txt"),
        Path("C:/dev/api-key-forge/vault/11labs/api_key.txt"),
        Path("C:/dev/api-key-forge/vault/ELEVEN_LABS/api_key.txt"),
    ]
    
    for vault_path in vault_paths:
        if vault_path.exists():
            try:
                with open(vault_path, 'r') as f:
                    api_key = f.read().strip()
                    if api_key:
                        print(f"* Loaded API key from: {vault_path}")
                        return api_key
            except Exception as e:
                print(f"[ERROR] Error reading API key from {vault_path}: {e}")
                
    print("[ERROR] Could not find 11labs API key in vault")
    return None


def main():
    """Main function to generate sounds."""
    print("*** Danger Rose Sound Generation Tool ***")
    print("==========================================\n")
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("\n[ERROR] Cannot proceed without API key")
        print("Please ensure 11labs API key is in the vault:")
        print("  C:/dev/api-key-forge/vault/11LABS/api_key.txt")
        return 1
        
    # Check for ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("* ffmpeg is available - will generate OGG files")
    except:
        print("* ffmpeg not found - will generate MP3 files instead")
        print("  (Install ffmpeg from https://ffmpeg.org/download.html for OGG conversion)")
        
    # Initialize generator
    generator = ElevenLabsSoundGenerator(api_key)
    
    # Setup directories
    generator.setup_directories()
    
    # Generate priority sounds (Hub and Drive)
    print("\n>>> Focusing on priority areas: Hub World and Drive Game")
    
    # Optional: Set a limit for testing
    # generator.generate_priority_sounds(limit=5)
    
    # Generate all priority sounds
    generator.generate_priority_sounds()
    
    # Validate generated sounds
    validation_results = generator.validate_sounds()
    
    valid_count = sum(1 for v in validation_results.values() if v)
    total_count = len(validation_results)
    
    print(f"\n=== Generation complete! ===")
    print(f"   Valid sounds: {valid_count}/{total_count}")
    
    if valid_count < total_count:
        print("\n!!! Some sounds failed validation. Check the output above.")
        
    print("\n=== Next steps ===")
    print("1. Test sounds in the game")
    print("2. Adjust generation parameters if needed")
    print("3. Generate remaining game sounds")
    print("4. Integrate with enhanced sound manager")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())