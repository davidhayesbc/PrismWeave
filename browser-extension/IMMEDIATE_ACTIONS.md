# PrismWeave Browser Extension - Immediate Action Items

> **Generated**: July 3, 2025 **Priority**: CRITICAL - Address within 48 hours
> **Goal**: Simplify codebase and eliminate duplicates before expanding test
> coverage

## 🚨 CRITICAL - Immediate Deduplication (Today)

### 1. Remove Duplicate Test Files

**DUPLICATE FOUND**: Two identical git operations test files

```bash
# Verify files are identical
diff src/__tests__/utils/git-operations.test.ts src/__tests__/utils/git-operations-consolidated.test.ts

# If identical, remove the consolidated version
rm src/__tests__/utils/git-operations-consolidated.test.ts

# Run tests to ensure no regressions
npm test
```

**Impact**: Eliminates 804 lines of duplicate code immediately

### 2. Consolidate Test Utilities

**PROBLEM**: Three overlapping test utility files causing confusion

**FILES**:

- `test-utils.ts` (107 lines, 0% coverage)
- `test-utilities.ts` (218 lines, 79.31% coverage)
- `test-logger.ts` (267 lines, 17.52% coverage)

**ACTION**:

1. Keep `test-utilities.ts` as primary (highest coverage)
2. Merge essential functions from `test-utils.ts`
3. Integrate test logging from `test-logger.ts`
4. Update all test imports
5. Remove redundant files

### 3. File Manager Consolidation

**PROBLEM**: Two file managers with 0% coverage

**FILES**:

- `file-manager.ts` (487 lines, 0% coverage)
- `github-file-manager.ts` (unknown size, 0% coverage)

**ACTION**: Audit overlap and consolidate into single, well-tested manager

## ⚠️ HIGH PRIORITY - Console Cleanup (Tomorrow)

### Eliminate Direct Console Usage

**CURRENT**: 20+ instances of direct console.\* calls

**LOCATIONS**:

- `logger.ts` (lines 438, 442) - Replace remaining console.log
- Various test files - Clean up test console references
- Service worker and utilities - Audit for missed console statements

**REPLACEMENT PATTERN**:

```typescript
// Replace:
console.log() → logger.info()
console.error() → logger.error()
console.warn() → logger.warn()
console.debug() → logger.debug()
```

## 📊 COVERAGE PRIORITIES - This Week

### 1. Options Page (0% Coverage) - 584 Lines

**CRITICAL**: Completely untested settings UI

**FOCUS AREAS**:

- Settings form validation
- GitHub token/repository validation
- Chrome storage operations
- Error handling and display

### 2. Popup Component (6.13% Coverage) - 899 Lines

**CRITICAL**: Massive file with minimal testing

**FOCUS AREAS**:

- Page capture workflow
- Tab detection and validation
- Message passing to service worker
- UI state management

### 3. UI Utils (0% Coverage) - 685 Lines

**HIGH PRIORITY**: Zero test coverage

**FOCUS AREAS**:

- DOM manipulation helpers
- Event handling utilities
- Form validation functions

## 🎯 Quick Wins

### Markdown Converter Consolidation

**DUPLICATE FUNCTIONALITY**:

- `markdown-converter.ts` (64.51% coverage)
- `markdown-converter-core.ts` (72.89% coverage)

**ACTION**: Audit and consolidate to single converter

### Performance Monitor Testing

**ZERO COVERAGE**: 180 lines completely untested

**ACTION**: Create basic test suite for timing and memory tracking

## 📋 Implementation Order

### Day 1 (Today):

1. ✅ Remove duplicate git-operations test file
2. ✅ Audit file manager overlap
3. ✅ Start test utility consolidation

### Day 2 (Tomorrow):

1. ✅ Complete console cleanup
2. ✅ Finish test utility consolidation
3. ✅ Start options page testing

### Day 3-5 (This Week):

1. ✅ Options page comprehensive testing
2. ✅ Begin popup component testing
3. ✅ UI utils basic testing

## 🔍 Verification Commands

```bash
# Check for duplicate files
find src -name "*.ts" -exec basename {} \; | sort | uniq -d

# Find remaining console usage
grep -r "console\." src --include="*.ts" | grep -v test

# Run tests with coverage
npm test -- --coverage

# Check for unused imports
npx ts-unused-exports tsconfig.json
```

## 📈 Success Metrics

**TARGET FOR WEEK 1**:

- Remove ALL duplicate files (0 duplicates)
- Reduce console.\* usage to <5 instances
- Achieve 50%+ coverage on Options page
- Start Popup testing (25%+ coverage)
- Overall project coverage: 36.39% → 45%+

---

**Next Update**: July 5, 2025 (End of deduplication phase)
