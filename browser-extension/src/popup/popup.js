// PrismWeave Popup Script
// Handles the extension popup interface and user interactions

// Import logger
const logger = window.PrismWeaveLogger ? 
  window.PrismWeaveLogger.createLogger('Popup') : 
  { debug: console.log, info: console.log, warn: console.warn, error: console.error, group: console.group, groupEnd: console.groupEnd };

class PrismWeavePopup {
  constructor() {
    logger.info('PrismWeavePopup constructor called');
    this.currentTab = null;
    this.settings = null;
    this.initializePopup();
  }

  async initializePopup() {
    logger.group('Initializing popup');
    try {
      // Get current tab information
      logger.debug('Getting current tab');
      await this.getCurrentTab();
      logger.debug('Current tab obtained:', this.currentTab);

      // Load settings
      logger.debug('Loading settings');
      await this.loadSettings();
      logger.debug('Settings loaded:', this.settings);

      // Update UI
      logger.debug('Updating page info');
      this.updatePageInfo();
      
      logger.debug('Setting up event listeners');
      this.setupEventListeners();

      // Check if page is capturable
      logger.debug('Checking page capturability');
      this.checkPageCapturability();
      
      logger.info('Initialization complete');
    } catch (error) {
      logger.error('Failed to initialize popup:', error);
      this.showStatus('Failed to initialize', 'error');
    } finally {
      logger.groupEnd();
    }
  }

