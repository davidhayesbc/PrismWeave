# PrismWeave Browser Extension - Testing Plan

## Overview

This document outlines a focused testing strategy for the PrismWeave browser extension based on the current implementation. It covers core functionality including settings management, popup validation, content extraction, and service worker operations.

## Testing Framework

- **Framework**: Jest with TypeScript support
- **Coverage Target**: 70% for critical modules
- **Current Status**: 18 tests passing, 2 test suites implemented

---

## Test Status Summary

### ✅ Implemented Tests (21 total)

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
- **B.1.4** ✅ Should return valid when both GitHub token and repository are present
- **B.1.5** ✅ Should return valid when optional settings like defaultFolder are also present
- **B.1.6** ✅ Should handle multiple missing settings
- **B.1.7** ✅ Should handle null settings

#### C. Content Extraction (3 tests) - `content-extractor.test.ts`
- **C.1.1** ✅ Extract main content from article pages
- **C.1.1a** ✅ Extract content from article with multiple content selectors  
- **C.1.1b** ✅ Extract content with custom selectors

---

## Planned Test Suites

### C. Content Extraction - `content-extractor.test.ts` (Priority: High)

**Test Suite**: `ContentExtractor - Core Functionality`

```typescript
describe('ContentExtractor - Core Functionality', () => {
  // Core extraction tests
});
```

**Test Cases Needed:**

1. **Content Identification**
   - **C.1.1** ✅ Extract main content from article pages
   - **C.1.2** ⏳ Extract content from blog posts
   - **C.1.3** ⏳ Handle pages with no clear main content
   - **C.1.4** ⏳ Process single-page applications

2. **Content Cleaning**
   - **C.2.1** Remove unwanted selectors (ads, navigation)
   - **C.2.2** Preserve formatting elements
   - **C.2.3** Handle custom selectors for removal
   - **C.2.4** Clean malformed HTML

3. **Metadata Extraction**
   - **C.3.1** Extract title from various sources
   - **C.3.2** Extract description and keywords
   - **C.3.3** Extract author information
   - **C.3.4** Extract publish date

4. **Content Quality Assessment**
   - **C.4.1** Calculate word count accurately
   - **C.4.2** Estimate reading time
   - **C.4.3** Assess content richness
   - **C.4.4** Detect media content

### D. Service Worker Communication - `service-worker.test.ts` (Priority: Medium)

**Test Suite**: `ServiceWorker - Message Handling`

```typescript
describe('ServiceWorker - Message Handling', () => {
  // Service worker tests
});
```

**Test Cases Needed:**

1. **Message Processing**
   - **D.1.1** Handle GET_SETTINGS message
   - **D.1.2** Handle UPDATE_SETTINGS message
   - **D.1.3** Handle CAPTURE_PAGE message
   - **D.1.4** Return proper error responses

2. **Storage Operations**
   - **D.2.1** Read settings from chrome.storage
   - **D.2.2** Write settings to chrome.storage
   - **D.2.3** Handle storage quota errors
   - **D.2.4** Fallback to local storage

3. **Extension Lifecycle**
   - **D.3.1** Initialize on installation
   - **D.3.2** Handle runtime startup
   - **D.3.3** Cleanup on shutdown

### E. Error Handling - `error-handler.test.ts` (Priority: Medium)

**Test Suite**: `ErrorHandler - Error Processing`

```typescript
describe('ErrorHandler - Error Processing', () => {
  // Error handling tests
});
```

**Test Cases Needed:**

1. **Error Categorization**
   - **E.1.1** Categorize Chrome API errors
   - **E.1.2** Categorize network errors
   - **E.1.3** Categorize validation errors
   - **E.1.4** Handle unknown errors

2. **Error Reporting**
   - **E.2.1** Log errors with context
   - **E.2.2** Send errors to background script
   - **E.2.3** Include stack traces
   - **E.2.4** Sanitize sensitive data

### F. Markdown Conversion - `markdown-converter.test.ts` (Priority: Low)

**Test Suite**: `MarkdownConverter - HTML to Markdown`

**Test Cases Needed:**

1. **HTML Conversion**
   - **F.1.1** Convert basic HTML elements
   - **F.1.2** Handle nested structures
   - **F.1.3** Preserve code blocks
   - **F.1.4** Convert links and images

2. **Frontmatter Generation**
   - **F.2.1** Generate YAML frontmatter
   - **F.2.2** Include metadata fields
   - **F.2.3** Handle special characters
   - **F.2.4** Validate YAML format

---

## Test Implementation Priority

### Phase 1: Critical Core Tests (Week 1)
1. **Content Extraction Tests (C.1.1 - C.4.4)** - Core functionality
2. **Service Worker Tests (D.1.1 - D.2.4)** - Extension communication

### Phase 2: Error Handling (Week 2)
1. **Error Handler Tests (E.1.1 - E.2.4)** - Robust error management

### Phase 3: Markdown Processing (Week 3)
1. **Markdown Converter Tests (F.1.1 - F.2.4)** - Output generation

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

| Component | Target Coverage | Current Coverage |
|-----------|----------------|------------------|
| SettingsManager | 90% | 67% |
| PopupValidation | 85% | 100% |
| ContentExtractor | 80% | 0% |
| ServiceWorker | 75% | 9% |
| ErrorHandler | 70% | 0% |
| MarkdownConverter | 70% | 0% |

**Overall Target**: 70% line coverage

---

## Test Suite Templates

### Content Extractor Test Template

```typescript
// Generated by Copilot
// Content Extractor Tests

import { ContentExtractor } from '../../utils/content-extractor';

describe('ContentExtractor - Core Functionality', () => {
  let extractor: ContentExtractor;

  beforeEach(() => {
    extractor = new ContentExtractor();
  });

  describe('Content Identification', () => {
    test('C.1.1 - Extract main content from article pages', () => {
      // Test article page content extraction
    });

    test('C.1.2 - Extract content from blog posts', () => {
      // Test blog post extraction
    });
  });

  describe('Content Cleaning', () => {
    test('C.2.1 - Remove unwanted selectors', () => {
      // Test ad and navigation removal
    });
  });
});
```

### Service Worker Test Template

```typescript
// Generated by Copilot
// Service Worker Tests

describe('ServiceWorker - Message Handling', () => {
  beforeEach(() => {
    // Mock Chrome APIs
    (global as any).chrome = {
      storage: { sync: { get: jest.fn(), set: jest.fn() } },
      runtime: { onMessage: { addListener: jest.fn() } }
    };
  });

  describe('Message Processing', () => {
    test('D.1.1 - Handle GET_SETTINGS message', async () => {
      // Test settings retrieval
    });
  });
});
```

---

## Implementation Guidelines

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Mock Dependencies**: Use Jest mocks for Chrome APIs and external dependencies
3. **Test Data**: Use realistic test data that represents actual use cases
4. **Error Scenarios**: Test both success and failure paths
5. **Async Testing**: Use async/await for asynchronous operations
6. **Coverage**: Aim for high coverage but focus on critical paths first

## Next Steps

1. Create `content-extractor.test.ts` (highest priority)
2. Create `service-worker.test.ts` for background script testing
3. Add error handling tests for robustness
4. Implement integration tests for component interaction
5. Set up automated test running in CI/CD pipeline
