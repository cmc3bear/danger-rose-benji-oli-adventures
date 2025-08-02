# 🎮 Contributing to Danger Rose

Welcome to the Danger Rose family! We're so excited you want to help make our game even better. This guide will help you contribute whether you're 8 or 80!

## 🌟 For Our Young Developers

### Your Ideas Matter!
We LOVE hearing from kids who play our game. You might have the best ideas!

**Ways You Can Help:**
- 🎨 Draw new character designs
- 💡 Suggest cool power-ups
- 🐛 Tell us about bugs you find
- 🎯 Create new minigame ideas
- 🎵 Hum theme songs for us

### How to Share Your Ideas

1. **Ask a Grown-up to Help**
   - They can help you create a GitHub account
   - They can type your ideas if needed

2. **Use Our Kid-Friendly Templates**
   ```
   🌟 My Cool Idea 🌟
   Name: [Your name and age]

   What's your idea?
   [Draw or describe it here!]

   Why is it fun?
   [Tell us why other kids would love it]

   Can you draw it?
   [Paste a photo of your drawing!]
   ```

3. **No Idea is Too Small!**
   - "Make the snowflakes rainbow colored!"
   - "Add a pet cat to the hub world!"
   - "Dad should do a funny dance!"

## 👨‍👩‍👧‍👦 For Parents & Adult Contributors

### Getting Started

1. **Fork the Repository**
   ```bash
   # Click 'Fork' on GitHub
   git clone https://github.com/YOUR_USERNAME/danger-rose.git
   cd danger-rose
   poetry install
   ```

2. **Create a Branch**

   **Branch Naming Convention (Required):**
   - Format: `{type}/issue-{number}-{description}`
   - Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
   - Always include the issue number
   - Use kebab-case for descriptions

   ```bash
   # Features
   git checkout -b feat/issue-123-add-power-ups

   # Bug fixes
   git checkout -b fix/issue-456-player-collision

   # Documentation
   git checkout -b docs/issue-789-update-readme

   # Other examples
   git checkout -b refactor/issue-101-scene-manager
   git checkout -b test/issue-202-add-minigame-tests
   git checkout -b chore/issue-303-update-dependencies
   ```

3. **Make Your Changes**
   - Write clean, commented code
   - Follow existing patterns
   - Add tests when possible

4. **Test Everything**
   ```bash
   # Run tests
   poetry run pytest

   # Check code style
   poetry run ruff format src/ tests/
   poetry run ruff check src/ tests/
   ```

5. **Submit a Pull Request**
   - Reference the issue number
   - Describe your changes clearly
   - Include screenshots if visual

### Code Style Guidelines

#### Python Code
```python
# Good: Clear variable names kids can understand
player_speed = 5
jump_height = 128

# Bad: Unclear abbreviations
ps = 5
jh = 128

# Good: Simple, documented functions
def make_player_jump(player):
    """Makes the player character jump up high!"""
    player.velocity_y = -jump_height
    play_sound("jump.ogg")
```

#### Comments for Learning
```python
# LEARNING MOMENT: This is a "variable" - it stores information!
score = 0

# LEARNING MOMENT: This is a "loop" - it repeats actions!
for snowflake in snowflakes:
    if player.collides_with(snowflake):
        score += 10  # Add 10 points!
```

### Testing Guidelines

#### Writing Kid-Friendly Tests
```python
def test_player_can_jump():
    """Test that our character can jump like a superhero!"""
    player = Player("Danger")

    # The player starts on the ground
    assert player.y == ground_level

    # Make them jump!
    player.jump()

    # They should be in the air now!
    assert player.y < ground_level
    assert player.is_jumping == True
```

### Commit Message Format
```
feat: add rainbow power-up to ski game

- Rainbow trail follows player
- Lasts for 10 seconds
- Makes you invincible
- Suggested by Ellie, age 8!

Closes #123
```

## 🎯 Areas We Need Help

### 🎨 Art & Assets
- Character animations
- Background scenery
- UI elements
- Sound effects

### 💻 Programming
- New minigames
- Bug fixes
- Performance improvements
- Accessibility features

### 📝 Documentation
- Tutorials for kids
- Video guides
- Translation to other languages
- Code comments

### 🧪 Testing
- Playtesting with kids
- Finding bugs
- Suggesting improvements
- Balance testing

## 🏆 Recognition

### Contributors Hall of Fame
We maintain a special section in our game credits for all contributors!

**Special Badges:**
- 🌟 **First PR** - Your first contribution!
- 🎨 **Artist** - Contributed art/assets
- 🐛 **Bug Hunter** - Found and reported bugs
- 💡 **Idea Machine** - Suggested great features
- 👶 **Young Coder** - Under 13 years old!

## 📋 Issue Templates

### Bug Report Template
```markdown
**What happened?**
[Describe the bug in simple words]

**What should happen?**
[What did you expect?]

**How can we make it happen again?**
1. Start the game
2. Go to [where]
3. Press [what button]
4. See the bug!

**Pictures help!**
[Add a screenshot if you can]
```

### Feature Request Template
```markdown
**What's your idea?**
[Describe your cool feature]

**Why would it be fun?**
[Tell us why kids would love it]

**How would it work?**
[Explain how players would use it]

**Can you draw it?**
[Add sketches or mockups]
```

## 🤝 Code of Conduct

### Be Kind and Respectful
- Use friendly words
- Help others learn
- Celebrate mistakes as learning
- Include everyone

### Kid-Safe Environment
- No scary content
- No bad words
- Keep it fun and positive
- Protect privacy

### Learning Together
- Ask questions - they help everyone!
- Share what you learn
- Be patient with beginners
- Celebrate small wins

## 🚀 Quick Commands for Contributors

```bash
# See all available commands
make help

# Run the game
make run

# Run in kid-mode (simpler errors)
make run-kids

# Check your code
make check

# Run specific minigame
make run-ski
make run-pool
make run-vegas

# Create new scene
poetry run python tools/create_scene.py my_cool_scene
```

## 💬 Getting Help

### For Kids
- Ask in our [Discord #kids-help channel](https://discord.gg/danger-rose)
- Email us at kids@dangerrose.game
- Ask your grown-up to help

### For Adults
- [Discord #dev-help channel](https://discord.gg/danger-rose)
- GitHub Discussions
- Check existing issues first

## 🎉 Thank You!

Every contribution makes Danger Rose more fun for families everywhere. Whether you're fixing bugs, adding features, or sharing ideas, you're part of our game development family!

**Remember**: The best games are made by people who play them. So play, have fun, and tell us how to make it even better!

---

*P.S. from Danger & Rose: We can't wait to see what cool stuff you add to our game! Maybe you'll create the next awesome minigame that becomes everyone's favorite!* 🎮✨
