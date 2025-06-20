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
      '.article-wrapper',
      '.post-text',
      '.content-area',
      '.entry-text'
    ];

    this.unwantedSelectors = [
      'script',
      'style',
      'noscript',
      'nav',
      'header:not(.article-header):not(.post-header)',
      'footer:not(.article-footer):not(.post-footer)',
      'aside:not(.content-aside)',
      '.navigation',
      '.nav',
      '.menu',
      '.sidebar:not(.content-sidebar)',
      '.ad',
      '.advertisement',
      '.ads',
      '.sponsored',
      '.promo',
      '.banner:not(.content-banner)',
      '.social-share',
      '.social-buttons',
      '.share-buttons',
      '.comments:not(.article-comments)',
      '.comment-section:not(.article-comments)',
      '.newsletter',
      '.subscription',
      '.popup',
      '.modal',
      '.overlay',
      '.cookie-notice',
      '.related-articles:not(.content-related)',
      '.recommendations',
      '.trending',
      '.most-popular',
      '[class*="ad-"]:not([class*="read"])',
      '[id*="ad-"]:not([id*="read"])',
      '[class*="social"]:not([class*="article"])',
      '[class*="share"]:not([class*="content"])',
      '[role="banner"]',
      '[role="navigation"]',
      '[role="complementary"]:not([class*="content"])',
      '.skip-link',
      '.screen-reader-text',
      '.visually-hidden'
    ];

    // Enhanced selectors for better content preservation
    this.preserveSelectors = [
      '.article-comments',
      '.content-related',
      '.author-bio',
      '.article-metadata',
      '.post-metadata',
      '.content-sidebar',
      '.article-aside',
      '.content-aside'
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
        readingTime: this.estimateReadingTime(mainContent.innerText),
      };
    } catch (error) {
      console.error('Content extraction failed:', error);
      throw error;
    }
  }

  createCleanDocument(document) {
    // Clone the document body to avoid modifying the original
    const cleanBody = document.body.cloneNode(true);

    // Remove unwanted elements, but be more selective
    this.unwantedSelectors.forEach(selector => {
      cleanBody.querySelectorAll(selector).forEach(el => {
        // Double-check that we're not removing valuable content
        if (!this.shouldPreserveElement(el)) {
          el.remove();
        }
      });
    });

    // Clean up attributes selectively
    cleanBody.querySelectorAll('*').forEach(el => {
      // Remove style attributes that might interfere with content extraction
      el.removeAttribute('style');

      // Remove event handlers
      Array.from(el.attributes).forEach(attr => {
        if (attr.name.startsWith('on')) {
          el.removeAttribute(attr.name);
        }
      });

      // Preserve important semantic attributes
      const keepAttributes = [
        'href', 'src', 'alt', 'title', 'lang', 'dir',
        'colspan', 'rowspan', 'headers', 'scope',
        'datetime', 'cite', 'data-lang', 'data-language',
        'role', 'aria-label', 'aria-describedby'
      ];
      
      // Keep class attributes that indicate semantic meaning
      const className = el.getAttribute('class');
      if (className && this.hasSemanticClass(className)) {
        keepAttributes.push('class');
      }

      Array.from(el.attributes).forEach(attr => {
        if (!keepAttributes.includes(attr.name) && !attr.name.startsWith('data-')) {
          el.removeAttribute(attr.name);
        }
      });
    });

    // Enhance semantic structure
    this.enhanceSemanticStructure(cleanBody);

    return cleanBody;
  }

  shouldPreserveElement(element) {
    // Check if element should be preserved despite being in unwanted selectors
    const text = element.textContent.trim();
    const wordCount = text.split(/\s+/).filter(word => word.length > 0).length;
    
    // Preserve if it has substantial content
    if (wordCount > 20) return true;
    
    // Preserve if it contains semantic elements
    if (element.querySelector('h1, h2, h3, h4, h5, h6, p, ul, ol, table, blockquote, pre, code, figure')) {
      return true;
    }
    
    // Preserve if it matches preserve selectors
    return this.preserveSelectors.some(selector => {
      try {
        return element.matches(selector);
      } catch (e) {
        return false;
      }
    });
  }

  hasSemanticClass(className) {
    const semanticClasses = [
      'content', 'article', 'post', 'entry', 'main', 'body',
      'header', 'title', 'subtitle', 'author', 'date', 'time',
      'quote', 'blockquote', 'highlight', 'note', 'callout',
      'code', 'syntax', 'example', 'demo',
      'caption', 'figcaption', 'attribution',
      'warning', 'info', 'tip', 'important', 'alert',
      'metadata', 'byline', 'summary', 'abstract',
      'section', 'chapter', 'paragraph'
    ];
    
    return semanticClasses.some(semantic => 
      className.toLowerCase().includes(semantic)
    );
  }

  enhanceSemanticStructure(container) {
    // Convert div elements with semantic classes to appropriate semantic tags
    container.querySelectorAll('div').forEach(div => {
      const className = div.className.toLowerCase();
      
      // Convert quote-like divs to blockquotes
      if (className.includes('quote') || className.includes('blockquote')) {
        const blockquote = document.createElement('blockquote');
        blockquote.innerHTML = div.innerHTML;
        Array.from(div.attributes).forEach(attr => {
          if (attr.name !== 'class' || !attr.value.match(/quote|blockquote/i)) {
            blockquote.setAttribute(attr.name, attr.value);
          }
        });
        div.parentNode.replaceChild(blockquote, div);
      }
      
      // Convert code-like divs to pre/code
      else if (className.includes('code') && !div.querySelector('pre, code')) {
        const pre = document.createElement('pre');
        const code = document.createElement('code');
        
        // Preserve language information
        const langMatch = className.match(/(?:language|lang|brush|highlight)-(\w+)/);
        if (langMatch) {
          code.className = `language-${langMatch[1]}`;
        }
        
        code.textContent = div.textContent;
        pre.appendChild(code);
        div.parentNode.replaceChild(pre, div);
      }
    });

    // Enhance image figures
    container.querySelectorAll('img').forEach(img => {
      const parent = img.parentElement;
      if (parent && parent.tagName.toLowerCase() !== 'figure') {
        // Look for nearby caption elements
        const nextSibling = img.nextElementSibling;
        const prevSibling = img.previousElementSibling;
        
        let caption = null;
        if (nextSibling && this.isCaptionElement(nextSibling)) {
          caption = nextSibling;
        } else if (prevSibling && this.isCaptionElement(prevSibling)) {
          caption = prevSibling;
        }
        
        if (caption) {
          const figure = document.createElement('figure');
          const figcaption = document.createElement('figcaption');
          figcaption.textContent = caption.textContent;
          
          parent.insertBefore(figure, img);
          figure.appendChild(img);
          figure.appendChild(figcaption);
          caption.remove();
        }
      }
    });

    // Enhance definition lists from description lists patterns
    container.querySelectorAll('.definition, .term').forEach(element => {
      const parent = element.parentElement;
      if (parent && !parent.querySelector('dl')) {
        const dt = document.createElement('dt');
        dt.textContent = element.textContent;
        const dd = document.createElement('dd');
        
        // Look for definition content
        const definition = element.nextElementSibling;
        if (definition) {
          dd.textContent = definition.textContent;
          definition.remove();
        }
        
        const dl = document.createElement('dl');
        dl.appendChild(dt);
        dl.appendChild(dd);
        element.parentNode.replaceChild(dl, element);
      }
    });
  }

  isCaptionElement(element) {
    const tagName = element.tagName.toLowerCase();
    const className = element.className.toLowerCase();
    
    return tagName === 'figcaption' ||
           className.includes('caption') ||
           className.includes('image-caption') ||
           className.includes('photo-caption') ||
           className.includes('figure-caption');
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
      const score = textLength + childElements * 10;

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
      description: 'meta[name="description"]',
      keywords: 'meta[name="keywords"]',
      author: 'meta[name="author"]',
      published_time: 'meta[property="article:published_time"]',
      modified_time: 'meta[property="article:modified_time"]',
      section: 'meta[property="article:section"]',
      tags: 'meta[property="article:tag"]',
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
          height: img.naturalHeight || img.height,
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
          title: link.title || '',
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
      avgWordsPerParagraph: Math.round(avgWordsPerParagraph),
    };
  }

  countWords(text) {
    return SharedUtils?.countWords(text) || this._fallbackCountWords(text);
  }

  _fallbackCountWords(text) {
    return text
      .trim()
      .split(/\s+/)
      .filter(word => word.length > 0).length;
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

  resolveImageUrl(src, baseUrl) {
    try {
      return new URL(src, baseUrl).href;
    } catch {
      return url;
    }
  }

  // Additional methods expected by tests
  cleanContent(element) {
    if (!element) return null;
    
    // Clean content by removing unwanted elements and attributes
    const clone = element.cloneNode(true);
    
    // Remove unwanted elements
    this.unwantedSelectors.forEach(selector => {
      clone.querySelectorAll(selector).forEach(el => {
        if (!this.shouldPreserveElement(el)) {
          el.remove();
        }
      });
    });
    
    // Clean attributes
    this.cleanAttributes(clone);
    
    return clone;
  }

  cleanAttributes(element) {
    if (!element || !element.querySelectorAll) return;
    
    element.querySelectorAll('*').forEach(el => {
      const keepAttributes = ['href', 'src', 'alt', 'title', 'class', 'id'];
      
      // Get list of attributes to remove
      const attrsToRemove = [];
      if (el.attributes) {
        for (let i = 0; i < el.attributes.length; i++) {
          const attr = el.attributes[i];
          if (attr.name.startsWith('on') || // Remove event handlers
              (attr.name.startsWith('data-') && !attr.name.startsWith('data-lang')) || // Keep only data-lang
              (!keepAttributes.includes(attr.name) && !attr.name.startsWith('aria-'))) {
            attrsToRemove.push(attr.name);
          }
        }
      }
      
      // Remove the attributes
      attrsToRemove.forEach(attrName => {
        el.removeAttribute(attrName);
      });
    });
  }

  calculateReadingTime(text) {
    if (!text || typeof text !== 'string') return 0;
    
    const words = this.countWords(text);
    const wordsPerMinute = 200; // Average reading speed
    return Math.ceil(words / wordsPerMinute);
  }

  analyzeContentQuality(element) {
    if (!element || !element.textContent) {
      return {
        score: 0,
        hasHeadings: false,
        hasImages: false,
        hasLinks: false,
        wordCount: 0,
        readingTime: 0
      };
    }

    const textContent = element.textContent;
    const wordCount = this.countWords(textContent);
    const readingTime = this.calculateReadingTime(textContent);
    
    const hasHeadings = !!element.querySelector('h1, h2, h3, h4, h5, h6');
    const hasImages = !!element.querySelector('img');
    const hasLinks = !!element.querySelector('a[href]');
    
    // Calculate quality score based on various factors
    let score = 0;
    if (wordCount > 100) score += 20;
    if (wordCount > 500) score += 20;
    if (hasHeadings) score += 20;
    if (hasImages) score += 15;
    if (hasLinks) score += 15;
    if (wordCount > 200 && hasHeadings) score += 10; // Bonus for substantial content with structure
    
    return {
      score: Math.min(score, 100),
      hasHeadings,
      hasImages,
      hasLinks,
      wordCount,
      readingTime
    };
  }

  async extractPageContentWithTimeout(document, timeoutMs = 5000) {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error('Content extraction timeout'));
      }, timeoutMs);

      try {
        const result = this.extractPageContent(document);
        clearTimeout(timeoutId);
        resolve(result);
      } catch (error) {
        clearTimeout(timeoutId);
        reject(error);
      }
    });
  }

  validateExtractedContent(content) {
    if (!content || typeof content !== 'object') {
      return false;
    }

    // Check required fields
    const requiredFields = ['title', 'content', 'url', 'timestamp'];
    for (const field of requiredFields) {
      if (!content[field]) {
        return false;
      }
    }

    // Validate content quality
    if (typeof content.content !== 'string' || content.content.trim().length < 10) {
      return false;
    }

    // Validate URL format
    try {
      new URL(content.url);
    } catch {
      return false;
    }

    return true;
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
