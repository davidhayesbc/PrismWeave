// PrismWeave File Management
// Utilities for file naming, organization, and metadata handling

class FileManager {
  constructor() {
    this.folderMapping = {
      'tech': ['technology', 'programming', 'software', 'development', 'coding', 'github', 'stackoverflow'],
      'business': ['business', 'finance', 'marketing', 'startup', 'entrepreneur', 'economy'],
      'research': ['research', 'academic', 'paper', 'study', 'science', 'journal'],
      'news': ['news', 'breaking', 'current', 'politics', 'world'],
      'tutorial': ['tutorial', 'howto', 'guide', 'learn', 'course', 'training'],
      'reference': ['documentation', 'docs', 'reference', 'api', 'manual'],
      'blog': ['blog', 'personal', 'opinion', 'thoughts', 'medium'],
      'social': ['twitter', 'facebook', 'linkedin', 'social', 'reddit']
    };
  }

  generateFilename(metadata, settings = {}) {
    const pattern = settings.fileNamingPattern || 'YYYY-MM-DD-domain-title';
    const date = new Date(metadata.timestamp || Date.now());
    const domain = this.sanitizeDomain(metadata.domain);
    const title = this.sanitizeTitle(metadata.title);
    
    let filename = pattern;
    
    // Replace date patterns
    filename = filename.replace('YYYY', date.getFullYear().toString());
    filename = filename.replace('MM', (date.getMonth() + 1).toString().padStart(2, '0'));
    filename = filename.replace('DD', date.getDate().toString().padStart(2, '0'));
    
    // Replace domain and title
    filename = filename.replace('domain', domain);
    filename = filename.replace('title', title);
    
    // Ensure .md extension
    if (!filename.endsWith('.md')) {
      filename += '.md';
    }
    
    return filename;
  }

  sanitizeDomain(domain) {
    if (!domain) return 'unknown';
    
    return domain
      .toLowerCase()
      .replace(/^www\./, '') // Remove www.
      .replace(/[^a-z0-9.-]/g, '') // Keep only alphanumeric, dots, and hyphens
      .substring(0, 20); // Limit length
  }

