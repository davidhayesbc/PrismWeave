# VS Code Extension Development Guide

## Launch Configurations

The extension includes three launch configurations:

### 1. Run Extension
- **Purpose**: Launch the extension in a new VS Code window for testing
- **Pre-launch**: Compiles TypeScript code
- **Usage**: Press F5 or use "Run Extension" from the debug panel

### 2. Run Extension (Watch Mode)
- **Purpose**: Launch with automatic recompilation on file changes
- **Pre-launch**: Starts TypeScript watch mode
- **Usage**: Best for active development

### 3. Extension Tests
- **Purpose**: Run the test suite
- **Pre-launch**: Compiles TypeScript code
- **Usage**: For testing extension functionality

## Development Workflow

1. **Initial Setup**:
   ```bash
   npm install
   npm run compile
   ```

2. **Development**:
   - Use "Run Extension (Watch Mode)" for continuous development
   - Make changes to TypeScript files
   - Changes are automatically compiled and reloaded

3. **Testing**:
   - Use "Extension Tests" configuration
   - Or run: `npm test`

## Available Tasks

- **Build**: `npm run compile` - Compile TypeScript once
- **Watch**: `npm run watch` - Compile with file watching
- **Lint**: `npm run lint` - Run ESLint
- **Test**: `npm run test` - Run extension tests

## Settings

The `.vscode/settings.json` configures:
- TypeScript auto-imports
- ESLint integration
- File exclusions for better performance
- Code formatting on save

## Extension Testing

To test your extension:

1. Press F5 to open a new VS Code window
2. In the new window, your extension will be loaded
3. Open the Command Palette (Ctrl+Shift+P)
4. Look for "PrismWeave" commands
5. Click the robot icon in the Activity Bar to open the sidebar

## Configuration

The extension can be configured in VS Code settings:
- `prismweave.chromadb.host`: ChromaDB server host
- `prismweave.chromadb.port`: ChromaDB server port
- `prismweave.model.provider`: Model provider (onnx, phi-silica, custom)
- `prismweave.model.name`: Model name or path

## Troubleshooting

If the extension doesn't load:
1. Check the Developer Console (Help > Toggle Developer Tools)
2. Look for error messages in the console
3. Verify all dependencies are installed
4. Try recompiling with `npm run compile`
