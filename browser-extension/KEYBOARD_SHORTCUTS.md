# ## Overview

The PrismWeave browser extension now supports keyboard shortcuts for quick page
capture. Press **Alt+S** to instantly capture the current page.

## Supported Shortcuts

| Shortcut | Action       | Description                                                            |
| -------- | ------------ | ---------------------------------------------------------------------- | ------------------------------------- |
| `Alt+S`  | Capture Page | Captures the current web page as markdown and saves to your repository | rtcuts - PrismWeave Browser Extension |

## Overview

The PrismWeave browser extension now supports keyboard shortcuts for quick page
capture. Press **Ctrl+Alt+S** (or **Cmd+Alt+S** on Mac) to instantly capture the
current page.

## Supported Shortcuts

| Shortcut                     | Action       | Description                                                            |
| ---------------------------- | ------------ | ---------------------------------------------------------------------- |
| `Ctrl+Alt+S` (Windows/Linux) | Capture Page | Captures the current web page as markdown and saves to your repository |
| `Cmd+Alt+S` (Mac)            | Capture Page | Captures the current web page as markdown and saves to your repository |

## How It Works

1. **Keyboard Detection**: Content script detects keyboard shortcuts on all web
   pages
2. **Service Worker Integration**: Commands are handled by the service worker
3. **Page Capture**: Uses the same capture logic as the popup button
4. **User Feedback**: Shows success/error notifications directly on the page

## Implementation Details

### Components Added

1. **Manifest Commands** (`manifest.json`)

   - Defines the `capture-page` command with keyboard bindings
   - Supports both Windows/Linux (`Ctrl+Alt+S`) and Mac (`Cmd+Alt+S`)

2. **Content Script** (`src/content/content-script.ts`)

   - Runs on all web pages to handle keyboard events
   - Detects Ctrl+Alt+S (or Cmd+Alt+S) combinations
   - Shows toast notifications for user feedback
   - Communicates with service worker for page capture

3. **Service Worker Handler** (`src/background/service-worker.ts`)
   - Listens for `chrome.commands.onCommand` events
   - Handles `capture-page` command from keyboard shortcuts
   - Uses existing capture service for consistent behavior
   - Provides error handling and user notifications

### Technical Features

- **Cross-Platform**: Works on Windows, Linux, and Mac
- **Input Field Detection**: Skips capture when user is typing in forms
- **Error Handling**: Shows appropriate error messages if capture fails
- **Settings Integration**: Respects extension settings and GitHub configuration
- **Non-Intrusive**: Toast notifications fade away automatically

## Installation & Testing

### 1. Build the Extension

```bash
cd browser-extension
npm run build
```

### 2. Load in Chrome/Edge

1. Open Chrome/Edge and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the `dist` folder
4. The extension should now be loaded with keyboard shortcuts enabled

### 3. Test Keyboard Shortcuts

1. **Configure Extension**:

   - Click the extension icon and go to Settings
   - Add your GitHub token and repository
   - Save settings

2. **Test Shortcut**:

   - Navigate to any web page (e.g., a news article)
   - Press `Ctrl+Alt+S` (or `Cmd+Alt+S` on Mac)
   - You should see a "Page captured successfully!" notification
   - Check your repository for the new markdown file

3. **Verify in Chrome Settings**:
   - Go to `chrome://extensions/shortcuts`
   - You should see "PrismWeave" with the "Capture current page" command
   - The shortcut should show as `Ctrl+Alt+S`

## Troubleshooting

### Shortcut Not Working

1. **Check Extension Permissions**:

   - Ensure the extension has `activeTab` and `scripting` permissions
   - Make sure content scripts are loading on the page

2. **Verify Settings**:

   - Open extension popup and check that GitHub settings are configured
   - Test capture via the popup button first

3. **Check Browser Shortcuts**:
   - Go to `chrome://extensions/shortcuts`
   - Ensure no other extension is using `Ctrl+Shift+S`
   - You can customize the shortcut if needed

### Input Field Detection

- Shortcuts are automatically disabled when typing in:
  - Text inputs (`<input type="text">`)
  - Textareas (`<textarea>`)
  - Content-editable elements
  - Any focused input field

### Error Messages

| Error                             | Likely Cause                | Solution                               |
| --------------------------------- | --------------------------- | -------------------------------------- |
| "No active tab found"             | Extension permissions issue | Reload the page and try again          |
| "Capture service not initialized" | Extension startup issue     | Reload the extension                   |
| "Capture failed: [details]"       | GitHub/network issue        | Check settings and internet connection |

## Development Notes

### File Structure

```
browser-extension/
├── manifest.json                    # Commands definition
├── src/
│   ├── content/
│   │   └── content-script.ts       # Keyboard detection
│   ├── background/
│   │   └── service-worker.ts       # Command handling
│   └── ...
└── dist/                           # Built extension
    ├── content/
    │   └── content-script.js
    └── ...
```

### Build Process

The content script is automatically included in both production and development
builds via `scripts/build-simple.js`:

- **Production**: `npm run build` - Minified, no source maps
- **Development**: `npm run build -- --watch` - Watch mode with source maps

### Testing

- Unit tests include mocks for `chrome.commands` API
- Service worker tests verify command handling logic
- Content script functionality can be tested manually

## Future Enhancements

1. **Customizable Shortcuts**: Allow users to customize keyboard shortcuts
2. **Multiple Actions**: Add shortcuts for different capture modes (selection,
   full page, etc.)
3. **Visual Feedback**: Enhanced toast notifications or capture progress
   indicators
4. **Conflict Detection**: Warn users about shortcut conflicts with other
   extensions
