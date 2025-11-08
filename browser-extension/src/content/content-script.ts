/**
 * @fileoverview PrismWeave Content Script
 *
 * Responsibilities:
 * - Keyboard shortcut handling for page capture (Alt+S by default)
 * - Content extraction with heuristics & fallbacks
 * - PDF detection and specialized capture path
 * - Delegated messaging with background/service worker
 * - Unified toast notifications (via shared `showToast` utility)
 * - Graceful degradation when extension context invalidated
 */
import {
  IContentExtractionData,
  IContentExtractionResult,
  IMessageData,
  IMessageResponse,
  MESSAGE_TYPES,
} from '../types/types';
import { ContentExtractor, IImageInfo } from '../utils/content-extractor';
import { createLogger } from '../utils/logger';
import { MarkdownConverter } from '../utils/markdown-converter';
import { configureNotificationContext, notification, notify } from '../utils/notifications/notify';

// NOTE: We use the unified notification API that automatically selects the best implementation
// based on execution environment (popup status UI → toast → Chrome notifications → console)
// -----------------------------------------------------------------------------
// Type & Interface Definitions (restored after refactor)
// -----------------------------------------------------------------------------

interface IEnhancedMessageResponse extends IMessageResponse {
  commitUrl?: string;
  url?: string;
  saveResult?: { url?: string; commitUrl?: string; [k: string]: unknown };
  warnings?: string[];
}

interface IContentScriptState {
  isInitialized: boolean;
  keyboardShortcutsEnabled: boolean;
  isCapturing: boolean;
}

interface IKeyboardShortcut {
  ctrlKey: boolean;
  shiftKey: boolean;
  altKey: boolean;
  metaKey: boolean;
  key: string;
  action: string;
}

// State
let contentScriptState: IContentScriptState = {
  isInitialized: false,
  keyboardShortcutsEnabled: true,
  isCapturing: false,
};

// Logger
const logger = createLogger('ContentScript');

// Keyboard shortcuts (Alt+S for capture)
const KEYBOARD_SHORTCUTS: IKeyboardShortcut[] = [
  {
    ctrlKey: false,
    shiftKey: false,
    altKey: true,
    metaKey: false,
    key: 'S',
    action: 'capture-page',
  },
];
// =============================================================================
// INITIALIZATION FUNCTIONS
// =============================================================================

/**
 * Initialize the content script
 * Sets up keyboard listeners, message handlers, and loads settings
 */
async function initializeContentScript(): Promise<void> {
  try {
    logger.info('Initializing PrismWeave content script...');

    // Configure notification context for content script environment
    configureNotificationContext({
      isContentScript: true,
      isPopup: false,
      isServiceWorker: false,
    });

    // Load settings to check if keyboard shortcuts are enabled
    await loadKeyboardShortcutSettings();

    // Set up keyboard event listeners
    setupKeyboardListeners();

    // Set up message listeners for communication with service worker
    setupMessageListeners();

    contentScriptState.isInitialized = true;
    logger.info('PrismWeave content script initialized successfully');
  } catch (error) {
    logger.error('Failed to initialize content script:', error);
  }
}

/**
 * Load keyboard shortcut settings from storage
 * Retrieves user preferences for keyboard shortcut behavior
 */
async function loadKeyboardShortcutSettings(): Promise<void> {
  try {
    const response = await sendMessageToBackground(MESSAGE_TYPES.GET_SETTINGS);
    if (response.success && response.data) {
      const settings = response.data as any;
      contentScriptState.keyboardShortcutsEnabled = settings.enableKeyboardShortcuts ?? true;
      logger.info('Keyboard shortcuts enabled:', contentScriptState.keyboardShortcutsEnabled);
    }
  } catch (error) {
    logger.warn('Failed to load settings, using defaults:', error);
    contentScriptState.keyboardShortcutsEnabled = true;
  }
}

// =============================================================================
// KEYBOARD SHORTCUT HANDLING
// =============================================================================

