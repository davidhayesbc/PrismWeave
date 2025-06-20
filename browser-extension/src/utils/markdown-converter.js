// PrismWeave Markdown Converter
// Enhanced HTML to Markdown conversion with high-fidelity preservation

class MarkdownConverter {
  constructor() {
    this.turndownService = null;
    this.initializeTurndown();
    
    // Enhanced selectors for semantic elements
    this.semanticSelectors = {
      callouts: ['.callout', '.note', '.warning', '.info', '.alert', '.notice', '[role="note"]'],
      quotes: ['blockquote', '.quote', '.pullquote', '[role="blockquote"]'],
      highlights: ['.highlight', '.featured', '.important', 'mark', '.marker'],
      captions: ['figcaption', '.caption', '.image-caption', '.photo-caption'],
      metadata: ['.byline', '.author', '.date', '.timestamp', '.published', '.updated'],
      codeElements: ['code', 'pre', '.code', '.highlight', '.syntax']
    };
  }
  initializeTurndown() {
    // Service worker context check - TurndownService should never be loaded here
    const isServiceWorker = (typeof importScripts === 'function' && typeof window === 'undefined');
    
    if (isServiceWorker) {
      console.info('MarkdownConverter: Running in service worker context, using enhanced fallback conversion');
      this.turndownService = null;
      return;
    }
    
    // Check if TurndownService is available (from imported library)
    if (typeof TurndownService === 'undefined') {
      console.warn('TurndownService not available, using enhanced fallback conversion');
      this.turndownService = null;
      return;
    }

    console.info('MarkdownConverter: Initializing TurndownService with enhanced rules');
    
    // Initialize Turndown service with enhanced custom rules
    this.turndownService = new TurndownService({
      headingStyle: 'atx',
      bulletListMarker: '-',
      codeBlockStyle: 'fenced',
      emDelimiter: '*',
      strongDelimiter: '**',
      linkStyle: 'inlined',
      linkReferenceStyle: 'full',
      preformattedCode: true,
      blankReplacement: function (content, node) {
        return node.isBlock ? '\n\n' : '';
      },
      keepReplacement: function (content, node) {
        return node.isBlock ? '\n\n' + node.outerHTML + '\n\n' : node.outerHTML;
      },
      defaultReplacement: function (content, node) {
        return node.isBlock ? '\n\n' + content + '\n\n' : content;
      }
    });

    // Add enhanced custom rules for better conversion
    this.addEnhancedCustomRules();
  }
  addEnhancedCustomRules() {
    if (!this.turndownService) return;

    // Remove unwanted elements but preserve more content
    this.turndownService.addRule('removeUnwanted', {
      filter: ['script', 'style', 'noscript'],
      replacement: () => '',
    });

    // Preserve semantic HTML elements that should be kept
    this.turndownService.addRule('preserveSemanticHTML', {
      filter: ['details', 'summary', 'kbd', 'var', 'samp', 'output'],
      replacement: (content, node) => {
        const tagName = node.nodeName.toLowerCase();
        return `<${tagName}>${content}</${tagName}>`;
      }
    });

    // Enhanced code block handling with language detection
    this.turndownService.addRule('enhancedCodeBlocks', {
      filter: ['pre'],
      replacement: (content, node) => {
        const code = node.querySelector('code');
        let language = '';
        
        if (code) {
          // Try multiple methods to detect language
          language = this.detectCodeLanguage(code, node);
          content = code.textContent || code.innerText || content;
        }
        
        // Preserve original formatting and indentation
        const lines = content.split('\n');
        const minIndent = this.getMinimumIndentation(lines);
        const cleanedContent = lines
          .map(line => line.substring(minIndent))
          .join('\n')
          .trim();
        
        return `\n\`\`\`${language}\n${cleanedContent}\n\`\`\`\n\n`;
      },
    });

    // Enhanced inline code handling
    this.turndownService.addRule('enhancedInlineCode', {
      filter: ['code'],
      replacement: (content, node) => {
        // Don't process if it's inside a pre tag (handled by code blocks)
        if (node.closest('pre')) return content;
        
        // Handle backticks in content
        const backtickCount = (content.match(/`/g) || []).length;
        const wrapper = backtickCount > 0 ? '``' : '`';
        
        return `${wrapper}${content}${wrapper}`;
      },
    });

    // Enhanced blockquote handling with attribution
    this.turndownService.addRule('enhancedBlockquotes', {
      filter: 'blockquote',
      replacement: (content, node) => {
        // Look for citation or attribution
        const cite = node.querySelector('cite, .cite, .attribution, .author');
        let attribution = '';
        
        if (cite) {
          attribution = `\n\n*— ${cite.textContent.trim()}*`;
          cite.remove(); // Remove from content to avoid duplication
        }
        
        const lines = content.trim().split('\n');
        const quotedLines = lines.map(line => `> ${line.trim()}`).join('\n');
        
        return `\n${quotedLines}${attribution}\n\n`;
      },
    });

    // Enhanced table handling with better formatting
    this.turndownService.addRule('enhancedTables', {
      filter: 'table',
      replacement: (content, node) => {
        return this.convertEnhancedTable(node);
      },
    });

    // Enhanced image handling with figure support
    this.turndownService.addRule('enhancedImages', {
      filter: ['img', 'figure'],
      replacement: (content, node) => {
        if (node.nodeName.toLowerCase() === 'figure') {
          return this.convertFigure(node);
        }
        
        const alt = node.getAttribute('alt') || '';
        const src = node.getAttribute('src') || '';
        const title = node.getAttribute('title');
        const width = node.getAttribute('width');
        const height = node.getAttribute('height');

        if (!src) return '';

        let imageMarkdown = `![${alt}](${src}`;
        if (title) {
          imageMarkdown += ` "${title}"`;
        }
        imageMarkdown += ')';
        
        // Add size information as HTML if available
        if (width || height) {
          const sizeAttrs = [];
          if (width) sizeAttrs.push(`width="${width}"`);
          if (height) sizeAttrs.push(`height="${height}"`);
          imageMarkdown += `\n<img src="${src}" ${sizeAttrs.join(' ')} alt="${alt}" style="display: none;">`;
        }

        return imageMarkdown;
      },
    });

    // Handle definition lists
    this.turndownService.addRule('definitionLists', {
      filter: ['dl', 'dt', 'dd'],
      replacement: (content, node) => {
        const tagName = node.nodeName.toLowerCase();
        
        if (tagName === 'dl') {
          return `\n${content}\n`;
        } else if (tagName === 'dt') {
          return `**${content.trim()}**\n`;
        } else if (tagName === 'dd') {
          return `: ${content.trim()}\n\n`;
        }
        
        return content;
      }
    });

    // Handle callouts and special content boxes
    this.turndownService.addRule('callouts', {
      filter: node => {
        return this.semanticSelectors.callouts.some(selector => 
          node.matches && node.matches(selector)
        );
      },
      replacement: (content, node) => {
        const type = this.detectCalloutType(node);
        return `\n> **${type}:** ${content.trim()}\n\n`;
      }
    });

    // Preserve important formatting elements
    this.turndownService.addRule('preserveFormatting', {
      filter: ['sub', 'sup', 'small', 'del', 'ins', 'mark'],
      replacement: (content, node) => {
        const tagName = node.nodeName.toLowerCase();
        
        switch (tagName) {
          case 'sub':
            return `<sub>${content}</sub>`;
          case 'sup':
            return `<sup>${content}</sup>`;
          case 'small':
            return `<small>${content}</small>`;
          case 'del':
            return `~~${content}~~`;
          case 'ins':
            return `<ins>${content}</ins>`;
          case 'mark':
            return `==${content}==`;
          default:
            return content;
        }
      }
    });

    // Enhanced link handling with better title preservation
    this.turndownService.addRule('enhancedLinks', {
      filter: 'a',
      replacement: (content, node) => {
        const href = node.getAttribute('href');
        const title = node.getAttribute('title');
        
        if (!href) return content;
        
        // Handle anchor links
        if (href.startsWith('#')) {
          return `[${content}](${href})`;
        }
        
        // Handle email links
        if (href.startsWith('mailto:')) {
          const email = href.replace('mailto:', '');
          return `[${content || email}](${href})`;
        }
        
        // Regular links with optional title
        let linkMarkdown = `[${content}](${href}`;
        if (title && title !== content) {
          linkMarkdown += ` "${title}"`;
        }
        linkMarkdown += ')';
        
        return linkMarkdown;
      }
    });

    // Handle horizontal rules
    this.turndownService.addRule('horizontalRules', {
      filter: 'hr',
      replacement: () => '\n\n---\n\n'
    });
  }

  detectCodeLanguage(codeElement, preElement) {
    // Try class-based detection first
    const codeClasses = codeElement.className || '';
    const preClasses = preElement.className || '';
    
    // Common patterns for language detection
    const languagePatterns = [
      /(?:language|lang|brush|highlight)-(\w+)/i,
      /(\w+)(?:-code|highlight)/i,
      /code-(\w+)/i
    ];
    
    for (const pattern of languagePatterns) {
      let match = codeClasses.match(pattern) || preClasses.match(pattern);
      if (match) {
        return this.normalizeLanguageName(match[1]);
      }
    }
    
    // Try data attributes
    const dataLang = codeElement.getAttribute('data-lang') || 
                    codeElement.getAttribute('data-language') ||
                    preElement.getAttribute('data-lang') ||
                    preElement.getAttribute('data-language');
    
    if (dataLang) {
      return this.normalizeLanguageName(dataLang);
    }
    
    // Try content-based detection for common patterns
    const content = codeElement.textContent || codeElement.innerText || '';
    return this.detectLanguageFromContent(content);
  }

  normalizeLanguageName(lang) {
    const languageMap = {
      'js': 'javascript',
      'ts': 'typescript',
      'py': 'python',
      'rb': 'ruby',
      'sh': 'bash',
      'shell': 'bash',
      'zsh': 'bash',
      'ps1': 'powershell',
      'cs': 'csharp',
      'cpp': 'c++',
      'hpp': 'c++',
      'h': 'c',
      'c': 'c',
      'php': 'php',
      'md': 'markdown',
      'yml': 'yaml',
      'json': 'json',
      'xml': 'xml',
      'html': 'html',
      'css': 'css',
      'scss': 'scss',
      'sass': 'sass',
      'sql': 'sql'
    };
    
    return languageMap[lang.toLowerCase()] || lang.toLowerCase();
  }

  detectLanguageFromContent(content) {
    const trimmed = content.trim();
    
    // JavaScript/TypeScript patterns
    if (/(?:function|const|let|var|=>|interface|class)\s/.test(trimmed)) {
      return /interface|type\s+\w+\s*=/.test(trimmed) ? 'typescript' : 'javascript';
    }
    
    // Python patterns
    if (/(?:def |import |from |class |if __name__|print\()/i.test(trimmed)) {
      return 'python';
    }
    
    // HTML patterns
    if (/^<(?:html|!DOCTYPE|head|body|div|span|p|a|img)/i.test(trimmed)) {
      return 'html';
    }
    
    // CSS patterns
    if (/^[.#]?\w+\s*\{|\w+\s*:\s*[^;]+;/.test(trimmed)) {
      return 'css';
    }
    
    // JSON patterns
    if (/^[\{\[]/.test(trimmed) && /[\}\]]$/.test(trimmed)) {
      try {
        JSON.parse(trimmed);
        return 'json';
      } catch (e) {
        // Not valid JSON
      }
    }
    
    // SQL patterns
    if (/(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\s+/i.test(trimmed)) {
      return 'sql';
    }
    
    // Shell/Bash patterns
    if (/^[$#]\s|#!/.test(trimmed) || /(?:echo|grep|sed|awk|ls|cd|mkdir)\s/.test(trimmed)) {
      return 'bash';
    }
    
    return '';
  }

  getMinimumIndentation(lines) {
    const nonEmptyLines = lines.filter(line => line.trim().length > 0);
    if (nonEmptyLines.length === 0) return 0;
    
    return Math.min(...nonEmptyLines.map(line => {
      const match = line.match(/^(\s*)/);
      return match ? match[1].length : 0;
    }));
  }

  convertFigure(figureElement) {
    const img = figureElement.querySelector('img');
    const caption = figureElement.querySelector('figcaption, .caption');
    
    if (!img) return '';
    
    const alt = img.getAttribute('alt') || '';
    const src = img.getAttribute('src') || '';
    const title = img.getAttribute('title');
    
    let markdown = `![${alt}](${src}`;
    if (title) {
      markdown += ` "${title}"`;
    }
    markdown += ')';
    
    if (caption) {
      const captionText = caption.textContent.trim();
      markdown += `\n*${captionText}*`;
    }
    
    return `\n${markdown}\n\n`;
  }

  convertEnhancedTable(tableNode) {
    const rows = Array.from(tableNode.querySelectorAll('tr'));
    if (rows.length === 0) return '';

    const markdown = [];
    let hasHeader = false;

    // Check if first row contains th elements or is in thead
    const firstRow = rows[0];
    const isHeaderRow = firstRow.closest('thead') || 
                       firstRow.querySelectorAll('th').length > 0;

    if (isHeaderRow) {
      hasHeader = true;
      const headerCells = Array.from(firstRow.querySelectorAll('th, td'));
      const headerText = headerCells.map(cell => this.cleanCellContent(cell)).join(' | ');
      markdown.push(`| ${headerText} |`);

      // Add separator with alignment detection
      const separator = headerCells.map(cell => {
        const align = cell.style.textAlign || cell.align || '';
        switch (align.toLowerCase()) {
          case 'left': return ':---';
          case 'right': return '---:';
          case 'center': return ':---:';
          default: return '---';
        }
      }).join(' | ');
      markdown.push(`| ${separator} |`);
    }

    // Process data rows
    const dataRows = hasHeader ? rows.slice(1) : rows;
    for (const row of dataRows) {
      // Skip rows that are in thead if we haven't processed header yet
      if (!hasHeader && row.closest('thead')) continue;
      
      const cells = Array.from(row.querySelectorAll('td, th'));
      if (cells.length === 0) continue;
      
      const rowText = cells.map(cell => this.cleanCellContent(cell)).join(' | ');
      markdown.push(`| ${rowText} |`);
    }

    // If no header was found, add a generic one
    if (!hasHeader && markdown.length > 0) {
      const firstDataRow = markdown[0];
      const cellCount = (firstDataRow.match(/\|/g) || []).length - 1;
      const headerRow = `| ${Array(cellCount).fill('Column').map((col, i) => `${col} ${i + 1}`).join(' | ')} |`;
      const separatorRow = `| ${Array(cellCount).fill('---').join(' | ')} |`;
      markdown.unshift(separatorRow);
      markdown.unshift(headerRow);
    }

    return markdown.length > 0 ? `\n${markdown.join('\n')}\n\n` : '';
  }

  cleanCellContent(cell) {
    // Convert internal markdown elements
    let content = cell.innerHTML;
    
    // Handle bold/strong
    content = content.replace(/<(strong|b)(?:\s[^>]*)?>([^<]*)<\/\1>/gi, '**$2**');
    
    // Handle italic/em
    content = content.replace(/<(em|i)(?:\s[^>]*)?>([^<]*)<\/\1>/gi, '*$2*');
    
    // Handle code
    content = content.replace(/<code(?:\s[^>]*)?>([^<]*)<\/code>/gi, '`$1`');
    
    // Handle links
    content = content.replace(/<a(?:\s[^>]*)?href=["']([^"']*)["'][^>]*>([^<]*)<\/a>/gi, '[$2]($1)');
    
    // Remove remaining HTML tags
    content = content.replace(/<[^>]+>/g, '');
    
    // Clean up whitespace and escape pipe characters
    return content.trim().replace(/\|/g, '\\|').replace(/\n/g, ' ');
  }

  detectCalloutType(node) {
    const className = node.className.toLowerCase();
    const nodeText = node.textContent.toLowerCase();
    
    if (className.includes('warning') || className.includes('danger') || nodeText.includes('warning')) {
      return 'Warning';
    } else if (className.includes('info') || className.includes('information')) {
      return 'Info';
    } else if (className.includes('note')) {
      return 'Note';
    } else if (className.includes('tip') || className.includes('hint')) {
      return 'Tip';
    } else if (className.includes('important') || className.includes('alert')) {
      return 'Important';
    }
    
    return 'Note';
  }

  extractLanguage(codeElement) {
    const className = codeElement.className || '';
    const languageMatch = className.match(/language-(\w+)/);
    return languageMatch ? languageMatch[1] : '';
  }

  convertTable(tableNode) {
    // This is the original simpler table conversion - keeping for fallback
    const rows = Array.from(tableNode.querySelectorAll('tr'));
    if (rows.length === 0) return '';

    const markdown = [];

    // Process header row
    const headerRow = rows[0];
    const headerCells = Array.from(headerRow.querySelectorAll('th, td'));
    const headerText = headerCells.map(cell => cell.textContent.trim()).join(' | ');
    markdown.push(`| ${headerText} |`);

    // Add separator
    const separator = headerCells.map(() => '---').join(' | ');
    markdown.push(`| ${separator} |`);

    // Process data rows
    for (let i = 1; i < rows.length; i++) {
      const cells = Array.from(rows[i].querySelectorAll('td, th'));
      const rowText = cells.map(cell => cell.textContent.trim()).join(' | ');
      markdown.push(`| ${rowText} |`);
    }

    return markdown.join('\n') + '\n\n';
  }
  convert(html) {
    if (!html || typeof html !== 'string') {
      return '';
    }

    try {
      // Enhanced HTML preprocessing
      const preprocessedHtml = this.preprocessHtml(html);

      // Convert to markdown using Turndown if available, otherwise use enhanced fallback
      let markdown;
      if (this.turndownService) {
        markdown = this.turndownService.turndown(preprocessedHtml);
      } else {
        markdown = this.enhancedHtmlToMarkdown(preprocessedHtml);
      }

      // Enhanced post-processing
      return this.enhancedPostProcessMarkdown(markdown);
    } catch (error) {
      console.error('Markdown conversion failed:', error);
      // Fallback to enhanced conversion
      return this.enhancedHtmlToMarkdown(html);
    }
  }

  preprocessHtml(html) {
    // Check if we're in a service worker context (no document available)
    if (typeof document === 'undefined' || typeof window === 'undefined') {
      return this.regexPreprocessHtml(html);
    }

    // Create a temporary DOM element to preprocess the HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;

    // Enhanced content preservation - be more selective about what we remove
    const unwantedSelectors = [
      // Scripts and styles
      'script', 'style', 'noscript',
      // Navigation and UI elements
      'nav', '.navigation', '.nav', '.menu', '.sidebar',
      // Ads and promotional content
      '.ad', '.advertisement', '.ads', '.sponsored', '.promo',
      // Social and sharing
      '.social-share', '.social-buttons', '.share-buttons',
      // Comments (but preserve if they seem to be part of content)
      '.comments:not(.article-comments)', '.comment-section:not(.article-comments)',
      // Subscription and newsletter forms
      '.newsletter', '.subscription', '.subscribe',
      // UI overlays
      '.popup', '.modal', '.overlay', '.cookie-notice',
      // Generic promotional selectors
      '[class*="ad-"]', '[id*="ad-"]'
    ];

    unwantedSelectors.forEach(selector => {
      tempDiv.querySelectorAll(selector).forEach(el => {
        // Double-check we're not removing valuable content
        if (!this.containsValueableContent(el)) {
          el.remove();
        }
      });
    });

    // Enhance semantic structure
    this.enhanceSemanticStructure(tempDiv);

    // Clean up attributes more selectively
    tempDiv.querySelectorAll('*').forEach(el => {
      // Remove style attributes but preserve data attributes that might be useful
      el.removeAttribute('style');
      
      // Remove event handlers
      Array.from(el.attributes).forEach(attr => {
        if (attr.name.startsWith('on')) {
          el.removeAttribute(attr.name);
        }
      });

      // Preserve important attributes for semantic meaning
      const keepAttributes = [
        'href', 'src', 'alt', 'title', 'lang', 'dir',
        'colspan', 'rowspan', 'headers', 'scope',
        'datetime', 'cite', 'data-lang', 'data-language'
      ];
      
      const attributes = Array.from(el.attributes);
      attributes.forEach(attr => {
        if (!keepAttributes.includes(attr.name) && !attr.name.startsWith('data-')) {
          // Keep class if it might indicate semantic meaning
          if (attr.name === 'class' && this.hasSemanticClass(attr.value)) {
            return;
          }
          if (attr.name !== 'class' && attr.name !== 'id') {
            el.removeAttribute(attr.name);
          }
        }
      });
    });

    return tempDiv.innerHTML;
  }

  containsValueableContent(element) {
    const text = element.textContent.trim();
    const wordCount = text.split(/\s+/).filter(word => word.length > 0).length;
    
    // Consider content valuable if it has substantial text
    // or contains semantic elements like headers, lists, etc.
    return wordCount > 10 || 
           element.querySelector('h1, h2, h3, h4, h5, h6, ul, ol, table, blockquote, pre, code');
  }

  hasSemanticClass(className) {
    const semanticClasses = [
      'content', 'article', 'post', 'entry', 'main',
      'header', 'title', 'subtitle', 'author', 'date',
      'quote', 'blockquote', 'highlight', 'note', 'callout',
      'code', 'syntax', 'example', 'demo',
      'caption', 'figcaption', 'attribution',
      'warning', 'info', 'tip', 'important', 'alert'
    ];
    
    return semanticClasses.some(semantic => 
      className.toLowerCase().includes(semantic)
    );
  }

  enhanceSemanticStructure(container) {
    // Only run if we have document access (not in service worker)
    if (typeof document === 'undefined' || typeof window === 'undefined') {
      return;
    }

    // Convert div elements with semantic classes to appropriate semantic tags
    container.querySelectorAll('div').forEach(div => {
      const className = div.className.toLowerCase();
      
      if (className.includes('quote') || className.includes('blockquote')) {
        const blockquote = document.createElement('blockquote');
        blockquote.innerHTML = div.innerHTML;
        div.parentNode.replaceChild(blockquote, div);
      } else if (className.includes('code') && !div.querySelector('pre, code')) {
        const pre = document.createElement('pre');
        const code = document.createElement('code');
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
        if (nextSibling && (
          nextSibling.className.toLowerCase().includes('caption') ||
          nextSibling.tagName.toLowerCase() === 'figcaption'
        )) {
          const figure = document.createElement('figure');
          const caption = document.createElement('figcaption');
          caption.textContent = nextSibling.textContent;
          
          parent.insertBefore(figure, img);
          figure.appendChild(img);
          figure.appendChild(caption);
          nextSibling.remove();
        }
      }
    });
  }

  regexPreprocessHtml(html) {
    // Enhanced regex-based HTML preprocessing for service worker context
    let processed = html;

    // Remove unwanted elements and their content more selectively
    const unwantedPatterns = [
      /<(script|style|noscript)[^>]*>.*?<\/\1>/gis,
      /<[^>]*\b(?:class|id)=["'][^"']*\b(?:ad(?!-)(?!ministrat)|advertisement|ads|sponsored|sidebar|nav|navigation|menu|popup|modal|overlay|cookie-notice)\b[^"']*["'][^>]*>.*?<\/[^>]+>/gis,
    ];

    unwantedPatterns.forEach(pattern => {
      processed = processed.replace(pattern, '');
    });

    // Enhance semantic structure with regex
    // Convert semantic divs to appropriate tags
    processed = processed.replace(
      /<div[^>]*class=["'][^"']*\b(?:quote|blockquote)\b[^"']*["'][^>]*>(.*?)<\/div>/gis,
      '<blockquote>$1</blockquote>'
    );

    return processed;
  }

  cleanHtml(html) {
    // Check if we're in a service worker context (no document available)
    if (typeof document === 'undefined' || typeof window === 'undefined') {
      // Fallback for service worker: use regex-based cleaning
      return this.regexCleanHtml(html);
    }

    // Create a temporary DOM element to clean the HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;

    // Remove ads and unwanted content
    const unwantedSelectors = [
      '.ad',
      '.advertisement',
      '.ads',
      '.sponsored',
      '.sidebar',
      '.nav',
      '.navigation',
      '.menu',
      '.footer',
      '.header',
      '.banner',
      '[class*="ad-"]',
      '[id*="ad-"]',
      '.social-share',
      '.social-buttons',
      '.newsletter',
      '.subscription',
      '.comments',
      '.comment-section',
      '.related-articles',
      '.recommendations',
    ];

    unwantedSelectors.forEach(selector => {
      tempDiv.querySelectorAll(selector).forEach(el => el.remove());
    });

    // Clean up attributes that might interfere
    tempDiv.querySelectorAll('*').forEach(el => {
      // Remove style attributes
      el.removeAttribute('style');
      el.removeAttribute('class');
      el.removeAttribute('id');

      // Keep only essential attributes
      const keepAttributes = ['href', 'src', 'alt', 'title'];
      const attributes = Array.from(el.attributes);
      attributes.forEach(attr => {
        if (!keepAttributes.includes(attr.name)) {
          el.removeAttribute(attr.name);
        }
      });
    });

    return tempDiv.innerHTML;
  }

  regexCleanHtml(html) {
    // Regex-based HTML cleaning for service worker context
    let cleaned = html;

    // Remove unwanted elements and their content
    const unwantedPatterns = [
      /<(script|style|noscript)[^>]*>.*?<\/\1>/gis,
      /<[^>]*\b(class|id)=["'][^"']*\b(ad|advertisement|ads|sponsored|sidebar|nav|navigation|menu|footer|header|comments|comment-section|related-articles|recommendations)\b[^"']*["'][^>]*>.*?<\/[^>]+>/gis,
      /<[^>]*\bstyle=["'][^"']*["'][^>]*>/gi, // Remove style attributes
      /<[^>]*\bclass=["'][^"']*["'][^>]*>/gi, // Remove class attributes
      /<[^>]*\bid=["'][^"']*["'][^>]*>/gi,    // Remove id attributes
    ];

    unwantedPatterns.forEach(pattern => {
      cleaned = cleaned.replace(pattern, '');
    });

    return cleaned;
  }

  enhancedPostProcessMarkdown(markdown) {
    // Clean up excessive whitespace
    let cleaned = markdown
      .replace(/\n{4,}/g, '\n\n\n') // Replace 4+ newlines with 3 (allowing some breathing room)
      .replace(/[ \t]+$/gm, '') // Remove trailing whitespace
      .replace(/^[ \t]+/gm, '') // Remove leading whitespace except for code blocks
      .trim();

    // Fix spacing around headers
    cleaned = cleaned.replace(/^(#{1,6}\s+.+)$/gm, '\n$1\n');
    cleaned = cleaned.replace(/\n\n(#{1,6}\s+.+)\n\n/g, '\n\n$1\n');

    // Fix spacing around code blocks
    cleaned = cleaned.replace(/([^\n])\n```/g, '$1\n\n```');
    cleaned = cleaned.replace(/```\n([^\n])/g, '```\n\n$1');

    // Fix spacing around blockquotes
    cleaned = cleaned.replace(/([^\n])\n>/g, '$1\n\n>');
    cleaned = cleaned.replace(/>\s*([^>\n].*)\n([^>\n])/g, '> $1\n\n$2');

    // Fix spacing around lists
    cleaned = cleaned.replace(/([^\n])\n[*\-+]\s/g, '$1\n\n- ');
    cleaned = cleaned.replace(/([^\n])\n\d+\.\s/g, '$1\n\n1. ');

    // Fix spacing around horizontal rules
    cleaned = cleaned.replace(/([^\n])\n---/g, '$1\n\n---');
    cleaned = cleaned.replace(/---\n([^\n])/g, '---\n\n$1');

    // Clean up multiple consecutive spaces (but preserve code formatting)
    const lines = cleaned.split('\n');
    const processedLines = lines.map(line => {
      // Don't process lines that are part of code blocks
      if (line.trim().startsWith('```') || line.includes('`')) {
        return line;
      }
      return line.replace(/  +/g, ' ');
    });
    
    cleaned = processedLines.join('\n');

    // Fix link formatting issues
    cleaned = cleaned.replace(/\]\s+\(/g, '](');
    cleaned = cleaned.replace(/\[\s+/g, '[');
    cleaned = cleaned.replace(/\s+\]/g, ']');

    // Fix emphasis formatting
    cleaned = cleaned.replace(/\*\s+/g, '*');
    cleaned = cleaned.replace(/\s+\*/g, '*');
    cleaned = cleaned.replace(/\*\*\s+/g, '**');
    cleaned = cleaned.replace(/\s+\*\*/g, '**');

    // Remove excessive blank lines at start and end
    cleaned = cleaned.replace(/^\n+/, '').replace(/\n+$/, '\n');

    return cleaned;
  }

  // Enhanced fallback conversion for when Turndown is not available
  enhancedHtmlToMarkdown(html) {
    let markdown = html;

    // Enhanced header conversion with better spacing
    markdown = markdown.replace(/<h1[^>]*>(.*?)<\/h1>/gi, '\n# $1\n\n');
    markdown = markdown.replace(/<h2[^>]*>(.*?)<\/h2>/gi, '\n## $1\n\n');
    markdown = markdown.replace(/<h3[^>]*>(.*?)<\/h3>/gi, '\n### $1\n\n');
    markdown = markdown.replace(/<h4[^>]*>(.*?)<\/h4>/gi, '\n#### $1\n\n');
    markdown = markdown.replace(/<h5[^>]*>(.*?)<\/h5>/gi, '\n##### $1\n\n');
    markdown = markdown.replace(/<h6[^>]*>(.*?)<\/h6>/gi, '\n###### $1\n\n');

    // Enhanced paragraph handling
    markdown = markdown.replace(/<p[^>]*>(.*?)<\/p>/gi, '\n$1\n\n');

    // Enhanced code block handling
    markdown = markdown.replace(/<pre[^>]*><code[^>]*>(.*?)<\/code><\/pre>/gis, (match, content) => {
      // Try to detect language from classes
      const langMatch = match.match(/class=["'][^"']*\b(?:language|lang|brush|highlight)-(\w+)/i);
      const language = langMatch ? this.normalizeLanguageName(langMatch[1]) : '';
      
      // Clean and preserve formatting
      const cleanContent = content
        .replace(/<br\s*\/?>/gi, '\n')
        .replace(/<[^>]+>/g, '')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&')
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'");
      
      return `\n\`\`\`${language}\n${cleanContent}\n\`\`\`\n\n`;
    });

    // Handle standalone pre tags
    markdown = markdown.replace(/<pre[^>]*>((?:(?!<\/pre>).)*)<\/pre>/gis, '\n```\n$1\n```\n\n');

    // Enhanced inline code
    markdown = markdown.replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`');

    // Enhanced blockquote handling with nesting
    markdown = markdown.replace(/<blockquote[^>]*>(.*?)<\/blockquote>/gis, (match, content) => {
      const lines = content.trim().split('\n');
      const quotedLines = lines.map(line => `> ${line.trim()}`).join('\n');
      return `\n${quotedLines}\n\n`;
    });

    // Enhanced list handling
    markdown = markdown.replace(/<ul[^>]*>(.*?)<\/ul>/gis, (match, content) => {
      const items = content.match(/<li[^>]*>(.*?)<\/li>/gis) || [];
      const listItems = items.map(item => {
        const text = item.replace(/<li[^>]*>(.*?)<\/li>/gi, '$1').trim();
        return `- ${text}`;
      }).join('\n');
      return `\n${listItems}\n\n`;
    });

    markdown = markdown.replace(/<ol[^>]*>(.*?)<\/ol>/gis, (match, content) => {
      const items = content.match(/<li[^>]*>(.*?)<\/li>/gis) || [];
      const listItems = items.map((item, index) => {
        const text = item.replace(/<li[^>]*>(.*?)<\/li>/gi, '$1').trim();
        return `${index + 1}. ${text}`;
      }).join('\n');
      return `\n${listItems}\n\n`;
    });

    // Enhanced table handling
    markdown = markdown.replace(/<table[^>]*>(.*?)<\/table>/gis, (match, content) => {
      return this.convertTableFromHtml(content);
    });

    // Enhanced link handling
    markdown = markdown.replace(/<a[^>]*href=["']([^"']*)["'][^>]*>(.*?)<\/a>/gi, (match, href, text, offset, string) => {
      // Check if there's a title attribute
      const titleMatch = match.match(/title=["']([^"']*)["']/);
      const title = titleMatch ? titleMatch[1] : '';
      
      let linkMarkdown = `[${text}](${href}`;
      if (title && title !== text) {
        linkMarkdown += ` "${title}"`;
      }
      linkMarkdown += ')';
      
      return linkMarkdown;
    });

    // Enhanced image handling
    markdown = markdown.replace(/<img[^>]*src=["']([^"']*)["'][^>]*>/gi, (match, src) => {
      const altMatch = match.match(/alt=["']([^"']*)["']/);
      const titleMatch = match.match(/title=["']([^"']*)["']/);
      
      const alt = altMatch ? altMatch[1] : '';
      const title = titleMatch ? titleMatch[1] : '';
      
      let imageMarkdown = `![${alt}](${src}`;
      if (title) {
        imageMarkdown += ` "${title}"`;
      }
      imageMarkdown += ')';
      
      return imageMarkdown;
    });

    // Enhanced formatting
    markdown = markdown.replace(/<(strong|b)[^>]*>(.*?)<\/\1>/gi, '**$2**');
    markdown = markdown.replace(/<(em|i)[^>]*>(.*?)<\/\1>/gi, '*$2*');
    markdown = markdown.replace(/<del[^>]*>(.*?)<\/del>/gi, '~~$1~~');
    markdown = markdown.replace(/<mark[^>]*>(.*?)<\/mark>/gi, '==$1==');

    // Handle horizontal rules
    markdown = markdown.replace(/<hr[^>]*>/gi, '\n\n---\n\n');

    // Handle line breaks
    markdown = markdown.replace(/<br\s*\/?>/gi, '  \n');

    // Clean up HTML entities
    markdown = markdown.replace(/&nbsp;/g, ' ');
    markdown = markdown.replace(/&lt;/g, '<');
    markdown = markdown.replace(/&gt;/g, '>');
    markdown = markdown.replace(/&amp;/g, '&');
    markdown = markdown.replace(/&quot;/g, '"');
    markdown = markdown.replace(/&#39;/g, "'");
    markdown = markdown.replace(/&ldquo;/g, '"');
    markdown = markdown.replace(/&rdquo;/g, '"');
    markdown = markdown.replace(/&lsquo;/g, "'");
    markdown = markdown.replace(/&rsquo;/g, "'");
    markdown = markdown.replace(/&mdash;/g, '—');
    markdown = markdown.replace(/&ndash;/g, '–');

    // Remove remaining HTML tags
    markdown = markdown.replace(/<[^>]+>/g, '');

    // Clean up excessive whitespace
    markdown = markdown.replace(/\n\s*\n\s*\n/g, '\n\n');
    markdown = markdown.replace(/^\s+|\s+$/g, '');

    return this.enhancedPostProcessMarkdown(markdown);
  }

  convertTableFromHtml(tableContent) {
    // Extract rows from HTML content
    const rowMatches = tableContent.match(/<tr[^>]*>(.*?)<\/tr>/gis) || [];
    if (rowMatches.length === 0) return '';

    const rows = [];
    let hasHeader = false;

    rowMatches.forEach((rowMatch, index) => {
      const cellMatches = rowMatch.match(/<(th|td)[^>]*>(.*?)<\/\1>/gis) || [];
      const cells = cellMatches.map(cellMatch => {
        const cellContent = cellMatch.replace(/<(th|td)[^>]*>(.*?)<\/\1>/gi, '$2');
        return cellContent.replace(/<[^>]+>/g, '').trim().replace(/\|/g, '\\|');
      });
      
      if (cells.length > 0) {
        rows.push(cells);
        if (index === 0 && rowMatch.includes('<th')) {
          hasHeader = true;
        }
      }
    });

    if (rows.length === 0) return '';

    const markdown = [];
    
    // Add header row
    if (hasHeader || rows.length > 0) {
      const headerRow = rows[0];
      markdown.push(`| ${headerRow.join(' | ')} |`);
      
      // Add separator
      const separator = headerRow.map(() => '---').join(' | ');
      markdown.push(`| ${separator} |`);
      
      // Add remaining rows
      for (let i = 1; i < rows.length; i++) {
        markdown.push(`| ${rows[i].join(' | ')} |`);
      }
    } else {
      // No header, treat first row as header
      rows.forEach(row => {
        markdown.push(`| ${row.join(' | ')} |`);
      });
    }

    return `\n${markdown.join('\n')}\n\n`;
  }

  // Fallback basic conversion for when Turndown fails - now redirects to enhanced version
  basicHtmlToMarkdown(html) {
    return this.enhancedHtmlToMarkdown(html);
  }
}

// For use in service worker context
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MarkdownConverter;
}

// For browser extension context
if (typeof window !== 'undefined') {
  window.MarkdownConverter = MarkdownConverter;
}
