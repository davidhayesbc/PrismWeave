# PrismWeave Extension Debugging Guide

## Quick Setup

1. Build the extension:
   ```bash
   cd browser-extension
   npm run build
   ```

2. Load the extension in Chrome/Edge:
   - Go to `chrome://extensions/` or `edge://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `browser-extension/dist` folder

## Debugging the Popup

1. **Right-click the extension icon** → **Inspect popup**
2. **Open the Console tab** in DevTools
3. **Click any button** and watch the console output

### Expected Console Output:
```
🔧 PrismWeave Logging Configuration Loaded
[HH:MM:SS.mmm] [Popup] [INFO] PrismWeavePopup constructor called
[HH:MM:SS.mmm] [Popup] [DEBUG] Getting current tab
[HH:MM:SS.mmm] [Popup] [DEBUG] Current tab obtained: {id: 123, url: "..."}
[HH:MM:SS.mmm] [Popup] [DEBUG] Setting up event listeners
[HH:MM:SS.mmm] [Popup] [DEBUG] Setting up capture button listener
[HH:MM:SS.mmm] [Popup] [INFO] Event listeners setup completed
```

When you click the **Capture** button:
```
[HH:MM:SS.mmm] [Popup] [INFO] Capture button clicked
[HH:MM:SS.mmm] [Popup] [INFO] Starting page capture process
[HH:MM:SS.mmm] [Popup] [DEBUG] Sending CAPTURE_PAGE message to background script
```

## Debugging the Background Script

1. **Go to** `chrome://extensions/`
2. **Find PrismWeave** and click **"Inspect views: background"**
3. **Open the Console tab**

### Expected Console Output:
```
🔧 PrismWeave Logging Configuration Loaded
[HH:MM:SS.mmm] [Background] [INFO] 🚀 PrismWeave Background Service Worker starting up
[HH:MM:SS.mmm] [Background] [INFO] PrismWeaveBackground constructor called
[HH:MM:SS.mmm] [Background] [DEBUG] Initializing core components
```

When popup sends a message:
```
[HH:MM:SS.mmm] [Background] [DEBUG] Message received from: popup
[HH:MM:SS.mmm] [Background] [INFO] Processing CAPTURE_PAGE request
```

## Logging Controls

### Enable/Disable Logging
In any console (popup or background):
```javascript
// Disable all logging
window.PRISMWEAVE_LOG_CONFIG.enabled = false;

// Enable logging
window.PRISMWEAVE_LOG_CONFIG.enabled = true;
```

### Change Log Level
```javascript
// Show only errors and warnings
window.PRISMWEAVE_LOG_CONFIG.level = 1;

// Show everything (very verbose)
window.PRISMWEAVE_LOG_CONFIG.level = 4;

// Default level (errors, warnings, info, debug)
window.PRISMWEAVE_LOG_CONFIG.level = 3;
```

### Disable Specific Components
```javascript
// Disable popup logging only
window.PRISMWEAVE_LOG_CONFIG.components.Popup.enabled = false;

// Disable background logging only
window.PRISMWEAVE_LOG_CONFIG.components.Background.enabled = false;
```

## Common Issues to Look For

### 1. **Buttons Not Working**
- Check if event listeners are being set up
- Look for "Setting up capture button listener" messages
- Check for DOM element errors like "Capture button not found in DOM"

### 2. **Background Script Not Responding**
- Check if background script starts up properly
- Look for "🚀 PrismWeave Background Service Worker starting up"
- Check for import errors or missing dependencies

### 3. **Message Passing Issues**
- Look for "Sending CAPTURE_PAGE message" in popup console
- Look for "Message received from: popup" in background console
- Check for chrome.runtime errors

## Log File Locations

Edit these files to permanently change logging behavior:
- `src/utils/log-config.js` - Main logging configuration
- `src/utils/logger.js` - Logger implementation

## Quick Test Commands

Run these in the popup console to test functionality:

```javascript
// Test if popup can send messages
chrome.runtime.sendMessage({action: 'GET_SETTINGS'}, response => {
  console.log('Settings response:', response);
});

// Test if DOM elements exist
console.log('Capture button:', document.getElementById('capture-btn'));
console.log('Highlight button:', document.getElementById('highlight-btn'));
```