/**
 * Set up keyboard event listeners
 * Attaches global keyboard event handler to document
 */
function setupKeyboardListeners(): void {
  document.addEventListener('keydown', handleKeyboardEvent, true);
  logger.info('Keyboard event listeners set up');
}

/**
 * Handle keyboard events
 * Processes keyboard shortcuts and triggers appropriate actions
 * @param event - The keyboard event
 */
function handleKeyboardEvent(event: KeyboardEvent): void {
  // Skip if shortcuts are disabled
  if (!contentScriptState.keyboardShortcutsEnabled) {
    return;
  }

  // Skip if already capturing to prevent multiple simultaneous captures
  if (contentScriptState.isCapturing) {
    return;
  }

  // Skip if user is typing in an input field
  if (isTypingInInputField(event.target as Element)) {
    return;
  }

  // Check if the event matches any of our shortcuts
  for (const shortcut of KEYBOARD_SHORTCUTS) {
    if (matchesShortcut(event, shortcut)) {
      // Only log when a shortcut is actually triggered
      logger.info('Keyboard shortcut matched:', {
        key: event.key,
        ctrlKey: event.ctrlKey,
        altKey: event.altKey,
        shiftKey: event.shiftKey,
        action: shortcut.action,
      });

      event.preventDefault();
      event.stopPropagation();
      handleShortcutAction(shortcut.action);
      break;
    }
  }
}

/**
 * Check if user is typing in an input field
 * Prevents shortcuts from triggering when user is actively typing
 * @param target - The event target element
 * @returns True if user is typing in an input field
 */
function isTypingInInputField(target: Element | null): boolean {
  if (!target) return false;

  const tagName = target.tagName.toLowerCase();
  const inputTypes = ['input', 'textarea', 'select'];

  // Check if it's an input element
  if (inputTypes.includes(tagName)) {
    return true;
  }

  // Check if it's a contentEditable element
  const element = target as HTMLElement;
  if (element.contentEditable === 'true') {
    return true;
  }

  // Check if we're inside a contentEditable element
  let parent = target.parentElement;
  while (parent) {
    if (parent.contentEditable === 'true') {
      return true;
    }
    parent = parent.parentElement;
  }

  return false;
}

/**
 * Check if keyboard event matches a shortcut
 * Compares event properties with shortcut configuration
 * @param event - The keyboard event
 * @param shortcut - The shortcut configuration
 * @returns True if the event matches the shortcut
 */
function matchesShortcut(event: KeyboardEvent, shortcut: IKeyboardShortcut): boolean {
  // Normalize key comparison
  const eventKey = event.key.toUpperCase();
  const shortcutKey = shortcut.key.toUpperCase();

  return (
    event.ctrlKey === shortcut.ctrlKey &&
    event.shiftKey === shortcut.shiftKey &&
    event.altKey === shortcut.altKey &&
    event.metaKey === shortcut.metaKey &&
    eventKey === shortcutKey
  );
}

/**
 * Handle shortcut actions
 * Routes shortcut actions to appropriate handler functions
 * @param action - The action to perform
 */
