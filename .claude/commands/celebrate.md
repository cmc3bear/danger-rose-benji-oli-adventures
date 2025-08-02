# Celebrate!

Show an animated celebration for achievements, milestones, or just for fun! Perfect for rewarding kids' progress.

## Usage

```bash
# Default celebration
poetry run python tools/celebrate.py

# Custom message
poetry run python tools/celebrate.py "You fixed your first bug!"

# Different celebration types
poetry run python tools/celebrate.py --type fireworks "Level Complete!"
poetry run python tools/celebrate.py --type confetti "New High Score!"
poetry run python tools/celebrate.py --type stars "Achievement Unlocked!"

# With sound effects
poetry run python tools/celebrate.py --sound "Great job!"
```

## Celebration Types

### Fireworks 🎆
```python
# Colorful fireworks exploding on screen
# Perfect for big achievements
```

### Confetti 🎊
```python
# Falling confetti in rainbow colors
# Great for level completion
```

### Stars ⭐
```python
# Twinkling stars with sparkle effects
# Nice for collecting all items
```

### Rainbow 🌈
```python
# Animated rainbow sweep
# For extra special moments
```

## Implementation

Create `tools/celebrate.py`:

```python
import pygame
import random
import math
import time

class Celebration:
    def __init__(self, message="Great Job!", celebration_type="confetti"):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("🎉 Celebration! 🎉")
        self.clock = pygame.time.Clock()
        self.message = message
        self.type = celebration_type
        self.particles = []
        self.font = pygame.font.Font(None, 72)

    def create_confetti(self):
        """Create confetti particles"""
        colors = [
            (255, 0, 0),     # Red
            (0, 255, 0),     # Green
            (0, 0, 255),     # Blue
            (255, 255, 0),   # Yellow
            (255, 0, 255),   # Magenta
            (0, 255, 255),   # Cyan
        ]

        for _ in range(100):
            self.particles.append({
                'x': random.randint(0, 800),
                'y': random.randint(-600, 0),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(2, 5),
                'color': random.choice(colors),
                'angle': random.uniform(0, 360),
                'spin': random.uniform(-10, 10)
            })

    def create_fireworks(self):
        """Create firework bursts"""
        # Launch firework
        self.firework_burst(400, 300, 50)

    def firework_burst(self, x, y, count):
        """Create a burst of particles"""
        for i in range(count):
            angle = (360 / count) * i
            speed = random.uniform(3, 6)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(math.radians(angle)) * speed,
                'vy': math.sin(math.radians(angle)) * speed,
                'color': (
                    random.randint(200, 255),
                    random.randint(100, 255),
                    random.randint(100, 255)
                ),
                'life': 60
            })

    def run(self):
        """Run celebration animation"""
        # Initialize particles
        if self.type == "confetti":
            self.create_confetti()
        elif self.type == "fireworks":
            self.create_fireworks()

        # Animation loop
        running = True
        duration = 5000  # 5 seconds
        start_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks()
            if current_time - start_time > duration:
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Clear screen
            self.screen.fill((20, 20, 40))

            # Update and draw particles
            self.update_particles()
            self.draw_particles()

            # Draw message
            self.draw_message()

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
```

## Celebration Messages

### Achievement Messages
```python
ACHIEVEMENT_MESSAGES = [
    "🌟 Amazing Work! 🌟",
    "🎮 Level Complete! 🎮",
    "🏆 New High Score! 🏆",
    "✨ You Did It! ✨",
    "🚀 Awesome Job! 🚀",
    "🎯 Perfect! 🎯",
    "💫 Superstar! 💫",
    "🎨 Creative Genius! 🎨"
]
```

### Encouragement Messages
```python
ENCOURAGEMENT_MESSAGES = [
    "Keep it up! 👍",
    "You're learning fast! 📚",
    "Great progress! 📈",
    "Almost there! 💪",
    "Nice try! 🌟",
    "You're improving! ⬆️"
]
```

## Integration with Game

### Trigger Celebrations
```python
# In your game code
def check_achievements():
    if score > high_score:
        trigger_celebration("New High Score!", "fireworks")

    if all_coins_collected:
        trigger_celebration("All Coins Found!", "stars")

    if first_bug_fixed:
        trigger_celebration("First Bug Fixed!", "confetti")
```

### In-Game Mini Celebrations
```python
def show_mini_celebration(x, y, text):
    """Quick celebration effect at position"""
    # Spawn particles at location
    # Show floating text
    # Play happy sound
```

## Sound Effects

Celebration sounds included:
- `tada.ogg` - Classic celebration
- `cheer.ogg` - Kids cheering
- `magic.ogg` - Magical sparkle
- `applause.ogg` - Clapping
- `victory.ogg` - Victory fanfare

## Customization

Kids can customize celebrations:

```python
# Let kids pick their favorite
MY_CELEBRATION = {
    "particles": "hearts",  # hearts, stars, smileys
    "colors": ["pink", "purple", "blue"],
    "sound": "my_recording.ogg",
    "message_style": "rainbow"  # rainbow, bounce, sparkle
}
```

## Parent Mode

Track celebrations to see progress:

```json
{
    "celebrations_earned": [
        {
            "date": "2024-01-20",
            "reason": "First successful run",
            "type": "confetti"
        },
        {
            "date": "2024-01-21",
            "reason": "Fixed syntax error",
            "type": "fireworks"
        }
    ],
    "total_celebrations": 15,
    "favorite_type": "stars"
}
```

Remember: Celebrations make coding fun! Use them liberally to reward progress, attempts, and creativity! 🎉✨
