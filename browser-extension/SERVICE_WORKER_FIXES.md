# Service Worker Compatibility Fixes

## Issue Identified
The enhanced markdown converter was using `window` and `document` objects that are not available in the service worker context, causing runtime errors when the extension loads.

## Root Cause
- Service workers run in a different context than content scripts or popup scripts
- They don't have access to DOM APIs like `document` or `window`
- The enhanced markdown converter had DOM-dependent code that wasn't properly guarded

## Fixes Applied

### 1. Enhanced Context Detection
Updated all DOM-dependent methods to check for both `window` and `document`:

```javascript
// Before (only checked document)
if (typeof document === 'undefined') {
  return this.regexPreprocessHtml(html);
}

// After (checks both window and document)
if (typeof document === 'undefined' || typeof window === 'undefined') {
  return this.regexPreprocessHtml(html);
}
```

### 2. Service Worker Safe DOM Operations
Added proper guards to prevent DOM operations in service worker context:

#### In `preprocessHtml()`:
- Checks context before creating DOM elements
- Falls back to regex-based preprocessing

#### In `enhanceSemanticStructure()`:
- Added early return for service worker context
- Prevents DOM manipulation when not available

#### In `cleanHtml()`:
- Enhanced context detection
- Proper fallback to regex-based cleaning

### 3. Content Extractor Verification
Confirmed that ContentExtractor usage is correct:
- Only used in content script context via `chrome.scripting.executeScript`
- Not instantiated directly in service worker
- Properly injected into tab context where DOM is available

### 4. Testing Infrastructure
Added comprehensive testing:
- `test-service-worker-compatibility.js` for runtime verification
- Automatic compatibility testing in service worker context
- Manual test functions for debugging

## Files Modified

1. **`src/utils/markdown-converter.js`**:
   - Enhanced `preprocessHtml()` with proper context detection
   - Updated `enhanceSemanticStructure()` with service worker guards
   - Fixed `cleanHtml()` context checking

2. **`src/background/service-worker.js`**:
   - Added test import for verification

3. **New Files**:
   - `src/utils/test-service-worker-compatibility.js` - Compatibility testing

## Technical Details

### Context Detection Strategy
```javascript
const isServiceWorker = typeof window === 'undefined' && typeof document === 'undefined';
const isBrowserContext = typeof window !== 'undefined' && typeof document !== 'undefined';
```

### Fallback Chain
1. **TurndownService Available**: Use enhanced conversion with DOM preprocessing
2. **Service Worker Context**: Use regex-based preprocessing + enhanced fallback conversion
3. **Error Fallback**: Use basic regex-based conversion

### Performance Impact
- Minimal performance impact in browser contexts
- Improved reliability in service worker context
- Maintains all enhanced features when DOM is available

## Testing Results

The compatibility test verifies:
- ✅ TurndownService library loads correctly
- ✅ MarkdownConverter initializes without errors
- ✅ HTML conversion works in service worker context
- ✅ Proper context detection and fallback usage
- ✅ No DOM API calls in service worker environment

## Benefits

1. **Reliability**: Extension loads without errors in all contexts
2. **Functionality**: Full feature set maintained in appropriate contexts
3. **Performance**: Optimal conversion method used based on available APIs
4. **Maintainability**: Clear separation of DOM-dependent and DOM-independent code
5. **Testing**: Comprehensive verification of compatibility

## Future Considerations

- The architecture now supports adding more service worker-specific optimizations
- Easy to extend with additional context-aware features
- Clear patterns established for handling cross-context compatibility
