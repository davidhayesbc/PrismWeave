// PrismWeave Content Extractor
// Enhanced content extraction and cleaning utilities

// Import shared utilities if available
let SharedUtils;
try {
  if (typeof require !== 'undefined') {
    SharedUtils = require('./shared-utils.js');
  } else if (typeof window !== 'undefined' && window.SharedUtils) {
    SharedUtils = window.SharedUtils;
  }
} catch (e) {
  // Fallback if shared utils not available
  SharedUtils = null;
}

class ContentExtractor {
  constructor() {
    this.readabilitySelectors = [
      'article',
      'main',
      '[role="main"]',
      '.content',
      '.post-content',
      '.entry-content',
      '.article-content',
      '.article-body',
      '.post-body',
      '.entry-body',
      '.content-body',
      '.main-content',
      '.article-text',
      '.story-body',
      '.article-wrapper'
    ];

    this.unwantedSelectors = [
      'script',
      'style',
      'nav',
      'header',
      'footer',
      'aside',
      '.navigation',
      '.nav',
      '.menu',
      '.sidebar',
      '.ad',
      '.advertisement',
      '.ads',
      '.sponsored',
      '.promo',
      '.banner',
      '.social-share',
      '.social-buttons',
      '.share-buttons',
      '.comments',
      '.comment-section',
      '.newsletter',
      '.subscription',
      '.popup',
      '.modal',
      '.overlay',
      '.cookie-notice',
      '.related-articles',
      '.recommendations',
      '.trending',
      '.most-popular',
      '[class*="ad-"]',
      '[id*="ad-"]',
      '[class*="social"]',
      '[class*="share"]',
      '[role="banner"]',
      '[role="navigation"]',
      '[role="complementary"]'
    ];
  }

  extractPageContent(document) {
    try {
      // Create a clean copy of the document
      const cleanDocument = this.createCleanDocument(document);
      
      // Find the main content
      const mainContent = this.findMainContent(cleanDocument);
      
      // Extract metadata
      const metadata = this.extractMetadata(document);
      
      // Extract images
      const images = this.extractImages(mainContent);
      
      // Extract links
      const links = this.extractLinks(mainContent);
      
      // Calculate content quality metrics
      const quality = this.assessContentQuality(mainContent);
      
      return {
        title: document.title,
        content: mainContent.innerHTML,
        textContent: mainContent.innerText,
        metadata,
        images,
        links,
        quality,
        wordCount: this.countWords(mainContent.innerText),
        readingTime: this.estimateReadingTime(mainContent.innerText)
      };
    } catch (error) {
      console.error('Content extraction failed:', error);
      throw error;
    }
  }

  createCleanDocument(document) {
    // Clone the document body to avoid modifying the original
    const cleanBody = document.body.cloneNode(true);
    
    // Remove unwanted elements
    this.unwantedSelectors.forEach(selector => {
      cleanBody.querySelectorAll(selector).forEach(el => el.remove());
    });
    
    // Clean up attributes
    cleanBody.querySelectorAll('*').forEach(el => {
      // Remove style attributes that might interfere
      el.removeAttribute('style');
      
      // Remove event handlers
      Array.from(el.attributes).forEach(attr => {
        if (attr.name.startsWith('on')) {
          el.removeAttribute(attr.name);
        }
      });
    });
    
    return cleanBody;
  }

  findMainContent(cleanDocument) {
    // Try readability selectors first
    for (const selector of this.readabilitySelectors) {
      const element = cleanDocument.querySelector(selector);
      if (element && this.hasSignificantContent(element)) {
        return element;
      }
    }
    
    // Fallback: find the element with the most text content
    let bestElement = cleanDocument;
    let maxTextLength = 0;
    
    const candidates = cleanDocument.querySelectorAll('div, section, article');
    
    candidates.forEach(element => {
      const textLength = element.innerText.length;
      const childElements = element.children.length;
      
      // Score based on text length and structure
      const score = textLength + (childElements * 10);
      
      if (score > maxTextLength && this.hasSignificantContent(element)) {
        maxTextLength = score;
        bestElement = element;
      }
    });
    
    return bestElement;
  }

  hasSignificantContent(element) {
    const text = element.innerText.trim();
    const wordCount = text.split(/\s+/).length;
    
    // Must have at least 50 words and some structural elements
    return wordCount >= 50 && element.children.length > 0;
  }

