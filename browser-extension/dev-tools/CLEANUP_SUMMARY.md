# Dev Tools Cleanup Summary

## Changes Made

### File Naming Convention

Updated to follow browser extension's kebab-case naming convention:

- `simple-url-test.ts` → `url-test-cli.ts`
- `node-markdown-converter.ts` → `markdown-converter-node.ts`

### Output File Naming

Updated output file naming to use kebab-case and improved URL slug generation:

- Removes `https://` protocol from URL slugs
- Uses single dash `-` separator instead of double dash `--`
- Converts to lowercase for consistency
- Example: `example-com-2025-06-27T12-41-00-000Z.md`

### Cleaned Up Files

Removed duplicate and unnecessary files:

- Multiple test variations (`simple-url-test-new.js`, `simple-url-test-tsx.ts`,
  etc.)
- Debug and development files (`debug-test.ts`, `dev-cli.js`, etc.)
- Build artifacts (`dist/`, `src/`, `tsconfig.tsbuildinfo`)
- Documentation files that are no longer relevant

### Essential Files Remaining

- `url-test-cli.ts` - Main CLI tool for URL testing
- `markdown-converter-node.ts` - Node.js wrapper for browser extension core
- `package.json` - Updated with new script names
- `tsconfig.json` - TypeScript configuration
- `README.md` - Updated documentation
- `test-outputs/` - Directory for generated test results

### TypeScript Improvements

- Added proper type annotations
- Fixed error handling for unknown error types
- Made `originalHtml` optional in interface to match actual implementation

## Usage

```bash
npm run test-url "https://example.com/article"
```

Files are now consistent with browser extension naming conventions and the
directory is clean and focused.
