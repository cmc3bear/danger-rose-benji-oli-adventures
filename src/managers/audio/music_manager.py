"""Advanced music management system for Danger Rose."""

import os
import json
import random
from typing import Dict, List, Optional, Set, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import pygame

from src.utils.asset_paths import get_music_path


class MusicCategory(Enum):
    """Categories for organizing music."""
    TITLE = "title"
    HUB = "hub"
    MINIGAME = "minigame"
    VICTORY = "victory"
    AMBIENT = "ambient"
    UNLOCKABLE = "unlockable"


class UnlockCondition(Enum):
    """Types of unlock conditions for music."""
    SCORE_THRESHOLD = "score_threshold"
    EASTER_EGG = "easter_egg"
    COMPLETION = "completion"
    SECRET_AREA = "secret_area"
    PERFECT_GAME = "perfect_game"
    TIME_TRIAL = "time_trial"


@dataclass
class MusicTrack:
    """Represents a music track with metadata."""
    id: str
    title: str
    filename: str
    category: MusicCategory
    duration: float = 0.0
    bpm: int = 120
    artist: str = "Danger Rose Team"
    unlocked: bool = True
    unlock_condition: Optional[UnlockCondition] = None
    unlock_data: Dict = None
    scene_specific: List[str] = None
    
    def __post_init__(self):
        if self.unlock_data is None:
            self.unlock_data = {}
        if self.scene_specific is None:
            self.scene_specific = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "filename": self.filename,
            "category": self.category.value,
            "duration": self.duration,
            "bpm": self.bpm,
            "artist": self.artist,
            "unlocked": self.unlocked,
            "unlock_condition": self.unlock_condition.value if self.unlock_condition else None,
            "unlock_data": self.unlock_data,
            "scene_specific": self.scene_specific
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MusicTrack':
        """Create from dictionary."""
        unlock_condition = None
        if data.get("unlock_condition"):
            unlock_condition = UnlockCondition(data["unlock_condition"])
        
        return cls(
            id=data["id"],
            title=data["title"],
            filename=data["filename"],
            category=MusicCategory(data["category"]),
            duration=data.get("duration", 0.0),
            bpm=data.get("bpm", 120),
            artist=data.get("artist", "Danger Rose Team"),
            unlocked=data.get("unlocked", True),
            unlock_condition=unlock_condition,
            unlock_data=data.get("unlock_data", {}),
            scene_specific=data.get("scene_specific", [])
        )


