# PrismWeave Browser Extension - Quick Deployment Checklist

## Pre-Deployment Checklist

### Development Complete

- [ ] All features implemented and tested
- [ ] All tests passing (`npm test`)
- [ ] No TypeScript errors (`npm run type-check`)
- [ ] Code linted and formatted (`npm run lint`)
- [ ] Documentation updated

### Version & Changelog

- [ ] Version number updated in `package.json`
- [ ] Version number updated in `manifest.json`
- [ ] CHANGELOG.md updated with new changes
- [ ] Git commit history clean

### Marketing Materials Prepared

- [ ] Screenshots captured (1280x800 recommended)
  - [ ] Extension popup
  - [ ] Options page
  - [ ] Content capture in action
  - [ ] GitHub integration
  - [ ] Captured documents
- [ ] Privacy policy published at accessible URL
- [ ] Detailed description written
- [ ] Short description written (132 chars max)
- [ ] Feature list prepared

### Legal & Compliance

- [ ] Privacy policy URL: ******\_\_\_\_******
- [ ] Support/contact email: ******\_\_\_\_******
- [ ] Terms of service (if applicable)
- [ ] License information confirmed (MIT)

---

## Build & Package

### Quick Build

```bash
# Navigate to browser extension directory
cd /home/dhayes/Source/PrismWeave/browser-extension

# Run automated deployment helper
bash scripts/deploy.sh
```

### Manual Build Steps

```bash
# 1. Clean previous builds
npm run clean

# 2. Run tests
npm test

# 3. Build production version
npm run build:prod

# 4. Create package
npm run package
```

### Verify Build

- [ ] Package created: `prismweave-extension-v*.zip`
- [ ] Package size reasonable (< 10MB)
- [ ] All files included in ZIP
- [ ] manifest.json at root level
- [ ] No development files (.ts, .map) in production build

---

## Local Testing

### Chrome Testing

```bash
# 1. Open chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select: /home/dhayes/Source/PrismWeave/dist/browser-extension
```

- [ ] Extension loads without errors
- [ ] Icon displays correctly
- [ ] Popup opens and works
- [ ] Options page accessible
- [ ] Content capture works
- [ ] GitHub integration works
- [ ] Context menu appears
- [ ] Keyboard shortcut works (Alt+S)

### Edge Testing

```bash
# 1. Open edge://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select: /home/dhayes/Source/PrismWeave/dist/browser-extension
```

- [ ] Extension loads without errors
- [ ] All features work as in Chrome
- [ ] No Edge-specific issues

---

## GitHub Release

### Create Release

```bash
# 1. Tag the version
git tag -a v1.0.0 -m "Release v1.0.0"

# 2. Push tag to GitHub
git push origin v1.0.0

# 3. Create release on GitHub
# Go to: https://github.com/davidhayesbc/PrismWeave/releases/new
```

### Release Content

- [ ] Tag version: v1.0.0
- [ ] Release title: "PrismWeave Browser Extension v1.0.0"
- [ ] Description with changelog
- [ ] ZIP file attached: `prismweave-extension-v1.0.0.zip`
- [ ] Installation instructions included

---

## Website Deployment

### Update Download Page

- [ ] Add/update download button with GitHub release URL
- [ ] Update version number on website
- [ ] Add installation instructions
- [ ] Link to privacy policy
- [ ] Add support/contact information

### Example Download URL

```
https://github.com/davidhayesbc/PrismWeave/releases/download/v1.0.0/prismweave-extension-v1.0.0.zip
```

---

## Edge Add-ons Submission

### Partner Center Setup

- [ ] Microsoft Partner Center account created
- [ ] Enrolled in Edge Add-ons program
- [ ] Developer profile completed

### Submission Info

- [ ] Product name: `PrismWeave`
- [ ] Category: `Productivity`
- [ ] Short description (132 chars)
- [ ] Detailed description
- [ ] Screenshots uploaded (min 1, max 10)
- [ ] Icon uploaded (128x128)
- [ ] Privacy policy URL: ******\_\_\_\_******
- [ ] Support URL: ******\_\_\_\_******
- [ ] Homepage URL: ******\_\_\_\_******

### Upload Package

- [ ] ZIP file uploaded
- [ ] Validation passed
- [ ] No errors reported

### Certification Notes

```
Testing Instructions:
1. Install extension
2. Open options page
3. Configure GitHub token and repository:
   - Token: User must provide their own token
   - Repository: Format owner/repo-name
4. Visit any article page
5. Click extension icon to capture
6. Verify content saved to GitHub

Note: GitHub token is user-provided, NOT included in extension.
Extension does not collect any user data.
```

### Submit

- [ ] All information reviewed
- [ ] Privacy practices disclosed
- [ ] Submitted for review
- [ ] Confirmation received

