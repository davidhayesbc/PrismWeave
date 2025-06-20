// Unit tests for Popup Script
// Testing popup interface, user interactions, and communication with background

// Setup is imported via jest setupFilesAfterEnv
// testUtils is available as a global

beforeAll(() => {
  // Mock DOM elements that the popup expects
  const mockElement = {
    addEventListener: jest.fn(),
    style: { display: 'none' },
    textContent: '',
    innerHTML: '',
    value: '',
    checked: false,
    disabled: false,
    className: '',
    href: ''
  };

  global.document.getElementById = jest.fn((id) => {
    const elements = {
      'page-title': { ...mockElement, textContent: '', innerHTML: '' },
      'page-url': { ...mockElement, textContent: '', innerHTML: '', href: '' },
      'capture-btn': { 
        ...mockElement,
        addEventListener: jest.fn(),
        disabled: false,
        textContent: '📄 Capture This Page',
        style: {}
      },
      'highlight-btn': { ...mockElement, addEventListener: jest.fn() },
      'settings-btn': { ...mockElement, addEventListener: jest.fn() },
      'options-link': { ...mockElement, addEventListener: jest.fn() },
      'status': {
        ...mockElement,
        textContent: '',
        className: '',
        style: { display: 'none' },
        innerHTML: ''
      },
      'status-text': { ...mockElement, textContent: '' },
      'loading': { ...mockElement, style: { display: 'none' } },
      'main-content': { ...mockElement, style: { display: 'block' } }
    };
    return elements[id] || { ...mockElement };
  });

  // Mock window.close
  global.window.close = jest.fn();
  // Mock window.PrismWeaveLogger
  global.window.PrismWeaveLogger = {
    createLogger: jest.fn(() => ({
      debug: jest.fn(),
      info: jest.fn(),
      warn: jest.fn(),
      error: jest.fn(),
      trace: jest.fn(),
      group: jest.fn(),
      groupEnd: jest.fn()
    }))
  };

  // Mock document.addEventListener for keyboard shortcuts
  global.document.addEventListener = jest.fn();

  // Mock document.querySelector and querySelectorAll
  global.document.querySelector = jest.fn((selector) => {
    if (selector === '.current-step') return { textContent: '' };
    if (selector === '.dot') return { classList: { toggle: jest.fn() } };
    return null;
  });
  
  global.document.querySelectorAll = jest.fn((selector) => {
    if (selector === '.dot') {
      return [
        { classList: { toggle: jest.fn() } },
        { classList: { toggle: jest.fn() } },
        { classList: { toggle: jest.fn() } },
        { classList: { toggle: jest.fn() } }
      ];
    }
    return [];
  });
});

// Import the PrismWeavePopup class
const PrismWeavePopup = require('../../src/popup/popup.js');