  extractMetadata(document) {
    const metadata = {};
    
    // Open Graph metadata
    const ogTags = document.querySelectorAll('meta[property^="og:"]');
    ogTags.forEach(tag => {
      const property = tag.getAttribute('property').replace('og:', '');
      metadata[property] = tag.getAttribute('content');
    });
    
    // Twitter Card metadata
    const twitterTags = document.querySelectorAll('meta[name^="twitter:"]');
    twitterTags.forEach(tag => {
      const name = tag.getAttribute('name').replace('twitter:', '');
      metadata[`twitter_${name}`] = tag.getAttribute('content');
    });
    
    // Standard meta tags
    const metaTags = {
      'description': 'meta[name="description"]',
      'keywords': 'meta[name="keywords"]',
      'author': 'meta[name="author"]',
      'published_time': 'meta[property="article:published_time"]',
      'modified_time': 'meta[property="article:modified_time"]',
      'section': 'meta[property="article:section"]',
      'tags': 'meta[property="article:tag"]'
    };
    
    Object.entries(metaTags).forEach(([key, selector]) => {
      const element = document.querySelector(selector);
      if (element) {
        metadata[key] = element.getAttribute('content');
      }
    });
    
    // Extract canonical URL
    const canonical = document.querySelector('link[rel="canonical"]');
    if (canonical) {
      metadata.canonical_url = canonical.getAttribute('href');
    }
    
    // Extract language
    metadata.language = document.documentElement.lang || 'en';
    
    return metadata;
  }

  extractImages(contentElement) {
    const images = [];
    const imageElements = contentElement.querySelectorAll('img');
    
    imageElements.forEach(img => {
      const src = img.src;
      const alt = img.alt || '';
      const title = img.title || '';
        if (src && !src.startsWith('data:') && this.isValidImageUrl(src)) {
        images.push({
          src: this.resolveUrl(src),
          alt,
          title,
          width: img.naturalWidth || img.width,
          height: img.naturalHeight || img.height
        });
      }
    });
    
    return images;
  }

  extractLinks(contentElement) {
    const links = [];
    const linkElements = contentElement.querySelectorAll('a[href]');
    
    linkElements.forEach(link => {
      const href = link.href;
      const text = link.textContent.trim();
      
      if (href && text && this.isValidUrl(href)) {
        links.push({
          href: this.resolveUrl(href),
          text,
          title: link.title || ''
        });
      }
    });
    
    return links;
  }
  assessContentQuality(contentElement) {
    const text = contentElement.innerText;
    const wordCount = this.countWords(text);
    const paragraphs = contentElement.querySelectorAll('p').length;
    const headings = contentElement.querySelectorAll('h1, h2, h3, h4, h5, h6').length;
    const images = contentElement.querySelectorAll('img').length;
    const links = contentElement.querySelectorAll('a').length;
    
    // Use SharedUtils for score calculation if available
    let score = SharedUtils?.calculateReadabilityScore(text, paragraphs, headings) || 0;
    
    // Add additional scoring for media and links
    if (images >= 1) score += 10;
    if (links >= 2) score += 10;
    
    const avgWordsPerParagraph = paragraphs > 0 ? wordCount / paragraphs : 0;
    
    return {
      score: Math.min(score, 100),
      wordCount,
      paragraphs,
      headings,
      images,
      links,
      avgWordsPerParagraph: Math.round(avgWordsPerParagraph)
    };
  }

  countWords(text) {
    return SharedUtils?.countWords(text) || this._fallbackCountWords(text);
  }

  _fallbackCountWords(text) {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  }

  estimateReadingTime(text) {
    const wordCount = this.countWords(text);
    const wordsPerMinute = 200; // Average reading speed
    return Math.ceil(wordCount / wordsPerMinute);
  }

  // Method for highlighting content on the page
  highlightMainContent() {
    const mainContent = this.findMainContent(document.body);
    
    if (mainContent) {
      // Add highlight overlay
      const overlay = document.createElement('div');
      overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999998;
        pointer-events: none;
      `;
      
      // Highlight the main content
      const rect = mainContent.getBoundingClientRect();
      const highlight = document.createElement('div');
      highlight.style.cssText = `
        position: fixed;
        top: ${rect.top + window.scrollY}px;
        left: ${rect.left + window.scrollX}px;
        width: ${rect.width}px;
        height: ${rect.height}px;
        border: 3px solid #2196F3;
        background: rgba(33, 150, 243, 0.1);
        z-index: 999999;
        pointer-events: none;
        box-sizing: border-box;
      `;
      
      document.body.appendChild(overlay);
      document.body.appendChild(highlight);
      
      // Remove highlight after 3 seconds
      setTimeout(() => {
        if (overlay.parentNode) overlay.remove();
        if (highlight.parentNode) highlight.remove();
      }, 3000);
    }
  }

  isValidImageUrl(url) {
    return SharedUtils?.isValidImageUrl(url) || this._fallbackIsValidImageUrl(url);
  }

  _fallbackIsValidImageUrl(url) {
    const imageExtensions = /\.(jpg|jpeg|png|gif|svg|webp|bmp)(\?.*)?$/i;
    return imageExtensions.test(url) || url.includes('image') || url.includes('img');
  }

  isValidUrl(url) {
    return SharedUtils?.isValidUrl(url) || this._fallbackIsValidUrl(url);
  }

  _fallbackIsValidUrl(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  resolveUrl(url) {
    return SharedUtils?.resolveUrl(url) || this._fallbackResolveUrl(url);
  }

  _fallbackResolveUrl(url) {
    try {
      return new URL(url, window.location.href).href;
    } catch {
      return url;
    }
  }
}

// For use in content script context
if (typeof window !== 'undefined') {
  window.ContentExtractor = ContentExtractor;
}

// For use in service worker context
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ContentExtractor;
}
