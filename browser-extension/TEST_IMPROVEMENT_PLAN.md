# PrismWeave Browser Extension - Test Improvement Plan

## Overview

**Current Status**: 135 passing tests, 24.08% coverage  
**Target**: 70%+ coverage with improved test quality  
**Focus**: Test real code instead of mocks, reduce duplication, improve
reliability

---

## Phase 1: Consolidate and Reduce Duplication 🔄

### Settings Manager Test Consolidation

- [ ] **Merge settings manager test files**
  - [ ] Combine `settings-manager.test.ts` and
        `settings-manager-extended.test.ts`
  - [ ] Remove duplicate test cases (schema validation, load/save operations)
  - [ ] Keep only comprehensive tests for each feature
  - [ ] Consolidate mock setup into single beforeEach block
  - **Impact**: Reduce ~20 duplicate tests, improve maintainability

### Content Extractor Test Consolidation

- [ ] **Merge content extractor test files**
  - [ ] Combine `content-extractor.test.ts` and
        `content-extractor-cleaning.test.ts`
  - [ ] Remove overlapping test scenarios (malformed HTML handling)
  - [ ] Organize into logical test suites by functionality
  - [ ] Use parameterized tests for similar scenarios
  - **Impact**: Reduce ~15 duplicate tests, better organization

### Test Helper Enhancement

- [ ] **Improve test helper utilities**
  - [ ] Create specific Chrome API mock factories (reduce repetition)
  - [ ] Add realistic test data generators (HTML structures, settings)
  - [ ] Create reusable DOM setup utilities
  - [ ] Add performance testing helpers
  - **Impact**: Reduce boilerplate code across all tests

---

## Phase 2: Test Real Code Instead of Mocks 🎯

### Service Worker Real Implementation Testing (CRITICAL - 0% Coverage)

- [ ] **Replace mock service worker with real implementation tests**

  - [ ] Test actual `handleMessage()` function from service worker
  - [ ] Test real Chrome storage integration with actual storage calls
  - [ ] Test real GitHub API error scenarios (network failures, auth errors)
  - [ ] Test actual extension lifecycle events (install, update, startup)
  - [ ] Test real message validation and error handling
  - **Impact**: +25% coverage, critical extension functionality tested

- [ ] **Service worker storage operations**
  - [ ] Test real Chrome storage quota handling
  - [ ] Test storage corruption recovery
  - [ ] Test concurrent storage operations
  - [ ] Test storage fallback mechanisms (sync → local)
  - **Impact**: +10% coverage, robust storage handling

### Content Script Integration Testing (CRITICAL - 0% Coverage)

- [ ] **Add real content script functionality tests**

  - [ ] Test actual DOM content extraction with real HTML
  - [ ] Test real markdown conversion using actual Turndown library
  - [ ] Test actual Chrome message passing between content script and background
  - [ ] Test real page analysis and content scoring algorithms
  - [ ] Test actual image and link extraction from DOM
  - **Impact**: +20% coverage, core extraction functionality tested

- [ ] **Content script DOM interaction**
  - [ ] Test real DOM manipulation and element selection
  - [ ] Test content quality scoring with actual algorithms
  - [ ] Test page structure analysis with real HTML documents
  - [ ] Test error handling for malformed DOM structures
  - **Impact**: +15% coverage, reliable content extraction

### Error Handler Real Logic Testing

- [ ] **Replace mock error categorization with real logic**
  - [ ] Test actual error type detection algorithms
  - [ ] Test real Chrome API error handling and categorization
  - [ ] Test actual user notification systems
  - [ ] Test real error logging and reporting mechanisms
  - [ ] Test error sanitization for sensitive data
  - **Impact**: +8% coverage, proper error handling verification

---

## Phase 3: Improve Test Quality and Coverage 📈

### Background Script Testing (0% Coverage)

- [ ] **Add background script real functionality tests**
  - [ ] Test actual service worker initialization and lifecycle
  - [ ] Test real Chrome extension event handling
  - [ ] Test actual GitHub API integration (with mocked network calls)
  - [ ] Test real capture workflow end-to-end
  - **Impact**: +12% coverage, extension lifecycle reliability

### Options and Popup UI Testing (0% Coverage)

- [ ] **Add UI component testing**
  - [ ] Test actual options page form validation and submission
  - [ ] Test real popup interactions and state management
  - [ ] Test actual settings save/load workflows
  - [ ] Test real error display and user feedback
  - **Impact**: +10% coverage, UI reliability

### Integration and End-to-End Testing

- [ ] **Add component interaction tests**
  - [ ] Test message flow: popup → service worker → content script
  - [ ] Test complete capture workflow: trigger → extract → convert → save
  - [ ] Test settings propagation across all components
  - [ ] Test error handling across component boundaries
  - **Impact**: +5% coverage, workflow reliability

---

## Phase 4: Advanced Testing and Optimization 🚀

### Performance Testing

- [ ] **Add performance benchmarks**
  - [ ] Test content extraction performance with large documents
  - [ ] Test memory usage during batch operations
  - [ ] Test markdown conversion speed benchmarks
  - [ ] Test storage operation performance limits
  - **Impact**: Performance regression prevention

