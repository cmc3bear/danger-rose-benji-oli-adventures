# Minigame Sound Integration Guide

This guide explains how to integrate the newly created scene-specific sound effects into the Pool, Ski, and Vegas minigames.

## Sound File Locations

### Pool Minigame (`assets/audio/sfx/pool/impact/`)
- `pool_shot.mp3` - Sound of shooting at targets
- `target_hit.mp3` - Successful target hit
- `bullseye.mp3` - Perfect center hit
- `target_miss.mp3` - Shot misses target
- `powerup_collect.mp3` - Collecting power-ups
- `perfect_round.mp3` - Completing a perfect round

### Ski Minigame (`assets/audio/sfx/ski/movement/`)
- `ski_swoosh.mp3` - Skiing sound
- `ski_turn.mp3` - Sharp turn on skis
- `snow_spray.mp3` - Snow spraying effect
- `tree_hit.mp3` - Hitting a tree
- `checkpoint.mp3` - Passing checkpoint
- `speed_boost.mp3` - Speed boost pickup
- `finish_line.mp3` - Crossing finish line

### Vegas Minigame (`assets/audio/sfx/vegas/casino/`)
- `coin_collect.mp3` - Collecting coins/tokens
- `slot_machine.mp3` - Slot machine sounds
- `dice_roll.mp3` - Rolling dice
- `card_flip.mp3` - Card game sound
- `jackpot.mp3` - Big win sound
- `boss_appear.mp3` - Boss enemy appears
- `special_attack.mp3` - Special ability sound

## Integration Code Examples

### Basic Sound Manager Integration

```python
# Example: src/scenes/pool.py
class PoolScene(Scene):
    def __init__(self):
        super().__init__()
        self.sounds = {
            'shot': pygame.mixer.Sound('assets/audio/sfx/pool/impact/pool_shot.mp3'),
            'hit': pygame.mixer.Sound('assets/audio/sfx/pool/impact/target_hit.mp3'),
            'bullseye': pygame.mixer.Sound('assets/audio/sfx/pool/impact/bullseye.mp3'),
            'miss': pygame.mixer.Sound('assets/audio/sfx/pool/impact/target_miss.mp3'),
            'powerup': pygame.mixer.Sound('assets/audio/sfx/pool/impact/powerup_collect.mp3'),
            'perfect': pygame.mixer.Sound('assets/audio/sfx/pool/impact/perfect_round.mp3')
        }
    
    def shoot_at_target(self, target_position):
        # Play shooting sound
        self.sounds['shot'].play()
        
        # Check hit/miss and play appropriate sound
        if self.check_hit(target_position):
            if self.is_bullseye(target_position):
                self.sounds['bullseye'].play()
            else:
                self.sounds['hit'].play()
        else:
            self.sounds['miss'].play()
```

### Advanced Sound Manager Integration

```python
# Example: Enhanced integration with the existing sound manager
from src.managers.sound_manager import SoundManager

class SkiScene(Scene):
    def __init__(self):
        super().__init__()
        self.sound_manager = SoundManager()
        
        # Register ski sounds
        self.sound_manager.load_sound('ski_swoosh', 'assets/audio/sfx/ski/movement/ski_swoosh.mp3')
        self.sound_manager.load_sound('ski_turn', 'assets/audio/sfx/ski/movement/ski_turn.mp3')
        self.sound_manager.load_sound('snow_spray', 'assets/audio/sfx/ski/movement/snow_spray.mp3')
        self.sound_manager.load_sound('tree_hit', 'assets/audio/sfx/ski/movement/tree_hit.mp3')
        self.sound_manager.load_sound('checkpoint', 'assets/audio/sfx/ski/movement/checkpoint.mp3')
        self.sound_manager.load_sound('speed_boost', 'assets/audio/sfx/ski/movement/speed_boost.mp3')
        self.sound_manager.load_sound('finish_line', 'assets/audio/sfx/ski/movement/finish_line.mp3')
    
    def update_movement(self, dt):
        if self.player.is_moving:
            # Play continuous skiing sound
            if not self.sound_manager.is_playing('ski_swoosh'):
                self.sound_manager.play_sound('ski_swoosh', loop=True)
        
        if self.player.is_turning:
            self.sound_manager.play_sound('ski_turn')
            self.sound_manager.play_sound('snow_spray')
    
    def on_collision(self, collision_type):
        if collision_type == 'tree':
            self.sound_manager.play_sound('tree_hit')
        elif collision_type == 'checkpoint':
            self.sound_manager.play_sound('checkpoint')
    
    def on_powerup_collected(self, powerup_type):
        if powerup_type == 'speed_boost':
            self.sound_manager.play_sound('speed_boost')
    
    def on_finish_line_crossed(self):
        self.sound_manager.stop_all_sounds()
        self.sound_manager.play_sound('finish_line')
```

### Vegas Minigame Example

