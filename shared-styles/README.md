# PrismWeave Shared Styles

Canonical source of design tokens and shared UI styles used across:

- Website (`/website`)
- Browser extension (`/browser-extension`)
- Other tools in this repo

## Files

- `design-tokens.css`: CSS custom properties for colors, typography, spacing, elevation, and themes (light/dark). Includes legacy alias variables (e.g., `--muted-color`) for backward compatibility.
- `shared-ui.css`: Reusable UI primitives (buttons, cards, modals, utilities) that import `design-tokens.css`.

## How to consume

Prefer linking directly to the files in this directory to avoid duplication:

- From the website CSS (proxy example already wired): `website/assets/styles/shared-ui.css` imports `../../../shared-styles/shared-ui.css`.
- From the browser extension styles: import via relative path up to this folder (see `browser-extension/src/styles/extension-base.css`).

If you previously duplicated these files elsewhere, please remove the copies and import from here instead.

## Notes

- `shared-ui.css` already imports `design-tokens.css`, so you typically only need to import `shared-ui.css`.
- Keep changes backwards-compatible: avoid renaming variables/classes without a migration.
- When adding new tokens, include sensible dark-mode values and update the legacy aliases if appropriate.
