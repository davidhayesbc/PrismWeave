// PrismWeave Content Script
// Runs on web pages to assist with content extraction and user interactions

class PrismWeaveContent {
  constructor() {
    this.isCapturing = false;
    this.contentExtractor = null;
    this.initializeContentScript();
  }

  initializeContentScript() {
    // Listen for messages from background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true;
    });

    // Add keyboard shortcut listener
    document.addEventListener('keydown', event => {
      // Ctrl+Shift+S to capture page
      if (event.ctrlKey && event.shiftKey && event.key === 'S') {
        event.preventDefault();
        this.captureCurrentPage();
      }

      // Ctrl+Shift+H to highlight content
      if (event.ctrlKey && event.shiftKey && event.key === 'H') {
        event.preventDefault();
        this.highlightMainContent();
      }
    });

    // Add visual feedback for capturing
    this.createCaptureIndicator();

    // Load content extractor when needed
    this.loadContentExtractor();
  }

  async loadContentExtractor() {
    if (!window.ContentExtractor) {
      // Content extractor will be injected by background script when needed
      return;
    }
    this.contentExtractor = new ContentExtractor();
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'EXTRACT_CONTENT':
          await this.loadContentExtractor();
          const content = this.extractPageContent();
          sendResponse({ success: true, data: content });
          break;

        case 'HIGHLIGHT_CONTENT':
          await this.loadContentExtractor();
          this.highlightMainContent();
          sendResponse({ success: true });
          break;

        case 'SHOW_CAPTURE_SUCCESS':
          this.showCaptureSuccess(message.filename);
          sendResponse({ success: true });
          break;

        case 'SHOW_CAPTURE_ERROR':
          this.showCaptureError(message.error);
          sendResponse({ success: true });
          break;

        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('Content script error:', error);
      sendResponse({ success: false, error: error.message });
    }
  }

  async captureCurrentPage() {
    if (this.isCapturing) return;

    this.isCapturing = true;
    this.showCaptureIndicator();

    try {
      // Send capture request to background script
      const response = await chrome.runtime.sendMessage({
        action: 'CAPTURE_PAGE',
      });

      if (response.success) {
        this.showCaptureSuccess(response.data.filename);
      } else {
        this.showCaptureError(response.error);
      }
    } catch (error) {
      this.showCaptureError(error.message);
    } finally {
      this.isCapturing = false;
      this.hideCaptureIndicator();
    }
  }
  extractPageContent() {
    if (this.contentExtractor) {
      return this.contentExtractor.extractPageContent(document);
    }

    // Fallback extraction if ContentExtractor not available
    return this.basicExtractPageContent();
  }

  basicExtractPageContent() {
    // Clean up the page before extraction
    this.removeUnwantedElements();

    // Find the main content area
    const mainContent = this.findMainContent();

    // Extract structured data
    const content = {
      title: this.getPageTitle(),
      content: mainContent.innerHTML,
      textContent: mainContent.innerText,
      images: this.extractImages(),
      links: this.extractLinks(),
      metadata: this.extractMetadata(),
      quality: { score: 50 }, // Default quality score
      wordCount: mainContent.innerText.split(/\s+/).length,
      readingTime: Math.ceil(mainContent.innerText.split(/\s+/).length / 200),
    };

    return content;
  }

  removeUnwantedElements() {
    const selectorsToRemove = [
      // Navigation and UI elements
      'nav',
      'header',
      'footer',
      'aside',
      '[role="banner"]',
      '[role="navigation"]',
      '[role="complementary"]',

      // Ads and promotional content
      '.ad',
      '.ads',
      '.advertisement',
      '.promo',
      '.promotion',
      '[class*="ad-"]',
      '[id*="ad-"]',
      '[class*="ads-"]',
      '[id*="ads-"]',

      // Social media and sharing
      '.social',
      '.share',
      '.sharing',
      '.social-media',
      '.twitter',
      '.facebook',
      '.linkedin',
      '.pinterest',

      // Comments and related content
      '.comments',
      '.comment',
      '.related',
      '.sidebar',
      '.widget',
      '.widgets',
      '.recommended',

      // Cookie notices and popups
      '.cookie',
      '.gdpr',
      '.modal',
      '.popup',
      '.overlay',

      // Scripts and styles
      'script',
      'style',
      'noscript',
    ];

    selectorsToRemove.forEach(selector => {
      document.querySelectorAll(selector).forEach(element => {
        element.remove();
      });
    });
  }

  findMainContent() {
    // Try common content selectors in order of preference
    const contentSelectors = [
      'article',
      'main',
      '[role="main"]',
      '.post-content',
      '.entry-content',
      '.article-content',
      '.content',
      '.main-content',
      '.post-body',
      '.entry-body',
      '#content',
      '#main',
    ];

    for (const selector of contentSelectors) {
      const element = document.querySelector(selector);
      if (element && this.hasSignificantContent(element)) {
        return element;
      }
    }

    // Fallback: find the element with the most text content
    const allElements = document.querySelectorAll('div, section, article');
    let bestElement = document.body;
    let maxTextLength = 0;

    allElements.forEach(element => {
      const textLength = element.innerText.length;
      if (textLength > maxTextLength && this.hasSignificantContent(element)) {
        maxTextLength = textLength;
        bestElement = element;
      }
    });

    return bestElement;
  }

  hasSignificantContent(element) {
    const text = element.innerText.trim();
    const words = text.split(/\s+/).length;
    return words > 50; // Require at least 50 words
  }

  getPageTitle() {
    // Try different title sources
    const titleSources = [
      'h1',
      '.title',
      '.post-title',
      '.entry-title',
      '.article-title',
      '[property="og:title"]',
      'title',
    ];

    for (const selector of titleSources) {
      const element = document.querySelector(selector);
      if (element) {
        const title = element.textContent || element.getAttribute('content');
        if (title && title.trim()) {
          return title.trim();
        }
      }
    }

    return document.title;
  }

  extractImages() {
    const images = [];
    const imgElements = document.querySelectorAll('img');

    imgElements.forEach(img => {
      // Skip small images (likely icons or decorative)
      if (img.width < 100 || img.height < 100) return;

      // Skip images with ad-related classes
      if (img.className.match(/ad|advertisement|banner/i)) return;

      images.push({
        src: img.src,
        alt: img.alt || '',
        title: img.title || '',
        width: img.width,
        height: img.height,
      });
    });

    return images;
  }

  extractLinks() {
    const links = [];
    const linkElements = document.querySelectorAll('a[href]');

    linkElements.forEach(link => {
      const href = link.href;
      const text = link.textContent.trim();

      // Skip empty links or javascript: links
      if (!text || href.startsWith('javascript:')) return;

      // Skip navigation and footer links
      if (link.closest('nav, header, footer, .menu, .navigation')) return;

      links.push({
        href: href,
        text: text,
        title: link.title || '',
      });
    });

    return links;
  }

  extractMetadata() {
    const metadata = {};

    // Extract Open Graph metadata
    document.querySelectorAll('meta[property^="og:"]').forEach(meta => {
      const property = meta.getAttribute('property').replace('og:', '');
      metadata[property] = meta.getAttribute('content');
    });

    // Extract Twitter Card metadata
    document.querySelectorAll('meta[name^="twitter:"]').forEach(meta => {
      const name = meta.getAttribute('name').replace('twitter:', '');
      metadata[`twitter_${name}`] = meta.getAttribute('content');
    });

    // Extract other useful metadata
    const metaSelectors = {
      description: 'meta[name="description"]',
      keywords: 'meta[name="keywords"]',
      author: 'meta[name="author"]',
      published: 'meta[name="article:published_time"], meta[property="article:published_time"]',
    };

    Object.entries(metaSelectors).forEach(([key, selector]) => {
      const meta = document.querySelector(selector);
      if (meta) {
        metadata[key] = meta.getAttribute('content');
      }
    });

    return metadata;
  }

  createCaptureIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'prismweave-indicator';
    indicator.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #4CAF50;
      color: white;
      padding: 10px 15px;
      border-radius: 5px;
      font-family: Arial, sans-serif;
      font-size: 14px;
      z-index: 10000;
      display: none;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    `;
    document.body.appendChild(indicator);
  }
  showCaptureIndicator() {
    const indicator = document.getElementById('prismweave-indicator');
    if (indicator) {
      indicator.textContent = 'Capturing page...';
      indicator.style.display = 'block';
      indicator.style.background = '#2196F3';
    }
  }
  hideCaptureIndicator() {
    const indicator = document.getElementById('prismweave-indicator');
    if (indicator) {
      indicator.style.display = 'none';
    }
  }

  showCaptureSuccess(filename) {
    const indicator = document.getElementById('prismweave-indicator');
    if (indicator) {
      indicator.textContent = `✓ Captured: ${filename}`;
      indicator.style.background = '#4CAF50';
      indicator.style.display = 'block';

      setTimeout(() => {
        indicator.style.display = 'none';
      }, 3000);
    }
  }
  showCaptureError(error) {
    const indicator = document.getElementById('prismweave-indicator');
    if (indicator) {
      indicator.textContent = `✗ Error: ${error}`;
      indicator.style.background = '#f44336';
      indicator.style.display = 'block';

      setTimeout(() => {
        indicator.style.display = 'none';
      }, 5000);
    }
  }
  highlightMainContent() {
    if (this.contentExtractor) {
      this.contentExtractor.highlightMainContent();
      return;
    }

    // Fallback highlighting
    const mainContent = this.findMainContent();
    if (mainContent) {
      mainContent.style.outline = '3px solid #4CAF50';
      mainContent.style.outlineOffset = '2px';

      setTimeout(() => {
        mainContent.style.outline = '';
        mainContent.style.outlineOffset = '';
      }, 2000);
    }
  }
}

// Export for tests
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PrismWeaveContent;
} else {
  // Initialize content script in browser context
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      new PrismWeaveContent();
    });
  } else {
    new PrismWeaveContent();
  }
}
