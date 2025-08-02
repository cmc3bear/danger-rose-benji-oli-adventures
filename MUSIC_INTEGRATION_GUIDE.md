# Music Integration System Documentation

## Overview

The Danger Rose Music Integration System provides a comprehensive solution for managing scene-specific music, unlockable tracks, and an interactive jukebox experience. The system is designed to be family-friendly, performance-optimized, and extensible.

## Architecture Components

### 1. Enhanced Sound Manager (`enhanced_sound_manager.py`)
The core audio system that integrates all sound components:
- Priority-based channel management
- Spatial audio support
- Performance monitoring
- Memory management
- Event-based sound triggering

### 2. Music Manager (`music_manager.py`)
Handles music-specific functionality:
- Track metadata and organization
- Unlock condition checking
- Scene music selection
- Jukebox integration

### 3. Interactive Jukebox (`jukebox.py`)
Hub world entity for music selection:
- Intuitive menu interface
- Track browsing and selection
- Unlock hint system
- Visual feedback for track status

### 4. Audio Converter (`audio_converter.py`)
Optimizes music files for game use:
- MP3 to OGG conversion
- Quality/size optimization
- Batch processing
- Validation tools

## File Organization

```
assets/audio/music/
├── original/           # Source MP3 files
│   ├── title/
│   ├── hub/
│   ├── ski/
│   ├── pool/
│   ├── vegas/
│   └── unlockables/
└── converted/          # Optimized OGG files
    ├── title/
    ├── hub/
    ├── ski/
    ├── pool/
    ├── vegas/
    └── unlockables/
```

## Usage Examples

### Basic Scene Music Integration

```python
from src.managers.enhanced_sound_manager import EnhancedSoundManager
from src.managers.audio.music_manager import MusicManager

class GameScene:
    def __init__(self):
        self.sound_manager = EnhancedSoundManager()
        self.music_manager = MusicManager(self.sound_manager)
    
    def on_enter(self, previous_scene=None, data=None):
        # Auto-select appropriate music for this scene
        self.music_manager.play_scene_music(self.scene_name)
```

### Unlocking Music from Gameplay

```python
class PoolScene:
    def update_score(self, points):
        self.score += points
        
        # Check for music unlocks
        game_data = {
            "game_scores": {"pool": self.score},
            "games_completed": self.completed_games,
            "perfect_games": self.perfect_games
        }
        
        newly_unlocked = self.music_manager.check_unlock_conditions(game_data)
        
        if newly_unlocked:
            # Show unlock notification
            for track_id in newly_unlocked:
                track = self.music_manager.tracks[track_id]
                self.show_unlock_notification(f"🎵 Unlocked: {track.title}")
```

### Jukebox Integration in Hub

```python
class HubScene:
    def __init__(self):
        super().__init__()
        
        # Create jukebox entity
        self.jukebox = Jukebox(
            x=400, y=300,
            music_manager=self.music_manager,
            sound_manager=self.sound_manager
        )
        
        # Add to entities list
        self.entities.append(self.jukebox)
    
    def handle_event(self, event):
        # Let jukebox handle its events first
        if self.jukebox.handle_event(event):
            return "continue"
        
        return super().handle_event(event)
    
    def update(self, dt):
        super().update(dt)
        
        # Update jukebox with player position
        self.jukebox.update(dt, (self.player.x, self.player.y))
```

## Unlock Conditions Implementation

### Score-Based Unlocks
```python
# In game scenes, trigger unlock checks
def end_game(self):
    game_data = {
        "game_scores": {"pool": self.final_score}
    }
    self.music_manager.check_unlock_conditions(game_data)
```

### Easter Egg Unlocks
```python
# Hidden code entry
def check_secret_code(self, entered_code):
    if entered_code == "FAMILY":
        game_data = {
            "easter_eggs": ["FAMILY"]
        }
        self.music_manager.check_unlock_conditions(game_data)
```

### Perfect Game Unlocks
```python
# Ski game - no crashes
class SkiScene:
    def __init__(self):
        self.crashes = 0
    
    def end_game(self):
        if self.crashes == 0:
            game_data = {
                "perfect_games": ["ski"]
            }
            self.music_manager.check_unlock_conditions(game_data)
```

### Secret Area Unlocks
```python
# Hidden door discovery
def interact_with_hidden_door(self):
    game_data = {
        "secret_areas": ["hub_secret"]
    }
    self.music_manager.check_unlock_conditions(game_data)
```

