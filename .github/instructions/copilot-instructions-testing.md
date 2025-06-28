---
applyTo: '**/*.{js,ts}'
---

# Copilot Instructions for Jest Test Case Creation - PrismWeave Project

## Testing Framework Overview
- **Primary Framework**: Jest with jsdom environment
- **Test Structure**: Organized in `src/__tests__/` directory
- **Coverage Target**: 80%+ for critical modules
- **File Naming**: `*.test.js` pattern
- Use JSDOM for browser tests

## Test File Organization
```
src/
├── __tests__/
│   ├── utils/
│   │   ├── settings-manager.test.js
│   │   ├── content-extractor.test.js
│   │   ├── markdown-converter.test.js
│   │   └── file-manager.test.js
│   ├── background/
│   │   └── service-worker.test.js
│   ├── content/
│   │   └── content-script.test.js
│   └── integration/
│       └── end-to-end.test.js
```

## Test Case Naming Conventions
- Use numbered test cases for easy reference: `test('1.1 Description')`
- Follow the pattern: `[Category].[Subcategory] Description`
- Examples:
  - `test('1.1 Verify all schema fields have default values')`
  - `test('2.3 Handle storage failures gracefully')`
  - `test('B.1.2 Test blog post extraction')`

## Test Structure Guidelines

### Basic Test Template
```javascript
describe('ModuleName - Feature Category', () => {
  // Setup and teardown
  beforeEach(() => {
    // Reset state, clear mocks
  });

  afterEach(() => {
    // Cleanup
  });

  test('X.Y Description of what is being tested', () => {
    // Arrange
    const input = setupTestData();
    
    // Act
    const result = moduleFunction(input);
    
    // Assert
    expect(result).toBe(expectedValue);
  });
});
```

### Testing Async Functions
```javascript
test('X.Y Async operation description', async () => {
  // Arrange
  const mockData = { /* test data */ };
  
  // Act
  const result = await asyncFunction(mockData);
  
  // Assert
  expect(result).toMatchObject(expectedShape);
});
```

### Mocking Browser APIs
```javascript
// Mock chrome.storage
const mockStorage = {
  sync: {
    get: jest.fn(),
    set: jest.fn()
  },
  local: {
    get: jest.fn(),
    set: jest.fn()
  }
};
global.chrome = { storage: mockStorage };
```

## Test Data Management

### Creating Test Fixtures
- Store complex test data in separate files
- Use factory functions for generating test objects
- Create realistic but minimal test scenarios

### Test Data Patterns
```javascript
const createMockSettings = (overrides = {}) => ({
  repositoryPath: '',
  githubToken: '',
  defaultFolder: 'unsorted',
  autoCommit: true,
  ...overrides
});

const createMockDocument = (overrides = {}) => ({
  title: 'Test Document',
  url: 'https://example.com',
  content: '<h1>Test Content</h1>',
  ...overrides
});
```

## Validation Testing Patterns

### Schema Validation Tests
```javascript
test('X.Y Validate required fields', () => {
  const invalidData = { /* missing required fields */ };
  const result = validateFunction(invalidData);
  
  expect(result.isValid).toBe(false);
  expect(result.errors).toContain('Missing required field');
});
```

### Type Validation Tests
```javascript
test('X.Y Validate field types', () => {
  const schema = getSchema();
  const testData = getTestData();
  
  Object.entries(schema).forEach(([key, config]) => {
    if (config.type === 'boolean') {
      expect(typeof testData[key]).toBe('boolean');
    }
  });
});
```

## Error Handling Test Patterns

### Exception Testing
```javascript
test('X.Y Handle invalid input gracefully', () => {
  expect(() => {
    functionThatShouldThrow(invalidInput);
  }).toThrow('Expected error message');
});
```

### Async Error Testing
```javascript
test('X.Y Handle async errors', async () => {
  await expect(asyncFunctionThatFails()).rejects.toThrow('Error message');
});
```

## Integration Testing Guidelines

### Module Integration Tests
```javascript
describe('Integration - Module A + Module B', () => {
  test('X.Y Data flows correctly between modules', () => {
    // Test that output from Module A works as input to Module B
    const moduleAOutput = moduleA.process(input);
    const moduleBOutput = moduleB.process(moduleAOutput);
    
    expect(moduleBOutput).toMatchExpectedShape();
  });
});
```