### Cross-Browser and Edge Case Testing

- [ ] **Enhance edge case coverage**
  - [ ] Test with real website HTML structures (Wikipedia, Medium, etc.)
  - [ ] Test Chrome vs Edge API differences
  - [ ] Test extension in incognito mode
  - [ ] Test with disabled JavaScript content
  - **Impact**: Better real-world reliability

### Mock Reduction and Real API Testing

- [ ] **Minimize unnecessary mocking**
  - [ ] Use real DOM APIs where possible (jsdom)
  - [ ] Use real Turndown library for markdown conversion
  - [ ] Use real localStorage/Chrome storage APIs in tests
  - [ ] Mock only external network calls and Chrome extension APIs
  - **Impact**: More realistic test scenarios

---

## Implementation Priority and Timeline

### Week 1: Foundation (Phase 1)

**Priority**: HIGH - Reduces maintenance burden

- [ ] Consolidate settings manager tests
- [ ] Consolidate content extractor tests
- [ ] Enhance test helpers
- **Expected Coverage**: 24% → 28% (cleanup and organization)

### Week 2: Critical Coverage (Phase 2a)

**Priority**: CRITICAL - Major coverage gaps

- [ ] Service worker real implementation testing
- [ ] Content script integration testing
- **Expected Coverage**: 28% → 55% (major functionality)

### Week 3: Core Components (Phase 2b)

**Priority**: HIGH - Important functionality

- [ ] Error handler real logic testing
- [ ] Background script testing
- **Expected Coverage**: 55% → 65% (approaching target)

### Week 4: UI and Integration (Phase 3)

**Priority**: MEDIUM - User-facing components

- [ ] Options and popup UI testing
- [ ] Integration and end-to-end testing
- **Expected Coverage**: 65% → 75% (exceeds target)

---

## Success Metrics

### Coverage Targets

- [ ] **Overall Coverage**: 24% → 70%+
- [ ] **Service Worker**: 0% → 80%+
- [ ] **Content Script**: 0% → 75%+
- [ ] **Background**: 0% → 70%+
- [ ] **Utils**: 41% → 80%+

### Quality Metrics

- [ ] **Real vs Mock Ratio**: Increase real code testing by 300%
- [ ] **Test Duplication**: Reduce by 40% (remove ~35 duplicate tests)
- [ ] **Test Maintainability**: Single source of truth for common test patterns
- [ ] **Test Reliability**: Tests fail only when actual functionality breaks

### Performance Metrics

- [ ] **Test Execution Time**: Maintain under 10 seconds total
- [ ] **Test Flakiness**: Zero flaky tests (consistent pass/fail)
- [ ] **CI/CD Integration**: All tests pass in automated environment

---

## Risk Mitigation

### High-Risk Changes

- [ ] **Service Worker Refactoring**: Create backup of existing tests before
      replacing
- [ ] **Mock Reduction**: Gradual transition, maintain fallbacks for critical
      paths
- [ ] **Integration Testing**: Start with simple scenarios, add complexity
      incrementally

### Testing Strategy

- [ ] **Incremental Implementation**: One component at a time
- [ ] **Continuous Validation**: Run tests after each change
- [ ] **Rollback Plan**: Keep original test files until new ones are stable

---

## File Structure After Implementation

```
src/__tests__/
├── test-helpers.ts (enhanced)
├── integration/
│   ├── capture-workflow.test.ts (new)
│   └── message-passing.test.ts (new)
├── background/
│   ├── service-worker.test.ts (enhanced - real implementation)
│   └── lifecycle.test.ts (new)
├── content/
│   ├── content-script.test.ts (new - real implementation)
│   └── dom-extraction.test.ts (new)
├── popup/
│   ├── popup.test.ts (new)
│   └── popup-settings-validation.test.ts (existing)
├── options/
│   └── options.test.ts (new)
└── utils/
    ├── content-extractor.test.ts (consolidated)
    ├── settings-manager.test.ts (consolidated)
    ├── error-handler.test.ts (enhanced - real logic)
    ├── markdown-converter.test.ts (existing)
    └── other utility tests...
```

---

## Notes and Considerations

### Development Guidelines

- **Test-Driven Approach**: Write tests for new functionality before
  implementation
- **Real Code Priority**: Test actual business logic whenever possible
- **Mock Judiciously**: Mock only external dependencies and Chrome APIs
- **Documentation**: Update test documentation as we improve coverage

### Browser Extension Specific Considerations

- **Chrome API Limitations**: Some APIs require real browser environment
- **Message Passing**: Test async communication patterns thoroughly
- **Storage Limitations**: Test quota and performance constraints
- **Content Script Isolation**: Test cross-context communication

---

## Getting Started

To begin implementation:

1. **Review Current Tests**: Understand existing test patterns and coverage gaps
2. **Start with Phase 1**: Low-risk consolidation to reduce duplication
3. **Incremental Progress**: Complete one checkbox at a time
4. **Continuous Validation**: Run test suite after each major change
5. **Documentation**: Update this plan as we discover new requirements

**Ready to proceed with Phase 1? Let's start with consolidating the settings
manager tests!**
