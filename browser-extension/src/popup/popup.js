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
      this.showAdvancedLoading();
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
        this.showSuccessWithDetails(response.data);
        
        // Auto-close popup after successful capture
        setTimeout(() => {
          logger.debug('Auto-closing popup after successful capture');
          window.close();
        }, 2000);
      } else {
        throw new Error(response.error || 'Capture failed');
      }
    } catch (error) {
      logger.error('Capture failed:', error);
      this.showEnhancedError(error);
    } finally {
      this.hideLoading();
      this.enableCaptureButton();
      logger.groupEnd();
    }
  }
  async highlightContent() {
    try {
      logger.info('Starting highlight content process');
      
      // Send message to background script instead of directly to tab
      logger.debug('Sending HIGHLIGHT_CONTENT message to background script');
      const response = await chrome.runtime.sendMessage({
        action: 'HIGHLIGHT_CONTENT',
      });

      logger.debug('Received response from background script:', response);

      if (response.success) {
        this.showStatus('Content highlighted on page', 'success');
        setTimeout(() => {
          this.hideStatus();
        }, 2000);
      } else {
        throw new Error(response.error);
      }    } catch (error) {
      const errorMsg = error?.message || error?.toString() || 'Unknown error occurred';
      logger.error('Highlight failed:', errorMsg, error);
      this.showStatus(`✗ Highlight failed: ${errorMsg}`, 'error');
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

  showAdvancedLoading() {
    const steps = [
      'Extracting page content...',
      'Converting to markdown...',
      'Preparing for upload...',
      'Saving to repository...'
    ];
    
    const loadingElement = document.getElementById('loading');
    loadingElement.innerHTML = `
      <div class="advanced-spinner">
        <div class="spinner-circle"></div>
      </div>
      <div class="loading-steps">
        <div class="current-step">${steps[0]}</div>
        <div class="progress-dots">
          <span class="dot active"></span>
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    `;
    loadingElement.style.display = 'block';
    
    // Simulate progress through steps
    let currentStep = 0;
    const stepInterval = setInterval(() => {
      currentStep++;
      if (currentStep < steps.length) {
        this.updateLoadingStep(currentStep, steps[currentStep]);
      } else {
        clearInterval(stepInterval);
      }
    }, 800);
    
    this.loadingInterval = stepInterval;
  }

  updateLoadingStep(stepIndex, stepText) {
    const stepElement = document.querySelector('.current-step');
    const dots = document.querySelectorAll('.dot');
    
    if (stepElement) {
      stepElement.textContent = stepText;
    }
    
    dots.forEach((dot, index) => {
      dot.classList.toggle('active', index <= stepIndex);
    });
  }

  showSuccessWithDetails(data) {
    const statusDiv = document.getElementById('status');
    statusDiv.className = 'status success';
    statusDiv.innerHTML = `
      <div class="status-icon">✅</div>
      <div class="status-content">
        <div class="status-title">Page Captured Successfully!</div>
        <div class="status-details">
          <div class="detail-item">
            <strong>File:</strong> ${data.filename}
          </div>
          <div class="detail-item">
            <strong>Folder:</strong> ${data.metadata?.folder || 'unsorted'}
          </div>
          ${data.metadata?.quality ? `
            <div class="detail-item">
              <strong>Quality:</strong> ${this.formatQuality(data.metadata.quality)}
            </div>
          ` : ''}
        </div>
      </div>
    `;
    statusDiv.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      statusDiv.style.display = 'none';
    }, 5000);
  }

  showEnhancedError(error) {
    const errorInfo = window.ErrorHandler ? 
      window.ErrorHandler.createUserFriendlyError(error, 'page capture') :
      { message: error.message, solution: 'Please try again.' };
      
    const statusDiv = document.getElementById('status');
    statusDiv.className = 'status error';
    statusDiv.innerHTML = `
      <div class="status-icon">❌</div>
      <div class="status-content">
        <div class="status-title">Capture Failed</div>
        <div class="status-message">${errorInfo.message}</div>
        ${errorInfo.solution ? `
          <div class="status-solution">
            <strong>Solution:</strong> ${errorInfo.solution}
          </div>
        ` : ''}
      </div>
    `;
    statusDiv.style.display = 'block';
  }

  formatQuality(quality) {
    const percentage = Math.round(quality * 100);
    if (percentage >= 80) return `${percentage}% (Excellent)`;
    if (percentage >= 60) return `${percentage}% (Good)`;
    if (percentage >= 40) return `${percentage}% (Fair)`;
    return `${percentage}% (Poor)`;
  }

  hideLoading() {
    if (this.loadingInterval) {
      clearInterval(this.loadingInterval);
      this.loadingInterval = null;
    }
    document.getElementById('loading').style.display = 'none';
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
