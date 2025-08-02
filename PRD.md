# Danger Rose - Product Requirements Document

## Project Overview

**Danger Rose** is a family-friendly couch co-op Pygame project designed for parents to play with their kids. Players control Dad, Danger (Yasha, 10), and Rose (Ellie, 8) through a cozy hub world apartment and three unique minigames.

**Primary Goal**: Create an AI-assisted coding learning experience where kids can contribute ideas, playtest, and learn basic programming concepts through Claude Code.

## Target Audience

- **Primary**: Children ages 8-10 learning to code
- **Secondary**: Parents who want to bond with kids through game creation
- **Platform**: Windows (with serverless deployment potential)

## Technical Specifications

### Development Environment
- **Language**: Python 3.12+
- **Framework**: Pygame
- **AI Tools**: Claude Code for collaborative development
- **Version Control**: Git/GitHub
- **Resolution**: 1920x1080 (fullscreen support)
- **Frame Rate**: 60 FPS

### Architecture (Current)
```
danger-rose/
├── assets/
│   ├── images/
│   │   ├── characters/     # Sprite sheets (128x128 base)
│   │   └── tilesets/       # Backgrounds and environments
│   └── audio/
│       ├── music/          # Background loops
│       └── sfx/            # Sound effects
├── src/
│   ├── main.py             # Entry point
│   ├── scene_manager.py    # Scene state management
│   ├── scenes/
│   │   ├── title_screen.py # Character selection (DONE)
│   │   ├── hub.py          # Apartment hub world
│   │   ├── ski.py          # Ski minigame
│   │   ├── pool.py         # Pool minigame
│   │   └── vegas.py        # Vegas minigame
│   └── utils/
│       ├── sprite_loader.py # Asset loading
│       ├── attack_character.py # Animation system
│       └── ui.py           # Shared UI components
```

## Core Features

### 1. Character System
- **Playable Characters**:
  - Danger (Yasha) - Currently selectable
  - Rose (Ellie) - Currently selectable
  - Dad - Unlockable after completing all minigames
- **Co-op Support**: Up to 3 players local multiplayer
- **Character Selection**: Visual sprite-based selection with attack animations

### 2. Hub World (MVP Priority)
- **Setting**: Cozy apartment living room
- **Visual Elements**:
  - Large window showing pool with kids playing
  - Three doors leading to minigames (visible indicators)
  - Trophy shelf showing high scores
  - Decorations unlock based on achievements
- **Mechanics**:
  - Free movement with arrow keys/WASD
  - Interact with doors using Space/Enter
  - Character swap stations for co-op play
  - Visual feedback for unlocked content

### 3. Minigames

#### Ski Downhill (MVP Priority)
- **Duration**: 1 minute runs
- **Perspective**: Top-down view
- **Mechanics**:
  - Procedural obstacle generation (trees, rocks)
  - Difficulty scales obstacle density
  - Dad on snowboard as pace setter (rubber-band AI)
  - Snowflake collection for points
  - Jump mechanic (Space) to avoid obstacles
- **Scoring**:
  - +10 points per snowflake
  - -1 life per collision (3 lives total)
  - Time bonus for completion

#### Pool Splash
- **Duration**: 1 minute time limit
- **Style**: Cute shoot-em-up
- **Mechanics**:
  - Arrow key movement, mouse aim
  - Left-click fires water balloons
  - Moving targets drift across pool
  - Power-ups: Multi-shot, speed boost
  - Ring collection for bonus points
- **Scoring**:
  - Target hits: 50 points
  - Rings: 25 points
  - Combo multiplier for consecutive hits

#### Vegas Dash
- **Setting**: Mandalay Bay pools level
- **Boss**: Las Vegas Sphere (3 phases with emoji faces)
- **Mechanics**:
  - Side-scrolling platformer
  - Slash sword/shoot rainbows at slot machines
  - Collect casino chips
  - Health pickups (nachos, soda)
  - Linear path to boss encounter