**Estimated review time:** 1-3 business days

---

## Chrome Web Store Submission (Optional)

### Developer Account

- [ ] Chrome Web Store Developer account created
- [ ] $5 registration fee paid
- [ ] Identity verified

### Store Listing

- [ ] Detailed description added
- [ ] Screenshots uploaded (1280x800)
- [ ] Small tile icon (440x280)
- [ ] Privacy practices disclosed
- [ ] Category selected: Productivity

### Submission

- [ ] ZIP file uploaded
- [ ] Validation passed
- [ ] All required fields completed
- [ ] Submitted for review

**Estimated review time:** 1-3 business days

---

## Post-Deployment

### Monitor Review Status

**Edge Add-ons:**

- URL: https://partner.microsoft.com/dashboard/microsoftedge
- [ ] Check status daily
- [ ] Respond to reviewer feedback if needed

**Chrome Web Store:**

- URL: https://chrome.google.com/webstore/devconsole
- [ ] Check status daily
- [ ] Respond to reviewer feedback if needed

### Once Approved

#### Update Website

- [ ] Add Edge Add-ons store badge and link
- [ ] Add Chrome Web Store badge and link (if applicable)
- [ ] Update installation instructions
- [ ] Add "Get it from Microsoft Edge Add-ons" button

#### Update Repository

- [ ] Update README.md with store links
- [ ] Add store badges to README
- [ ] Update documentation links

#### Announce Release

- [ ] Create announcement on GitHub Discussions
- [ ] Post on social media
- [ ] Update project website
- [ ] Notify beta testers/early users

---

## Support Setup

### User Support Channels

- [ ] GitHub Issues configured for bug reports
- [ ] Support email set up
- [ ] FAQ page created
- [ ] Documentation site updated

### Monitoring

- [ ] Set up alerts for new reviews
- [ ] Monitor GitHub Issues
- [ ] Check extension error reports
- [ ] Track installation numbers

---

## Version Control

### Git Tags

```bash
# List all tags
git tag -l

# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push single tag
git push origin v1.0.0

# Push all tags
git push --tags
```

### Branch Strategy

- [ ] `main` branch is stable
- [ ] Development work in feature branches
- [ ] Tagged releases from `main`

---

## Troubleshooting Common Issues

### Build Errors

```bash
# Clear cache and rebuild
npm run clean
rm -rf node_modules
npm install
npm run build:prod
```

### Package Too Large

- [ ] Check for unnecessary files in dist/
- [ ] Verify no test files included
- [ ] Compress images if needed
- [ ] Review bundled dependencies

### Validation Failures

**Missing Icons:**

```bash
# Verify icons exist
ls -la icons/
# Should have: icon16.png, icon32.png, icon48.png, icon128.png
```

**Manifest Errors:**

```javascript
// Validate manifest.json
node -e "console.log(JSON.parse(require('fs').readFileSync('manifest.json')))"
```

**Permission Issues:**

- Review all requested permissions
- Ensure minimal permissions requested
- Justify each permission in submission notes

---

## Quick Commands Reference

```bash
# Navigate to extension directory
cd /home/dhayes/Source/PrismWeave/browser-extension

# Run all tests
npm test

# Build production (no source maps, minified)
npm run build:prod

# Create deployment package
npm run package

# Run deployment helper script
bash scripts/deploy.sh

# Type check only
npm run type-check

# Lint code
npm run lint

# Format code
npm run format

# Clean build artifacts
npm run clean
```

---

## Important URLs

### Development

- Repository: https://github.com/davidhayesbc/PrismWeave
- Issues: https://github.com/davidhayesbc/PrismWeave/issues
- Releases: https://github.com/davidhayesbc/PrismWeave/releases

### Store Dashboards

- Edge Partner Center: https://partner.microsoft.com/dashboard/microsoftedge
- Chrome Web Store: https://chrome.google.com/webstore/devconsole

### Documentation

- Edge Extensions:
  https://learn.microsoft.com/en-us/microsoft-edge/extensions-chromium/
- Chrome Extensions: https://developer.chrome.com/docs/extensions/
- Manifest V3: https://developer.chrome.com/docs/extensions/mv3/

---

## Support Contacts

**Microsoft Edge Add-ons Support:**

- https://developer.microsoft.com/microsoft-edge/extensions/support/

**Chrome Web Store Support:**

- https://support.google.com/chrome_webstore/

**Community Support:**

- GitHub Discussions: https://github.com/davidhayesbc/PrismWeave/discussions

---

## Notes

- Keep this checklist updated with each release
- Document any new issues discovered during deployment
- Update process improvements for next release
- Save reviewer feedback for future reference

**Last Updated:** [Date] **Current Version:** [Version]
