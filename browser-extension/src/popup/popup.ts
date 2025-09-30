// Handles the extension popup interface and user interactions

import { IMessageData, IMessageResponse, ISettings, MESSAGE_TYPES } from '../types/types';
import { createLogger } from '../utils/logger';

// Initialize logger
const logger = createLogger('Popup');

// Dependencies interface for better testability
export interface IPopupDependencies {
  chrome?: typeof chrome;
  document?: Document;
  window?: Window;
  autoInitialize?: boolean;
}

export class PrismWeavePopup {
  private currentTab: chrome.tabs.Tab | null = null;
  private settings: Partial<ISettings> | null = null;
  private isCapturing: boolean = false;
  private lastCapturedContent: string | null = null;
  private eventListenersSetup: boolean = false;
  private openRepositoryDebounceTimer: NodeJS.Timeout | null = null;
  private statusTemplateHTML: string | null = null;
  private themeToggleSetup: boolean = false;

  // Dependencies for testability
  private chrome: typeof chrome;
  private document: Document;
  private window: Window;

  constructor(dependencies: IPopupDependencies = {}) {
    this.chrome = dependencies.chrome || (globalThis as any).chrome;
    this.document = dependencies.document || (globalThis as any).document;
    this.window = dependencies.window || (globalThis as any).window;

    logger.debug('PrismWeavePopup constructor called');

    // Allow tests to skip auto-initialization
    if (dependencies.autoInitialize !== false) {
      this.initializePopup();
    }
  }

  // Public getters for testing
  public get currentTabForTest(): chrome.tabs.Tab | null {
    return this.currentTab;
  }

  public get settingsForTest(): Partial<ISettings> | null {
    return this.settings;
  }

  public get isCapturingForTest(): boolean {
    return this.isCapturing;
  }

  public get lastCapturedContentForTest(): string | null {
    return this.lastCapturedContent;
  }

  // Public methods for testing
  public async initializeForTest(): Promise<void> {
    return this.initializePopup();
  }

  public async getCurrentTabForTest(): Promise<void> {
    return this.getCurrentTab();
  }

  public async loadSettingsForTest(): Promise<void> {
    return this.loadSettings();
  }

  public validateCaptureSettingsForTest(): {
    isValid: boolean;
    missingSettings: string[];
    message?: string;
  } {
    return this.validateCaptureSettings();
  }

  public setupEventListenersForTest(): void {
    return this.setupEventListeners();
  }

  public updatePageInfoForTest(): void {
    return this.updatePageInfo();
  }

  public checkPageCapturabilityForTest(): void {
    return this.checkPageCapturability();
  }

  public isPageCapturableForTest(): boolean {
    return this.isPageCapturable();
  }

  public isPDFPageForTest(): boolean {
    return this.isPDFPage();
  }

