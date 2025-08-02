# Drive Game Audio Requirements

This document outlines the audio files needed for "The Drive" racing minigame and their specifications.

## Music Tracks

All music files should be placed in `assets/audio/music/` and use OGG Vorbis format.

### Main Racing Tracks

#### 1. Highway Dreams (Main Theme)
- **File**: `drive_highway_dreams.ogg`
- **Style**: OutRun-inspired synthwave/80s electronic
- **BPM**: ~125
- **Length**: 3-4 minutes for seamless looping
- **Mood**: Cruising, nostalgic, uplifting
- **Description**: The quintessential driving song - evokes endless highways and freedom
- **Loop Points**: Preview starts at 15 seconds
- **Instruments**: Synthesizers, electric piano, smooth bass, steady drums

#### 2. Sunset Cruise (Relaxed Theme)  
- **File**: `drive_sunset_cruise.ogg`
- **Style**: Chillwave/ambient electronic
- **BPM**: ~108
- **Length**: 3-4 minutes for seamless looping
- **Mood**: Relaxed, peaceful, contemplative
- **Description**: Perfect for a leisurely drive as the sun sets
- **Loop Points**: Preview starts at 20 seconds
- **Instruments**: Soft pads, gentle arpeggios, subtle percussion, ambient textures

#### 3. Turbo Rush (High Energy Theme)
- **File**: `drive_turbo_rush.ogg`
- **Style**: High-energy synthwave/eurobeat
- **BPM**: ~140
- **Length**: 3-4 minutes for seamless looping
- **Mood**: Intense, exciting, adrenaline-pumping
- **Description**: Fast-paced beats for competitive racing
- **Loop Points**: Preview starts at 10 seconds
- **Instruments**: Driving synths, pumping bass, fast hi-hats, energetic leads

### Music Technical Specifications

```yaml
Format: OGG Vorbis
Sample Rate: 44100 Hz
Channels: Stereo
Bitrate: 128-192 kbps
Dynamic Range: Moderate compression for consistent volume
Loop Points: Seamless loops with proper fade points
Preview Points: Designated start times for 15-30 second previews
```

## Sound Effects

All SFX files should be placed in `assets/audio/sfx/` and use OGG Vorbis format.

### UI Sounds (for Music Selection)

#### Music Selection Interface
- **File**: `ui_preview_start.ogg`
- **Description**: Gentle chime when starting music preview
- **Length**: 0.5-1.0 seconds
- **Volume**: Moderate

- **File**: `ui_confirm.ogg` 
- **Description**: Positive confirmation sound for track selection
- **Length**: 0.5-1.0 seconds
- **Volume**: Clear but not overpowering

- **File**: `ui_cancel.ogg`
- **Description**: Subtle negative sound for cancellation
- **Length**: 0.3-0.7 seconds  
- **Volume**: Gentle

### Race Stingers (Musical Event Sounds)

#### Racing Events
- **File**: `stinger_crash.ogg`
- **Description**: Musical stinger for crashes (dramatic but not harsh)
- **Length**: 1-2 seconds
- **Style**: Dramatic chord or sound effect
- **Volume**: Prominent but not jarring

- **File**: `stinger_boost.ogg` 
- **Description**: Energetic musical flourish for boost activation
- **Length**: 1-1.5 seconds
- **Style**: Rising synth or triumphant chord
- **Volume**: Exciting and noticeable

- **File**: `stinger_victory.ogg`
- **Description**: Victory fanfare for winning races
- **Length**: 2-4 seconds
- **Style**: Celebratory musical phrase
- **Volume**: Loud and triumphant

- **File**: `stinger_final_lap.ogg`
- **Description**: Tension-building sound for final lap
- **Length**: 1-2 seconds
- **Style**: Dramatic build-up or warning sound
- **Volume**: Attention-grabbing

- **File**: `stinger_position_up.ogg`
- **Description**: Positive musical note for improving position
- **Length**: 0.5-1.0 seconds
- **Style**: Ascending musical phrase
- **Volume**: Encouraging

- **File**: `stinger_position_down.ogg`
- **Description**: Neutral/slightly negative sound for losing position
- **Length**: 0.5-1.0 seconds
- **Style**: Descending musical phrase or neutral tone
- **Volume**: Noticeable but not discouraging

### SFX Technical Specifications

```yaml
Format: OGG Vorbis
Sample Rate: 44100 Hz
Channels: Mono (for SFX) or Stereo (for stingers)
Bitrate: 96-128 kbps
Length: Keep under 5 seconds for responsiveness
Volume: Normalized to -6dB to prevent clipping
```

## Audio Integration Points

### Scene Manager Integration

The Drive scene should be added to the scene manager's music mapping:

```python
# In src/scene_manager.py, update _handle_music_transition():
music_map = {
    SCENE_TITLE: "title_theme.ogg",
    SCENE_HUB_WORLD: "hub_theme.ogg", 
    SCENE_SKI_GAME: "ski_theme.ogg",
    SCENE_VEGAS_GAME: "vegas_theme.ogg",
    SCENE_POOL_GAME: "pool_theme.ogg",
    SCENE_DRIVE_GAME: None,  # Drive handles its own music selection
}
```

### Hub World Integration

The Drive minigame should be accessible from the Hub World. Add a door/portal that transitions to `SCENE_DRIVE_GAME`.

### Leaderboard Integration

The Drive game should submit scores to the leaderboard system using the existing high score manager.

## Implementation Status

- ✅ Music selection UI component (`MusicSelector`)
- ✅ Race music manager (`RaceMusicManager`) 
- ✅ Drive scene with music integration (`DriveGame`)
- ✅ Audio file path structure
- ⚠️ Audio files need to be created/sourced
- ⚠️ Scene manager integration needed
- ⚠️ Hub world door/access needed

## Audio File Sourcing

### Recommended Sources for Royalty-Free Music:
1. **Freesound.org** - Community-driven free sounds
2. **OpenGameArt.org** - Game-specific audio assets
3. **Incompetech.com** - Kevin MacLeod's royalty-free music
4. **Pixabay Audio** - Free music and sound effects
5. **Custom Creation** - Using DAWs like GarageBand, FL Studio, or Reaper

### Style References:
- **OutRun (1986)** - Original arcade racing music
- **Kavinsky** - Modern synthwave artist
- **FM-84** - Retro synthwave
- **Dance With The Dead** - Dark synthwave
- **Power Trip** - High-energy electronic

## Testing Checklist

- [ ] Music selection interface works correctly
- [ ] All three tracks can be selected and previewed
- [ ] Music starts properly when race begins
- [ ] Dynamic music adjustments work (pitch/volume changes)
- [ ] Stingers play at appropriate times
- [ ] Music ducking works for important sounds
- [ ] Smooth transitions between states
- [ ] Volume controls affect race music appropriately
- [ ] Memory usage is reasonable
- [ ] No audio artifacts or glitches

## Future Enhancements

- **Custom Loop Points**: Implement precise loop point handling for seamless music
- **Adaptive Music**: Change music based on race position or time remaining
- **More Tracks**: Add additional music tracks with different styles
- **Music Mixing**: Fade between track layers based on race intensity
- **Player Preferences**: Remember selected tracks between sessions
- **Rhythm Game Elements**: Sync some gameplay elements to the beat