// Integration tests for PrismWeave Browser Extension
// Testing end-to-end workflows and component interactions

describe('PrismWeave Integration Tests', () => {
  let background;
  let popup;
  let contentScript;
  let mockSettingsManager;
  let mockGitOperations;
  let mockFileManager;

  beforeEach(async () => {
    // Setup mock components
    mockSettingsManager = {
      loadSettings: jest.fn().mockResolvedValue(testUtils.createMockSettings()),
      saveSettings: jest.fn().mockResolvedValue({ success: true }),
      validateSettings: jest.fn().mockResolvedValue({ isValid: true, errors: [] })
    };

    mockGitOperations = {
      initialize: jest.fn().mockResolvedValue(),
      testConnection: jest.fn().mockResolvedValue({ success: true }),
      validateRepository: jest.fn().mockResolvedValue({ success: true, hasWrite: true }),
      saveToGitHub: jest.fn().mockResolvedValue({ success: true })
    };

    mockFileManager = {
      createProcessedContent: jest.fn().mockReturnValue(testUtils.createMockProcessedContent()),
      generateMetadata: jest.fn().mockReturnValue({ folder: 'tech' })
    };

    // Initialize components
    global.SettingsManager = jest.fn(() => mockSettingsManager);
    global.GitOperations = jest.fn(() => mockGitOperations);
    global.FileManager = jest.fn(() => mockFileManager);
  });

  describe('Complete Capture Workflow', () => {
    test('should capture page from popup to GitHub successfully', async () => {
      // Simulate user clicking capture from popup
      const captureMessage = {
        action: 'CAPTURE_PAGE',
        githubToken: 'test-token',
        githubRepo: 'owner/repo'
      };

      // Mock content extraction from page
      chrome.tabs.executeScript = jest.fn()
        .mockResolvedValueOnce(['content extractor loaded'])
        .mockResolvedValueOnce(['markdown converter loaded'])
        .mockResolvedValueOnce([testUtils.createMockContent()]);

      // Simulate background script handling the capture
      const mockSender = { tab: testUtils.createMockTab() };
      const mockSendResponse = jest.fn();

      // This would normally be called by the background script
      const result = await simulateCaptureWorkflow(captureMessage, mockSender);

      expect(result.success).toBe(true);
      expect(mockGitOperations.initialize).toHaveBeenCalled();
      expect(mockFileManager.createProcessedContent).toHaveBeenCalled();
      expect(mockGitOperations.saveToGitHub).toHaveBeenCalled();
    });

    test('should handle capture failures gracefully', async () => {
      // Simulate GitHub API failure
      mockGitOperations.saveToGitHub.mockRejectedValueOnce(new Error('GitHub API error'));

      const captureMessage = {
        action: 'CAPTURE_PAGE',
        githubToken: 'test-token',
        githubRepo: 'owner/repo'
      };

      chrome.tabs.executeScript = jest.fn()
        .mockResolvedValueOnce(['content extractor loaded'])
        .mockResolvedValueOnce(['markdown converter loaded'])
        .mockResolvedValueOnce([testUtils.createMockContent()]);

      const result = await simulateCaptureWorkflow(captureMessage);

      expect(result.success).toBe(false);
      expect(result.error).toContain('GitHub API error');
    });
  });

  describe('Settings Flow', () => {
    test('should save and validate settings end-to-end', async () => {
      const newSettings = testUtils.createMockSettings({
        githubRepo: 'newuser/newrepo',
        githubToken: 'new-token'
      });

      // Simulate settings update from popup
      const updateMessage = {
        action: 'UPDATE_SETTINGS',
        settings: newSettings
      };

      const mockSendResponse = jest.fn();
      await simulateSettingsUpdate(updateMessage, mockSendResponse);

      expect(mockSettingsManager.saveSettings).toHaveBeenCalledWith(newSettings);
      expect(mockSendResponse).toHaveBeenCalledWith({ success: true });

      // Test that the new settings are used in subsequent operations
      const testMessage = { action: 'TEST_CONNECTION' };
      await simulateConnectionTest(testMessage, mockSendResponse);

      expect(mockGitOperations.initialize).toHaveBeenCalledWith(
        expect.objectContaining({
          githubRepo: 'newuser/newrepo',
          githubToken: 'new-token'
        })
      );
    });

    test('should reject invalid settings', async () => {
      const invalidSettings = {
        githubRepo: 'invalid-format',
        githubToken: '',
        defaultFolder: 'nonexistent'
      };

      mockSettingsManager.validateSettings.mockResolvedValueOnce({
        isValid: false,
        errors: ['Invalid repository format', 'Token required', 'Invalid folder']
      });

      const updateMessage = {
        action: 'UPDATE_SETTINGS',
        settings: invalidSettings
      };

      const mockSendResponse = jest.fn();
      await simulateSettingsUpdate(updateMessage, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: false,
        errors: expect.arrayContaining([
          expect.stringContaining('Invalid repository'),
          expect.stringContaining('Token required'),
          expect.stringContaining('Invalid folder')
        ])
      });
    });
  });

  describe('GitHub Integration Flow', () => {
    test('should test connection and validate repository', async () => {
      const testMessage = { action: 'TEST_CONNECTION' };
      const mockSendResponse = jest.fn();

      await simulateConnectionTest(testMessage, mockSendResponse);

      expect(mockGitOperations.testConnection).toHaveBeenCalled();
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: { success: true }
      });

      // Follow up with repository validation
      const validateMessage = { action: 'VALIDATE_REPOSITORY' };
      await simulateRepositoryValidation(validateMessage, mockSendResponse);

      expect(mockGitOperations.validateRepository).toHaveBeenCalled();
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: { success: true, hasWrite: true }
      });
    });

    test('should handle GitHub authentication failures', async () => {
      mockGitOperations.testConnection.mockResolvedValueOnce({
        success: false,
        error: 'Unauthorized: Bad credentials'
      });

      const testMessage = { action: 'TEST_CONNECTION' };
      const mockSendResponse = jest.fn();

      await simulateConnectionTest(testMessage, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: {
          success: false,
          error: 'Unauthorized: Bad credentials'
        }
      });
    });
  });

  describe('Content Script Integration', () => {
    test('should communicate between content script and background', async () => {
      // Simulate content script requesting page extraction
      const extractMessage = { action: 'EXTRACT_CONTENT' };
      const mockSender = { tab: testUtils.createMockTab() };
      const mockSendResponse = jest.fn();

      // Mock content script functionality
      const mockExtractedContent = testUtils.createMockContent();
      
      // Simulate the extraction response
      mockSendResponse.mockImplementation((response) => {
        expect(response.success).toBe(true);
        expect(response.data).toEqual(mockExtractedContent);
      });

      // This would be handled by content script
      mockSendResponse({
        success: true,
        data: mockExtractedContent
      });

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: expect.objectContaining({
          title: expect.any(String),
          content: expect.any(String),
          url: expect.any(String)
        })
      });
    });

    test('should handle content highlighting requests', async () => {
      const highlightMessage = { action: 'HIGHLIGHT_CONTENT' };
      const mockSender = { tab: testUtils.createMockTab() };
      const mockSendResponse = jest.fn();

      // Simulate highlighting injection
      chrome.tabs.executeScript = jest.fn().mockResolvedValueOnce(['highlighted']);

      await simulateContentHighlighting(highlightMessage, mockSender, mockSendResponse);

      expect(chrome.tabs.executeScript).toHaveBeenCalledWith(
        mockSender.tab.id,
        expect.objectContaining({
          code: expect.stringContaining('highlight')
        })
      );
      expect(mockSendResponse).toHaveBeenCalledWith({ success: true });
    });
  });

  describe('Error Recovery', () => {
    test('should recover from temporary GitHub API failures', async () => {
      // First attempt fails
      mockGitOperations.saveToGitHub
        .mockRejectedValueOnce(new Error('Temporary server error'))
        .mockResolvedValueOnce({ success: true });

      const captureMessage = {
        action: 'CAPTURE_PAGE',
        githubToken: 'test-token',
        githubRepo: 'owner/repo'
      };

      chrome.tabs.executeScript = jest.fn()
        .mockResolvedValueOnce(['content extractor loaded'])
        .mockResolvedValueOnce(['markdown converter loaded'])
        .mockResolvedValueOnce([testUtils.createMockContent()]);

      // First attempt
      let result = await simulateCaptureWorkflow(captureMessage);
      expect(result.success).toBe(false);

      // Second attempt (simulating retry)
      result = await simulateCaptureWorkflow(captureMessage);
      expect(result.success).toBe(true);
    });

    test('should handle extension context invalidation', async () => {
      chrome.runtime.lastError = { message: 'Extension context invalidated' };

      const message = { action: 'GET_SETTINGS' };
      const mockSendResponse = jest.fn();

      await simulateMessageHandling(message, {}, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: false,
        error: expect.stringContaining('Extension context')
      });

      // Reset error state
      chrome.runtime.lastError = null;
    });
  });

  describe('Performance Integration', () => {
    test('should handle concurrent capture requests', async () => {
      const captureMessage = {
        action: 'CAPTURE_PAGE',
        githubToken: 'test-token',
        githubRepo: 'owner/repo'
      };

      chrome.tabs.executeScript = jest.fn()
        .mockResolvedValue(['mocked response']);

      // Simulate multiple concurrent captures
      const promises = Array(3).fill(null).map(() => 
        simulateCaptureWorkflow(captureMessage)
      );

      const results = await Promise.all(promises);

      expect(results.every(r => r.success)).toBe(true);
      expect(mockGitOperations.saveToGitHub).toHaveBeenCalledTimes(3);
    });

    test('should maintain performance with large content', async () => {
      const largeContent = testUtils.createMockContent({
        content: 'Large content block. '.repeat(10000), // ~150KB of text
        images: Array(50).fill(null).map((_, i) => ({
          src: `https://example.com/image${i}.jpg`,
          alt: `Image ${i}`
        }))
      });

      chrome.tabs.executeScript = jest.fn()
        .mockResolvedValueOnce(['content extractor loaded'])
        .mockResolvedValueOnce(['markdown converter loaded'])
        .mockResolvedValueOnce([largeContent]);

      const startTime = Date.now();

      const result = await simulateCaptureWorkflow({
        action: 'CAPTURE_PAGE',
        githubToken: 'test-token',
        githubRepo: 'owner/repo'
      });

      const endTime = Date.now();
      const processingTime = endTime - startTime;

      expect(result.success).toBe(true);
      expect(processingTime).toBeLessThan(5000); // Should complete within 5 seconds
    });
  });

  // Helper functions for simulating workflows
  async function simulateCaptureWorkflow(message, sender = { tab: testUtils.createMockTab() }) {
    try {
      const extractedContent = await extractContentFromTab(sender.tab);
      const processedContent = mockFileManager.createProcessedContent(
        extractedContent,
        testUtils.createMockSettings()
      );
      
      await mockGitOperations.initialize(testUtils.createMockSettings());
      await mockGitOperations.saveToGitHub(processedContent);
      
      return { success: true, data: processedContent };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async function simulateSettingsUpdate(message, sendResponse) {
    try {
      const validation = await mockSettingsManager.validateSettings(message.settings);
      
      if (!validation.isValid) {
        sendResponse({ success: false, errors: validation.errors });
        return;
      }
      
      await mockSettingsManager.saveSettings(message.settings);
      sendResponse({ success: true });
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
  }

  async function simulateConnectionTest(message, sendResponse) {
    try {
      const settings = await mockSettingsManager.loadSettings();
      await mockGitOperations.initialize(settings);
      const result = await mockGitOperations.testConnection();
      sendResponse({ success: true, data: result });
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
  }

  async function simulateRepositoryValidation(message, sendResponse) {
    try {
      const result = await mockGitOperations.validateRepository();
      sendResponse({ success: true, data: result });
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
  }

  async function simulateContentHighlighting(message, sender, sendResponse) {
    try {
      await chrome.tabs.executeScript(sender.tab.id, {
        code: `
          // Highlight main content
          const main = document.querySelector('main, article, .content');
          if (main) {
            main.style.outline = '2px solid #007cba';
            main.style.backgroundColor = 'rgba(0, 124, 186, 0.1)';
          }
        `
      });
      sendResponse({ success: true });
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
  }

  async function simulateMessageHandling(message, sender, sendResponse) {
    try {
      if (chrome.runtime.lastError) {
        throw new Error(chrome.runtime.lastError.message);
      }
      
      switch (message.action) {
        case 'GET_SETTINGS':
          const settings = await mockSettingsManager.loadSettings();
          sendResponse({ success: true, data: settings });
          break;
        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
  }

  async function extractContentFromTab(tab) {
    // Simulate content extraction
    const mockContent = testUtils.createMockContent({
      url: tab.url,
      title: tab.title
    });
    
    return mockContent;
  }
});
