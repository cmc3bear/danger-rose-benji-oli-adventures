# Issue #26: Missing Player EV Vehicle Sprites

## Problem
Player vehicle sprites were missing, causing the game to show placeholder rectangles instead of the designed EV vehicles.

## Root Cause
1. Vehicle sprites were named with "ev_" prefix in assets (`ev_professional.png`, `ev_kids_drawing.png`)
2. The sprite loader was looking for files without the prefix
3. Drive minigame door was not registered in the hub world
4. Scene manager was missing Drive game registration

## Solution Implemented

### 1. Fixed Sprite Loading
Updated `load_vehicle_sprite()` in `sprite_loader.py` to include "ev_" prefix:
```python
vehicle_path = os.path.join(project_root, "assets", "images", "vehicles", f"ev_{vehicle_name}.png")
```

### 2. Added Drive Door to Hub
Updated `hub.py` to include the purple Drive door:
```python
Door(600, 100, 100, 150, "drive", "Highway Drive", (128, 0, 128)),  # Purple door
```

### 3. Registered Drive Scene
- Added `SCENE_DRIVE_GAME = "drive_game"` to `constants.py`
- Imported and registered `DriveGame` in `scene_manager.py`
- Added drive scene to pause-allowed scenes
- Added "drive" transition handler

## Files Modified
- `src/utils/sprite_loader.py`: Fixed vehicle sprite path
- `src/scenes/hub.py`: Added Drive door
- `src/config/constants.py`: Added SCENE_DRIVE_GAME constant
- `src/scene_manager.py`: Registered Drive scene
- Retrieved `ev_professional.png` and `ev_kids_drawing.png` from git history

## Testing
- Verify EV sprites load correctly in vehicle selection
- Check that selected vehicle appears in game
- Ensure Drive door appears in hub world
- Test scene transitions work properly

## Status
✅ Implemented and tested