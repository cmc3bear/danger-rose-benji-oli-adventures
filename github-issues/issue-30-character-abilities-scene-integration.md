# Issue #30: Integrate Character Abilities into All Game Scenes

## 🎯 Overview
Integrate the character special abilities system (Issue #29) into all four minigames (Pool, Ski, Vegas, Drive). This involves modifying each scene to support and respond to character-specific abilities.

## 📋 Prerequisites
- Issue #28 Sprints 1-4 completed (characters and animations ready)
- Issue #29 completed (ability system implemented)
- All ability classes and manager are functional
- Visual effects system is in place

## 🏊 Pool Game Integration

### File: `src/scenes/pool.py`

#### Ability Effects Implementation

**1. Homing Balloons (Benji - Tech Boost)**
```python
class WaterBalloon:
    def __init__(self, x, y, vx, vy, homing_enabled=False):
        self.homing_enabled = homing_enabled
        self.homing_strength = 0.0
        self.target = None
    
    def update(self, dt, targets):
        if self.homing_enabled and targets:
            # Find nearest target
            if not self.target or self.target.hit:
                self.target = self._find_nearest_target(targets)
            
            if self.target:
                # Apply homing force
                dx = self.target.x - self.x
                dy = self.target.y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    # Normalize and apply homing
                    dx /= dist
                    dy /= dist
                    self.vx += dx * self.homing_strength * dt
                    self.vy += dy * self.homing_strength * dt
```

**2. Triple Shot (Olive - Nature's Blessing)**
```python
def throw_balloon(self):
    if self.ability_effects.get("effect") == "triple_shot":
        # Create three balloons in spread pattern
        angles = [-15, 0, 15]  # Degrees
        for angle in angles:
            rad = math.radians(angle)
            vx = math.cos(rad) * self.throw_power
            vy = math.sin(rad) * self.throw_power
            balloon = WaterBalloon(self.player.x, self.player.y, vx, vy)
            self.balloons.append(balloon)
    else:
        # Normal single balloon throw
        pass
```

**3. Splash Damage (Uncle Bear - Bear Strength)**
```python
def check_balloon_collision(self, balloon, targets):
    hit_target = None
    for target in targets:
        if self._check_collision(balloon, target):
            hit_target = target
            break
    
    if hit_target and self.ability_effects.get("effect") == "splash_damage":
        # Apply splash damage to nearby targets
        splash_radius = 100
        for target in targets:
            if target != hit_target:
                dist = self._get_distance(hit_target, target)
                if dist < splash_radius:
                    damage = 1.0 - (dist / splash_radius)  # Falloff
                    target.take_damage(damage * 0.5)  # Half damage
```

**4. Existing Character Abilities**
- **Rapid Fire (Danger)**: Reduce throw cooldown by 50%
- **Slow-Mo Aim (Rose)**: Time slows while aiming
- **Score Multiplier (Dad)**: 2x points for duration

### Integration Points
```python
class PoolGame(Scene):
    def __init__(self, scene_manager):
        super().__init__()
        self.ability_effects = {}
        
    def update(self, dt):
        # Update ability effects
        self.ability_effects = self.scene_manager.ability_manager.update(
            dt, {"scene": "pool", "targets": self.targets}
        )
        
        # Apply ongoing effects
        if self.ability_effects.get("effect") == "rapid_fire":
            self.throw_cooldown = 0.25  # Half normal
        
        # Update balloons with ability modifiers
        for balloon in self.balloons:
            if self.ability_effects.get("effect") == "homing_balloons":
                balloon.homing_enabled = True
                balloon.homing_strength = self.ability_effects.get("homing_strength", 0.8)
```

## 🎿 Ski Game Integration

### File: `src/scenes/ski.py`

#### Ability Effects Implementation

**1. Optimal Path Display (Benji - Tech Boost)**
```python
def draw_optimal_path(self, screen):
    if self.ability_effects.get("effect") == "optimal_path":
        # Calculate best path through obstacles
        path_points = self._calculate_optimal_path()
        
        # Draw holographic line
        if len(path_points) > 1:
            color = (0, 255, 255, 128)  # Cyan with transparency
            for i in range(len(path_points) - 1):
                pygame.draw.line(screen, color, 
                               path_points[i], path_points[i+1], 3)
```

**2. Speed Boost Trail (Olive - Nature's Blessing)**
```python
class FlowerTrail:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 5.0
        self.boost_strength = 1.3
        
def update_player(self, dt):
    # Leave flower trail
    if self.ability_effects.get("effect") == "flower_trail":
        if self.frame_count % 10 == 0:  # Every 10 frames
            trail = FlowerTrail(self.player.x, self.player.y)
            self.flower_trails.append(trail)
    
    # Check if player hits any trails
    for trail in self.flower_trails:
        if self._check_collision(self.player, trail):
            self.player.speed *= trail.boost_strength
            trail.lifetime = 0  # Consume trail
```

**3. Obstacle Destruction (Uncle Bear - Bear Strength)**
```python
def check_obstacle_collision(self, player, obstacle):
    if self._check_collision(player, obstacle):
        if self.ability_effects.get("effect") == "smash_mode":
            # Destroy obstacle instead of crash
            self.score += 50
            self.create_destruction_effect(obstacle)
            self.obstacles.remove(obstacle)
            return False  # No crash
        else:
            return True  # Normal crash
```

**4. Existing Character Abilities**
- **Speed Burst (Danger)**: 2x speed for duration
- **Perfect Line (Rose)**: Bonus points for optimal path
- **Warning System (Dad)**: Obstacle indicators

## 🎰 Vegas Game Integration

### File: `src/scenes/vegas.py`

#### Ability Effects Implementation

**1. Shield System (Benji - Tech Boost)**
```python
class TechShield:
    def __init__(self, player):
        self.player = player
        self.health = 1
        self.active = True
        self.recharge_timer = 0
        
    def absorb_damage(self):
        if self.active and self.health > 0:
            self.health -= 1
            if self.health <= 0:
                self.active = False
                self.recharge_timer = 10.0
            return True  # Damage absorbed
        return False
        
def player_take_damage(self, damage):
    if hasattr(self, 'tech_shield') and self.tech_shield.absorb_damage():
        self.create_shield_effect()
        return  # No damage taken
    # Normal damage
    self.player.health -= damage
```

**2. Vine Barriers (Olive - Nature's Blessing)**
```python
class VineBarrier:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 100)
        self.health = 3
        self.growth_animation = 0
        
def activate_vine_barrier(self):
    if self.ability_effects.get("effect") == "vine_barrier":
        # Create barriers in front of player
        for offset in [-50, 0, 50]:
            vine = VineBarrier(
                self.player.x + 100,  # In front
                self.player.y + offset
            )
            self.vine_barriers.append(vine)
```

**3. Ground Pound (Uncle Bear - Bear Strength)**
```python
def activate_ground_pound(self):
    if self.ability_effects.get("effect") == "ground_pound":
        # Find all enemies in radius
        pound_radius = 150
        for enemy in self.enemies:
            dist = self._get_distance(self.player, enemy)
            if dist < pound_radius:
                # Stun enemy
                enemy.stunned = True
                enemy.stun_timer = 2.0
                # Knockback
                angle = math.atan2(
                    enemy.y - self.player.y,
                    enemy.x - self.player.x
                )
                enemy.vx = math.cos(angle) * 200
                enemy.vy = math.sin(angle) * 200
```

**4. Existing Character Abilities**
- **Dash Attack (Danger)**: Quick dash through enemies
- **Critical Hits (Rose)**: 50% chance for double damage
- **Weakness Display (Dad)**: Show enemy weak points

## 🚗 Drive Game Integration

### File: `src/scenes/drive.py`

#### Ability Effects Implementation

**1. Hazard Preview (Benji - Tech Boost)**
```python
def draw_hazard_warnings(self, screen):
    if self.ability_effects.get("effect") == "hazard_preview":
        preview_distance = self.ability_effects.get("preview_distance", 300)
        
        for hazard in self.hazards:
            # Calculate screen position for upcoming hazards
            if 0 < hazard.y < preview_distance:
                screen_y = self.horizon_y + (hazard.y / preview_distance) * 200
                # Draw warning icon
                warning_rect = pygame.Rect(
                    self._get_lane_x(hazard.lane) - 20,
                    screen_y - 20, 40, 40
                )
                pygame.draw.rect(screen, (255, 255, 0), warning_rect, 3)
                # Draw hazard type icon
                self.draw_hazard_icon(screen, warning_rect, hazard.hazard_type)
```

**2. Item Magnetism (Olive - Nature's Blessing)**
```python
def update_collectibles(self, dt):
    if self.ability_effects.get("effect") == "item_magnet":
        magnet_radius = 200
        magnet_strength = 300
        
        for item in self.collectibles:
            dist = self._get_distance(self.player, item)
            if dist < magnet_radius and dist > 0:
                # Pull item toward player
                dx = self.player.x - item.x
                dy = self.player.y - item.y
                dx /= dist
                dy /= dist
                item.x += dx * magnet_strength * dt
                item.y += dy * magnet_strength * dt
```

**3. Collision Resistance (Uncle Bear - Bear Strength)**
```python
def handle_collision(self, player, other_vehicle):
    if self.ability_effects.get("effect") == "heavy_vehicle":
        # Reduced impact on player
        impact_reduction = 0.3
        player.vx *= impact_reduction
        player.spin *= impact_reduction
        
        # Push other vehicle more
        push_multiplier = 2.0
        angle = math.atan2(
            other_vehicle.y - player.y,
            other_vehicle.x - player.x
        )
        other_vehicle.vx = math.cos(angle) * 200 * push_multiplier
        other_vehicle.lateral_velocity = math.sin(angle) * 100 * push_multiplier
    else:
        # Normal collision handling
        pass
```

**4. Existing Character Abilities**
- **Nitro Boost (Danger)**: Temporary speed increase
- **Precise Steering (Rose)**: Tighter turn radius
- **Experience Bonus (Dad)**: Faster score accumulation

## 🎮 Common Integration Patterns

### Ability Activation Handler
```python
# In each scene's handle_event method
def handle_event(self, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_x:  # Ability key
            character = self.scene_manager.game_data.get("selected_character")
            effects = self.scene_manager.ability_manager.activate_ability(
                character,
                self.get_ability_context()
            )
            self.apply_ability_effects(effects)
    
    # Existing event handling...
```

### Visual Effects Integration
```python
class AbilityEffectRenderer:
    """Render ability-specific visual effects"""
    
    def render_tech_effects(self, screen, player_pos):
        # Digital particles, holographic elements
        pass
    
    def render_nature_effects(self, screen, player_pos):
        # Leaves, flowers, organic particles
        pass
    
    def render_strength_effects(self, screen, player_pos):
        # Impact waves, dust clouds
        pass
```

## 🧪 Testing Requirements

### Scene-Specific Tests
- [ ] Pool: All balloon modifications work correctly
- [ ] Ski: Path rendering doesn't impact performance
- [ ] Vegas: Shield and barrier systems function properly
- [ ] Drive: Warning systems display accurately

### Cross-Scene Tests
- [ ] Abilities maintain state across scene transitions
- [ ] Visual effects consistent across all scenes
- [ ] Performance remains stable with abilities active

## 📋 Implementation Tasks

### Pool Game Integration (Week 7)
- [ ] Implement homing balloon system
- [ ] Add triple shot mechanics
- [ ] Create splash damage calculations
- [ ] Integrate existing character abilities

### Ski Game Integration (Week 7)
- [ ] Create optimal path algorithm
- [ ] Implement flower trail system
- [ ] Add obstacle destruction mechanics
- [ ] Integrate existing character abilities

### Vegas Game Integration (Week 8)
- [ ] Implement shield system
- [ ] Create vine barrier mechanics
- [ ] Add ground pound effects
- [ ] Integrate existing character abilities

### Drive Game Integration (Week 8)
- [ ] Create hazard preview system
- [ ] Implement item magnetism
- [ ] Add collision resistance
- [ ] Integrate existing character abilities

### Testing & Polish (Week 8)
- [ ] Test all abilities in all scenes
- [ ] Balance ability effectiveness
- [ ] Fix integration bugs
- [ ] Optimize performance

## 🎯 Acceptance Criteria

### Functionality
- [ ] All abilities work correctly in their respective scenes
- [ ] No abilities break existing game mechanics
- [ ] Visual feedback is consistent and clear

### Performance
- [ ] Frame rate remains stable (60 FPS)
- [ ] No memory leaks from ability effects
- [ ] Load times unaffected

### Balance
- [ ] Abilities enhance gameplay without trivializing it
- [ ] All characters remain viable choices
- [ ] No single ability dominates

## 🔗 Dependencies
- Issue #28 (New Characters) - Must have characters implemented
- Issue #29 (Ability System) - Core system must be complete
- Existing scene code must be modular enough for integration

This comprehensive integration will bring unique gameplay experiences to each character across all minigames!