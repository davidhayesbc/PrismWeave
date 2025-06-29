# PrismWeave Browser Extension - Testing Plan

## Overview

This document outlines a focused testing strategy for the PrismWeave browser
extension based on the current implementation. It covers core functionality
including settings management, popup validation, content extraction, and service
worker operations.

## Testing Framework

- **Framework**: Jest with TypeScript support
- **Coverage Target**: 70% for critical modules
- **Current Status**: 33 tests passing, 5 test suites implemented

---

## Test Status Summary

### ✅ Implemented Tests (48 total)

#### A. Settings Management (11 tests) - `settings-manager.test.ts`

- **A.1.1** ✅ Verify all schema fields have default values
- **A.1.2** ✅ Test loading when storage is empty
- **A.1.3** ✅ Verify schema validation on load
- **A.2.2** ✅ Test saving valid settings
- **A.3.1** ✅ Validate settings with correct types
- **A.3.2** ✅ Validate settings with incorrect types
- **A.4.1** ✅ Handle storage errors gracefully
- **A.4.3** ✅ Reset settings to defaults
- **A.5.1** ✅ Export settings (sanitized)
- **A.6.1** ✅ Import settings successfully
- **A.6.3** ✅ Import invalid JSON fails gracefully

#### B. Popup Settings Validation (7 tests) - `popup-settings-validation.test.ts`

- **B.1.1** ✅ Should return valid when all required settings are present
- **B.1.2** ✅ Should return invalid when GitHub token is missing
- **B.1.3** ✅ Should return invalid when GitHub repo is missing
- **B.1.4** ✅ Should return valid when both GitHub token and repository are
  present
- **B.1.5** ✅ Should return valid when optional settings like defaultFolder are
  also present
- **B.1.6** ✅ Should handle multiple missing settings
- **B.1.7** ✅ Should handle null settings

#### C. Content Extraction (23 tests) - `content-extractor.test.ts`

**Core Content Extraction:**

- **C.1.1** ✅ Extract main content from article pages
- **C.1.2** ✅ Extract content from blog posts
- **C.1.3** ✅ Handle pages with no clear main content

**Content Quality Assessment:**

- **C.4.1** ✅ Calculate word count accurately
- **C.4.2** ✅ Estimate reading time

**Metadata Extraction:**

- **M.1.1** ✅ Extract title from various sources
- **M.1.2** ✅ Extract author information
- **M.1.3** ✅ Extract and process tags

**Utility Methods:**

- **U.1.1** ✅ Extract images with metadata
- **U.1.2** ✅ Extract links with metadata
- **U.1.3** ✅ Analyze page structure
- **U.1.4** ✅ Calculate content quality score

**Edge Cases:**

- **E.1.1** ✅ Handle empty document
- **E.1.2** ✅ Handle malformed HTML
- **E.1.3** ✅ Handle content with only whitespace

#### D. Content Cleaning (9 tests) - `content-extractor-cleaning.test.ts`

- **C.2.1** ✅ Remove unwanted selectors (ads, navigation)
- **C.2.1b** ✅ Remove navigation elements specifically
- **C.2.2** ✅ Preserve formatting elements
- **C.2.3** ✅ Handle custom selectors for removal
- **C.2.4** ✅ Clean malformed HTML
- **D.1.1** ✅ Handle content with mixed wanted and unwanted elements
- **D.1.2** ✅ Preserve content when cleaning options are disabled
- **D.1.3** ✅ Handle deeply nested empty elements
- **D.1.4** ✅ Test individual cleaning method execution

#### E. Line Number Removal (7 tests) - `line-number-removal.test.ts`

- **R.1.1** ✅ Remove line numbers from HTML code blocks
- **R.1.2** ✅ Handle code blocks with various line number formats
- **R.1.3** ✅ Preserve formatting and indentation in code blocks
- **R.1.4** ✅ Handle mixed content with and without line numbers
- **R.1.5** ✅ Handle inline code elements (no line numbers expected)
- **R.1.6** ✅ Process real-world Docker example
- **R.1.7** ✅ Handle empty or malformed code blocks

---

## Planned Test Suites (To Improve Coverage)

### F. Service Worker Communication - `service-worker.test.ts` (Priority: High)

**Test Suite**: `ServiceWorker - Message Handling`

