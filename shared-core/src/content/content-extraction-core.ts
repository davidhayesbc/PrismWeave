import type { IDocumentMetadata } from '../types.js';
import { createConsoleLogger, type ILogger } from '../util/index.js';

export interface ICoreExtractionOptions {
  customSelectors?: string[];
  cleanHtml?: boolean;
  preserveFormatting?: boolean;
  waitForDynamicContent?: boolean;
  removeAds?: boolean;
  removeNavigation?: boolean;
  excludeSelectors?: string[];
  includeImages?: boolean;
  includeLinks?: boolean;
  maxWordCount?: number;
}

export interface ICoreContentResult {
  content: string;
  metadata: IDocumentMetadata;
  cleanedContent: string;
  wordCount: number;
  readingTime: number;
}

export interface IPageStructure {
  headings: Array<{ level: number; text: string }>;
  sections: number;
  paragraphs: number;
}

export interface IImageInfo {
  src: string;
  alt: string;
}

/**
 * Core content extraction utility that works without Chrome APIs. Consumers are
 * responsible for executing this code in a DOM-enabled environment (browser,
 * puppeteer, etc.).
 */
export class ContentExtractionCore {
  private readonly logger: ILogger;

  constructor(logger: ILogger = createConsoleLogger('ContentExtractionCore')) {
    this.logger = logger;
  }

  async extractContent(options: ICoreExtractionOptions = {}): Promise<ICoreContentResult> {
    try {
      this.logger.debug('Starting core content extraction');

      if (options.waitForDynamicContent !== false) {
        await this.waitForContent();
      }

      const metadata = this.extractMetadata();
      const mainContent = this.findMainContent(options);
      if (!mainContent) {
        throw new Error('No suitable content found on page');
      }

      const cleanedElement = this.cleanContent(mainContent, options);
      const content = cleanedElement.innerHTML;
      const cleanedContent = cleanedElement.textContent || '';

      const wordCount = this.countWords(cleanedContent);
      const readingTime = this.estimateReadingTime(wordCount);

      this.logger.debug('Content extraction completed', {
        wordCount,
        readingTime,
        contentLength: content.length,
      });

      return {
        content,
        metadata: {
          ...metadata,
          wordCount,
          estimatedReadingTime: readingTime,
        },
        cleanedContent,
        wordCount,
        readingTime,
      };
    } catch (error) {
      this.logger.error('Content extraction failed:', error);
      throw error;
    }
  }

  extractMetadata(): IDocumentMetadata {
    const wordCount = this.countWords(document.body.textContent || '');
    const metadata: IDocumentMetadata = {
      title: this.extractTitle(),
      url: window.location.href,
      captureDate: new Date().toISOString(),
      tags: this.extractKeywords(),
      author: this.extractAuthor(),
      wordCount,
      estimatedReadingTime: this.estimateReadingTime(wordCount),
      description: this.extractDescription(),
      publishedDate: this.extractPublishedDate(),
      language: this.extractLanguage(),
    };

    if (this.isBlogPage()) {
      Object.assign(metadata, this.extractBlogMetadata());
    }

    return metadata;
  }

  extractImages(): IImageInfo[] {
    const images: IImageInfo[] = [];
    const imgElements = document.querySelectorAll('img');

    imgElements.forEach(img => {
      const src = img.src || (img as HTMLImageElement).dataset.src;
      const alt = img.alt || '';

      if (src && !src.startsWith('data:') && src.length > 0) {
        try {
          const absoluteUrl = new URL(src, window.location.href).href;
          images.push({ src: absoluteUrl, alt });
        } catch (error) {
          // Ignore invalid URLs
        }
      }
    });

    return images;
  }

  getPageStructure(): IPageStructure {
    const headings: Array<{ level: number; text: string }> = [];
    const headingElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6');

    headingElements.forEach(heading => {
      const level = parseInt(heading.tagName.charAt(1));
      const text = heading.textContent?.trim() || '';
      if (text) {
        headings.push({ level, text });
      }
    });

    const sections = document.querySelectorAll('section, article, main').length;
    const paragraphs = document.querySelectorAll('p').length;

    return { headings, sections, paragraphs };
  }