```python
# Example: src/scenes/vegas.py
class VegasScene(Scene):
    def __init__(self):
        super().__init__()
        self.sound_manager = SoundManager()
        
        # Load casino sounds
        casino_sounds = {
            'coin_collect': 'assets/audio/sfx/vegas/casino/coin_collect.mp3',
            'slot_machine': 'assets/audio/sfx/vegas/casino/slot_machine.mp3',
            'dice_roll': 'assets/audio/sfx/vegas/casino/dice_roll.mp3',
            'card_flip': 'assets/audio/sfx/vegas/casino/card_flip.mp3',
            'jackpot': 'assets/audio/sfx/vegas/casino/jackpot.mp3',
            'boss_appear': 'assets/audio/sfx/vegas/casino/boss_appear.mp3',
            'special_attack': 'assets/audio/sfx/vegas/casino/special_attack.mp3'
        }
        
        for sound_name, path in casino_sounds.items():
            self.sound_manager.load_sound(sound_name, path)
    
    def collect_coin(self):
        self.sound_manager.play_sound('coin_collect')
        self.score += 10
    
    def spin_slot_machine(self):
        self.sound_manager.play_sound('slot_machine')
        # Slot machine logic...
        
    def roll_dice(self):
        self.sound_manager.play_sound('dice_roll')
        # Dice rolling logic...
        
    def flip_card(self):
        self.sound_manager.play_sound('card_flip')
        # Card game logic...
        
    def trigger_jackpot(self):
        self.sound_manager.play_sound('jackpot')
        # Jackpot celebration...
        
    def spawn_boss(self):
        self.sound_manager.play_sound('boss_appear')
        # Boss spawning logic...
        
    def use_special_ability(self):
        self.sound_manager.play_sound('special_attack')
        # Special ability logic...
```

## Integration with Existing Sound Manager

The sound effects are designed to work with the existing sound manager architecture. Here's how to enhance the current sound manager:

```python
# Example: Enhancement to src/managers/sound_manager.py
class SoundManager:
    def __init__(self):
        # ... existing initialization ...
        
        # Minigame sound categories
        self.minigame_sounds = {
            'pool': {},
            'ski': {}, 
            'vegas': {}
        }
    
    def load_minigame_sounds(self, minigame_name):
        """Load all sounds for a specific minigame."""
        sound_paths = {
            'pool': {
                'shot': 'assets/audio/sfx/pool/impact/pool_shot.mp3',
                'hit': 'assets/audio/sfx/pool/impact/target_hit.mp3',
                'bullseye': 'assets/audio/sfx/pool/impact/bullseye.mp3',
                'miss': 'assets/audio/sfx/pool/impact/target_miss.mp3',
                'powerup': 'assets/audio/sfx/pool/impact/powerup_collect.mp3',
                'perfect': 'assets/audio/sfx/pool/impact/perfect_round.mp3'
            },
            'ski': {
                'swoosh': 'assets/audio/sfx/ski/movement/ski_swoosh.mp3',
                'turn': 'assets/audio/sfx/ski/movement/ski_turn.mp3',
                'snow_spray': 'assets/audio/sfx/ski/movement/snow_spray.mp3',
                'tree_hit': 'assets/audio/sfx/ski/movement/tree_hit.mp3',
                'checkpoint': 'assets/audio/sfx/ski/movement/checkpoint.mp3',
                'speed_boost': 'assets/audio/sfx/ski/movement/speed_boost.mp3',
                'finish_line': 'assets/audio/sfx/ski/movement/finish_line.mp3'
            },
            'vegas': {
                'coin_collect': 'assets/audio/sfx/vegas/casino/coin_collect.mp3',
                'slot_machine': 'assets/audio/sfx/vegas/casino/slot_machine.mp3',
                'dice_roll': 'assets/audio/sfx/vegas/casino/dice_roll.mp3',
                'card_flip': 'assets/audio/sfx/vegas/casino/card_flip.mp3',
                'jackpot': 'assets/audio/sfx/vegas/casino/jackpot.mp3',
                'boss_appear': 'assets/audio/sfx/vegas/casino/boss_appear.mp3',
                'special_attack': 'assets/audio/sfx/vegas/casino/special_attack.mp3'
            }
        }
        
        if minigame_name in sound_paths:
            for sound_name, path in sound_paths[minigame_name].items():
                sound_key = f"{minigame_name}_{sound_name}"
                self.load_sound(sound_key, path)
                self.minigame_sounds[minigame_name][sound_name] = sound_key
    
    def play_minigame_sound(self, minigame_name, sound_name, **kwargs):
        """Play a sound effect for a specific minigame."""
        if minigame_name in self.minigame_sounds:
            if sound_name in self.minigame_sounds[minigame_name]:
                sound_key = self.minigame_sounds[minigame_name][sound_name]
                self.play_sound(sound_key, **kwargs)
            else:
                print(f"Warning: Sound '{sound_name}' not found for {minigame_name}")
        else:
            print(f"Warning: Minigame '{minigame_name}' not loaded")
    
    def unload_minigame_sounds(self, minigame_name):
        """Unload sounds for a specific minigame to free memory."""
        if minigame_name in self.minigame_sounds:
            for sound_name, sound_key in self.minigame_sounds[minigame_name].items():
                if sound_key in self.sounds:
                    del self.sounds[sound_key]
            self.minigame_sounds[minigame_name].clear()
```

## Best Practices

1. **Preload Sounds**: Load minigame sounds when entering the scene
2. **Memory Management**: Unload sounds when leaving the scene
3. **Volume Control**: Use appropriate volume levels for each sound type
4. **Sound Variations**: Consider adding random pitch variations for repetitive sounds
5. **Kid-Friendly**: Ensure all sounds are appropriate and not scary for children

## Next Steps

1. **Replace Placeholders**: The current files are empty placeholders - replace with actual sound files
2. **Volume Balancing**: Adjust volume levels for each sound effect
3. **Add Variations**: Create multiple versions of frequently played sounds
4. **Retro Processing**: Apply 8-bit/retro effects to match game aesthetic
5. **Integration Testing**: Test each sound effect in its respective minigame

## Sound Replacement

When you have actual sound files (from 11labs API or other sources), simply replace the placeholder MP3 files in:
- `assets/audio/sfx/pool/impact/`
- `assets/audio/sfx/ski/movement/`
- `assets/audio/sfx/vegas/casino/`

The integration code will automatically use the new sound files!