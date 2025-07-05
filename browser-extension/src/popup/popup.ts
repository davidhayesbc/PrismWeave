// Handles the extension popup interface and user interactions

import { IMessageData, IMessageResponse, ISettings, MESSAGE_TYPES } from '../types/index';
import { createLogger } from '../utils/logger';

// Initialize logger
const logger = createLogger('Popup');

export class PrismWeavePopup {
  private currentTab: chrome.tabs.Tab | null = null;
  private settings: Partial<ISettings> | null = null;
  private isCapturing: boolean = false;
  private lastCapturedContent: string | null = null;

  constructor(skipInitialization: boolean = false) {
    // Only log during normal operation, not tests
    if (!skipInitialization) {
      logger.debug('PrismWeavePopup constructor called');
      this.initializePopup();
    }
  }

  // Test accessors - public methods for testing private functionality
  public async testInitializePopup(): Promise<void> {
    return this.initializePopup();
  }

  public async testGetCurrentTab(): Promise<void> {
    return this.getCurrentTab();
  }

  public async testLoadSettings(): Promise<void> {
    return this.loadSettings();
  }

  public testValidateCaptureSettings(): {
    isValid: boolean;
    missingSettings: string[];
    message?: string;
  } {
    return this.validateCaptureSettings();
  }

  public testSetupEventListeners(): void {
    return this.setupEventListeners();
  }

  public testUpdatePageInfo(): void {
    return this.updatePageInfo();
  }

  public testCheckPageCapturability(): void {
    return this.checkPageCapturability();
  }

  public async testCapturePage(): Promise<void> {
    return this.capturePage();
  }

  public async testCaptureSelection(): Promise<void> {
    return this.captureSelection();
  }

  public testIsPageCapturable(): boolean {
    return this.isPageCapturable();
  }

  // Getters for testing state
  public getCurrentTabForTest(): chrome.tabs.Tab | null {
    return this.currentTab;
  }

  public getSettingsForTest(): Partial<ISettings> | null {
    return this.settings;
  }

  public getIsCapturingForTest(): boolean {
    return this.isCapturing;
  }

  public getLastCapturedContentForTest(): string | null {
    return this.lastCapturedContent;
  }

