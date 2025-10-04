import type { IDocumentMetadata, IImageAsset } from '../types.js';
import { createConsoleLogger, type ILogger } from '../util/index.js';

export interface IConversionOptions {
  preserveFormatting?: boolean;
  includeMetadata?: boolean;
  generateFrontmatter?: boolean;
  customRules?: Record<string, unknown>;
  headingStyle?: 'atx' | 'setext';
  bulletListMarker?: '-' | '*' | '+';
  codeBlockStyle?: 'fenced' | 'indented';
  linkStyle?: 'inlined' | 'referenced';
}

export interface IConversionResult {
  markdown: string;
  frontmatter: string;
  metadata: IDocumentMetadata;
  images: IImageAsset[];
  wordCount: number;
}

interface ISemanticSelectors {
  callouts: string[];
  quotes: string[];
  highlights: string[];
  captions: string[];
  metadata: string[];
  codeElements: string[];
}

/**
 * Environment-agnostic Markdown conversion engine. This class avoids direct
 * browser dependencies so it can run in the extension, CLI, and test
 * environments. Environment-specific adapters are responsible for wiring up
 * TurndownService or any other HTML-to-Markdown implementation.
 */
export class MarkdownConverterCore {
  protected turndownService: any = null;
  protected readonly semanticSelectors: ISemanticSelectors;
  protected _isInitialized = false;
  protected readonly logger: ILogger;

  constructor(logger: ILogger = createConsoleLogger('MarkdownConverterCore')) {
    this.logger = logger;
    this.semanticSelectors = {
      callouts: ['.callout', '.note', '.warning', '.info', '.alert', '.notice', '[role="note"]'],
      quotes: ['blockquote', '.quote', '.pullquote', '[role="blockquote"]'],
      highlights: ['.highlight', '.featured', '.important', 'mark', '.marker'],
      captions: ['figcaption', '.caption', '.image-caption', '.photo-caption'],
      metadata: ['.byline', '.author', '.date', '.timestamp', '.published', '.updated'],
      codeElements: ['code', 'pre', '.code', '.highlight', '.syntax'],
    };
  }

  /**
   * Called by environment-specific wrappers after assigning `turndownService`.
   */
  protected setupTurndownService(): void {
    if (!this.turndownService) {
      throw new Error('TurndownService not initialized');
    }

    this.turndownService.remove([
      'script',
      'style',
      'head',
      'noscript',
      'meta',
      'link',
      'nav',
      'footer',
      'aside',
      '.advertisement',
      '.ads',
      '.popup',
      '.modal',
      '.overlay',
      '.social-share',
      '.share-buttons',
      '.comment-form',
      '.subscription',
      '.newsletter',
      '.paywall',
      '.navigation',
      '.menu',
      '.sidebar',
      '.widget',
      '.substack-nav',
      '.publication-header',
      '.subscribe-widget',
      '.recommend',
      '.like-button',
      '.related-posts',
    ]);

    this.addMinimalCustomRules();
  }

  private addMinimalCustomRules(): void {
    if (!this.turndownService) return;

    this.turndownService.addRule('pseudoNumberedParagraphs', {
      filter: (node: any) => {
        if (node.nodeType !== 1 || node.tagName !== 'P') return false;
        if (node.closest('ol, ul, li')) return false;
        const text = (node.textContent || '').trim();
        return /^\d+\.\s+\w/.test(text) && text.length > 20;
      },
      replacement: (content: string) => {
        return content.trim() ? `\n${content.trim()}\n` : '';
      },
    });

    this.turndownService.addRule('basicTables', {
      filter: 'table',
      replacement: (_content: string, node: any) => {
        const rows: string[][] = [];
        const tableRows = node.querySelectorAll('tr');

        tableRows.forEach((row: any) => {
          const cells: string[] = [];
          const cellNodes = row.querySelectorAll('td, th');
          cellNodes.forEach((cell: any) => {
            cells.push((cell.textContent || '').trim());
          });
          if (cells.length > 0) {
            rows.push(cells);
          }
        });

        if (rows.length === 0) return '';

        let table = '';
        rows.forEach((row, index) => {
          table += '| ' + row.join(' | ') + ' |\n';
          if (index === 0) {
            table += '|' + row.map(() => '---').join('|') + '|\n';
          }
        });

        return `\n${table}\n`;
      },
    });
  }

  public convertToMarkdown(html: string, options: IConversionOptions = {}): IConversionResult {
    if (!this._isInitialized || !this.turndownService) {
      throw new Error('MarkdownConverter not properly initialized');
    }

    try {
      let cleanedHtml = this.preprocessHtml(html);

      if (
        (!cleanedHtml || cleanedHtml.trim() === '') &&
        typeof document !== 'undefined' &&
        document.body &&
        document.body.innerHTML
      ) {
        cleanedHtml = document.body.innerHTML;
      }

      let markdown = this.turndownService.turndown(cleanedHtml);

      if (
        (!markdown || markdown.trim() === '') &&
        typeof document !== 'undefined' &&
        document.body &&
        document.body.textContent
      ) {
        markdown = document.body.textContent.trim();
      }

      const cleanedMarkdown = this.postprocessMarkdown(markdown);

      let wordCount = cleanedMarkdown.split(/\s+/).filter(Boolean).length;
      if (
        wordCount === 0 &&
        typeof document !== 'undefined' &&
        document.body &&
        document.body.textContent
      ) {
        wordCount = document.body.textContent.trim().split(/\s+/).filter(Boolean).length;
      }

      const metadata: IDocumentMetadata = {
        title: '',
        url: typeof window !== 'undefined' ? window.location.href : '',
        captureDate: new Date().toISOString(),
        tags: [],
        author: '',
        wordCount,
        estimatedReadingTime: Math.ceil(wordCount / 200),
      };

      return {
        markdown: cleanedMarkdown,
        frontmatter: '',
        metadata,
        images: [],
        wordCount,
      };
    } catch (error) {
      this.logger.error('MarkdownConverter: Conversion failed:', error);
      throw error;
    }
  }

  private preprocessHtml(html: string): string {
    if (!html) return '';

    let cleaned = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
    cleaned = cleaned.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
    cleaned = cleaned.replace(/<!--[\s\S]*?-->/g, '');
    cleaned = cleaned.replace(/[ \t]+/g, ' ');
    cleaned = cleaned.replace(/\n\s*\n\s*\n/g, '\n\n');
    cleaned = cleaned.trim();

    return cleaned;
  }

  private postprocessMarkdown(markdown: string): string {
    if (!markdown) return '';

    let cleaned = markdown.replace(/\n\s*\n\s*\n\s*\n/g, '\n\n\n');
    cleaned = cleaned.replace(/\n\s*\n\s*\n/g, '\n\n');
    cleaned = cleaned.replace(/\n(#{1,6}\s[^\n]+)\n/g, '\n\n$1\n\n');
    cleaned = cleaned.replace(/\n(\s*[-*+]\s[^\n]+)/g, '\n\n$1');
    cleaned = cleaned.replace(/\n(\s*\d+\.\s[^\n]+)/g, '\n\n$1');
    cleaned = cleaned.trim();

    if (cleaned && !cleaned.endsWith('\n')) {
      cleaned += '\n';
    }

    return cleaned;
  }
}
