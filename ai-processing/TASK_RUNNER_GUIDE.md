# Task Runner Guide - PrismWeave AI Processing

This guide explains the task running approaches used in the PrismWeave AI Processing module.

## Quick Reference

```bash
# Recommended: Use the ./run task runner
./run mcp          # Launch server + inspector
./run test         # Run tests
./run --help       # Show all commands

# Alternative: Use UV entry points
uv run prismweave-mcp-inspector  # Launch server + inspector
uv run prismweave-mcp            # Run server only

# Or: Press F5 in VS Code to launch with debugging
```

## Three Task Running Approaches

### 1. Task Runner Script (`./run`) - Recommended for Development

**Best for**: Daily development tasks, quick testing

```bash
./run mcp          # Launch server + inspector together
./run test         # Run all tests
./run lint         # Check code quality
./run --help       # Show all available commands
```

**Advantages**:

- ✅ Simplest UX (similar to npm scripts)
- ✅ Self-documenting with help menu
- ✅ Works with any UV version
- ✅ Easy to customize and extend

**How it works**:

- Simple bash script with case statement
- Runs commands in the virtual environment
- Single source of truth for all tasks

### 2. UV Entry Points (`[project.scripts]`) - For Installed Commands

**Best for**: Commands you want installed and available globally

```bash
uv run prismweave-mcp            # Run MCP server
uv run prismweave-mcp-inspector  # Run server + inspector
uv run prismweave-process        # Run document processor
```

**Advantages**:

- ✅ Official Python packaging standard
- ✅ Commands work from any directory
- ✅ Proper Python entry point format
- ✅ Can be used in other projects

**How it works**:

- Defined in `[project.scripts]` section of `pyproject.toml`
- Installed into virtual environment by `uv sync`
- Standard Python packaging approach

### 3. Direct Commands (`uv run`) - For Ad-Hoc Tasks

**Best for**: One-off commands, exploration, custom invocations

```bash
uv run python -m prismweave_mcp.server --transport sse
uv run pytest tests/test_specific.py -v
uv run ruff check src/
uv run python -c "import prismweave_mcp; print(prismweave_mcp.__version__)"
```

**Advantages**:

- ✅ Maximum flexibility
- ✅ Direct command execution
- ✅ Good for debugging and exploration
- ✅ No configuration needed

**How it works**:

- UV runs command in project's virtual environment
- Automatically activates venv
- No need for explicit `source .venv/bin/activate`

## Comparison with npm

If you're coming from Node.js/npm, here's the equivalent:

| npm            | PrismWeave      |
| -------------- | --------------- |
| `npm run test` | `./run test`    |
| `npm run dev`  | `./run dev`     |
| `npm start`    | `./run mcp`     |
| `npm run lint` | `./run lint`    |
| `npm test`     | `uv run pytest` |

## VS Code Integration

### F5 Debugging

Press **F5** in VS Code to launch the MCP server + inspector with debugging enabled.

**Configuration** (`.vscode/launch.json`):

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

### VS Code Tasks

Available tasks defined in `.vscode/tasks.json`:

- "AI Processing: Run Tests"
- "AI Processing: Run Tests with Coverage"
- "AI Processing: Install Dependencies"

Access via: `Ctrl+Shift+P` → "Tasks: Run Task"

## Implementation Details

### Task Runner Script (`./run`)

Located at: `/home/dhayes/Source/PrismWeave/ai-processing/run`

```bash
#!/usr/bin/env bash
# Task runner for PrismWeave AI Processing Module

set -e  # Exit on error

case "$1" in
  mcp)
    python launch_mcp_with_inspector.py
    ;;
  test)
    pytest tests/ -v
    ;;
  --help|help|"")
    echo "Usage: ./run <command>"
    echo "Available commands: mcp, test, lint, format..."
    ;;
  *)
    echo "Unknown command: $1"
    exit 1
    ;;
esac
```

### Entry Points (`pyproject.toml`)

```toml
[project.scripts]
prismweave-process = "main:main"
prismweave-mcp = "prismweave_mcp.server:main"
prismweave-mcp-inspector = "launch_mcp_with_inspector:main"
```

