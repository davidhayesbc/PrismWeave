# UV Task Running Guide for PrismWeave

This guide explains the **official UV approaches** for task running in Python projects, similar to npm scripts in Node.js.

## Official UV Approaches

UV supports **two official methods** for task running:

### 1. Entry Points (`[project.scripts]`)

Entry points create **installed commands** that become available after installing the project.

**Configuration** (in `pyproject.toml`):

```toml
[project.scripts]
prismweave-cli = "cli:main"
prismweave-process = "cli:main" # Legacy alias
prismweave-mcp = "prismweave_mcp.server:main"
prismweave-mcp-inspector = "launch_mcp_with_inspector:main"
```

**Usage**:

```bash
# After uv sync, these commands are available
uv run prismweave-mcp              # Run MCP server
uv run prismweave-mcp-inspector    # Run server + inspector
uv run prismweave-cli -- --help    # Same CLI as python cli.py --help
uv run prismweave-cli -- process PrismWeaveDocs/documents --incremental
uv run prismweave-cli -- rebuild-db --yes
uv run prismweave-process -- stats # Backwards-compatible alias
```

**Best for**:

- Actual CLI tools you want to install
- Commands that should be available in the environment
- Entry points to your Python modules

### 2. Direct Commands with `uv run`

Run any command in the project environment:

```bash
# Run Python commands
uv run python -m prismweave_mcp.server --transport sse
uv run python -c "from src.utils.config_simplified import get_config; print(get_config())"

# Run pytest
uv run pytest tests/ -v
uv run pytest tests/ --cov=src

# Run other tools
uv run ruff check src/
uv run mypy src/
```

**Best for**:

- Ad-hoc commands during development
- Running tests and linters
- Direct Python module execution

## Task Runner Script (./run)

Since UV doesn't have a native task runner like npm scripts, we use a simple bash script for convenient task management.

**File**: `./run`

```bash
#!/usr/bin/env bash
# Task runner for PrismWeave AI Processing Module

case "$1" in
  mcp)
    python launch_mcp_with_inspector.py
    ;;
  mcp-server)
    python -m prismweave_mcp.server --transport sse
    ;;
  test)
    pytest tests/ -v
    ;;
  # ... more tasks
  *)
    echo "Usage: ./run <command>"
    echo "Available commands:"
    echo "  mcp, mcp-server, test, lint, format..."
    ;;
esac
```

**Usage**:

```bash
./run mcp          # Launch server + inspector
./run test         # Run tests
./run lint         # Run linting
./run --help       # Show all commands
```

**Advantages**:

- ✅ Simple, cross-platform compatible
- ✅ Works immediately without UV version dependencies
- ✅ Easy to customize and extend
- ✅ Similar UX to npm scripts
- ✅ No file format constraints (TOML syntax issues)

## Comparison to npm

| npm            | UV Official               | PrismWeave   |
| -------------- | ------------------------- | ------------ |
| `npm run test` | `uv run pytest tests/ -v` | `./run test` |
| `npm run dev`  | `uv run python -m module` | `./run dev`  |
| `npm start`    | `uv run entry-point`      | `./run mcp`  |
| `npm run lint` | `uv run ruff check`       | `./run lint` |

## Migration from Shell Scripts

### Before (Multiple Shell Scripts)

```
ai-processing/
├── inspector.sh     # Launch inspector
├── dev.sh          # Development mode
├── verify-setup.sh # Verify environment
```

### After (Unified Task Runner)

```
ai-processing/
├── run             # Single task runner
└── pyproject.toml  # Entry points configuration
```

**Benefits**:

- ✅ Single source of truth for all tasks
- ✅ Easier to maintain and discover commands
- ✅ Consistent command interface
- ✅ Help menu with `./run --help`
- ✅ No permission issues (`chmod +x` done once)

## Best Practices

### 1. Use `[project.scripts]` for Permanent Commands

Commands that should be **installed** and available as CLI tools:

```toml
[project.scripts]
my-tool = "package.module:main_function"
```

### 2. Use `./run` for Development Tasks

Tasks that are **development-only** and don't need installation:

```bash
./run test
./run lint
./run dev
```

### 3. Use `uv run` Directly for Ad-Hoc Commands

One-off commands or exploration:

```bash
uv run python -c "import package; print(package.__version__)"
uv run pytest tests/test_specific.py -v
```

## VS Code Integration

### Launch Configurations

F5 in VS Code can launch your tasks via `launch.json`:

```json
{
  "configurations": [
    {
      "name": "MCP Server + Inspector",
      "type": "debugpy",
      "request": "launch",
      "module": "launch_mcp_with_inspector",
      "cwd": "${workspaceFolder}/ai-processing"
    }
  ]
}
```

### Tasks Integration

Create VS Code tasks for `./run` commands:

```json
{
  "tasks": [
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "./run test",
      "group": "test"
    }
  ]
}
```

## About `[tool.uv.scripts]`

**Important Note**: `[tool.uv.scripts]` is **NOT officially supported** by UV as of version 0.9.9.

While some unofficial documentation or future proposals may reference it, the official UV documentation does not include this feature. Attempting to use it results in errors:

```toml
# ❌ NOT SUPPORTED - Do not use!
[tool.uv.scripts]
test = "pytest tests/ -v"
```

**Error**:

```
error: unknown field `scripts`, expected one of...
```

**Official UV features instead**:

- ✅ `[project.scripts]` - For installed CLI commands
- ✅ `uv run <command>` - For running commands in project environment
- ✅ Standalone scripts with `# /// script` metadata (PEP 723)

## References

- [UV Scripts Guide](https://docs.astral.sh/uv/guides/scripts/) - Standalone Python scripts with inline metadata (PEP 723)
- [UV Projects Guide](https://docs.astral.sh/uv/guides/projects/) - Working with UV projects
- [UV Running Commands](https://docs.astral.sh/uv/concepts/projects/run/) - Using `uv run`
- [UV Project Configuration](https://docs.astral.sh/uv/concepts/projects/config/) - Configuring `pyproject.toml`
- [PEP 723](https://peps.python.org/pep-0723/) - Inline script metadata specification

## Summary

**Current best practices for PrismWeave**:

1. ✅ Use `[project.scripts]` for installed CLI tools
2. ✅ Use `./run` script for development task running
3. ✅ Use `uv run <command>` for direct command execution
4. ❌ Don't use `[tool.uv.scripts]` (not officially supported)

This provides the best developer experience while using **official UV features** only.
