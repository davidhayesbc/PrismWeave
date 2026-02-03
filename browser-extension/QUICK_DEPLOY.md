# 🚀 PrismWeave Extension - Quick Deployment Guide

A streamlined guide to get your browser extension deployed quickly.

---

## Prerequisites Checklist

Before you begin:

- [ ] Extension fully tested and working
- [ ] All tests passing (`npm test`)
- [ ] Privacy policy created and hosted
- [ ] 3-5 screenshots captured (1280x800 recommended)
- [ ] GitHub repository ready for releases
- [ ] Microsoft Partner Center account (for Edge, free)
- [ ] Chrome Web Store developer account (for Chrome, $5 one-time)

---

## Step 1: Build Production Package (5 minutes)

### Option A: Automated (Recommended)

```bash
cd /home/dhayes/Source/PrismWeave/browser-extension
npm run deploy
```

This interactive script will:

- ✅ Prompt to bump version
- ✅ Run tests
- ✅ Build production version
- ✅ Create versioned ZIP package
- ✅ Provide next steps

### Option B: Manual

```bash
cd /home/dhayes/Source/PrismWeave/browser-extension

# Update version in package.json and manifest.json
# Then:
npm run clean
npm test
npm run build:prod
npm run package
```

**Result:** `releases/prismweave-extension-v*.zip` ready for deployment

---

## Step 2: Test Package Locally (10 minutes)

### In Chrome

```
1. Open chrome://extensions/
2. Enable "Developer mode" (top-right toggle)
3. Click "Load unpacked"
4. Select: /home/dhayes/Source/PrismWeave/dist/browser-extension
5. Test all features:
   - Popup opens
   - Settings save
   - Content capture works
   - GitHub integration works
```

### In Edge

```
1. Open edge://extensions/
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select: /home/dhayes/Source/PrismWeave/dist/browser-extension
5. Verify same functionality as Chrome
```

**Critical:** Test the exact build you'll submit, not the source code in
developer mode.

---

## Step 3: Website Distribution (15 minutes)

### Create GitHub Release

```bash
cd /home/dhayes/Source/PrismWeave

# Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Upload to GitHub Releases

1. Go to: https://github.com/davidhayesbc/PrismWeave/releases/new
2. Select tag: `v1.0.0`
3. Title: `PrismWeave Browser Extension v1.0.0`
4. Description: Include changelog and installation instructions
5. Upload: `releases/prismweave-extension-v1.0.0.zip`
6. Click **Publish release**

**Download URL:**

```
https://github.com/davidhayesbc/PrismWeave/releases/download/v1.0.0/prismweave-extension-v1.0.0.zip
```

### Update Your Website

Add download button to your website:

```html
<a
  href="https://github.com/davidhayesbc/PrismWeave/releases/download/v1.0.0/prismweave-extension-v1.0.0.zip"
>
  Download PrismWeave v1.0.0
</a>
```

---

## Step 4: Edge Add-ons Submission (30-45 minutes)

### 1. Partner Center Setup

1. Go to: https://partner.microsoft.com/dashboard/microsoftedge
2. Sign in with Microsoft account
3. Click **"New extension"**

### 2. Fill Required Information

**Product Details:**

```
Name: PrismWeave
Category: Productivity
```

**Short Description** (132 chars max):

```
Capture web pages as markdown and sync to GitHub. Smart content extraction and Git integration.
```

**Upload Package:**

- Upload: `releases/prismweave-extension-v1.0.0.zip`
- Wait for automatic validation

**Store Listing:**

- Upload screenshots (min 1, max 10)
- Add detailed description
- Set visibility: Public
- Set pricing: Free

**Privacy & Support:**

```
Privacy Policy URL: https://yoursite.com/privacy-policy
Support URL: https://github.com/davidhayesbc/PrismWeave/issues
Contact Email: your-email@example.com
```

### 3. Certification Notes

Add for reviewers:

```
Testing Instructions:
1. Install extension
2. Open options page (right-click icon → Options)
3. Configure:
   - GitHub Token: User provides their own (not included)
   - Repository: Format "owner/repo-name"
4. Visit any article page
5. Click extension icon to capture
6. Verify content committed to GitHub repository

Note: GitHub token is user-provided, NOT included in extension.
Extension does NOT collect any user data.
```

### 4. Submit for Review

1. Review all information
2. Click **Submit**
3. Wait 1-3 business days for review

**Track Status:** https://partner.microsoft.com/dashboard/microsoftedge/overview

---

## Step 5: Chrome Web Store (Optional, 30-45 minutes)

### 1. Developer Account

1. Go to: https://chrome.google.com/webstore/devconsole
2. Pay $5 one-time registration fee
3. Verify developer account

### 2. Submit Extension

1. Click **"New Item"**
2. Upload: `releases/prismweave-extension-v1.0.0.zip`
3. Click **Upload**

### 3. Store Listing

Fill in (similar to Edge):

- Detailed description
- Screenshots (1280x800)
- Category: Productivity
- Privacy practices disclosure
- Support information

### 4. Submit for Review

1. Click **Submit for review**
2. Wait 1-3 business days

---

## Step 6: Post-Deployment (10 minutes)

### Once Approved

#### Update Website with Store Links

**Edge Add-ons URL:**

```
https://microsoftedge.microsoft.com/addons/detail/[extension-id]
```

**Chrome Web Store URL:**

```
https://chrome.google.com/webstore/detail/[extension-id]
```

Add badges to your site:

```html
<a href="[edge-url]">
  <img src="https://img.shields.io/badge/edge-addons-blue" alt="Edge Add-ons" />
