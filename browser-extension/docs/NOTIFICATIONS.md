# PrismWeave Notification System

This document describes the unified toast notification mechanism shared across:

- Browser extension pages (popup, options, injected contexts)
- Content scripts / in‑page extraction flows
- Generated bookmarklets (self‑contained capture tool)

As of the latest unification pass the **visual styling and token usage are
identical** across all surfaces.

## Overview

Historically the bookmarklet used blocking `alert()` dialogs for success / error
feedback. The extension UI defined toast styles in `src/styles/shared-ui.css`
but there was no reusable JS helper and no integration for bookmarklets.

## Implementation

The utility `src/utils/toast.ts` exports
`showToast(message, { type, duration, dismissible })` which:

- Injects the **canonical toast CSS subset** (variable tokens + toast block) if
  not already present.
- Ensures a single `.pw-toast-container` (top‑right stack) exists.
- Renders transient toast elements with `success | error | info` variants.
- Auto‑dismisses after 4s by default (configurable via `duration`, pass `0` to
  persist until manually dismissed if `dismissible` is true).
- Provides an accessible structure (`role="status"`, polite live region
  behaviour).
- Exposes a global helper `window.prismweaveShowToast` for
  bookmarklet/content‑script convenience.

### Canonical Styling

Instead of a bespoke minimal style, both the extension and bookmarklet now use
an identical **canonical toast CSS subset** distilled from
`src/styles/shared-ui.css`:

Included tokens (only those required by the toast block):

```
--pw-space-3, --pw-space-4, --pw-space-5,
--pw-radius-lg,
--pw-font-family,
--pw-success-500, --pw-error-500, --pw-primary-500, --pw-warning-500,
--pw-shadow-lg, --pw-z-modal
```

The bookmarklet inlines this subset for self‑containment. If the full shared
stylesheet is already present (extension UIs) the variables simply merge without
conflict.

No additional site styles are relied upon, keeping rendering consistent on
arbitrary third‑party pages.

### Bookmarklet Integration

`src/bookmarklet/generator.ts` injects the identical canonical CSS + helper
logic. This replaced the earlier ad‑hoc “minimal” style, eliminating visual
drift. The inline helper will **not** downgrade to `alert()` — per policy there
is no legacy fallback.

## Usage

```ts
import { showToast } from '../utils/toast';
showToast('Saved successfully', { type: 'success' });
showToast('Something went wrong', { type: 'error', duration: 6000 });
```

From a page where the bookmarklet runs:

```js
window.prismweaveShowToast('Captured!', 'success');
```

## Design Goals

- Non‑blocking feedback with polished animation parity.
- Identical color / spacing / elevation tokens across all contexts.
- Minimal injected payload (only necessary variables + rules) for bookmarklet.
- Opinionated: no native alerts; single UI surface.
- Stable class names to allow future progressive enhancements (queueing,
  progress indicators) without breaking existing integrations.

## Future Enhancements

- Toast queue management (max N visible, FIFO dismissal)
- Optional progress / activity variant (e.g., embedding spinner or progress bar)
- Return handle object: `{ id, dismiss }` for programmatic lifecycle control
- Theme switching hook (dark / high contrast tokens injection)
- Optional telemetry events (capture success rate, error taxonomy)
