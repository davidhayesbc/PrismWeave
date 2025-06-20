// Unit tests for Popup Script
// Testing popup interface, user interactions, and communication with background

// Import test utilities - setup.js sets up global.testUtils
require('../setup.js');

// Import the PrismWeavePopup class
const PrismWeavePopup = require('../../src/popup/popup.js');

beforeAll(() => {
  // Mock window object
  global.window = {
    ...global.window,
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
    },
    ErrorHandler: {
      createUserFriendlyError: jest.fn((error, context) => ({
        message: error.message || 'An error occurred',
        solution: 'Please try again.'
      }))
    }
  };

  // Mock document addEventListener
  global.document.addEventListener = jest.fn();
});

describe('PrismWeavePopup', () => {
  let popup;
  let mockElements;  beforeEach(async () => {
    jest.clearAllMocks();
    
    // Ensure document is properly set up
    if (!global.document) {
      global.document = document;
    }
    
    // Setup mock DOM elements
    mockElements = {
      'page-title': { textContent: '', innerHTML: '' },
      'page-url': { textContent: '', innerHTML: '', href: '' },
      'capture-btn': { 
        addEventListener: jest.fn(),
        disabled: false,
        textContent: 'Capture Page',
        style: {}
      },
      'status': { 
        textContent: '', 
        className: '',
        style: { display: 'none' },
        innerHTML: ''
      },
      'status-text': { 
        textContent: ''
      },
      'loading': {
        style: { display: 'none' },
        innerHTML: ''
      },
      'main-content': {
        style: { display: 'block' }
      },
      'highlight-btn': {
        addEventListener: jest.fn()
      },
      'settings-btn': {
        addEventListener: jest.fn()
      },
      'options-link': {
        addEventListener: jest.fn()
      }
    };

    // Reset document mock to override setup.js
    global.document.getElementById = jest.fn().mockImplementation((id) => mockElements[id] || {
      addEventListener: jest.fn(),
      style: {},
      textContent: '',
      innerHTML: '',
      value: '',
      checked: false,
      disabled: false
    });

    // Mock DOM query methods
    global.document.querySelector = jest.fn((selector) => {
      if (selector === '.current-step') return { textContent: '' };
      if (selector === '.dot') return { classList: { toggle: jest.fn() } };
      return { style: {}, textContent: '', classList: { toggle: jest.fn() } };
    });
    
    global.document.querySelectorAll = jest.fn((selector) => {
      if (selector === '.dot') {
        return Array(4).fill({ classList: { toggle: jest.fn() } });
      }
      return [];
    });

    // Mock chrome APIs
    chrome.tabs.query.mockResolvedValue([global.testUtils.createMockTab()]);
    chrome.runtime.sendMessage.mockImplementation((message, callback) => {
      const response = { success: true, data: global.testUtils.createMockSettings() };
      if (callback && typeof callback === 'function') {
        callback(response);
      }
      return Promise.resolve(response);
    });

    // Create popup instance
    popup = new PrismWeavePopup();
    
    // Wait for async initialization
    await new Promise(resolve => setTimeout(resolve, 50));
    
    // Spy on existing methods
    jest.spyOn(popup, 'showStatus').mockImplementation((message, type) => {
      mockElements['status-text'].textContent = message;
      mockElements['status'].className = `status ${type}`;
      mockElements['status'].style.display = 'block';
    });
  });
  describe('Initialization', () => {
    test('should initialize popup components', () => {      expect(popup.currentTab).toEqual(global.testUtils.createMockTab());
      expect(popup.settings).toEqual(global.testUtils.createMockSettings());
    });

    test('should get current tab', async () => {
      await popup.getCurrentTab();
      expect(chrome.tabs.query).toHaveBeenCalledWith({ active: true, currentWindow: true });
      expect(popup.currentTab).toEqual(global.testUtils.createMockTab());
    });

    test('should load settings', async () => {
      await popup.loadSettings();
      expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({ action: 'GET_SETTINGS' });
      expect(popup.settings).toEqual(global.testUtils.createMockSettings());
    });

    test('should setup event listeners', () => {
      jest.clearAllMocks();
      popup.setupEventListeners();
      expect(mockElements['capture-btn'].addEventListener).toHaveBeenCalled();
    });  });

  describe('Page Information Display', () => {
    test('should update page info', () => {
      const tab = global.testUtils.createMockTab({
        title: 'Test Article',
        url: 'https://example.com/test'
      });
      popup.currentTab = tab;

      popup.updatePageInfo();

      expect(mockElements['page-title'].textContent).toBe('Test Article');
      expect(mockElements['page-url'].textContent).toBe('https://example.com/test');
    });

    test('should handle missing tab gracefully', () => {
      popup.currentTab = null;
      expect(() => popup.updatePageInfo()).not.toThrow();
    });

    test('should check page capturability', () => {
      popup.currentTab = global.testUtils.createMockTab({ url: 'chrome://extensions/' });
      popup.checkPageCapturability();
      expect(mockElements['capture-btn'].disabled).toBe(true);
    });
  });
  describe('Page Capture', () => {
    test('should capture page successfully', async () => {
      // Mock successful capture response
      chrome.runtime.sendMessage.mockResolvedValue({
        success: true,
        data: {
          filename: 'test-article.md',
          metadata: { folder: 'articles', quality: 0.9 }
        }
      });

      await popup.captureCurrentPage();
      expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({
        action: 'CAPTURE_PAGE',
        githubToken: global.testUtils.createMockSettings().githubToken,
        githubRepo: global.testUtils.createMockSettings().repositoryPath
      });
    });

    test('should handle capture errors', async () => {
      // Mock error response
      chrome.runtime.sendMessage.mockResolvedValue({
        success: false,
        error: 'Network error'
      });

      // Spy on showEnhancedError
      const showErrorSpy = jest.spyOn(popup, 'showEnhancedError').mockImplementation(() => {});

      await popup.captureCurrentPage();
      expect(showErrorSpy).toHaveBeenCalled();
    });
  });

  describe('Status Display', () => {
    test('should show success status', () => {
      popup.showStatus('Success', 'success');
      expect(mockElements['status-text'].textContent).toBe('Success');
      expect(mockElements['status'].className).toBe('status success');
      expect(mockElements['status'].style.display).toBe('block');
    });

    test('should show error status', () => {
      popup.showStatus('Error', 'error');
      expect(mockElements['status-text'].textContent).toBe('Error');
      expect(mockElements['status'].className).toBe('status error');
    });
  });

  describe('Utility Methods', () => {
    test('should show and hide loading', () => {
      expect(() => popup.showLoading(true)).not.toThrow();
      expect(mockElements['loading'].style.display).toBe('flex');
      expect(mockElements['main-content'].style.display).toBe('none');
      
      popup.showLoading(false);
      expect(mockElements['loading'].style.display).toBe('none');
      expect(mockElements['main-content'].style.display).toBe('block');
    });

    test('should enable and disable capture button', () => {
      popup.disableCaptureButton();
      expect(mockElements['capture-btn'].disabled).toBe(true);
      expect(mockElements['capture-btn'].textContent).toBe('Cannot Capture');

      popup.enableCaptureButton();
      expect(mockElements['capture-btn'].disabled).toBe(false);
      expect(mockElements['capture-btn'].textContent).toBe('📄 Capture This Page');
    });

    test('should estimate capture time', () => {
      const time = popup.estimateCaptureTime();
      expect(typeof time).toBe('number');
      expect(time).toBeGreaterThan(0);
    });

    test('should hide status', () => {
      popup.hideStatus();
      expect(mockElements['status'].style.display).toBe('none');
    });

    test('should handle different URL types for capture time estimation', () => {
      // Test news site
      popup.currentTab = global.testUtils.createMockTab({ url: 'https://news.example.com/article' });
      expect(popup.estimateCaptureTime()).toBe(8);

      // Test documentation site
      popup.currentTab = global.testUtils.createMockTab({ url: 'https://docs.example.com/guide' });
      expect(popup.estimateCaptureTime()).toBe(3);

      // Test social media site
      popup.currentTab = global.testUtils.createMockTab({ url: 'https://twitter.com/user/status' });
      expect(popup.estimateCaptureTime()).toBe(10);

      // Test default
      popup.currentTab = global.testUtils.createMockTab({ url: 'https://example.com/page' });
      expect(popup.estimateCaptureTime()).toBe(5);
    });
  });

  describe('Advanced Loading and Error Handling', () => {
    test('should show advanced loading with steps', () => {
      popup.showAdvancedLoading();
      expect(mockElements['loading'].style.display).toBe('block');
      expect(mockElements['loading'].innerHTML).toContain('advanced-spinner');
      expect(mockElements['loading'].innerHTML).toContain('Extracting page content...');
    });

    test('should update loading steps', () => {
      popup.updateLoadingStep(1, 'Converting to markdown...');
      const stepElement = { textContent: '' };
      document.querySelector.mockReturnValue(stepElement);
      popup.updateLoadingStep(1, 'Converting to markdown...');
      // Just verify method executes without error
      expect(document.querySelector).toHaveBeenCalledWith('.current-step');
    });

    test('should hide loading and clear intervals', () => {
      popup.loadingInterval = setInterval(() => {}, 100);
      popup.hideLoading();
      expect(mockElements['loading'].style.display).toBe('none');
      expect(popup.loadingInterval).toBe(null);
    });

    test('should show success with details', () => {
      const data = {
        filename: 'test-article.md',
        metadata: { folder: 'articles', quality: 0.85 }
      };
      popup.showSuccessWithDetails(data);
      expect(mockElements['status'].className).toBe('status success');
      expect(mockElements['status'].innerHTML).toContain('Page Captured Successfully!');
      expect(mockElements['status'].innerHTML).toContain('test-article.md');
    });

    test('should show enhanced error', () => {
      const error = new Error('Network timeout');
      popup.showEnhancedError(error);
      expect(mockElements['status'].className).toBe('status error');
      expect(mockElements['status'].innerHTML).toContain('Capture Failed');
      expect(mockElements['status'].innerHTML).toContain('Network timeout');
    });

    test('should format quality scores', () => {
      expect(popup.formatQuality(0.9)).toBe('90% (Excellent)');
      expect(popup.formatQuality(0.7)).toBe('70% (Good)');
      expect(popup.formatQuality(0.5)).toBe('50% (Fair)');
      expect(popup.formatQuality(0.3)).toBe('30% (Poor)');
    });
  });

  describe('Settings and Default Values', () => {
    test('should return default settings when needed', () => {
      const defaults = popup.getDefaultSettings();
      expect(defaults).toEqual({
        autoCommit: false,
        autoPush: false,
        repositoryPath: '',
        githubToken: '',
        defaultFolder: 'unsorted',
        fileNamingPattern: 'YYYY-MM-DD-domain-title',
      });
    });

    test('should handle settings load failure', async () => {
      chrome.runtime.sendMessage.mockResolvedValue({ success: false });
      await popup.loadSettings();      expect(popup.settings).toEqual(popup.getDefaultSettings());
    });

    test('should open settings page', () => {
      chrome.runtime.openOptionsPage = jest.fn();
      popup.openSettings();
      expect(chrome.runtime.openOptionsPage).toHaveBeenCalled();
      expect(global.window.close).toHaveBeenCalled();
    });

    test('should open options page', () => {
      chrome.runtime.openOptionsPage = jest.fn();
      popup.openOptions();
      expect(chrome.runtime.openOptionsPage).toHaveBeenCalled();
      expect(global.window.close).toHaveBeenCalled();
    });
  });

  describe('Page Capturability Checks', () => {
    test('should disable capture for chrome:// URLs', () => {
      popup.currentTab = global.testUtils.createMockTab({ url: 'chrome://extensions/' });
      jest.spyOn(popup, 'showStatus');
      jest.spyOn(popup, 'disableCaptureButton');
      
      popup.checkPageCapturability();
      
      expect(popup.showStatus).toHaveBeenCalledWith('Cannot capture browser internal pages', 'warning');
      expect(popup.disableCaptureButton).toHaveBeenCalled();
    });

    test('should disable capture for edge:// URLs', () => {
      popup.currentTab = global.testUtils.createMockTab({ url: 'edge://settings/' });
      jest.spyOn(popup, 'showStatus');
      jest.spyOn(popup, 'disableCaptureButton');
      
      popup.checkPageCapturability();
      
      expect(popup.showStatus).toHaveBeenCalledWith('Cannot capture browser internal pages', 'warning');
      expect(popup.disableCaptureButton).toHaveBeenCalled();
    });

    test('should disable capture for non-web URLs', () => {
      popup.currentTab = global.testUtils.createMockTab({ url: 'file:///local/file.html' });
      jest.spyOn(popup, 'showStatus');
      jest.spyOn(popup, 'disableCaptureButton');
      
      popup.checkPageCapturability();
      
      expect(popup.showStatus).toHaveBeenCalledWith('Cannot capture non-web pages', 'warning');
      expect(popup.disableCaptureButton).toHaveBeenCalled();
    });

    test('should warn when repository not configured', () => {
      popup.currentTab = global.testUtils.createMockTab({ url: 'https://example.com' });
      popup.settings = { ...popup.settings, repositoryPath: '' };
      jest.spyOn(popup, 'showStatus');
      
      popup.checkPageCapturability();
      
      expect(popup.showStatus).toHaveBeenCalledWith('Repository not configured. Click Settings to set up.', 'warning');
    });
  });
});
