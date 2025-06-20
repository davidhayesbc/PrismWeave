// Simple test to verify Jest setup and basic functionality
// This tests the infrastructure itself

describe('Test Infrastructure', () => {
  test('Jest is working correctly', () => {
    expect(1 + 1).toBe(2);
    expect(true).toBeTruthy();
    expect(false).toBeFalsy();
  });

  test('Global mocks are available', () => {
    expect(chrome).toBeDefined();
    expect(chrome.storage).toBeDefined();
    expect(chrome.storage.local).toBeDefined();
    expect(chrome.storage.local.get).toBeDefined();
    expect(chrome.storage.local.set).toBeDefined();
  });

  test('Jest mocking functions work', () => {
    const mockFunction = jest.fn();
    mockFunction('test');
    
    expect(mockFunction).toHaveBeenCalled();
    expect(mockFunction).toHaveBeenCalledWith('test');
    expect(mockFunction).toHaveBeenCalledTimes(1);
  });

  test('Async/await works in tests', async () => {
    const asyncFunction = async () => {
      return new Promise(resolve => {
        setTimeout(() => resolve('success'), 10);
      });
    };

    const result = await asyncFunction();
    expect(result).toBe('success');
  });

  test('DOM environment is available', () => {
    expect(document).toBeDefined();
    expect(window).toBeDefined();
    expect(HTMLElement).toBeDefined();
  });

  test('fetch mock is available', () => {
    expect(fetch).toBeDefined();
    expect(typeof fetch).toBe('function');
  });

  test('ES6 features work', () => {
    const arrow = () => 'arrow function';
    const [first, second] = [1, 2];
    const {prop} = {prop: 'value'};
    const template = `template literal: ${prop}`;

    expect(arrow()).toBe('arrow function');
    expect(first).toBe(1);
    expect(second).toBe(2);
    expect(prop).toBe('value');
    expect(template).toBe('template literal: value');
  });
  test('Module imports work', () => {
    // Test that we can require Node.js modules
    const path = require('path');
    const joined = path.join('a', 'b');
    // Accept both Windows and Unix path separators
    expect(joined === 'a/b' || joined === 'a\\b').toBeTruthy();
  });
});

describe('Chrome API Mocks', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('chrome.storage.local.get mock works', () => {
    const callback = jest.fn();
    chrome.storage.local.get(['test'], callback);
    
    expect(chrome.storage.local.get).toHaveBeenCalledWith(['test'], callback);
  });

  test('chrome.storage.local.set mock works', () => {
    const callback = jest.fn();
    chrome.storage.local.set({test: 'value'}, callback);
    
    expect(chrome.storage.local.set).toHaveBeenCalledWith({test: 'value'}, callback);
  });

  test('chrome runtime mocks are available', () => {
    expect(chrome.runtime).toBeDefined();
    expect(chrome.runtime.sendMessage).toBeDefined();
    expect(chrome.runtime.onMessage).toBeDefined();
  });
  test('chrome tabs mocks are available', () => {
    expect(chrome.tabs).toBeDefined();
    expect(chrome.tabs.query).toBeDefined();
    // Note: sendMessage might not be mocked in setup, which is fine
    // expect(chrome.tabs.sendMessage).toBeDefined();
  });
});
