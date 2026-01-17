# Development Container

This directory contains the VS Code Dev Container configuration for consistent development environments.

## What's Included

The dev container provides:
- **Python 3.11** with all project dependencies pre-installed
- **PostgreSQL client** tools for database interaction
- **PostgreSQL database** running in a linked container
- **VS Code extensions** for Python, Docker, and SQL development
- **Pre-configured settings** for code formatting (Black), linting (Ruff)

## Quick Start

### Prerequisites
- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Using the Dev Container

1. **Open in VS Code**
   ```bash
   code /path/to/poc-dta-mcp
   ```

2. **Reopen in Container**
   - Press `F1` or `Cmd/Ctrl+Shift+P`
   - Select: `Dev Containers: Reopen in Container`
   - Wait for the container to build and start (~2-3 minutes first time)

3. **Verify Setup**
   ```bash
   # Check Python version
   python --version  # Should be 3.11.x
   
   # Check PostgreSQL connection
   psql -h localhost -U analytics_user -d analytics_db -c "SELECT COUNT(*) FROM customers;"
   
   # Run demo
   python demo.py
   ```

## What Happens Automatically

When the dev container starts:

1. ✅ **Python dependencies installed** from `pyproject.toml`
2. ✅ **PostgreSQL started** with sample data loaded
3. ✅ **Environment variables set** (`.env` created from `.env.example`)
4. ✅ **VS Code extensions installed** (Python, Ruff, Black, SQL Tools, etc.)
5. ✅ **Port 5432 forwarded** for PostgreSQL access

## VS Code Features Configured

### Python Development
- **Linting**: Ruff (automatically on save)
- **Formatting**: Black (automatically on save)
- **IntelliSense**: Pylance for code completion
- **Type Checking**: Enabled

### Database Tools
- **SQL Tools**: Pre-configured connection to PostgreSQL
- **Query Execution**: Run SQL queries directly from VS Code
- **Schema Explorer**: Browse database tables and columns

### Code Quality
- **Format on Save**: Enabled for Python files
- **Organize Imports**: Automatic on save
- **Hidden Files**: `__pycache__`, `.pytest_cache` auto-hidden

## Environment Variables

The dev container automatically sets:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=analytics_db
POSTGRES_USER=analytics_user
POSTGRES_PASSWORD=analytics_password
```

## Testing the Setup

Run these commands inside the dev container:

```bash
# Verify database connection
python test_server.py

# Run comprehensive demo
python demo.py

# Test MCP client
python example_client.py

# Run tests (if any)
pytest
```

## Accessing PostgreSQL

### From VS Code
1. Open the **SQLTools** extension (database icon in sidebar)
2. Select "PostgreSQL - Analytics DB" connection
3. Explore tables and run queries

### From Command Line
```bash
# Connect to database
psql -h localhost -U analytics_user -d analytics_db

# Sample query
psql -h localhost -U analytics_user -d analytics_db \
  -c "SELECT account_type, COUNT(*) FROM customers GROUP BY account_type;"
```

## Troubleshooting

### Container won't start
- Ensure Docker Desktop is running
- Check that port 5432 is not in use: `lsof -i :5432`
- Rebuild container: `Dev Containers: Rebuild Container`

### PostgreSQL connection fails
- Wait ~10 seconds after container starts for PostgreSQL to initialize
- Check logs: `docker compose logs postgres`
- Verify health: `docker compose ps`

### Python imports not working
- Ensure dependencies installed: `pip install -e .[dev]`
- Reload VS Code window: `Developer: Reload Window`

## Customization

### Add VS Code Extensions
Edit `.devcontainer/devcontainer.json` and add to `extensions` array:
```json
"extensions": [
  "ms-python.python",
  "your-extension-id"
]
```

### Install Additional Tools
Edit `.devcontainer/Dockerfile` and add:
```dockerfile
RUN apt-get update && apt-get install -y your-tool
```

### Change Python Version
Edit `.devcontainer/Dockerfile`, line 2:
```dockerfile
FROM mcr.microsoft.com/devcontainers/python:3.12-bullseye
```

## Benefits

✅ **Consistent Environment**: Everyone uses the same Python version, dependencies, and tools
✅ **No Local Setup**: No need to install Python, PostgreSQL, or dependencies locally
✅ **Isolated**: Project dependencies don't interfere with other projects
✅ **Pre-configured**: All tools and settings ready to use
✅ **Fast Onboarding**: New developers can start coding in minutes

## Files in This Directory

- `devcontainer.json` - Main configuration file (references docker-compose files)
- `Dockerfile` - Custom development container image (Python 3.11 + dependencies)
- `docker-compose.extend.yml` - Docker Compose extension for dev service
  - **Note**: Build context is set to parent directory (`..`) to access `pyproject.toml`
  - Dockerfile path: `.devcontainer/Dockerfile` (relative to project root)
- `README.md` - This file

## Architecture

```
poc-dta-mcp/                    # Project root
├── .devcontainer/
│   ├── devcontainer.json       # Dev container config
│   ├── Dockerfile              # Image definition
│   ├── docker-compose.extend.yml  # Dev service (context: ..)
│   └── README.md
├── docker-compose.yml          # PostgreSQL service
├── pyproject.toml              # Python dependencies (copied in Dockerfile)
└── src/                        # Application code
```

The build context for the dev container is set to the project root (`..` relative to `.devcontainer/`) to ensure access to `pyproject.toml` and other project files.

## Learn More

- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Dev Container Specification](https://containers.dev/)
- [Docker Compose](https://docs.docker.com/compose/)