```typescript
describe('ServiceWorker - Message Handling', () => {
  // Service worker tests for 0% → 60% coverage
});
```

**Test Cases Needed:**

1. **Message Processing**

   - **F.1.1** Handle GET_SETTINGS message
   - **F.1.2** Handle UPDATE_SETTINGS message
   - **F.1.3** Handle CAPTURE_PAGE message
   - **F.1.4** Handle TEST_GITHUB_CONNECTION message
   - **F.1.5** Return proper error responses
   - **F.1.6** Handle invalid message types

2. **Storage Operations**

   - **F.2.1** Read settings from chrome.storage
   - **F.2.2** Write settings to chrome.storage
   - **F.2.3** Handle storage quota errors
   - **F.2.4** Fallback when storage unavailable

3. **Extension Lifecycle**
   - **F.3.1** Initialize on installation
   - **F.3.2** Handle runtime startup
   - **F.3.3** Process extension updates

### G. Error Handling - `error-handler.test.ts` (Priority: High)

**Test Suite**: `ErrorHandler - Error Processing`

```typescript
describe('ErrorHandler - Error Processing', () => {
  // Error handling tests for 0% → 70% coverage
});
```

**Test Cases Needed:**

1. **Error Categorization**

   - **G.1.1** Categorize Chrome API errors
   - **G.1.2** Categorize network errors
   - **G.1.3** Categorize validation errors
   - **G.1.4** Handle unknown errors
   - **G.1.5** Process timeout errors

2. **Error Reporting**
   - **G.2.1** Log errors with context
   - **G.2.2** Send errors to background script
   - **G.2.3** Include stack traces
   - **G.2.4** Sanitize sensitive data
   - **G.2.5** Handle error logging failures

### H. Settings Manager Improvements - `settings-manager-extended.test.ts` (Priority: Medium)

**Test Suite**: `SettingsManager - Extended Functionality`

**Test Cases to Reach 90% Coverage:**

1. **Schema Operations**

   - **H.1.1** Get setting definition by key
   - **H.1.2** Get all setting definitions
   - **H.1.3** Validate setting dependencies
   - **H.1.4** Check required dependencies

2. **Advanced Validation**

   - **H.2.1** Validate number ranges (min/max)
   - **H.2.2** Validate pattern matching
   - **H.2.3** Validate enum options
   - **H.2.4** Cross-field validation

3. **Storage Edge Cases**
   - **H.3.1** Handle Chrome storage unavailable
   - **H.3.2** Handle storage corruption
   - **H.3.3** Test storage with large data

### I. Markdown Conversion - `markdown-converter.test.ts` (Priority: Medium)

**Test Suite**: `MarkdownConverter - HTML to Markdown`

```typescript
describe('MarkdownConverter - HTML to Markdown', () => {
  // Markdown conversion tests for 0% → 70% coverage
});
```

**Test Cases Needed:**

1. **HTML Conversion**

   - **I.1.1** Convert basic HTML elements (h1-h6, p, div)
   - **I.1.2** Handle nested structures
   - **I.1.3** Preserve code blocks and syntax highlighting
   - **I.1.4** Convert links and images with proper escaping
   - **I.1.5** Handle lists (ordered, unordered, nested)
   - **I.1.6** Convert tables to markdown
   - **I.1.7** Handle blockquotes and emphasis

2. **Frontmatter Generation**

   - **I.2.1** Generate YAML frontmatter
   - **I.2.2** Include metadata fields (title, date, tags)
   - **I.2.3** Handle special characters in frontmatter
   - **I.2.4** Validate YAML format
   - **I.2.5** Generate consistent field ordering

3. **Content Processing**
   - **I.3.1** Clean up excessive whitespace
   - **I.3.2** Normalize line endings
   - **I.3.3** Handle Unicode and emoji
   - **I.3.4** Process relative URLs to absolute

### J. Git Operations - `git-operations.test.ts` (Priority: Medium)

**Test Suite**: `GitOperations - Repository Management`

```typescript
describe('GitOperations - Repository Management', () => {
  // Git operations tests for 0% → 60% coverage
});
```

**Test Cases Needed:**

1. **GitHub API Integration**

   - **J.1.1** Authenticate with GitHub token
   - **J.1.2** Validate repository access
   - **J.1.3** Test connection with invalid credentials
   - **J.1.4** Handle API rate limiting
   - **J.1.5** Process network timeouts

