# GitHub Actions Deployment - Quick Reference

## ✅ What Was Added

Three new/enhanced GitHub Actions workflows for automated browser extension
deployment:

### 1. **deploy-browser-extension.yml** (NEW)

- **Location:** `.github/workflows/deploy-browser-extension.yml`
- **Purpose:** Dedicated browser extension deployment workflow
- **Triggers:**
  - Automatic: Git tag push matching `extension-v*`
  - Manual: Workflow dispatch from GitHub UI
- **Features:**
  - ✅ Auto-syncs `package.json` ↔ `manifest.json` versions
  - ✅ Runs TypeScript type checking
  - ✅ Runs full test suite with coverage
  - ✅ Creates production build
  - ✅ Packages versioned ZIP
  - ✅ Creates GitHub Release
  - ✅ Updates documentation
  - ✅ Optionally triggers website deployment

### 2. **auto-release.yml** (ENHANCED)

- **Location:** `.github/workflows/auto-release.yml`
- **Enhancement:** Now properly syncs `manifest.json` version
- **Purpose:** Full automated version management and release
- **Triggers:** Manual workflow dispatch only
- **Features:**
  - ✅ Automatic version calculation
  - ✅ Syncs all version files (package.json + manifest.json)
  - ✅ Creates Git tags
  - ✅ Builds browser extension + bookmarklet
  - ✅ Creates GitHub Release

### 3. **New Documentation**

- **GITHUB_ACTIONS_DEPLOYMENT.md** - Complete GitHub Actions deployment guide
- **README.md** - Updated with GitHub Actions deployment section

---

## 🚀 How to Deploy (3 Methods)

### Method 1: Push a Tag (Quickest) ⚡

```bash
# Create and push an extension tag
git tag -a extension-v1.0.0 -m "Release browser extension v1.0.0"
git push origin extension-v1.0.0
```

**Result:** Within 5-10 minutes, you'll have:

- ✅ Automated build & tests
- ✅ GitHub Release with downloadable ZIP
- ✅ Ready for website distribution & store submission

---

### Method 2: Manual Workflow Dispatch 🎛️

1. Go to: https://github.com/davidhayesbc/PrismWeave/actions
2. Click "Deploy Browser Extension" workflow
3. Click "Run workflow" button
4. Enter version (e.g., `1.0.0`)
5. Configure options (create release, deploy to website)
6. Click "Run workflow"

**Best for:** Custom deployments with specific options

---

### Method 3: Auto-Release (Full Automation) 🤖

1. Go to: https://github.com/davidhayesbc/PrismWeave/actions
2. Click "Auto Release" workflow
3. Click "Run workflow"
4. Configure:
   - Major: `1`
   - Minor: `0`
   - Release type: `patch` / `minor` / `major`
5. Click "Run workflow"

**Result:** Workflow automatically:

- Calculates next version
- Updates all version files
- Creates tag & commit
- Builds & packages
- Creates GitHub Release

**Best for:** Regular release cycles with version management

---

## 📋 Quick Comparison

| Method              | Trigger   | Version Mgmt | Effort | Use Case       |
| ------------------- | --------- | ------------ | ------ | -------------- |
| **Push Tag**        | Git tag   | Manual       | Low    | Quick releases |
| **Manual Dispatch** | GitHub UI | Manual/Auto  | Medium | Custom options |
| **Auto-Release**    | GitHub UI | Automatic    | Low    | Regular cycles |

---

## 🎯 Workflow Outputs

After successful deployment, you get:

### GitHub Release

- **URL:** `https://github.com/davidhayesbc/PrismWeave/releases`
- **Contains:**
  - Browser extension ZIP (ready for website distribution)
  - Installation instructions
  - Release notes
  - Direct download links

### Build Artifacts

- **Location:** Workflow run → Artifacts section
- **Contains:**
  - Full build output
  - Test coverage reports
  - Package files

### Website Deployment (Optional)

- Automatically triggers website update workflow
- Extension available at: `https://davidhayesbc.github.io/PrismWeave/`

---

## 📥 What You Can Do with the Release

### 1. Website Distribution

**Download the ZIP from GitHub Releases and:**

- Host on your website for user downloads
- Link directly to GitHub Release download URL
- Provide installation instructions

**Example:**

```markdown
Download:
[PrismWeave Extension v1.0.0](https://github.com/davidhayesbc/PrismWeave/releases/download/extension-v1.0.0/prismweave-extension-v1.0.0.zip)
```

---

### 2. Microsoft Edge Add-ons Submission

**Steps:**

1. Download ZIP from GitHub Release
2. Go to: https://partner.microsoft.com/dashboard/microsoftedge
3. Click "New Extension"
4. Upload the ZIP file
5. Fill in store listing:
   - Name: PrismWeave
   - Description: (from DEPLOYMENT.md)
   - Screenshots: (capture from running extension)
   - Privacy policy URL: (your hosted policy)
6. Submit for review

**Review time:** 1-3 business days

---

### 3. Chrome Web Store Submission

