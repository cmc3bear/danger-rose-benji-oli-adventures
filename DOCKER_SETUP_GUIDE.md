# Claude Code Docker Setup - Copy Guide

## Files to Copy to Other Projects

### Required Files (4 files)

1. **`Dockerfile`** - The main Docker configuration
2. **`docker-compose.yml`** - Service definitions (now dynamic)
3. **`.mcp.json`** - MCP server configuration for Claude Code
4. **`DOCKER.md`** - Documentation (optional but recommended)

### Makefile Targets to Add

Add these targets to your project's Makefile:

```makefile
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
```

### Environment Setup

1. **Create `.env` file** with at least:
   ```
   GH_TOKEN=your_github_token_here
   ```

2. **Optional**: Copy `.claude/settings.json` for project-specific Claude settings

## Dynamic Configuration

The setup now uses `${COMPOSE_PROJECT_NAME:-project}` which:
- Defaults to "project" if not set
- Automatically uses the directory name in most Docker Compose versions
- Can be overridden by setting `COMPOSE_PROJECT_NAME` in `.env`

## Quick Setup for New Projects

```bash
# 1. Copy the Docker files
cp /path/to/augint-library/{Dockerfile,docker-compose.yml,.mcp.json,DOCKER.md} .

# 2. Add Makefile targets (see above)

# 3. Create .env with GH_TOKEN

# 4. Build and run
make docker-build
make claude
```

## What's Included

- Python 3.12 with Poetry
- Claude Code pre-installed
- Playwright with Chromium (headless)
- All pytest/testing tools
- Git, Make, and development tools
- AWS LocalStack (optional)
- Automatic Poetry virtualenv activation
- Environment variables from .env

## Notes

- Works with any Python/Poetry/pytest project
- No hardcoded project names
- Preserves your local development setup
- Mounts your SSH keys and AWS credentials
- Poetry cache persisted in Docker volume