  sanitizeTitle(title) {
    if (!title) return 'untitled';
    
    return title
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/-+/g, '-') // Replace multiple hyphens with single
      .replace(/^-|-$/g, '') // Remove leading/trailing hyphens
      .substring(0, 50); // Limit length
  }

  determineFolderFromUrl(url, metadata = {}) {
    try {
      const urlObj = new URL(url);
      const domain = urlObj.hostname.toLowerCase();
      const pathname = urlObj.pathname.toLowerCase();
      const title = (metadata.title || '').toLowerCase();
      const description = (metadata.description || '').toLowerCase();
      
      // Check domain-specific mappings first
      for (const [folder, keywords] of Object.entries(this.folderMapping)) {
        if (keywords.some(keyword => 
          domain.includes(keyword) || 
          pathname.includes(keyword) || 
          title.includes(keyword) ||
          description.includes(keyword)
        )) {
          return folder;
        }
      }
      
      // Check specific domain patterns
      if (domain.includes('github.com')) return 'tech';
      if (domain.includes('stackoverflow.com')) return 'tech';
      if (domain.includes('medium.com')) return 'blog';
      if (domain.includes('news') || domain.includes('cnn') || domain.includes('bbc')) return 'news';
      if (domain.includes('wikipedia.org')) return 'reference';
      if (domain.includes('youtube.com') && pathname.includes('watch')) return 'tutorial';
      
      // Check URL path patterns
      if (pathname.includes('/blog/')) return 'blog';
      if (pathname.includes('/news/')) return 'news';
      if (pathname.includes('/tutorial/') || pathname.includes('/guide/')) return 'tutorial';
      if (pathname.includes('/docs/') || pathname.includes('/documentation/')) return 'reference';
      
      return 'unsorted';
    } catch (error) {
      return 'unsorted';
    }
  }

  createFrontmatter(metadata, pageData = {}) {
    const frontmatter = {
      title: metadata.title || 'Untitled',
      source_url: metadata.url,
      domain: metadata.domain,
      captured_date: metadata.timestamp || new Date().toISOString(),
      tags: this.generateTags(metadata, pageData),
      summary: this.generateSummary(pageData),
      reading_time: pageData.readingTime || 0,
      word_count: pageData.wordCount || 0,
      quality_score: pageData.quality?.score || 0
    };

    // Add optional metadata if available
    if (metadata.author) frontmatter.author = metadata.author;
    if (metadata.published_time) frontmatter.published_date = metadata.published_time;
    if (metadata.section) frontmatter.category = metadata.section;
    if (metadata.language && metadata.language !== 'en') frontmatter.language = metadata.language;

    return this.formatFrontmatter(frontmatter);
  }

  formatFrontmatter(data) {
    let yaml = '---\n';
    
    for (const [key, value] of Object.entries(data)) {
      if (value === null || value === undefined) continue;
      
      if (Array.isArray(value)) {
        if (value.length > 0) {
          yaml += `${key}:\n`;
          value.forEach(item => {
            yaml += `  - "${this.escapeYaml(item)}"\n`;
          });
        } else {
          yaml += `${key}: []\n`;
        }
      } else if (typeof value === 'string') {
        yaml += `${key}: "${this.escapeYaml(value)}"\n`;
      } else {
        yaml += `${key}: ${value}\n`;
      }
    }
    
    yaml += '---';
    return yaml;
  }

  escapeYaml(str) {
    if (typeof str !== 'string') return str;
    return str.replace(/"/g, '\\"').replace(/\n/g, '\\n');
  }

  generateTags(metadata, pageData = {}) {
    const tags = new Set();
    
    // Extract from URL domain
    const domain = metadata.domain;
    if (domain) {
      const domainParts = domain.split('.');
      domainParts.forEach(part => {
        if (part.length > 2 && part !== 'com' && part !== 'org' && part !== 'net') {
          tags.add(part);
        }
      });
    }
    
    // Extract from metadata keywords
    if (metadata.keywords) {
      metadata.keywords.split(',').forEach(keyword => {
        const clean = keyword.trim().toLowerCase();
        if (clean.length > 2) tags.add(clean);
      });
    }
    
    // Extract from title and description
    const text = `${metadata.title || ''} ${metadata.description || ''}`.toLowerCase();
    const commonTags = [
      'javascript', 'python', 'react', 'node', 'api', 'tutorial', 'guide',
      'technology', 'programming', 'development', 'business', 'marketing',
      'startup', 'ai', 'machine learning', 'data science', 'web development'
    ];
    
    commonTags.forEach(tag => {
      if (text.includes(tag.toLowerCase())) {
        tags.add(tag);
      }
    });
    
    // Limit to most relevant tags
    return Array.from(tags).slice(0, 10);
  }

  generateSummary(pageData = {}) {
    if (!pageData.textContent) return '';
    
    const text = pageData.textContent.trim();
    if (text.length <= 200) return text;
    
    // Find the first meaningful paragraph
    const paragraphs = text.split('\n\n').filter(p => p.trim().length > 50);
    if (paragraphs.length > 0) {
      const firstParagraph = paragraphs[0].trim();
      if (firstParagraph.length <= 200) return firstParagraph;
      
      // Truncate at sentence boundary
      const sentences = firstParagraph.split(/[.!?]+/);
      let summary = '';
      for (const sentence of sentences) {
        if ((summary + sentence).length > 180) break;
        summary += sentence + '.';
      }
      return summary.trim();
    }
    
    // Fallback: truncate at word boundary
    const words = text.split(' ');
    let summary = '';
    for (const word of words) {
      if ((summary + ' ' + word).length > 180) break;
      summary += ' ' + word;
    }
    return summary.trim() + '...';
  }

  validateFilename(filename) {
    const errors = [];
    
    if (!filename) {
      errors.push('Filename cannot be empty');
      return { valid: false, errors };
    }
    
    if (filename.length > 100) {
      errors.push('Filename too long (max 100 characters)');
    }
    
    if (!/\.md$/.test(filename)) {
      errors.push('Filename must end with .md');
    }
    
    if (/[<>:"/\\|?*]/.test(filename)) {
      errors.push('Filename contains invalid characters');
    }
    
    if (/^\s|\s$/.test(filename)) {
      errors.push('Filename cannot start or end with whitespace');
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }

  getFileExtension(filename) {
    const match = filename.match(/\.([a-zA-Z0-9]+)$/);
    return match ? match[1].toLowerCase() : '';
  }

  isMarkdownFile(filename) {
    return this.getFileExtension(filename) === 'md';
  }

  generateUniqueFilename(baseFilename, existingFiles = []) {
    if (!existingFiles.includes(baseFilename)) {
      return baseFilename;
    }
    
    const extension = this.getFileExtension(baseFilename);
    const nameWithoutExt = baseFilename.substring(0, baseFilename.length - extension.length - 1);
    
    let counter = 1;
    let newFilename;
    
    do {
      newFilename = `${nameWithoutExt}-${counter}.${extension}`;
      counter++;
    } while (existingFiles.includes(newFilename));
    
    return newFilename;
  }

  getDateFromFilename(filename) {
    const dateMatch = filename.match(/(\d{4}-\d{2}-\d{2})/);
    if (dateMatch) {
      return new Date(dateMatch[1]);
    }
    return null;
  }

  getTopLevelFolders() {
    return Object.keys(this.folderMapping).concat(['unsorted', 'generated']);
  }

  suggestFolder(content, metadata = {}) {
    // Use the URL-based determination as primary method
    const urlBasedFolder = this.determineFolderFromUrl(metadata.url || '', metadata);
    
    if (urlBasedFolder !== 'unsorted') {
      return urlBasedFolder;
    }
    
    // Fallback: analyze content
    const text = (content || '').toLowerCase();
    const title = (metadata.title || '').toLowerCase();
    
    for (const [folder, keywords] of Object.entries(this.folderMapping)) {
      if (keywords.some(keyword => text.includes(keyword) || title.includes(keyword))) {
        return folder;
      }
    }
    
    return 'unsorted';
  }
}

// For use in service worker context
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FileManager;
}

// For browser extension context
if (typeof window !== 'undefined') {
  window.FileManager = FileManager;
}
