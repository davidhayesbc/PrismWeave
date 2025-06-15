// PrismWeave Background Service Worker
// Handles extension lifecycle, Git operations, and file management

// Import utilities and dependencies
importScripts('lib/turndown.js');
importScripts('src/utils/shared-utils.js');
importScripts('src/utils/settings-manager.js');
importScripts('src/utils/markdown-converter.js');
importScripts('src/utils/git-operations.js');
importScripts('src/utils/file-manager.js');

class PrismWeaveBackground {
  constructor() {
    this.settingsManager = new SettingsManager();
    this.markdownConverter = new MarkdownConverter();
    this.gitOperations = new GitOperations();
    this.fileManager = new FileManager();
    this.initializeExtension();
  }

  initializeExtension() {
    // Listen for extension installation/startup
    chrome.runtime.onInstalled.addListener(details => {
      this.handleInstallation(details);
    });

    // Listen for messages from content scripts and popup
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
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
    try {
      switch (message.action) {
        case 'CAPTURE_PAGE':
          const result = await this.captureCurrentPage(sender.tab);
          sendResponse({ success: true, data: result });
          break;

        case 'GET_SETTINGS':
          const settings = await this.settingsManager.loadSettings();
          sendResponse({ success: true, data: settings });
          break;

        case 'UPDATE_SETTINGS':
          const saveResult = await this.settingsManager.saveSettings(message.settings);
          sendResponse(saveResult);
          break;

        case 'PROCESS_CONTENT':
          const processed = await this.processPageContent(message.content, message.metadata);
          sendResponse({ success: true, data: processed });
          break;

        case 'TEST_CONNECTION':
          const connectionResult = await this.testGitConnection();
          sendResponse({ success: true, data: connectionResult });
          break;

        case 'VALIDATE_REPOSITORY':
          const repoResult = await this.validateRepository();
          sendResponse({ success: true, data: repoResult });
          break;

        case 'HIGHLIGHT_CONTENT':
          await this.highlightPageContent(sender.tab);
          sendResponse({ success: true });
          break;

        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('Background script error:', error);
      sendResponse({ success: false, error: error.message });
    }
  }
  async captureCurrentPage(tab) {
    try {
      // Get current settings
      const settings = await this.settingsManager.loadSettings();
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
new PrismWeaveBackground();