</a>
<a href="[chrome-url]">
  <img
    src="https://img.shields.io/badge/chrome-web%20store-brightgreen"
    alt="Chrome Web Store"
  />
</a>
```

#### Update README

```markdown
[![Edge Add-ons](https://img.shields.io/badge/edge-addons-blue)](edge-url)
[![Chrome Web Store](https://img.shields.io/badge/chrome-web%20store-brightgreen)](chrome-url)
```

#### Announce Release

- [ ] GitHub Discussions announcement
- [ ] Social media post
- [ ] Blog post (optional)
- [ ] Email newsletter (if applicable)

---

## Troubleshooting

### Build Fails

```bash
# Clear everything and rebuild
npm run clean
rm -rf node_modules
npm install
npm run build:prod
```

### Validation Errors

**Missing Icons:**

- Ensure `icons/` folder has: icon16.png, icon32.png, icon48.png, icon128.png

**Manifest Errors:**

- Validate manifest.json syntax
- Check all permissions are necessary

**Package Too Large:**

- Check for test files in dist/
- Verify no source files (.ts) in package
- Ensure production build (no source maps)

### Rejected Submission

Common reasons:

1. **Privacy policy not accessible** - Ensure URL works
2. **Insufficient testing instructions** - Add detailed steps
3. **Permissions not justified** - Explain why each is needed
4. **Functionality unclear** - Improve description

**Action:**

1. Read reviewer feedback carefully
2. Fix issues
3. Bump version (e.g., 1.0.0 → 1.0.1)
4. Rebuild and resubmit

---

## Quick Commands Reference

```bash
# Navigate to extension directory
cd /home/dhayes/Source/PrismWeave/browser-extension

# Full deployment process
npm run deploy

# Individual steps
npm run clean          # Clean build artifacts
npm test               # Run tests
npm run build:prod     # Production build
npm run package        # Create ZIP
npm run type-check     # TypeScript validation
npm run lint           # ESLint check

# Git operations
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## Timeline Estimates

| Task                        | Time Estimate |
| --------------------------- | ------------- |
| Pre-deployment preparation  | 1-2 hours     |
| Build and package           | 5 minutes     |
| Local testing               | 10-15 minutes |
| GitHub release              | 15 minutes    |
| Edge Add-ons submission     | 30-45 minutes |
| Chrome Web Store submission | 30-45 minutes |
| Edge review                 | 1-3 days      |
| Chrome review               | 1-3 days      |
| Post-deployment updates     | 15-30 minutes |

**Total Active Time:** ~2-3 hours (excluding review wait time)

---

## Support Resources

### Documentation

- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md) - Comprehensive guide
- **Checklist:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Detailed
  checklist
- **Privacy Template:** [PRIVACY_POLICY_TEMPLATE.md](PRIVACY_POLICY_TEMPLATE.md)

### Official Resources

- **Edge Developer:**
  https://learn.microsoft.com/en-us/microsoft-edge/extensions-chromium/
- **Chrome Extensions:** https://developer.chrome.com/docs/webstore/
- **Manifest V3:** https://developer.chrome.com/docs/extensions/mv3/

### Getting Help

- **GitHub Issues:** https://github.com/davidhayesbc/PrismWeave/issues
- **Edge Support:**
  https://developer.microsoft.com/microsoft-edge/extensions/support/
- **Chrome Support:** https://support.google.com/chrome_webstore/

---

## Success Checklist

After completing all steps:

- [ ] Extension built and packaged
- [ ] Tested locally in Chrome and Edge
- [ ] GitHub release created
- [ ] Download available on website
- [ ] Submitted to Edge Add-ons (pending review)
- [ ] Submitted to Chrome Web Store (optional, pending review)
- [ ] Privacy policy accessible
- [ ] Support email configured
- [ ] Documentation updated
- [ ] Ready to monitor reviews and user feedback

**Congratulations! Your extension is deployed!** 🎉

---

## What's Next?

### During Review Period

- Monitor submission status daily
- Respond promptly to reviewer questions
- Prepare for potential requested changes

### After Approval

- Update website with official store links
- Announce release to community
- Set up user support channels
- Monitor user reviews and ratings
- Plan for version 1.1 features

### Ongoing Maintenance

- Monitor GitHub Issues
- Respond to user feedback
- Plan updates and improvements
- Keep dependencies updated
- Maintain documentation

---

**Need help?**

- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guidance
- Open an issue: https://github.com/davidhayesbc/PrismWeave/issues
- Contact: [your-email@example.com]
