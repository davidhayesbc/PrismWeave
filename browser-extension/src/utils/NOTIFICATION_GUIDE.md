# Unified Notification System Guide

## Overview

PrismWeave uses a **single unified notification API** (located at
`src/utils/notifications/index.ts`) that automatically selects the best display
method based on the execution environment. This provides consistent UX while
leveraging the most appropriate notification mechanism for each context.

## Architecture

### Directory Structure

```
src/utils/notifications/
├── index.ts              # PUBLIC API - Import from here
└── toast-internal.ts     # Internal implementation (DO NOT import directly)
```

**CRITICAL RULE**: Always import from `src/utils/notifications/index.ts` or
`../utils/notifications`. Never import `toast-internal.ts` directly unless
you're working on injectable/bookmarklet code that runs in isolated page
contexts.

### Fallback Strategy

```
1. Popup Status UI (popup.html only)
   ↓ (if unavailable or not appropriate)
2. In-Page Toast (toast-internal.ts)
   ↓ (if DOM unavailable)
3. Chrome Notifications API
   ↓ (if all else fails)
4. Console Logging
```

### Components

- **`notifications/index.ts`** - Main unified API (USE THIS EVERYWHERE)
- **`notifications/toast-internal.ts`** - In-page toast implementation (called
  internally by index.ts)
- **`popup.ts`** - Popup status UI with progress/actions (integrated with
  notifications system)

## Usage

### Basic Usage

```typescript
import { notify, notification } from '../utils/notifications';

// Simple notification
notify('Page captured successfully');

// With options
notify('Processing content...', {
  type: 'info',
  message: 'This may take a moment',
  duration: 5000,
});

// Using convenience methods
notification.success('Saved to repository', {
  clickUrl: 'https://github.com/user/repo/commit/abc123',
  linkLabel: 'View Commit',
});

notification.error('Failed to save', {
  message: 'Network connection lost',
  duration: 0, // Persistent until dismissed
});

notification.warning('Settings incomplete', {
  message: 'Please configure GitHub token',
});

notification.info('Processing started');
```

### Environment-Specific Behavior

#### Popup Context (popup.html)

Shows sophisticated status UI with progress bars and action buttons:

```typescript
import { configureNotificationContext, notify } from '../utils/notifications';

// In popup constructor
configureNotificationContext({
  isPopup: true,
  popupStatusHandler: this.updateCaptureStatus.bind(this),
});

// Then use notify() anywhere
notify('Capturing content...', {
  type: 'progress',
  showProgress: true,
  progressValue: 50,
  message: 'Extracting and processing content',
  actions: [
    {
      label: 'View Repository',
      action: () => this.openRepository(),
      primary: true,
    },
    {
      label: 'Try Again',
      action: () => this.retry(),
    },
  ],
});
```

#### Content Script Context

Shows in-page toast notifications:

```typescript
import { configureNotificationContext, notify } from '../utils/notifications';

configureNotificationContext({
  isContentScript: true,
});

notify('Content captured!', {
  type: 'success',
  clickUrl: commitUrl,
  linkLabel: 'View on GitHub',
});
```

#### Service Worker Context

Tries Chrome notifications API (no DOM available):

```typescript
import { configureNotificationContext, notify } from '../utils/notifications';

configureNotificationContext({
  isServiceWorker: true,
});

notify('Operation failed', {
  type: 'error',
  message: 'Please try again',
});
```

### Advanced Options

```typescript
interface INotificationOptions {
  // Common options
  type?: 'success' | 'error' | 'info' | 'warning' | 'progress';
  message?: string; // Secondary message/details
  duration?: number; // Auto-hide duration (0 = persistent)
  dismissible?: boolean;

  // Advanced options (popup status UI)
  showProgress?: boolean;
  progressValue?: number; // 0-100
  actions?: INotificationAction[];
  details?: string[];

  // Toast-specific options
  clickUrl?: string;
  linkLabel?: string;
  openInNewTab?: boolean;
  onClick?: () => void;

  // Environment hints
  preferPopupStatus?: boolean; // Force popup status UI if available
  preferToast?: boolean; // Force toast if available
}
```

### Progress Notifications

For long-running operations in the popup:

```typescript
// Start
notify('Initializing...', {
  type: 'progress',
  showProgress: true,
  progressValue: 10,
});

// Update
notify('Processing content...', {
  type: 'progress',
  showProgress: true,
  progressValue: 50,
  message: 'Extracting and converting to markdown',
});

// Complete
notify('Capture complete!', {
  type: 'success',
  message: 'Saved to repository',
  actions: [
    {
      label: 'View on GitHub',
      action: () => window.open(url, '_blank'),
      primary: true,
    },
  ],
});
```

