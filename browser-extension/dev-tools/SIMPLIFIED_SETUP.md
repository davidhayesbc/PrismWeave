# Simplified Local Development Setup for PrismWeave Bookmarklet Generator

This simplified setup leverages the existing TypeScript code from `generator.ts`
instead of duplicating the logic.

## Quick Start

1. **Build the TypeScript generator:**

   ```powershell
   cd browser-extension
   npm run build:bookmarklet
   ```

2. **Start the local server:**

   ```powershell
   cd dev-tools
   .\start-local-dev.ps1
   ```

3. **Open the simplified generator:**
   - Browser will automatically open to: http://localhost:8080
   - Navigate to: **Simplified Generator** → `simplified-local-generator.html`

## How It Works

### Code Reuse Strategy

- ✅ **Uses existing TypeScript**: Compiles `src/bookmarklet/generator.ts` to
  `dist/bookmarklet/generator.js`
- ✅ **Leverages existing HTML**: Loads the original `generator.html` template
  dynamically
- ✅ **Reuses CSS**: Uses the shared `shared-ui.css` from the project
- ✅ **No duplication**: No duplicate JavaScript implementation

### Build Process

The existing build system (`build.js`) includes a `bookmarklet-generator` target
that:

- Compiles `src/bookmarklet/generator.ts` → `dist/bookmarklet/generator.js`
- Uses esbuild with IIFE format for browser compatibility
- Includes source maps for debugging

### File Structure

```
browser-extension/
├── src/bookmarklet/
│   ├── generator.ts          # Original TypeScript (364 lines)
│   ├── generator.html        # Original HTML template
│   └── ...
├── dist/bookmarklet/
│   ├── generator.js          # Compiled output (auto-generated)
│   └── ...
└── dev-tools/
    ├── simplified-local-generator.html  # New simplified loader
    ├── start-local-dev.ps1            # Existing server script
    └── ...
```

## Development Workflow

### Initial Setup

```powershell
# One-time setup
cd browser-extension
npm install
npm run build:bookmarklet
```

### Daily Development

```powershell
# Start local development
cd dev-tools
.\start-local-dev.ps1

# Make changes to generator.ts, then rebuild:
cd ..\browser-extension
npm run build:bookmarklet

# Refresh browser to see changes
```

### Auto-Rebuild (Optional)

For continuous development, you can watch for changes:

```powershell
# In one terminal - watch for changes
cd browser-extension
npx esbuild src/bookmarklet/generator.ts --outfile=dist/bookmarklet/generator.js --bundle --format=iife --platform=browser --watch

# In another terminal - serve files
cd dev-tools
.\start-local-dev.ps1
```

## Benefits of Simplified Approach

### ✅ Code Reuse

- No duplicate JavaScript implementation
- Single source of truth in `generator.ts`
- Consistent behavior between development and production

### ✅ Maintenance

- Changes only need to be made in `generator.ts`
- Uses existing build system and configurations
- Leverages existing CSS and HTML templates

### ✅ Development Experience

- Fast rebuilds with esbuild
- Source maps for debugging
- Hot reload by refreshing browser
- Full TypeScript tooling support

### ✅ Production Alignment

- Same build process used for extension
- Same compiled output format
- Identical functionality to production bookmarklet

## Comparison with Previous Approach

| Aspect                   | Previous (Standalone HTML) | Simplified (TypeScript Build) |
| ------------------------ | -------------------------- | ----------------------------- |
| **Code Duplication**     | ❌ JavaScript duplicated   | ✅ Single TypeScript source   |
| **Maintenance**          | ❌ Two places to update    | ✅ One place to update        |
| **Build Process**        | ❌ Custom standalone       | ✅ Uses existing build system |
| **Development Speed**    | ✅ No build step           | ⚡ Fast esbuild compilation   |
| **Production Alignment** | ❌ Different code paths    | ✅ Identical code paths       |
| **Type Safety**          | ❌ No TypeScript           | ✅ Full TypeScript support    |

## Troubleshooting

### Generator Not Loading?

1. **Check build**: Run `npm run build:bookmarklet` first
2. **Check server**: Ensure local server is running on port 8080
3. **Check console**: Look for JavaScript errors in browser DevTools

### Build Errors?

1. **Install dependencies**: Run `npm install` in browser-extension folder
2. **Check TypeScript**: Ensure TypeScript code compiles without errors
3. **Check paths**: Verify file paths in build configuration

### CSS Not Loading?

1. **Check relative paths**: Ensure CSS paths are correct for dev-tools folder
2. **Server root**: Verify server is serving from correct directory

## Next Steps

### Potential Enhancements

1. **Live Reload**: Add file watching for automatic browser refresh
2. **Source Maps**: Enable source map support for easier debugging
3. **Hot Module Replacement**: Implement HMR for even faster development
4. **Testing Integration**: Add automated testing for generator functionality

### Integration Opportunities

1. **VS Code Extension**: Integrate with the VS Code extension development
2. **CI/CD**: Include in automated build and test pipeline
3. **Documentation**: Auto-generate documentation from TypeScript comments
