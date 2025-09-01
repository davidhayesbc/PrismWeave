// Tests for PDF capture functionality

import { PrismWeavePopup } from '../popup/popup';
import { MESSAGE_TYPES } from '../types/types';
import { mockChromeAPIs } from './test-helpers';

describe('PDF Capture Functionality', () => {
  let popup: PrismWeavePopup;
  let mockChrome: any;
  let mockDocument: any;
  let mockWindow: any;

  beforeEach(async () => {
    // Set up Chrome API mocks
    mockChrome = mockChromeAPIs();

    // Set up document and window mocks
    mockDocument = {
      getElementById: jest.fn(),
      body: { innerHTML: '' },
    };

    mockWindow = {
      open: jest.fn(),
    } as any;

    // Mock DOM elements
    document.body.innerHTML = `
      <button id="capture-content" class="action-button">Capture Content</button>
      <div id="status-container"></div>
      <div id="status-title"></div>
      <div id="status-message"></div>
      <div id="progress-bar"></div>
    `;

    // Mock the initialization calls that popup makes
    mockChrome.tabs.query.mockImplementation((queryInfo: any, callback: Function) => {
      callback([{ id: 1, url: 'https://example.com/test', title: 'Test Page' }]);
    });

    mockChrome.runtime.sendMessage.mockImplementation((message: any, callback: Function) => {
      if (message.type === 'GET_SETTINGS' || message === 'GET_SETTINGS') {
        callback({ success: true, data: { githubToken: 'test-token', githubRepo: 'user/repo' } });
      }
    });

    // Create popup instance with dependency injection
    popup = new PrismWeavePopup({
      chrome: mockChrome as any,
      document: mockDocument as any,
      window: mockWindow as any,
    });

    // Wait for initialization to complete
    await new Promise(resolve => setTimeout(resolve, 100));

    // Clear the mocks after initialization
    jest.clearAllMocks();
  });

  describe('isPDFPage detection', () => {
    test('should detect PDF URLs ending with .pdf', () => {
      // Set up mock tab with PDF URL
      (popup as any).currentTab = {
        id: 1,
        url: 'https://example.com/document.pdf',
        title: 'Document PDF',
      };

      const isPDF = popup.isPDFPageForTest();
      expect(isPDF).toBe(true);
    });

    test('should detect PDF URLs with .pdf in query parameters', () => {
      // Set up mock tab with PDF URL
      (popup as any).currentTab = {
        id: 1,
        url: 'https://example.com/view?file=document.pdf&page=1',
        title: 'Document PDF',
      };

      const isPDF = popup.isPDFPageForTest();
      expect(isPDF).toBe(true);
    });

    test('should detect PDF URLs with fragment identifier', () => {
      // Set up mock tab with PDF URL
      (popup as any).currentTab = {
        id: 1,
        url: 'https://example.com/document.pdf#page=1',
        title: 'Document PDF',
      };

      const isPDF = popup.isPDFPageForTest();
      expect(isPDF).toBe(true);
    });

    test('should not detect non-PDF URLs', () => {
      // Set up mock tab with regular URL
      (popup as any).currentTab = {
        id: 1,
        url: 'https://example.com/article.html',
        title: 'Regular Article',
      };

      const isPDF = popup.isPDFPageForTest();
      expect(isPDF).toBe(false);
    });

    test('should handle null/undefined URL', () => {
      // Set up mock tab with no URL
      (popup as any).currentTab = {
        id: 1,
        url: null,
        title: 'No URL',
      };

      const isPDF = popup.isPDFPageForTest();
      expect(isPDF).toBe(false);
    });

    test('should handle missing currentTab', () => {
      // Set up mock with no current tab
      (popup as any).currentTab = null;

      const isPDF = popup.isPDFPageForTest();
      expect(isPDF).toBe(false);
    });
  });

  describe('Unified capture button with PDF detection', () => {
    test('should enable unified capture button for PDF pages', () => {
      // Set up mock tab with PDF URL
      (popup as any).currentTab = {
        id: 1,
        url: 'https://example.com/document.pdf',
        title: 'Document PDF',
      };

      // Call checkPageCapturability
      (popup as any).checkPageCapturability();

      // Check if unified capture button is enabled (it should handle PDF detection internally)
      const captureButton = document.getElementById('capture-content') as HTMLButtonElement;
      expect(captureButton.disabled).toBe(false);
    });

    test('should enable unified capture button for non-PDF pages', () => {
      // Set up mock tab with regular URL
      (popup as any).currentTab = {
        id: 1,
        url: 'https://example.com/article.html',
        title: 'Regular Article',
      };

      // Call checkPageCapturability
      (popup as any).checkPageCapturability();

      // Check if unified capture button is enabled (it should handle content detection internally)
      const captureButton = document.getElementById('capture-content') as HTMLButtonElement;
      expect(captureButton.disabled).toBe(false);
    });
  });

  describe('PDF capture flow', () => {
    test('should handle successful PDF capture', async () => {
      // Set up mock tab with PDF URL
      (popup as any).currentTab = {
        id: 1,
        url: 'https://example.com/document.pdf',
        title: 'Document PDF',
      };

      // Set up mock settings
      (popup as any).settings = {
        githubToken: 'test-token',
        githubRepo: 'user/repo',
      };

      // Mock successful responses in sequence
      mockChrome.runtime.sendMessage
        .mockImplementationOnce((message: any, callback: Function) => {
          // First call: CHECK_PDF
          if (message.type === MESSAGE_TYPES.CHECK_PDF) {
            callback({ success: true, data: { isPDF: true } });
          }
        })
        .mockImplementationOnce((message: any, callback: Function) => {
          // Second call: CAPTURE_PDF
          if (message.type === MESSAGE_TYPES.CAPTURE_PDF) {
            callback({ success: true, data: { filename: 'document.pdf' } });
          }
        });

      // Test PDF capture
      await popup.capturePDFForTest();

      // Verify messages were sent
      expect(mockChrome.runtime.sendMessage).toHaveBeenCalledTimes(2);

      // Verify CHECK_PDF was called first
      expect(mockChrome.runtime.sendMessage).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({
          type: MESSAGE_TYPES.CHECK_PDF,
          data: expect.objectContaining({
            tabId: 1,
            url: 'https://example.com/document.pdf',
          }),
        }),
        expect.any(Function)
      );

      // Verify CAPTURE_PDF was called second
      expect(mockChrome.runtime.sendMessage).toHaveBeenNthCalledWith(
        2,
        expect.objectContaining({
          type: MESSAGE_TYPES.CAPTURE_PDF,
          data: expect.objectContaining({
            tabId: 1,
            url: 'https://example.com/document.pdf',
            settings: expect.any(Object),
          }),
        }),
        expect.any(Function)
      );
    }, 15000);

    test('should handle non-PDF pages gracefully', async () => {
      // Set up mock tab with regular URL
      (popup as any).currentTab = {
        id: 1,
        url: 'https://example.com/article.html',
        title: 'Regular Article',
      };

      // Set up mock settings
      (popup as any).settings = {
        githubToken: 'test-token',
        githubRepo: 'user/repo',
      };

      // Mock CHECK_PDF response indicating not a PDF
      mockChrome.runtime.sendMessage.mockImplementationOnce((message: any, callback: Function) => {
        // CHECK_PDF call
        if (message.type === MESSAGE_TYPES.CHECK_PDF) {
          callback({ success: true, data: { isPDF: false } });
        }
      });

      // Test PDF capture on non-PDF page
      await popup.capturePDFForTest();

      // Verify CHECK_PDF message was sent (no CAPTURE_PDF)
      expect(mockChrome.runtime.sendMessage).toHaveBeenCalledTimes(1);
      expect(mockChrome.runtime.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          type: MESSAGE_TYPES.CHECK_PDF,
        }),
        expect.any(Function)
      );
    }, 15000);

    test('should handle missing settings', async () => {
      // Set up mock tab with PDF URL
      (popup as any).currentTab = {
        id: 1,
        url: 'https://example.com/document.pdf',
        title: 'Document PDF',
      };

      // Set up incomplete settings (missing GitHub token)
      (popup as any).settings = {
        githubRepo: 'user/repo',
      };

      // Test PDF capture with incomplete settings
      await popup.capturePDFForTest();

      // Verify no messages were sent due to settings validation failure
      expect(mockChrome.runtime.sendMessage).not.toHaveBeenCalled();
    }, 15000);
  });
});
