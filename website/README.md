# PrismWeave Website (Source)

This folder contains the source assets for the static website that is deployed to GitHub Pages and served locally with `npm run serve:web`.

Build output is written to `dist/web/` by the root `build.js` script.

Contents:
- `index.html` — Template home page used by the build script. It contains template tokens that are replaced during build.
- `assets/` — Place static files (images, CSS, JS) required by the website. These will be copied to `dist/web/assets/` on build.

Notes:
- Do not put build artifacts in this folder. Only source files that should be copied or templated into the web distribution.
- The build pipeline replaces tokens in `index.html`:
  - `{{VERSION}}` from `package.json`
  - `{{BUILD_DATE}}` current ISO datetime
  - `{{ENVIRONMENT}}` production/development

## Local Development / Preview

Fastest full cycle (build everything + serve with auto-rebuild of the web bundle):
```
npm run dev:web
```
This will:
1. Build the browser extension, bookmarklet, and web bundle (same as `npm run build:web`)
2. Start the local server at http://localhost:8080/
3. Watch `website/` (and existing built `dist/bookmarklet`, `dist/browser-extension`) for changes, automatically rebuilding the web distribution with a short debounce.

If you have already built assets and only want to serve & watch website changes (skipping a fresh build):
```
npm run watch:web
```

One‑shot build + serve (no watching):
```
npm run build:web
npm run serve:web
```

Open: http://localhost:8080/

### Changing Only Website Assets
Edits to files under `website/` (HTML/CSS) trigger a quick rebuild of the web output. Extension or bookmarklet code is **not** rebuilt unless you explicitly run their build scripts.

### Rebuild Performance Tips
* For iterative website styling/content work: use `watch:web`.
* For end-to-end validation after extension or bookmarklet changes: use `dev:web`.
* If favicon/logo changes, re-run a full `npm run build:web` to regenerate favicons.