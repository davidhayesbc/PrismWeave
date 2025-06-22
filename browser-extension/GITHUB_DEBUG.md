# PrismWeave GitHub Commit Debugging Guide

## Issue

Documents are not being saved to the GitHub repository despite having the
capture functionality working.

## Debugging Steps

### Step 1: Verify Extension is Built and Loaded

1. Run `npm run build` in the browser-extension directory
2. Load the extension in Chrome (chrome://extensions/)
3. Ensure the extension is enabled

### Step 2: Check Settings Configuration

1. Open the extension popup
2. Go to Settings tab
3. Verify the following are configured:
   - **GitHub Token**: Should start with `ghp_` or `github_pat_`
   - **GitHub Repository**: Should be in format `username/repository`
   - **Auto Commit**: Should be enabled (checked)

### Step 3: Test GitHub Connection

1. In the popup, go to Settings tab
2. Click "Test Connection" button
3. Check the result - should show successful connection

### Step 4: Check Browser Console for Errors

1. Open Chrome Developer Tools (F12)
2. Go to Console tab
3. Look for any red error messages
4. Particularly look for messages starting with `[SW-ERROR]` or `[SW-INFO]`

### Step 5: Check Service Worker Console

1. Go to `chrome://extensions/`
2. Find PrismWeave extension
3. Click "Service worker" link
4. This opens the service worker console
5. Try capturing a page and watch for log messages

### Step 6: Manual Debug Test

1. Open the file `debug-test.html` in the browser extension folder
2. This provides buttons to test each component:
   - Test Service Worker communication
   - Check current settings
   - Update settings
   - Test GitHub connection
   - Test page capture

## Expected Log Messages

When capture works correctly, you should see:

```
[SW-INFO] Checking GitHub commit conditions: {autoCommit: true, hasGithubToken: true, hasGithubRepo: true, ...}
[SW-INFO] All conditions met, starting GitHub commit process
[SW-INFO] Starting GitHub commit process: {repo: "username/repo", filePath: "documents/...", ...}
[SW-DEBUG] Parsed repository: {owner: "username", repoName: "repo"}
[SW-DEBUG] Checking if file already exists...
[SW-DEBUG] File does not exist, will create new file. Status: 404
[SW-DEBUG] Commit data prepared: {hasMessage: true, hasContent: true, branch: "main", hasSha: false}
[SW-DEBUG] Making GitHub API request to: https://api.github.com/repos/username/repo/contents/documents/...
[SW-DEBUG] GitHub API response status: 201
[SW-INFO] Successfully committed to GitHub: https://github.com/username/repo/blob/main/documents/...
```

## Common Issues and Solutions

### 1. Settings Not Saved

**Symptom**: GitHub token/repo appear empty even after setting them
**Solution**: Check Chrome storage permissions, try resetting settings

### 2. GitHub Token Invalid

**Symptom**: "GitHub API error: 401" or "Invalid GitHub token" **Solution**:

- Generate a new Personal Access Token
- Ensure it has `repo` or `contents` permissions
- Check token hasn't expired

### 3. Repository Not Found

**Symptom**: "GitHub API error: 404" or "Repository not found" **Solution**:

- Verify repository name format: `username/repository`
- Check repository exists and is accessible
- Ensure token has access to the repository

### 4. Auto-Commit Disabled

**Symptom**: Files stored locally but not committed **Solution**: Check
auto-commit setting is enabled

### 5. Permission Issues

**Symptom**: Various errors about access **Solution**: Check GitHub token
permissions include repository access

## Testing Commands

```bash
# Build the extension
npm run build

# Run tests
npm test

# Check for any TypeScript errors
npx tsc --noEmit
```

## Quick Test Script

Copy this into the browser console on any webpage to test capture:

```javascript
chrome.runtime.sendMessage({ type: 'CAPTURE_PAGE' }, response => {
  console.log('Capture result:', response);
});
```

## Manual Repository Check

Visit your GitHub repository at:
`https://github.com/[username]/[repository]/tree/main/documents`

You should see markdown files appear there when capture is successful.
