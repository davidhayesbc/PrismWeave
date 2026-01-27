# PrismWeave Website (Source)

This folder contains the source assets for the static website that is deployed to GitHub Pages.

Build output is written to `dist/web/` by the `scripts/build-web.js` script.

## Contents

- `index.html` — Template home page used by the build script
- `assets/` — Static files (images, CSS, JS)
- `dist/` — Build output (generated, not in source control)

## Development

### Start All Services (Recommended)

The fastest way to develop is using Aspire, which runs all services including the website:

```bash
npm run dev
```

This starts:

- Website at http://localhost:4003
- Aspire Dashboard at http://localhost:4000
- All other PrismWeave services

The Aspire dashboard provides integrated logging, metrics, and health checks for all services.

### Build Website Only

To build just the website component:

```bash
npm run build --workspace=website
```

### Build Full Web Distribution

To build the complete web distribution (website + browser extension + bookmarklet):

```bash
npm run build:web
```

This will:

1. Build website assets
2. Build browser extension
3. Assemble everything into `dist/web/`

### Quick Static Preview

If you need a quick static file server (without Aspire):

```bash
npx serve dist/web
```

## Build Notes

- Do not put build artifacts in this folder. Only source files.
- Brand assets (logos, icons) are generated from `logo.svg` during build
