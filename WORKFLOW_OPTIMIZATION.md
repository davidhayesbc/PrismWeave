# GitHub Actions Workflow Optimization

## 🔍 Problem Identified

Previously, multiple workflows were triggering on the same events, causing redundant builds:

- `ci-cd.yml` - Main comprehensive CI/CD (triggered on push to main/develop)
- `vscode-extension.yml` - VS Code extension build (also triggered on push to main/develop)
- `quick-test.yml` - Quick test suite (also triggered on push to main/develop)

This resulted in **3 parallel builds** running simultaneously on every commit, wasting CI minutes and causing confusion.

## ✅ Solution Implemented

### 1. **Main CI/CD Pipeline** (`ci-cd.yml`)
- **Triggers**: All pushes and PRs to main/develop branches
- **Purpose**: Comprehensive testing, building, and validation
- **Status**: ✅ Primary workflow - runs on every commit

### 2. **VS Code Extension Build** (`vscode-extension.yml`) 
- **Triggers**: Only when `vscode-extension/**` files are modified
- **Purpose**: Cross-platform ONNX Runtime compatibility testing
- **Status**: ✅ Optimized - runs only when relevant files change

### 3. **Quick Tests** (`quick-test.yml`)
- **Triggers**: Manual only (`workflow_dispatch`) or draft PRs
- **Purpose**: Quick feedback during development
- **Status**: ✅ Optimized - no longer conflicts with main CI/CD

### 4. **Release Workflows**
- `auto-release.yml` - Manual trigger only ✅
- `quick-patch.yml` - Manual trigger only ✅
- `create-release.yml` - Manual trigger only ✅
- `deploy-website.yml` - Triggers on releases and tags ✅

## 🚀 Benefits

1. **Reduced CI Minutes**: Only one comprehensive build runs per commit
2. **Faster Feedback**: No competing workflows
3. **Clear Purpose**: Each workflow has a distinct role
4. **Better Performance**: Parallel jobs within workflows, not parallel workflows
5. **Easier Debugging**: Clear which workflow failed and why

## 📋 Workflow Triggers Summary

| Workflow | Push to main/develop | PR | VS Code files only | Manual | Release/Tag |
|----------|---------------------|----|--------------------|--------|-------------|
| ci-cd.yml | ✅ | ✅ | ❌ | ✅ | ❌ |
| vscode-extension.yml | ✅* | ✅* | ✅ | ✅ | ❌ |
| quick-test.yml | ❌ | ✅** | ❌ | ✅ | ❌ |
| auto-release.yml | ❌ | ❌ | ❌ | ✅ | ❌ |
| quick-patch.yml | ❌ | ❌ | ❌ | ✅ | ❌ |
| deploy-website.yml | ❌ | ❌ | ❌ | ✅ | ✅ |

*Only when `vscode-extension/**` files change  
**Only for draft PRs (optional)

## 🎯 Usage Guidelines

### For Regular Development:
- **Commit to main/develop**: Only `ci-cd.yml` runs (comprehensive testing)
- **Modify VS Code extension**: Both `ci-cd.yml` and `vscode-extension.yml` run
- **Create PR**: `ci-cd.yml` runs for validation

### For Quick Testing:
- Use **"Quick Tests"** workflow manually when you need fast feedback
- Use **VS Code Extension Build** manually for ONNX Runtime testing

### For Releases:
- Use **"Auto Release"** for version bumping and automated releases
- Use **"Quick Patch"** for immediate hotfixes
- Website deploys automatically after releases

## 🔧 Future Optimizations

Consider these additional optimizations:

1. **Path-based triggers**: Add path filters to main CI/CD for different components
2. **Conditional jobs**: Skip jobs based on changed files
3. **Caching**: Improve dependency caching between jobs
4. **Matrix optimization**: Reduce matrix combinations where appropriate

## 📊 Expected Results

- **Before**: ~15-20 CI minutes per commit (3 workflows × 5-7 minutes each)
- **After**: ~5-7 CI minutes per commit (1 comprehensive workflow)
- **Savings**: 60-70% reduction in CI resource usage

---

*Last updated: August 13, 2025*