2. **File Operations**

   - **J.2.1** Create new files in repository
   - **J.2.2** Update existing files
   - **J.2.3** Handle file conflicts
   - **J.2.4** Generate appropriate commit messages
   - **J.2.5** Batch multiple file operations

3. **Error Handling**
   - **J.3.1** Handle repository not found
   - **J.3.2** Handle insufficient permissions
   - **J.3.3** Handle large file uploads
   - **J.3.4** Retry failed operations

### K. File Manager - `file-manager.test.ts` (Priority: Low)

**Test Suite**: `FileManager - File Operations`

**Test Cases Needed:**

1. **File Path Generation**

   - **K.1.1** Generate filenames from metadata
   - **K.1.2** Handle special characters in filenames
   - **K.1.3** Ensure unique filenames
   - **K.1.4** Apply naming patterns correctly

2. **Content Organization**
   - **K.2.1** Determine folder from content type
   - **K.2.2** Auto-categorize content
   - **K.2.3** Handle custom folder assignments
   - **K.2.4** Validate folder names

### L. Logger - `logger.test.ts` (Priority: Low)

**Test Suite**: `Logger - Debugging and Monitoring`

**Test Cases Needed:**

1. **Log Level Management**

   - **L.1.1** Filter by log level (debug, info, warn, error)
   - **L.1.2** Configure log levels dynamically
   - **L.1.3** Handle console availability

2. **Log Formatting**
   - **L.2.1** Format messages with timestamps
   - **L.2.2** Include context information
   - **L.2.3** Handle object serialization

### M. UI Utils - `ui-utils.test.ts` (Priority: Low)

**Test Suite**: `UIUtils - User Interface Helpers`

**Test Cases Needed:**

1. **DOM Manipulation**

   - **M.1.1** Show/hide notification messages
   - **M.1.2** Update progress indicators
   - **M.1.3** Validate form inputs

2. **User Feedback**
   - **M.2.1** Display success messages
   - **M.2.2** Show error notifications
   - **M.2.3** Handle loading states

---

## Test Implementation Priority

### Phase 1: Critical Coverage Gaps (Week 1)

**Target: Increase overall coverage from 18% to 40%**

1. **Service Worker Tests (F.1.1 - F.3.3)** - Currently 0% coverage

   - Highest impact: Core extension functionality
   - 339 uncovered lines in service-worker.ts
   - Focus on message handling and basic lifecycle

2. **Error Handler Tests (G.1.1 - G.2.5)** - Currently 0% coverage

   - Critical for production reliability
   - 148 uncovered lines in error-handler.ts
   - Essential for debugging user issues

3. **Settings Manager Extended (H.1.1 - H.3.3)** - Improve from 67% to 90%
   - Already well tested, need edge cases
   - ~20 additional lines to cover

### Phase 2: Core Functionality (Week 2)

**Target: Increase overall coverage from 40% to 55%**

1. **Markdown Converter Tests (I.1.1 - I.3.4)** - Currently 0% coverage

   - Output generation critical for user experience
   - 225 uncovered lines across converter files
   - Focus on HTML → Markdown accuracy

2. **Git Operations Tests (J.1.1 - J.3.4)** - Currently 0% coverage
   - Core feature for document storage
   - 673 uncovered lines in git-operations.ts
   - Test GitHub API integration without real requests

### Phase 3: Supporting Features (Week 3)

**Target: Reach overall 60%+ coverage**

1. **File Manager Tests (K.1.1 - K.2.4)** - Currently 0% coverage

   - 382 uncovered lines in file-manager.ts
   - Focus on filename generation and organization

2. **Logger & UI Utils Tests (L.1.1 - M.2.3)** - Currently 0% coverage
   - 865 uncovered lines across logger.ts and ui-utils.ts
   - Lower priority but needed for comprehensive coverage

---

## Immediate Actions Recommended

### 1. Service Worker Testing Strategy

The service worker has 0% coverage and is critical. Start with:

```typescript
// service-worker.test.ts - Basic structure
describe('ServiceWorker - Core Functionality', () => {
  test('F.1.1 - Handle GET_SETTINGS message', async () => {
    // Mock chrome APIs and test message handling
  });

  test('F.1.2 - Handle CAPTURE_PAGE message', async () => {
    // Test capture workflow without actual browser interaction
  });
});
```