### Storage Integration Tests
```javascript
test('X.Y Settings persist and reload correctly', async () => {
  const originalSettings = { /* test settings */ };
  
  await settingsManager.saveSettings(originalSettings);
  const reloadedSettings = await settingsManager.loadSettings();
  
  expect(reloadedSettings).toEqual(originalSettings);
});
```

## Performance Testing Patterns

### Timing Tests
```javascript
test('X.Y Operation completes within time limit', async () => {
  const startTime = Date.now();
  
  await performOperation();
  
  const endTime = Date.now();
  expect(endTime - startTime).toBeLessThan(1000); // 1 second max
});
```

### Memory Usage Tests
```javascript
test('X.Y No memory leaks in repeated operations', () => {
  const initialMemory = process.memoryUsage().heapUsed;
  
  for (let i = 0; i < 1000; i++) {
    performOperation();
  }
  
  // Force garbage collection if available
  if (global.gc) global.gc();
  
  const finalMemory = process.memoryUsage().heapUsed;
  const memoryIncrease = finalMemory - initialMemory;
  
  expect(memoryIncrease).toBeLessThan(1024 * 1024); // Less than 1MB increase
});
```

## Content Processing Test Patterns

### HTML Extraction Tests
```javascript
test('X.Y Extract content from complex HTML', () => {
  const complexHTML = `
    <article>
      <h1>Title</h1>
      <nav>Navigation</nav>
      <p>Main content</p>
      <aside>Sidebar</aside>
    </article>
  `;
  
  const extracted = extractor.extractContent(complexHTML);
  
  expect(extracted.title).toBe('Title');
  expect(extracted.content).toContain('Main content');
  expect(extracted.content).not.toContain('Navigation');
});
```

### Markdown Conversion Tests
```javascript
test('X.Y Convert HTML to valid markdown', () => {
  const html = '<h1>Title</h1><p>Content with <strong>bold</strong> text</p>';
  const markdown = converter.htmlToMarkdown(html);
  
  expect(markdown).toMatch(/^# Title/);
  expect(markdown).toContain('**bold**');
});
```

## Browser Extension Specific Testing

### Message Passing Tests
```javascript
test('X.Y Background script receives messages correctly', () => {
  const mockMessage = { type: 'CAPTURE_PAGE', data: {} };
  const mockSender = { tab: { id: 123 } };
  
  backgroundScript.onMessage(mockMessage, mockSender);
  
  expect(messageHandler).toHaveBeenCalledWith(mockMessage);
});
```

### Content Script Tests
```javascript
test('X.Y Content script injects correctly', () => {
  document.body.innerHTML = '<div>Test content</div>';
  
  contentScript.inject();
  
  expect(document.querySelector('.prismweave-overlay')).toBeTruthy();
});
```

## Test Coverage Requirements

### Critical Path Testing
- All public methods must have tests
- All error paths must be tested
- All configuration options must be validated
- All user input validation must be tested

### Edge Case Testing
- Empty inputs
- Maximum size inputs
- Invalid data types
- Boundary conditions
- Race conditions (for async operations)

## Debugging Test Guidelines

### Verbose Test Output
```javascript
test('X.Y Complex operation with debugging', () => {
  console.log('Input:', input);
  
  const result = complexOperation(input);
  
  console.log('Result:', result);
  expect(result).toMatchSnapshot();
});
```

### Test Data Snapshots
- Use Jest snapshots for complex object comparisons
- Update snapshots carefully when behavior changes
- Review snapshot changes in code reviews

## Best Practices Summary

1. **One Concept Per Test**: Each test should verify one specific behavior
2. **Descriptive Names**: Test names should clearly describe what is being tested
3. **Arrange-Act-Assert**: Follow the AAA pattern consistently
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Execution**: Keep tests fast to encourage frequent running
6. **Realistic Data**: Use realistic test data that mirrors production scenarios
7. **Error Coverage**: Test both success and failure scenarios
8. **Mocking**: Mock external dependencies to isolate units under test
9. **Documentation**: Comment complex test logic and assumptions
10. **Maintenance**: Keep tests up-to-date as code changes

## Common Patterns to Avoid

- Don't test implementation details, test behavior
- Don't create overly complex test setups
- Don't ignore flaky tests - fix them
- Don't test third-party library behavior
- Don't use real network calls in unit tests
- Don't share mutable state between tests
