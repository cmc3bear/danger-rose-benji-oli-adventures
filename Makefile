# Danger Rose - Game Development Makefile
# Simple commands for Windows, macOS, and Linux

# Default target
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@echo "Danger Rose - Make Commands"
	@echo "==========================="
	@echo ""
	@echo "Game Commands:"
	@echo "  make run          Run the game"
	@echo "  make debug        Run in debug mode"
	@echo "  make run-ski      Run ski minigame directly"
	@echo "  make run-pool     Run pool minigame directly"
	@echo "  make run-vegas    Run vegas minigame directly"
	@echo "  make kids         Run in kid-friendly mode"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build        Build executable (folder version)"
	@echo "  make build-onefile Build single executable file"
	@echo "  make build-all    Build for all platforms"
	@echo "  make clean-build  Clean build artifacts only"
	@echo ""
	@echo "Development Commands:"
	@echo "  make test         Run unit tests"
	@echo "  make test-game    Run game tests only"
	@echo "  make test-all     Run all tests including integration"
	@echo "  make test-visual  Run visual regression tests"
	@echo "  make test-audio   Run comprehensive audio test suite"
	@echo "  make test-auto    Run automated bug detection"
	@echo "  make coverage     Run tests with coverage report"
	@echo "  make check        Run all checks (lint + test)"
	@echo ""
	@echo "Audio Testing:"
	@echo "  make test-audio-quick         Quick audio tests"
	@echo "  make test-audio-performance   Audio performance tests"
	@echo "  make test-audio-accessibility Audio accessibility tests"
	@echo "  make test-audio-integration   Audio integration tests"
	@echo "  make test-audio-stress        Audio stress tests"
	@echo "  make validate-audio-assets    Validate audio files"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         Check code style"
	@echo "  make format       Auto-format code"
	@echo "  make security     Run security checks"
	@echo ""
	@echo "Asset Management:"
	@echo "  make assets-check   Validate all game assets"
	@echo "  make sprites        Generate sprite test output"
	@echo "  make audio-download Download high-quality audio"
	@echo "  make audio-check    Check current audio files"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean        Clean all artifacts"
	@echo "  make profile      Profile game performance"
	@echo "  make celebrate    Celebrate achievements!"
	@echo ""
	@echo "Docker:"
	@echo "  make claude       Launch Claude Code in Docker"
	@echo "  make join-claude  Open bash shell in Docker container"
	@echo "  make docker-build Build Docker images"
	@echo "  make docker-stop  Stop Docker containers"
	@echo "  make docker-clean Clean up Docker resources"
	@echo ""

# ========== GAME COMMANDS ==========

.PHONY: run
run: ## Run the game
	@echo "🎮 Starting Danger Rose..."
	poetry run python src/main.py

.PHONY: debug
debug: ## Run the game in debug mode
	@echo "🐛 Starting in debug mode..."
	@DEBUG=true poetry run python src/main.py

.PHONY: run-ski
run-ski: ## Run ski minigame directly
	@echo "⛷️  Starting ski minigame..."
	@SCENE=ski poetry run python src/main.py

.PHONY: run-pool
run-pool: ## Run pool minigame directly
	@echo "🏊 Starting pool minigame..."
	@SCENE=pool poetry run python src/main.py

.PHONY: run-vegas
run-vegas: ## Run vegas minigame directly
	@echo "🎰 Starting Vegas minigame..."
	@SCENE=vegas poetry run python src/main.py

.PHONY: kids
kids: ## Run in kid-friendly mode
	@echo "👶 Starting in kid-friendly mode..."
	@KID_MODE=true poetry run python src/main.py

.PHONY: build
build: ## Build standalone executable (folder version)
	@echo "📦 Building executable (folder version)..."
	poetry run pyinstaller danger-rose.spec --noconfirm
	@echo "✅ Build complete! Check dist/DangerRose/ folder"

.PHONY: build-onefile
build-onefile: ## Build single executable file
	@echo "📦 Building single executable file..."
	poetry run pyinstaller danger-rose-onefile.spec --noconfirm
	@echo "✅ Build complete! Check dist/ folder for DangerRose.exe"

.PHONY: build-all
build-all: ## Build for all platforms
	@echo "📦 Building for all platforms..."
	@echo "Note: Cross-platform builds require platform-specific builders"
	poetry run pyinstaller danger-rose.spec --noconfirm
	@echo "✅ Current platform build complete!"

.PHONY: clean-build
clean-build: ## Clean build artifacts only
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build dist 2>/dev/null || true
	@find . -name "*.spec" ! -name "danger-rose*.spec" -delete 2>/dev/null || true
	@echo "✨ Build artifacts cleaned!"

# ========== DEVELOPMENT COMMANDS ==========

.PHONY: test
test: ## Run unit tests
	@echo "🧪 Running unit tests..."
	poetry run pytest tests/unit -v

.PHONY: test-game
test-game: ## Run game tests only
	@echo "🎮 Running game-specific tests..."
	poetry run pytest tests/unit tests/integration -v -k "not test_visual"

.PHONY: test-all
test-all: ## Run all tests including integration
	@echo "🧪 Running all tests..."
	poetry run pytest tests/ -v

