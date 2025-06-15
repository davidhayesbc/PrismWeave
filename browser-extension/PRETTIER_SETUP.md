# Prettier Configuration

This project uses [Prettier](https://prettier.io/) for consistent code
formatting across all JavaScript, JSON, HTML, CSS, and Markdown files.

## Setup

### Install Dependencies

```bash
npm install
```

This will install Prettier and related tools as specified in `package.json`.

### VS Code Integration

If you're using VS Code, install the
[Prettier extension](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)
for automatic formatting:

1. Install the extension: `ext install esbenp.prettier-vscode`
2. The project includes VS Code settings in `.vscode/settings.json` that will:
   - Enable format on save
   - Use Prettier as the default formatter
   - Integrate with ESLint

## Available Scripts

### Format All Files

```bash
npm run format
```

Formats all supported files in the project.

### Check Formatting

```bash
npm run format:check
```

Checks if all files are properly formatted without making changes. Useful for
CI/CD.

### Format Staged Files (Git)

```bash
npm run format:staged
```

Formats only files that are staged for commit. Great for pre-commit hooks.

### Format with ESLint Fix

```bash
npm run lint:fix
```

Runs ESLint with auto-fix, then you can run `npm run format` for full
formatting.

## Configuration Details

### Main Configuration (`.prettierrc.json`)

```json
{
  "printWidth": 100, // Line length that Prettier will wrap on
  "tabWidth": 2, // Number of spaces per indentation level
  "useTabs": false, // Use spaces instead of tabs
  "semi": true, // Add semicolons at end of statements
  "singleQuote": true, // Use single quotes instead of double
  "trailingComma": "es5", // Add trailing commas where valid in ES5
  "bracketSpacing": true, // Print spaces between brackets in object literals
  "arrowParens": "avoid" // Omit parentheses when possible in arrow functions
}
```

### File-Specific Overrides

- **JSON files**: 80 character line width for better readability
- **Markdown files**: 80 character width with prose wrapping
- **HTML files**: 120 character width, single attribute per line
- **CSS files**: 120 character width, double quotes
- **Manifest files**: No trailing commas for JSON compatibility

### Ignored Files (`.prettierignore`)

The following are automatically ignored:

- `node_modules/` and other dependencies
- Build outputs (`dist/`, `*.min.js`)
- Binary files (images, fonts)
- Generated files and lock files
- Documentation that shouldn't be auto-formatted

## Workflow Integration

### Pre-commit Hook (Recommended)

Add to your `package.json`:

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "pretty-quick --staged"
    }
  }
}
```

### CI/CD Integration

Add to your CI pipeline:

```bash
# Check formatting in CI
npm run format:check

# Check linting
npm run lint
```

## Browser Extension Specific Notes

### Service Worker Formatting

- Service workers use `importScripts()` which Prettier handles correctly
- Chrome extension APIs are preserved with proper formatting

### Manifest Files

- `manifest.json` uses special formatting rules (no trailing commas)
- Content scripts and background scripts are formatted consistently

### HTML/CSS in Extension

- Popup and options pages get consistent formatting
- CSS in extension contexts follows web standards

## Common Commands

```bash
# Format just JavaScript files
prettier --write "src/**/*.js"

# Format just the manifest
prettier --write manifest.json

# Check a specific file
prettier --check src/background/service-worker.js

# Format and show diff
prettier --write --list-different "src/**/*.js"
```

## Integration with ESLint

This project uses both ESLint and Prettier:

1. **ESLint**: Handles code quality rules (unused variables, etc.)
2. **Prettier**: Handles code formatting (spacing, quotes, etc.)

The configuration ensures they work together without conflicts:

- ESLint focuses on code quality
- Prettier focuses on formatting
- No overlapping rules that would cause conflicts

## Troubleshooting

### Format on Save Not Working

1. Ensure Prettier extension is installed in VS Code
2. Check that `.prettierrc.json` exists in project root
3. Verify VS Code settings in `.vscode/settings.json`

### Conflicts with ESLint

- Run `npm run lint:fix` first, then `npm run format`
- The configurations are designed to work together

### Files Not Being Formatted

- Check if the file extension is in the format script patterns
- Verify the file isn't listed in `.prettierignore`
- Ensure the file has valid syntax (Prettier skips files with syntax errors)

## Benefits

✅ **Consistent formatting** across the entire codebase ✅ **Automatic
formatting** on save reduces manual work  
✅ **Team consistency** when multiple developers work on the project ✅
**Reduced diff noise** from formatting changes ✅ **Integration** with existing
ESLint setup ✅ **Browser extension optimized** settings for manifest files and
service workers
