// Simplified Popup tests that match actual implementation
const testUtils = require('../../tests/test-utils-extended.js');

// Mock chrome APIs
global.chrome = {
  tabs: {
    query: jest.fn()
  },
  runtime: {
    sendMessage: jest.fn(),
    openOptionsPage: jest.fn()
  }
};

// Mock DOM
global.document = {
  getElementById: jest.fn(),
  addEventListener: jest.fn(),
  querySelector: jest.fn(),
  querySelectorAll: jest.fn()
};

global.window = {
  close: jest.fn(),
  PrismWeaveLogger: {
    createLogger: jest.fn(() => ({
      debug: jest.fn(),
      info: jest.fn(),
      warn: jest.fn(),
      error: jest.fn(),
      group: jest.fn(),
      groupEnd: jest.fn(),
      trace: jest.fn()
    }))
  }
};

global.setTimeout = jest.fn((fn) => fn());
global.setInterval = jest.fn();
global.clearInterval = jest.fn();

const PrismWeavePopup = require('../../src/popup/popup.js');

// Test utilities - local to avoid conflicts with global setup
const localTestUtils = {
  createMockSettings: (overrides = {}) => ({
    repositoryPath: 'owner/repo',
    githubToken: 'test-token',
    githubRepo: 'owner/repo',
    defaultFolder: 'unsorted',
    fileNamingPattern: 'YYYY-MM-DD-domain-title',
    customFolder: '',
    customNamingPattern: '',
    autoCommit: true,
    autoPush: false,
    commitMessage: 'Add captured content: {title}',
    commitMessageTemplate: 'Add: {domain} - {title}',
    enableKeyboardShortcuts: true,
    showNotifications: true,
    autoClosePopup: true,
    captureImages: true,
    maxImageSize: 5242880,
    captureTimeout: 30000,
    removeAds: true,
    removeNavigation: true,
    preserveLinks: true,
    customSelectors: '',
    ...overrides
  }),

  createMockTab: (overrides = {}) => ({
    id: 1,
    url: 'https://example.com/test-page',
    title: 'Test Page Title',
    active: true,
    windowId: 1,
    ...overrides
  })
};

