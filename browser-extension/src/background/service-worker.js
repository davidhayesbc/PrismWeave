// PrismWeave Background Service Worker
// Handles extension lifecycle, Git operations, and file management

// Import utilities and dependencies
importScripts('../utils/logger.js');
importScripts('../utils/log-config.js');
importScripts('../utils/shared-utils.js');
importScripts('../utils/settings-manager.js');
// NOTE: TurndownService is NOT imported in service worker context to avoid 'window is not defined' error
// MarkdownConverter will automatically use enhanced fallback conversion in service worker
importScripts('../utils/markdown-converter.js');
importScripts('../utils/git-operations.js');
importScripts('../utils/file-manager.js');
importScripts('../utils/test-service-worker-compatibility.js');

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
          
          // Get the current active tab if sender.tab is undefined (e.g., from popup)
          let targetTab = sender.tab;
          if (!targetTab) {
            logger.debug('No sender.tab found, querying for active tab');
            const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
            targetTab = activeTab;
          }
          
          if (!targetTab) {
            throw new Error('No active tab found for capture. Please ensure you have an active browser tab open.');
          }
          
          logger.debug('Capturing page:', { url: targetTab.url, title: targetTab.title });
          const result = await this.captureCurrentPage(targetTab, settings);
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
          
          logger.debug('Testing connection with settings:', { 
            hasToken: !!settings.githubToken, 
            repo: settings.githubRepo 
          });
          
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
          
          logger.debug('Validating repository with settings:', { 
            hasToken: !!settings.githubToken, 
            repo: settings.githubRepo || settings.repositoryPath,
            tokenLength: settings.githubToken?.length
          });
          
          try {
            await this.gitOperations.initialize(settings);
            const repoResult = await this.gitOperations.validateRepository();
            logger.debug('Repository validation result:', repoResult);
            sendResponse({ success: true, data: repoResult });
          } catch (initError) {
            logger.error('Failed to initialize git operations:', initError);
            sendResponse({ 
              success: false, 
              data: { 
                success: false, 
                error: `Initialization failed: ${initError.message}` 
              } 
            });
          }
          break;
        }
        case 'CHECK_GITHUB_SETUP': {
          logger.info('Processing CHECK_GITHUB_SETUP request');
          const settings = await this.settingsManager.loadSettings();
          
          // Comprehensive GitHub setup validation
          const setupCheck = {
            hasToken: !!settings.githubToken,
            hasRepo: !!(settings.githubRepo || settings.repositoryPath),
            tokenValid: false,
            repoValid: false,
            repoWriteable: false,
            errors: []
          };
          
          if (!setupCheck.hasToken) {
            setupCheck.errors.push('GitHub token not configured');
          }
          
          if (!setupCheck.hasRepo) {
            setupCheck.errors.push('Repository path not configured');
          }
          
          if (setupCheck.hasToken && setupCheck.hasRepo) {
            try {
              await this.gitOperations.initialize(settings);
              
              // Test token validity
              const connectionResult = await this.gitOperations.testConnection();
              setupCheck.tokenValid = connectionResult.success;
              if (!setupCheck.tokenValid) {
                setupCheck.errors.push(`Token validation failed: ${connectionResult.error}`);
              }
              
              // Test repository access
              const repoResult = await this.gitOperations.validateRepository();
              setupCheck.repoValid = repoResult.success;
              setupCheck.repoWriteable = repoResult.hasWrite || false;
              
              if (!setupCheck.repoValid) {
                setupCheck.errors.push(`Repository validation failed: ${repoResult.error}`);
              } else if (!setupCheck.repoWriteable) {
                setupCheck.errors.push('No write access to repository');
              }
              
            } catch (error) {
              setupCheck.errors.push(`Setup check failed: ${error.message}`);
            }
          }
          
          logger.debug('GitHub setup check result:', setupCheck);
          sendResponse({ success: true, data: setupCheck });
          break;
        }
        case 'HIGHLIGHT_CONTENT': {
          logger.info('Processing HIGHLIGHT_CONTENT request');
          // Get the current active tab if sender.tab is undefined (e.g., from popup)
          let targetTab = sender.tab;
          if (!targetTab) {
            logger.debug('No sender.tab found, querying for active tab');
            const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
            targetTab = activeTab;
          }
          
          if (!targetTab) {
            throw new Error('No active tab found for highlighting. Please ensure you have an active browser tab open.');
          }
          
          logger.debug('Highlighting content on page:', { url: targetTab.url, title: targetTab.title });
          await this.highlightPageContent(targetTab);
          sendResponse({ success: true });
          break;
        }
        default: {
          sendResponse({ success: false, error: 'Unknown action' });
        }
      }
    } catch (error) {
      logger.error('Background script error processing message:', message.action, error);
      logger.error('Error details:', { 
        message: error.message, 
        stack: error.stack?.substring(0, 500) 
      });
      
      // Provide more specific error messages based on error type
      let userMessage = error.message;
      
      if (error.message.includes('GitHub API')) {
        userMessage = `GitHub API Error: ${error.message}`;
      } else if (error.message.includes('repository')) {
        userMessage = `Repository Error: ${error.message}`;
      } else if (error.message.includes('tab')) {
        userMessage = `Browser Tab Error: ${error.message}`;
      } else if (error.message.includes('token')) {
        userMessage = `Authentication Error: ${error.message}`;
      }
      
      sendResponse({ 
        success: false, 
        error: userMessage,
        details: error.message !== userMessage ? error.message : undefined
      });
    }
  }
  async captureCurrentPage(tab, settingsOverride = null) {
    try {
      if (!tab || typeof tab.id === 'undefined') {
        throw new Error('Invalid tab or tab ID for page capture. Please refresh the page and try again.');
      }
      
      logger.debug('Starting page capture for:', { url: tab.url, title: tab.title, tabId: tab.id });
      
      // Get current settings, allow override
      const settings = settingsOverride || await this.settingsManager.loadSettings();
      await this.gitOperations.initialize(settings);

      // Inject content script to extract page content
      logger.debug('Injecting content extractor script');
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['src/utils/content-extractor.js'],
      });

      // Extract page content using enhanced extractor
      logger.debug('Extracting page content');
      const contentResults = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          const extractor = new ContentExtractor();
          return extractor.extractPageContent(document);
        },
      });

      if (!contentResults || !contentResults[0]) {
        throw new Error('Failed to extract page content. The page may not be fully loaded or accessible.');
      }

      const pageData = contentResults[0].result;
      logger.debug('Page data extracted:', { 
        contentLength: pageData.content?.length,
        quality: pageData.quality,
        imagesCount: pageData.images?.length
      });

      // Process the content and save to repository
      const processedContent = await this.processPageContent(pageData, {
        url: tab.url,
        title: tab.title,
        timestamp: new Date().toISOString(),
        domain: new URL(tab.url).hostname,
      });

      // Save to repository
      logger.debug('Saving to repository');
      await this.saveToRepository(processedContent);

      logger.info('Page capture completed successfully');
      return processedContent;
    } catch (error) {
      logger.error('Capture failed for tab:', tab?.url, error);
      
      // Enhance error message based on error type
      if (error.message.includes('Cannot access')) {
        throw new Error(`Cannot access this page for capture. The page may be restricted or require special permissions. Original error: ${error.message}`);
      } else if (error.message.includes('GitHub API')) {
        throw new Error(`Failed to save to GitHub: ${error.message}`);
      } else {
        throw error;
      }
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

      if (settings.githubToken && (settings.repositoryPath || settings.githubRepo)) {
        const repoPath = settings.githubRepo || settings.repositoryPath;
        logger.debug('Saving to GitHub repository:', repoPath);
        logger.debug('GitHub configuration:', {
          hasToken: !!settings.githubToken,
          tokenLength: settings.githubToken?.length,
          repositoryPath: settings.repositoryPath,
          githubRepo: settings.githubRepo,
          finalRepoPath: repoPath
        });
        
        // First validate the repository exists and we have access
        logger.debug('Validating repository access before saving...');
        await this.gitOperations.initialize(settings);
        const repoValidation = await this.gitOperations.validateRepository();
        
        if (!repoValidation.success) {
          throw new Error(`Repository validation failed: ${repoValidation.error}`);
        }
        
        logger.debug('Repository validation successful, proceeding with save');
        // Save to GitHub repository
        await this.gitOperations.saveToRepository(processedContent);
        logger.info('Successfully saved to GitHub repository');
      } else {
        logger.debug('No GitHub configuration found, downloading locally');
        // Fallback: download file locally
        await this.downloadFile(processedContent);
        logger.info('File downloaded locally due to missing GitHub configuration');
      }
    } catch (error) {
      logger.error('Failed to save to repository:', error);
      logger.debug('Attempting fallback to local download');
      
      // Always fallback to local download on GitHub failure
      try {
        await this.downloadFile(processedContent);
        logger.info('Successfully downloaded file locally as fallback');
        // Don't re-throw the error if local download succeeded
        logger.warn('GitHub save failed but local download succeeded. GitHub error:', error.message);
      } catch (downloadError) {
        logger.error('Local download fallback also failed:', downloadError);
        throw new Error(`Both GitHub save and local download failed. GitHub error: ${error.message}. Download error: ${downloadError.message}`);
      }
    }
  }
  async downloadFile(processedContent) {
    try {
      // Convert content to data URL (compatible with service workers)
      const content = processedContent.content;
      const dataUrl = 'data:text/markdown;charset=utf-8,' + encodeURIComponent(content);

      const folder = processedContent.metadata.folder || 'unsorted';

      await chrome.downloads.download({
        url: dataUrl,
        filename: `prismweave/${folder}/${processedContent.filename}`,
        saveAs: false,
      });
    } catch (error) {
      console.error('Failed to download file:', error);
      throw new Error(`Download failed: ${error.message}`);
    }
  }
  async testGitConnection() {
    try {
      const settings = await this.settingsManager.loadSettings();
      logger.debug('Testing Git connection with settings:', { 
        hasToken: !!settings.githubToken, 
        repo: settings.githubRepo 
      });
      
      await this.gitOperations.initialize(settings);
      const result = await this.gitOperations.testConnection();
      logger.debug('Git connection test result:', result);
      return result;
    } catch (error) {
      logger.error('Git connection test failed:', error);
      return { 
        success: false, 
        error: `Connection test failed: ${error.message}`,
        details: error.message
      };
    }
  }

  async validateRepository() {
    try {
      const settings = await this.settingsManager.loadSettings();
      logger.debug('Validating repository with settings:', { 
        hasToken: !!settings.githubToken, 
        repo: settings.githubRepo 
      });
      
      await this.gitOperations.initialize(settings);
      const result = await this.gitOperations.validateRepository();
      logger.debug('Repository validation result:', result);
      return result;
    } catch (error) {
      logger.error('Repository validation failed:', error);
      return { 
        success: false, 
        error: `Repository validation failed: ${error.message}`,
        details: error.message
      };
    }
  }

  async highlightPageContent(tab) {
    if (!tab || typeof tab.id === 'undefined') {
      throw new Error('Invalid tab or tab ID for highlighting content. Please refresh the page and try again.');
    }
    
    logger.debug('Highlighting page content for:', { url: tab.url, title: tab.title, tabId: tab.id });
    
    try {
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
      logger.info('Page content highlighted successfully');
    } catch (error) {
      logger.error('Failed to highlight page content:', error);
      if (error.message.includes('Cannot access')) {
        throw new Error(`Cannot highlight content on this page. The page may be restricted or require special permissions. Original error: ${error.message}`);
      }
      throw error;
    }
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
