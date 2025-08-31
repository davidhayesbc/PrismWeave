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

To serve locally:
```
npm run build:web
npm run serve:web
```
Then open http://localhost:8080/.