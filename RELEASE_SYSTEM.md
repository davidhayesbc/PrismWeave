# 🚀 Automatic Release System

This document explains how to use PrismWeave's automatic versioning and release system.

## 📋 Overview

PrismWeave now has three ways to create releases:

1. **🎯 Auto Release** - Full control over major.minor, automatic patch increment
2. **⚡ Quick Patch** - One-click patch releases with automatic versioning  
3. **🔧 Manual Release** - Traditional tag-based releases (legacy)

## 🎯 Auto Release Workflow

**File**: `.github/workflows/auto-release.yml`

### Features
- ✅ Manual control over major and minor version numbers
- ✅ Automatic patch version increment based on latest release
- ✅ Supports patch, minor, and major release types
- ✅ Updates all package.json files automatically
- ✅ Builds and packages both extension and bookmarklet
- ✅ Creates comprehensive release notes
- ✅ Triggers automatic website deployment

### Usage

1. Go to **Actions** tab in GitHub
2. Select **"Auto Release"** workflow  
3. Click **"Run workflow"**
4. Configure:
   - **Major version**: e.g., `1` 
   - **Minor version**: e.g., `0`
   - **Release type**: `patch`, `minor`, or `major`
   - **Draft**: Create as draft (optional)

### Examples

#### Patch Release (Most Common)
```
Major: 1
Minor: 0  
Type: patch
→ Creates: v1.0.1, v1.0.2, v1.0.3, etc.
```

#### Minor Release 
```
Major: 1
Minor: 1
Type: minor
→ Creates: v1.1.0 (resets patch to 0)
```

#### Major Release
```
Major: 2
Minor: 0
Type: major  
→ Creates: v2.0.0 (resets minor and patch to 0)
```

### How Version Calculation Works

1. **Gets latest tag** matching `v{major}.{minor}.*` pattern
2. **Extracts patch number** from latest tag
3. **Increments patch** by 1 for patch releases
4. **Resets appropriately** for minor/major releases
5. **Updates package.json** files with new version
6. **Creates git tag** and pushes changes

## ⚡ Quick Patch Workflow

**File**: `.github/workflows/quick-patch.yml`

### Features
- ✅ One-click patch releases
- ✅ Automatic version detection and increment
- ✅ Simple release notes
- ✅ Fast deployment (no manual inputs required)
- ✅ Perfect for bug fixes and small updates

### Usage

1. Go to **Actions** tab in GitHub
2. Select **"Quick Patch Release"** workflow
3. Click **"Run workflow"**
4. Optional: Add brief description of changes
5. Click **"Run workflow"** button

### Example Output
```
Current version: 1.0.5
Latest tag: v1.0.7
→ Creates: v1.0.8
```

## 📦 Release Assets

Both workflows create these downloadable assets:

### Browser Extension
- **Filename**: `prismweave-extension-v{version}.zip`
- **Contents**: Complete browser extension ready for developer mode loading
- **Size**: ~500KB

### Bookmarklet  
- **Filename**: `prismweave-bookmarklet-v{version}.zip`
- **Contents**: Bookmarklet files including loader, runtime, and installation guide
- **Size**: ~200KB

## 🌐 Website Integration

### Automatic Updates
- ✅ Website automatically updates when new releases are created
- ✅ Shows latest version number on homepage
- ✅ Bookmarklet files are automatically deployed
- ✅ Installation guides stay current

### Deploy Triggers
The website deployment is triggered by:
- Pushes to main branch  
- New releases (published/created)
- Manual workflow dispatch

## 🔧 Manual Release (Legacy)

**File**: `.github/workflows/create-release.yml`

This is the original tag-based release system that's still available:

```bash
git tag v1.0.10
git push origin v1.0.10
```

## 📋 Version Management Best Practices

### Semantic Versioning
```
v{MAJOR}.{MINOR}.{PATCH}
```

- **MAJOR**: Breaking changes, new architecture
- **MINOR**: New features, backwards compatible  
- **PATCH**: Bug fixes, small improvements

### Recommended Workflow

1. **Daily/Weekly**: Use **Quick Patch** for bug fixes
2. **Monthly**: Use **Auto Release** with `minor` type for feature releases
3. **Quarterly**: Use **Auto Release** with `major` type for major updates

### Version Planning

```
Current: v1.0.15
Next patch: v1.0.16 (Quick Patch)
Next minor: v1.1.0 (Auto Release - minor)  
Next major: v2.0.0 (Auto Release - major)
```

## 🛠️ Troubleshooting

### Version Conflicts
**Error**: "Tag already exists"
**Solution**: Check existing releases, the system prevents duplicates

### Build Failures  
**Error**: Build fails during workflow
**Solution**: Check build logs, ensure dependencies are correct

### Missing Assets
**Error**: ZIP files not created
**Solution**: Verify build completed successfully, check dist/ folder

### Website Not Updating
**Error**: Website shows old version
**Solution**: Check deploy-website workflow, may need manual trigger

## 🎯 Quick Reference

| Task | Workflow | Trigger |
|------|----------|---------|
| Bug fix | Quick Patch | One-click button |
| Feature release | Auto Release (minor) | Manual inputs |
| Breaking changes | Auto Release (major) | Manual inputs |
| Emergency patch | Auto Release (patch) | Manual inputs |

## 🔗 Related Files

- `.github/workflows/auto-release.yml` - Main automatic release workflow
- `.github/workflows/quick-patch.yml` - Quick patch release workflow  
- `.github/workflows/deploy-website.yml` - Website deployment
- `.github/workflows/create-release.yml` - Legacy manual releases
- `package.json` - Root version configuration
- `browser-extension/package.json` - Extension version
- `vscode-extension/package.json` - VS Code extension version

---

**Ready to release?** Use the Quick Patch workflow for your first automatic release! 🚀
