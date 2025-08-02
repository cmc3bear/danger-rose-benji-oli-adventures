# 🎮 Danger Rose

<div align="center">
  <img src="docs/images/logo-placeholder.png" alt="Danger Rose Logo" width="400">

  **A cozy family game with endless minigame adventures**

  <!-- Build & Release -->
  [![CI/CD](https://github.com/cmc3bear/danger-rose-benji-oli-adventures/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/cmc3bear/danger-rose-benji-oli-adventures/actions)
  [![Release](https://img.shields.io/github/v/release/cmc3bear/danger-rose-benji-oli-adventures?include_prereleases)](https://github.com/cmc3bear/danger-rose-benji-oli-adventures/releases)
  [![Downloads](https://img.shields.io/github/downloads/cmc3bear/danger-rose-benji-oli-adventures/total)](https://github.com/cmc3bear/danger-rose-benji-oli-adventures/releases)
  
  <!-- Code Quality -->
  [![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
  [![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
  [![Coverage](https://img.shields.io/badge/coverage-55%25-yellow.svg)](https://github.com/cmc3bear/danger-rose-benji-oli-adventures)
  
  <!-- Tech Stack -->
  [![Pygame-CE](https://img.shields.io/badge/Pygame--CE-2.5.5-green.svg)](https://pyga.me/)
  [![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
  [![PyInstaller](https://img.shields.io/badge/PyInstaller-6.0-orange.svg)](https://www.pyinstaller.org/)
  
  <!-- Project Info -->
  [![License](https://img.shields.io/github/license/cmc3bear/danger-rose-benji-oli-adventures)](LICENSE)
  [![Issues](https://img.shields.io/github/issues/cmc3bear/danger-rose-benji-oli-adventures)](https://github.com/cmc3bear/danger-rose-benji-oli-adventures/issues)
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](guides/setup/contributing.md)
  
  <!-- Activity -->
  [![Last Commit](https://img.shields.io/github/last-commit/cmc3bear/danger-rose-benji-oli-adventures)](https://github.com/cmc3bear/danger-rose-benji-oli-adventures/commits/main)
  [![Contributors](https://img.shields.io/github/contributors/cmc3bear/danger-rose-benji-oli-adventures)](https://github.com/cmc3bear/danger-rose-benji-oli-adventures/graphs/contributors)
</div>

## 🏠 About

**Danger Rose** is a cozy family game built with Python and Pygame. Players control Danger, Rose, or Dad as they explore an apartment hub world and play various minigames.

Each minigame offers a different adventure - from skiing down mountains to water balloon battles at the pool to side-scrolling action in Vegas. The game continues to grow with new minigames being added regularly.

<div align="center">
  <h3>
    <a href="https://github.com/svange/danger-rose/releases/latest">
      🎮 Download Game
    </a>
  </h3>
  <p>
    <strong>Windows, macOS, and Linux</strong>
  </p>
</div>

## 🎯 Quick Play

1. **[Download the game](https://github.com/svange/danger-rose/releases)** for your system
2. **Run it** - no installation needed!
3. **Pick a character** with arrow keys
4. **Press SPACE** to start exploring

### Controls
- **Move**: Arrow keys or WASD
- **Jump/Interact**: Space
- **Pause**: Escape

## 🎮 Current Minigames

Start in the apartment hub and walk through doors to discover:

### Available Now
- **🎿 Ski Game** - Race down the mountain while Dad chases on his snowboard
- **🏊 Pool Game** - Water balloon target practice 
- **🎰 Vegas Game** - Side-scrolling adventure through the city

### Coming Soon
More minigames are in development! The hub world is designed to expand with new doors and adventures.

## 👨‍💻 Development

Here's how to run the game from source:

```bash
# Get the code
git clone https://github.com/svange/danger-rose.git
cd danger-rose

# Install Poetry (if needed)
curl -sSL https://install.python-poetry.org | python3 -

# Install game dependencies
poetry install

# Run the game
make run
```

### Useful Commands

```bash
make run          # Play the game
make test         # Run tests
make lint         # Check code style
make format       # Auto-format code
make claude       # Start Claude Code for AI pair programming
```

See our [development guides](./guides/) for more details.

## 🛠️ Tech Stack

<div align="center">

| Category | Technology | Version |
|----------|------------|---------|
| **Language** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) | 3.12+ |
| **Game Engine** | ![Pygame](https://img.shields.io/badge/Pygame--CE-00AA00?style=for-the-badge&logo=python&logoColor=white) | 2.5.5 |
| **Package Manager** | ![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white) | Latest |
| **Linting** | ![Ruff](https://img.shields.io/badge/Ruff-FCC21B?style=for-the-badge&logo=ruff&logoColor=black) | Latest |
| **Testing** | ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white) | Latest |
| **CI/CD** | ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white) | - |
| **Distribution** | ![PyInstaller](https://img.shields.io/badge/PyInstaller-FF6600?style=for-the-badge&logo=python&logoColor=white) | 6.0 |

</div>

### Key Features
- 🎮 **Cross-platform** - Runs on Windows, macOS, and Linux
- 🚀 **Fast Development** - Hot reload and debug mode
- 🧪 **Well Tested** - Comprehensive test suite with mocks
- 📦 **Easy Distribution** - Single executable files
- 🤖 **AI-Friendly** - Extensive documentation for Claude Code
- 🎨 **Asset Pipeline** - Automatic placeholder generation

## 🤝 Contributing

Contributions are welcome from developers of all experience levels!

Check out [CONTRIBUTING.md](guides/setup/contributing.md) to get started.

## 📚 Documentation

- **[LINKS.md](./LINKS.md)** - Quick navigation to all docs
- **[Setup Guides](./guides/setup/)** - Getting started
- **[Development Guides](./guides/development/)** - How we build the game
- **[AI Guides](./guides/ai/)** - Using Claude Code effectively

## 👥 Credits

**Made by**: Samuel, Yasha, and Ellie Vange

**Special Thanks**:
- Character sprites from [Kenney.nl](https://kenney.nl)
- Sound effects from [Freesound.org](https://freesound.org)
- Music made with BeepBox

---

<div align="center">
  Made with ❤️ thanks to the <a href="https://pyga.me/">pygame-ce</a> community
</div>