  public async capturePDFForTest(): Promise<void> {
    return this.capturePDF();
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

      logger.debug('Setting up theme toggle');
      this.setupThemeToggle();

      this.cacheStatusTemplate();

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
      this.chrome.tabs.query({ active: true, currentWindow: true }, (tabs: chrome.tabs.Tab[]) => {
        if (this.chrome.runtime.lastError) {
          logger.error('Chrome tabs API error:', this.chrome.runtime.lastError.message);
          reject(new Error(this.chrome.runtime.lastError.message));
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
    // Prevent duplicate event listeners
    if (this.eventListenersSetup) {
      logger.debug('Event listeners already setup, skipping...');
      return;
    }

    // Unified capture content button
    const captureContentBtn = this.document.getElementById('capture-content');
    if (captureContentBtn) {
      captureContentBtn.addEventListener('click', e => {
        e.stopPropagation();
        e.preventDefault();
        logger.debug('Capture content button clicked');
        this.captureContent();
      });
    }

    // Settings button
    const settingsBtn = this.document.getElementById('settings-btn');
    if (settingsBtn) {
      settingsBtn.addEventListener('click', e => {
        e.stopPropagation();
        e.preventDefault();
        logger.debug('Settings button clicked');
        this.openSettings();
      });
    }

    // View repository button
    const viewRepoBtn = this.document.getElementById('view-repo');
    if (viewRepoBtn) {
      viewRepoBtn.addEventListener('click', e => {
        e.stopPropagation();
        e.preventDefault();
        logger.debug('View repository button clicked');
        this.openRepository();
      });
    }

    // Mark event listeners as setup
    this.eventListenersSetup = true;
    logger.debug('Event listeners setup completed');
  }

  private setupThemeToggle(): void {
    // Prevent duplicate theme toggle setup
    if (this.themeToggleSetup) {
      logger.debug('Theme toggle already setup, skipping...');
      return;
    }

    const storageKey = 'prismweave-theme';
    const root = this.document.documentElement;
    const toggle = this.document.querySelector('[data-theme-toggle]') as HTMLButtonElement;

    const systemTheme = (): string => {
      return this.window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    const setTheme = (theme: string): void => {
      root.dataset.theme = theme;
      if (toggle) {
        toggle.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`);
      }
      logger.debug('Theme set to:', theme);
    };

    const getStoredTheme = (): string | null => {
      try {
        return localStorage.getItem(storageKey);
      } catch (error) {
        logger.warn('Failed to get stored theme:', error);
        return null;
      }
    };

    // Initialize theme
    const storedTheme = getStoredTheme();
    const initialTheme = storedTheme || root.dataset.theme || systemTheme();
    setTheme(initialTheme);

    // Listen for system theme changes
    this.window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
      if (!getStoredTheme()) {
        setTheme(event.matches ? 'dark' : 'light');
      }
    });

    // Setup toggle button
    if (toggle) {
      toggle.addEventListener('click', () => {
        const currentTheme = root.dataset.theme || 'light';
        const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(nextTheme);

        try {
          localStorage.setItem(storageKey, nextTheme);
          logger.debug('Theme preference saved:', nextTheme);
        } catch (error) {
          logger.warn('Failed to save theme preference:', error);
        }
      });
    } else {
      logger.warn('Theme toggle button not found');
    }

    this.themeToggleSetup = true;
    logger.debug('Theme toggle setup completed');
  }

  private cacheStatusTemplate(): void {
    if (this.statusTemplateHTML) {
      return;
    }

    const container = this.document.getElementById('capture-status');
    if (container) {
      this.statusTemplateHTML = container.innerHTML;
    }
  }

  private ensureStatusTemplate(): HTMLElement | null {
    const container = this.document.getElementById('capture-status');
    if (!container) {
      return null;
    }

    if (!this.statusTemplateHTML) {
      this.statusTemplateHTML = container.innerHTML;
    } else if (!container.querySelector('#status-title')) {
      container.innerHTML = this.statusTemplateHTML;
    }

    return container;
  }

  private updatePageInfo(): void {
    if (!this.currentTab) return;

    // Update page title
    const titleElement = this.document.getElementById('page-title');
    if (titleElement) {
      titleElement.textContent = this.currentTab.title || 'Unknown page';
    }

    // Update page URL
    const urlElement = this.document.getElementById('page-url');
    if (urlElement) {
      const url = new URL(this.currentTab.url || '');
      urlElement.textContent = `${url.hostname}${url.pathname}`;
      urlElement.title = this.currentTab.url || '';
    }

    // Update favicon if available
    const faviconElement = this.document.getElementById('page-favicon') as HTMLImageElement;
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

  private async captureContent(): Promise<void> {
    if (this.isCapturing) return;

    try {
      this.isCapturing = true;

      // First test connection to background service worker
      this.updateCaptureStatus(
        'Connecting...',
        'Testing connection to background service',
        'progress',
        { showProgress: true, progressValue: 5 }
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
      }

      // Validate crucial settings before proceeding
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
        'Detecting Content Type...',
        'Analyzing page to determine the best capture method (HTML vs PDF)',
        'progress',
        { showProgress: true, progressValue: 15 }
      );

      // Send trigger to service worker to handle content script communication
      // This uses the same flow as keyboard shortcut but initiated from popup
      const message: IMessageData = {
        type: 'TRIGGER_CAPTURE_FROM_POPUP',
        data: {
          tabId: this.currentTab.id,
          timestamp: Date.now(),
        },
      };

      // Update progress
      this.updateCaptureStatus(
        'Processing Content...',
        'Using intelligent content detection to capture with best method',
        'progress',
        { showProgress: true, progressValue: 60 }
      );

      logger.debug(
        'Sending capture trigger to service worker (same as keyboard shortcut):',
        message
      );
      const response = await this.sendMessageToBackground(message.type, message.data);

      if (response.success) {
        logger.debug(
          'Capture initiated successfully via content script (same as keyboard shortcut)'
        );

        // The content script now handles the entire capture process including notifications
        // Just show a simple "initiated" message in the popup
        this.updateCaptureStatus(
          'Content Capture Initiated!',
          'Using the same proven method as the keyboard shortcut. Check the page for progress updates.',
          'success',
          {
            autoHide: 3000,
            actions: [
              {
                label: 'Close',
                action: () => window.close(),
                primary: true,
              },
            ],
          }
        );
      } else {
        throw new Error(response.error || 'Content capture failed');
      }
    } catch (error) {
      logger.error('Error capturing content:', error);
      const errorMessage = (error as Error).message;

      // Provide more specific actions based on error type
      const actions = [];

      if (
        errorMessage.includes('Content script not ready') ||
        errorMessage.includes('refresh the page')
      ) {
        actions.push({
          label: 'Refresh Page',
          action: () => {
            if (this.currentTab?.id) {
              this.chrome.tabs.reload(this.currentTab.id);
            }
          },
          primary: true,
        });
        actions.push({
          label: 'Try Again',
          action: () => {
            this.resetCaptureStatus();
            setTimeout(() => this.captureContent(), 1000);
          },
        });
      } else if (errorMessage.includes('Extension needs to be reloaded')) {
        actions.push({
          label: 'Reload Extension',
          action: () => {
            this.chrome.runtime.reload();
          },
          primary: true,
        });
      } else {
        actions.push({
          label: 'Try Again',
          action: () => {
            this.resetCaptureStatus();
            setTimeout(() => this.captureContent(), 100);
          },
          primary: true,
        });
        actions.push({
          label: 'Open Settings',
          action: () => this.openSettings(),
        });
      }

      this.updateCaptureStatus('Content Capture Failed', errorMessage, 'error', {
        autoHide: 8000,
        actions,
      });
    } finally {
      this.isCapturing = false;
    }
  }
  private checkPageCapturability(): void {
    if (!this.currentTab?.url) return;

    const isCapturable = this.isPageCapturable();

    const captureContentBtn = this.document.getElementById('capture-content') as HTMLButtonElement;
    const warningContainer = this.document.getElementById('capture-warning');

    // Handle capture buttons
    if (isCapturable) {
      if (captureContentBtn) captureContentBtn.disabled = false;
      if (warningContainer) warningContainer.style.display = 'none';
    } else {
      if (captureContentBtn) captureContentBtn.disabled = true;
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

      // Step 1: Initial setup and detection
      this.updateCaptureStatus(
        'Initializing Capture...',
        'Detecting page type and preparing capture',
        'progress',
        { showProgress: true, progressValue: 10 }
      );

      // Detect if current page is a PDF to use appropriate capture method
      const isPDF = this.isCurrentPagePDF();
      const messageType = isPDF ? MESSAGE_TYPES.CAPTURE_CONTENT : MESSAGE_TYPES.CAPTURE_PAGE;

      logger.debug(
        `Page type detected: ${isPDF ? 'PDF' : 'HTML'}, using message type: ${messageType}`
      );

      // Step 2: Preparing message
      this.updateCaptureStatus(
        'Preparing Capture...',
        `Setting up ${isPDF ? 'PDF' : 'HTML'} capture process`,
        'progress',
        { showProgress: true, progressValue: 20 }
      );

      const message: IMessageData = {
        type: messageType,
        data: {
          tabId: this.currentTab.id,
          tabInfo: {
            url: this.currentTab.url,
            title: this.currentTab.title,
          },
          settings: this.settings,
        },
      };

      // Step 3: Sending to background
      this.updateCaptureStatus(
        'Connecting to Service...',
        'Sending capture request to background service',
        'progress',
        { showProgress: true, progressValue: 30 }
      );
      logger.debug('Sending capture message:', message);

      // Step 4: Processing content
      this.updateCaptureStatus(
        'Processing Content...',
        `Extracting and processing ${isPDF ? 'PDF' : 'HTML'} content`,
        'progress',
        { showProgress: true, progressValue: 50 }
      );

      // Add timeout to prevent indefinite hanging, especially for PDFs in Edge
      const timeoutMs = 30000; // 30 seconds timeout
      const capturePromise = this.sendMessageToBackground(message.type, message.data);
      const timeoutPromise = new Promise<never>((_, reject) => {
        setTimeout(() => {
          reject(
            new Error(
              `Capture operation timed out after ${timeoutMs / 1000} seconds - stuck at: Processing Content`
            )
          );
        }, timeoutMs);
      });

      // Step 5: Waiting for response
      this.updateCaptureStatus(
        'Finalizing Capture...',
        'Converting content and preparing for save',
        'progress',
        { showProgress: true, progressValue: 70 }
      );

      const response = await Promise.race([capturePromise, timeoutPromise]);

      // Step 6: Processing response
      this.updateCaptureStatus(
        'Processing Response...',
        'Analyzing capture results and preparing display',
        'progress',
        { showProgress: true, progressValue: 85 }
      );

      if (response.success) {
        const responseData = response.data as any;
        const saveResult = responseData?.saveResult;
        logger.debug('CAPTURE responseData:', responseData);

        // Step 7: Extracting content
        this.updateCaptureStatus(
          'Extracting Content...',
          'Parsing captured content and metadata',
          'progress',
          { showProgress: true, progressValue: 95 }
        );
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
            action: () => this.window.open(saveResult.url, '_blank'),
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

  private isPDFPage(): boolean {
    if (!this.currentTab?.url) return false;

    const url = this.currentTab.url;

    // Check if URL ends with .pdf
    if (url.toLowerCase().endsWith('.pdf')) {
      return true;
    }

    // Check if URL contains PDF indicators
    if (url.toLowerCase().includes('.pdf')) {
      return true;
    }

    // Check if it's a common PDF viewer URL pattern
    const pdfPatterns = [/\/pdf\//i, /\.pdf$/i, /\.pdf\?/i, /\.pdf#/i, /application\/pdf/i];

    return pdfPatterns.some(pattern => pattern.test(url));
  }

  private isCurrentPagePDF(): boolean {
    return this.isPDFPage();
  }

  private async capturePDF(): Promise<void> {
    if (this.isCapturing) return;

    try {
      this.isCapturing = true;

      // Check if we have a current tab
      if (!this.currentTab?.id) {
        logger.warn('No current tab available, attempting to refresh tab info');
        try {
          await this.getCurrentTab();
        } catch (error) {
          logger.error('Failed to get current tab:', error);
          this.updateCaptureStatus('No active tab available for PDF capture', 'error');
          setTimeout(() => this.resetCaptureStatus(), 3000);
          return;
        }
      }

      // Double-check we now have a valid tab ID
      if (!this.currentTab?.id) {
        this.updateCaptureStatus('Unable to identify current tab', 'error');
        setTimeout(() => this.resetCaptureStatus(), 3000);
        return;
      }

      // Validate crucial settings before proceeding
      const settingsValidation = this.validateCaptureSettings();
      if (!settingsValidation.isValid) {
        this.showMissingSettingsMessage(
          settingsValidation.message!,
          settingsValidation.missingSettings
        );
        return;
      }

      // Check if current page is a PDF
      this.updateCaptureStatus(
        'Checking PDF...',
        'Verifying if current page is a PDF document',
        'progress',
        { showProgress: true, progressValue: 10 }
      );

      const checkMessage: IMessageData = {
        type: MESSAGE_TYPES.CHECK_PDF,
        data: {
          tabId: this.currentTab.id,
          url: this.currentTab.url,
        },
      };

      const checkResponse = await this.sendMessageToBackground(
        checkMessage.type,
        checkMessage.data
      );

      if (!checkResponse.success || !(checkResponse.data as { isPDF: boolean })?.isPDF) {
        this.updateCaptureStatus(
          'Not a PDF Document',
          'The current page is not a PDF file. Please navigate to a PDF document first.',
          'error',
          { autoHide: 4000 }
        );
        return;
      }

      // Proceed with PDF capture
      this.updateCaptureStatus(
        'Downloading PDF...',
        'Fetching PDF content from the current page',
        'progress',
        { showProgress: true, progressValue: 40 }
      );

      const captureMessage: IMessageData = {
        type: MESSAGE_TYPES.CAPTURE_PDF,
        data: {
          tabId: this.currentTab.id,
          url: this.currentTab.url,
          settings: this.settings,
        },
      };

      // Update progress
      this.updateCaptureStatus(
        'Processing PDF...',
        'Converting and preparing for repository upload',
        'progress',
        { showProgress: true, progressValue: 70 }
      );

      const response = await this.sendMessageToBackground(captureMessage.type, captureMessage.data);

      // Final progress update before showing result
      this.updateCaptureStatus(
        'Saving to Repository...',
        'Uploading PDF to GitHub repository',
        'progress',
        { showProgress: true, progressValue: 90 }
      );

      if (response.success) {
        const responseData = response.data as any;
        this.updateCaptureStatus(
          'PDF Captured Successfully!',
          `PDF saved as: ${responseData?.filename || 'document.pdf'}`,
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
        throw new Error(response.error || 'PDF capture failed');
      }
    } catch (error) {
      logger.error('Error capturing PDF:', error);
      const errorMessage = (error as Error).message;

      this.updateCaptureStatus('PDF Capture Failed', errorMessage, 'error', {
        autoHide: 6000,
        actions: [
          {
            label: 'Try Again',
            action: () => {
              this.resetCaptureStatus();
              setTimeout(() => this.capturePDF(), 100);
            },
            primary: true,
          },
          {
            label: 'Capture Page Content',
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
    const container = this.ensureStatusTemplate();
    if (!container) return;

    // Update container class
    container.className = `pw-card pw-card--static capture-status-container ${type}`;

    // Update icon based on type
    const iconElement = this.document.getElementById('status-icon');
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
    const titleElement = this.document.getElementById('status-title');
    if (titleElement) {
      titleElement.textContent = title;
    }

    // Update message
    const messageElement = this.document.getElementById('status-message');
    if (messageElement) {
      messageElement.textContent = message || '';
      messageElement.style.display = message ? 'block' : 'none';
    }

    // Handle progress bar
    const progressBar = this.document.getElementById('progress-bar');
    const progressFill = progressBar?.querySelector('.progress-fill') as HTMLElement;
    if (options.showProgress && progressBar && progressFill) {
      progressBar.style.display = 'block';
      progressFill.style.width = `${options.progressValue || 0}%`;
    } else if (progressBar) {
      progressBar.style.display = 'none';
    }

    // Handle actions
    const actionsContainer = this.document.getElementById('status-actions');
    if (options.actions && actionsContainer) {
      actionsContainer.innerHTML = '';
      options.actions.forEach(action => {
        const button = this.document.createElement('button');
        button.className = `status-action-btn ${action.primary ? 'primary' : ''}`;
        button.textContent = action.label;

        // Add data attribute to track action type for debugging
        if (action.label.includes('Repository') || action.label.includes('GitHub')) {
          button.setAttribute('data-action-type', 'repository');
        }

        // Wrap action in debounce to prevent multiple rapid clicks
        button.addEventListener('click', e => {
          e.stopPropagation(); // Prevent event bubbling
          e.preventDefault();

          logger.debug(`Action button clicked: ${action.label}`);

          // Disable button temporarily to prevent double clicks
          button.disabled = true;
          setTimeout(() => {
            button.disabled = false;
          }, 1000);

          action.action();
        });

        actionsContainer.appendChild(button);
      });
      actionsContainer.style.display = 'flex';
    } else if (actionsContainer) {
      actionsContainer.style.display = 'none';
    }

    // Handle details
    const detailsContainer = this.document.getElementById('status-details');
    if ((options.showProgress || options.actions) && detailsContainer) {
      detailsContainer.style.display = 'block';
    } else if (detailsContainer) {
      detailsContainer.style.display = 'none';
    }

    // Setup close button
    const closeButton = this.document.getElementById('status-close');
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
    this.cacheStatusTemplate();

    const container = this.document.getElementById('capture-status');
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

    container.className = 'pw-card pw-card--static capture-status-container missing-settings';
    container.style.display = 'block';

    // Setup event handlers
    const openSettingsBtn = this.document.getElementById('open-settings-action');
    const closeBtn = this.document.getElementById('missing-settings-close');

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
    const statusElement = this.document.getElementById('capture-status');
    if (statusElement) {
      this.cacheStatusTemplate();

      if (this.statusTemplateHTML) {
        statusElement.innerHTML = this.statusTemplateHTML;
      } else {
        statusElement.textContent = '';
      }

      statusElement.style.display = 'none';
      statusElement.className = 'pw-card pw-card--static capture-status-container hidden';
    }
    this.lastCapturedContent = null;
  }

  private openSettings(): void {
    this.chrome.runtime.openOptionsPage();
  }

  private openRepository(): void {
    logger.debug('openRepository called');

    // Add call stack logging to debug duplicate calls
    if (console.trace) {
      console.trace('openRepository call stack:');
    }

    // Debounce multiple calls within 500ms
    if (this.openRepositoryDebounceTimer) {
      logger.warn('🚨 openRepository debounced - ignoring duplicate call within 500ms');
      return;
    }

    this.openRepositoryDebounceTimer = setTimeout(() => {
      this.openRepositoryDebounceTimer = null;
    }, 500);

    if (!this.settings?.githubRepo) {
      logger.warn('Cannot open repository: githubRepo not configured');
      this.showError('GitHub repository not configured. Please check your settings.');
      return;
    }

    const url = `https://github.com/${this.settings.githubRepo}`;
    logger.debug('Opening repository URL:', url);

    try {
      this.chrome.tabs.create({ url }, tab => {
        if (this.chrome.runtime.lastError) {
          logger.error('Failed to create tab:', this.chrome.runtime.lastError.message);
          this.showError('Failed to open repository tab');
        } else {
          logger.debug('Successfully created tab:', tab?.id);
        }
      });
    } catch (error) {
      logger.error('Error in chrome.tabs.create:', error);
      this.showError('Failed to open repository');
    }
  }

  private openDocument(documentUrl: string): void {
    logger.debug('openDocument called with URL:', documentUrl);

    if (!documentUrl) {
      logger.warn('Cannot open document: no URL provided');
      this.showError('Document URL not available');
      return;
    }

    logger.debug('Opening document URL:', documentUrl);

    try {
      this.chrome.tabs.create({ url: documentUrl }, tab => {
        if (this.chrome.runtime.lastError) {
          logger.error('Failed to create tab for document:', this.chrome.runtime.lastError.message);
          this.showError('Failed to open document tab');
        } else {
          logger.debug('Successfully created document tab:', tab?.id);
          // Close the popup after successfully opening the document
          window.close();
        }
      });
    } catch (error) {
      logger.error('Error in chrome.tabs.create for document:', error);
      this.showError('Failed to open document');
    }
  }

  private showError(message: string): void {
    const errorElement = this.document.getElementById('error-message');
    if (errorElement) {
      errorElement.textContent = message;
      errorElement.style.display = 'block';
    }
  }

  private async sendMessageToBackground(type: string, data?: any): Promise<IMessageResponse> {
    return new Promise<IMessageResponse>((resolve, reject) => {
      const message: IMessageData = { type, data };

      this.chrome.runtime.sendMessage(message, (response: IMessageResponse) => {
        if (this.chrome.runtime.lastError) {
          reject(new Error(this.chrome.runtime.lastError.message));
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

      this.chrome.tabs.sendMessage(this.currentTab!.id!, message, (response: IMessageResponse) => {
        if (this.chrome.runtime.lastError) {
          reject(new Error(this.chrome.runtime.lastError.message));
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
    const modal = this.document.createElement('div');
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
    this.document.body.appendChild(modal);

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
        this.document.removeEventListener('keydown', handleKeydown);
      }
    };
    this.document.addEventListener('keydown', handleKeydown);
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
let popupInstance: PrismWeavePopup | null = null;

document.addEventListener('DOMContentLoaded', () => {
  if (popupInstance) {
    logger.debug('Popup already initialized, skipping...');
    return;
  }

  logger.debug('Initializing popup...');
  popupInstance = new PrismWeavePopup();
});
