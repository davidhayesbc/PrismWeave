# Quick Fix: VS Code Test Runner Not Showing Tests

## What Changed

Created per-folder Jest configuration files to properly support multi-root workspace:

### New Files:
1. **`browser-extension/.vscode/settings.json`**
   ```json
   {
     "jest.jestCommandLine": "npm test --"
   }
   ```

2. **`cli/.vscode/settings.json`**
   ```json
   {
     "jest.jestCommandLine": "npm test --"
   }
   ```

### Updated Files:
- **`.vscode/settings.json`** - Simplified Jest config to enable auto-detection

## Why This Works

VS Code's Jest extension in multi-root workspaces works best when:
- Each project folder with tests has its own `.vscode/settings.json`
- The workspace-level settings are minimal
- The extension can auto-detect tests in each folder independently

## How to Make Tests Appear

1. **Reload VS Code**: 
   - Press `Ctrl+Shift+P`
   - Type "Developer: Reload Window"
   - Press Enter

2. **Open Test Explorer**:
   - Click the beaker icon in the sidebar (Testing panel)
   - Or press `Ctrl+Shift+T`

3. **Wait for Discovery**:
   - VS Code will scan both folders
   - You should see two test tree roots:
     - `browser-extension` (14 test files)
     - `cli` (4 test files with 120 tests)

## If Tests Still Don't Appear

1. Check Output Panel:
   - `Ctrl+Shift+U` to open Output
   - Select "Jest" from the dropdown
   - Look for any error messages

2. Verify Jest Extension:
   - Check if "Jest" extension by Orta is installed
   - If not, install it from Extensions marketplace

3. Manual Test Run:
   - Open terminal in `cli` folder
   - Run: `npm test`
   - Verify tests run successfully (should see 120 passing tests)

4. Try Native Testing:
   - VS Code has built-in testing support for Jest
   - Sometimes it works better than the Jest extension
   - Look for test run buttons in the gutter (left of line numbers) in test files

## Verifying Configuration

Run these commands to verify everything is set up correctly:

```powershell
# From PrismWeave root directory
cd browser-extension
npm test -- --listTests

cd ../cli  
npm test -- --listTests
```

Both should list their respective test files.