- **Scoring**:
  - Chips: 100 points each
  - Enemy defeats: 200 points
  - Boss completion bonus: 5000 points

## Art & Audio Direction

### Visual Style
- **Resolution**: Pixel art (16x16 or 32x32 tiles)
- **Color Palette**: Bright, vibrant, kid-friendly
- **Character Sprites**: 128x128 with multiple animation states
- **UI**: Large, readable fonts with high contrast

### Asset Sources
- 99% free online assets (OpenGameArt, itch.io)
- Kid-created drawings scanned/digitized
- AI-generated placeholders for prototyping

### Recommended Sprite Alignment
For consistent animations:
- Base sprite size: 128x128
- Animation frames: 4-8 per action
- States needed: idle, walk, jump, attack, hurt

## Progression & Unlockables

### Save System
- Local JSON save files
- Track high scores per character per minigame
- Persist unlocked content

### Leaderboard Features
- Per-minigame high scores
- Character-specific tracking
- Visual celebration for new records
- Family leaderboard (all players)

### Unlockable Content
1. **Dad Character**: Complete all 3 minigames
2. **Hub Decorations**:
   - Ski trophy (beat ski high score)
   - Pool float (beat pool high score)
   - Neon sign (beat Vegas high score)
   - Family photo (unlock Dad)
3. **Difficulty Modes**: Easy/Normal/Hard per game
4. **Color palettes**: For each character

## Development Phases

### Phase 1: MVP (Current Sprint)
- [x] Basic game loop and scene manager
- [x] Title screen with character selection
- [ ] Hub world with movement and door interaction
- [ ] Ski minigame basic mechanics
- [ ] Simple save/load system
- [ ] Basic leaderboard display

### Phase 2: Core Gameplay
- [ ] Pool minigame implementation
- [ ] Vegas minigame implementation
- [ ] Dad character unlock system
- [ ] Sound effects integration
- [ ] Background music loops

### Phase 3: Polish
- [ ] Animated transitions between scenes
- [ ] Particle effects (snow, water splashes)
- [ ] Achievement notifications
- [ ] Co-op character selection
- [ ] Difficulty tuning based on playtesting

### Phase 4: Enhancement
- [ ] Tutorial/help screens
- [ ] Additional unlockables
- [ ] Mini cutscenes
- [ ] Export high scores
- [ ] Steam Deck compatibility

## Educational Components

### Programming Concepts to Highlight
- **Variables**: Score tracking, player position
- **Loops**: Game loop, animation cycles
- **Conditionals**: Collision detection, win conditions
- **Functions**: Modular minigame code
- **Classes**: Character and scene objects

### Kid Participation Points
- Adjusting game difficulty values
- Choosing color schemes
- Designing simple levels
- Creating sound effects
- Playtesting and feedback

## Technical Considerations

### Performance Targets
- Maintain 60 FPS on modest hardware
- Load times under 2 seconds
- Memory usage under 500MB

### Code Standards
- Clear variable names kids can understand
- Extensive comments explaining logic
- Modular design for easy modification
- Visual debugging options

### Deployment
- Single executable via PyInstaller
- Auto-save on scene transitions
- Graceful error handling
- Parent-friendly installation

## Success Metrics

1. **Engagement**: Kids request to play/code together
2. **Learning**: Kids can explain basic game concepts
3. **Completion**: All family members unlock Dad
4. **Creativity**: Kids suggest new features
5. **Technical**: Stable 60 FPS gameplay

## Next Steps

1. Implement hub world scene with door interactions
2. Create procedural ski slope generator
3. Add score persistence system
4. Implement basic sound manager
5. Weekly family playtesting sessions

## Open Questions for Development

1. Should power-ups carry between minigames?
2. Add a final "family game" after unlocking Dad?
3. Include difficulty assists for younger players?
4. Online leaderboard integration later?
5. Character customization options?
