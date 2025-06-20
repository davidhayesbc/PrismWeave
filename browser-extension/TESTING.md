# PrismWeave Browser Extension - Testing

This document describes the comprehensive testing setup for the PrismWeave browser extension, including unit tests, integration tests, and testing utilities.

## 📋 Test Overview

The test suite provides comprehensive coverage for all extension components:

- **Unit Tests**: Testing individual components in isolation
- **Integration Tests**: Testing component interactions and workflows
- **Mock System**: Comprehensive Chrome API and dependency mocking
- **Test Utilities**: Shared testing helpers and mock data generators

## 🏗️ Test Structure

```
tests/
├── setup.js                     # Global test setup and mocks
├── utils/                       # Utility component tests
│   ├── settings-manager.test.js
│   ├── git-operations.test.js
│   ├── content-extractor.test.js
│   └── file-manager.test.js
├── background/                  # Background script tests
│   └── service-worker.test.js
├── popup/                      # Popup interface tests
│   └── popup.test.js
├── content/                    # Content script tests
│   └── content-script.test.js
└── integration/                # End-to-end workflow tests
    └── complete-workflow.test.js
```

## 🧪 Test Categories

### Unit Tests

Testing individual components with mocked dependencies:

- **SettingsManager**: Settings validation, storage, schema enforcement
- **GitOperations**: GitHub API integration, repository management
- **ContentExtractor**: HTML parsing, content cleaning, metadata extraction
- **FileManager**: File organization, naming, metadata generation
- **ServiceWorker**: Message handling, extension lifecycle
- **Popup**: UI interactions, settings management
- **ContentScript**: Page interaction, content extraction

### Integration Tests

Testing complete workflows and component interactions:

- **Complete Capture Flow**: From popup click to GitHub save
- **Settings Management**: End-to-end settings validation and storage
- **GitHub Integration**: Authentication, repository validation, file operations
- **Error Recovery**: Handling failures and edge cases

## 🚀 Running Tests

### Quick Start

```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### Using Test Runner

The custom test runner provides additional commands:

```bash
# Run all tests
node test-runner.js all

# Run with coverage report
node test-runner.js coverage

# Run specific test suite
node test-runner.js suite "SettingsManager"

# Run specific test file
node test-runner.js file "settings-manager.test.js"

# Run unit tests only
node test-runner.js unit

# Run integration tests only
node test-runner.js integration

# Validate test setup
node test-runner.js validate

# Clean test artifacts
node test-runner.js clean

# Show help
node test-runner.js help
```

### CI/CD Testing

```bash
# Run CI tests (no watch, with coverage)
npm run test:ci
node test-runner.js ci
```

## 🔧 Test Configuration

### Jest Configuration (`jest.config.js`)

- **Environment**: jsdom for DOM testing
- **Coverage**: Lines, functions, branches, statements
- **Thresholds**: 70% minimum coverage
- **Setup**: Global mocks and utilities
- **Timeout**: 10 seconds for async operations

### Babel Configuration (`.babelrc`)

- **Preset**: @babel/preset-env for Node.js compatibility
- **Target**: Current Node.js version

## 🎭 Mocking System

### Chrome API Mocks

Complete mocking of Chrome extension APIs:

```javascript
// Storage API
chrome.storage.local.get()
chrome.storage.local.set()

// Runtime API
chrome.runtime.sendMessage()
chrome.runtime.onMessage

// Tabs API
chrome.tabs.query()
chrome.tabs.executeScript()

// Action API
chrome.action.onClicked
```

### Global Mocks

- **fetch**: GitHub API mocking
- **console**: Clean test output
- **importScripts**: Service worker compatibility
- **Document/DOM**: Complete DOM mocking

### Test Utilities

Shared utilities in `tests/setup.js`:

```javascript
// Mock data generators
testUtils.createMockSettings()
testUtils.createMockTab()
testUtils.createMockContent()
testUtils.createMockProcessedContent()

// Mock API responses
testUtils.mockGitHubAPI.success()
testUtils.mockGitHubAPI.error()

// Async helpers
testUtils.waitFor(ms)
```

## 📊 Coverage Reports

### Coverage Thresholds

- **Lines**: 70% minimum
- **Functions**: 70% minimum  
- **Branches**: 70% minimum
- **Statements**: 70% minimum

### Coverage Output

```bash
# Text report (console)
npm run test:coverage

# HTML report (coverage/lcov-report/index.html)
open coverage/lcov-report/index.html

