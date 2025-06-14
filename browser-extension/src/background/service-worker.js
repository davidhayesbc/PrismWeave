// PrismWeave Background Service Worker
// Handles extension lifecycle, Git operations, and file management

// Import utilities and dependencies
importScripts('lib/turndown.js');
importScripts('src/utils/markdown-converter.js');
importScripts('src/utils/git-operations.js');
importScripts('src/utils/file-manager.js');

class PrismWeaveBackground {
  constructor() {
    this.markdownConverter = new MarkdownConverter();
    this.gitOperations = new GitOperations();
    this.fileManager = new FileManager();
    this.initializeExtension();
  }

  initializeExtension() {
    // Listen for extension installation/startup
    chrome.runtime.onInstalled.addListener((details) => {
      this.handleInstallation(details);
    });

    // Listen for messages from content scripts and popup
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep message channel open for async responses
    });

    // Listen for action button clicks
    chrome.action.onClicked.addListener((tab) => {
      this.captureCurrentPage(tab);
    });
  }

  async handleInstallation(details) {
    console.log('PrismWeave installed:', details.reason);
    
    // Initialize default settings
    const defaultSettings = {
      autoCommit: false,
      autoPush: false,
      repositoryPath: '',
      githubToken: '',
      defaultFolder: 'unsorted',
      fileNamingPattern: 'YYYY-MM-DD-domain-title'
    };

    await chrome.storage.sync.set({ prismWeaveSettings: defaultSettings });
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'CAPTURE_PAGE':
          const result = await this.captureCurrentPage(sender.tab);
          sendResponse({ success: true, data: result });
          break;

        case 'GET_SETTINGS':
          const settings = await this.getSettings();
          sendResponse({ success: true, data: settings });
          break;

        case 'UPDATE_SETTINGS':
          await this.updateSettings(message.settings);
          sendResponse({ success: true });
          break;

        case 'PROCESS_CONTENT':
          const processed = await this.processPageContent(message.content, message.metadata);
          sendResponse({ success: true, data: processed });
          break;        case 'TEST_CONNECTION':
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
      const settings = await this.getSettings();
      await this.gitOperations.initialize(settings);

      // Inject content script to extract page content
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['src/utils/content-extractor.js']
      });

      // Extract page content using enhanced extractor
      const contentResults = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          const extractor = new ContentExtractor();
          return extractor.extractPageContent(document);
        }
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
        domain: new URL(tab.url).hostname
      });

      // Save to repository
      await this.saveToRepository(processedContent);

      return processedContent;
    } catch (error) {
      console.error('Capture failed:', error);
      throw error;
    }  }

  async processPageContent(pageData, metadata) {
    // Determine target folder
    const settings = await this.getSettings();
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
        quality: pageData.quality
      },
      images: pageData.images,
      links: pageData.links
    };
  }

  async htmlToMarkdown(html) {
    // Basic HTML to Markdown conversion
    // TODO: Integrate proper library like Turndown.js
    let markdown = html;
    
    // Headers
    markdown = markdown.replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n\n');
    markdown = markdown.replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n\n');
    markdown = markdown.replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n\n');
    markdown = markdown.replace(/<h4[^>]*>(.*?)<\/h4>/gi, '#### $1\n\n');
    markdown = markdown.replace(/<h5[^>]*>(.*?)<\/h5>/gi, '##### $1\n\n');
    markdown = markdown.replace(/<h6[^>]*>(.*?)<\/h6>/gi, '###### $1\n\n');
    
    // Paragraphs
    markdown = markdown.replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n');
    
    // Links
    markdown = markdown.replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '[$2]($1)');
    
    // Bold and italic
    markdown = markdown.replace(/<strong[^>]*>(.*?)<\/strong>/gi, '**$1**');
    markdown = markdown.replace(/<b[^>]*>(.*?)<\/b>/gi, '**$1**');
    markdown = markdown.replace(/<em[^>]*>(.*?)<\/em>/gi, '*$1*');
    markdown = markdown.replace(/<i[^>]*>(.*?)<\/i>/gi, '*$1*');
    
    // Lists
    markdown = markdown.replace(/<ul[^>]*>(.*?)<\/ul>/gis, (match, content) => {
      const items = content.match(/<li[^>]*>(.*?)<\/li>/gi) || [];
      return items.map(item => `- ${item.replace(/<li[^>]*>(.*?)<\/li>/gi, '$1')}`).join('\n') + '\n\n';
    });
    
    markdown = markdown.replace(/<ol[^>]*>(.*?)<\/ol>/gis, (match, content) => {
      const items = content.match(/<li[^>]*>(.*?)<\/li>/gi) || [];
      return items.map((item, index) => `${index + 1}. ${item.replace(/<li[^>]*>(.*?)<\/li>/gi, '$1')}`).join('\n') + '\n\n';
    });
    
    // Images
    markdown = markdown.replace(/<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>/gi, '![$2]($1)');
    markdown = markdown.replace(/<img[^>]*src="([^"]*)"[^>]*>/gi, '![]($1)');
    
    // Clean up HTML tags and extra whitespace
    markdown = markdown.replace(/<[^>]+>/g, '');
    markdown = markdown.replace(/\n\s*\n\s*\n/g, '\n\n');
    markdown = markdown.trim();
    
    return markdown;
  }

  generateFilename(metadata) {
    const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const domain = metadata.domain.replace(/^www\./, ''); // Remove www.
    const title = metadata.title
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '') // Remove special chars
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .substring(0, 50); // Limit length

    return `${date}-${domain}-${title}.md`;
  }

  createFrontmatter(metadata, pageData) {
    const frontmatter = {
      title: metadata.title,
      source_url: metadata.url,
      domain: metadata.domain,
      captured_date: metadata.timestamp,
      tags: [],
      summary: ""
    };

    return `---\n${Object.entries(frontmatter)
      .map(([key, value]) => `${key}: "${value}"`)
      .join('\n')}\n---`;
  }
  async saveToRepository(processedContent) {
    try {
      const settings = await this.getSettings();
      
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
      saveAs: false
    });

    URL.revokeObjectURL(url);
  }

  async testGitConnection() {
    try {
      const settings = await this.getSettings();
      await this.gitOperations.initialize(settings);
      return await this.gitOperations.testConnection();
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async validateRepository() {
    try {
      const settings = await this.getSettings();
      await this.gitOperations.initialize(settings);
      return await this.gitOperations.validateRepository();
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async highlightPageContent(tab) {
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ['src/utils/content-extractor.js']
    });

    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => {
        const extractor = new ContentExtractor();
        extractor.highlightMainContent();
      }
    });
  }
  async getSettings() {    const result = await chrome.storage.sync.get(['prismWeaveSettings']);
    return result.prismWeaveSettings || this.getDefaultSettings();
  }

  getDefaultSettings() {
    return {
      autoCommit: false,
      autoPush: false,
      repositoryPath: '',
      githubToken: '',
      defaultFolder: 'unsorted',
      fileNamingPattern: 'YYYY-MM-DD-domain-title'
    };
  }

  async updateSettings(newSettings) {
    await chrome.storage.sync.set({ prismWeaveSettings: newSettings });
  }
}

// Initialize the background service
new PrismWeaveBackground();