### With Actions (Popup Only)

```typescript
notify('Capture failed', {
  type: 'error',
  message: 'Content script not ready. Try refreshing the page.',
  actions: [
    {
      label: 'Refresh Page',
      action: () => chrome.tabs.reload(tabId),
      primary: true,
    },
    {
      label: 'Try Again',
      action: () => this.retry(),
    },
    {
      label: 'Open Settings',
      action: () => chrome.runtime.openOptionsPage(),
    },
  ],
});
```

## Migration Guide

### From popup.ts `updateCaptureStatus()`

**Before:**

```typescript
this.updateCaptureStatus(
  'Capture Complete',
  'Document saved successfully',
  'success',
  {
    autoHide: 5000,
    actions: [{ label: 'View', action: () => this.open() }],
  }
);
```

**After:**

```typescript
notify('Capture Complete', {
  type: 'success',
  message: 'Document saved successfully',
  duration: 5000,
  actions: [{ label: 'View', action: () => this.open() }],
});
```

### From toast.ts `showToast()`

**Before:**

```typescript
showToast('Saved successfully', {
  type: 'success',
  clickUrl: commitUrl,
  linkLabel: 'View Commit',
});
```

**After:**

```typescript
notify('Saved successfully', {
  type: 'success',
  clickUrl: commitUrl,
  linkLabel: 'View Commit',
});
```

### From service worker notifications

**Before:**

```typescript
chrome.notifications.create({
  type: 'basic',
  title: 'PrismWeave',
  message: 'Operation complete',
});
```

**After:**

```typescript
notify('Operation complete', {
  type: 'success',
});
```

## Best Practices

### ✅ DO

- **Use `notify()` for all notifications** - it automatically adapts
- **Configure context once** in component initialization
- **Use `notification.success()` etc.** for cleaner code
- **Provide clickable URLs** when available (GitHub commits, etc.)
- **Use progress notifications** for long operations in popup
- **Include helpful actions** for error states

### ❌ DON'T

- **Don't call `showToast()` directly** - use `notify()` instead
- **Don't call `chrome.notifications.create()` directly** - use `notify()`
- **Don't use `updateCaptureStatus()` outside popup** - it's popup-specific
- **Don't forget to configure context** in new components

## Examples

### Content Capture Success

```typescript
const commitUrl = result.data?.saveResult?.url;

notify('Content captured successfully!', {
  type: 'success',
  message: `Saved as: ${filename}`,
  clickUrl: commitUrl,
  linkLabel: 'View Commit',
  duration: 5000,
});
```

### Error with Retry

```typescript
notify('Capture failed', {
  type: 'error',
  message: error.message,
  actions: [
    {
      label: 'Try Again',
      action: () => this.captureContent(),
      primary: true,
    },
    {
      label: 'Check Settings',
      action: () => chrome.runtime.openOptionsPage(),
    },
  ],
});
```

### Progress Updates

```typescript
// Initial
notify('Starting capture...', {
  type: 'progress',
  showProgress: true,
  progressValue: 0,
});

// Mid-way
notify('Processing content...', {
  type: 'progress',
  showProgress: true,
  progressValue: 50,
  message: 'Converting to markdown',
});

// Complete
notify('Capture complete!', {
  type: 'success',
  clickUrl: githubUrl,
});
```

## Testing

### Mock Configuration

```typescript
import { configureNotificationContext } from '../utils/notifications';

beforeEach(() => {
  configureNotificationContext({
    isPopup: true,
    popupStatusHandler: jest.fn(),
  });
});
```

### Verify Calls

```typescript
import { notify } from '../utils/notifications';

jest.mock('../utils/notify');

test('shows success notification', () => {
  myFunction();

  expect(notify).toHaveBeenCalledWith(
    'Operation successful',
    expect.objectContaining({
      type: 'success',
    })
  );
});
```

## Architecture Benefits

1. **Single Source of Truth** - One API for all notifications
2. **Automatic Fallback** - Gracefully degrades based on environment
3. **Consistent UX** - Same notification style across extension
4. **Type Safety** - Full TypeScript support
5. **Testable** - Easy to mock and verify
6. **Maintainable** - Changes in one place affect entire extension
7. **Context-Aware** - Automatically uses best display method
8. **Flexible** - Supports simple toasts to complex status UI

## Future Enhancements

Potential improvements to the unified notification system:

- [ ] Notification queuing for rapid-fire notifications
- [ ] Notification history/log
- [ ] Customizable notification positioning
- [ ] Sound effects (optional)
- [ ] Notification grouping/stacking
- [ ] Multi-language support
- [ ] Accessibility improvements (screen reader optimization)

---

**Remember:** Always use `notify()` - it's the single API for all your
notification needs!