# LCOV report for CI tools
coverage/lcov.info
```

## 🧩 Test Patterns

### Unit Test Pattern

```javascript
describe('ComponentName', () => {
  let component;
  
  beforeEach(() => {
    component = new ComponentName();
    jest.clearAllMocks();
  });

  describe('Method Group', () => {
    test('should do something specific', () => {
      // Arrange
      const input = 'test-input';
      
      // Act
      const result = component.method(input);
      
      // Assert
      expect(result).toBe('expected-output');
    });
  });
});
```

### Integration Test Pattern

```javascript
describe('Workflow Integration', () => {
  test('should complete end-to-end workflow', async () => {
    // Setup
    const mockData = testUtils.createMockData();
    
    // Execute workflow
    const result = await executeWorkflow(mockData);
    
    // Verify all steps
    expect(step1).toHaveBeenCalled();
    expect(step2).toHaveBeenCalledWith(expectedParams);
    expect(result.success).toBe(true);
  });
});
```

### Async Test Pattern

```javascript
test('should handle async operations', async () => {
  // Mock async dependency
  mockService.asyncMethod.mockResolvedValue(expectedResult);
  
  // Execute async operation
  const result = await component.asyncMethod();
  
  // Verify
  expect(mockService.asyncMethod).toHaveBeenCalled();
  expect(result).toEqual(expectedResult);
});
```

## 🐛 Debugging Tests

### Running Single Tests

```bash
# Run specific test file
npm test -- settings-manager.test.js

# Run specific test suite
npm test -- --testNamePattern="SettingsManager"

# Run with verbose output
npm test -- --verbose
```

### Debug Mode

```bash
# Run with Node debugger
node --inspect-brk node_modules/.bin/jest --runInBand

# Debug specific test
node --inspect-brk node_modules/.bin/jest --runInBand settings-manager.test.js
```

### Console Output

```javascript
// Enable console in tests
global.console = {
  ...originalConsole,
  log: originalConsole.log, // Enable for debugging
  error: originalConsole.error
};
```

## ⚡ Performance Testing

### Large Content Handling

```javascript
test('should handle large content efficiently', async () => {
  const largeContent = 'content'.repeat(10000);
  const startTime = Date.now();
  
  const result = await processContent(largeContent);
  
  const processingTime = Date.now() - startTime;
  expect(processingTime).toBeLessThan(5000);
});
```

### Concurrent Operations

```javascript
test('should handle concurrent requests', async () => {
  const promises = Array(5).fill(null).map(() => 
    component.asyncOperation()
  );
  
  const results = await Promise.all(promises);
  
  expect(results.every(r => r.success)).toBe(true);
});
```

## 🔒 Error Testing

### Error Handling Pattern

```javascript
test('should handle errors gracefully', async () => {
  // Mock error condition
  mockDependency.method.mockRejectedValue(new Error('Test error'));
  
  // Execute and verify error handling
  const result = await component.methodWithErrorHandling();
  
  expect(result.success).toBe(false);
  expect(result.error).toContain('Test error');
});
```

### Edge Cases

```javascript
test('should handle edge cases', () => {
  // Test with null/undefined
  expect(() => component.method(null)).not.toThrow();
  expect(() => component.method(undefined)).not.toThrow();
  
  // Test with empty data
  expect(component.method({})).toEqual(defaultResult);
  expect(component.method([])).toEqual(defaultResult);
});
```

## 📈 Continuous Integration

### GitHub Actions Example

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-node@v2
      with:
        node-version: '18'
    - run: npm ci
    - run: npm run test:ci
    - uses: codecov/codecov-action@v1
      with:
        file: ./coverage/lcov.info
```

### Test Reports

The test runner generates comprehensive reports:

- **test-report.json**: Detailed test execution report
- **coverage/**: Coverage reports in multiple formats
- **Console output**: Real-time test progress

## 🛠️ Maintenance

### Adding New Tests

1. Create test file following naming convention: `component-name.test.js`
2. Add to appropriate directory (`unit` vs `integration`)
3. Use existing test patterns and utilities
4. Update coverage thresholds if needed

### Updating Mocks

1. Chrome API changes: Update `tests/setup.js`
2. New dependencies: Add mocks in test files
3. Test utilities: Extend `testUtils` object

### Best Practices

- **Isolation**: Each test should be independent
- **Clarity**: Descriptive test names and clear assertions
- **Coverage**: Aim for high coverage with meaningful tests
- **Performance**: Keep tests fast and efficient
- **Maintenance**: Regular mock updates and cleanup

## 📚 Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Chrome Extension Testing](https://developer.chrome.com/docs/extensions/mv3/tut_debugging/)
- [jsdom Documentation](https://github.com/jsdom/jsdom)
- [Testing Best Practices](https://testingjavascript.com/)

---

For questions or issues with the test setup, please refer to the project documentation or create an issue in the repository.
