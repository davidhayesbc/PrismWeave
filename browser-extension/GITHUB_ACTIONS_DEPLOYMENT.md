# GitHub Actions Deployment Guide

Automated deployment workflows for PrismWeave browser extension using GitHub
Actions.

## 🚀 Overview

PrismWeave includes comprehensive GitHub Actions workflows for automated browser
extension deployment. You have three deployment options:

1. **Automated Tag Deployment** - Push a tag to trigger automatic build and
   release
2. **Manual Workflow Dispatch** - Deploy from GitHub UI with custom options
3. **Full Auto-Release** - Complete version management and deployment automation

---

## 📋 Available Workflows

### 1. Deploy Browser Extension (`deploy-browser-extension.yml`)

**Purpose:** Dedicated workflow for building, testing, and deploying the browser
extension.

**Triggers:**

- **Automatic:** Push a Git tag matching `extension-v*` (e.g.,
  `extension-v1.0.0`)
- **Manual:** Trigger from GitHub Actions tab with custom inputs

**What it does:**

- ✅ Syncs version across `package.json` and `manifest.json`
- ✅ Runs TypeScript type checking
- ✅ Runs full test suite with coverage
- ✅ Builds production-optimized extension
- ✅ Creates versioned ZIP package
- ✅ Uploads to GitHub Releases
- ✅ Updates documentation automatically
- ✅ Optionally triggers website deployment

**Outputs:**

- Browser extension ZIP package
- Test coverage reports
- Build artifacts
- GitHub Release with installation instructions

---

### 2. Auto Release (`auto-release.yml`)

**Purpose:** Automated version management and multi-component release.

**Triggers:**

- **Manual only:** Workflow dispatch from GitHub Actions tab

**What it does:**

- ✅ Calculates next version automatically
- ✅ Updates all package.json files
- ✅ Builds browser extension AND bookmarklet
- ✅ Creates versioned packages
- ✅ Creates Git tag and pushes changes
- ✅ Creates GitHub Release with both packages
- ✅ Triggers website deployment

**Use when:**

- You want full version automation
- You need to release both extension and bookmarklet
- You want automatic version calculation

---

### 3. Create Release (`create-release.yml`)

**Purpose:** Simple tag-based release creation.

**Triggers:**

- **Automatic:** Push any Git tag matching `v*` (e.g., `v1.0.0`)

**What it does:**

- ✅ Builds browser extension
- ✅ Builds bookmarklet
- ✅ Creates GitHub Release
- ✅ Deploys to GitHub Pages

**Use when:**

- You've already updated version numbers manually
- You want a simple tag-triggered release

---

## 🎯 Quick Start Guides

### Option A: Automated Tag Deployment (Recommended)

**Best for:** Quick releases with minimal manual work

```bash
# 1. Create and push an extension tag
git tag -a extension-v1.0.0 -m "Release browser extension v1.0.0"
git push origin extension-v1.0.0

# The workflow automatically:
# - Syncs version across files
# - Runs tests
# - Builds production package
# - Creates GitHub Release
```

**Result:** Within 5-10 minutes, you'll have a GitHub Release with downloadable
ZIP package.

---

### Option B: Manual Workflow Dispatch (Maximum Control)

**Best for:** Custom deployments with specific options

1. **Navigate to GitHub Actions:**
   - Go to: `https://github.com/davidhayesbc/PrismWeave/actions`
   - Click on **"Deploy Browser Extension"** workflow

2. **Click "Run workflow"** button

3. **Fill in the form:**
   - **Version:** `1.0.0` (or your target version)
   - **Create GitHub Release:** ✅ Yes (default)
   - **Deploy to website:** ✅ Yes (default)

4. **Click "Run workflow"** to start

5. **Monitor progress:**
   - Watch the workflow run in the Actions tab
   - Review build logs if needed

6. **Access results:**
   - Download package from Actions artifacts
   - Or download from GitHub Releases (if enabled)

---

### Option C: Full Auto-Release (Complete Automation)

**Best for:** Regular release cycles with version management

1. **Navigate to GitHub Actions:**
   - Go to: `https://github.com/davidhayesbc/PrismWeave/actions`
   - Click on **"Auto Release"** workflow

2. **Click "Run workflow"** button

3. **Configure release:**
   - **Major version:** `1` (current major version)
   - **Minor version:** `0` (current minor version)
   - **Release type:** Select one:
     - `patch` - Bug fixes (1.0.0 → 1.0.1)
     - `minor` - New features (1.0.0 → 1.1.0)
     - `major` - Breaking changes (1.0.0 → 2.0.0)
   - **Draft release:** No (creates public release immediately)

4. **Click "Run workflow"**

