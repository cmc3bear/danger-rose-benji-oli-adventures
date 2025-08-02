# Kid Challenge

Create fun coding challenges for kids to learn programming through game development!

## Usage

```bash
# Generate a random easy challenge
poetry run python tools/kid_challenge.py --difficulty easy

# Create specific topic challenge
poetry run python tools/kid_challenge.py --topic variables --difficulty medium

# Generate challenge with hints
poetry run python tools/kid_challenge.py --topic loops --hints

# Create visual challenge
poetry run python tools/kid_challenge.py --topic drawing --visual
```

## Challenge Topics

### Easy Challenges (Ages 8-10)
- **variables**: Change character names and colors
- **numbers**: Modify jump height and speed
- **colors**: Create rainbow effects
- **sounds**: Add new sound effects
- **print**: Display messages on screen

### Medium Challenges (Ages 10-12)
- **loops**: Make patterns and animations
- **functions**: Create new character abilities
- **lists**: Manage collectible items
- **if_statements**: Add game rules
- **drawing**: Design new sprites

### Hard Challenges (Ages 12+)
- **classes**: Create new enemy types
- **physics**: Modify game physics
- **algorithms**: Improve AI behavior
- **data**: Track high scores
- **events**: Add new controls

## Example Challenges

### Easy: Change Jump Power
```python
# 🎮 Challenge: Make Danger jump SUPER high!
# Find this line in the code:
jump_power = 10

# Try changing it to:
jump_power = 20  # Wow! So high!

# 🌟 Bonus: Can you make a "mega jump" button?
```

### Medium: Create a Victory Dance
```python
# 🎮 Challenge: Make Rose dance when she wins!
def victory_dance():
    # Add your dance moves here!
    rose.spin()
    rose.jump()
    rose.sparkle()

    # 🌟 Bonus: Add music to the dance!
```

### Hard: Design a New Power-Up
```python
# 🎮 Challenge: Create a speed boost power-up!
class SpeedBoost(PowerUp):
    def __init__(self):
        super().__init__()
        self.duration = 5  # seconds
        self.speed_multiplier = 2

    def activate(self, player):
        # Your code here!
        # Make the player go zoom! 🏃‍♂️💨
```

## Challenge Generator Tool

Create `tools/kid_challenge.py`:

```python
import random

CHALLENGES = {
    "easy": {
        "variables": [
            "Change the player's starting lives from 3 to 5",
            "Make coins worth 20 points instead of 10",
            "Change the game title to include your name"
        ],
        "colors": [
            "Make the sky purple instead of blue",
            "Give Danger a red shirt",
            "Create a rainbow trail effect"
        ]
    },
    "medium": {
        "loops": [
            "Make stars twinkle using a loop",
            "Create a pattern of 10 platforms",
            "Make confetti fall when you win"
        ],
        "functions": [
            "Create a function that makes the player do a flip",
            "Add a heal() function that restores health",
            "Make a celebrate() function with sounds"
        ]
    }
}

def generate_challenge(difficulty="easy", topic=None):
    if topic:
        challenges = CHALLENGES[difficulty][topic]
    else:
        all_challenges = []
        for topic_challenges in CHALLENGES[difficulty].values():
            all_challenges.extend(topic_challenges)
        challenges = all_challenges

    return random.choice(challenges)
```

## Visual Challenges

For visual learners, generate challenges with pictures:

```
🎮 Visual Challenge: Platform Pattern
╔═══════════════════════════╗
║ Create this pattern:      ║
║                           ║
║ ▓▓    ▓▓    ▓▓    ▓▓    ║
║    ▓▓    ▓▓    ▓▓    ▓▓ ║
║ ▓▓    ▓▓    ▓▓    ▓▓    ║
║                           ║
║ Hint: Use a loop!         ║
╚═══════════════════════════╝
```

## Celebration Messages

When kids complete challenges:

```python
CELEBRATIONS = [
    "🎉 Amazing! You're a coding superstar!",
    "🚀 Wow! You just leveled up your skills!",
    "🌟 Fantastic work! You solved it!",
    "🎮 Game developer achievement unlocked!",
    "✨ Magic! Your code works perfectly!"
]
```

## Hint System

Progressive hints for stuck kids:

```python
HINTS = {
    "level_1": "Look for the line that says jump_power",
    "level_2": "The jump_power number controls how high",
    "level_3": "Try changing 10 to a bigger number like 20",
    "solution": "jump_power = 20  # This makes a super jump!"
}
```

## Parent/Teacher Mode

Generate printable challenge cards:

```bash
# Create PDF with 10 challenges
poetry run python tools/kid_challenge.py --pdf --count 10

# Generate answer key
poetry run python tools/kid_challenge.py --answers --difficulty medium
```

## Tracking Progress

The tool can track completed challenges:

```json
{
    "player_name": "Alex",
    "completed_challenges": [
        "variables_easy_1",
        "loops_medium_3"
    ],
    "points": 250,
    "badges": ["Variable Victor", "Loop Legend"]
}
```

Remember: Every challenge should be fun, not frustrating! Celebrate attempts, not just success! 🎮✨
