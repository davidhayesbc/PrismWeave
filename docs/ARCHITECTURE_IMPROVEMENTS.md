# PrismWeave Architecture Improvement Plan

**Date:** January 26, 2026  
**Status:** Implementation in Progress

## Executive Summary

This document outlines improvements to the PrismWeave solution structure to enhance maintainability, build consistency, and developer experience.

## Current Structure Analysis

### Strengths
✅ Clear component separation (browser-extension, CLI, ai-processing, visualization, website)  
✅ Docker-based development environment with hot-reload  
✅ Comprehensive testing infrastructure (Jest, pytest)  
✅ Good documentation per component  
✅ Aspire orchestration with OpenTelemetry integration

### Areas for Improvement

#### 1. Build System
**Issue:** Complex build.js script that doesn't fully leverage npm workspaces  
**Impact:** Slow builds, dependency duplication, unclear build order  
**Priority:** HIGH

#### 2. Workspace Configuration
**Issue:** Only browser-extension in workspaces; CLI, visualization, website excluded  
**Impact:** Dependency duplication, inconsistent tooling  
**Priority:** HIGH

#### 3. TypeScript Configuration  
**Issue:** Inconsistent tsconfig settings across components  
**Impact:** Different compilation behavior, no project references  
**Priority:** MEDIUM

#### 4. Dependency Management
**Issue:** Shared dependencies (TypeScript, Jest, esbuild) duplicated  
**Impact:** Larger install size, version drift, maintenance overhead  
**Priority:** MEDIUM

#### 5. Shared Code Utilization
**Issue:** packages/shared exists but underutilized  
**Impact:** Code duplication between components  
**Priority:** LOW

## Improvement Roadmap

### Phase 1: Build System Modernization (PRIORITY)

**Goals:**
- Consolidate npm workspace configuration
- Create unified build orchestration
- Establish proper TypeScript project references
- Streamline dependency management

**Tasks:**
1. ✅ Update root package.json to include all TypeScript/Node.js components in workspaces
2. ✅ Create shared tsconfig.base.json for common settings
3. ✅ Add TypeScript project references between components
4. ✅ Simplify build.js to leverage workspace scripts
5. ✅ Hoist common dev dependencies to root

### Phase 2: Testing Infrastructure (MEDIUM)

**Goals:**
- Unified test running
- Consistent coverage reporting
- Integration test framework

**Tasks:**
1. ✅ Create root-level test script that runs all component tests
2. ✅ Add unified coverage reporting
3. ⏭️ Set up integration test suite (deferred - requires more planning)
4. ✅ Add pre-commit hooks for testing

### Phase 3: Developer Experience (LOW)

**Goals:**
- Faster builds
- Better error messages
- Simplified setup

**Tasks:**
1. ✅ Add turbo or nx for build caching (optional - add if needed)
2. ✅ Improve error handling in build scripts
3. ✅ Create developer setup scripts
4. ✅ Document architecture decisions

## Implementation Plan

### Step 1: Workspace Consolidation
- Update package.json workspaces array
- Move common dependencies to root
- Test: `npm install` completes successfully

### Step 2: TypeScript Configuration
- Create tsconfig.base.json
- Update component tsconfig.json files to extend base
- Add project references
- Test: All TypeScript builds complete successfully

### Step 3: Build Simplification
- Refactor build.js to use workspace scripts
- Add individual build targets
- Test: `npm run build` works for all components

### Step 4: Testing Unification
- Add root test scripts
- Configure coverage aggregation
- Test: All test suites pass

### Step 5: Documentation
- Update README with new build process
- Add architecture decision records
- Create development guide

## Success Criteria

- [ ] All components build successfully with simplified commands
- [ ] Test coverage aggregated across all components
- [ ] Build time reduced by at least 20%
- [ ] Developer setup time reduced from 15min to 5min
- [ ] No duplicate dependencies in package-lock.json
- [ ] Documentation updated and accurate

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing builds | HIGH | Implement incrementally, test at each step |
| Version conflicts in hoisted deps | MEDIUM | Use exact versions, test thoroughly |
| Developer confusion | LOW | Update docs, provide migration guide |

## Next Steps

1. Review and approve this plan
2. Create feature branch: `feature/architecture-improvements`
3. Implement Phase 1 step-by-step
4. Test thoroughly at each step
5. Merge to main once validated

---

**Questions/Feedback:** Open GitHub issue or discuss in team meeting
