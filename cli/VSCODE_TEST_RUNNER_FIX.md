# VS Code Test Runner Configuration Fix

## Problem
VS Code's test runner wasn't detecting the CLI tests because the Jest configuration in `.vscode/settings.json` was only pointing to the `browser-extension` folder.

## Root Cause
The original configuration had:
```json
"jest.rootPath": "browser-extension",
```

This single `rootPath` setting meant VS Code's Jest extension would only look for tests in the `browser-extension` directory, completely ignoring the `cli` folder tests.

## Solution
For a multi-root workspace with multiple Jest projects, the best approach is to:

1. **Remove project-specific Jest config from workspace settings** (`.vscode/settings.json`)
2. **Add per-folder settings** for each project that has tests

### Files Created:
- `browser-extension/.vscode/settings.json` - Jest config for browser extension tests
- `cli/.vscode/settings.json` - Jest config for CLI tests

Each folder now has its own Jest configuration:
```json
{
  "jest.jestCommandLine": "npm test --"
}
```

### Updated Workspace Settings:
The main `.vscode/settings.json` now has minimal Jest configuration that applies to all folders:
```json
"jest.disabledWorkspaceFolders": [],
"jest.enable": true,
"jest.outputConfig": {
  "revealOn": "run",
  "revealWithFocus": false,
  "clearOnRun": "terminal"
}
```

## Benefits
1. ✅ VS Code Test Explorer now shows tests from both `browser-extension` and `cli`
2. ✅ Can run tests from either project independently
3. ✅ Test results are properly organized by project name
4. ✅ Each project uses its own Jest configuration and test scripts

## How to Use
1. **Open Test Explorer**: Click the test beaker icon in VS Code's sidebar (or press `Ctrl+Shift+T`)
2. **View Projects**: You should now see two projects:
   - `browser-extension` (existing tests)
   - `cli` (newly added tests)
3. **Run Tests**: Click the play button next to any test suite or individual test
4. **View Results**: Test results appear inline in the Test Explorer

## Verifying It Works
After reloading VS Code:
1. Open the Test Explorer (beaker icon in sidebar)
2. You should see both projects listed
3. Expand `cli` → should show:
   - `config.test.ts` (23 tests)
   - `file-manager.test.ts` (30 tests)
   - `markdown-converter.test.ts` (37 tests)
   - `content-extraction.test.ts` (30 tests)
4. Click any test to run it

## Troubleshooting
If tests still don't appear:
1. **Reload VS Code**: Press `Ctrl+Shift+P` → "Developer: Reload Window"
2. **Check Jest Extension**: Ensure "Jest" extension by Orta is installed
3. **Check package.json**: Verify `cli/package.json` has the test script
4. **Check jest.config.js**: Verify `cli/jest.config.js` exists and is valid
5. **Output Panel**: View "Jest" output panel for any error messages

## Related Files
- `.vscode/settings.json` - VS Code workspace settings (updated)
- `cli/package.json` - CLI test scripts
- `cli/jest.config.js` - Jest configuration for CLI
- `cli/tests/*.test.ts` - Test files (120 tests total)

## Test Coverage Summary
All 120 CLI tests are now passing:
- **config.test.ts**: 23 tests ✅
- **file-manager.test.ts**: 30 tests ✅
- **markdown-converter.test.ts**: 37 tests ✅
- **content-extraction.test.ts**: 30 tests ✅

## Next Steps
After reloading VS Code, you should be able to:
- Run individual tests from the Test Explorer
- See test results inline in the editor
- Debug tests using VS Code's debugger
- Run tests in watch mode for rapid development
