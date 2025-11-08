# Notification System Architecture

## Overview

The PrismWeave notification system has been refactored to enforce clean
architectural boundaries with a single public API and internal implementation
files.

## Architecture Goals

1. **Single Public API**: Only `src/utils/notifications/index.ts` should be
   imported by application code
2. **Internal Implementation**: `toast-internal.ts` is an implementation detail
3. **Clear Boundaries**: Prevent direct access to internal notification
   mechanisms
4. **Environment Detection**: Automatic selection of best notification method

## Directory Structure

```
src/utils/notifications/
├── index.ts              # PUBLIC API - Unified notification interface
└── toast-internal.ts     # Internal toast implementation
```

### Files Moved

- `src/utils/notify.ts` → `src/utils/notifications/index.ts`
- `src/utils/toast.ts` → `src/utils/notifications/toast-internal.ts`

## Import Rules

### ✅ Correct Usage

```typescript
// Application code - use unified API
import {
  notify,
  notification,
  configureNotificationContext,
} from '../utils/notifications';

// Show notifications
notification.success('Operation completed');
notification.error('Something went wrong');
notify('Custom notification', { type: 'info' });
```

### ❌ Incorrect Usage

```typescript
// NEVER import toast-internal directly in application code
import { showToast } from '../utils/notifications/toast-internal'; // ❌ WRONG

// NEVER use old paths
import { notify } from '../utils/notify'; // ❌ File doesn't exist
import { showToast } from '../utils/toast'; // ❌ File doesn't exist
```

### 🔧 Special Case: Injectable/Bookmarklet Code

Injectable code runs in isolated page contexts and may need direct toast access:

```typescript
// Injectable code CAN import toast-internal directly
import { showToast } from '../utils/notifications/toast-internal';

// This is allowed because injectables run in page context, not extension context
showToast('Content extracted', { type: 'success' });
```

## Updated Files

### Application Code Updated

All application code now imports from `notifications/index.ts`:

- ✅ `src/popup/popup.ts` - Updated
- ✅ `src/background/service-worker.ts` - Updated
- ✅ `src/options/options.ts` - Updated (migrated from `showToast()` to
  `notification.success/error/info()`)
- ✅ `src/content/content-script.ts` - Updated

### Injectable Code Updated

Injectable code imports `toast-internal.ts` directly:

- ✅ `src/injectable/prismweave-bundle.ts` - Updated to use `toast-internal.ts`
- ✅ `src/injectable/content-extractor-injectable.ts` - Updated to use
  `toast-internal.ts`

### Tests Updated

- ✅ `src/__tests__/utils/toast.test.ts` - Updated to mock
  `notifications/toast-internal`
- ✅ `src/__tests__/options/options.test.ts` - Updated to mock
  `notifications/index.ts` and test `notification.success/error/info()`

### Files Removed

- ❌ `src/utils/notify.ts` - Moved to `notifications/index.ts`
- ❌ `src/utils/toast.ts` - Moved to `notifications/toast-internal.ts`

## API Surface

### Public API (`notifications/index.ts`)

```typescript
// Main notification function
export function notify(title: string, options?: INotifyOptions): void;

// Convenience methods
export const notification = {
  success(title: string, options?: INotifyOptions): void,
  error(title: string, options?: INotifyOptions): void,
  info(title: string, options?: INotifyOptions): void,
  warning(title: string, options?: INotifyOptions): void,
  progress(title: string, options?: INotifyProgressOptions): void,
};

// Environment configuration
export function configureNotificationContext(config: INotificationContext): void;
```

### Internal API (`notifications/toast-internal.ts`)

**DO NOT USE** except in injectable/bookmarklet code:

```typescript
export function showToast(message: string, options?: IToastOptions): void;
export type ToastType = 'success' | 'error' | 'info';
```

## Fallback Strategy

The unified API automatically selects the best notification method:

1. **Popup Status UI** - If running in popup with status handler configured
2. **In-Page Toast** - If DOM is available (content scripts, options page)
3. **Chrome Notifications API** - If in service worker or DOM unavailable
4. **Console Logging** - Fallback for all other cases

## Migration Guide

### From `showToast()`

**Before:**

```typescript
import { showToast } from '../utils/toast';

showToast('Settings saved', { type: 'success', duration: 5000 });
showToast('Error occurred', { type: 'error' });
```

**After:**

```typescript
import { notification } from '../utils/notifications';

notification.success('Settings saved', { duration: 5000, dismissible: true });
notification.error('Error occurred');
```

### From old `notify.ts`

**Before:**

```typescript
import { notify } from '../utils/notify';

notify('Operation complete');
```

**After:**

```typescript
import { notify } from '../utils/notifications';

notify('Operation complete');
```

## Test Coverage

All 235 tests passing ✅

### Test Changes Summary

- Toast tests updated to mock `notifications/toast-internal`
- Options tests updated to mock `notifications/index` with
  `notification.success/error/info()`
- Service worker tests unchanged (already using unified API)
- Popup tests unchanged (already using unified API)

## Benefits

1. **Clear API Boundaries**: Single import path for all notification needs
2. **Prevents Misuse**: Internal implementation hidden from application code
3. **Better Testing**: Easier to mock single unified API
4. **Consistent UX**: All code uses same notification system
5. **Environment Agnostic**: Automatic fallback selection

## Documentation

- **User Guide**: `src/utils/NOTIFICATION_GUIDE.md` - Comprehensive usage
  examples
- **Architecture**: This document - System architecture and migration guide

---

**Last Updated**: January 2025  
**All Tests**: 235 passing ✅
