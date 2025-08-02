# 🎮 Danger Rose

<div align="center">
  <img src="docs/images/logo-placeholder.png" alt="Danger Rose Logo" width="400">

  **A retro-style adventure game featuring Danger, Rose, and their snowboarding Dad**

  [![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
  [![Pygame](https://img.shields.io/badge/Pygame--CE-2.4%2B-green.svg)](https://pyga.me/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  [![Downloads](https://img.shields.io/github/downloads/svange/danger-rose/total)](https://github.com/svange/danger-rose/releases)
  [![Issues](https://img.shields.io/github/issues/svange/danger-rose)](https://github.com/svange/danger-rose/issues)
</div>

## 🌟 About The Game

**Danger Rose** is a pixel-art adventure game where you play as two siblings exploring their apartment and competing in wild minigames. From racing down snowy mountains to battling the Vegas Sphere boss, every room holds a new challenge!

<div align="center">
  <h3>
    <a href="https://github.com/svange/danger-rose/releases/latest">
      🎮 Download Latest Release
    </a>
  </h3>
  <p>
    <strong>Available for Windows, macOS, and Linux!</strong>
  </p>
</div>

### 🎯 Key Features
- **Choose Your Hero**: Play as Danger, Rose, or unlock their snowboarding Dad
- **3 Epic Minigames**: Ski down treacherous mountains, splash targets at the pool, and survive Vegas!
- **Local Co-op**: Up to 3 players on one screen
- **Retro Pixel Art**: Classic arcade style with modern gameplay
- **Boss Battles**: Face off against the notorious Vegas Sphere

## 📸 Screenshots

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="docs/images/title-screen.png" alt="Title Screen" width="300"><br>
        <b>Character Selection</b>
      </td>
      <td align="center">
        <img src="docs/images/hub-world.png" alt="Hub World" width="300"><br>
        <b>Cozy Apartment Hub</b>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="docs/images/ski-game.png" alt="Ski Minigame" width="300"><br>
        <b>Ski Downhill</b>
      </td>
      <td align="center">
        <img src="docs/images/pool-game.png" alt="Pool Minigame" width="300"><br>
        <b>Pool Splash</b>
      </td>
    </tr>
  </table>
</div>

## 🚀 Quick Start - Just Want to Play?

### 🎮 Download and Play (Easiest!)

1. **Go to [Releases](https://github.com/svange/danger-rose/releases)**
2. **Download for your system:**
   - 🪟 **Windows**: `DangerRose.exe` - Just download and play!
   - 🍎 **macOS**: `DangerRose-macOS.zip` - Extract and run
   - 🐧 **Linux**: `DangerRose-Linux.zip` - Extract and run
3. **No installation needed!** The game runs directly from the executable

### 🎯 First Time Playing?
1. **Choose Your Character**: Use ← → arrows to pick Danger or Rose
2. **Press SPACE** to start your adventure!
3. **Explore**: Walk around with arrow keys
4. **Play Minigames**: Stand by doors and press SPACE

## 🎮 Game Modes Breakdown

Each minigame brings its own unique challenge and scoring system. Master them all to become the ultimate champion!

## 📋 Table of Contents

1. [Playing the Game](#-playing-the-game)
2. [How to Play](#-how-to-play)
3. [Game Modes](#-game-modes)
4. [Development Setup](#-development-setup)
5. [Technical Details](#-technical-details)
6. [Contributing](#-contributing)
7. [Credits](#-credits)
8. [License](#-license)

## 🎮 Playing the Game

### System Requirements
- **OS**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 20.04+)
- **RAM**: 2GB minimum
- **Storage**: 200MB free space
- **Display**: 1920x1080 recommended

### Installation Options

#### Option 1: Portable Executable (Recommended)
- Download from [Releases](https://github.com/svange/danger-rose/releases)
- No installation required - just run!
- Keep it on your desktop or USB drive

#### Option 2: Add to System PATH (Optional)
Want to run the game from anywhere? Add it to your PATH:

**Windows:**
1. Move `DangerRose.exe` to `C:\Program Files\DangerRose\`
2. Add `C:\Program Files\DangerRose` to your PATH environment variable
3. Run `DangerRose` from any command prompt

**macOS/Linux:**
```bash
# Move to a directory in your PATH
sudo mv DangerRose /usr/local/bin/
# Now run from anywhere
DangerRose
```

#### Option 3: Run from Source (For Developers)
See [Development Setup](#-development-setup) below.

## 🛠️ Development Setup

### Prerequisites
- **Python**: 3.12 or higher ([Download Python](https://python.org))
- **Poetry**: Package manager ([Install Poetry](https://python-poetry.org/docs/))
- **Git**: Version control ([Download Git](https://git-scm.com))

#### Step-by-Step Setup

##### Windows Development
```bash
# 1. Install Python 3.12+ from python.org
# 2. Install Poetry (in PowerShell as Administrator)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# 3. Clone the game code
git clone https://github.com/svange/danger-rose.git
cd danger-rose

# 4. Install dependencies
poetry install

# 5. Run from source
poetry run python src/main.py
```

##### macOS/Linux Development
```bash
# 1. Clone the repository
git clone https://github.com/svange/danger-rose.git
cd danger-rose

# 2. Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# 3. Install dependencies
poetry install

# 4. Run from source
poetry run python src/main.py
```

## 🎮 How to Play

### Hub World
The apartment is your home base! Walk around and interact with:
- **🎿 Blue Door**: Enter the Ski minigame
- **🏊 Green Door**: Enter the Pool minigame
- **🎰 Red Door**: Enter the Vegas minigame
- **🏆 Trophy Shelf**: View your high scores
- **💾 Save Point**: Auto-saves your progress

### Controls
| Action | Keyboard | Gamepad |
|--------|----------|---------|
| Move | Arrow Keys / WASD | D-Pad / Left Stick |
| Jump | Space | A / X |
| Interact | Space / Enter | A / X |
| Attack | Z | B / Circle |
| Pause | Escape | Start |
| Aim (Pool) | Mouse | Right Stick |

## 🎯 Game Modes

### 🎿 Ski Downhill
Race down the mountain while Dad chases you on his snowboard!
- **The Challenge**: Survive 60 seconds of high-speed skiing
- **Obstacles**: Trees, rocks, and ice patches
- **Collect**: Snowflakes for points (+10 each)
- **Pro Tip**: Dad's AI keeps him close - use this to your advantage!
- **High Score Target**: 1,000+ points

### 🏊 Pool Splash
Water balloon mayhem at the neighborhood pool!
- **The Challenge**: Hit as many targets as possible in 60 seconds
- **Targets**: Rubber ducks, beach balls, and donut floats
- **Power-ups**: Triple shot, rapid fire, homing balloons
- **Combo System**: Chain hits for massive multipliers
- **High Score Target**: 5,000+ points

### 🎰 Vegas Dash
Side-scrolling beat 'em up through neon-lit Vegas!
- **The Challenge**: Reach the Vegas Sphere boss and defeat it
- **Enemies**: Casino chips, dice, and playing cards come to life
- **Boss Battle**: The Vegas Sphere with 3 increasingly chaotic phases
- **Weapons**: Sword for close combat, rainbow beam for range
- **High Score Target**: 10,000+ points

## 🔧 Technical Details

### Architecture
```
danger-rose/
├── 📁 assets/           # Game resources
│   ├── 🖼️ images/       # Sprites and backgrounds
│   └── 🔊 audio/        # Music and sound effects
├── 📁 src/              # Source code
│   ├── 🎮 main.py       # Game entry point
│   ├── 🎬 scenes/       # Game scenes
│   └── 🛠️ utils/        # Helper modules
├── 📁 tests/            # Unit tests
├── 📁 docs/             # Documentation
└── 📄 pyproject.toml    # Project config
```

### Performance
- **Target FPS**: 60 (with graceful degradation)
- **Resolution**: 1920x1080 (scales to display)
- **Memory Usage**: < 500MB
- **Load Times**: < 2 seconds per scene

### Development Commands

#### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src --cov-report=html

# Run specific test category
poetry run pytest tests/unit -v
poetry run pytest tests/visual -v
```

#### Building & Debugging
```bash
# Run in debug mode (shows FPS, hitboxes)
DEBUG=true poetry run python src/main.py

# Build standalone executable
poetry run pyinstaller danger-rose-onefile.spec

# Create Windows installer (Windows only)
poetry run python scripts/build_installer.py
```

#### Code Quality
```bash
# Format code
poetry run ruff format src/ tests/

# Check code style
poetry run ruff check src/ tests/

# Run pre-commit hooks
poetry run pre-commit run --all-files
```

### Project Structure
- **Scene System**: Each game mode is a self-contained scene
- **Entity-Component**: Characters use component-based architecture
- **Asset Pipeline**: Automatic placeholder generation for missing assets
- **Save System**: JSON-based local storage with auto-save

## 🤝 Contributing

Want to help make Danger Rose even better? Check out [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Bug reporting guidelines
- Feature request process
- Code style guide
- Pull request workflow

## 👥 Credits

### Development Team
- **Game Design & Programming**: Samuel Vange
- **Character Concepts**: Yasha & Ellie
- **Quality Assurance**: The whole crew

### Assets
- Character sprites from [Kenney.nl](https://kenney.nl)
- Sound effects from [Freesound.org](https://freesound.org)
- Music composed using BeepBox
- Additional art from [OpenGameArt.org](https://opengameart.org)

### Special Thanks
- The Pygame-CE community
- All our playtesters and contributors

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

  [🐛 Report Bug](https://github.com/svange/danger-rose/issues) • [💡 Request Feature](https://github.com/svange/danger-rose/issues) • [📖 Documentation](docs/)
</div>
