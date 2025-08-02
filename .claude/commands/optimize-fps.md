# Optimize FPS

Profile and optimize game performance to maintain smooth 60 FPS gameplay.

## Usage

```bash
# Profile current scene
poetry run python tools/fps_profiler.py

# Profile specific scene
poetry run python tools/fps_profiler.py --scene ski_game

# Run with performance overlay
PROFILE=true SHOW_FPS=true poetry run python src/main.py

# Generate performance report
poetry run python tools/fps_profiler.py --report

# Auto-optimize settings
poetry run python tools/fps_profiler.py --auto-optimize
```

## Performance Profiling

### Quick Performance Check
```bash
# See current FPS in-game
SHOW_FPS=true poetry run python src/main.py

# Detailed frame timing
DEBUG=true PROFILE=true poetry run python src/main.py
```

### Profiling Tools

Create `tools/fps_profiler.py`:

```python
import cProfile
import pstats
import pygame
import time
from collections import deque

class FPSProfiler:
    def __init__(self, target_fps=60):
        self.target_fps = target_fps
        self.frame_times = deque(maxlen=300)  # 5 seconds at 60 FPS
        self.performance_events = []

    def profile_scene(self, scene_name):
        """Profile specific scene performance"""
        profiler = cProfile.Profile()
        profiler.enable()

        # Run scene for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            frame_start = time.time()

            # Scene update/draw
            scene.update(dt)
            scene.draw(screen)

            frame_time = time.time() - frame_start
            self.frame_times.append(frame_time)

            if frame_time > 1.0 / self.target_fps:
                self.log_performance_event(frame_time)

        profiler.disable()
        return profiler.stats
```

## Common Performance Issues

### 1. Too Many Sprites
```python
# Problem: Drawing hundreds of individual sprites
for sprite in all_sprites:
    screen.blit(sprite.image, sprite.rect)

# Solution: Use sprite groups and batch rendering
sprite_group.draw(screen)  # Much faster!
```

### 2. Unoptimized Collision Detection
```python
# Problem: Checking every sprite against every other
for sprite1 in sprites:
    for sprite2 in sprites:
        if sprite1.rect.colliderect(sprite2.rect):
            handle_collision()

# Solution: Use spatial partitioning
collision_groups = pygame.sprite.groupcollide(
    group1, group2, False, False
)
```

### 3. Surface Conversions
```python
# Problem: Using unconverted surfaces
image = pygame.image.load("sprite.png")

# Solution: Convert for faster blitting
image = pygame.image.load("sprite.png").convert_alpha()
```

## Optimization Strategies

### Automatic Optimizations
```bash
# The tool will automatically:
# 1. Convert all surfaces to optimal format
# 2. Enable sprite batching
# 3. Implement dirty rectangle updates
# 4. Reduce particle counts if needed
# 5. Adjust quality settings
```

### Performance Presets

```python
PERFORMANCE_PRESETS = {
    "ultra": {
        "particles": 1000,
        "shadows": True,
        "antialiasing": True,
        "vsync": True
    },
    "high": {
        "particles": 500,
        "shadows": True,
        "antialiasing": False,
        "vsync": True
    },
    "medium": {
        "particles": 200,
        "shadows": False,
        "antialiasing": False,
        "vsync": True
    },
    "low": {
        "particles": 50,
        "shadows": False,
        "antialiasing": False,
        "vsync": False
    }
}
```

## Performance Report

The tool generates a detailed report:

```
=== FPS Performance Report ===
Scene: ski_game
Duration: 10.0 seconds
Target FPS: 60

Performance Summary:
- Average FPS: 58.2
- Minimum FPS: 45
- Maximum FPS: 60
- Frames below target: 12%

Bottlenecks Found:
1. sprite_rendering (35% of frame time)
2. collision_detection (22% of frame time)
3. particle_updates (15% of frame time)

Recommendations:
✓ Enable sprite batching
✓ Reduce particle count to 200
✓ Use spatial grid for collisions
✓ Convert surfaces at load time

Estimated improvement: +15 FPS
```

## Scene-Specific Optimizations

### Ski Game
```python
# Reduce snow particles on slow systems
if avg_fps < 50:
    snow_particle_count = 100  # Instead of 500

# Use simpler collision shapes
player.collision_rect = player.rect.inflate(-10, -10)

# Cull off-screen obstacles
visible_obstacles = [o for o in obstacles if screen_rect.colliderect(o.rect)]
```

### Pool Game
```python
# Optimize ball physics
# Update only moving balls
active_balls = [b for b in balls if b.velocity.length() > 0.1]

# Use quadtree for ball collisions
quadtree = QuadTree(table_bounds)
for ball in active_balls:
    quadtree.insert(ball)
```

## Debug Overlay

When profiling is enabled, shows:
- Current FPS (color-coded)
- Frame time graph
- Sprite count
- Particle count
- Memory usage
- Draw calls

## Best Practices

1. **Profile before optimizing** - Don't guess!
2. **Test on target hardware** - Kids might have older PCs
3. **Provide quality options** - Let players choose
4. **Maintain gameplay** - 45 FPS stable > 60 FPS stuttering
5. **Optimize the hot path** - Focus on per-frame operations

Remember: Smooth gameplay is more important than fancy effects! 🎮⚡