  getContentQualityScore(): number {
    const structure = this.getPageStructure();
    const textLength = document.body.textContent?.length || 0;
    const wordCount = this.countWords(document.body.textContent || '');

    let score = 0;

    if (textLength > 500) score += 20;
    if (textLength > 1500) score += 20;
    if (textLength > 3000) score += 10;

    if (wordCount > 100) score += 15;
    if (wordCount > 500) score += 15;

    if (structure.headings.length > 0) score += 10;
    if (structure.headings.length > 2) score += 10;
    if (structure.paragraphs > 3) score += 10;

    const htmlLength = document.body.innerHTML?.length || 1;
    const density = textLength / htmlLength;
    score += density * 10;

    return Math.min(score, 100);
  }

  isPaywallPresent(): boolean {
    const paywallSelectors = [
      '.paywall',
      '[class*="paywall"]',
      '.subscription-required',
      '.premium-content',
      '[class*="subscription"]',
      '[id*="paywall"]',
    ];

    return paywallSelectors.some(selector => document.querySelector(selector) !== null);
  }

  extractAdvancedMetadata(): Record<string, unknown> {
    const metadata: Record<string, unknown> = {};

    document.querySelectorAll('[property^="og:"]').forEach(meta => {
      const property = meta.getAttribute('property');
      const content = meta.getAttribute('content');
      if (property && content) {
        metadata[property] = content;
      }
    });

    document.querySelectorAll('[name^="twitter:"]').forEach(meta => {
      const name = meta.getAttribute('name');
      const content = meta.getAttribute('content');
      if (name && content) {
        metadata[name] = content;
      }
    });

    const metaTags = ['description', 'keywords', 'author', 'generator', 'theme-color'];
    metaTags.forEach(name => {
      const meta = document.querySelector(`[name="${name}"]`);
      if (meta) {
        const content = meta.getAttribute('content');
        if (content) metadata[name] = content;
      }
    });

    try {
      const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
      const structuredData: any[] = [];
      jsonLdScripts.forEach(script => {
        try {
          const data = JSON.parse(script.textContent || '');
          structuredData.push(data);
        } catch (error) {
          // Ignore malformed JSON-LD
        }
      });
      if (structuredData.length > 0) {
        metadata.structuredData = structuredData;
      }
    } catch (error) {
      // Ignore structured data errors
    }

    metadata.url = window.location.href;
    metadata.domain = window.location.hostname;
    metadata.pathname = window.location.pathname;
    metadata.language = document.documentElement.lang || 'en';
    metadata.extractedAt = new Date().toISOString();

    return metadata;
  }

