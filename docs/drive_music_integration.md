# Drive Music Integration Guide

This guide explains how to integrate the synthwave music tracks into "The Drive" racing minigame in Danger Rose.

## Generated Music Tracks

Three OutRun-style synthwave tracks have been created:

### 1. Highway Dreams
- **Style**: Upbeat synthwave racing theme
- **BPM**: 125
- **Key**: C major
- **Mood**: Upbeat
- **Use**: Main racing theme, default background music

### 2. Sunset Cruise  
- **Style**: Relaxed chillwave cruising theme
- **BPM**: 108
- **Key**: G major
- **Mood**: Relaxed
- **Use**: Scenic/cruise mode, exploration sections

### 3. Turbo Rush
- **Style**: High-energy intense racing theme
- **BPM**: 140
- **Key**: A minor
- **Mood**: Intense
- **Use**: Time trials, high-speed sections, boss races

## File Locations

```
assets/audio/music/drive/
├── highway_dreams.wav          # Main racing theme
├── sunset_cruise.wav           # Cruising theme
├── turbo_rush.wav             # Intense racing theme
└── music_manifest.json        # Track metadata
```

## Music Manager Usage

### Basic Integration

```python
from src.audio.drive_music_manager import DriveMusicManager

class DriveGame:
    def __init__(self):
        self.music_manager = DriveMusicManager()
    
    def start_race(self, race_type="normal"):
        # Play appropriate music for race type
        self.music_manager.play_for_race_type(race_type)
    
    def on_pause(self):
        self.music_manager.pause()
    
    def on_resume(self):
        self.music_manager.unpause()
    
    def cleanup(self):
        self.music_manager.stop()
```

### Advanced Usage

```python
# Play specific tracks
music_manager.play_highway_dreams()    # Main theme
music_manager.play_sunset_cruise()     # Relaxed
music_manager.play_turbo_rush()        # Intense

# Dynamic music based on speed
if player_speed > 200:
    music_manager.play_turbo_rush()
elif player_speed < 100:
    music_manager.play_sunset_cruise()
else:
    music_manager.play_highway_dreams()

# Volume control
music_manager.set_volume(0.7)  # 70% volume

# Check what's playing
current = music_manager.get_current_track()
if current:
    print(f"Now playing: {current['title']}")
```

## Integration Points

### 1. Game Start
```python
def start_drive_game(self):
    self.music_manager.play_highway_dreams()
    # Start with main theme
```

### 2. Speed-Based Music Switching
```python
def update_music_for_speed(self, speed):
    """Change music based on driving speed"""
    if speed > 180:  # High speed
        if self.music_manager.current_track != "turbo_rush":
            self.music_manager.play_turbo_rush()
    elif speed < 80:  # Slow/scenic
        if self.music_manager.current_track != "sunset_cruise":
            self.music_manager.play_sunset_cruise()
    else:  # Normal speed
        if self.music_manager.current_track != "highway_dreams":
            self.music_manager.play_highway_dreams()
```

### 3. Game Mode Selection
```python
def set_game_mode(self, mode):
    """Set music based on game mode"""
    music_map = {
        "cruise": "sunset_cruise",
        "time_trial": "turbo_rush", 
        "race": "highway_dreams",
        "exploration": "sunset_cruise"
    }
    
    track_id = music_map.get(mode, "highway_dreams")
    self.music_manager.play_track(track_id)
```

### 4. Menu Integration
```python
# In main menu or track selection
def show_music_options(self):
    tracks = self.music_manager.get_available_tracks()
    for track in tracks:
        # Show track selection UI
        print(f"🎵 {track['title']} - {track['description']}")
```

## Audio Settings

### Volume Controls
```python
# Master volume control
def set_music_volume(self, volume):
    self.music_manager.set_volume(volume)

# Mute/unmute
def toggle_music(self):
    if self.music_manager.is_playing():
        self.music_manager.pause()
    else:
        self.music_manager.unpause()
```

### Fade Transitions
The music manager automatically handles smooth transitions with 1-second fades when switching tracks.

## Performance Notes

### Memory Usage
- Tracks are loaded on-demand
- Only one track loaded in memory at a time
- WAV files are ~60MB each (high quality for development)

### Optimization Tips
1. **Preload**: Load tracks during game initialization
2. **Format**: Convert to OGG when ffmpeg is available (smaller files)
3. **Streaming**: For final release, consider streaming longer tracks
4. **Compression**: Optimize for web builds if needed

## Track Characteristics

### Loop Points
All tracks are designed to loop seamlessly:
- **Highway Dreams**: 90 seconds, smooth loop
- **Sunset Cruise**: 90 seconds, ambient fade
- **Turbo Rush**: 90 seconds, beat-matched loop

### Mixing Levels
- Normalized to prevent clipping
- Leave headroom for sound effects
- Stereo with subtle spatial effects

## Future Enhancements

### When Suno API is Available
1. Replace placeholder tracks with real AI-generated music
2. Generate longer variations (3-5 minutes)
3. Create additional tracks for specific scenarios:
   - Night driving theme
   - Rain/weather variations
   - Victory/completion music

### Dynamic Music Features
```python
# Possible future enhancements
def dynamic_music_update(self, game_state):
    # Adjust tempo based on excitement level
    if game_state.near_crash:
        # Increase intensity
        pass
    
    # Layer additional instruments for combos
    if game_state.combo_count > 5:
        # Add excitement layers
        pass
```

## Troubleshooting

### Common Issues

1. **No Sound**: Check pygame mixer initialization
2. **File Not Found**: Verify WAV files exist in assets/audio/music/drive/
3. **Choppy Playback**: Increase pygame mixer buffer size
4. **Memory Issues**: Consider streaming for very long tracks

### Debug Code
```python
# Add to your game for debugging
if DEBUG:
    current_track = music_manager.get_current_track()
    if current_track:
        print(f"Music: {current_track['title']} - {current_track['bpm']} BPM")
    else:
        print("Music: None")
```

## Example Scene Integration

```python
class DriveScene(Scene):
    def __init__(self):
        super().__init__()
        self.music_manager = DriveMusicManager()
        self.last_speed = 0
        
    def on_enter(self, previous_scene, data):
        # Start with main theme
        self.music_manager.play_highway_dreams()
        
    def update(self, dt):
        super().update(dt)
        
        # Update music based on player speed
        current_speed = self.player.get_speed()
        if abs(current_speed - self.last_speed) > 20:  # Significant speed change
            self.update_music_for_speed(current_speed)
            self.last_speed = current_speed
            
    def on_exit(self):
        # Fade out music when leaving
        self.music_manager.stop(fade_out=True)
        return super().on_exit()
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:  # Toggle music
                if self.music_manager.is_playing():
                    self.music_manager.pause()
                else:
                    self.music_manager.unpause()
                    
        return super().handle_event(event)
```

---

This integration provides a solid foundation for the Drive minigame's audio experience, with room for future enhancements when the Suno API becomes available.