async function handleShortcutAction(action: string): Promise<void> {
  logger.info('Handling shortcut action:', action);

  try {
    switch (action) {
      case 'capture-page':
        await handleCapturePageShortcut();
        break;
      default:
        logger.warn('Unknown shortcut action:', action);
    }
  } catch (error) {
    logger.error('Error handling shortcut action:', error);
    notification.error('Failed to execute shortcut: ' + (error as Error).message);
  }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Enhanced commit URL extraction function
 * Attempts to extract commit URL from various response formats
 * @param response - The response object from background script
 * @returns The commit URL if found, undefined otherwise
 */
function extractCommitUrlFromResponse(response: IEnhancedMessageResponse): string | undefined {
  // Try all possible locations for the commit URL
  const possibleUrls = [
    response.commitUrl,
    (response.data as any)?.commitUrl,
    (response.data as any)?.url,
    response.saveResult?.commitUrl,
    response.saveResult?.url,
    (response.data as any)?.saveResult?.commitUrl,
    (response.data as any)?.saveResult?.url,
    (response.data as any)?.githubResult?.url,
    (response.data as any)?.githubResult?.html_url,
    (response.data as any)?.content?.html_url,
    response.url,
  ];

  // Find the first valid URL
  for (const url of possibleUrls) {
    if (url && typeof url === 'string' && url.startsWith('http')) {
      return url;
    }
  }

  // If no URL found, log minimal warning
  logger.warn('No commit URL found in response');
  return undefined;
}

// Handle capture page shortcut
async function handleCapturePageShortcut(): Promise<void> {
  logger.info('Keyboard shortcut triggered - starting capture process');

  if (contentScriptState.isCapturing) {
    logger.warn('Page capture already in progress');
    return;
  }

  try {
    contentScriptState.isCapturing = true;

    // Show "capturing" notification that stays until capture completes (no auto-hide)
    notification.info('Capturing content...', { duration: 0 }); // 0 duration = no auto-hide

    // Check if current page is a PDF
    const isPDFPage = checkIfCurrentPageIsPDF();
    logger.debug('PDF detection result:', isPDFPage);

    if (isPDFPage) {
      logger.info('PDF page detected - using unified capture service via background');

      // For PDF pages, send capture request directly to background service
      const messageData = {
        url: window.location.href,
        title: document.title,
        contentType: 'pdf',
      };

      const response = await sendMessageToBackground(MESSAGE_TYPES.CAPTURE_CONTENT, messageData);

      if (response.success) {
        // Enhanced commit URL extraction with comprehensive fallback
        const commitUrl = extractCommitUrlFromResponse(response);

        if (commitUrl) {
          // Show success notification with GitHub link
          notification.success('PDF captured successfully! Click to view on GitHub.', {
            duration: 8000,
            clickUrl: commitUrl,
          });
          logger.info('PDF capture completed successfully via keyboard shortcut', {
            commitUrl,
            hasCommitUrl: true,
          });
        } else {
          // Show success notification without GitHub link
          notification.success('PDF captured successfully!', { duration: 8000 });
          logger.warn('PDF capture completed but no commit URL found');
        }
      } else {
        throw new Error(response.error || 'PDF capture failed');
      }
    } else {
      logger.info('HTML page detected - extracting content locally then sending to background');

      // Extract content first for HTML pages
      const extractedContent = await extractPageContentWithUtilities();
      logger.info('Content extracted successfully for keyboard shortcut', {
        hasMarkdown: !!extractedContent.markdown,
        markdownLength: extractedContent.markdown?.length || 0,
        hasHtml: !!extractedContent.html,
        htmlLength: extractedContent.html?.length || 0,
        hasTitle: !!extractedContent.title,
        title: extractedContent.title || 'no title',
      });

      // Send capture request with extracted content to service worker
      const messageData = {
        url: window.location.href,
        title: document.title,
        extractedContent,
        contentType: 'html',
      };

      const response = await sendMessageToBackground(MESSAGE_TYPES.CAPTURE_CONTENT, messageData);

      if (response.success) {
        // Enhanced commit URL extraction with comprehensive fallback
        const commitUrl = extractCommitUrlFromResponse(response);

        if (commitUrl) {
          // Show success notification with GitHub link
          notification.success('Page captured successfully! Click to view on GitHub.', {
            duration: 8000,
            clickUrl: commitUrl,
          });
          logger.info('Page capture completed successfully via keyboard shortcut', {
            commitUrl,
            hasCommitUrl: true,
          });
        } else {
          // Show success notification without GitHub link
          notification.success('Page captured successfully!', { duration: 8000 });
          logger.warn('Page capture completed but no commit URL found');
        }
      } else {
        throw new Error(response.error || 'Page capture failed');
      }
    }
  } catch (error) {
    logger.error('Keyboard shortcut capture failed:', error);
    // Hide the "capturing" notification and show error
    notification.error('Capture failed: ' + (error as Error).message, { duration: 8000 });
  } finally {
    contentScriptState.isCapturing = false;
  }
}

/**
 * Check if current page is a PDF document
 * Uses multiple detection methods: URL patterns, DOM elements, and content type
 * @returns true if the page is detected as a PDF, false otherwise
 */
function checkIfCurrentPageIsPDF(): boolean {
  const url = window.location.href;

  // Check if URL ends with .pdf
  if (url.toLowerCase().endsWith('.pdf')) {
    return true;
  }

  // Check if URL contains PDF indicators
  if (url.toLowerCase().includes('.pdf')) {
    return true;
  }

  // Check for common PDF viewer URL patterns
  const pdfPatterns = [
    /\/pdf\//i,
    /\.pdf$/i,
    /\.pdf\?/i,
    /\.pdf#/i,
    /application\/pdf/i,
    /chrome-extension:\/\/.*\/web\/viewer\.html/i, // Chrome PDF viewer
  ];

  const isPDFByPattern = pdfPatterns.some(pattern => pattern.test(url));

  if (isPDFByPattern) {
    return true;
  }

  // Check document MIME type if available
  try {
    if (document.contentType && document.contentType.includes('pdf')) {
      return true;
    }
  } catch (error) {
    // Ignore contentType access errors
  }

  // Check for PDF viewer indicators in the DOM
  const pdfViewerSelectors = [
    'embed[type="application/pdf"]',
    'object[type="application/pdf"]',
    '#viewer', // Common PDF viewer element
    '.pdfViewer', // Common PDF viewer class
    '[data-pdf-viewer]', // PDF viewer data attribute
  ];

  const hasPDFViewerElements = pdfViewerSelectors.some(selector => {
    try {
      return document.querySelector(selector) !== null;
    } catch (error) {
      return false;
    }
  });

  logger.info('PDF detection result:', {
    url,
    isPDFByPattern,
    hasPDFViewerElements,
    documentContentType: document.contentType || 'unknown',
    finalResult: hasPDFViewerElements,
  });

  return hasPDFViewerElements;
}

// =============================================================================
// MESSAGE HANDLING
// =============================================================================

/**
 * Set up message listeners for communication with service worker
 * Attaches Chrome runtime message listener
 */
function setupMessageListeners(): void {
  chrome.runtime.onMessage.addListener(
    (
      message: IMessageData,
      sender: chrome.runtime.MessageSender,
      sendResponse: (response: IMessageResponse) => void
    ) => {
      handleMessage(message, sender)
        .then(result => sendResponse({ success: true, data: result }))
        .catch(error => {
          logger.error('Content script message error:', error);
          sendResponse({ success: false, error: error.message });
        });

      return true; // Keep message channel open for async response
    }
  );
}

/**
 * Handle messages from service worker
 * Routes messages to appropriate handler functions
 * @param message - The message data
 * @param sender - The message sender
 * @returns Promise resolving to message response
 */
async function handleMessage(
  message: IMessageData,
  sender: chrome.runtime.MessageSender
): Promise<unknown> {
  switch (message.type) {
    case 'PING':
      return { status: 'ready', timestamp: Date.now() };

    case 'TRIGGER_CAPTURE_SHORTCUT':
      // Triggered by keyboard shortcut from service worker
      logger.info('Capture triggered by keyboard shortcut via service worker');
      handleShortcutAction('capture-page').catch(error => {
        logger.error('Error handling shortcut capture:', error);
      });
      return { success: true };

    case 'TRIGGER_CAPTURE_CONTEXT_MENU':
      // Triggered by context menu from service worker
      logger.info('Capture triggered by context menu via service worker');
      handleShortcutAction('capture-page').catch(error => {
        logger.error('Error handling context menu capture:', error);
      });
      return { success: true };

    case 'UPDATE_KEYBOARD_SHORTCUTS':
      if (message.data && typeof message.data.enabled === 'boolean') {
        contentScriptState.keyboardShortcutsEnabled = message.data.enabled;
        logger.info('Keyboard shortcuts updated:', contentScriptState.keyboardShortcutsEnabled);
      }
      return { success: true };

    case 'GET_PAGE_INFO':
      return {
        title: document.title,
        url: window.location.href,
        domain: window.location.hostname,
      };

    case 'SHOW_NOTIFICATION':
      if (message.data && typeof message.data.message === 'string') {
        const notificationType = (message.data.type as 'success' | 'error' | 'info') || 'info';
        const duration = (message.data.duration as number) || 8000; // Increased default duration
        const clickUrl = (message.data.clickUrl || message.data.url) as string | undefined;

        const options: any = { duration };
        if (clickUrl) options.clickUrl = clickUrl;

        notify(message.data.message, { type: notificationType, ...options });
        logger.info('Notification shown:', message.data.message);
      }
      return { success: true };

    case 'EXTRACT_AND_CONVERT_TO_MARKDOWN':
      // This is called by the service worker for content extraction
      try {
        const extractedContent = await extractPageContentWithUtilities(message.data);
        return {
          success: true,
          data: extractedContent,
          extractionMethod: 'content-script',
          timestamp: new Date().toISOString(),
        } as IContentExtractionResult;
      } catch (error) {
        logger.error('Content extraction failed:', error);
        return {
          success: false,
          error: (error as Error).message,
          extractionMethod: 'content-script',
          timestamp: new Date().toISOString(),
        } as IContentExtractionResult;
      }

    default:
      throw new Error(`Unknown message type: ${message.type}`);
  }
}

// Extract page content using existing utilities
async function extractPageContentWithUtilities(options?: any): Promise<IContentExtractionData> {
  try {
    logger.info('Extracting page content using ContentExtractor...');

    // Initialize utilities with error handling for extension context invalidation
    let contentExtractor: ContentExtractor;
    let markdownConverter: MarkdownConverter;

    try {
      contentExtractor = new ContentExtractor();
      markdownConverter = new MarkdownConverter();
    } catch (error) {
      // If utilities fail to initialize (e.g., extension context invalidated or other issues),
      // fall back to basic content extraction
      logger.warn('Utility initialization failed, falling back to basic extraction:', error);
      notification.info('Using basic capture mode', { duration: 3000 });
      return await basicContentExtraction();
    }

    // Extract content using the existing utility
    const extractorOptions = {
      customSelectors: options?.customSelectors,
      cleanHtml: options?.cleanHtml !== false,
      preserveFormatting: options?.preserveFormatting === true,
      waitForDynamicContent: options?.waitForDynamicContent !== false,
      // Enhanced cleaning for blog sites and promotional content
      removeAds: true,
      removeNavigation: true,
      excludeSelectors: [
        // Blog-specific elements to exclude
        '.s-navigation',
        '.s-topbar',
        '.js-header',
        '.js-footer',
        '.recent-articles',
        '.latest-podcast',
        '.add-to-discussion',
        '.blog-sidebar',
        '.blog-nav',
        '.site-header',
        '.site-footer',
        '.products-nav',
        // Generic promotional content
        '[href*="/teams/"]',
        '[href*="/advertising/"]',
        '[href*="/talent/"]',
        '.promo',
        '.newsletter',
        '.subscribe',
        '.signup',
        '.cta',
        '.call-to-action',
        // Our own notification elements
        '#prismweave-notification',
        '[id*="prismweave"]',
        '[class*="prismweave"]',
      ],
    };

    let contentResult;
    try {
      contentResult = await contentExtractor.extractContent(extractorOptions);
    } catch (extractError) {
      logger.warn('Content extractor failed, falling back to basic extraction:', extractError);
      return await basicContentExtraction();
    }

    // Convert to markdown with enhanced cleaning
    let markdownResult;
    try {
      markdownResult = markdownConverter.convertToMarkdown(contentResult.content, {
        preserveFormatting: options?.preserveFormatting === true,
        includeMetadata: true,
        generateFrontmatter: true,
      });
    } catch (markdownError) {
      logger.warn('Markdown conversion failed, falling back to basic extraction:', markdownError);
      return await basicContentExtraction();
    }

    // Post-process markdown to remove any remaining unwanted content
    let cleanedMarkdown = markdownResult.markdown;

    // Remove our own "Capturing page..." text and similar notifications
    cleanedMarkdown = cleanedMarkdown.replace(/Capturing page\.\.\./gi, '');
    cleanedMarkdown = cleanedMarkdown.replace(/PrismWeave[^.\n]*\./gi, '');

    // Remove promotional content patterns from various blog platforms
    const removePatterns = [
      /Products\s*\n+\s*\*\*Stack Overflow for Teams\*\*[^]*?technologists\./gi,
      /\[Blog\]\(\/\)/gi,
      /\[\]\(https:\/\/stackoverflow\.com\)/gi,
      /\[.*?\]\(\/feed\)/gi,
      /Recent articles\s*\n+.*?\d{4}/gims,
      /Latest Podcast\s*\n+.*?\d{4}/gims,
      /Add to the discussion\s*\n+.*?take part in the discussion\./gims,
      /Login with your.*?account to take part/gi,
    ];

    removePatterns.forEach(pattern => {
      cleanedMarkdown = cleanedMarkdown.replace(pattern, '');
    });

    // Clean up excessive whitespace
    cleanedMarkdown = cleanedMarkdown.replace(/\n{3,}/g, '\n\n').trim();

    // Extract images using the utility
    const images = contentExtractor.extractImages();
    const imageUrls = images.map((img: IImageInfo) => img.src);

    // Get page structure for additional metadata
    const pageStructure = contentExtractor.getPageStructure();

    // Prepare the result data
    const extractionData: IContentExtractionData = {
      html: contentResult.content,
      title: contentResult.metadata.title,
      url: window.location.href,
      metadata: {
        ...contentResult.metadata,
        extractedAt: new Date().toISOString(),
        domain: window.location.hostname,
        wordCount: contentResult.wordCount,
        readingTime: contentResult.readingTime,
        headings: pageStructure.headings,
        sections: pageStructure.sections,
        paragraphs: pageStructure.paragraphs,
        qualityScore: contentExtractor.getContentQualityScore(),
        isPaywallPresent: contentExtractor.isPaywallPresent(),
      },
      markdown: cleanedMarkdown,
      frontmatter: markdownResult.frontmatter,
      images: imageUrls,
    };

    logger.info('Content extraction completed successfully using utilities', {
      wordCount: contentResult.wordCount,
      imageCount: imageUrls.length,
      markdownLength: cleanedMarkdown.length,
    });

    return extractionData;
  } catch (error) {
    logger.error('Page content extraction failed with utilities:', error);

    // If the main extraction failed, try basic fallback
    if (error instanceof Error && error.message.includes('Extension context invalidated')) {
      logger.warn('Falling back to basic content extraction due to extension context invalidation');
      notification.info('Extension reloaded - using basic capture mode', { duration: 3000 });
      return await basicContentExtraction();
    }

    throw error;
  }
}

// Basic content extraction fallback for when extension context is invalidated
async function basicContentExtraction(): Promise<IContentExtractionData> {
  try {
    // Basic content selectors
    const contentSelectors = [
      'article',
      'main',
      '[role="main"]',
      '.content',
      '.post',
      '.entry',
      '#content',
    ];

    let contentElement: Element | null = null;

    // Try to find main content element
    for (const selector of contentSelectors) {
      contentElement = document.querySelector(selector);
      if (
        contentElement &&
        contentElement.textContent &&
        contentElement.textContent.trim().length > 100
      ) {
        break;
      }
    }

    // Fall back to body if no content area found
    if (!contentElement || !contentElement.textContent?.trim()) {
      contentElement = document.body;
    }

    const html = contentElement?.innerHTML || document.body.innerHTML || '';
    const textContent = contentElement?.textContent || document.body.textContent || '';
    const title = document.title || 'Untitled Page';

    // Ensure we have some content
    if (!html.trim() && !textContent.trim()) {
      throw new Error('No content found on page - completely empty document');
    }

    // Basic word count
    const wordCount = textContent.split(/\s+/).filter(word => word.length > 0).length;

    // Ensure minimum content
    if (wordCount < 10) {
      logger.warn('Very little content found on page, but proceeding with basic extraction');
    }

    // Basic image extraction
    const images = Array.from(document.images)
      .map(img => img.src)
      .filter(src => src && !src.startsWith('data:'));

    // Simple markdown conversion (very basic) - ensure we have some content
    let markdown = textContent.trim();
    if (title && title !== 'Untitled Page') {
      markdown = `# ${title}\n\n${textContent.trim()}`;
    } else if (markdown) {
      markdown = `# Untitled Page\n\n${markdown}`;
    } else {
      markdown = '# Untitled Page\n\nNo readable content found on this page.';
    }

    // Ensure frontmatter is valid
    const frontmatter = `---
title: "${title.replace(/"/g, '\\"')}"
url: "${window.location.href}"
captured: "${new Date().toISOString()}"
extraction_method: "basic-fallback"
word_count: ${wordCount}
---
`;

    const extractionData: IContentExtractionData = {
      html: html.trim(),
      title,
      url: window.location.href,
      metadata: {
        extractedAt: new Date().toISOString(),
        domain: window.location.hostname,
        wordCount,
        readingTime: Math.ceil(wordCount / 200),
        extractionMethod: 'basic-fallback',
      },
      markdown: markdown,
      frontmatter: frontmatter,
      images,
    };

    logger.info('Basic content extraction completed:', {
      hasHtml: !!extractionData.html,
      htmlLength: extractionData.html?.length || 0,
      hasMarkdown: !!extractionData.markdown,
      markdownLength: extractionData.markdown?.length || 0,
      wordCount,
      imageCount: images.length,
    });

    return extractionData;
  } catch (error) {
    throw new Error(
      `Basic content extraction failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Send message to background script
 * Wrapper function for Chrome runtime messaging with error handling
 * @param type - The message type identifier
 * @param data - Optional data payload to send
 * @returns Promise resolving to the background script response
 */
function sendMessageToBackground(type: string, data?: any): Promise<IEnhancedMessageResponse> {
  return new Promise<IEnhancedMessageResponse>((resolve, reject) => {
    const message: IMessageData = { type, data, timestamp: Date.now() };

    chrome.runtime.sendMessage(message, (response: IEnhancedMessageResponse) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
      } else if (!response) {
        reject(new Error('No response received from background script'));
      } else {
        resolve(response);
      }
    });
  });
}

// =============================================================================
// INITIALIZATION AND EXPORTS
// =============================================================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeContentScript);
} else {
  initializeContentScript();
}

// Export for debugging (optional) - Make available immediately
if (typeof window !== 'undefined') {
  (window as any).prismweaveContentScript = {
    state: contentScriptState,
    handleCapturePageShortcut,
    loadKeyboardShortcutSettings,
    testNotification: () => {
      // Test function to debug notification clicks
      notification.success('Test notification - Click me!', {
        duration: 10000,
        clickUrl: 'https://github.com/davidhayesbc/PrismWeaveDocs',
      });
    },
    version: '1.0.0',
  };

  // Dispatch a custom event to notify the page that the extension is ready
  const readyEvent = new CustomEvent('prismweave-ready', {
    detail: { version: '1.0.0' },
  });
  document.dispatchEvent(readyEvent);

  console.log('PrismWeave content script API exposed to window');
}

console.log('PrismWeave content script loaded successfully');