  private async waitForContent(): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 500));

    const images = Array.from(document.images);
    if (images.length > 0) {
      const imagePromises = images.map(
        img =>
          new Promise(resolve => {
            if (img.complete) {
              resolve(img);
            } else {
              img.addEventListener('load', () => resolve(img));
              img.addEventListener('error', () => resolve(img));
              setTimeout(() => resolve(img), 2000);
            }
          })
      );
      await Promise.all(imagePromises);
    }
  }

  private findMainContent(options: ICoreExtractionOptions): Element | null {
    if (options.customSelectors?.length) {
      for (const selector of options.customSelectors) {
        const element = document.querySelector(selector);
        if (element && this.hasSubstantialContent(element)) {
          return element;
        }
      }
    }

    const contentSelectors = [
      'article',
      'main',
      '[role="main"]',
      '.content',
      '.post-content',
      '.entry-content',
      '.article-content',
      '#content',
      '#main',
      '.post',
      '.entry',
    ];

    for (const selector of contentSelectors) {
      const element = document.querySelector(selector);
      if (element && this.hasSubstantialContent(element)) {
        return element;
      }
    }

    const candidates = Array.from(document.querySelectorAll('div, section, article'));
    let bestCandidate: { element: Element; score: number } | null = null;

    for (const candidate of candidates) {
      if (this.hasSubstantialContent(candidate)) {
        const score = this.scoreElement(candidate);
        if (!bestCandidate || score > bestCandidate.score) {
          bestCandidate = { element: candidate, score };
        }
      }
    }

    return bestCandidate?.element || document.body;
  }

  private hasSubstantialContent(element: Element): boolean {
    const textContent = element.textContent || '';
    const wordCount = this.countWords(textContent);
    return wordCount > 30;
  }

  private scoreElement(element: Element): number {
    const text = element.textContent || '';
    const wordCount = this.countWords(text);
    let score = 0;

    score += Math.min(wordCount / 10, 50);

    const paragraphs = element.querySelectorAll('p').length;
    score += paragraphs * 2;

    const links = element.querySelectorAll('a').length;
    const linkDensity = links / Math.max(wordCount, 1);
    if (linkDensity > 0.3) score -= 20;

    const tagName = element.tagName.toLowerCase();
    if (tagName === 'article') score += 15;
    if (tagName === 'main') score += 10;

    const className = element.className.toLowerCase();
    if (className.includes('content')) score += 10;
    if (className.includes('post')) score += 8;
    if (className.includes('article')) score += 8;
    if (className.includes('sidebar')) score -= 10;
    if (className.includes('footer')) score -= 10;
    if (className.includes('header')) score -= 10;
    if (className.includes('nav')) score -= 15;

    return Math.max(score, 0);
  }

  private cleanContent(element: Element, options: ICoreExtractionOptions): Element {
    const cloned = element.cloneNode(true) as Element;

    const defaultExcludeSelectors = [
      'script',
      'style',
      'noscript',
      'iframe',
      '.advertisement',
      '.ad',
      '.ads',
      '.popup',
      '.modal',
      '.social-share',
      '.comments',
      '.related-posts',
      '[style*="display: none"]',
      '[style*="visibility: hidden"]',
    ];

    const excludeSelectors = [...defaultExcludeSelectors, ...(options.excludeSelectors || [])];

    excludeSelectors.forEach(selector => {
      const elements = cloned.querySelectorAll(selector);
      elements.forEach(el => el.remove());
    });

    if (options.removeAds !== false) {
      this.removeAds(cloned);
    }

    if (options.removeNavigation !== false) {
      this.removeNavigation(cloned);
    }

    return cloned;
  }

  private removeAds(element: Element): void {
    const adSelectors = [
      '[class*="ad"]',
      '[id*="ad"]',
      '[class*="banner"]',
      '[id*="banner"]',
      '[class*="promo"]',
      '[id*="promo"]',
      '[class*="sponsor"]',
      '[id*="sponsor"]',
    ];

    adSelectors.forEach(selector => {
      const elements = element.querySelectorAll(selector);
      elements.forEach(el => {
        const text = el.textContent || '';
        const wordCount = this.countWords(text);
        const className = el.className.toLowerCase();
        const id = el.id.toLowerCase();

        const adPatterns = [
          'advertisement',
          'google-ad',
          'adsense',
          'ad-banner',
          'ad-container',
          'ad-wrapper',
          'sponsored',
          'promo-box',
        ];

        const hasAdCharacteristics = adPatterns.some(
          pattern => className.includes(pattern) || id.includes(pattern)
        );

        if (wordCount < 10 || hasAdCharacteristics) {
          el.remove();
        }
      });
    });
  }

  private removeNavigation(element: Element): void {
    const navSelectors = [
      'nav',
      'header',
      'footer',
      '[role="navigation"]',
      '[role="banner"]',
      '[role="contentinfo"]',
      '.navigation',
      '.nav',
      '.menu',
      '.breadcrumb',
    ];

    navSelectors.forEach(selector => {
      const elements = element.querySelectorAll(selector);
      elements.forEach(el => el.remove());
    });
  }

  private extractTitle(): string {
    const titleSources = [
      () => document.querySelector('[property="og:title"]')?.getAttribute('content'),
      () => document.querySelector('[name="twitter:title"]')?.getAttribute('content'),
      () => document.querySelector('h1')?.textContent,
      () => document.title,
    ];

    for (const source of titleSources) {
      const title = source();
      if (title && title.trim().length > 0) {
        return title.trim();
      }
    }

    return 'Untitled';
  }

  private extractDescription(): string {
    const descSources = [
      () => document.querySelector('[property="og:description"]')?.getAttribute('content'),
      () => document.querySelector('[name="twitter:description"]')?.getAttribute('content'),
      () => document.querySelector('[name="description"]')?.getAttribute('content'),
    ];

    for (const source of descSources) {
      const desc = source();
      if (desc && desc.trim().length > 0) {
        return desc.trim();
      }
    }

    return '';
  }

  private extractKeywords(): string[] {
    const keywordsMeta = document.querySelector('[name="keywords"]')?.getAttribute('content');
    if (keywordsMeta) {
      return keywordsMeta
        .split(',')
        .map(keyword => keyword.trim())
        .filter(keyword => keyword.length > 0);
    }
    return [];
  }

  private extractAuthor(): string {
    const authorSources = [
      () => document.querySelector('[property="article:author"]')?.getAttribute('content'),
      () => document.querySelector('[name="author"]')?.getAttribute('content'),
      () => document.querySelector('[rel="author"]')?.textContent,
      () => document.querySelector('.author')?.textContent,
      () => document.querySelector('.byline')?.textContent,
      () => document.querySelector('[class*="author"]')?.textContent,
      () => document.querySelector('.post-author')?.textContent,
    ];

    for (const source of authorSources) {
      const author = source();
      if (author && author.trim().length > 0) {
        return author.trim();
      }
    }

    return '';
  }

  private extractPublishedDate(): string {
    const dateSources = [
      () => document.querySelector('[property="article:published_time"]')?.getAttribute('content'),
      () => document.querySelector('[name="publish_date"]')?.getAttribute('content'),
      () => document.querySelector('time[datetime]')?.getAttribute('datetime'),
      () => document.querySelector('.publish-date')?.textContent,
      () => document.querySelector('.date')?.textContent,
      () => document.querySelector('.published')?.textContent,
      () => document.querySelector('[class*="date"]')?.textContent,
    ];

    for (const source of dateSources) {
      const date = source();
      if (date && date.trim().length > 0) {
        return date.trim();
      }
    }

    return '';
  }

  private extractLanguage(): string {
    return (
      document.documentElement.lang ||
      document.querySelector('[property="og:locale"]')?.getAttribute('content') ||
      'en'
    );
  }

  private isBlogPage(): boolean {
    const url = window.location.href.toLowerCase();
    const hostname = window.location.hostname.toLowerCase();

    const blogUrlPatterns = [
      /\/blog\//,
      /\/posts?\//,
      /\/\d{4}\/\d{2}\/\d{2}\//,
      /\/\d{4}\/\d{2}\//,
      /\/article\//,
      /\/news\//,
    ];

    if (blogUrlPatterns.some(pattern => pattern.test(url))) {
      return true;
    }

    const blogHostnames = [
      'blog.',
      '.blog',
      'medium.com',
      'dev.to',
      'hashnode.dev',
      'substack.com',
      'ghost.io',
    ];

    if (blogHostnames.some(host => hostname.includes(host))) {
      return true;
    }

    const blogSelectors = [
      '.post',
      '.entry',
      '.article',
      '[class*="post"]',
      '[class*="entry"]',
      '[class*="article"]',
      '.blog-post',
      '.news-article',
    ];

    const hasBlogElements = blogSelectors.some(selector => {
      const elements = document.querySelectorAll(selector);
      return Array.from(elements).some(el => {
        const wordCount = this.countWords(el.textContent || '');
        return wordCount > 50;
      });
    });

    return hasBlogElements;
  }

  private extractBlogMetadata(): Partial<IDocumentMetadata> {
    const blogMetadata: Partial<IDocumentMetadata> = {};

    const tags = this.extractTags();
    if (tags.length > 0) {
      blogMetadata.tags = tags;
    }

    const wordCount = this.countWords(document.body.textContent || '');
    blogMetadata.estimatedReadingTime = this.estimateReadingTime(wordCount);

    return blogMetadata;
  }

  private extractTags(): string[] {
    const tags: string[] = [];

    const tagSelectors = [
      '.tags a',
      '.tag',
      '.post-tags a',
      '[class*="tag"] a',
      '.categories a',
      '.category',
      '[rel="tag"]',
    ];

    tagSelectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        const tagText = el.textContent?.trim();
        if (tagText && tagText.length > 0 && tagText.length < 50) {
          tags.push(tagText);
        }
      });
    });

    return [...new Set(tags)];
  }

  private countWords(text: string): number {
    return text.split(/\s+/).filter(word => word.length > 0).length;
  }

  private estimateReadingTime(wordCount: number): number {
    return Math.ceil(wordCount / 200);
  }
}