### 2. Error Handler Priority

Error handling has no tests but is essential for debugging:

```typescript
// error-handler.test.ts - Start here
describe('ErrorHandler - Error Processing', () => {
  test('G.1.1 - Categorize Chrome API errors', () => {
    // Test error classification logic
  });

  test('G.2.1 - Log errors with context', () => {
    // Verify logging includes sufficient debugging info
  });
});
```

### 3. Settings Manager Completion

Already at 67% - finish the remaining edge cases:

```typescript
// settings-manager-extended.test.ts
describe('SettingsManager - Edge Cases', () => {
  test('H.3.1 - Handle Chrome storage unavailable', async () => {
    // Test graceful fallback when storage fails
  });
});
```

---

## Test Data and Fixtures

### HTML Test Fixtures

- **Article Page**: Standard blog/news article
- **E-commerce Page**: Product listings with ads
- **Documentation Page**: Technical documentation
- **Social Media Page**: Timeline/feed structure

### Settings Test Data

- **Valid Settings**: Complete configuration
- **Invalid Settings**: Type mismatches, missing required fields
- **Edge Cases**: Empty values, extremely long strings

### Error Scenarios

- **Network Failures**: Timeout, connection refused
- **Storage Failures**: Quota exceeded, permission denied
- **Validation Failures**: Schema violations, type errors

---

## Running Tests

```bash
# Run all tests
npm test

# Run specific test suite
npm test -- --testNamePattern="SettingsManager"

# Run with coverage
npm test -- --coverage

# Watch mode for development
npm test -- --watch
```

---

## Coverage Goals

| Component         | Target Coverage | Current Coverage | Status |
| ----------------- | --------------- | ---------------- | ------ |
| SettingsManager   | 90%             | 67%              | ⚠️     |
| PopupValidation   | 85%             | 100%             | ✅     |
| ContentExtractor  | 80%             | 79%              | ✅     |
| ServiceWorker     | 60%             | 0%               | ❌     |
| ErrorHandler      | 70%             | 0%               | ❌     |
| MarkdownConverter | 70%             | 0%               | ❌     |
| GitOperations     | 60%             | 0%               | ❌     |
| FileManager       | 60%             | 0%               | ❌     |
| Logger            | 50%             | 0%               | ❌     |
| UI Utils          | 50%             | 0%               | ❌     |

**Overall Target**: 60% line coverage (current: 18.4%) **Priority**: Focus on
high-impact, low-coverage modules

---

## High-Priority Test Templates

### Service Worker Test Template

```typescript
// Generated by Copilot
// Service Worker Tests - Critical for 0% → 60% coverage improvement

import { jest } from '@jest/globals';

describe('ServiceWorker - Message Handling', () => {
  let mockChrome: any;
  let mockSettingsManager: any;

  beforeEach(() => {
    // Mock Chrome APIs for service worker testing
    mockChrome = {
      storage: {
        sync: {
          get: jest.fn(),
          set: jest.fn(),
        },
      },
      runtime: {
        onMessage: { addListener: jest.fn() },
        onInstalled: { addListener: jest.fn() },
        lastError: null,
      },
      tabs: {
        sendMessage: jest.fn(),
        query: jest.fn(),
      },
    };
    (global as any).chrome = mockChrome;
  });

  describe('Message Processing', () => {
    test('F.1.1 - Handle GET_SETTINGS message', async () => {
      // Test settings retrieval through message passing
      const mockSettings = { githubToken: 'test', githubRepo: 'user/repo' };
      mockChrome.storage.sync.get.mockImplementation((keys, callback) => {
        callback({ prismWeaveSettings: mockSettings });
      });

      // Import and test service worker message handler
      // This tests the actual handleMessage function
    });

    test('F.1.2 - Handle CAPTURE_PAGE message', async () => {
      // Test capture workflow initiation
      // Mock content script injection and content extraction
    });

    test('F.1.3 - Handle invalid message types', async () => {
      // Test error handling for unknown message types
    });
  });

  describe('Storage Operations', () => {
    test('F.2.1 - Read settings from chrome.storage', async () => {
      // Test storage read operations with various data scenarios
    });

    test('F.2.3 - Handle storage quota errors', async () => {
      // Mock quota exceeded error and test graceful handling
      mockChrome.runtime.lastError = { message: 'Quota exceeded' };
    });
  });
});
```

