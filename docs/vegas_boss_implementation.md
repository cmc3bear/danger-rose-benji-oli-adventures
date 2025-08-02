# Vegas Sphere Boss Implementation

## Overview
The Vegas Sphere boss is a multi-phase boss fight implemented for the Vegas minigame in Danger Rose. The boss features three distinct phases with unique attack patterns, visual appearances, and difficulty progression.

## Features

### Visual Design
- **Phase 1 (Happy Face)**: Golden yellow sphere with a simple smile
- **Phase 2 (Angry Face)**: Red sphere with furrowed brows and frown
- **Phase 3 (Dizzy Face)**: Purple sphere with spiral eyes and wavy mouth
- Smooth floating animation and rotation
- Particle effects on hit
- Phase transition effects with invulnerability frames

### Attack Patterns
1. **Phase 1 - Happy (100% - 67% health)**
   - Radial burst: 8 projectiles in all directions
   - Attack rate: 2.5 seconds
   - Movement: Gentle side-to-side floating

2. **Phase 2 - Angry (66% - 34% health)**
   - Triple shot: 3 targeted projectiles at player
   - Attack rate: 1.5 seconds
   - Movement: Aggressive tracking towards player

3. **Phase 3 - Dizzy (33% - 0% health)**
   - Spiral pattern: 4 projectiles in rotating spiral
   - Attack rate: 0.8 seconds
   - Movement: Chaotic, unpredictable motion

### Sound Integration
- **Music**: Vegas theme continues during boss fight with dramatic ducking on start
- **Sound Effects**:
  - Boss hit: `collision.ogg`
  - Boss attack: `attack.ogg`
  - Phase transition: `collision.ogg`
  - Player hit: `player_hurt.wav`
  - Player attack: `attack.ogg`
  - Victory: `victory.wav`

### Player Combat
- **Health**: 3 hearts
- **Attack**: Close-range melee with spacebar (must be within 150 pixels)
- **Attack Cooldown**: 0.5 seconds between attacks
- **Invulnerability**: 2 seconds after taking damage
- **Visual Feedback**:
  - Flash effect when hit
  - Blinking during invulnerability
  - "Press SPACE to attack!" prompt when in range

### UI Elements
- **Boss Health Bar**:
  - Displays "VEGAS SPHERE" name
  - Phase indicators at 66% and 33%
  - Color changes based on current phase
  - Shows current phase name below bar

- **Player Health**:
  - Heart display in UI
  - Red hearts for remaining health
  - Gray hearts for lost health

### Victory Conditions
- **Victory**: Defeat the boss (reduce health to 0)
  - Boss falls off screen
  - Victory screen with gold text
  - Score calculation: 1000 base + 500 per remaining heart
  - Return to hub option

- **Game Over**: Lose all player health
  - Game over screen with red text
  - Return to hub option

## Technical Implementation

### Key Classes
- `VegasBoss` (src/entities/vegas_boss.py): Main boss entity with state machine
- `BossPhase`: Enum for phase management
- `Projectile`: Boss projectile class
- Vegas scene integration in `src/scenes/vegas.py`

### State Machine
- Automatic phase transitions based on health thresholds
- Invulnerability during transitions (2 seconds)
- Special defeated state with falling animation

### Collision Detection
- Rectangle-based collision for projectiles
- Distance-based detection for player attacks
- Proper cleanup of inactive projectiles

## Balance Considerations
- **Difficulty Progression**: Each phase increases attack frequency and complexity
- **Player Strategy**: Must dodge projectiles while finding openings to attack
- **Risk/Reward**: Getting close to attack exposes player to more danger
- **Accessibility**: 3 hearts provide reasonable margin for error

## Testing
- 13 unit tests covering all boss mechanics
- Tests for phase transitions, projectiles, movement, and damage
- Manual playtesting for balance and fun factor

## Future Enhancements
- Additional attack patterns per phase
- Environmental hazards in boss arena
- Power-ups during boss fight
- Leaderboard integration for boss speedruns
- Unique boss theme music
