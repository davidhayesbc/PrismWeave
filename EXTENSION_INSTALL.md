# PrismWeave Browser Extension Installation Guide

## 🚀 Quick Installation

### Prerequisites
- Chrome, Edge, or Chromium-based browser
- Downloaded PrismWeave extension package

### Step-by-Step Instructions

#### 1. Download the Extension
- Go to [PrismWeave Releases](https://github.com/davidhayesbc/PrismWeave/releases/latest)
- Download `prismweave-extension-vX.X.X.zip`
- Extract the ZIP file to a folder on your computer

#### 2. Enable Developer Mode
- Open your browser and go to the extensions page:
  - Chrome: `chrome://extensions/`
  - Edge: `edge://extensions/`
  - Other Chromium browsers: Look for Extensions in settings
- Toggle **"Developer mode"** ON (usually in the top-right corner)

#### 3. Load the Extension
- Click **"Load unpacked"** button
- Select the extracted extension folder
- The PrismWeave icon should appear in your browser toolbar

#### 4. Configure Your Settings
- Click the PrismWeave icon in your toolbar
- Enter your GitHub personal access token
- Set your target repository (format: `owner/repo`)
- Customize folder structure and other preferences

## ✅ Verification

After installation, you should see:
- PrismWeave icon in your browser toolbar
- Extension listed in your extensions page
- Options accessible via right-click on the icon

## 🔧 Configuration

### GitHub Personal Access Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select these scopes:
   - `repo` (for private repositories) or `public_repo` (for public only)
4. Copy the token and paste it in the extension settings

### Repository Setup
- Format: `username/repository-name`
- Repository must exist and be accessible with your token
- Extension will create folders and files as needed

### Advanced Settings
- **Folder Structure**: Customize how files are organized
- **Filename Template**: Set naming conventions for captured files
- **Content Processing**: Configure markdown conversion options
- **Keyboard Shortcuts**: Set custom hotkeys for quick capture

## 🛠️ Troubleshooting

### Common Issues

#### Extension Won't Load
- **Cause**: Invalid extension package
- **Solution**: Re-download and extract the latest release

#### No Icon in Toolbar
- **Cause**: Extension not properly loaded
- **Solution**: Check extensions page, reload if needed

#### GitHub API Errors
- **Cause**: Invalid token or insufficient permissions
- **Solution**: Generate new token with correct scopes

#### Content Not Captured
- **Cause**: Website restrictions or unusual page structure
- **Solution**: Try refresh, check content settings, or use manual selection

### Getting Help
- [GitHub Issues](https://github.com/davidhayesbc/PrismWeave/issues)
- [Discussions](https://github.com/davidhayesbc/PrismWeave/discussions)
- Check browser console for error messages

## 🔄 Updating

### Manual Update
1. Download the latest release
2. Remove old extension from extensions page
3. Load unpacked new version
4. Reconfigure settings if needed

### Automatic Updates
- Currently not supported (manual updates required)
- Future Chrome Web Store release will enable auto-updates

## ⚡ Quick Tips

- **Keyboard Shortcut**: Set a custom hotkey for instant capture
- **Context Menu**: Right-click on pages for capture options  
- **Batch Processing**: Select multiple elements before capturing
- **Preview Mode**: Review content before saving to repository
- **Offline Mode**: Extension works offline, syncs when connected

## 🔒 Privacy & Security

- Your GitHub token is stored locally in encrypted browser storage
- No data is sent to third-party servers
- Direct API communication with GitHub only
- Open source code available for security review

---

**Need more help?** Visit the [main documentation](https://github.com/davidhayesbc/PrismWeave) or create an [issue](https://github.com/davidhayesbc/PrismWeave/issues).