5. **What happens automatically:**
   - Calculates new version number
   - Updates `package.json` files
   - Runs full test suite
   - Builds production packages
   - Creates Git tag
   - Pushes version commit
   - Creates GitHub Release
   - Uploads browser extension + bookmarklet
   - Triggers website deployment

---

## 📊 Workflow Comparison

| Feature                 | Deploy Extension | Auto Release | Create Release |
| ----------------------- | ---------------- | ------------ | -------------- |
| **Trigger**             | Tag or Manual    | Manual Only  | Tag Only       |
| **Version Syncing**     | ✅ Yes           | ✅ Yes       | ⚠️ Manual      |
| **Test Coverage**       | ✅ Yes           | ✅ Yes       | ✅ Yes         |
| **Extension Package**   | ✅ Yes           | ✅ Yes       | ✅ Yes         |
| **Bookmarklet Package** | ❌ No            | ✅ Yes       | ✅ Yes         |
| **GitHub Release**      | ✅ Optional      | ✅ Yes       | ✅ Yes         |
| **Website Deploy**      | ✅ Optional      | ✅ Yes       | ✅ Yes         |
| **Version Automation**  | ⚠️ Uses tag      | ✅ Full Auto | ❌ Manual      |
| **Git Commit**          | ❌ No            | ✅ Yes       | ❌ No          |

**Legend:**

- ✅ Full support
- ⚠️ Partial/conditional support
- ❌ Not included

---

## 🛠️ Detailed Instructions

### How to Push a Tag (Option A)

```bash
# Method 1: Create annotated tag (recommended)
git tag -a extension-v1.0.0 -m "Release browser extension v1.0.0"
git push origin extension-v1.0.0

# Method 2: Create lightweight tag
git tag extension-v1.0.0
git push origin extension-v1.0.0

# Method 3: Create tag from specific commit
git tag -a extension-v1.0.0 <commit-hash> -m "Release v1.0.0"
git push origin extension-v1.0.0
```

**Tag Naming Convention:**

- Use format: `extension-v{MAJOR}.{MINOR}.{PATCH}`
- Examples:
  - `extension-v1.0.0` - First release
  - `extension-v1.0.1` - Patch release
  - `extension-v1.1.0` - Minor release
  - `extension-v2.0.0` - Major release

---

### How to Run Manual Deployment (Option B)

**Step-by-Step:**

1. **Navigate to Actions Tab:**

   ```
   https://github.com/davidhayesbc/PrismWeave/actions
   ```

2. **Select Workflow:**
   - Click "Deploy Browser Extension" in the left sidebar

3. **Run Workflow:**
   - Click "Run workflow" dropdown (top-right)
   - Select branch: `main`
   - Enter version: `1.0.0`
   - Check/uncheck options as needed
   - Click green "Run workflow" button

4. **Monitor Execution:**
   - Workflow appears in the runs list
   - Click the workflow run to see live progress
   - Each job shows real-time logs

5. **Download Results:**
   - **From Artifacts:** Scroll to bottom of workflow run → Download ZIP
   - **From Releases:** Go to Releases page → Download latest release

---

### How to Use Auto-Release (Option C)

**Step-by-Step:**

1. **Prepare for Release:**

   ```bash
   # Ensure your main branch is up-to-date
   git checkout main
   git pull origin main

   # Verify tests pass locally
   cd browser-extension
   npm test
   ```

2. **Navigate to Actions Tab:**

   ```
   https://github.com/davidhayesbc/PrismWeave/actions
   ```

3. **Select "Auto Release" Workflow:**
   - Click "Auto Release" in the left sidebar

4. **Fill in Release Configuration:**

   **Example 1: Patch Release (Bug Fix)**
   - Major: `1`
   - Minor: `0`
   - Release type: `patch`
   - Result: `v1.0.5` → `v1.0.6`

   **Example 2: Minor Release (New Features)**
   - Major: `1`
   - Minor: `0`
   - Release type: `minor`
   - Result: `v1.0.x` → `v1.1.0`

   **Example 3: Major Release (Breaking Changes)**
   - Major: `1`
   - Minor: `0`
   - Release type: `major`
   - Result: `v1.x.x` → `v2.0.0`

5. **Create Release:**
   - Check "Create as draft release" if you want to review first
   - Click "Run workflow"

6. **Automatic Steps:**
   - Workflow calculates next version
   - Updates package.json and manifest.json
   - Runs full CI/CD pipeline
   - Creates Git tag
   - Commits and pushes changes
   - Creates GitHub Release
   - Uploads packages

7. **Post-Release:**

   ```bash
   # Pull the new version commit and tag
   git pull origin main --tags

   # Verify new version
   git describe --tags
   ```

---

## 📥 Accessing Build Outputs

