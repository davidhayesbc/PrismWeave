# PrismWeave Browser Extension: Dead Code Review & Removal Plan

## 1. File Inventory

- [x] src/background/service-worker.ts
- [x] src/popup/popup.ts ✅ KEEP - Active popup interface
- [x] src/types/index.ts
- [x] src/options/options.ts ✅ KEEP - Active options page (manifest.json +
      service worker integration)
- [x] src/utils/content-capture-service.ts ✅ KEEP - Core service for content
      extraction, processing, and GitHub operations (active in service worker)
- [x] src/utils/content-cleaner.ts - **KEEP** - Used by content-extractor.ts
      which is imported in content-script.ts and tested
- [x] src/utils/content-extractor.ts - **KEEP** - Main content extraction
      orchestrator used in content-script.ts and comprehensively tested
- [x] src/utils/content-quality-analyzer.ts - **KEEP** - Used by
      content-extractor.ts for content quality assessment
- [x] src/utils/content-selector-strategies.ts - **KEEP** -
      ContentSelectorManager used by content-extractor.ts for content selection
- [x] src/utils/error-handler.ts - **REMOVE** - Only used in its own test file,
      no production usage found
- [x] src/utils/file-manager.ts - **KEEP** - Used by ContentCaptureService for
      GitHub operations and file management
- [x] src/utils/global-types.ts - **KEEP** - Provides global type definitions
      and getGlobalScope() used by logger, ui-utils, shared-utils, and
      performance-monitor
- [x] src/utils/log-config.ts - **KEEP** - Used by logger.ts for centralized
      logging configuration
- [x] src/utils/logger.ts - **KEEP** - Core logging utility used throughout the
      entire extension (20+ imports)
- [x] src/utils/markdown-converter.ts - **KEEP** - Browser-specific markdown
      converter adapter with comprehensive test coverage
- [x] src/utils/markdown-converter-core.ts - **KEEP** - Base class extended by
      MarkdownConverter, provides core conversion logic and interfaces used in
      production
- [x] src/utils/markdown/index.ts - **REMOVE** - Re-export index file with no
      actual imports in production code
- [x] src/utils/metadata-extractor.ts - **REMOVE** - Only used by
      ContentExtractor which is not used in production code
- [ ] src/utils/performance-monitor.ts
- [ ] src/utils/settings-manager.ts
- [ ] src/utils/shared-utils.ts
- [ ] src/utils/test-utilities.ts
- [ ] src/utils/ui-utils.ts

## 2. Review Process for Each File

### A. For Each Production Code File

1. [ ] **Enumerate all exported functions, classes, constants, and interfaces.**
2. [ ] **For each export:**

- [ ] Search for all references in the codebase (including other production
      files and test files).
- [ ] If the export is only referenced in test files (or not at all), mark it as
      unused.
- [ ] If the export is referenced in production code, keep it.

3. [ ] **For each non-exported function/class:**

- [ ] Check if it is called anywhere in the file or from other files.
- [ ] If only called by tests, mark as unused.

4. [ ] **Remove all unused code.**
5. [ ] **If a file becomes empty after removals, delete it.**

### B. For Each Test File

1. [ ] **Identify all tests and helper functions.**
2. [ ] **For each test:**

- [ ] Determine if it tests only unused code (i.e., code not called by
      production).
- [ ] If so, mark the test for removal.

3. [ ] **Remove all tests and helpers that only exercise unused code.**
4. [ ] **If the test file becomes empty, delete it.**

## 3. Special Considerations

- [ ] **Mocks:** If a mock is only used for testing unused code, remove the
      mock.
- [ ] **Type Definitions:** Interfaces/types only used by unused code should
      also be removed.
- [ ] **Logger/Debug Utilities:** If debug or logger helpers are only referenced
      in tests, remove them.
- [ ] **Component/Feature Flags:** Remove any feature toggles or config entries
      that are only used by unused code.

## 4. Validation

- [ ] After each removal, run the build and all remaining tests to ensure no
      accidental breakage.
- [ ] Commit changes with clear messages indicating dead code removal.

## 5. Documentation

- [ ] Document all major removals in a `DEAD_CODE_REMOVAL.md` (optional) for
      future reference.

---

**Next Steps:**

- [ ] Begin with a file inventory and proceed file-by-file as outlined above.
- [ ] For each file, document what was removed and why (in commit messages or a
      summary log).