**Steps:**

1. Download ZIP from GitHub Release
2. Go to: https://chrome.google.com/webstore/devconsole
3. Click "New item"
4. Upload the ZIP file
5. Complete store listing
6. Submit for review

**Review time:** 1-7 days

---

## 🔧 Configuration

### Required Permissions

The workflows use `GITHUB_TOKEN` (automatically provided).

**To enable workflow permissions:**

1. Go to: Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Check "Allow GitHub Actions to create and approve pull requests"
5. Save

---

### Optional Secrets (Future Store Automation)

If you want to automate store submissions in the future:

**Microsoft Edge:**

- `EDGE_CLIENT_ID`
- `EDGE_CLIENT_SECRET`

**Chrome Web Store:**

- `CHROME_CLIENT_ID`
- `CHROME_CLIENT_SECRET`
- `CHROME_REFRESH_TOKEN`

---

## 📖 Documentation

| Document                         | Purpose                                        |
| -------------------------------- | ---------------------------------------------- |
| **GITHUB_ACTIONS_DEPLOYMENT.md** | Complete GitHub Actions guide with examples    |
| **DEPLOYMENT.md**                | Manual deployment process and store submission |
| **QUICK_DEPLOY.md**              | Fast-track deployment guide                    |
| **DEPLOYMENT_CHECKLIST.md**      | Step-by-step checklist                         |

---

## ✅ Next Steps

### 1. Test the Workflow (Recommended)

```bash
# Test with a development tag first
git tag -a extension-v0.0.1-test -m "Test deployment workflow"
git push origin extension-v0.0.1-test
```

This will:

- Run the full workflow
- Create a test release
- Verify everything works
- Can be deleted after verification

---

### 2. Configure Workflow Permissions

Follow the "Required Permissions" section above.

---

### 3. Create Your First Release

**Option A - Quick release:**

```bash
git tag -a extension-v1.0.0 -m "Release v1.0.0"
git push origin extension-v1.0.0
```

**Option B - Full automation:**

- Use "Auto Release" workflow from GitHub Actions tab

---

### 4. Submit to Stores

After release is created:

1. Download ZIP from GitHub Releases
2. Submit to Edge Add-ons (1-3 days review)
3. Optionally submit to Chrome Web Store (1-7 days review)

---

## 🆘 Troubleshooting

### Workflow Failed?

**Check the logs:**

1. Go to Actions tab
2. Click the failed workflow run
3. Click the failed job
4. Review error messages

**Common issues:**

- **Tests failed:** Fix tests locally first, then re-trigger
- **Permission denied:** Enable workflow permissions (see Configuration)
- **Tag already exists:** Delete tag or use new version number
- **Build failed:** Check TypeScript errors locally

---

### Manual Intervention Needed?

**Download from artifacts:**

1. Go to workflow run
2. Scroll to "Artifacts" section
3. Download the extension package

---

## 📊 Workflow Timing

**Typical execution times:**

- Deploy Extension: **5-8 minutes**
- Auto Release: **8-12 minutes**

**Breakdown:**

- Checkout & setup: ~1 min
- Install dependencies: ~2 min
- Tests: ~1-2 min
- Build: ~1 min
- Package & upload: ~1 min

---

## 🎓 Examples

### Example 1: Hotfix Release

```bash
# You fixed a critical bug
git add .
git commit -m "fix: critical content extraction bug"
git push

# Deploy immediately
git tag -a extension-v1.0.1 -m "Hotfix: Critical bug"
git push origin extension-v1.0.1

# Within 5-10 minutes: Release is live!
```

---

### Example 2: Feature Release

```bash
# Use Auto-Release for version management
# 1. Go to Actions tab
# 2. Select "Auto Release"
# 3. Set: Major=1, Minor=0, Type=minor
# 4. Run workflow
# 5. Workflow creates v1.1.0 automatically
```

---

### Example 3: Draft Release for Review

```bash
# Use Manual Dispatch
# 1. Go to Actions tab → Deploy Browser Extension
# 2. Enter version: 1.0.0
# 3. Create GitHub Release: No
# 4. Run workflow
# 5. Download from artifacts
# 6. Test locally
# 7. Manually create release when ready
```

---

## ✨ Summary

**You now have automated browser extension deployment!**

**Three ways to deploy:**

1. 🏷️ **Tag push** - `git push origin extension-v1.0.0`
2. 🎛️ **Manual dispatch** - GitHub Actions UI
3. 🤖 **Auto-release** - Full automation

**What you get:**

- ✅ Automated testing
- ✅ Production build
- ✅ Versioned ZIP package
- ✅ GitHub Release
- ✅ Ready for website & store distribution

**Ready to deploy! 🚀**

---

## 📞 Support

- **Detailed guide:**
  [GITHUB_ACTIONS_DEPLOYMENT.md](GITHUB_ACTIONS_DEPLOYMENT.md)
- **Manual deployment:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues:** [GitHub Issues](https://github.com/davidhayesbc/PrismWeave/issues)