  async getCurrentTab() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    this.currentTab = tab;
  }

  async loadSettings() {
    const response = await chrome.runtime.sendMessage({ action: 'GET_SETTINGS' });
    if (response.success) {
      this.settings = response.data;
    } else {
      this.settings = this.getDefaultSettings();
    }
  }

  getDefaultSettings() {
    return {
      autoCommit: false,
      autoPush: false,
      repositoryPath: '',
      githubToken: '',
      defaultFolder: 'unsorted',
      fileNamingPattern: 'YYYY-MM-DD-domain-title',
    };
  }

  updatePageInfo() {
    if (!this.currentTab) return;

    const titleElement = document.getElementById('page-title');
    const urlElement = document.getElementById('page-url');

    titleElement.textContent = this.currentTab.title || 'Untitled';
    urlElement.textContent = this.currentTab.url;
  }

  setupEventListeners() {
    logger.group('Setting up event listeners');
    
    // Main capture button
    const captureBtn = document.getElementById('capture-btn');
    if (captureBtn) {
      logger.debug('Setting up capture button listener');
      captureBtn.addEventListener('click', () => {
        logger.info('Capture button clicked');
        this.captureCurrentPage();
      });
    } else {
      logger.error('Capture button not found in DOM');
    }

    // Highlight button
    const highlightBtn = document.getElementById('highlight-btn');
    if (highlightBtn) {
      logger.debug('Setting up highlight button listener');
      highlightBtn.addEventListener('click', () => {
        logger.info('Highlight button clicked');
        this.highlightContent();
      });
    } else {
      logger.error('Highlight button not found in DOM');
    }

    // Settings button
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
      logger.debug('Setting up settings button listener');
      settingsBtn.addEventListener('click', () => {
        logger.info('Settings button clicked');
        this.openSettings();
      });
    } else {
      logger.error('Settings button not found in DOM');
    }

    // Options link
    const optionsLink = document.getElementById('options-link');
    if (optionsLink) {
      logger.debug('Setting up options link listener');
      optionsLink.addEventListener('click', e => {
        e.preventDefault();
        logger.info('Options link clicked');
        this.openOptions();
      });
    } else {
      logger.error('Options link not found in DOM');
    }

    // Keyboard shortcuts
    logger.debug('Setting up keyboard shortcuts');
    document.addEventListener('keydown', e => {
      logger.trace('Key pressed:', e.key);
      if (e.key === 'Enter' && !e.shiftKey) {
        logger.info('Enter key pressed - capturing page');
        this.captureCurrentPage();
      } else if (e.key === 'Escape') {
        logger.info('Escape key pressed - closing popup');
        window.close();
      }
    });
    
    logger.info('Event listeners setup completed');
    logger.groupEnd();
  }

  checkPageCapturability() {
    if (!this.currentTab) return;

    const url = this.currentTab.url;

    // Check if URL is capturable
    if (
      url.startsWith('chrome://') ||
      url.startsWith('chrome-extension://') ||
      url.startsWith('edge://') ||
      url.startsWith('about:')
    ) {
      this.showStatus('Cannot capture browser internal pages', 'warning');
      this.disableCaptureButton();
      return;
    }

    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      this.showStatus('Cannot capture non-web pages', 'warning');
      this.disableCaptureButton();
      return;
    }

    // Check repository configuration
    if (!this.settings.repositoryPath) {
      this.showStatus('Repository not configured. Click Settings to set up.', 'warning');
    }
  }

  async captureCurrentPage() {
    logger.group('Capturing current page');
    try {
      logger.info('Starting page capture process');
      this.showLoading(true);
      this.disableCaptureButton();

      logger.debug('Sending CAPTURE_PAGE message to background script');
      const response = await chrome.runtime.sendMessage({
        action: 'CAPTURE_PAGE',
        githubToken: this.settings.githubToken,
        githubRepo: this.settings.githubRepo || this.settings.repositoryPath,
      });
      
      logger.debug('Received response from background script:', response);

      if (response.success) {
        logger.info('Page capture successful:', response.data.filename);
        this.showStatus(`✓ Captured: ${response.data.filename}`, 'success');

        // Auto-close popup after successful capture
        setTimeout(() => {
          logger.debug('Auto-closing popup after successful capture');
          window.close();
        }, 2000);
      } else {
        throw new Error(response.error);
      }
    } catch (error) {
      logger.error('Capture failed:', error);
      this.showStatus(`✗ Capture failed: ${error.message}`, 'error');
    } finally {
      this.showLoading(false);
      this.enableCaptureButton();
      logger.groupEnd();
    }
  }

  async highlightContent() {
    try {
      await chrome.tabs.sendMessage(this.currentTab.id, {
        action: 'HIGHLIGHT_CONTENT',
      });

      this.showStatus('Content highlighted on page', 'success');

      setTimeout(() => {
        this.hideStatus();
      }, 2000);
    } catch (error) {
      console.error('Highlight failed:', error);
      this.showStatus('Highlight failed', 'error');
    }
  }

  openSettings() {
    // Open options page
    chrome.runtime.openOptionsPage();
    window.close();
  }

  openOptions() {
    chrome.runtime.openOptionsPage();
    window.close();
  }

  showLoading(show) {
    const loadingElement = document.getElementById('loading');
    const mainContent = document.getElementById('main-content');

    if (show) {
      loadingElement.style.display = 'flex';
      mainContent.style.display = 'none';
    } else {
      loadingElement.style.display = 'none';
      mainContent.style.display = 'block';
    }
  }

  showStatus(message, type = 'success') {
    const statusElement = document.getElementById('status');
    const statusText = document.getElementById('status-text');

    statusText.textContent = message;
    statusElement.className = `status ${type}`;
    statusElement.style.display = 'block';
  }

  hideStatus() {
    const statusElement = document.getElementById('status');
    statusElement.style.display = 'none';
  }

  disableCaptureButton() {
    const button = document.getElementById('capture-btn');
    button.disabled = true;
    button.textContent = 'Cannot Capture';
  }

  enableCaptureButton() {
    const button = document.getElementById('capture-btn');
    button.disabled = false;
    button.textContent = '📄 Capture This Page';
  }

  // Utility method to estimate capture time
  estimateCaptureTime() {
    if (!this.currentTab) return 5;

    // Rough estimation based on URL and page type
    const url = this.currentTab.url;
    const title = this.currentTab.title || '';

    // News sites might have more complex content
    if (url.includes('news') || url.includes('article')) {
      return 8;
    }

    // Documentation sites are usually clean
    if (url.includes('docs') || url.includes('documentation')) {
      return 3;
    }

    // Social media sites might have dynamic content
    if (url.includes('twitter') || url.includes('facebook') || url.includes('linkedin')) {
      return 10;
    }

    return 5; // Default estimate
  }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new PrismWeavePopup();
});