describe('PrismWeavePopup', () => {
  let popup;
  let mockElements;
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Ensure window.close is mocked
    global.window.close = jest.fn();

    // Setup mock DOM elements
    mockElements = {
      'page-title': { textContent: '' },
      'page-url': { textContent: '' },
      'status': { 
        style: { display: 'none' },
        className: '',
        innerHTML: ''
      },
      'status-text': { textContent: '' },
      'capture-btn': {
        addEventListener: jest.fn(),
        disabled: false,
        textContent: '📄 Capture This Page'
      },
      'highlight-btn': {
        addEventListener: jest.fn()
      },
      'settings-btn': {
        addEventListener: jest.fn()
      },      'options-link': {
        addEventListener: jest.fn()
      },
      'loading': {
        style: { display: 'none' },
        innerHTML: ''
      },
      'main-content': {
        style: { display: 'block' }
      }
    };
    
    // Override the mock for this specific test
    document.getElementById = jest.fn().mockImplementation((id) => mockElements[id] || {
      addEventListener: jest.fn(),
      style: {},
      textContent: '',
      disabled: false
    });    // Override DOM mocks for tests
    document.querySelector = jest.fn(() => ({ 
      textContent: '',
      style: {},
      appendChild: jest.fn(),
      removeChild: jest.fn(),
      addEventListener: jest.fn(),
      remove: jest.fn() 
    }));
    
    document.querySelectorAll = jest.fn(() => [
      { classList: { toggle: jest.fn() } }
    ]);    // Mock Chrome APIs
    chrome.tabs.query.mockResolvedValue([localTestUtils.createMockTab()]);
    chrome.runtime.sendMessage.mockResolvedValue({ 
      success: true, 
      data: localTestUtils.createMockSettings() 
    });

    // Create popup without calling constructor to avoid initialization
    popup = Object.create(PrismWeavePopup.prototype);
    popup.currentTab = null;
    popup.settings = null;
  });

  describe('Core Methods', () => {
    test('should get current tab', async () => {
      await popup.getCurrentTab();
      
      expect(chrome.tabs.query).toHaveBeenCalledWith({ active: true, currentWindow: true });
      expect(popup.currentTab).toEqual(localTestUtils.createMockTab());
    });

    test('should load settings', async () => {
      await popup.loadSettings();
        expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({ action: 'GET_SETTINGS' });
      expect(popup.settings).toBeTruthy();
    });

    test('should update page info', () => {      popup.currentTab = localTestUtils.createMockTab();
      popup.updatePageInfo();
      
      expect(mockElements['page-title'].textContent).toBe('Test Page Title');
      expect(mockElements['page-url'].textContent).toBe('https://example.com/test-page');
    });

    test('should setup event listeners', () => {
      popup.setupEventListeners();
      
      expect(mockElements['capture-btn'].addEventListener).toHaveBeenCalledWith('click', expect.any(Function));      expect(mockElements['highlight-btn'].addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
    });

    test('should check page capturability', () => {
      popup.currentTab = localTestUtils.createMockTab();
      popup.settings = localTestUtils.createMockSettings();
      
      expect(() => popup.checkPageCapturability()).not.toThrow();
    });

    test('should show status', () => {
      popup.showStatus('Test message', 'success');
      
      expect(mockElements['status-text'].textContent).toBe('Test message');
      expect(mockElements['status'].className).toBe('status success');
      expect(mockElements['status'].style.display).toBe('block');
    });

    test('should hide status', () => {
      popup.hideStatus();
      
      expect(mockElements['status'].style.display).toBe('none');
    });  });

  describe('Page Capture', () => {
    test('should capture current page', async () => {
      popup.currentTab = localTestUtils.createMockTab();
      popup.settings = localTestUtils.createMockSettings();

      chrome.runtime.sendMessage.mockResolvedValue({
        success: true,
        data: { filename: 'test.md', metadata: { folder: 'test' } }
      });

      await popup.captureCurrentPage();      expect(chrome.runtime.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({ action: 'CAPTURE_PAGE' })
      );
    });

    test('should handle capture errors', async () => {
      popup.currentTab = localTestUtils.createMockTab();
      popup.settings = localTestUtils.createMockSettings();

      chrome.runtime.sendMessage.mockResolvedValue({
        success: false,
        error: 'Capture failed'
      });

      await popup.captureCurrentPage();

      // Should not throw, error should be handled
      expect(chrome.runtime.sendMessage).toHaveBeenCalled();
    });
  });

  describe('UI Controls', () => {
    test('should disable capture button', () => {
      popup.disableCaptureButton();
      
      expect(mockElements['capture-btn'].disabled).toBe(true);
      expect(mockElements['capture-btn'].textContent).toBe('Cannot Capture');
    });

    test('should enable capture button', () => {
      popup.enableCaptureButton();
      
      expect(mockElements['capture-btn'].disabled).toBe(false);
      expect(mockElements['capture-btn'].textContent).toBe('📄 Capture This Page');
    });

    test('should show loading', () => {
      popup.showLoading(true);
      
      expect(mockElements['loading'].style.display).toBe('flex');
      expect(mockElements['main-content'].style.display).toBe('none');
    });

    test('should hide loading', () => {
      popup.showLoading(false);
      
      expect(mockElements['loading'].style.display).toBe('none');
      expect(mockElements['main-content'].style.display).toBe('block');
    });
  });

  describe('Helper Methods', () => {
    test('should get default settings', () => {
      const defaults = popup.getDefaultSettings();
      
      expect(defaults).toHaveProperty('autoCommit', false);
      expect(defaults).toHaveProperty('autoPush', false);
      expect(defaults).toHaveProperty('repositoryPath', '');
      expect(defaults).toHaveProperty('defaultFolder', 'unsorted');
    });

    test('should open settings', () => {
      popup.openSettings();
      
      expect(chrome.runtime.openOptionsPage).toHaveBeenCalled();
      expect(window.close).toHaveBeenCalled();
    });

    test('should open options', () => {
      popup.openOptions();
      
      expect(chrome.runtime.openOptionsPage).toHaveBeenCalled();
      expect(window.close).toHaveBeenCalled();
    });
  });
});
