"""
Drive Music Manager for Danger Rose - The Drive Minigame

Manages the 3 synthwave music tracks for the racing game:
- Highway Dreams: Main upbeat racing theme
- Sunset Cruise: Relaxed cruising theme  
- Turbo Rush: High-energy intense racing theme

Integrates with pygame mixer for seamless music transitions and looping.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import pygame.mixer as mixer

logger = logging.getLogger(__name__)

class DriveMusicManager:
    """Manages music for The Drive racing minigame"""
    
    def __init__(self):
        """Initialize the music manager"""
        # Initialize pygame mixer if not already done
        if not mixer.get_init():
            mixer.init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=512
            )
        
        self.music_tracks: Dict[str, Dict] = {}
        self.current_track: Optional[str] = None
        self.music_volume = 0.7
        self.fade_time = 1000  # ms
        
        # Load track configurations
        self._load_music_manifest()
    
    def _load_music_manifest(self):
        """Load music track configurations from manifest"""
        manifest_path = Path("assets/audio/music/drive/music_manifest.json")
        
        if not manifest_path.exists():
            logger.warning(f"Music manifest not found: {manifest_path}")
            return
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            for track_info in manifest.get("drive_music_tracks", []):
                track_id = track_info["id"]
                
                # Check if music file exists (try different extensions)
                music_dir = Path("assets/audio/music/drive")
                possible_files = [
                    music_dir / track_info["filename"],
                    music_dir / track_info["filename"].replace(".ogg", ".wav"),
                    music_dir / track_info["filename"].replace(".ogg", ".mp3")
                ]
                
                music_file = None
                for file_path in possible_files:
                    if file_path.exists():
                        music_file = file_path
                        break
                
                if music_file:
                    self.music_tracks[track_id] = {
                        "title": track_info["title"],
                        "file_path": str(music_file),
                        "bpm": track_info["bpm"],
                        "key": track_info["key"],
                        "mood": track_info["mood"],
                        "description": track_info["description"]
                    }
                    logger.info(f"Loaded music track: {track_info['title']}")
                else:
                    logger.warning(f"Music file not found for track: {track_info['title']}")
        
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Failed to load music manifest: {e}")
    
    def play_track(self, track_id: str, loops: int = -1, fade_in: bool = True):
        """
        Play a specific music track
        
        Args:
            track_id: ID of the track to play (highway_dreams, sunset_cruise, turbo_rush)
            loops: Number of loops (-1 for infinite)
            fade_in: Whether to fade in the track
        """
        if track_id not in self.music_tracks:
            logger.error(f"Unknown track ID: {track_id}")
            return False
        
        track_info = self.music_tracks[track_id]
        
        try:
            # Stop current music with fade out if playing
            if self.current_track and mixer.music.get_busy():
                if fade_in:
                    mixer.music.fadeout(self.fade_time)
                else:
                    mixer.music.stop()
            
            # Load and play new track
            mixer.music.load(track_info["file_path"])
            mixer.music.set_volume(self.music_volume)
            
            if fade_in and self.current_track:
                mixer.music.play(loops, fade_ms=self.fade_time)
            else:
                mixer.music.play(loops)
            
            self.current_track = track_id
            logger.info(f"Playing track: {track_info['title']} ({track_info['mood']})")
            return True
            
        except pygame.error as e:
            logger.error(f"Failed to play track {track_id}: {e}")
            return False
    
    def play_highway_dreams(self):
        """Play the main upbeat racing theme"""
        return self.play_track("highway_dreams")
    
    def play_sunset_cruise(self):
        """Play the relaxed cruising theme"""
        return self.play_track("sunset_cruise")
    
    def play_turbo_rush(self):
        """Play the high-energy intense racing theme"""
        return self.play_track("turbo_rush")
    
    def play_for_race_type(self, race_type: str):
        """
        Play appropriate music based on race type
        
        Args:
            race_type: Type of race (normal, cruise, time_trial, etc.)
        """
        if race_type == "cruise" or race_type == "scenic":
            self.play_sunset_cruise()
        elif race_type == "time_trial" or race_type == "challenge":
            self.play_turbo_rush()
        else:
            self.play_highway_dreams()  # Default
    
    def set_volume(self, volume: float):
        """
        Set music volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        if mixer.music.get_busy():
            mixer.music.set_volume(self.music_volume)
    
    def pause(self):
        """Pause the current music"""
        if mixer.music.get_busy():
            mixer.music.pause()
    
    def unpause(self):
        """Unpause the current music"""
        mixer.music.unpause()
    
    def stop(self, fade_out: bool = True):
        """
        Stop the current music
        
        Args:
            fade_out: Whether to fade out before stopping
        """
        if mixer.music.get_busy():
            if fade_out:
                mixer.music.fadeout(self.fade_time)
            else:
                mixer.music.stop()
        self.current_track = None
    
    def get_available_tracks(self) -> List[Dict]:
        """Get list of available music tracks"""
        return [
            {
                "id": track_id,
                **track_info
            }
            for track_id, track_info in self.music_tracks.items()
        ]
    
    def get_current_track(self) -> Optional[Dict]:
        """Get information about the currently playing track"""
        if self.current_track:
            return {
                "id": self.current_track,
                **self.music_tracks[self.current_track]
            }
        return None
    
    def is_playing(self) -> bool:
        """Check if music is currently playing"""
        return mixer.music.get_busy()

# Example usage and testing
if __name__ == "__main__":
    """Test the music manager"""
    import time
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize pygame
    import pygame
    pygame.init()
    
    print("🎵 Testing Drive Music Manager")
    print("=" * 50)
    
    # Create music manager
    music_manager = DriveMusicManager()
    
    # Show available tracks
    tracks = music_manager.get_available_tracks()
    print(f"Available tracks: {len(tracks)}")
    for track in tracks:
        print(f"  - {track['title']} ({track['mood']}) - {track['bpm']} BPM")
    
    if tracks:
        print("\n🎮 Demo Playback:")
        
        # Demo each track for 5 seconds
        for track in tracks:
            print(f"\nPlaying: {track['title']}")
            music_manager.play_track(track['id'])
            
            # Wait and show status
            for i in range(5):
                if music_manager.is_playing():
                    current = music_manager.get_current_track()
                    print(f"  [{i+1}/5] Playing: {current['title']} - Volume: {music_manager.music_volume}")
                    time.sleep(1)
                else:
                    print(f"  Music stopped unexpectedly")
                    break
        
        # Test volume control
        print(f"\n🔊 Testing volume control...")
        music_manager.play_highway_dreams()
        for volume in [1.0, 0.5, 0.2, 0.8]:
            print(f"  Setting volume to {volume}")
            music_manager.set_volume(volume)
            time.sleep(1)
        
        # Stop music
        print(f"\n⏹️ Stopping music...")
        music_manager.stop()
        time.sleep(2)
        
        print(f"Music playing: {music_manager.is_playing()}")
    
    print("\n✅ Music manager test complete!")