describe('PrismWeavePopup', () => {
  let popup;
  let mockElements;

  beforeEach(async () => {
    jest.clearAllMocks();
    
    // Setup mock DOM elements
    const mockElement = {
      addEventListener: jest.fn(),
      style: { display: 'none' },
      textContent: '',
      innerHTML: '',
      value: '',
      checked: false,
      disabled: false,
      className: '',
      href: ''
    };

    mockElements = {
      'page-title': { ...mockElement, textContent: '', innerHTML: '' },
      'page-url': { ...mockElement, textContent: '', innerHTML: '', href: '' },
      'capture-btn': { 
        ...mockElement,
        addEventListener: jest.fn(),
        disabled: false,
        textContent: '📄 Capture This Page',
        style: {}
      },
      'highlight-btn': { ...mockElement, addEventListener: jest.fn() },
      'settings-btn': { ...mockElement, addEventListener: jest.fn() },
      'options-link': { ...mockElement, addEventListener: jest.fn() },
      'status': { 
        ...mockElement,
        textContent: '', 
        className: '',
        style: { display: 'none' },
        innerHTML: ''
      },
      'status-text': { ...mockElement, textContent: '' },
      'loading': { ...mockElement, style: { display: 'none' } },
      'main-content': { ...mockElement, style: { display: 'block' } }
    };

    document.getElementById.mockImplementation((id) => mockElements[id] || { ...mockElement });

    // Mock chrome APIs
    chrome.tabs.query.mockResolvedValue([testUtils.createMockTab()]);
    chrome.runtime.sendMessage.mockImplementation((message) => {
      const response = { success: true, data: testUtils.createMockSettings() };
      return Promise.resolve(response);
    });

    // Mock chrome.runtime.openOptionsPage
    chrome.runtime.openOptionsPage = jest.fn();

    // Create popup instance
    popup = new PrismWeavePopup();
    
    // Wait for async initialization
    await new Promise(resolve => setTimeout(resolve, 100));
  });
  describe('Initialization', () => {
    test('should initialize popup components', () => {
      expect(popup.currentTab).toEqual(testUtils.createMockTab());
      expect(popup.settings).toEqual(testUtils.createMockSettings());
    });

    test('should get current tab', async () => {
      await popup.getCurrentTab();
      expect(chrome.tabs.query).toHaveBeenCalledWith({ active: true, currentWindow: true });
      expect(popup.currentTab).toEqual(testUtils.createMockTab());
    });

    test('should load settings', async () => {
      await popup.loadSettings();
      expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({ action: 'GET_SETTINGS' });
      expect(popup.settings).toEqual(testUtils.createMockSettings());
    });

    test('should use default settings when loading fails', async () => {
      chrome.runtime.sendMessage.mockResolvedValue({ success: false });
      await popup.loadSettings();
      expect(popup.settings).toEqual(popup.getDefaultSettings());
    });

    test('should setup event listeners', () => {
      jest.clearAllMocks();
      popup.setupEventListeners();
      expect(mockElements['capture-btn'].addEventListener).toHaveBeenCalled();
      expect(document.addEventListener).toHaveBeenCalledWith('keydown', expect.any(Function));
    });
  });
  describe('Page Information Display', () => {
    test('should update page info', () => {
      const tab = testUtils.createMockTab({
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

    test('should handle missing title', () => {
      popup.currentTab = testUtils.createMockTab({ title: null });
      popup.updatePageInfo();
      expect(mockElements['page-title'].textContent).toBe('Untitled');
    });

    test('should check page capturability for valid pages', () => {
      popup.currentTab = testUtils.createMockTab({ url: 'https://example.com/test' });
      popup.settings = testUtils.createMockSettings();
      
      jest.spyOn(popup, 'showStatus').mockImplementation(() => {});
      jest.spyOn(popup, 'disableCaptureButton').mockImplementation(() => {});
      
      popup.checkPageCapturability();
      expect(popup.disableCaptureButton).not.toHaveBeenCalled();
    });

    test('should disable capture for non-web pages', () => {
      popup.currentTab = testUtils.createMockTab({ url: 'chrome://extensions/' });
      
      jest.spyOn(popup, 'showStatus').mockImplementation(() => {});
      jest.spyOn(popup, 'disableCaptureButton').mockImplementation(() => {});
      
      popup.checkPageCapturability();
      expect(popup.disableCaptureButton).toHaveBeenCalled();
      expect(popup.showStatus).toHaveBeenCalledWith('Cannot capture browser internal pages', 'warning');
    });

    test('should warn when repository not configured', () => {
      popup.currentTab = testUtils.createMockTab({ url: 'https://example.com/test' });
      popup.settings = testUtils.createMockSettings({ repositoryPath: '' });
      
      jest.spyOn(popup, 'showStatus').mockImplementation(() => {});
      
      popup.checkPageCapturability();
      expect(popup.showStatus).toHaveBeenCalledWith('Repository not configured. Click Settings to set up.', 'warning');
    });
  });
  describe('Page Capture', () => {
    test('should capture page successfully', async () => {
      chrome.runtime.sendMessage.mockResolvedValue({
        success: true,
        data: {
          filename: 'test-file.md',
          metadata: { folder: 'test', quality: 0.8 }
        }
      });

      jest.spyOn(popup, 'showAdvancedLoading').mockImplementation(() => {});
      jest.spyOn(popup, 'hideLoading').mockImplementation(() => {});
      jest.spyOn(popup, 'disableCaptureButton').mockImplementation(() => {});
      jest.spyOn(popup, 'enableCaptureButton').mockImplementation(() => {});
      jest.spyOn(popup, 'showSuccessWithDetails').mockImplementation(() => {});

      await popup.captureCurrentPage();

      expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({
        action: 'CAPTURE_PAGE',
        githubToken: popup.settings.githubToken,
        githubRepo: popup.settings.githubRepo || popup.settings.repositoryPath
      });
      expect(popup.showSuccessWithDetails).toHaveBeenCalled();
    });

    test('should handle capture failure', async () => {
      chrome.runtime.sendMessage.mockResolvedValue({
        success: false,
        error: 'Network error'
      });

      jest.spyOn(popup, 'showAdvancedLoading').mockImplementation(() => {});
      jest.spyOn(popup, 'hideLoading').mockImplementation(() => {});
      jest.spyOn(popup, 'disableCaptureButton').mockImplementation(() => {});
      jest.spyOn(popup, 'enableCaptureButton').mockImplementation(() => {});
      jest.spyOn(popup, 'showEnhancedError').mockImplementation(() => {});

      await popup.captureCurrentPage();

      expect(popup.showEnhancedError).toHaveBeenCalled();
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
      expect(mockElements['status'].style.display).toBe('block');
    });

    test('should hide status', () => {
      popup.hideStatus();
      expect(mockElements['status'].style.display).toBe('none');
    });

    test('should show success with details', () => {
      const data = {
        filename: 'test-file.md',
        metadata: { folder: 'test', quality: 0.8 }
      };
      
      popup.showSuccessWithDetails(data);
      expect(mockElements['status'].className).toBe('status success');
      expect(mockElements['status'].innerHTML).toContain('test-file.md');
      expect(mockElements['status'].innerHTML).toContain('80% (Excellent)');
    });

    test('should show enhanced error', () => {
      const error = new Error('Test error');
      popup.showEnhancedError(error);
      expect(mockElements['status'].className).toBe('status error');
      expect(mockElements['status'].innerHTML).toContain('Capture Failed');
    });
  });
  describe('Utility Methods', () => {
    test('should show and hide loading', () => {
      popup.showLoading(true);
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
      popup.currentTab = testUtils.createMockTab({ url: 'https://example.com/news/article' });
      expect(popup.estimateCaptureTime()).toBe(8);
      
      popup.currentTab = testUtils.createMockTab({ url: 'https://docs.example.com' });
      expect(popup.estimateCaptureTime()).toBe(3);
      
      popup.currentTab = testUtils.createMockTab({ url: 'https://twitter.com/user' });
      expect(popup.estimateCaptureTime()).toBe(10);
      
      popup.currentTab = testUtils.createMockTab({ url: 'https://example.com' });
      expect(popup.estimateCaptureTime()).toBe(5);
    });

    test('should handle missing tab for time estimation', () => {
      popup.currentTab = null;
      expect(popup.estimateCaptureTime()).toBe(5);
    });

    test('should format quality percentage', () => {
      expect(popup.formatQuality(0.85)).toBe('85% (Excellent)');
      expect(popup.formatQuality(0.65)).toBe('65% (Good)');
      expect(popup.formatQuality(0.45)).toBe('45% (Fair)');
      expect(popup.formatQuality(0.25)).toBe('25% (Poor)');
    });

    test('should show advanced loading with steps', () => {
      jest.useFakeTimers();
      popup.showAdvancedLoading();
      expect(mockElements['loading'].style.display).toBe('block');
      expect(mockElements['loading'].innerHTML).toContain('Extracting page content...');
      jest.useRealTimers();
    });

    test('should hide loading and clear intervals', () => {
      popup.loadingInterval = setInterval(() => {}, 100);
      popup.hideLoading();
      expect(mockElements['loading'].style.display).toBe('none');
      expect(popup.loadingInterval).toBeNull();
    });
  });

  describe('User Interactions', () => {
    test('should handle highlight content', async () => {
      chrome.runtime.sendMessage.mockResolvedValue({ success: true });
      jest.spyOn(popup, 'showStatus').mockImplementation(() => {});
      jest.spyOn(popup, 'hideStatus').mockImplementation(() => {});

      await popup.highlightContent();
      
      expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({
        action: 'HIGHLIGHT_CONTENT'
      });
      expect(popup.showStatus).toHaveBeenCalledWith('Content highlighted on page', 'success');
    });

    test('should handle highlight content failure', async () => {
      chrome.runtime.sendMessage.mockResolvedValue({ 
        success: false, 
        error: 'Failed to highlight' 
      });
      jest.spyOn(popup, 'showStatus').mockImplementation(() => {});

      await popup.highlightContent();
      
      expect(popup.showStatus).toHaveBeenCalledWith('✗ Highlight failed: Failed to highlight', 'error');
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
  describe('Edge Cases and Error Handling', () => {
    test('should handle initialization failure gracefully', async () => {
      // Create a spy on showStatus before creating a new popup
      const showStatusSpy = jest.fn();
      
      // Mock chrome.tabs.query to fail
      chrome.tabs.query.mockRejectedValueOnce(new Error('Tab query failed'));
      
      // Create a popup instance and spy on its showStatus method
      const failingPopup = new PrismWeavePopup();
      failingPopup.showStatus = showStatusSpy;
      
      // Wait for initialization to complete
      await new Promise(resolve => setTimeout(resolve, 150));
      
      expect(showStatusSpy).toHaveBeenCalledWith('Failed to initialize', 'error');
    });

    test('should handle chrome runtime sendMessage rejection', async () => {
      chrome.runtime.sendMessage.mockRejectedValue(new Error('Runtime error'));
      jest.spyOn(popup, 'showEnhancedError').mockImplementation(() => {});
      jest.spyOn(popup, 'hideLoading').mockImplementation(() => {});
      jest.spyOn(popup, 'enableCaptureButton').mockImplementation(() => {});

      await popup.captureCurrentPage();

      expect(popup.showEnhancedError).toHaveBeenCalled();
    });

    test('should handle missing DOM elements gracefully', () => {
      document.getElementById.mockReturnValue(null);
      expect(() => popup.setupEventListeners()).not.toThrow();
    });

    test('should handle keyboard shortcuts', () => {
      // Reset mock to capture new calls
      document.addEventListener.mockClear();
      jest.spyOn(popup, 'captureCurrentPage').mockImplementation(() => Promise.resolve());
      
      // Call setup again to get fresh event listeners
      popup.setupEventListeners();
      
      const mockEvent = { key: 'Enter', shiftKey: false };

      // Find the keydown event listener
      const keydownCall = document.addEventListener.mock.calls.find(
        call => call[0] === 'keydown'
      );
      
      expect(keydownCall).toBeDefined();
      const keydownHandler = keydownCall[1];
      
      keydownHandler(mockEvent);
      expect(popup.captureCurrentPage).toHaveBeenCalled();
    });

    test('should handle Escape key to close popup', () => {
      const mockEvent = { key: 'Escape' };

      // Use the existing event listener
      const keydownCall = document.addEventListener.mock.calls.find(
        call => call[0] === 'keydown'
      );
      
      expect(keydownCall).toBeDefined();
      const keydownHandler = keydownCall[1];
      
      keydownHandler(mockEvent);
      expect(window.close).toHaveBeenCalled();
    });

    test('should handle advanced loading step updates', () => {
      const mockStepElement = { textContent: '' };
      const mockDots = [
        { classList: { toggle: jest.fn() } },
        { classList: { toggle: jest.fn() } },
        { classList: { toggle: jest.fn() } },
        { classList: { toggle: jest.fn() } }
      ];

      document.querySelector.mockImplementation((selector) => {
        if (selector === '.current-step') return mockStepElement;
        return null;
      });
      
      document.querySelectorAll.mockImplementation((selector) => {
        if (selector === '.dot') return mockDots;
        return [];
      });

      popup.updateLoadingStep(1, 'Step 2');
      
      expect(mockStepElement.textContent).toBe('Step 2');
      expect(mockDots[0].classList.toggle).toHaveBeenCalledWith('active', true);
      expect(mockDots[1].classList.toggle).toHaveBeenCalledWith('active', true);
      expect(mockDots[2].classList.toggle).toHaveBeenCalledWith('active', false);
    });

    test('should handle update loading step with missing elements', () => {
      document.querySelector.mockReturnValue(null);
      document.querySelectorAll.mockReturnValue([]);

      expect(() => popup.updateLoadingStep(1, 'Step 2')).not.toThrow();
    });

    test('should handle error with ErrorHandler utility', () => {
      global.window.ErrorHandler = {
        createUserFriendlyError: jest.fn((error, context) => ({
          message: 'User friendly error message',
          solution: 'Try this solution'
        }))
      };

      const error = new Error('Original error');
      popup.showEnhancedError(error);

      expect(window.ErrorHandler.createUserFriendlyError).toHaveBeenCalledWith(error, 'page capture');
      expect(mockElements['status'].innerHTML).toContain('User friendly error message');
      expect(mockElements['status'].innerHTML).toContain('Try this solution');
    });

    test('should handle error without ErrorHandler utility', () => {
      global.window.ErrorHandler = undefined;

      const error = new Error('Test error message');
      popup.showEnhancedError(error);

      expect(mockElements['status'].innerHTML).toContain('Test error message');
    });

    test('should handle success details without metadata', () => {
      const data = { filename: 'test-file.md' };
      
      popup.showSuccessWithDetails(data);
      expect(mockElements['status'].innerHTML).toContain('test-file.md');
      expect(mockElements['status'].innerHTML).toContain('unsorted');
    });

    test('should handle all URL types for capturability check', () => {
      const urlTests = [
        { url: 'edge://settings/', shouldDisable: true },
        { url: 'about:blank', shouldDisable: true },
        { url: 'ftp://example.com', shouldDisable: true },
        { url: 'file:///C:/test.html', shouldDisable: true },
        { url: 'https://example.com', shouldDisable: false },
        { url: 'http://example.com', shouldDisable: false }
      ];

      jest.spyOn(popup, 'showStatus').mockImplementation(() => {});
      jest.spyOn(popup, 'disableCaptureButton').mockImplementation(() => {});

      urlTests.forEach(({ url, shouldDisable }) => {
        popup.currentTab = testUtils.createMockTab({ url });
        popup.settings = testUtils.createMockSettings();
        
        jest.clearAllMocks();
        popup.checkPageCapturability();
        
        if (shouldDisable) {
          expect(popup.disableCaptureButton).toHaveBeenCalled();
        }
      });
    });
  });
});