.PHONY: coverage
coverage: ## Run tests with coverage report
	@echo "📊 Running coverage analysis..."
	poetry run pytest tests/unit --cov=src --cov-report=html --cov-report=term
	@echo "📊 Coverage report generated in htmlcov/"

.PHONY: check
check: lint test ## Run all checks (lint + test)
	@echo "✅ All checks passed!"

.PHONY: lint
lint: ## Run code linting
	@echo "🔍 Checking code style..."
	poetry run ruff check src/ tests/

.PHONY: format
format: ## Format code
	@echo "💅 Formatting code..."
	poetry run ruff format src/ tests/
	poetry run ruff check src/ tests/ --fix

.PHONY: security
security: ## Run security checks
	@echo "🔒 Running security checks..."
	poetry run bandit -r src/ -ll
	poetry run safety check --json

.PHONY: clean
clean: ## Clean all artifacts
	@echo "🧹 Cleaning up..."
	@rm -rf build dist __pycache__ .pytest_cache htmlcov .coverage .mypy_cache .ruff_cache test-artifacts *.spec .coverage.* 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✨ Clean!"

# ========== SPECIAL COMMANDS ==========

.PHONY: assets-check
assets-check: ## Validate all game assets exist
	@echo "🎨 Checking assets..."
	poetry run python tools/check_assets.py

.PHONY: audio-download
audio-download: ## Download high-quality audio files
	@echo "🎵 Downloading audio files..."
	python scripts/download_audio.py

.PHONY: audio-check
audio-check: ## Check current audio file quality
	@echo "🔊 Checking audio files..."
	@echo "Music files:"
	@ls -lh assets/audio/music/*.ogg 2>/dev/null || echo "No music files found"
	@echo ""
	@echo "SFX files:"
	@ls -lh assets/audio/sfx/*.ogg 2>/dev/null || echo "No SFX files found"

.PHONY: test-visual
test-visual: ## Run visual regression tests
	@echo "👁️ Running visual regression tests..."
	poetry run python tools/visual_regression_tester.py
	@echo "Check visual_test_results/ for reports"

.PHONY: test-audio
test-audio: ## Run comprehensive audio test suite
	@echo "🔊 Running comprehensive audio test suite..."
	poetry run python tools/audio_test_suite.py
	@echo "Check audio_test_report.txt for detailed results"

.PHONY: test-audio-quick
test-audio-quick: ## Run quick audio tests only
	@echo "🔊 Running quick audio tests..."
	poetry run python tools/audio_test_suite.py --quick
	@echo "Quick audio test completed"

.PHONY: test-audio-performance
test-audio-performance: ## Run audio performance tests
	@echo "⚡ Running audio performance tests..."
	poetry run python tools/audio_test_suite.py --category performance
	@echo "Performance test completed"

.PHONY: test-audio-accessibility
test-audio-accessibility: ## Run audio accessibility tests
	@echo "♿ Running audio accessibility tests..."
	poetry run python tools/audio_test_suite.py --category accessibility
	@echo "Accessibility test completed"

.PHONY: test-audio-integration
test-audio-integration: ## Run audio integration tests
	@echo "🔗 Running audio integration tests..."
	poetry run python tools/audio_test_suite.py --category integration
	@echo "Integration test completed"

.PHONY: test-audio-stress
test-audio-stress: ## Run audio stress tests
	@echo "💪 Running audio stress tests..."
	poetry run python tools/audio_test_suite.py --stress
	@echo "Stress test completed"

.PHONY: validate-audio-assets
validate-audio-assets: ## Validate audio asset files
	@echo "🎵 Validating audio assets..."
	poetry run python tools/audio_validator.py --all
	@echo "Audio asset validation completed"

.PHONY: test-auto
test-auto: ## Run automated bug detection (quick 30s test)
	@echo "🤖 Running automated bug detection..."
	poetry run python tools/automated_game_tester.py
	@echo "Check test_results/ for bug reports"

.PHONY: sprites
sprites: ## Generate sprite test output
	@echo "🖼️ Generating sprite tests..."
	poetry run python tools/visual/test_sprite_cutting.py
	poetry run python tools/visual/test_attack_character.py
	@echo "✅ Sprite tests complete! Check test-artifacts/"

.PHONY: profile
profile: ## Profile game performance
	@echo "⚡ Profiling game..."
	poetry run python -m cProfile -o profile.stats src/main.py
	@echo "Profile saved to profile.stats"

.PHONY: celebrate
celebrate: ## Celebrate achievements!
	@echo "🎉 Celebration time!"
	poetry run python tools/celebrate.py


# Docker targets
claude:
	@echo "Preparing Claude Code environment..."
	@docker-compose build dev
	@docker-compose up -d dev
	@echo "Waiting for container to be ready..."
	@powershell -Command "Start-Sleep -Seconds 3"
	@echo "Launching Claude Code inside container..."
	@docker-compose exec -it dev bash -l -c "claude"

join-claude:
	@echo "Joining Claude container with bash shell..."
	@docker-compose exec -it dev /bin/bash

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f
