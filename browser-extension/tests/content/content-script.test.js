// Unit tests for Content Script
// Testing content script functionality, message handling, and page interaction

beforeAll(() => {
  // Mock DOM APIs
  global.document = {
    addEventListener: jest.fn(),
    createElement: jest.fn(() => ({
      style: {},
      textContent: '',
      innerHTML: '',
      classList: {
        add: jest.fn(),
        remove: jest.fn(),
        contains: jest.fn(() => false)
      },
      setAttribute: jest.fn(),
      getAttribute: jest.fn(),
      appendChild: jest.fn(),
      removeChild: jest.fn()
    })),
    body: {
      appendChild: jest.fn(),
      removeChild: jest.fn(),
      style: {}
    },
    querySelector: jest.fn(),
    querySelectorAll: jest.fn(() => []),
    title: 'Test Page',
    URL: 'https://example.com/test'
  };

  // Import the real ContentExtractor class
  const ContentExtractorClass = require('../../src/utils/content-extractor.js');
  
  // Mock window.ContentExtractor with the actual class
  global.window = {
    ContentExtractor: ContentExtractorClass
  };
});

// Import the PrismWeaveContent class
const PrismWeaveContent = require('../../src/content/content-script.js');

describe('PrismWeaveContent', () => {
  let contentScript;
  let mockContentExtractor;

  beforeEach(() => {
    jest.clearAllMocks();
    
    mockContentExtractor = new window.ContentExtractor();
    contentScript = new PrismWeaveContent();
    contentScript.contentExtractor = mockContentExtractor;
  });

  describe('Initialization', () => {
    test('should initialize with default state', () => {
      expect(contentScript.isCapturing).toBe(false);
      expect(contentScript.contentExtractor).toBeDefined();
    });

    test('should setup message listener', () => {
      expect(chrome.runtime.onMessage.addListener).toHaveBeenCalled();
    });

    test('should setup keyboard event listeners', () => {
      expect(document.addEventListener).toHaveBeenCalledWith(
        'keydown',
        expect.any(Function)
      );
    });

    test('should create capture indicator', () => {
      expect(document.createElement).toHaveBeenCalled();
      expect(document.body.appendChild).toHaveBeenCalled();
    });
  });

  describe('Message Handling', () => {
    let mockSender;
    let mockSendResponse;

    beforeEach(() => {
      mockSender = { tab: testUtils.createMockTab() };
      mockSendResponse = jest.fn();
    });

    test('should handle EXTRACT_CONTENT message', async () => {
      const message = { action: 'EXTRACT_CONTENT' };

      await contentScript.handleMessage(message, mockSender, mockSendResponse);

      expect(mockContentExtractor.extractPageContent).toHaveBeenCalledWith(document);
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: expect.any(Object)
      });
    });

    test('should handle HIGHLIGHT_CONTENT message', async () => {
      const message = { action: 'HIGHLIGHT_CONTENT' };

      await contentScript.handleMessage(message, mockSender, mockSendResponse);

      expect(mockContentExtractor.highlightContent).toHaveBeenCalled();
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true
      });
    });

    test('should handle ANALYZE_PAGE message', async () => {
      const message = { action: 'ANALYZE_PAGE' };

      await contentScript.handleMessage(message, mockSender, mockSendResponse);

      expect(mockContentExtractor.analyzePageStructure).toHaveBeenCalledWith(document);
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: { hasMainContent: true }
      });
    });

    test('should handle SHOW_CAPTURE_INDICATOR message', async () => {
      const message = { action: 'SHOW_CAPTURE_INDICATOR' };

      await contentScript.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true
      });
    });

    test('should handle HIDE_CAPTURE_INDICATOR message', async () => {
      const message = { action: 'HIDE_CAPTURE_INDICATOR' };

      await contentScript.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true
      });
    });

    test('should handle unknown message action', async () => {
      const message = { action: 'UNKNOWN_ACTION' };

      await contentScript.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: false,
        error: 'Unknown action: UNKNOWN_ACTION'
      });
    });

    test('should handle message processing errors', async () => {
      const message = { action: 'EXTRACT_CONTENT' };
      mockContentExtractor.extractPageContent.mockImplementation(() => {
        throw new Error('Extraction failed');
      });

      await contentScript.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: false,
        error: 'Extraction failed'
      });
    });
  });

  describe('Keyboard Shortcuts', () => {
    test('should handle Ctrl+Shift+S for page capture', () => {
      const captureEvent = {
        ctrlKey: true,
        shiftKey: true,
        key: 'S',
        preventDefault: jest.fn()
      };

      contentScript.captureCurrentPage = jest.fn();

      // Simulate keydown event
      const keydownHandler = document.addEventListener.mock.calls.find(
        call => call[0] === 'keydown'
      )[1];

      keydownHandler(captureEvent);

      expect(captureEvent.preventDefault).toHaveBeenCalled();
      expect(contentScript.captureCurrentPage).toHaveBeenCalled();
    });

    test('should handle Ctrl+Shift+H for content highlighting', () => {
      const highlightEvent = {
        ctrlKey: true,
        shiftKey: true,
        key: 'H',
        preventDefault: jest.fn()
      };

      contentScript.highlightMainContent = jest.fn();

      // Simulate keydown event
      const keydownHandler = document.addEventListener.mock.calls.find(
        call => call[0] === 'keydown'
      )[1];

      keydownHandler(highlightEvent);

      expect(highlightEvent.preventDefault).toHaveBeenCalled();
      expect(contentScript.highlightMainContent).toHaveBeenCalled();
    });

    test('should ignore other keyboard combinations', () => {
      const normalEvent = {
        ctrlKey: false,
        shiftKey: false,
        key: 'A',
        preventDefault: jest.fn()
      };

      contentScript.captureCurrentPage = jest.fn();

      // Simulate keydown event
      const keydownHandler = document.addEventListener.mock.calls.find(
        call => call[0] === 'keydown'
      )[1];

      keydownHandler(normalEvent);

      expect(normalEvent.preventDefault).not.toHaveBeenCalled();
      expect(contentScript.captureCurrentPage).not.toHaveBeenCalled();
    });
  });

  describe('Content Extraction', () => {
    test('should extract page content', async () => {
      const extractedContent = await contentScript.extractPageContent();

      expect(mockContentExtractor.extractPageContent).toHaveBeenCalledWith(document);
      expect(extractedContent).toEqual(testUtils.createMockContent());
    });

    test('should handle content extraction errors', async () => {
      mockContentExtractor.extractPageContent.mockImplementation(() => {
        throw new Error('DOM parsing failed');
      });

      const result = await contentScript.extractPageContent();

      expect(result).toHaveProperty('error');
      expect(result.error).toContain('DOM parsing failed');
    });

    test('should include additional metadata in extraction', async () => {
      const extractedContent = await contentScript.extractPageContent();

      expect(extractedContent).toHaveProperty('captureTimestamp');
      expect(extractedContent).toHaveProperty('userAgent');
      expect(extractedContent).toHaveProperty('viewport');
    });
  });

  describe('Content Highlighting', () => {
    test('should highlight main content', async () => {
      await contentScript.highlightMainContent();

      expect(mockContentExtractor.highlightContent).toHaveBeenCalledWith(document);
    });

    test('should handle highlighting errors gracefully', async () => {
      mockContentExtractor.highlightContent.mockImplementation(() => {
        throw new Error('Highlighting failed');
      });

      await expect(contentScript.highlightMainContent()).resolves.not.toThrow();
    });

    test('should add visual highlighting to page', async () => {
      const mockElement = {
        style: {},
        classList: {
          add: jest.fn(),
          remove: jest.fn()
        }
      };

      document.querySelector.mockReturnValue(mockElement);

      await contentScript.highlightMainContent();

      expect(mockElement.classList.add).toHaveBeenCalledWith('prismweave-highlighted');
    });

    test('should remove highlighting after timeout', async () => {
      jest.useFakeTimers();
      
      const mockElement = {
        style: {},
        classList: {
          add: jest.fn(),
          remove: jest.fn()
        }
      };

      document.querySelector.mockReturnValue(mockElement);

      await contentScript.highlightMainContent();
      
      jest.advanceTimersByTime(3000);

      expect(mockElement.classList.remove).toHaveBeenCalledWith('prismweave-highlighted');
      
      jest.useRealTimers();
    });
  });

  describe('Capture Indicator', () => {
    test('should create capture indicator element', () => {
      contentScript.createCaptureIndicator();

      expect(document.createElement).toHaveBeenCalledWith('div');
      expect(document.body.appendChild).toHaveBeenCalled();
    });

    test('should show capture indicator', () => {
      contentScript.showCaptureIndicator('Capturing page...');

      expect(contentScript.captureIndicator.style.display).toBe('block');
      expect(contentScript.captureIndicator.textContent).toBe('Capturing page...');
    });

    test('should hide capture indicator', () => {
      contentScript.hideCaptureIndicator();

      expect(contentScript.captureIndicator.style.display).toBe('none');
    });

    test('should update indicator with progress', () => {
      contentScript.updateCaptureProgress(50, 'Processing content...');

      expect(contentScript.captureIndicator.textContent).toContain('50%');
      expect(contentScript.captureIndicator.textContent).toContain('Processing content...');
    });
  });

  describe('Page Analysis', () => {
    test('should analyze page structure', async () => {
      const analysis = await contentScript.analyzePageStructure();

      expect(mockContentExtractor.analyzePageStructure).toHaveBeenCalledWith(document);
      expect(analysis).toHaveProperty('hasMainContent', true);
    });

    test('should detect page type', () => {
      // Mock different page types
      document.querySelector
        .mockReturnValueOnce({ tagName: 'ARTICLE' }) // Article page
        .mockReturnValueOnce(null)
        .mockReturnValueOnce({ className: 'blog-post' }); // Blog page

      expect(contentScript.detectPageType()).toBe('article');
      expect(contentScript.detectPageType()).toBe('blog');
      expect(contentScript.detectPageType()).toBe('unknown');
    });

    test('should check if page is capturable', () => {
      // Test different URL schemes
      expect(contentScript.isPageCapturable('https://example.com')).toBe(true);
      expect(contentScript.isPageCapturable('http://example.com')).toBe(true);
      expect(contentScript.isPageCapturable('chrome://settings')).toBe(false);
      expect(contentScript.isPageCapturable('chrome-extension://id/popup.html')).toBe(false);
      expect(contentScript.isPageCapturable('about:blank')).toBe(false);
    });
  });

  describe('User Interactions', () => {
    test('should capture current page via keyboard shortcut', async () => {
      chrome.runtime.sendMessage.mockImplementation((message, callback) => {
        callback({ success: true });
      });

      await contentScript.captureCurrentPage();

      expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({
        action: 'CAPTURE_PAGE',
        source: 'content-script'
      });
    });

    test('should handle capture errors gracefully', async () => {
      chrome.runtime.sendMessage.mockImplementation((message, callback) => {
        callback({ success: false, error: 'Capture failed' });
      });

      await contentScript.captureCurrentPage();

      expect(contentScript.captureIndicator.textContent).toContain('Error');
    });

    test('should provide visual feedback during capture', async () => {
      let messageHandler;
      chrome.runtime.sendMessage.mockImplementation((message, callback) => {
        messageHandler = callback;
        // Don't call immediately to simulate async operation
      });

      const capturePromise = contentScript.captureCurrentPage();

      expect(contentScript.captureIndicator.style.display).toBe('block');
      expect(contentScript.isCapturing).toBe(true);

      // Simulate successful response
      messageHandler({ success: true });
      await capturePromise;

      expect(contentScript.isCapturing).toBe(false);
    });
  });

  describe('Error Handling', () => {
    test('should handle content extractor loading failure', async () => {
      window.ContentExtractor = undefined;

      await contentScript.loadContentExtractor();

      expect(contentScript.contentExtractor).toBeNull();
    });

    test('should handle DOM manipulation errors', () => {
      document.body.appendChild.mockImplementation(() => {
        throw new Error('DOM error');
      });

      expect(() => contentScript.createCaptureIndicator()).not.toThrow();
    });

    test('should handle chrome runtime errors', async () => {
      chrome.runtime.lastError = { message: 'Extension context invalidated' };
      chrome.runtime.sendMessage.mockImplementation((message, callback) => {
        callback({ success: false, error: 'Runtime error' });
      });

      await contentScript.captureCurrentPage();

      expect(contentScript.captureIndicator.textContent).toContain('Error');
    });
  });

  describe('Integration with Background Script', () => {
    test('should send extracted content to background', async () => {
      const message = { action: 'EXTRACT_CONTENT' };
      const mockSender = {};
      const mockSendResponse = jest.fn();

      await contentScript.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: expect.objectContaining({
          title: expect.any(String),
          content: expect.any(String),
          url: expect.any(String),
          timestamp: expect.any(String)
        })
      });
    });

    test('should communicate capture progress', async () => {
      chrome.runtime.sendMessage.mockImplementation((message) => {
        if (message.action === 'CAPTURE_PROGRESS') {
          expect(message).toHaveProperty('progress');
          expect(message).toHaveProperty('status');
        }
      });

      contentScript.reportCaptureProgress(25, 'Extracting content...');

      expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({
        action: 'CAPTURE_PROGRESS',
        progress: 25,
        status: 'Extracting content...'
      });
    });
  });

  describe('Performance Considerations', () => {
    test('should debounce rapid capture requests', async () => {
      jest.useFakeTimers();
      
      const captureSpy = jest.spyOn(contentScript, 'captureCurrentPage');
      
      // Rapid fire multiple capture requests
      contentScript.captureCurrentPage();
      contentScript.captureCurrentPage();
      contentScript.captureCurrentPage();

      jest.advanceTimersByTime(500);

      // Should only call once due to debouncing
      expect(captureSpy).toHaveBeenCalledTimes(1);
      
      jest.useRealTimers();
    });

    test('should clean up resources on page unload', () => {
      const beforeUnloadHandler = jest.fn();
      window.addEventListener = jest.fn((event, handler) => {
        if (event === 'beforeunload') {
          beforeUnloadHandler.mockImplementation(handler);
        }
      });

      contentScript.setupCleanup();

      beforeUnloadHandler();

      expect(contentScript.isCapturing).toBe(false);
    });
  });
});
