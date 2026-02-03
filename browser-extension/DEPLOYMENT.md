# PrismWeave Browser Extension - Deployment Guide

This guide covers how to package and deploy the PrismWeave browser extension
for:

- **Direct distribution from your website**
- **Microsoft Edge Add-ons gallery**
- **Chrome Web Store** (optional)

## Table of Contents

- [Prerequisites](#prerequisites)
- [Building for Production](#building-for-production)
- [Packaging the Extension](#packaging-the-extension)
- [Website Deployment](#website-deployment)
- [Edge Add-ons Submission](#edge-add-ons-submission)
- [Chrome Web Store Submission](#chrome-web-store-submission-optional)
- [Post-Deployment](#post-deployment)
- [Updating the Extension](#updating-the-extension)

---

## Prerequisites

Before deploying, ensure you have:

- [x] Node.js 18+ installed
- [x] Extension tested in both Chrome and Edge
- [x] All tests passing (`npm test`)
- [x] GitHub repository with clean commit history
- [x] Privacy policy prepared (required for store submissions)
- [x] Marketing materials (screenshots, promotional images)
- [x] Microsoft Partner Center account (for Edge Add-ons)
- [x] Chrome Web Store Developer account (for Chrome Web Store, $5 one-time fee)

---

## Building for Production

### 1. Update Version Number

First, update the version in both `package.json` and `manifest.json`:

```bash
# Current version
"version": "1.0.0"

# Update to your release version (e.g., "1.0.1" or "1.1.0")
```

**Semantic Versioning Guidelines:**

- **Major** (1.0.0 → 2.0.0): Breaking changes, major new features
- **Minor** (1.0.0 → 1.1.0): New features, backwards compatible
- **Patch** (1.0.0 → 1.0.1): Bug fixes, minor improvements

### 2. Clean Build

```bash
cd /home/dhayes/Source/PrismWeave/browser-extension

# Clean any previous builds
npm run clean

# Install dependencies (if needed)
npm install

# Run tests to ensure everything works
npm test

# Build for production (minified, no source maps)
npm run build:prod
```

This creates optimized files in `../../dist/browser-extension/`.

### 3. Verify Build Output

Check that the build completed successfully:

```bash
ls -la ../../dist/browser-extension/

# You should see:
# ├── background/
# │   └── service-worker.js
# ├── content/
# │   └── content-script.js
# ├── icons/
# │   ├── icon16.png
# │   ├── icon32.png
# │   ├── icon48.png
# │   └── icon128.png
# ├── popup/
# │   ├── popup.html
# │   ├── popup.js
# │   └── popup.css
# ├── options/
# │   ├── options.html
# │   ├── options.js
# │   └── options.css
# ├── injectable/
# ├── libs/
# ├── styles/
# └── manifest.json
```

---

## Packaging the Extension

### 1. Create ZIP Package

```bash
# Run the packaging script
npm run package
```

This creates `prismweave-extension.zip` in the `browser-extension` folder.

**Manual packaging (alternative):**

```bash
cd ../../dist/browser-extension

# Linux/Mac
zip -r prismweave-extension-v1.0.0.zip ./*

# Windows (PowerShell)
Compress-Archive -Path * -DestinationPath prismweave-extension-v1.0.0.zip
```

### 2. Verify Package Contents

```bash
# Check ZIP contents without extracting
unzip -l prismweave-extension.zip

# Verify package size (should be under 10MB)
ls -lh prismweave-extension.zip
```

**Important checks:**

- ✅ All files are in the ZIP (not nested in a folder)
- ✅ manifest.json is at the root level
- ✅ No development files (.ts, .map files if production build)
- ✅ No node_modules or source files
- ✅ Package size is reasonable (typically 1-3MB)

### 3. Test the Package

**Chrome:**

```
1. Open chrome://extensions/
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select ../../dist/browser-extension directory
5. Test all functionality
```

**Edge:**

```
1. Open edge://extensions/
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select ../../dist/browser-extension directory
5. Test all functionality
```

---

## Website Deployment

### Option 1: GitHub Releases (Recommended)

This is the easiest way to distribute your extension from your website.

#### 1. Create a GitHub Release

```bash
# Tag the release
cd /home/dhayes/Source/PrismWeave
git tag -a v1.0.0 -m "PrismWeave Browser Extension v1.0.0"
git push origin v1.0.0

# Create release on GitHub
# Go to: https://github.com/davidhayesbc/PrismWeave/releases/new
```

#### 2. Upload Extension Package

1. **Create Release on GitHub:**
   - Tag version: `v1.0.0`
   - Release title: "PrismWeave Browser Extension v1.0.0"
   - Description: Include changelog, features, and installation instructions
   - Attach the `prismweave-extension.zip` file

2. **Direct Download Link:**
   ```
   https://github.com/davidhayesbc/PrismWeave/releases/download/v1.0.0/prismweave-extension.zip
   ```

#### 3. Add Download Section to Your Website

Create a download page on your website (e.g., `https://yoursite.com/download`):

```html
<!-- Example download page snippet -->
<section class="extension-download">
  <h2>Download PrismWeave Browser Extension</h2>

  <div class="download-options">
    <a
      href="https://github.com/davidhayesbc/PrismWeave/releases/download/v1.0.0/prismweave-extension.zip"
      class="download-button"
    >
      Download for Chrome/Edge (v1.0.0)
    </a>

    <!-- Add Edge Add-ons link when published -->
    <a href="#" class="store-button edge-button">
      Get it from Microsoft Edge Add-ons
    </a>

    <!-- Add Chrome Web Store link when published -->
    <a href="#" class="store-button chrome-button">
      Get it from Chrome Web Store
    </a>
  </div>

  <h3>Installation Instructions</h3>
  <ol>
    <li>Download the extension ZIP file</li>
    <li>Extract the ZIP file to a permanent location</li>
    <li>Open Chrome/Edge and navigate to extensions page</li>
    <li>Enable "Developer mode"</li>
    <li>Click "Load unpacked" and select the extracted folder</li>
    <li>Configure GitHub settings in the extension options</li>
  </ol>

  <h3>System Requirements</h3>
  <ul>
    <li>Chrome 88+ or Edge 88+ (Chromium-based)</li>
    <li>GitHub account with personal access token</li>
    <li>Dedicated GitHub repository for documents</li>
  </ul>
</section>
```

### Option 2: Self-Hosted on Your Website

If you want to host the ZIP directly on your website:

```bash
# Upload to your web server
scp browser-extension/prismweave-extension.zip user@yoursite.com:/var/www/downloads/

# Or use your web hosting file manager
```

**Direct download URL:**

```
https://yoursite.com/downloads/prismweave-extension.zip
```

**Important:** Ensure your web server serves the ZIP with correct MIME type:

```
Content-Type: application/zip
```

---

## Edge Add-ons Submission

### Step 1: Prepare Materials

Before submitting to Microsoft Edge Add-ons, prepare:

#### 1. **Privacy Policy** (Required)

Create a privacy policy page on your website. Example outline:

```markdown
# PrismWeave Privacy Policy

## Data Collection

PrismWeave does not collect any personal data. All processing happens locally.

## Data Storage

- GitHub tokens are stored securely in browser storage
- No data is transmitted to third-party servers
- Content is sent directly to your GitHub repository

## Third-Party Services

- GitHub API for repository synchronization
- No analytics or tracking services

## Contact

For privacy concerns: your-email@example.com

Last Updated: [Current Date]
```

Host at: `https://yoursite.com/privacy-policy`

#### 2. **Screenshots** (Required)

Capture high-quality screenshots (1280x800 or 640x400):

```bash
# Recommended screenshots:
1. Extension popup with capture interface
2. Options/settings page
3. Content extraction in action
4. Successfully captured document in GitHub
5. GitHub repository view with captured documents
```

Save as PNG format, ensure good visual quality.

#### 3. **Promotional Images** (Optional but Recommended)

- **Small tile**: 440x280 pixels
- **Large tile**: 920x680 pixels
- **Marquee**: 1400x560 pixels

These appear in the Edge Add-ons store.

#### 4. **Description and Details**

Prepare:

- **Short description** (132 characters max)
- **Detailed description** (10,000 characters max)
- **Feature list**
- **Release notes**

### Step 2: Create Microsoft Partner Center Account

1. **Go to:** https://partner.microsoft.com/dashboard/microsoftedge/overview
2. **Sign in** with Microsoft account
3. **Enroll** in the Microsoft Edge program (free, no fee)
4. **Complete** developer profile

### Step 3: Submit Extension

#### 1. Start New Submission

1. Click **"New extension"** in Partner Center
2. Choose **manual upload** (we'll use the ZIP file)

#### 2. Fill in Product Info

**Product name:**

```
PrismWeave
```

**Category:**

```
Productivity
```

**Short description:**

```
Capture web pages as markdown and sync to GitHub. Smart content extraction, Git integration, and document management.
```

**Detailed description:**

```
PrismWeave is a powerful browser extension that captures web content, converts it to clean markdown, and syncs it to your GitHub repository.

Features:
• Smart content extraction with ad removal
• Clean markdown conversion
• Direct GitHub integration
• Automatic metadata generation
• One-click capture with keyboard shortcut
• Context menu integration for link capture
• Bookmarklet support for universal browser compatibility

Perfect for:
- Knowledge management
- Research documentation
- Content archiving
- Personal wiki creation
- Cross-device document sync

How it works:
1. Click the extension icon on any web page
2. PrismWeave extracts the main content
3. Converts to formatted markdown
4. Commits directly to your GitHub repository
5. Access your documents across all devices

Requirements:
- GitHub account with personal access token
- Dedicated GitHub repository
- Chrome 88+ or Edge 88+

Privacy:
All processing happens locally. No data collection or third-party tracking.
```

#### 3. Upload Extension Package

1. **Upload** the `prismweave-extension.zip` file
2. **Automatic validation** will run
3. **Fix any errors** reported

Common validation issues:

- Missing required icons
- Invalid manifest permissions
- CSP policy violations

#### 4. Add Store Listing Assets

1. **Upload screenshots** (at least 1 required, up to 10 allowed)
2. **Add promotional images** (optional)
3. **Set language** (English - en)

#### 5. Set Availability and Pricing

- **Markets:** Select all markets or specific regions
- **Pricing:** Free (most extensions are free)
- **Visibility:** Public

#### 6. Add Properties

**Privacy policy URL:**

```
https://yoursite.com/privacy-policy
```

**Support URL:**

```
https://github.com/davidhayesbc/PrismWeave/issues
```

**Homepage URL:**

```
https://yoursite.com
```

**Contact email:**

```
your-email@example.com
```

#### 7. Certification Notes

Add notes for reviewers:

```
Test Account (if needed):
- GitHub test repository: [provide if needed]
- Test token scope: repo access only

Testing Instructions:
1. Install extension
2. Open options page
3. Configure GitHub token and repository
4. Visit any article page (e.g., https://example.com/article)
5. Click extension icon to capture
6. Verify commit in GitHub repository

Note: GitHub token is user-provided and NOT included in extension.
```

#### 8. Submit for Review

1. **Review** all information
2. Click **"Submit for review"**
3. **Wait for certification** (typically 1-3 business days)

### Step 4: Monitor Submission Status

Check status at: https://partner.microsoft.com/dashboard/microsoftedge/overview

**Possible statuses:**

- ✅ **In certification**: Being reviewed
- ✅ **Published**: Live in Edge Add-ons
- ❌ **Failed certification**: Needs fixes (check feedback)

### Step 5: Respond to Certification Issues

If certification fails:

1. **Read feedback** carefully
2. **Fix reported issues**
3. **Update version number** (e.g., 1.0.0 → 1.0.1)
4. **Rebuild and repackage**
5. **Resubmit**

---

## Chrome Web Store Submission (Optional)

### Step 1: Create Developer Account

1. **Go to:** https://chrome.google.com/webstore/devconsole
2. **Pay** $5 one-time registration fee
3. **Verify** developer identity

### Step 2: Create New Item

1. Click **"New Item"**
2. **Upload** `prismweave-extension.zip`
3. Click **"Upload"**

### Step 3: Fill Store Listing

Similar to Edge Add-ons:

**Store listing:**

- Detailed description
- Screenshots (1280x800)
- Small tile (440x280)
- Promotional images

**Privacy practices:**

```
Data usage:
- Extension does not collect user data
- GitHub tokens stored locally only
```

**Category:**

```
Productivity
```

**Language:**

```
English
```

### Step 4: Submit for Review

1. **Review** all information
2. **Submit** for review
3. **Wait** for approval (1-3 business days)

---

## Post-Deployment

### 1. Update Website Links

Once published in Edge Add-ons or Chrome Web Store, update your website:

**Edge Add-ons URL format:**

```
https://microsoftedge.microsoft.com/addons/detail/[extension-id]
```

**Chrome Web Store URL format:**

```
https://chrome.google.com/webstore/detail/[extension-id]
```

Update your website's download page with the official store links.

### 2. Update README Badges

Update `browser-extension/README.md`:

```markdown
[![Edge Add-ons](https://img.shields.io/badge/edge--addons-available-blue.svg)](https://microsoftedge.microsoft.com/addons/detail/[your-extension-id])
[![Chrome Web Store](https://img.shields.io/badge/chrome-web%20store-brightgreen.svg)](https://chrome.google.com/webstore/detail/[your-extension-id])
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/davidhayesbc/PrismWeave/releases)
```

### 3. Announce Release

- **GitHub Discussions:** Create announcement thread
- **Social Media:** Share release with feature highlights
- **Blog Post:** Write about the extension capabilities
- **Email Newsletter:** Notify existing users

### 4. Monitor Analytics

**Edge Add-ons:**

- View installs, ratings, reviews in Partner Center
- Monitor crash reports and errors

**Chrome Web Store:**

- View stats in Chrome Web Store Developer Dashboard
- Track user reviews and ratings

### 5. Set Up Support Channels

- **GitHub Issues:** For bug reports and feature requests
- **Email Support:** For direct user inquiries
- **Documentation:** Maintain comprehensive user guide

---

## Updating the Extension

### For Minor Updates (Bug Fixes)

1. **Fix the issue** in source code
2. **Update version** (e.g., 1.0.0 → 1.0.1)
3. **Run tests**
4. **Build production** (`npm run build:prod`)
5. **Package** (`npm run package`)
6. **Test locally**
7. **Upload to stores** (Edge Add-ons and/or Chrome Web Store)

### For Major Updates (New Features)

1. **Implement features** with tests
2. **Update version** (e.g., 1.0.0 → 1.1.0)
3. **Update documentation**
4. **Test thoroughly**
5. **Create changelog**
6. **Build and package**
7. **Submit to stores** with detailed changelog

### Update Checklist

- [ ] Version incremented in `package.json` and `manifest.json`
- [ ] All tests passing
- [ ] Changelog updated
- [ ] Documentation updated
- [ ] Built with `npm run build:prod`
- [ ] Package created and tested
- [ ] GitHub release created
- [ ] Submitted to Edge Add-ons (if applicable)
- [ ] Submitted to Chrome Web Store (if applicable)
- [ ] Website download links updated
- [ ] Release announced

---

## Troubleshooting Deployment Issues

### Common Edge Add-ons Rejection Reasons

**1. Manifest Issues**

```
Error: Invalid permissions declared
Fix: Review and justify all permissions in manifest.json
```

**2. Content Security Policy**

```
Error: CSP too permissive
Fix: Tighten CSP in manifest, avoid 'unsafe-eval'
```

**3. Privacy Policy**

```
Error: Privacy policy URL not accessible
Fix: Ensure privacy policy is publicly accessible
```

**4. Functionality Issues**

```
Error: Extension doesn't work as described
Fix: Provide detailed testing instructions
```

### Build Errors

**TypeScript Errors:**

```bash
npm run type-check
# Fix reported errors
```

**Missing Files:**

```bash
# Ensure all required files are in dist/
ls -la ../../dist/browser-extension/
```

**Size Issues:**

```bash
# Check package size
du -h prismweave-extension.zip

# If too large, check for:
# - Unnecessary files in dist
# - Large images (compress)
# - Bundled test files (exclude)
```

---

## Security Checklist

Before deploying:

- [ ] No hardcoded API keys or tokens
- [ ] Proper CSP headers in manifest
- [ ] Input sanitization in content scripts
- [ ] Secure GitHub token storage
- [ ] HTTPS-only external requests
- [ ] No `eval()` or `new Function()` usage
- [ ] Proper error handling (no sensitive data in logs)
- [ ] Updated dependencies (check for vulnerabilities)

---

## Resources

### Official Documentation

- **Edge Add-ons:**
  https://learn.microsoft.com/en-us/microsoft-edge/extensions-chromium/
- **Chrome Web Store:** https://developer.chrome.com/docs/webstore/
- **Manifest V3:** https://developer.chrome.com/docs/extensions/mv3/

### Tools

- **Extension Size Analyzer:** https://www.crx4chrome.com/crx-size/
- **CSP Validator:** https://csp-evaluator.withgoogle.com/
- **Icon Generator:** https://www.icoconverter.com/

### Support

- **GitHub Issues:** https://github.com/davidhayesbc/PrismWeave/issues
- **Edge Add-ons Support:**
  https://developer.microsoft.com/microsoft-edge/extensions/support/
- **Chrome Web Store Support:** https://support.google.com/chrome_webstore/

---

## Next Steps

1. **Complete production build** and testing
2. **Prepare marketing materials** (screenshots, descriptions)
3. **Create privacy policy** page
4. **Submit to Edge Add-ons** for review
5. **(Optional)** Submit to Chrome Web Store
6. **Update website** with download links
7. **Monitor and respond** to user feedback

Good luck with your deployment! 🚀
