// PrismWeave Background Service Worker
// Handles extension lifecycle, Git operations, and file management

// Import utilities and dependencies
importScripts('../utils/logger.js');
importScripts('../utils/log-config.js');
importScripts('../utils/shared-utils.js');
importScripts('../utils/settings-manager.js');
importScripts('../utils/markdown-converter.js');
importScripts('../utils/git-operations.js');
importScripts('../utils/file-manager.js');

// Initialize logger for background
const logger = self.PrismWeaveLogger ? 
  self.PrismWeaveLogger.createLogger('Background') : 
  { debug: console.log, info: console.log, warn: console.warn, error: console.error, group: console.group, groupEnd: console.groupEnd };

class PrismWeaveBackground {
  constructor() {
    logger.info('PrismWeaveBackground constructor called');
    logger.debug('Initializing core components');
    
    this.settingsManager = new SettingsManager();
    this.markdownConverter = new MarkdownConverter();
    this.gitOperations = new GitOperations();
    this.fileManager = new FileManager();
    this.isInitialized = false;
    
    logger.debug('Core components initialized, starting extension initialization');
    this.initializeExtension();
  }

  async initializeExtension() {
    logger.group('Initializing extension');
    
    // Load initial settings to ensure they exist
    try {
      const initialSettings = await this.settingsManager.loadSettings();
      logger.info('Initial settings loaded on startup:', initialSettings);
      this.isInitialized = true;
    } catch (error) {
      logger.error('Failed to load initial settings:', error);
    }
    
    // Listen for extension installation/startup
    chrome.runtime.onInstalled.addListener(details => {
      logger.info('Extension installed/updated:', details.reason);
      this.handleInstallation(details);
    });

    // Test settings persistence on startup
    setTimeout(async () => {
      try {
        logger.info('Testing settings on startup...');
        const testLoad = await this.settingsManager.loadSettings();
        logger.info('Startup settings test - loaded:', testLoad);
      } catch (error) {
        logger.error('Startup settings test failed:', error);
      }
    }, 1000);

    // Listen for messages from content scripts and popup
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      logger.debug('Message received from:', sender.tab ? 'content script' : 'popup');
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep message channel open for async responses
    });

    // Listen for action button clicks
    chrome.action.onClicked.addListener(tab => {
      this.captureCurrentPage(tab);
    });
  }
  async handleInstallation(details) {
    console.log('PrismWeave installed:', details.reason);

    // Initialize default settings using SettingsManager
    await this.settingsManager.resetSettings();
  }

  async handleMessage(message, sender, sendResponse) {
    logger.group(`Handling message: ${message.action}`);
    logger.debug('Message details:', message);
    logger.debug('Sender details:', sender);

    try {
      switch (message.action) {
        case 'CAPTURE_PAGE': {
          logger.info('Processing CAPTURE_PAGE request');
          // Prefer token/repo from message, fallback to settings
          let settings = await this.settingsManager.loadSettings();
          if (message.githubToken) settings.githubToken = message.githubToken;
          if (message.githubRepo) {
            settings.githubRepo = message.githubRepo;
            settings.repositoryPath = message.githubRepo;
          }
          const result = await this.captureCurrentPage(sender.tab, settings);
          logger.debug('Capture result:', result);
          sendResponse({ success: true, data: result });
          break;
        }
        case 'GET_SETTINGS': {
          logger.info('Processing GET_SETTINGS request');
          const settings = await this.settingsManager.loadSettings();
          logger.debug('Settings loaded:', settings);
          sendResponse({ success: true, data: settings });
          break;
        }
        case 'UPDATE_SETTINGS': {
          logger.info('Processing UPDATE_SETTINGS request');
          const saveResult = await this.settingsManager.saveSettings(message.settings);
          logger.debug('Settings save result:', saveResult);
          sendResponse(saveResult);
          break;
        }
        case 'PROCESS_CONTENT': {
          logger.info('Processing PROCESS_CONTENT request');
          const processed = await this.processPageContent(message.content, message.metadata);
          logger.debug('Content processing result:', processed);
          sendResponse({ success: true, data: processed });
          break;
        }
        case 'TEST_CONNECTION': {
          logger.info('Processing TEST_CONNECTION request');
          // Prefer token/repo from message, fallback to settings
          let settings = await this.settingsManager.loadSettings();
          if (message.githubToken) settings.githubToken = message.githubToken;
          if (message.githubRepo) {
            settings.githubRepo = message.githubRepo;
            settings.repositoryPath = message.githubRepo;
          }
          await this.gitOperations.initialize(settings);
          const connectionResult = await this.gitOperations.testConnection();
          logger.debug('Connection test result:', connectionResult);
          sendResponse({ success: true, data: connectionResult });
          break;
        }
        case 'VALIDATE_REPOSITORY': {
          logger.info('Processing VALIDATE_REPOSITORY request');
          // Prefer token/repo from message, fallback to settings
          let settings = await this.settingsManager.loadSettings();
          if (message.githubToken) settings.githubToken = message.githubToken;
          if (message.githubRepo) {
            settings.githubRepo = message.githubRepo;
            settings.repositoryPath = message.githubRepo;
          }
          await this.gitOperations.initialize(settings);
          const repoResult = await this.gitOperations.validateRepository();
          sendResponse({ success: true, data: repoResult });
          break;
        }
        case 'HIGHLIGHT_CONTENT': {
          await this.highlightPageContent(sender.tab);
          sendResponse({ success: true });
          break;
        }
        default: {
          sendResponse({ success: false, error: 'Unknown action' });
        }
      }
    } catch (error) {
      console.error('Background script error:', error);
      sendResponse({ success: false, error: error.message });
    }
  }
  async captureCurrentPage(tab, settingsOverride = null) {
    try {
      // Get current settings, allow override
      const settings = settingsOverride || await this.settingsManager.loadSettings();
      await this.gitOperations.initialize(settings);

      // Inject content script to extract page content
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['src/utils/content-extractor.js'],
      });

      // Extract page content using enhanced extractor
      const contentResults = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          const extractor = new ContentExtractor();
          return extractor.extractPageContent(document);
        },
      });

      if (!contentResults || !contentResults[0]) {
        throw new Error('Failed to extract page content');
      }

      const pageData = contentResults[0].result;

      // Process the content and save to repository
      const processedContent = await this.processPageContent(pageData, {
        url: tab.url,
        title: tab.title,
        timestamp: new Date().toISOString(),
        domain: new URL(tab.url).hostname,
      });

      // Save to repository
      await this.saveToRepository(processedContent);

      return processedContent;
    } catch (error) {
      console.error('Capture failed:', error);
      throw error;
    }
  }
  async processPageContent(pageData, metadata) {
    // Determine target folder
    const settings = await this.settingsManager.loadSettings();
    const targetFolder = this.fileManager.suggestFolder(pageData.textContent, metadata);

    // Convert HTML to clean markdown using enhanced converter
    const markdown = this.markdownConverter.convert(pageData.content);

    // Generate filename using file manager
    const filename = this.fileManager.generateFilename(metadata, settings);

    // Create YAML frontmatter with enhanced metadata
    const frontmatter = this.fileManager.createFrontmatter(metadata, pageData);

    // Combine into final document
    const document = `${frontmatter}\n\n${markdown}`;

    return {
      filename,
      content: document,
      metadata: {
        ...metadata,
        folder: targetFolder,
        quality: pageData.quality,
      },
      images: pageData.images,
      links: pageData.links,
    };
  }
  async saveToRepository(processedContent) {
    try {
      const settings = await this.settingsManager.loadSettings();

      if (settings.githubToken && settings.repositoryPath) {
        // Save to GitHub repository
        await this.gitOperations.saveToRepository(processedContent);
      } else {
        // Fallback: download file locally
        await this.downloadFile(processedContent);
      }
    } catch (error) {
      console.error('Failed to save to repository:', error);
      // Always fallback to local download
      await this.downloadFile(processedContent);
      throw error;
    }
  }
  async downloadFile(processedContent) {
    const blob = new Blob([processedContent.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);

    const folder = processedContent.metadata.folder || 'unsorted';

    await chrome.downloads.download({
      url: url,
      filename: `prismweave/${folder}/${processedContent.filename}`,
      saveAs: false,
    });

    URL.revokeObjectURL(url);
  }
  async testGitConnection() {
    try {
      const settings = await this.settingsManager.loadSettings();
      await this.gitOperations.initialize(settings);
      return await this.gitOperations.testConnection();
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async validateRepository() {
    try {
      const settings = await this.settingsManager.loadSettings();
      await this.gitOperations.initialize(settings);
      return await this.gitOperations.validateRepository();
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async highlightPageContent(tab) {
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ['src/utils/content-extractor.js'],
    });
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => {
        const extractor = new ContentExtractor();
        extractor.highlightMainContent();
      },
    });
  }
}

// Initialize the background service
logger.info('🚀 PrismWeave Background Service Worker starting up');
logger.debug('Chrome APIs available:', {
  runtime: !!chrome.runtime,
  tabs: !!chrome.tabs,
  storage: !!chrome.storage,
  action: !!chrome.action
});

new PrismWeaveBackground();
