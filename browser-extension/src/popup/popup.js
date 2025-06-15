// PrismWeave Popup Script
// Handles the extension popup interface and user interactions

class PrismWeavePopup {
  constructor() {
    this.currentTab = null;
    this.settings = null;
    this.initializePopup();
  }

  async initializePopup() {
    try {
      // Get current tab information
      await this.getCurrentTab();

      // Load settings
      await this.loadSettings();

      // Update UI
      this.updatePageInfo();
      this.setupEventListeners();

      // Check if page is capturable
      this.checkPageCapturability();
    } catch (error) {
      console.error('Failed to initialize popup:', error);
      this.showStatus('Failed to initialize', 'error');
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
    // Main capture button
    document.getElementById('capture-btn').addEventListener('click', () => {
      this.captureCurrentPage();
    });

    // Highlight button
    document.getElementById('highlight-btn').addEventListener('click', () => {
      this.highlightContent();
    });

    // Settings button
    document.getElementById('settings-btn').addEventListener('click', () => {
      this.openSettings();
    });

    // Options link
    document.getElementById('options-link').addEventListener('click', e => {
      e.preventDefault();
      this.openOptions();
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        this.captureCurrentPage();
      } else if (e.key === 'Escape') {
        window.close();
      }
    });
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
    try {
      this.showLoading(true);
      this.disableCaptureButton();

      const response = await chrome.runtime.sendMessage({
        action: 'CAPTURE_PAGE',
      });

      if (response.success) {
        this.showStatus(`✓ Captured: ${response.data.filename}`, 'success');

        // Auto-close popup after successful capture
        setTimeout(() => {
          window.close();
        }, 2000);
      } else {
        throw new Error(response.error);
      }
    } catch (error) {
      console.error('Capture failed:', error);
      this.showStatus(`✗ Capture failed: ${error.message}`, 'error');
    } finally {
      this.showLoading(false);
      this.enableCaptureButton();
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
