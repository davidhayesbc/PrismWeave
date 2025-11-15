# Shell Scripts Cleanup

The following shell scripts in `ai-processing/` are **no longer needed** and can be safely deleted. They have been replaced by the unified `./run` task runner script and `[project.scripts]` entry points.

## Scripts to Delete

```bash
# Delete these files:
rm inspector.sh
rm dev.sh
rm verify-setup.sh
```

## Replacements

| Old Script        | New Command    | What it does                        |
| ----------------- | -------------- | ----------------------------------- |
| `./inspector.sh`  | `./run mcp`    | Launch server + inspector together  |
| `./dev.sh`        | `./run dev`    | Auto-restart server on code changes |
| `verify-setup.sh` | `./run verify` | Verify setup/installation           |

Alternative using UV entry points:

```bash
uv run prismweave-mcp-inspector  # Same as ./run mcp
uv run prismweave-mcp            # Run server only
```

## New Functionality

### Combined Server + Inspector Launch

The new `./run mcp` command launches **both** the MCP server and inspector together:

```bash
# Old way (two separate commands):
python -m prismweave_mcp.server --transport sse &
./inspector.sh

# New way (one command):
./run mcp
# Or: uv run prismweave-mcp-inspector
# Or: Press F5 in VS Code
```

## VS Code Integration

The first launch configuration in `.vscode/launch.json` is now "MCP Server + Inspector", which means:

- **F5** launches both server and inspector
- No need to manually run scripts
- Integrated debugging support

## Benefits of Unified Task Runner

✅ **Cross-platform** - Works on Windows (Git Bash), Linux, Mac  
✅ **Single file** - All tasks in one place (`./run`)  
✅ **Self-documenting** - `./run --help` shows all commands  
✅ **No dependency issues** - Works with any UV version  
✅ **Easy to maintain** - Simple bash case statement

## Available Commands

See [UV_SCRIPTS.md](UV_SCRIPTS.md) for complete documentation.

Quick reference:

```bash
./run mcp          # Launch server + inspector
./run test         # Run tests
./run test-cov     # Run tests with coverage
./run dev          # Auto-reload server
./run lint-fix     # Fix code quality issues
./run --help       # Show all commands
```

## Migration Notes

**Why not `[tool.uv.scripts]`?**

After reviewing the official UV documentation, `[tool.uv.scripts]` is **not an official UV feature** as of version 0.9.9. The official UV approaches are:

1. `[project.scripts]` - For installed CLI commands
2. `uv run <command>` - For running commands directly
3. Custom task runners (like our `./run` script)

This is why we use a combination of:

- `[project.scripts]` for entry points
- `./run` script for development tasks
- `uv run` for ad-hoc commands
