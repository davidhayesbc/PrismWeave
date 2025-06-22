# Testing the Content Script Communication Fix

## Summary of Changes Made

I've fixed the content script communication error that was causing:

```
[SW-ERROR] Error in capture page: Error: Content script communication failed: Could not establish connection. Receiving end does not exist.
```

## What Was Fixed

### 1. **Robust Content Script Injection**

- Added `ensureContentScriptInjected()` function that checks if content script
  is active before attempting communication
- If content script isn't responding, it attempts to inject it dynamically using
  `chrome.scripting.executeScript`
- Added proper validation for special pages (chrome://, extension pages) where
  content scripts can't be injected

### 2. **Multi-Level Fallback Strategy**

The service worker now tries multiple approaches in order:

1. **Primary**: Use existing content script via message passing
2. **Fallback 1**: Direct content extraction using
   `chrome.scripting.executeScript`
3. **Fallback 2**: Basic page information extraction (title, URL only)

### 3. **Enhanced Content Script**

- Added `PING` message handler to check if content script is active
- Added `EXTRACT_CONTENT` message handler for service worker communication
- Improved error handling and extraction fallbacks

### 4. **Better Error Handling**

- More descriptive error messages
- Graceful degradation when content extraction fails
- Proper timeout handling (10 seconds for content extraction)

## Testing Instructions

To test the fix:

1. **Build the extension**: `npm run build`
2. **Load the extension** in Chrome developer mode
3. **Navigate to any webpage** (try different types: news articles, blogs,
   simple pages)
4. **Click the extension icon** and try to capture the page
5. **Check the browser console** (F12) for any errors

## Expected Behavior

- **Success case**: Page content should be extracted and processed without
  communication errors
- **Content script fails**: Should fallback to direct extraction automatically
- **All extraction fails**: Should still capture basic page info (title, URL)
  rather than throwing an error

## Files Modified

- `src/background/service-worker.ts`: Added extraction helpers and fallback
  logic
- `src/content/content-script.ts`: Added PING and EXTRACT_CONTENT message
  handlers

The fix ensures that page capture works reliably even when content scripts fail
to load or communicate properly.
