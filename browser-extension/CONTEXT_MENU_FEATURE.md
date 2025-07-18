# Context Menu Feature - PrismWeave Browser Extension

## Overview

The PrismWeave browser extension now includes right-click context menu support
for capturing web content directly from links without navigating to them first.

## Features

### Link Capture

- **Right-click any link** → Select "Capture this link with PrismWeave"
- Opens the link in a background tab
- Extracts and processes the content
- Automatically closes the background tab
- Saves content to your configured repository

### Page Capture

- **Right-click anywhere on a page** → Select "Capture this page with
  PrismWeave"
- Captures content from the current page
- Same functionality as the keyboard shortcut (Alt+S)

## How It Works

### Context Menu Creation

```typescript
// Context menus are created when the extension starts up
chrome.contextMenus.create({
  id: 'capture-link',
  title: 'Capture this link with PrismWeave',
  contexts: ['link'],
  documentUrlPatterns: ['<all_urls>'],
});
```

### Link Capture Workflow

1. User right-clicks on a link
2. Context menu shows "Capture this link with PrismWeave"
3. User selects the menu item
4. Extension creates a background tab with the link URL
5. Content extraction runs in the background tab
6. Content is processed and saved to repository
7. Background tab is automatically closed
8. User sees notification with result

### New Message Type

```typescript
MESSAGE_TYPES.CAPTURE_LINK = 'CAPTURE_LINK';
```

## Implementation Details

### Service Worker Changes

- Added `contextMenus` permission to manifest.json
- Created context menu items on extension startup
- Added context menu click handler
- Added `CAPTURE_LINK` message type support
- Enhanced error handling with notifications

### Content Capture Service Changes

- Added `captureLink()` method
- Supports background tab creation and management
- Automatic tab cleanup after capture
- Proper error handling for link capture scenarios

### Notifications

The extension shows notifications for:

- Capture start: "Capturing content from: domain.com"
- Success: "Successfully captured content from domain.com"
- Failure: "Failed to capture link: [error message]"

## Testing

Use the included test file: `test-context-menu.html`

### Test Cases

1. **Link Context Menu**: Right-click on test links
2. **Page Context Menu**: Right-click on page background
3. **Notification Display**: Check for status notifications
4. **Content Storage**: Verify content is saved to repository
5. **Error Handling**: Test with invalid links or no settings

### Expected Behavior

- Context menu appears on right-click
- Background tabs open/close automatically for link capture
- Notifications show capture progress
- Content appears in configured GitHub repository
- Extension handles errors gracefully

## Configuration

No additional configuration required. The context menu feature uses your
existing PrismWeave settings:

- GitHub token and repository
- File organization settings
- Auto-commit preferences

## Troubleshooting

### Context Menu Not Appearing

- Check extension is enabled in Edge
- Verify `contextMenus` permission in manifest
- Try reloading the extension

### Link Capture Fails

- Check extension settings (GitHub token, repository)
- Verify the link URL is accessible
- Check browser console for errors

### No Notifications

- Check browser notification permissions
- Verify notifications are enabled in browser settings

## Browser Compatibility

- **Microsoft Edge**: Full support (Manifest V3)
- **Google Chrome**: Full support (Manifest V3)
- **Other Chromium browsers**: Should work with Manifest V3 support

## Security Considerations

- Background tabs are created with `active: false` to avoid user distraction
- Tabs are automatically closed after content extraction
- Standard content security policies apply
- Link URLs are validated before processing

## Code Structure

```
src/
├── background/
│   └── service-worker.ts      # Context menu creation and handling
├── utils/
│   └── content-capture-service.ts  # Link capture implementation
├── content/
│   └── content-script.ts      # Content extraction support
└── types/
    └── index.ts              # New CAPTURE_LINK message type
```

## API Reference

### New Methods

#### `ContentCaptureService.captureLink()`

```typescript
async captureLink(
  linkUrl: string,
  data?: Record<string, unknown>,
  options: ICaptureServiceOptions = {}
): Promise<ICaptureResult>
```

#### Context Menu Event Handler

```typescript
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  // Handle context menu clicks
});
```

## Future Enhancements

- Bulk link capture (select multiple links)
- Preview mode before capture
- Custom extraction rules per domain
- Batch processing queue
- Link validation and filtering