### Error Handler Test Template

```typescript
// Generated by Copilot
// Error Handler Tests - Critical for debugging and reliability

import { ErrorHandler } from '../../utils/error-handler';

describe('ErrorHandler - Error Processing', () => {
  let errorHandler: ErrorHandler;
  let consoleSpy: jest.SpyInstance;

  beforeEach(() => {
    errorHandler = new ErrorHandler();
    consoleSpy = jest.spyOn(console, 'error').mockImplementation();
  });

  afterEach(() => {
    consoleSpy.mockRestore();
  });

  describe('Error Categorization', () => {
    test('G.1.1 - Categorize Chrome API errors', () => {
      const chromeError = new Error('Extension context invalidated');
      chromeError.name = 'ChromeExtensionError';

      const categorized = errorHandler.categorizeError(chromeError);

      expect(categorized.category).toBe('CHROME_API');
      expect(categorized.severity).toBe('HIGH');
      expect(categorized.context).toContain('Extension context');
    });

    test('G.1.2 - Categorize network errors', () => {
      const networkError = new Error('Failed to fetch');
      networkError.name = 'NetworkError';

      const categorized = errorHandler.categorizeError(networkError);

      expect(categorized.category).toBe('NETWORK');
      expect(categorized.severity).toBe('MEDIUM');
      expect(categorized.retryable).toBe(true);
    });

    test('G.1.4 - Handle unknown errors', () => {
      const unknownError = new Error('Something unexpected');

      const categorized = errorHandler.categorizeError(unknownError);

      expect(categorized.category).toBe('UNKNOWN');
      expect(categorized.severity).toBe('MEDIUM');
    });
  });

  describe('Error Reporting', () => {
    test('G.2.1 - Log errors with context', () => {
      const error = new Error('Test error');
      const context = {
        operation: 'content-extraction',
        url: 'https://example.com',
      };

      errorHandler.logError(error, context);

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Test error'),
        expect.objectContaining(context)
      );
    });

    test('G.2.4 - Sanitize sensitive data', () => {
      const error = new Error('Auth failed');
      const sensitiveContext = {
        githubToken: 'secret-token',
        apiKey: 'api-secret',
        publicInfo: 'safe-data',
      };

      errorHandler.logError(error, sensitiveContext);

      const logCall = consoleSpy.mock.calls[0];
      const loggedData = JSON.stringify(logCall);

      expect(loggedData).not.toContain('secret-token');
      expect(loggedData).not.toContain('api-secret');
      expect(loggedData).toContain('safe-data');
      expect(loggedData).toContain('[REDACTED]');
    });
  });
});
```

### Settings Manager Extended Template