### From GitHub Releases

```bash
# List all releases
gh release list

# Download specific release
gh release download extension-v1.0.0

# Or visit in browser
https://github.com/davidhayesbc/PrismWeave/releases
```

### From Workflow Artifacts

1. **Navigate to workflow run:**
   - Actions tab → Select workflow run → Scroll to "Artifacts"

2. **Download artifacts:**
   - Click artifact name to download ZIP
   - Extract to access files

**Artifact Types:**

- `browser-extension-v{VERSION}` - Full build output + ZIP package
- `extension-coverage-{VERSION}` - Test coverage reports
- `build-artifacts` - General build outputs

---

## 🔍 Monitoring Workflow Runs

### Viewing Workflow Status

**In GitHub UI:**

1. Go to Actions tab
2. Click on workflow name
3. Select specific run
4. View jobs and steps
5. Expand steps to see logs

### Using GitHub CLI

```bash
# List recent workflow runs
gh run list --workflow deploy-browser-extension.yml

# View specific run
gh run view <run-id>

# Watch run in real-time
gh run watch <run-id>

# View logs
gh run view <run-id> --log
```

### Workflow Summary

Each workflow provides a **summary page** with:

- 📦 Package details (version, size)
- ✅ Completed steps checklist
- 🔗 Direct download links
- 📋 Next steps for store submission
- 📖 Documentation links

---

## 🚨 Troubleshooting

### Common Issues

#### 1. **Workflow Failed: Tests Failed**

**Cause:** Test suite didn't pass.

**Solution:**

```bash
# Run tests locally first
cd browser-extension
npm test

# Fix any failing tests
# Then retry workflow
```

---

#### 2. **Workflow Failed: Version Already Exists**

**Cause:** Tag already exists for this version.

**Solution:**

```bash
# Delete the tag locally and remotely
git tag -d extension-v1.0.0
git push origin --delete extension-v1.0.0

# Or use a new version number
git tag -a extension-v1.0.1 -m "Release v1.0.1"
git push origin extension-v1.0.1
```

---

#### 3. **Workflow Failed: Permission Denied**

**Cause:** Workflow doesn't have permission to create releases.

**Solution:**

1. Go to: Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Check "Allow GitHub Actions to create and approve pull requests"
5. Save changes

---

#### 4. **Package Not Found in Release**

**Cause:** Workflow succeeded but package isn't attached.

**Solution:**

1. Check workflow logs for upload step
2. Verify file path in workflow output
3. Download from Artifacts as fallback
4. Manually attach to release if needed

---

#### 5. **Build Failed: TypeScript Errors**

**Cause:** Type check failed.

**Solution:**

```bash
# Run type check locally
cd browser-extension
npx tsc --noEmit

# Fix type errors
# Push fixes and retry
```

---

#### 6. **manifest.json Version Mismatch**

**Cause:** Versions not synced between package.json and manifest.json.

**Solution:**

```bash
# The workflow auto-syncs versions, but if manual intervention needed:
cd browser-extension

# Update manifest.json to match package.json
node -e "
  const fs = require('fs');
  const pkg = require('./package.json');
  const manifest = require('./manifest.json');
  manifest.version = pkg.version;
  fs.writeFileSync('manifest.json', JSON.stringify(manifest, null, 2));
"

# Commit and push
git add manifest.json
git commit -m "chore: sync manifest version"
git push
```

---

## 📚 Related Documentation

- [Main Deployment Guide](./DEPLOYMENT.md) - Comprehensive deployment
  documentation
- [Quick Deploy](./QUICK_DEPLOY.md) - Fast-track deployment guide
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md) - Step-by-step checklist
- [Privacy Policy Template](./PRIVACY_POLICY_TEMPLATE.md) - Required for store
  submission

---

## 🔐 Security Considerations

### Secrets Configuration

All workflows use `GITHUB_TOKEN` automatically provided by GitHub Actions. No
additional secrets needed for basic deployment.

**For store submission automation (future):**

- `EDGE_CLIENT_ID` - Microsoft Partner Center API client ID
- `EDGE_CLIENT_SECRET` - Microsoft Partner Center API secret
- `CHROME_CLIENT_ID` - Chrome Web Store API client ID
- `CHROME_CLIENT_SECRET` - Chrome Web Store API secret
- `CHROME_REFRESH_TOKEN` - Chrome Web Store API refresh token

**Setting secrets:**

1. Go to: Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add secret name and value
4. Save

---

## 📈 Best Practices

### 1. **Version Numbering**

Follow semantic versioning:

- **MAJOR:** Breaking changes (1.0.0 → 2.0.0)
- **MINOR:** New features, backwards compatible (1.0.0 → 1.1.0)
- **PATCH:** Bug fixes (1.0.0 → 1.0.1)

