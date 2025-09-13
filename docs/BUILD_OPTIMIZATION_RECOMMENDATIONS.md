# PrismWeave Build System: Optimization & Simplification Roadmap

This document captures concrete opportunities to further simplify and speed up the current build / dev workflow without introducing heavy tooling. Items are ordered roughly by ROI (highest impact first) and marked with suggested implementation patterns.

---
## 1. Incremental Web Deployment Copy (Implemented Prototype)
Current `buildWebDeployment()` always re-copies every file from website/, extension dist, and bookmarklet dist. For rapid iteration (e.g. editing a single CSS file) this is wasteful.

### Approach
Maintain a JSON manifest (`.build-cache/web-copy-manifest.json`) mapping source file absolute path -> `{ mtimeMs, size, hash }`. During each web build:
1. Walk copy sources, compare stat (mtime,size). When mismatch or manifest miss: copy + (optionally) hash.
2. Remove orphaned outputs when a source file is deleted (tracked via inverse mapping `dest -> src`).
3. Persist updated manifest.

### Benefits
* Large static directories (icons, libs) skipped when unchanged.
* Enables future `--fast` flag for web rebuilds invoked by the dev server.

### Future Enhancement
* Add optional SHA1/xxhash only when (mtime,size) changed to avoid extra IO.
* Record cumulative bytes skipped vs copied for telemetry.

---
## 2. Fast Path Web Build Flag (`--fast`)
Introduce a reduced build that:
* Skips rebuilding extension + bookmarklet when their existing dist outputs are present and newer than the last web copy.
* Only runs incremental copy + template render + manifest regeneration.

Command example:
```
node build.js web --fast
```
The dev watcher can use this flag for sub‑second rebuilds of website asset edits.

---
## 3. Shared Esbuild Config Extract
Currently `build-simple.js` defines `baseOptions` plus repeated blocks per target. Create `browser-extension/scripts/esbuild.common.js` exporting a factory:
```js
module.exports = ({minify,sourcemap}) => ({
  target:'es2020', platform:'browser', bundle:true, minify, sourcemap,
  define: { 'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV||'development') }
});
```
Reduces duplication between prod & dev builds and prepares for additional entry points.

---
## 4. Consolidate Extension & Bookmarklet Build Scripts
`build-bookmarklet.js` and `build-simple.js` share logic (esbuild invocation, static asset copy). Create a unified `scripts/build-extension.js` with tasks:
* `buildExtension()`
* `buildBookmarklet()`
* `buildAll()`
Allow `node scripts/build-extension.js --bookmarklet --extension --watch` selection flags.

---
## 5. Parallelization Safeguards
When future parallel builds are introduced (e.g. web + extension concurrently) protect shared `dist/` writes via a simple mutex file `.build-lock` to avoid partial copy states.

---
## 6. Optional Hash-Based Content Addressed Assets
For long‑term CDN deployment, generate hashed filenames for large static assets (e.g. `shared-ui.[hash].css`) and inject into `index.html`. Keep original dev names when `NODE_ENV!=='production'`.

---
## 7. Test Coverage Targets
Add lightweight tests for the build system (using Jest in root or a small node test harness):
* Incremental copy manifest skip path.
* Orphan removal when source deleted.
* Template token replacement in `index.html`.

---
## 8. DX Improvements
* Add `npm run dev:ext` to run extension esbuild watch only.
* Add `npm run dev:all` to run extension watch + `serve-web.js --watch` concurrently (`npm-run-all -p`).

---
## 9. Metrics & Logging
Emit summary per build:
```
Web Build Summary:
  Copied: 12 files (48 KB)
  Skipped (cached): 154 files (2.3 MB)
  Removed: 1 obsolete file
  Duration: 320ms (fast mode)
```

---
## 10. Future: Move to Single Build Graph
If complexity grows, adopt a lightweight graph (nodes = targets, edges = deps, each node has `inputs -> outputs`). For now the incremental copy + fast flag should suffice.

---
## Status Legend
| Item | Status |
|------|--------|
| Incremental copy manifest | Prototype implemented (see `build.js`) |
| Fast path flag | Implemented (`--fast`) |
| Shared esbuild config | Pending |
| Unified extension script | Pending |
| Hash-based assets | Planned |
| Tests for build system | Pending |

---
## Changelog
* 2025-09-13: Initial roadmap + incremental copy & fast path implementation.