After `uv sync`, these become available as commands in the virtual environment.

## Available Commands

### MCP Server Commands

| Command                | What it does                                      |
| ---------------------- | ------------------------------------------------- |
| `./run mcp`            | Launch server + inspector together (recommended)  |
| `./run mcp-server`     | Start server only (SSE transport, port 3000)      |
| `./run mcp-stdio`      | Start server only (stdio transport for inspector) |
| `./run mcp-debug`      | Start with debug logging enabled                  |
| `./run inspector-only` | Launch inspector UI only                          |
| `./run dev`            | Auto-restart server on code changes               |

### Testing Commands

| Command          | What it does                       |
| ---------------- | ---------------------------------- |
| `./run test`     | Run all tests with verbose output  |
| `./run test-cov` | Run tests with coverage report     |
| `./run test-mcp` | Test MCP server tools specifically |

### Code Quality Commands

| Command            | What it does                 |
| ------------------ | ---------------------------- |
| `./run lint`       | Check code quality with ruff |
| `./run lint-fix`   | Auto-fix linting issues      |
| `./run format`     | Format code with ruff        |
| `./run type-check` | Run mypy type checking       |

### Setup Commands

| Command        | What it does                          |
| -------------- | ------------------------------------- |
| `./run verify` | Verify installation and configuration |

## Best Practices

### When to Use Each Approach

**Use `./run`** for:

- Daily development tasks
- Quick testing and iteration
- Common workflows (test, lint, run server)

**Use `uv run <entry-point>`** for:

- Running the installed CLI tools
- Production/deployment scenarios
- When you need the full command path

**Use `uv run <command>`** for:

- Exploring and debugging
- Running specific test files
- Custom invocations with specific arguments
- One-off operations

### Customizing Tasks

To add a new task to the `./run` script:

1. Edit `/home/dhayes/Source/PrismWeave/ai-processing/run`
2. Add a new case statement:

```bash
case "$1" in
  # ... existing cases ...

  my-task)
    echo "Running my custom task..."
    python scripts/my_script.py
    ;;

  # ... rest of cases ...
esac
```

3. Update the help message
4. Test: `./run my-task`

## Migration from Shell Scripts

If you're migrating from the old shell scripts:

| Old               | New            |
| ----------------- | -------------- |
| `./inspector.sh`  | `./run mcp`    |
| `./dev.sh`        | `./run dev`    |
| `verify-setup.sh` | `./run verify` |

The old shell scripts can be safely deleted (see [CLEANUP_SCRIPTS.md](CLEANUP_SCRIPTS.md)).

## Troubleshooting

### Command Not Found

**Problem**: `./run: command not found`

**Solution**: Make the script executable:

```bash
chmod +x ./run
```

### Python Module Not Found

**Problem**: `ModuleNotFoundError` when running commands

**Solution**: Ensure dependencies are installed:

```bash
uv sync
```

### UV Entry Point Not Working

**Problem**: `uv run prismweave-mcp` fails

**Solution**:

1. Check `[project.scripts]` in `pyproject.toml`
2. Run `uv sync` to reinstall entry points
3. Verify with: `uv run --help`

### Script Hangs or Doesn't Exit

**Problem**: Command runs but doesn't return to prompt

**Solution**:

- Some commands run in background (like `./run mcp`)
- Use `Ctrl+C` to stop
- Check if background processes are running: `pgrep -la python`

## Further Reading

- [UV_SCRIPTS.md](UV_SCRIPTS.md) - Detailed UV task running guide
- [INSPECTOR_GUIDE.md](INSPECTOR_GUIDE.md) - MCP Inspector usage
- [README.md](README.md) - Complete module documentation
- [UV Documentation](https://docs.astral.sh/uv/) - Official UV docs

## Summary

PrismWeave uses a **multi-approach** task running system:

1. **`./run` script** - Primary interface for development tasks
2. **UV entry points** - Installed commands for production use
3. **Direct `uv run`** - Flexible ad-hoc command execution

This provides:

- ✅ Familiar npm-like UX
- ✅ Official Python packaging compliance
- ✅ Maximum flexibility
- ✅ Cross-platform compatibility
- ✅ Easy maintenance and customization
