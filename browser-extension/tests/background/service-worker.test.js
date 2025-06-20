// Unit tests for Service Worker (Background Script)
// Testing extension lifecycle, message handling, and core functionality

// Import required classes for service worker
const SettingsManager = require('../../src/utils/settings-manager.js');
const GitOperations = require('../../src/utils/git-operations.js');
const FileManager = require('../../src/utils/file-manager.js');

let PrismWeaveBackground;

beforeAll(() => {
  // Mock the importScripts function
  global.importScripts = jest.fn();

  // Mock logger
  global.PrismWeaveLogger = {
    createLogger: jest.fn(() => ({
      debug: jest.fn(),
      info: jest.fn(),
      warn: jest.fn(),
      error: jest.fn(),
      group: jest.fn(),
      groupEnd: jest.fn()
    }))
  };

  // Make classes available globally (as they would be with importScripts)
  global.SettingsManager = SettingsManager;
  global.GitOperations = GitOperations;
  global.FileManager = FileManager;

  // Import the PrismWeaveBackground class
  PrismWeaveBackground = require('../../src/background/service-worker.js');
});

describe('PrismWeaveBackground', () => {
  let background;
  let mockSettingsManager;
  let mockGitOperations;
  let mockFileManager;
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Create fresh mock instances with proper method mocks
    mockSettingsManager = {
      loadSettings: jest.fn().mockResolvedValue({}),
      saveSettings: jest.fn().mockResolvedValue({ success: true }),
      resetSettings: jest.fn().mockResolvedValue({ success: true }),
      getDefaultSettings: jest.fn().mockReturnValue({})
    };
      mockGitOperations = {
      initialize: jest.fn().mockResolvedValue(),
      testConnection: jest.fn().mockResolvedValue({ success: true }),
      validateRepository: jest.fn().mockResolvedValue({ success: true, hasWrite: true }),
      saveToRepository: jest.fn().mockResolvedValue({ success: true })
    };
      mockFileManager = {
      createProcessedContent: jest.fn().mockResolvedValue({
        filename: 'test.md',
        content: '# Test Content',
        metadata: {}
      }),
      generateFilename: jest.fn().mockReturnValue('test.md'),
      classifyContent: jest.fn().mockReturnValue('tech'),
      suggestFolder: jest.fn().mockReturnValue('tech'),
      createFrontmatter: jest.fn().mockReturnValue('---\ntitle: Test\n---')
    };
    
    // Create background without calling constructor to avoid automatic initialization
    background = Object.create(PrismWeaveBackground.prototype);
    background.settingsManager = mockSettingsManager;
    background.gitOperations = mockGitOperations;
    background.fileManager = mockFileManager;
    background.isInitialized = false;
  });

  describe('Initialization', () => {
    test('should initialize with core components', () => {
      expect(background.settingsManager).toBeDefined();
      expect(background.gitOperations).toBeDefined();
      expect(background.fileManager).toBeDefined();
      expect(background.isInitialized).toBe(false);
    });

    test('should load initial settings on startup', async () => {
      await background.initializeExtension();

      expect(mockSettingsManager.loadSettings).toHaveBeenCalled();
      expect(background.isInitialized).toBe(true);
    });    test('should handle settings loading errors gracefully', async () => {
      mockSettingsManager.loadSettings.mockRejectedValueOnce(new Error('Settings error'));
      
      // Initialize manually since we skipped constructor
      background.isInitialized = false;
      await background.initializeExtension();

      expect(background.isInitialized).toBe(false);
    });

    test('should setup event listeners', async () => {
      await background.initializeExtension();

      expect(chrome.runtime.onInstalled.addListener).toHaveBeenCalled();
      expect(chrome.runtime.onMessage.addListener).toHaveBeenCalled();
      expect(chrome.action.onClicked.addListener).toHaveBeenCalled();
    });
  });

  describe('Installation Handling', () => {
    test('should handle fresh installation', async () => {
      const installDetails = { reason: 'install' };

      await background.handleInstallation(installDetails);

      expect(mockSettingsManager.resetSettings).toHaveBeenCalled();
    });

    test('should handle extension updates', async () => {
      const updateDetails = { reason: 'update', previousVersion: '0.9.0' };

      await background.handleInstallation(updateDetails);

      expect(mockSettingsManager.resetSettings).toHaveBeenCalled();
    });
  });

  describe('Message Handling', () => {
    let mockSender;
    let mockSendResponse;

    beforeEach(() => {
      mockSender = {
        tab: testUtils.createMockTab()
      };
      mockSendResponse = jest.fn();
    });

    test('should handle GET_SETTINGS message', async () => {
      const message = { action: 'GET_SETTINGS' };

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSettingsManager.loadSettings).toHaveBeenCalled();
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: expect.any(Object)
      });
    });

    test('should handle UPDATE_SETTINGS message', async () => {
      const message = {
        action: 'UPDATE_SETTINGS',
        settings: testUtils.createMockSettings()
      };

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSettingsManager.saveSettings).toHaveBeenCalledWith(message.settings);
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true
      });
    });

    test('should handle TEST_CONNECTION message', async () => {
      const message = {
        action: 'TEST_CONNECTION',
        githubToken: 'test-token',
        githubRepo: 'owner/repo'
      };

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockGitOperations.initialize).toHaveBeenCalled();
      expect(mockGitOperations.testConnection).toHaveBeenCalled();
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: { success: true }
      });
    });

    test('should handle VALIDATE_REPOSITORY message', async () => {
      const message = {
        action: 'VALIDATE_REPOSITORY',
        githubToken: 'test-token',
        githubRepo: 'owner/repo'
      };

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockGitOperations.initialize).toHaveBeenCalled();
      expect(mockGitOperations.validateRepository).toHaveBeenCalled();
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: { success: true, hasWrite: true }
      });
    });    test('should handle CAPTURE_PAGE message', async () => {
      const message = {
        action: 'CAPTURE_PAGE',
        githubToken: 'test-token',
        githubRepo: 'owner/repo'
      };

      // Mock the page capture process using chrome.scripting
      chrome.scripting.executeScript = jest.fn()
        .mockResolvedValueOnce([{ result: 'injected scripts' }])
        .mockResolvedValueOnce([{ result: testUtils.createMockContent() }]);

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(chrome.scripting.executeScript).toHaveBeenCalledTimes(2);
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: expect.any(Object)
      });
    });

    test('should handle CHECK_GITHUB_SETUP message', async () => {
      const message = { action: 'CHECK_GITHUB_SETUP' };

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSettingsManager.loadSettings).toHaveBeenCalled();
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: expect.objectContaining({
          hasToken: expect.any(Boolean),
          hasRepo: expect.any(Boolean),
          tokenValid: expect.any(Boolean),
          repoValid: expect.any(Boolean)
        })
      });
    });    test('should handle HIGHLIGHT_CONTENT message', async () => {
      const message = { action: 'HIGHLIGHT_CONTENT' };
      chrome.scripting.executeScript.mockResolvedValue([{ result: 'highlighted' }]);

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(chrome.scripting.executeScript).toHaveBeenCalled();
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true
      });
    });

    test('should handle unknown message action', async () => {
      const message = { action: 'UNKNOWN_ACTION' };

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: false,
        error: 'Unknown action'
      });
    });    test('should handle message processing errors', async () => {
      const message = { action: 'GET_SETTINGS' };
      mockSettingsManager.loadSettings.mockRejectedValueOnce(new Error('Settings error'));

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: false,
        error: 'Settings error',
        details: undefined
      });
    });

    test('should handle message from popup without sender tab', async () => {
      const message = { action: 'CAPTURE_PAGE' };
      const popupSender = {}; // No tab property
        // Mock active tab query
      chrome.tabs.query.mockResolvedValueOnce([testUtils.createMockTab()]);
      chrome.scripting.executeScript = jest.fn()
        .mockResolvedValueOnce([{ result: 'injected scripts' }])
        .mockResolvedValueOnce([{ result: testUtils.createMockContent() }]);

      await background.handleMessage(message, popupSender, mockSendResponse);

      expect(chrome.tabs.query).toHaveBeenCalledWith({
        active: true,
        currentWindow: true
      });
      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: expect.any(Object)
      });
    });
  });

  describe('Page Capture', () => {    test('should capture page successfully', async () => {
      const tab = testUtils.createMockTab();
      const settings = testUtils.createMockSettings();

      // Mock script injection and content extraction
      chrome.scripting.executeScript = jest.fn()
        .mockResolvedValueOnce([{ result: 'injected scripts' }])
        .mockResolvedValueOnce([{ result: testUtils.createMockContent() }]);

      const result = await background.captureCurrentPage(tab, settings);

      expect(chrome.scripting.executeScript).toHaveBeenCalledTimes(2);
      expect(mockGitOperations.initialize).toHaveBeenCalledWith(settings);
      expect(result).toHaveProperty('filename');
      expect(result).toHaveProperty('content');
      expect(result).toHaveProperty('metadata');
    });

    test('should handle invalid tab', async () => {
      const invalidTab = null;

      await expect(background.captureCurrentPage(invalidTab))
        .rejects.toThrow('Invalid tab');
    });    test('should handle script injection failure', async () => {
      const tab = testUtils.createMockTab();
      chrome.scripting.executeScript.mockRejectedValueOnce(new Error('Injection failed'));

      await expect(background.captureCurrentPage(tab))
        .rejects.toThrow('Injection failed');
    });    test('should handle content extraction failure', async () => {
      const tab = testUtils.createMockTab();
      
      chrome.scripting.executeScript = jest.fn()
        .mockResolvedValueOnce([{ result: 'injected scripts' }])
        .mockRejectedValueOnce(new Error('Extraction failed'));

      await expect(background.captureCurrentPage(tab))
        .rejects.toThrow('Extraction failed');
    });
  });
  describe('Content Processing', () => {
    test('should process page content', async () => {
      const content = testUtils.createMockContent();
      const metadata = { folder: 'tech' };

      const result = await background.processPageContent(content, metadata);

      expect(mockFileManager.suggestFolder).toHaveBeenCalledWith(
        content.textContent,
        expect.any(Object)
      );
      expect(result).toHaveProperty('filename');
      expect(result).toHaveProperty('content');
      expect(result).toHaveProperty('metadata');
    });

    test('should handle content processing errors', async () => {
      const content = testUtils.createMockContent();
      const metadata = { folder: 'tech' };
      
      mockFileManager.suggestFolder.mockImplementation(() => {
        throw new Error('Processing failed');
      });

      await expect(background.processPageContent(content, metadata))
        .rejects.toThrow('Processing failed');
    });
  });

  describe('GitHub Setup Validation', () => {
    test('should validate complete GitHub setup', async () => {
      const settings = testUtils.createMockSettings();
      mockSettingsManager.loadSettings.mockResolvedValueOnce(settings);
      mockGitOperations.testConnection.mockResolvedValueOnce({ success: true });
      mockGitOperations.validateRepository.mockResolvedValueOnce({
        success: true,
        hasWrite: true
      });

      const message = { action: 'CHECK_GITHUB_SETUP' };
      const mockSender = {};
      const mockSendResponse = jest.fn();

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: expect.objectContaining({
          hasToken: true,
          hasRepo: true,
          tokenValid: true,
          repoValid: true,
          repoWriteable: true,
          errors: []
        })
      });
    });    test('should detect missing GitHub configuration', async () => {
      const incompleteSettings = testUtils.createMockSettings({
        githubToken: '',
        githubRepo: '',
        repositoryPath: ''
      });
      mockSettingsManager.loadSettings.mockResolvedValueOnce(incompleteSettings);

      const message = { action: 'CHECK_GITHUB_SETUP' };
      const mockSender = {};
      const mockSendResponse = jest.fn();

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: expect.objectContaining({
          hasToken: false,
          hasRepo: false,
          errors: expect.arrayContaining([
            'GitHub token not configured',
            'Repository path not configured'
          ])
        })
      });
    });

    test('should detect invalid GitHub credentials', async () => {
      const settings = testUtils.createMockSettings();
      mockSettingsManager.loadSettings.mockResolvedValueOnce(settings);
      mockGitOperations.testConnection.mockResolvedValueOnce({
        success: false,
        error: 'Unauthorized'
      });

      const message = { action: 'CHECK_GITHUB_SETUP' };
      const mockSender = {};
      const mockSendResponse = jest.fn();

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: true,
        data: expect.objectContaining({
          tokenValid: false,
          errors: expect.arrayContaining([
            expect.stringContaining('Unauthorized')
          ])
        })
      });
    });
  });
  describe('Content Highlighting', () => {
    test('should highlight content on page', async () => {
      const tab = testUtils.createMockTab();
      chrome.scripting.executeScript.mockResolvedValue([{ result: 'highlighted' }]);

      await background.highlightPageContent(tab);

      expect(chrome.scripting.executeScript).toHaveBeenCalledWith(
        expect.objectContaining({
          target: { tabId: tab.id },
          files: ['src/utils/content-extractor.js']
        })
      );
    });

    test('should handle highlighting errors', async () => {
      const tab = testUtils.createMockTab();
      chrome.scripting.executeScript.mockRejectedValueOnce(new Error('Highlighting failed'));

      await expect(background.highlightPageContent(tab))
        .rejects.toThrow('Highlighting failed');
    });
  });

  describe('Error Handling and Edge Cases', () => {    test('should handle chrome extension context invalidation', async () => {
      mockSettingsManager.loadSettings.mockRejectedValueOnce(new Error('Extension context invalidated'));
      
      const message = { action: 'GET_SETTINGS' };
      const mockSender = {};
      const mockSendResponse = jest.fn();

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: false,
        error: 'Extension context invalidated',
        details: undefined
      });
    });

    test('should handle network connectivity issues', async () => {
      mockGitOperations.testConnection.mockRejectedValueOnce(new Error('Network error'));
      
      const message = { action: 'TEST_CONNECTION' };
      const mockSender = {};
      const mockSendResponse = jest.fn();

      await background.handleMessage(message, mockSender, mockSendResponse);

      expect(mockSendResponse).toHaveBeenCalledWith({
        success: false,
        error: expect.stringContaining('Network error')
      });
    });

    test('should handle concurrent message processing', async () => {
      const message1 = { action: 'GET_SETTINGS' };
      const message2 = { action: 'TEST_CONNECTION' };
      const mockSender = {};
      const mockSendResponse1 = jest.fn();
      const mockSendResponse2 = jest.fn();

      // Process messages concurrently
      await Promise.all([
        background.handleMessage(message1, mockSender, mockSendResponse1),
        background.handleMessage(message2, mockSender, mockSendResponse2)
      ]);

      expect(mockSendResponse1).toHaveBeenCalledWith({
        success: true,
        data: expect.any(Object)
      });
      expect(mockSendResponse2).toHaveBeenCalledWith({
        success: true,
        data: expect.any(Object)
      });
    });
  });
});
