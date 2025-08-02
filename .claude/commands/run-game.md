# Run Game

Quickly launch the Danger Rose game with various options for testing and development.

## Usage

```bash
# Run game normally
poetry run python src/main.py

# Run with debug mode
DEBUG=true poetry run python src/main.py

# Run with FPS display
SHOW_FPS=true poetry run python src/main.py

# Run specific scene
poetry run python src/main.py --scene ski_game

# Run in windowed mode with specific size
poetry run python src/main.py --windowed --size 1024x768
```

## Environment Variables

- `DEBUG=true` - Enable debug output and overlays
- `SHOW_FPS=true` - Display FPS counter
- `PROFILE=true` - Enable performance profiling
- `KID_MODE=true` - Enable kid-friendly features
- `MUTE=true` - Start with audio muted

## Command Line Arguments

- `--scene SCENE_NAME` - Start at specific scene (hub_world, ski_game, pool_game, vegas_game)
- `--character NAME` - Start with specific character (danger, rose, dad)
- `--windowed` - Force windowed mode
- `--fullscreen` - Force fullscreen mode
- `--size WIDTHxHEIGHT` - Set window size

## Quick Testing Shortcuts

```bash
# Test ski game as Rose
poetry run python src/main.py --scene ski_game --character rose

# Debug hub world
DEBUG=true SHOW_FPS=true poetry run python src/main.py --scene hub_world

# Kid-friendly mode with Danger
KID_MODE=true poetry run python src/main.py --character danger
```

## Common Issues

If the game won't start:
1. Check that all dependencies are installed: `poetry install`
2. Verify assets are present: `python tools/check_assets.py`
3. Run with debug for more info: `DEBUG=true poetry run python src/main.py`
