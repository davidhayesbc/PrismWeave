// DocTracker Markdown Converter
// Enhanced HTML to Markdown conversion using Turndown.js

class MarkdownConverter {
  constructor() {
    this.turndownService = null;
    this.initializeTurndown();
  }
  initializeTurndown() {
    // Check if TurndownService is available (from imported library)
    if (typeof TurndownService === 'undefined') {
      console.warn('TurndownService not available, using fallback conversion');
      this.turndownService = null;
      return;
    }

    // Initialize Turndown service with custom rules
    this.turndownService = new TurndownService({
      headingStyle: 'atx',
      bulletListMarker: '-',
      codeBlockStyle: 'fenced',
      emDelimiter: '*',
      strongDelimiter: '**',
      linkStyle: 'inlined',
      linkReferenceStyle: 'full'
    });

    // Add custom rules for better conversion
    this.addCustomRules();
  }
  addCustomRules() {
    if (!this.turndownService) return;

    // Remove unwanted elements
    this.turndownService.addRule('removeUnwanted', {
      filter: ['script', 'style', 'nav', 'header', 'footer', 'aside', 'form'],
      replacement: () => ''
    });

    // Handle code blocks better
    this.turndownService.addRule('codeBlocks', {
      filter: ['pre'],
      replacement: (content, node) => {
        const code = node.querySelector('code');
        const language = code ? this.extractLanguage(code) : '';
        return `\n\`\`\`${language}\n${content}\n\`\`\`\n\n`;
      }
    });

    // Handle blockquotes
    this.turndownService.addRule('blockquotes', {
      filter: 'blockquote',
      replacement: (content) => {
        return content
          .trim()
          .split('\n')
          .map(line => `> ${line}`)
          .join('\n') + '\n\n';
      }
    });

    // Handle tables better
    this.turndownService.addRule('tables', {
      filter: 'table',
      replacement: (content, node) => {
        return this.convertTable(node);
      }
    });

    // Handle images with better alt text
    this.turndownService.addRule('images', {
      filter: 'img',
      replacement: (content, node) => {
        const alt = node.getAttribute('alt') || '';
        const src = node.getAttribute('src') || '';
        const title = node.getAttribute('title');
        
        if (!src) return '';
        
        let imageMarkdown = `![${alt}](${src}`;
        if (title) {
          imageMarkdown += ` "${title}"`;
        }
        imageMarkdown += ')';
        
        return imageMarkdown;
      }
    });
  }

  extractLanguage(codeElement) {
    const className = codeElement.className || '';
    const languageMatch = className.match(/language-(\w+)/);
    return languageMatch ? languageMatch[1] : '';
  }

  convertTable(tableNode) {
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
      // Clean the HTML before conversion
      const cleanedHtml = this.cleanHtml(html);
      
      // Convert to markdown using Turndown if available, otherwise use fallback
      let markdown;
      if (this.turndownService) {
        markdown = this.turndownService.turndown(cleanedHtml);
      } else {
        markdown = this.basicHtmlToMarkdown(cleanedHtml);
      }
      
      // Post-process the markdown
      return this.postProcessMarkdown(markdown);
    } catch (error) {
      console.error('Markdown conversion failed:', error);
      // Fallback to basic conversion
      return this.basicHtmlToMarkdown(html);
    }
  }

  cleanHtml(html) {
    // Create a temporary DOM element to clean the HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;

    // Remove ads and unwanted content
    const unwantedSelectors = [
      '.ad', '.advertisement', '.ads', '.sponsored',
      '.sidebar', '.nav', '.navigation', '.menu',
      '.footer', '.header', '.banner',
      '[class*="ad-"]', '[id*="ad-"]',
      '.social-share', '.social-buttons',
      '.newsletter', '.subscription',
      '.comments', '.comment-section',
      '.related-articles', '.recommendations'
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

  postProcessMarkdown(markdown) {
    // Clean up excessive whitespace
    let cleaned = markdown
      .replace(/\n{3,}/g, '\n\n')  // Replace 3+ newlines with 2
      .replace(/[ \t]+$/gm, '')    // Remove trailing whitespace
      .trim();

    // Ensure proper spacing around headers
    cleaned = cleaned.replace(/^(#{1,6}\s+.+)$/gm, '\n$1\n');
    
    // Ensure proper spacing around code blocks
    cleaned = cleaned.replace(/```[\s\S]*?```/g, (match) => `\n${match}\n`);
    
    // Clean up multiple consecutive spaces
    cleaned = cleaned.replace(/  +/g, ' ');
    
    return cleaned;
  }

  // Fallback basic conversion for when Turndown fails
  basicHtmlToMarkdown(html) {
    let markdown = html;
    
    // Headers
    markdown = markdown.replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n\n');
    markdown = markdown.replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n\n');
    markdown = markdown.replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n\n');
    markdown = markdown.replace(/<h4[^>]*>(.*?)<\/h4>/gi, '#### $1\n\n');
    markdown = markdown.replace(/<h5[^>]*>(.*?)<\/h5>/gi, '##### $1\n\n');
    markdown = markdown.replace(/<h6[^>]*>(.*?)<\/h6>/gi, '###### $1\n\n');
    
    // Paragraphs
    markdown = markdown.replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n');
    
    // Links
    markdown = markdown.replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '[$2]($1)');
    
    // Bold and italic
    markdown = markdown.replace(/<strong[^>]*>(.*?)<\/strong>/gi, '**$1**');
    markdown = markdown.replace(/<b[^>]*>(.*?)<\/b>/gi, '**$1**');
    markdown = markdown.replace(/<em[^>]*>(.*?)<\/em>/gi, '*$1*');
    markdown = markdown.replace(/<i[^>]*>(.*?)<\/i>/gi, '*$1*');
    
    // Images
    markdown = markdown.replace(/<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>/gi, '![$2]($1)');
    markdown = markdown.replace(/<img[^>]*src="([^"]*)"[^>]*>/gi, '![]($1)');
    
    // Clean up HTML tags
    markdown = markdown.replace(/<[^>]+>/g, '');
    markdown = markdown.replace(/\n\s*\n\s*\n/g, '\n\n');
    
    return markdown.trim();
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