  private async initializePopup(): Promise<void> {
    logger.group('Initializing popup');
    try {
      logger.debug('Getting current tab');
      await this.getCurrentTab();
      logger.debug('Current tab obtained:', this.currentTab);

      logger.debug('Loading settings');
      await this.loadSettings();
      logger.debug('Settings loaded:', this.settings);

      logger.debug('Updating page info');
      this.updatePageInfo();
      logger.debug('Setting up event listeners');
      this.setupEventListeners();

      logger.debug('Checking page capturability');
      this.checkPageCapturability();

      logger.info('Initialization complete');
    } catch (error) {
      logger.error('Error initializing popup:', error);
      this.showError('Failed to initialize extension popup');
    } finally {
      logger.groupEnd();
    }
  }
  private async getCurrentTab(): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs: chrome.tabs.Tab[]) => {
        if (chrome.runtime.lastError) {
          logger.error('Chrome tabs API error:', chrome.runtime.lastError.message);
          reject(new Error(chrome.runtime.lastError.message));
        } else if (tabs.length > 0 && tabs[0]) {
          this.currentTab = tabs[0];
          logger.debug('Current tab found:', {
            id: this.currentTab.id,
            url: this.currentTab.url,
            title: this.currentTab.title,
          });
          resolve();
        } else {
          logger.warn('No active tab found in current window');
          reject(new Error('No active tab found'));
        }
      });
    });
  }

  private async loadSettings(): Promise<void> {
    try {
      const response = await this.sendMessageToBackground(MESSAGE_TYPES.GET_SETTINGS);
      this.settings = response.data as Partial<ISettings>;
    } catch (error) {
      logger.error('Error loading settings:', error);
      this.settings = {};
    }
  }

  private setupEventListeners(): void {
    // Capture page button
    const captureBtn = document.getElementById('capture-page');
    if (captureBtn) {
      captureBtn.addEventListener('click', () => this.capturePage());
    }

    // Capture selection button
    const captureSelectionBtn = document.getElementById('capture-selection');
    if (captureSelectionBtn) {
      captureSelectionBtn.addEventListener('click', () => this.captureSelection());
    }

    // Settings button
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
      settingsBtn.addEventListener('click', () => this.openSettings());
    } // View repository button
    const viewRepoBtn = document.getElementById('view-repo');
    if (viewRepoBtn) {
      viewRepoBtn.addEventListener('click', () => this.openRepository());
    }
  }

  private updatePageInfo(): void {
    if (!this.currentTab) return;

    // Update page title
    const titleElement = document.getElementById('page-title');
    if (titleElement) {
      titleElement.textContent = this.currentTab.title || 'Unknown page';
    }

    // Update page URL
    const urlElement = document.getElementById('page-url');
    if (urlElement) {
      const url = new URL(this.currentTab.url || '');
      urlElement.textContent = `${url.hostname}${url.pathname}`;
      urlElement.title = this.currentTab.url || '';
    }

    // Update favicon if available
    const faviconElement = document.getElementById('page-favicon') as HTMLImageElement;
    if (faviconElement && this.currentTab.favIconUrl) {
      faviconElement.src = this.currentTab.favIconUrl;
      faviconElement.style.display = 'block';
    }
  }
  /**
   * Validates that crucial settings are configured for capture operations
   * @returns Object with validation results and missing settings
   */
  private validateCaptureSettings(): {
    isValid: boolean;
    missingSettings: string[];
    message?: string;
  } {
    const missingSettings: string[] = [];

    if (!this.settings) {
      return {
        isValid: false,
        missingSettings: ['settings'],
        message: 'Settings not loaded. Please try refreshing the extension.',
      };
    }

    // Check crucial repository settings
    if (!this.settings.githubToken) {
      missingSettings.push('GitHub Token');
    }

    if (!this.settings.githubRepo) {
      missingSettings.push('GitHub Repository');
    }

    const isValid = missingSettings.length === 0;

    if (!isValid) {
      const settingsText = missingSettings.length === 1 ? 'setting' : 'settings';
      const message = `Missing required ${settingsText}: ${missingSettings.join(', ')}. Please configure these in the extension settings.`;
      return { isValid, missingSettings, message };
    }

    return { isValid, missingSettings };
  }
  private checkPageCapturability(): void {
    if (!this.currentTab?.url) return;

    const isCapturable = this.isPageCapturable();

    const captureBtn = document.getElementById('capture-page') as HTMLButtonElement;
    const captureSelectionBtn = document.getElementById('capture-selection') as HTMLButtonElement;
    const warningContainer = document.getElementById('capture-warning');

    if (isCapturable) {
      if (captureBtn) captureBtn.disabled = false;
      if (captureSelectionBtn) captureSelectionBtn.disabled = false;
      if (warningContainer) warningContainer.style.display = 'none';
    } else {
      if (captureBtn) captureBtn.disabled = true;
      if (captureSelectionBtn) captureSelectionBtn.disabled = true;
      if (warningContainer) {
        warningContainer.style.display = 'block';
        // The warning content is already set in the HTML
      }
    }
  }
  private async capturePage(): Promise<void> {
    if (this.isCapturing) return;

    try {
      this.isCapturing = true;

      // First test connection to background service worker
      this.updateCaptureStatus(
        'Connecting...',
        'Testing connection to background service',
        'progress',
        { showProgress: true, progressValue: 10 }
      );

      try {
        const testResponse = await this.sendMessageToBackground('TEST');
        logger.info('Background service worker connected:', testResponse);
      } catch (error) {
        throw new Error(
          `Failed to connect to background service worker: ${(error as Error).message}`
        );
      }

      // Check if we have a current tab, and try to get it if not
      if (!this.currentTab?.id) {
        logger.warn('No current tab available, attempting to refresh tab info');
        try {
          await this.getCurrentTab();
        } catch (error) {
          logger.error('Failed to get current tab:', error);
          this.updateCaptureStatus('No active tab available for capture', 'error');
          setTimeout(() => this.resetCaptureStatus(), 3000);
          return;
        }
      }

      // Double-check we now have a valid tab ID
      if (!this.currentTab?.id) {
        this.updateCaptureStatus('Unable to identify current tab', 'error');
        setTimeout(() => this.resetCaptureStatus(), 3000);
        return;
      } // Validate crucial settings before proceeding
      const settingsValidation = this.validateCaptureSettings();
      if (!settingsValidation.isValid) {
        this.showMissingSettingsMessage(
          settingsValidation.message!,
          settingsValidation.missingSettings
        );
        return;
      }

      // Check if page is capturable
      if (!this.isPageCapturable()) {
        this.updateCaptureStatus(
          'Page Cannot Be Captured',
          'This type of page (browser internal page) cannot be captured.',
          'error',
          { autoHide: 4000 }
        );
        return;
      }

      this.updateCaptureStatus(
        'Capturing Page...',
        'Extracting content and preparing markdown',
        'progress',
        { showProgress: true, progressValue: 20 }
      );

      const message: IMessageData = {
        type: MESSAGE_TYPES.CAPTURE_PAGE,
        data: {
          tabId: this.currentTab.id,
          tabInfo: {
            url: this.currentTab.url,
            title: this.currentTab.title,
          },
          settings: this.settings,
        },
      };

      // Update progress
      this.updateCaptureStatus(
        'Processing Content...',
        'Converting to markdown format',
        'progress',
        { showProgress: true, progressValue: 60 }
      );
      logger.debug('Sending capture message:', message);
      const response = await this.sendMessageToBackground(message.type, message.data);
      if (response.success) {
        const responseData = response.data as any;
        const saveResult = responseData?.saveResult;
        logger.debug('CAPTURE responseData:', responseData);
        // Try to extract markdown from the correct location
        let markdownContent: string | null = null;
        if (responseData?.markdown) {
          markdownContent = responseData.markdown;
        } else if (responseData?.data?.markdown) {
          markdownContent = responseData.data.markdown;
        } else if (responseData?.content) {
          markdownContent = responseData.content;
        }
        this.lastCapturedContent = markdownContent;
        logger.debug('Stored captured content for preview, length:', markdownContent?.length || 0);

        // Determine success message based on save result
        let statusTitle = 'Page Captured Successfully!';
        let statusMessage = '';
        let statusType: 'success' | 'warning' = 'success';

        if (saveResult?.success && saveResult.committed) {
          statusMessage = `Saved and committed: ${responseData?.filename || 'document.md'}`;
          if (saveResult.sha) {
            statusMessage += ` (${saveResult.sha.substring(0, 7)})`;
          }
        } else if (saveResult?.success && !saveResult.committed) {
          statusTitle = 'Page Captured (Not Committed)';
          statusMessage = `Content saved as: ${responseData?.filename || 'document.md'}`;
          if (saveResult.reason) {
            statusMessage += ` - ${saveResult.reason}`;
          }
          statusType = 'warning';
        } else if (saveResult && !saveResult.success) {
          statusTitle = 'Page Captured (Save Failed)';
          statusMessage = `Content extracted but save failed: ${saveResult.error || 'Unknown error'}`;
          statusType = 'warning';
        } else {
          statusMessage = `Content extracted as: ${responseData?.filename || 'document.md'}`;
        }

        // Prepare actions based on save status
        const actions = [];

        if (saveResult?.success && saveResult.url) {
          actions.push({
            label: 'View on GitHub',
            action: () => window.open(saveResult.url, '_blank'),
            primary: true,
          });
        } else if (this.settings?.githubRepo) {
          actions.push({
            label: 'View Repository',
            action: () => this.openRepository(),
            primary: true,
          });
        }

        // Replace "Capture Another" with "Preview Markdown" when content is available
        if (this.lastCapturedContent) {
          actions.push({
            label: 'Preview Markdown',
            action: () => this.showMarkdownPreview(),
          });
        }

        // Add retry action if save failed
        if (saveResult && !saveResult.success) {
          actions.push({
            label: 'Check Settings',
            action: () => this.openSettings(),
          });
        }

        this.updateCaptureStatus(statusTitle, statusMessage, statusType, {
          autoHide: statusType === 'success' ? 5000 : 8000,
          actions,
        });
      } else {
        throw new Error(response.error || 'Capture failed');
      }
    } catch (error) {
      logger.error('Error capturing page:', error);
      const errorMessage = (error as Error).message;

      this.updateCaptureStatus('Capture Failed', errorMessage, 'error', {
        autoHide: 6000,
        actions: [
          {
            label: 'Try Again',
            action: () => {
              this.resetCaptureStatus();
              setTimeout(() => this.capturePage(), 100);
            },
            primary: true,
          },
          {
            label: 'Open Settings',
            action: () => this.openSettings(),
          },
        ],
      });
    } finally {
      this.isCapturing = false;
    }
  }

  private isPageCapturable(): boolean {
    if (!this.currentTab?.url) return false;

    const url = this.currentTab.url;
    return (
      !url.startsWith('chrome://') &&
      !url.startsWith('chrome-extension://') &&
      !url.startsWith('edge://') &&
      !url.startsWith('about:') &&
      !url.startsWith('moz-extension://') &&
      (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('file://'))
    );
  }
  private async captureSelection(): Promise<void> {
    if (this.isCapturing) return;

    try {
      this.isCapturing = true;

      // Check if we have a current tab, and try to get it if not
      if (!this.currentTab?.id) {
        logger.warn('No current tab available, attempting to refresh tab info');
        try {
          await this.getCurrentTab();
        } catch (error) {
          logger.error('Failed to get current tab:', error);
          this.updateCaptureStatus('No active tab available for capture', 'error');
          setTimeout(() => this.resetCaptureStatus(), 3000);
          return;
        }
      }

      // Double-check we now have a valid tab ID
      if (!this.currentTab?.id) {
        this.updateCaptureStatus('Unable to identify current tab', 'error');
        setTimeout(() => this.resetCaptureStatus(), 3000);
        return;
      } // Validate crucial settings before proceeding
      const settingsValidation = this.validateCaptureSettings();
      if (!settingsValidation.isValid) {
        this.showMissingSettingsMessage(
          settingsValidation.message!,
          settingsValidation.missingSettings
        );
        return;
      }

      // Check if page is capturable
      if (!this.isPageCapturable()) {
        this.updateCaptureStatus(
          'Page Cannot Be Captured',
          'This type of page (browser internal page) cannot be captured.',
          'error',
          { autoHide: 4000 }
        );
        return;
      }

      this.updateCaptureStatus(
        'Checking Selection...',
        'Looking for selected text on the page',
        'progress',
        { showProgress: true, progressValue: 30 }
      );

      // First, check if there's a selection
      const selectionCheck = await this.sendMessageToTab('GET_PAGE_INFO');
      if (!(selectionCheck.data as any)?.hasSelection) {
        this.updateCaptureStatus(
          'No Selection Found',
          'Please select some text on the page before capturing',
          'warning',
          {
            autoHide: 5000,
            actions: [
              {
                label: 'Capture Entire Page',
                action: () => {
                  this.resetCaptureStatus();
                  setTimeout(() => this.capturePage(), 100);
                },
                primary: true,
              },
            ],
          }
        );
        return;
      }

      this.updateCaptureStatus(
        'Capturing Selection...',
        'Processing selected content',
        'progress',
        { showProgress: true, progressValue: 70 }
      );

      const message: IMessageData = {
        type: 'CAPTURE_SELECTION',
        data: {
          tabId: this.currentTab.id,
          settings: this.settings,
        },
      };

      const response = await this.sendMessageToTab(message.type, message.data);

      if (response.success) {
        const responseData = response.data as any;
        this.updateCaptureStatus(
          'Selection Captured Successfully!',
          `Saved selected content as: ${responseData?.filename || 'selection.md'}`,
          'success',
          {
            autoHide: 5000,
            actions: [
              {
                label: 'View Repository',
                action: () => this.openRepository(),
                primary: true,
              },
              {
                label: 'Capture More',
                action: () => this.resetCaptureStatus(),
              },
            ],
          }
        );
      } else {
        throw new Error(response.error || 'Selection capture failed');
      }
    } catch (error) {
      logger.error('Error capturing selection:', error);
      const errorMessage = (error as Error).message;

      this.updateCaptureStatus('Selection Capture Failed', errorMessage, 'error', {
        autoHide: 6000,
        actions: [
          {
            label: 'Try Again',
            action: () => {
              this.resetCaptureStatus();
              setTimeout(() => this.captureSelection(), 100);
            },
            primary: true,
          },
          {
            label: 'Capture Full Page',
            action: () => {
              this.resetCaptureStatus();
              setTimeout(() => this.capturePage(), 100);
            },
          },
        ],
      });
    } finally {
      this.isCapturing = false;
    }
  }
  /**
   * Enhanced status update method with rich UI feedback
   * @param title The main status title
   * @param message Optional detailed message
   * @param type Status type (success, error, progress, warning)
   * @param options Additional options for the status display
   */
  private updateCaptureStatus(
    title: string,
    message?: string,
    type: 'progress' | 'success' | 'error' | 'warning' = 'progress',
    options: {
      showProgress?: boolean;
      progressValue?: number;
      actions?: Array<{ label: string; action: () => void; primary?: boolean }>;
      autoHide?: number;
      details?: string[];
    } = {}
  ): void {
    const container = document.getElementById('capture-status');
    if (!container) return;

    // Update container class
    container.className = `capture-status-container ${type}`;

    // Update icon based on type
    const iconElement = document.getElementById('status-icon');
    if (iconElement) {
      const icons = {
        success: '✓',
        error: '⚠',
        progress: '⟳',
        warning: '⚠',
      };
      iconElement.textContent = icons[type];
    }

    // Update title
    const titleElement = document.getElementById('status-title');
    if (titleElement) {
      titleElement.textContent = title;
    }

    // Update message
    const messageElement = document.getElementById('status-message');
    if (messageElement) {
      messageElement.textContent = message || '';
      messageElement.style.display = message ? 'block' : 'none';
    }

    // Handle progress bar
    const progressBar = document.getElementById('progress-bar');
    const progressFill = progressBar?.querySelector('.progress-fill') as HTMLElement;
    if (options.showProgress && progressBar && progressFill) {
      progressBar.style.display = 'block';
      progressFill.style.width = `${options.progressValue || 0}%`;
    } else if (progressBar) {
      progressBar.style.display = 'none';
    }

    // Handle actions
    const actionsContainer = document.getElementById('status-actions');
    if (options.actions && actionsContainer) {
      actionsContainer.innerHTML = '';
      options.actions.forEach(action => {
        const button = document.createElement('button');
        button.className = `status-action-btn ${action.primary ? 'primary' : ''}`;
        button.textContent = action.label;
        button.addEventListener('click', action.action);
        actionsContainer.appendChild(button);
      });
      actionsContainer.style.display = 'flex';
    } else if (actionsContainer) {
      actionsContainer.style.display = 'none';
    }

    // Handle details
    const detailsContainer = document.getElementById('status-details');
    if ((options.showProgress || options.actions) && detailsContainer) {
      detailsContainer.style.display = 'block';
    } else if (detailsContainer) {
      detailsContainer.style.display = 'none';
    }

    // Setup close button
    const closeButton = document.getElementById('status-close');
    if (closeButton) {
      closeButton.onclick = () => this.resetCaptureStatus();
    }

    // Show container
    container.style.display = 'block';

    // Auto-hide if specified
    if (options.autoHide) {
      setTimeout(() => this.resetCaptureStatus(), options.autoHide);
    }
  }

  /**
   * Shows enhanced missing settings message with better UX
   * @param message The error message to display
   * @param missingSettings Array of missing setting names
   */
  private showMissingSettingsMessage(message: string, missingSettings: string[] = []): void {
    const container = document.getElementById('capture-status');
    if (!container) return;

    // Custom HTML for missing settings
    container.innerHTML = `
      <div class="status-card">
        <div class="status-header">
          <div class="status-icon-wrapper">
            <div class="status-icon">⚙️</div>
          </div>
          <div class="status-content">
            <div class="status-title">Configuration Required</div>
            <div class="status-message">${message}</div>
          </div>
          <button class="status-close" id="missing-settings-close" aria-label="Close">×</button>
        </div>
        <div class="status-details" style="display: block;">
          <div class="missing-settings-content">
            ${
              missingSettings.length > 0
                ? `

              <div class="missing-settings-text">
                <strong>Missing settings:</strong> ${missingSettings.join(', ')}
              </div>
            `
                : ''
            }
            <button id="open-settings-action" class="settings-action-btn">
              ⚙️ Configure Settings
            </button>
          </div>
        </div>
      </div>
    `;

    container.className = 'capture-status-container missing-settings';
    container.style.display = 'block';

    // Setup event handlers
    const openSettingsBtn = document.getElementById('open-settings-action');
    const closeBtn = document.getElementById('missing-settings-close');

    if (openSettingsBtn) {
      openSettingsBtn.addEventListener('click', () => {
        this.openSettings();
        setTimeout(() => this.resetCaptureStatus(), 500);
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.resetCaptureStatus());
    }

    // Auto-hide after 12 seconds (longer for settings issues)
    setTimeout(() => this.resetCaptureStatus(), 12000);
  }
  private resetCaptureStatus(): void {
    const statusElement = document.getElementById('capture-status');
    if (statusElement) {
      statusElement.style.display = 'none';
      statusElement.textContent = '';
      statusElement.className = 'capture-status';
    }
    this.lastCapturedContent = null;
  }

  private openSettings(): void {
    chrome.runtime.openOptionsPage();
  }

  private openRepository(): void {
    if (this.settings?.githubRepo) {
      const url = `https://github.com/${this.settings.githubRepo}`;
      chrome.tabs.create({ url });
    }
  }

  private showError(message: string): void {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
      errorElement.textContent = message;
      errorElement.style.display = 'block';
    }
  }

  private async sendMessageToBackground(type: string, data?: any): Promise<IMessageResponse> {
    return new Promise<IMessageResponse>((resolve, reject) => {
      const message: IMessageData = { type, data };

      chrome.runtime.sendMessage(message, (response: IMessageResponse) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else {
          resolve(response);
        }
      });
    });
  }

  private async sendMessageToTab(type: string, data?: any): Promise<IMessageResponse> {
    if (!this.currentTab?.id) {
      throw new Error('No active tab available');
    }

    return new Promise<IMessageResponse>((resolve, reject) => {
      const message: IMessageData = { type, data };

      chrome.tabs.sendMessage(this.currentTab!.id!, message, (response: IMessageResponse) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else {
          resolve(response);
        }
      });
    });
  }

  private showMarkdownPreview(): void {
    if (!this.lastCapturedContent) {
      this.showError('No markdown content available for preview');
      return;
    }

    // Create preview modal
    const modal = document.createElement('div');
    modal.className = 'markdown-preview-modal';
    modal.innerHTML = `
      <div class="modal-backdrop"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>Markdown Preview</h3>
          <button class="modal-close" aria-label="Close">×</button>
        </div>
        <div class="modal-body">
          <div class="preview-controls">
            <button class="copy-button" title="Copy to clipboard">📋 Copy</button>
            <span class="content-stats">${this.lastCapturedContent.length} characters</span>
          </div>
          <pre class="markdown-content">${this.escapeHtml(this.lastCapturedContent)}</pre>
        </div>
      </div>
    `;

    // Add modal to document
    document.body.appendChild(modal);

    // Setup event listeners
    const closeBtn = modal.querySelector('.modal-close') as HTMLButtonElement;
    const backdrop = modal.querySelector('.modal-backdrop') as HTMLDivElement;
    const copyBtn = modal.querySelector('.copy-button') as HTMLButtonElement;

    const closeModal = () => {
      modal.remove();
    };

    closeBtn.addEventListener('click', closeModal);
    backdrop.addEventListener('click', closeModal);

    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(this.lastCapturedContent!);
        copyBtn.textContent = '✅ Copied!';
        setTimeout(() => {
          copyBtn.textContent = '📋 Copy';
        }, 2000);
      } catch (error) {
        logger.error('Failed to copy to clipboard:', error);
        copyBtn.textContent = '❌ Failed';
        setTimeout(() => {
          copyBtn.textContent = '📋 Copy';
        }, 2000);
      }
    });

    // Close on Escape key
    const handleKeydown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        closeModal();
        document.removeEventListener('keydown', handleKeydown);
      }
    };
    document.addEventListener('keydown', handleKeydown);
  }
  private escapeHtml(unsafe: string): string {
    return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

// Make available globally for service worker importScripts compatibility
if (typeof globalThis !== 'undefined') {
  (globalThis as any).PrismWeavePopup = PrismWeavePopup;
} else if (typeof self !== 'undefined') {
  (self as any).PrismWeavePopup = PrismWeavePopup;
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new PrismWeavePopup();
});