### 2. **Pre-Release Testing**

Always test locally before triggering workflows:

```bash
cd browser-extension
npm run test:coverage
npm run type-check
npm run build
```

### 3. **Git Tags**

Use annotated tags with descriptive messages:

```bash
git tag -a extension-v1.0.0 -m "
Release v1.0.0

Features:
- Added smart content extraction
- Improved markdown conversion
- GitHub integration enhancements

Fixes:
- Fixed image handling bug
- Resolved CORS issues
"
```

### 4. **Changelog Maintenance**

Keep `CHANGELOG.md` updated:

```markdown
## [1.0.0] - 2025-01-15

### Added

- Smart content extraction algorithm
- Keyboard shortcut support (Alt+Shift+C)

### Changed

- Improved markdown conversion quality

### Fixed

- Image URL resolution in captures
```

### 5. **Branch Protection**

Protect your main branch:

1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Check: "Require status checks to pass before merging"
4. Select: CI/CD Pipeline, tests

---

## ⏱️ Workflow Timing

**Typical execution times:**

| Workflow         | Duration  | Bottleneck                 |
| ---------------- | --------- | -------------------------- |
| Deploy Extension | 5-8 mins  | Tests + Build              |
| Auto Release     | 8-12 mins | Version management + Build |
| Create Release   | 6-10 mins | Build + Deploy             |

**Optimization tips:**

- Tests run in parallel where possible
- Build caching speeds up dependencies
- Artifacts have 90-day retention

---

## 🎓 Examples

### Example 1: Quick Patch Release

```bash
# You fixed a critical bug and need to release immediately

# 1. Commit your fix
git add .
git commit -m "fix: resolve critical bug in content extraction"
git push origin main

# 2. Create and push tag
git tag -a extension-v1.0.5 -m "Hotfix: Critical content extraction bug"
git push origin extension-v1.0.5

# 3. Workflow automatically:
#    - Runs tests
#    - Builds extension
#    - Creates release
#    - Deploys to website

# 4. Within 5-10 minutes, release is live
```

---

### Example 2: Feature Release with Auto-Version

```bash
# You've added several new features and want full automation

# 1. Ensure main branch is ready
git checkout main
git pull origin main
npm test  # Verify tests pass

# 2. Go to GitHub Actions tab
# 3. Select "Auto Release"
# 4. Configure:
#    - Major: 1
#    - Minor: 0
#    - Type: minor (1.0.x → 1.1.0)
# 5. Run workflow

# 6. Workflow automatically:
#    - Bumps version to 1.1.0
#    - Commits version change
#    - Creates tag v1.1.0
#    - Builds and tests
#    - Creates release
#    - Updates documentation

# 7. Pull the changes
git pull origin main --tags
```

---

### Example 3: Manual Control with Review

```bash
# You want to review everything before public release

# 1. Go to GitHub Actions → Auto Release
# 2. Configure:
#    - Version settings
#    - Draft release: YES
# 3. Run workflow

# 4. Workflow creates draft release
# 5. Review in GitHub Releases
# 6. Edit release notes if needed
# 7. Publish when ready
```

---

## 🔄 Workflow Integration

### Integration with Existing `deploy.sh`

The GitHub Actions workflows **complement** the local `deploy.sh` script:

**Local `deploy.sh` - Use when:**

- Developing locally
- Testing deployment process
- Quick manual package creation
- No internet connection

**GitHub Actions - Use when:**

- Want automated testing before deployment
- Need reproducible builds
- Want automatic GitHub Release creation
- Deploying from CI/CD pipeline

**Both approaches produce identical ZIP packages** and can be used
interchangeably.

---

## 📞 Support

If you encounter issues with GitHub Actions workflows:

1. **Check workflow logs:** Actions tab → Select run → View logs
2. **Review this guide:** Look for matching troubleshooting section
3. **Local testing:** Try building locally first to isolate the issue
4. **GitHub Issues:**
   [Create an issue](https://github.com/davidhayesbc/PrismWeave/issues)
5. **GitHub Discussions:**
   [Ask in discussions](https://github.com/davidhayesbc/PrismWeave/discussions)

---

## ✅ Summary

You now have **three powerful deployment options**:

1. **Tag Deployment** - Push `extension-v1.0.0` tag → Automatic release
2. **Manual Dispatch** - Use GitHub UI for custom deployments
3. **Auto-Release** - Full version management automation

Choose the method that best fits your workflow!

**Quick Reference:**

- 🚀 **Fast release:** Push a tag
- 🎛️ **Custom options:** Use manual dispatch
- 🤖 **Full automation:** Use auto-release

**Happy deploying! 🎉**
