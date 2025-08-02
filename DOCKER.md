# Docker Development Environment

This project includes a Docker-based development environment with Claude Code pre-installed.

## Quick Start

```bash
# Launch Claude Code in Docker
make claude

# Or manually:
docker-compose build dev
docker-compose up -d dev
docker-compose exec -it dev claude code
```

## Architecture

- **Base Image**: Python 3.12 on Debian Bookworm (full environment)
- **Claude Code**: Pre-installed in container, runs via docker exec
- **Volume Mounts**: Your project, Claude config, and credentials
- **AWS Services**: LocalStack for DynamoDB, S3, Lambda emulation

## Key Features

### IDE Integration
- PyCharm and JetBrains IDEs work perfectly with diffs and file navigation
- Container paths match Windows paths for seamless integration
- You continue using your Windows Python interpreter for performance

### Dependency Management
- Claude Code runs `poetry add/remove` in the Linux container
- You run `poetry lock` in Windows to sync your lock file
- Both environments remain isolated but share the same project

### Container Access
Claude Code runs inside the container via `docker exec`. Your SSH keys are mounted read-only for Git operations.

## Available Commands

```bash
make claude          # Launch Claude Code in container
make docker-build    # Build the Docker image
make docker-stop     # Stop all containers
make docker-clean    # Remove containers and volumes
```

## Container Services

### Development Container (`dev`)
- Python 3.12 with Poetry pre-installed
- Claude Code pre-installed via npm
- All development tools (git, make, vim, etc.)
- Your Claude configuration mounted

### LocalStack
- AWS services emulation
- Available at http://localhost:4566
- Services: DynamoDB, S3, Lambda, SQS, SNS

## Volume Mounts

| Local Path | Container Path | Purpose |
|------------|----------------|---------|
| `./` | `/workspace` | Project files |
| `./` | `/home/developer/project` | Project mount point |
| `~/.claude` | `/home/developer/.claude` | Claude settings |
| `~/.ssh` | `/home/developer/.ssh` | Git authentication |
| `~/.aws` | `/home/developer/.aws` | AWS credentials |

## Troubleshooting

### Container won't start
```bash
docker-compose logs dev
docker-compose down -v
make docker-build
```

### Claude Code won't start
```bash
# Check if container is running
docker-compose ps

# Check Claude Code installation
docker-compose exec dev which claude

# Restart container
docker-compose restart dev
```

### Permission issues
The container runs as user `developer` (UID 1000) with sudo access.

## Notes

- The container preserves Windows-style paths for IDE compatibility
- Poetry cache is stored in a named volume for performance
- AWS credentials are passed through from your environment
- Git operations use your mounted SSH keys
