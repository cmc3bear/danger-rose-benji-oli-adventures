# Issue #35: Comprehensive Music System for Hub and All Minigames

## 🎯 Overview
Implement a complete music system that provides background music for the hub world and all minigames, with smooth transitions, volume controls, and proper audio management across scenes.

## 🔍 Problem Statement
Currently:
- Hub world has no background music
- Some minigames (Pool, Ski) lack music entirely
- No consistent music transition system between scenes
- Music can bleed between scenes (as discovered in Drive scene)
- No unified volume control or music preferences

## 🎯 Solution Requirements

### Core Music System
1. **Hub World Music**
   - Cozy, ambient background tracks (3-5 variations)
   - Dynamic music that changes based on time spent in hub
   - Smooth fade when entering minigames

2. **Minigame Music**
   - Drive: ✅ Already has music selector (3 tracks)
   - Pool: Need upbeat, competitive tracks (3 tracks)
   - Ski: Need energetic, winter-themed tracks (3 tracks)
   - Vegas: Need casino/adventure themed tracks (3 tracks)

3. **Music Management**
   - Proper scene transition handling (stop previous music)
   - Volume persistence across scenes
   - Music preferences saved to game state
   - Crossfade support for smooth transitions

## 📋 Music Track Requirements

### Hub World (3-5 tracks)
- `cozy_home_theme.mp3` - Main hub theme
- `family_gathering.mp3` - Warm, inviting melody
- `afternoon_relaxation.mp3` - Calm background music
- `evening_ambience.mp3` - Gentle evening theme
- `morning_energy.mp3` - Upbeat morning theme

### Pool Minigame (3 tracks)
- `splashdown_showdown.mp3` - Main pool theme
- `water_balloon_warriors.mp3` - Fast-paced action
- `victory_splash_anthem.mp3` - Victory celebration

### Ski Minigame (3 tracks)
- `snow_rush_showdown.mp3` - Main ski theme
- `frostbite_frenzy.mp3` - Intense downhill racing
- `pixel_peaks_victory.mp3` - Victory theme

### Vegas Minigame (3 tracks)
- `neon_fury.mp3` - Main Vegas theme
- `battle_on_the_strip.mp3` - Boss battle music
- `las_vegas_lights_up.mp3` - Victory/exploration

## 🏗️ Technical Implementation

### Enhanced Sound Manager
```python
class EnhancedSoundManager:
    def __init__(self):
        self.current_music = None
        self.music_volume = 0.7
        self.fade_duration = 1000  # ms
        
    def play_scene_music(self, scene_name: str, track: str = None):
        """Play appropriate music for scene with crossfade"""
        
    def crossfade_to(self, new_track: str, duration: int = 1000):
        """Smoothly transition between tracks"""
        
    def stop_with_fade(self, duration: int = 500):
        """Fade out current music"""
```

### Scene Music Configuration
```json
{
  "hub": {
    "tracks": ["cozy_home_theme", "family_gathering", "afternoon_relaxation"],
    "shuffle": true,
    "loop": true,
    "volume": 0.6
  },
  "pool": {
    "tracks": ["splashdown_showdown", "water_balloon_warriors"],
    "shuffle": false,
    "loop": true,
    "volume": 0.8
  }
}
```

## 🎮 User Experience

### Music Settings Menu
- Master volume slider
- Music volume slider (separate from SFX)
- Track selection for each scene
- Preview button for each track
- Mute option

### Smart Music Behavior
- Remember last played track per scene
- Don't restart music if returning to same scene quickly
- Lower volume during dialogue or important sound effects
- Gradual volume increase when entering new scenes

## 📊 Success Metrics
- All scenes have appropriate background music
- No music bleeding between scenes
- Smooth transitions (no sudden stops/starts)
- Volume preferences persist between sessions
- Music enhances gameplay atmosphere

## 🔗 Related Issues
- Issue #33: Drive minigame audio fixes
- Issue #34: Game state logging (will log music events)

## 🎯 Acceptance Criteria
- [ ] Hub world has 3-5 background music tracks
- [ ] All minigames have appropriate music (3 tracks each)
- [ ] Music transitions smoothly between scenes
- [ ] Volume controls work consistently
- [ ] Music preferences are saved
- [ ] No audio bleeding between scenes
- [ ] Music can be muted/unmuted
- [ ] All music files are optimized (MP3, <5MB each)

**Estimated Development Time**: 2-3 weeks
**Priority**: Medium (enhances game experience significantly)
**Dependencies**: Requires music asset creation/sourcing