class MusicManager:
    """Advanced music management with unlockables and scene integration."""
    
    def __init__(self, sound_manager=None):
        """Initialize the music manager.
        
        Args:
            sound_manager: Reference to the main sound manager
        """
        self.sound_manager = sound_manager
        self.tracks: Dict[str, MusicTrack] = {}
        self.playlists: Dict[str, List[str]] = {}
        self.unlocked_tracks: Set[str] = set()
        self.current_track: Optional[MusicTrack] = None
        self.current_playlist: Optional[str] = None
        self.shuffle_mode = False
        self.repeat_mode = False
        self.auto_advance = True
        
        # Jukebox state
        self.jukebox_tracks: List[str] = []
        self.jukebox_selection = 0
        
        # Music conversion settings
        self.conversion_settings = {
            "target_format": "ogg",
            "quality": "192k",  # 192 kbps for efficiency without major quality loss
            "normalize": True,
            "fade_in": 0.5,
            "fade_out": 0.5
        }
        
        # Event callbacks
        self.track_change_callbacks: List[Callable] = []
        self.unlock_callbacks: List[Callable] = []
        
        # Load music library
        self._initialize_music_library()
        self._load_unlocked_tracks()
    
    def _initialize_music_library(self):
        """Initialize the music library with default tracks."""
        default_tracks = [
            # Title screen music
            MusicTrack(
                id="title_main",
                title="Danger Rose Theme",
                filename="title_main.ogg",
                category=MusicCategory.TITLE,
                duration=120.0,
                bpm=110
            ),
            
            # Hub world music
            MusicTrack(
                id="hub_cozy",
                title="Cozy Apartment",
                filename="hub_cozy.ogg",
                category=MusicCategory.HUB,
                duration=180.0,
                bpm=90
            ),
            MusicTrack(
                id="hub_upbeat",
                title="Family Fun Time",
                filename="hub_upbeat.ogg",
                category=MusicCategory.HUB,
                duration=150.0,
                bpm=120,
                unlocked=False,
                unlock_condition=UnlockCondition.SCORE_THRESHOLD,
                unlock_data={"total_score": 10000}
            ),
            
            # Ski game music
            MusicTrack(
                id="ski_main",
                title="Snowy Slopes",
                filename="ski_main.ogg",
                category=MusicCategory.MINIGAME,
                scene_specific=["ski"],
                duration=90.0,
                bpm=140
            ),
            MusicTrack(
                id="ski_intense",
                title="Avalanche Rush",
                filename="ski_intense.ogg",
                category=MusicCategory.MINIGAME,
                scene_specific=["ski"],
                duration=95.0,
                bpm=160,
                unlocked=False,
                unlock_condition=UnlockCondition.PERFECT_GAME,
                unlock_data={"game": "ski", "no_crashes": True}
            ),
            
            # Pool game music
            MusicTrack(
                id="pool_main",
                title="Splash Zone",
                filename="pool_main.ogg",
                category=MusicCategory.MINIGAME,
                scene_specific=["pool"],
                duration=100.0,
                bpm=125
            ),
            MusicTrack(
                id="pool_party",
                title="Pool Party Vibes",
                filename="pool_party.ogg",
                category=MusicCategory.MINIGAME,
                scene_specific=["pool"],
                duration=110.0,
                bpm=128,
                unlocked=False,
                unlock_condition=UnlockCondition.SCORE_THRESHOLD,
                unlock_data={"game": "pool", "score": 5000}
            ),
            
            # Vegas game music
            MusicTrack(
                id="vegas_main",
                title="Neon Nights",
                filename="vegas_main.ogg",
                category=MusicCategory.MINIGAME,
                scene_specific=["vegas"],
                duration=120.0,
                bpm=115
            ),
            MusicTrack(
                id="vegas_boss",
                title="Boss Battle Bonanza",
                filename="vegas_boss.ogg",
                category=MusicCategory.MINIGAME,
                scene_specific=["vegas"],
                duration=85.0,
                bpm=140,
                unlocked=False,
                unlock_condition=UnlockCondition.COMPLETION,
                unlock_data={"game": "vegas", "boss_defeated": True}
            ),
            
            # Victory music
            MusicTrack(
                id="victory_short",
                title="You Did It!",
                filename="victory_short.ogg",
                category=MusicCategory.VICTORY,
                duration=15.0,
                bpm=130
            ),
            
            # Unlockable/Secret tracks
            MusicTrack(
                id="secret_remix",
                title="Danger Rose Remix",
                filename="secret_remix.ogg",
                category=MusicCategory.UNLOCKABLE,
                duration=200.0,
                bpm=128,
                unlocked=False,
                unlock_condition=UnlockCondition.EASTER_EGG,
                unlock_data={"secret_code": "FAMILY"}
            ),
            MusicTrack(
                id="dev_track",
                title="Developer's Jam",
                filename="dev_track.ogg",
                category=MusicCategory.UNLOCKABLE,
                duration=180.0,
                bpm=135,
                unlocked=False,
                unlock_condition=UnlockCondition.SECRET_AREA,
                unlock_data={"hidden_door": "hub_secret"}
            ),
            MusicTrack(
                id="speedrun_theme",
                title="Lightning Fast",
                filename="speedrun_theme.ogg",
                category=MusicCategory.UNLOCKABLE,
                duration=75.0,
                bpm=180,
                unlocked=False,
                unlock_condition=UnlockCondition.TIME_TRIAL,
                unlock_data={"all_games_under": 60}  # Complete all games in under 60 seconds total
            )
        ]
        
        # Add tracks to library
        for track in default_tracks:
            self.tracks[track.id] = track
            if track.unlocked:
                self.unlocked_tracks.add(track.id)
        
        # Create default playlists
        self.playlists = {
            "hub_playlist": ["hub_cozy", "hub_upbeat"],
            "ski_playlist": ["ski_main", "ski_intense"],
            "pool_playlist": ["pool_main", "pool_party"],
            "vegas_playlist": ["vegas_main", "vegas_boss"],
            "unlockables": ["secret_remix", "dev_track", "speedrun_theme"],
            "all_tracks": list(self.tracks.keys())
        }
        
        # Set up jukebox with unlocked hub tracks
        self._update_jukebox_tracks()
    
    def get_scene_music_options(self, scene_name: str) -> List[MusicTrack]:
        """Get available music options for a specific scene.
        
        Args:
            scene_name: Name of the scene
            
        Returns:
            List of available music tracks for the scene
        """
        options = []
        for track in self.tracks.values():
            if (track.unlocked and 
                (scene_name in track.scene_specific or 
                 track.category == MusicCategory.HUB)):
                options.append(track)
        
        return options
    
    def play_scene_music(self, scene_name: str, track_id: Optional[str] = None):
        """Play appropriate music for a scene.
        
        Args:
            scene_name: Name of the scene
            track_id: Specific track to play (optional)
        """
        if track_id and track_id in self.tracks and self.tracks[track_id].unlocked:
            # Play specific track
            self.play_track(track_id)
        else:
            # Auto-select appropriate track
            options = self.get_scene_music_options(scene_name)
            if options:
                # Prefer scene-specific tracks
                scene_tracks = [t for t in options if scene_name in t.scene_specific]
                if scene_tracks:
                    track = random.choice(scene_tracks)
                else:
                    track = random.choice(options)
                self.play_track(track.id)
    
    def play_track(self, track_id: str) -> bool:
        """Play a specific music track.
        
        Args:
            track_id: ID of the track to play
            
        Returns:
            True if track was played successfully
        """
        if track_id not in self.tracks:
            print(f"Warning: Track '{track_id}' not found")
            return False
        
        track = self.tracks[track_id]
        
        if not track.unlocked:
            print(f"Warning: Track '{track.title}' is not unlocked")
            return False
        
        # Get full path to music file
        music_path = get_music_path(track.filename)
        
        if not os.path.exists(music_path):
            print(f"Warning: Music file not found: {music_path}")
            return False
        
        # Play through sound manager
        if self.sound_manager:
            self.sound_manager.play_music(music_path)
            self.current_track = track
            
            # Notify callbacks
            for callback in self.track_change_callbacks:
                callback(track)
            
            return True
        
        return False
    
    def check_unlock_conditions(self, game_data: Dict) -> List[str]:
        """Check and unlock tracks based on game data.
        
        Args:
            game_data: Dictionary with game progress data
            
        Returns:
            List of newly unlocked track IDs
        """
        newly_unlocked = []
        
        for track_id, track in self.tracks.items():
            if track.unlocked or not track.unlock_condition:
                continue
            
            if self._check_track_unlock_condition(track, game_data):
                track.unlocked = True
                self.unlocked_tracks.add(track_id)
                newly_unlocked.append(track_id)
                
                # Notify callbacks
                for callback in self.unlock_callbacks:
                    callback(track)
                
                print(f"🎵 New music unlocked: {track.title}")
        
        if newly_unlocked:
            self._update_jukebox_tracks()
            self._save_unlocked_tracks()
        
        return newly_unlocked
    
    def _check_track_unlock_condition(self, track: MusicTrack, game_data: Dict) -> bool:
        """Check if a track's unlock condition is met.
        
        Args:
            track: Track to check
            game_data: Game progress data
            
        Returns:
            True if condition is met
        """
        condition = track.unlock_condition
        data = track.unlock_data
        
        if condition == UnlockCondition.SCORE_THRESHOLD:
            if "game" in data:
                # Game-specific score
                game_scores = game_data.get("game_scores", {})
                return game_scores.get(data["game"], 0) >= data.get("score", 0)
            else:
                # Total score across all games
                total_score = sum(game_data.get("game_scores", {}).values())
                return total_score >= data.get("total_score", 0)
        
        elif condition == UnlockCondition.PERFECT_GAME:
            game_name = data.get("game")
            if game_name:
                perfect_games = game_data.get("perfect_games", [])
                return game_name in perfect_games
        
        elif condition == UnlockCondition.COMPLETION:
            game_name = data.get("game")
            if game_name:
                completed = game_data.get("games_completed", [])
                return game_name in completed
        
        elif condition == UnlockCondition.EASTER_EGG:
            secret_code = data.get("secret_code")
            if secret_code:
                found_codes = game_data.get("easter_eggs", [])
                return secret_code in found_codes
        
        elif condition == UnlockCondition.SECRET_AREA:
            area_id = data.get("hidden_door")
            if area_id:
                found_areas = game_data.get("secret_areas", [])
                return area_id in found_areas
        
        elif condition == UnlockCondition.TIME_TRIAL:
            time_limit = data.get("all_games_under")
            if time_limit:
                total_time = sum(game_data.get("best_times", {}).values())
                return total_time <= time_limit
        
        return False
    
    def get_jukebox_tracks(self) -> List[MusicTrack]:
        """Get tracks available in the jukebox.
        
        Returns:
            List of tracks available for jukebox selection
        """
        return [self.tracks[track_id] for track_id in self.jukebox_tracks 
                if track_id in self.tracks]
    
    def jukebox_select_track(self, index: int) -> bool:
        """Select a track in the jukebox.
        
        Args:
            index: Index of the track to select
            
        Returns:
            True if selection was successful
        """
        if 0 <= index < len(self.jukebox_tracks):
            self.jukebox_selection = index
            return True
        return False
    
    def jukebox_play_selected(self) -> bool:
        """Play the currently selected jukebox track.
        
        Returns:
            True if track was played
        """
        if 0 <= self.jukebox_selection < len(self.jukebox_tracks):
            track_id = self.jukebox_tracks[self.jukebox_selection]
            return self.play_track(track_id)
        return False
    
    def jukebox_next_track(self):
        """Move to next track in jukebox."""
        if self.jukebox_tracks:
            self.jukebox_selection = (self.jukebox_selection + 1) % len(self.jukebox_tracks)
    
    def jukebox_prev_track(self):
        """Move to previous track in jukebox."""
        if self.jukebox_tracks:
            self.jukebox_selection = (self.jukebox_selection - 1) % len(self.jukebox_tracks)
    
    def get_unlock_hints(self) -> Dict[str, str]:
        """Get hints for unlocking locked tracks.
        
        Returns:
            Dictionary mapping track titles to unlock hints
        """
        hints = {}
        
        for track in self.tracks.values():
            if not track.unlocked and track.unlock_condition:
                hint = self._generate_unlock_hint(track)
                hints[track.title] = hint
        
        return hints
    
    def _generate_unlock_hint(self, track: MusicTrack) -> str:
        """Generate a hint for unlocking a track.
        
        Args:
            track: Track to generate hint for
            
        Returns:
            Hint string
        """
        condition = track.unlock_condition
        data = track.unlock_data
        
        if condition == UnlockCondition.SCORE_THRESHOLD:
            if "game" in data:
                return f"Score {data['score']} points in {data['game'].title()}"
            else:
                return f"Score {data['total_score']} total points across all games"
        
        elif condition == UnlockCondition.PERFECT_GAME:
            game_name = data.get("game", "a game")
            return f"Complete {game_name.title()} without any mistakes"
        
        elif condition == UnlockCondition.COMPLETION:
            game_name = data.get("game", "a game")
            return f"Complete {game_name.title()}"
        
        elif condition == UnlockCondition.EASTER_EGG:
            return "Find a hidden secret in the game"
        
        elif condition == UnlockCondition.SECRET_AREA:
            return "Discover a hidden area"
        
        elif condition == UnlockCondition.TIME_TRIAL:
            time_limit = data.get("all_games_under", 60)
            return f"Complete all games in under {time_limit} seconds total"
        
        return "Complete special challenge"
    
    def _update_jukebox_tracks(self):
        """Update the list of tracks available in the jukebox."""
        # Include all unlocked hub and unlockable tracks
        self.jukebox_tracks = []
        
        for track_id, track in self.tracks.items():
            if (track.unlocked and 
                track.category in [MusicCategory.HUB, MusicCategory.UNLOCKABLE]):
                self.jukebox_tracks.append(track_id)
        
        # Sort by title for consistent ordering
        self.jukebox_tracks.sort(key=lambda tid: self.tracks[tid].title)
        
        # Reset selection if needed
        if self.jukebox_selection >= len(self.jukebox_tracks):
            self.jukebox_selection = 0
    
    def _load_unlocked_tracks(self):
        """Load unlocked tracks from save file."""
        try:
            save_path = "music_unlocks.json"
            if os.path.exists(save_path):
                with open(save_path, 'r') as f:
                    data = json.load(f)
                
                unlocked = set(data.get("unlocked_tracks", []))
                
                # Apply unlocked status
                for track_id in unlocked:
                    if track_id in self.tracks:
                        self.tracks[track_id].unlocked = True
                        self.unlocked_tracks.add(track_id)
                
                self._update_jukebox_tracks()
                
        except (json.JSONDecodeError, FileNotFoundError):
            # No save file or corrupted - use defaults
            pass
    
    def _save_unlocked_tracks(self):
        """Save unlocked tracks to file."""
        try:
            save_data = {
                "unlocked_tracks": list(self.unlocked_tracks),
                "version": "1.0"
            }
            
            with open("music_unlocks.json", 'w') as f:
                json.dump(save_data, f, indent=2)
                
        except IOError as e:
            print(f"Error saving music unlocks: {e}")
    
    def export_music_library(self, path: str):
        """Export music library to JSON file.
        
        Args:
            path: Path to export to
        """
        library_data = {
            "tracks": {tid: track.to_dict() for tid, track in self.tracks.items()},
            "playlists": self.playlists,
            "conversion_settings": self.conversion_settings,
            "version": "1.0"
        }
        
        with open(path, 'w') as f:
            json.dump(library_data, f, indent=2)
    
    def register_track_change_callback(self, callback: Callable):
        """Register callback for track changes.
        
        Args:
            callback: Function to call when track changes
        """
        self.track_change_callbacks.append(callback)
    
    def register_unlock_callback(self, callback: Callable):
        """Register callback for track unlocks.
        
        Args:
            callback: Function to call when track is unlocked
        """
        self.unlock_callbacks.append(callback)