# VS Code Jest Extension Troubleshooting

## Current Status
✅ **All 120 tests are PASSING** when run from command line
- `npm test` shows: Test Suites: 4 passed, Tests: 120 passed

## Common VS Code Test Explorer Issues

### Issue 1: Tests Show as Failing Despite Passing
**Symptom**: Tests pass in terminal but VS Code Test Explorer shows them as failing

**Causes**:
1. **Console warnings interpreted as failures**: The expected console.warn in config.test.ts may confuse the extension
2. **Experimental warnings**: Node.js warnings about VM Modules may be parsed as errors
3. **Output formatting**: Jest output may not be parsed correctly by VS Code extension

**Solutions**:
1. **Reload VS Code**: `Ctrl+Shift+P` → "Developer: Reload Window"
2. **Clear Jest cache**: Run `npm test -- --clearCache` then reload
3. **Check Jest Output panel**: View → Output → Select "Jest" from dropdown
4. **Disable test auto-run**: Let tests run only on-demand

### Issue 2: Tests Not Discovered
**Current Config** (`.vscode/settings.json` in cli folder):
```json
{
  "jest.jestCommandLine": "npm test --"
}
```

**If tests still not visible**:
1. Check Jest extension is installed: "Jest" by Orta
2. Enable Jest: `Ctrl+Shift+P` → "Jest: Start Runner"
3. Check workspace folder: Make sure you're in the `cli` folder context

### Issue 3: Expected Console Output Shows as Errors
**Example**: This warning is EXPECTED from a test:
```
console.warn
  Failed to load config: Unexpected token 'i', "invalid json {{{" is not valid JSON
```

This comes from the test: "should handle corrupted config file gracefully" in `config.test.ts`

**The test intentionally creates a corrupted config to verify error handling.**

## Manual Test Verification

Run tests manually to confirm they pass:
```bash
cd cli
npm test
```

Expected output:
```
Test Suites: 4 passed, 4 total
Tests:       120 passed, 120 total
```

## VS Code Jest Extension Limitations

The Jest extension sometimes has trouble with:
- ES Module projects (`"type": "module"`)
- Experimental Node.js features (`--experimental-vm-modules`)
- Complex Jest configurations with transforms

**Workaround**: Run tests from terminal instead of relying solely on Test Explorer

## Recommended Workflow

1. **Development**: Use `npm test -- --watch` in terminal for live feedback
2. **Verification**: Run `npm test` before committing
3. **VS Code Integration**: Use Test Explorer for navigation, but trust terminal output

## Test Coverage Verification

Check coverage:
```bash
cd cli
npm run test:coverage
```

Open `coverage/index.html` in browser to see detailed coverage report.

## Configuration Files

- `jest.config.js` - Jest configuration (ES modules, ts-jest)
- `.vscode/settings.json` - VS Code Jest extension config
- `package.json` - Test scripts and dependencies
- `tsconfig.json` - TypeScript compilation settings

## Quick Checks

✅ All tests pass in terminal: `npm test`
✅ TypeScript compiles: `npm run build`
✅ No actual test failures
⚠️ Console warnings are expected (from error handling tests)
⚠️ Experimental warnings are normal (Node.js VM Modules)

## Bottom Line

**Your tests are working correctly!** 🎉

If VS Code Test Explorer shows failures but `npm test` shows all passing, trust the terminal output. The console warnings you see are intentional test outputs, not actual failures.