```typescript
// Generated by Copilot
// Settings Manager Extended Tests - Improve from 67% to 90% coverage

import { SettingsManager } from '../../utils/settings-manager';

describe('SettingsManager - Extended Functionality', () => {
  let settingsManager: SettingsManager;
  let mockChrome: any;

  beforeEach(() => {
    mockChrome = {
      storage: { sync: { get: jest.fn(), set: jest.fn() } },
      runtime: { lastError: null },
    };
    (global as any).chrome = mockChrome;
    settingsManager = new SettingsManager();
  });

  describe('Schema Operations', () => {
    test('H.1.1 - Get setting definition by key', () => {
      const definition = settingsManager.getSettingDefinition('githubToken');

      expect(definition).toBeDefined();
      expect(definition?.type).toBe('string');
      expect(definition?.sensitive).toBe(true);
      expect(definition?.description).toContain('GitHub');
    });

    test('H.1.2 - Get all setting definitions', () => {
      const definitions = settingsManager.getAllSettingDefinitions();

      expect(Object.keys(definitions)).toContain('githubToken');
      expect(Object.keys(definitions)).toContain('githubRepo');
      expect(Object.keys(definitions)).toContain('defaultFolder');
      expect(Object.keys(definitions).length).toBeGreaterThan(10);
    });

    test('H.1.4 - Check required dependencies', async () => {
      const settings = { customFolder: 'my-folder' }; // Missing defaultFolder: 'custom'

      const dependencies =
        await settingsManager.checkRequiredDependencies(settings);

      expect(dependencies).toHaveLength(0); // customFolder doesn't have requirements
    });
  });

  describe('Advanced Validation', () => {
    test('H.2.2 - Validate pattern matching', () => {
      const validRepo = { githubRepo: 'user/repo-name' };
      const invalidRepo = { githubRepo: 'invalid-format' };

      const validResult = settingsManager.validateSettings(validRepo);
      const invalidResult = settingsManager.validateSettings(invalidRepo);

      expect(validResult.isValid).toBe(true);
      expect(invalidResult.isValid).toBe(false);
      expect(invalidResult.errors[0]).toContain('pattern');
    });

    test('H.2.3 - Validate enum options', () => {
      const validFolder = { defaultFolder: 'tech' };
      const invalidFolder = { defaultFolder: 'invalid-option' };

      const validResult = settingsManager.validateSettings(validFolder);
      const invalidResult = settingsManager.validateSettings(invalidFolder);

      expect(validResult.isValid).toBe(true);
      expect(invalidResult.isValid).toBe(false);
      expect(invalidResult.errors[0]).toContain('must be one of');
    });
  });

  describe('Storage Edge Cases', () => {
    test('H.3.1 - Handle Chrome storage unavailable', async () => {
      // Simulate Chrome storage API not available
      (global as any).chrome = undefined;

      await expect(settingsManager.getSettings()).rejects.toThrow(
        'Chrome storage API not available'
      );
    });

    test('H.3.2 - Handle storage corruption', async () => {
      // Mock corrupted JSON in storage
      mockChrome.storage.sync.get.mockImplementation((keys, callback) => {
        callback({ prismWeaveSettings: 'invalid-json-string' });
      });

      const settings = await settingsManager.getSettings();

      // Should return empty object when storage is corrupted
      expect(settings).toEqual({});
    });
  });
});
```

---

## Implementation Guidelines

1. **Test Isolation**: Each test should be independent and not rely on other
   tests
2. **Mock Dependencies**: Use Jest mocks for Chrome APIs and external
   dependencies
3. **Test Data**: Use realistic test data that represents actual use cases
4. **Error Scenarios**: Test both success and failure paths
5. **Async Testing**: Use async/await for asynchronous operations
6. **Coverage**: Aim for high coverage but focus on critical paths first

## Next Steps - Prioritized Action Plan

### Immediate (This Week)

1. **Create `service-worker.test.ts`** (CRITICAL - 0% coverage)

   - Use template above to test message handling
   - Focus on GET_SETTINGS and CAPTURE_PAGE messages
   - Target: 30-40% service worker coverage

2. **Create `error-handler.test.ts`** (HIGH - 0% coverage)

   - Test error categorization logic
   - Verify sensitive data sanitization
   - Target: 60%+ error handler coverage

3. **Extend settings manager tests** (MEDIUM - improve 67% → 90%)
   - Add `settings-manager-extended.test.ts`
   - Test edge cases and schema operations
   - Complete validation coverage

### Short Term (Next 2 Weeks)

4. **Create `markdown-converter.test.ts`** (HIGH - 0% coverage)

   - Test HTML → Markdown conversion accuracy
   - Verify frontmatter generation
   - Target: 70%+ converter coverage

5. **Create `git-operations.test.ts`** (MEDIUM - 0% coverage)
   - Mock GitHub API calls for testing
   - Test file operations and error handling
   - Target: 50%+ git operations coverage

### Medium Term (Month 2)

6. **Add integration tests** for complete workflows
7. **Performance tests** for large document processing
8. **Cross-browser compatibility tests** for manifest differences
9. **Memory leak tests** for long-running operations

### Success Metrics

- **Week 1 Target**: Overall coverage 18% → 35%
- **Week 2 Target**: Overall coverage 35% → 50%
- **Month 1 Target**: Overall coverage 50% → 60%
- **All Critical Paths**: Service worker, error handling, content extraction
  covered
- **Production Ready**: Sufficient test coverage for confident releases

### Tools and Setup

- Continue using Jest with TypeScript
- Maintain current DOM testing with jsdom
- Add GitHub API mocking for git operations tests
- Consider adding e2e tests with Puppeteer for complex scenarios
