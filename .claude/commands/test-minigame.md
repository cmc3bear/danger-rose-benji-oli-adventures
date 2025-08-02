# Test Minigame

Run comprehensive tests for a specific minigame or all minigames with detailed reporting.

## Usage

```bash
# Test specific minigame
poetry run pytest tests/test_ski_game.py -v

# Test all minigames
poetry run pytest tests/test_*_game.py -v

# Test with coverage report
poetry run pytest tests/test_pool_game.py --cov=src/scenes/pool --cov-report=term-missing

# Run visual tests for minigame
poetry run pytest tests/visual/test_ski_visual.py --update-baseline
```

## Test Categories by Minigame

### Ski Game Tests
```bash
# Core mechanics
poetry run pytest tests/test_ski_game.py::test_player_movement -v
poetry run pytest tests/test_ski_game.py::test_obstacle_collision -v
poetry run pytest tests/test_ski_game.py::test_speed_increase -v

# Visual tests
poetry run pytest tests/visual/test_ski_visual.py::test_ski_rendering -v

# Performance tests
poetry run pytest tests/performance/test_ski_performance.py::test_60fps_maintained -v
```

### Pool Game Tests
```bash
# Aiming mechanics
poetry run pytest tests/test_pool_game.py::test_aim_controls -v
poetry run pytest tests/test_pool_game.py::test_power_gauge -v

# Physics simulation
poetry run pytest tests/test_pool_game.py::test_ball_physics -v
poetry run pytest tests/test_pool_game.py::test_pocket_detection -v
```

### Vegas Game Tests
```bash
# Platforming mechanics
poetry run pytest tests/test_vegas_game.py::test_jump_mechanics -v
poetry run pytest tests/test_vegas_game.py::test_platform_collision -v

# Collectibles
poetry run pytest tests/test_vegas_game.py::test_coin_collection -v
poetry run pytest tests/test_vegas_game.py::test_powerup_effects -v
```

## Test Fixtures

```python
# Common test fixtures for minigames
@pytest.fixture
def ski_game():
    """Create ski game instance for testing"""
    game = SkiGame()
    game.setup_test_mode()
    return game

@pytest.fixture
def mock_player():
    """Create test player with predictable behavior"""
    player = Player(x=100, y=100)
    player.test_mode = True
    return player
```

## Integration Tests

```bash
# Test scene transitions
poetry run pytest tests/integration/test_scene_transitions.py -v

# Test save/load during minigames
poetry run pytest tests/integration/test_minigame_saves.py -v

# Test achievement unlocks
poetry run pytest tests/integration/test_achievements.py -v
```

## Performance Benchmarks

```bash
# Run performance suite
poetry run pytest tests/performance/ -v --benchmark-only

# Profile specific minigame
poetry run python -m cProfile -o ski_profile.stats src/main.py --scene ski_game

# Analyze profile
poetry run python -m pstats ski_profile.stats
```

## Visual Regression Tests

```bash
# Update baseline images
poetry run pytest tests/visual/ --update-baseline

# Run visual comparison
poetry run pytest tests/visual/ --visual-compare

# Generate visual diff report
poetry run pytest tests/visual/ --html=visual_report.html
```

## Debugging Failed Tests

```bash
# Run with debugger on failure
poetry run pytest tests/test_ski_game.py --pdb

# Show local variables
poetry run pytest tests/test_pool_game.py -l

# Verbose output with capture disabled
poetry run pytest tests/test_vegas_game.py -vv -s
```

## Creating New Tests

Template for new minigame tests:

```python
import pytest
from src.scenes.bonus_game import BonusGame

class TestBonusGame:
    def test_initialization(self):
        """Test game initializes correctly"""
        game = BonusGame()
        assert game.score == 0
        assert game.player is not None

    def test_player_controls(self):
        """Test player responds to input"""
        game = BonusGame()
        initial_x = game.player.x

        game.handle_input({"left": True})
        game.update(0.016)

        assert game.player.x < initial_x

    @pytest.mark.visual
    def test_rendering(self, visual_tester):
        """Test game renders correctly"""
        game = BonusGame()
        visual_tester.assert_matches("bonus_game_initial.png", game.render())
```