## Audio Conversion Workflow

### 1. Setup Directory Structure
```bash
mkdir -p assets/audio/music/original/{title,hub,ski,pool,vegas,unlockables}
mkdir -p assets/audio/music/converted/{title,hub,ski,pool,vegas,unlockables}
```

### 2. Add Source Music Files
Place MP3 files in appropriate `original/` subdirectories:
- `title/` - Title screen music
- `hub/` - Hub world background music
- `ski/` - Ski minigame tracks  
- `pool/` - Pool minigame tracks
- `vegas/` - Vegas minigame tracks
- `unlockables/` - Special unlockable tracks

### 3. Convert Music Files
```python
from src.utils.audio_converter import AudioConverter

converter = AudioConverter()

# Convert all music with optimized settings
success = converter.batch_convert_music_library("assets/audio/music")

# Get conversion report
report = converter.get_conversion_report()
print(f"Converted {report['files_converted']} files")
print(f"Saved {report['space_saved_mb']:.1f} MB")
```

### 4. Validation
```python
# Validate converted files
results = converter.validate_converted_files("assets/audio/music/converted")
invalid_files = [f for f, valid in results.items() if not valid]

if invalid_files:
    print("Invalid files found:", invalid_files)
```

## Music Track Configuration

### Track Definition
```python
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
)
```

### Adding New Tracks
1. Add track definition to `MusicManager._initialize_music_library()`
2. Place audio file in appropriate directory
3. Set unlock conditions and requirements
4. Test unlock functionality

## Performance Optimization

### Audio Settings
- **Format**: OGG Vorbis for best compression
- **Quality**: 192kbps for balance of quality and size
- **Sample Rate**: 44.1kHz (CD quality)
- **Channels**: Stereo (2 channels)

### Memory Management
- Automatic cache cleanup for unused sounds
- Maximum cache size limits
- Lazy loading of music tracks
- Performance monitoring and warnings

### File Size Guidelines
- Hub music: < 2MB per track
- Minigame music: < 1.5MB per track  
- Victory/short clips: < 500KB per track
- Total music library: < 50MB

## Family-Friendly Design

### Accessibility Features
- Visual indicators for locked tracks
- Clear unlock hints ("Score 5000 points in Pool game")
- Large, readable jukebox interface
- Simple controls (arrow keys + Enter)

### Kid-Friendly Unlocks
- **Easy**: Score-based unlocks with reasonable targets
- **Medium**: Perfect game challenges
- **Hard**: Time trials and secret areas
- **Fun**: Easter egg codes and hidden discoveries

### Encouraging Progression
- Unlock notifications with celebration sounds
- Progress hints that guide without frustrating
- Multiple unlock paths for different play styles
- Immediate gratification for achievements

## Testing Guidelines

### Unit Tests
```python
def test_unlock_conditions():
    """Test that unlock conditions work correctly."""
    music_manager = MusicManager()
    
    # Test score unlock
    game_data = {"game_scores": {"pool": 5000}}
    unlocked = music_manager.check_unlock_conditions(game_data)
    
    assert "pool_party" in unlocked
```

### Integration Tests
```python
def test_jukebox_interaction():
    """Test jukebox functionality in hub scene."""
    hub_scene = HubScene()
    jukebox = hub_scene.jukebox
    
    # Test menu opening
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
    handled = jukebox.handle_event(event)
    
    assert handled == True
    assert jukebox.menu_open == True
```

### Performance Tests
- Music loading times < 100ms
- Memory usage stays under limits
- No frame drops during music transitions
- Smooth jukebox animations at 60 FPS

## Common Issues and Solutions

### Issue: Music Files Too Large
**Solution**: Reduce quality to 160kbps or use higher compression

### Issue: Unlock Not Triggering
**Solution**: Check game_data format and condition logic

### Issue: Jukebox Not Responsive
**Solution**: Verify input cooldown settings and event handling

### Issue: Poor Audio Quality
**Solution**: Adjust conversion settings or use higher bitrate

## Future Enhancements

### Planned Features
- Custom playlist creation
- Music visualization effects
- Rhythm-based minigames
- Community music sharing
- Advanced audio effects

### Extensibility Points
- New unlock condition types
- Additional music categories
- Enhanced jukebox features
- Integration with external music APIs

---

This music integration system provides a solid foundation for an engaging, family-friendly audio experience that grows with player progress and provides lasting entertainment value.