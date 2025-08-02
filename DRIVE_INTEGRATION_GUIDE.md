# Drive Game Integration Guide

This guide explains how to integrate "The Drive" racing minigame into the existing Danger Rose game.

## Files Created

### Core Components
- `src/ui/music_selector.py` - OutRun-style music selection interface
- `src/managers/race_music_manager.py` - Dynamic racing music management
- `src/scenes/drive.py` - Main Drive racing scene
- `tools/create_audio_placeholders.py` - Script to create placeholder audio files

### Documentation
- `DRIVE_AUDIO_REQUIREMENTS.md` - Complete audio specifications
- `DRIVE_INTEGRATION_GUIDE.md` - This integration guide

## Integration Steps

### 1. Update Scene Manager

Add the Drive scene to the scene manager by editing `src/scene_manager.py`:

```python
# Add import at the top
from src.scenes.drive import DriveGame
from src.config.constants import SCENE_DRIVE_GAME

# In __init__ method, add the scene:
self.scenes[SCENE_DRIVE_GAME] = DriveGame(self)

# Update pause_allowed_scenes list:
self.pause_allowed_scenes = [
    SCENE_HUB_WORLD,
    SCENE_VEGAS_GAME,
    SCENE_SKI_GAME,
    SCENE_POOL_GAME,
    SCENE_DRIVE_GAME,  # Add this line
]

# In _handle_music_transition method, update music_map:
music_map = {
    SCENE_TITLE: "title_theme.ogg",
    SCENE_HUB_WORLD: "hub_theme.ogg",
    SCENE_SKI_GAME: "ski_theme.ogg",
    SCENE_VEGAS_GAME: "vegas_theme.ogg",
    SCENE_POOL_GAME: "pool_theme.ogg",
    SCENE_DRIVE_GAME: None,  # Drive handles its own music
}

# In handle_event method, add drive transition:
elif result == "drive":
    self.switch_scene(SCENE_DRIVE_GAME)
```

### 2. Update Hub World

Add a door or access point to the Drive game in `src/scenes/hub.py`:

```python
# Add import
from src.config.constants import SCENE_DRIVE_GAME

# In the hub world door setup, add a drive door:
drive_door = Door(
    x=door_x_position,  # Position as needed
    y=door_y_position,
    width=door_width,
    height=door_height,
    scene_name=SCENE_DRIVE_GAME,
    door_text="Racing",
    unlock_condition=None  # Always unlocked
)
self.doors.append(drive_door)
```

### 3. Create Placeholder Audio Files

Run the placeholder creation script:

```bash
python tools/create_audio_placeholders.py
```

This creates basic audio files so the game won't crash while waiting for real audio assets.

### 4. Update Makefile (Optional)

Add convenience commands to the Makefile:

```makefile
# Run Drive game directly
run-drive:
	$(POETRY) run python src/main.py --scene drive_game

# Create audio placeholders
audio-placeholders:
	$(POETRY) run python tools/create_audio_placeholders.py
```

## Testing the Integration

### Basic Functionality Test
1. Run the game: `make run`
2. Navigate to Hub World
3. Find and enter the Racing door
4. Verify music selection screen appears
5. Select a track and confirm
6. Test racing controls (arrow keys/WASD)
7. Verify UI elements display correctly
8. Test pause functionality (ESC)

### Audio System Test
1. Verify music selection preview works (SPACE key)
2. Test race music starts when racing begins
3. Check that stingers play during events (boost, crash, etc.)
4. Verify volume controls affect race music
5. Test smooth transitions between game states

### Edge Case Testing
1. Test canceling music selection (should return to hub)
2. Test restarting races with same music
3. Test changing music between races
4. Verify memory cleanup when leaving scene

## Customization Options

### Adding More Music Tracks

To add additional music tracks, edit `src/ui/music_selector.py`:

```python
# Add to MusicSelector.DRIVE_TRACKS list:
MusicTrack(
    name="custom_track",
    display_name="Custom Track Name", 
    description="Description of the track",
    filename="drive_custom_track.ogg",
    bpm=130,
    mood="energetic",
    preview_start=25.0
),
```

### Customizing Racing Mechanics

Edit `src/scenes/drive.py` to modify:
- Speed and acceleration values
- Road curvature patterns  
- Crash conditions
- Scoring system
- Race duration

### Styling the Music Selector

Modify `src/ui/music_selector.py` to change:
- Colors and fonts
- Animation effects
- Layout and positioning
- Track information display

## Performance Considerations

### Memory Usage
- Music files are loaded on-demand, not preloaded
- Sound effect cache is managed by the base SoundManager
- Track selection UI is lightweight

### Audio Quality vs. File Size
- Use 128-192 kbps for music (good quality, reasonable size)
- Use 96-128 kbps for short sound effects
- Consider mono for non-positional SFX to save space

### Loading Times
- Music preview loads the full track (might have slight delay)
- Consider adding loading indicators for large music files
- Placeholder files should load instantly

## Troubleshooting

### Common Issues

**"Music file not found" error:**
- Verify audio files exist in `assets/audio/music/`
- Check file names match exactly (case-sensitive)
- Run `python tools/create_audio_placeholders.py`

**Music selection doesn't appear:**
- Check scene manager integration steps
- Verify SCENE_DRIVE_GAME constant is imported
- Check hub world door configuration

**No sound during racing:**
- Verify pygame mixer is initialized
- Check volume settings in game options
- Test with placeholder audio files first

**Performance issues:**
- Check if multiple music tracks are playing simultaneously
- Verify audio files aren't too large (>10MB)
- Monitor memory usage with Task Manager

### Debug Tools

Add debug information to see music system state:

```python
# In drive.py, add to _draw_racing_ui method:
if DEBUG_MODE:
    music_info = self.race_music_manager.get_music_info()
    debug_text = f"Track: {music_info['track']}, Vol: {music_info['volume']:.2f}"
    debug_surface = self.font_small.render(debug_text, True, COLOR_WHITE)
    screen.blit(debug_surface, (10, self.screen_height - 30))
```

## Future Enhancements

### Planned Features
- **Multiplayer Racing**: Local split-screen or network play
- **Track Editor**: Let players create custom race courses
- **More Music Genres**: Electronic, rock, orchestral options
- **Advanced Audio**: 3D positional audio, dynamic mixing
- **Achievements**: Racing-specific achievement system

### Community Contributions
- **Custom Music Packs**: Community-created music collections
- **Translations**: Localize music descriptions and UI text
- **Visual Mods**: Custom car sprites and track themes
- **Accessibility**: Audio cues for vision-impaired players

## API Reference

### MusicSelector Class
```python
selector = MusicSelector(width, height, sound_manager, tracks)
selector.set_track_selected_callback(callback_function)
selector.handle_event(event)  # Returns action string
selector.update(dt)
selector.draw(screen)
```

### RaceMusicManager Class  
```python
manager = RaceMusicManager(sound_manager)
manager.select_track(music_track)
manager.start_race_music(fade_in_ms=1000)
manager.update_race_state(race_state)
manager.play_stinger("boost")
manager.duck_music(duration_ms=1500)
```

### RaceState Dataclass
```python
state = RaceState(
    speed=0.8,              # 0.0 to 1.0
    position=3,             # Current race position
    total_racers=8,         # Total number of racers
    time_remaining=45.0,    # Seconds left
    is_boost=True,          # Boost active
    is_crash=False,         # Just crashed
    is_final_lap=False,     # Final lap warning
    is_victory=False,       # Won the race
    is_game_over=False      # Race completed
)
```

This integration guide should provide everything needed to successfully add The Drive racing game to the Danger Rose project!