// file-manager.js

function getSharedUtils() {
  if (typeof window !== 'undefined' && window.SharedUtils) {
    return window.SharedUtils;
  }
  if (typeof self !== 'undefined' && self.SharedUtils) {
    return self.SharedUtils;
  }
  if (typeof global !== 'undefined' && global.self && global.self.SharedUtils) {
    return global.self.SharedUtils;
  }
  return null;
}

class FileManager {
  constructor() {
    this.folderMapping = {
      tech: ['programming', 'software', 'coding', 'development', 'technology', 'tech', 'javascript', 'python', 'react', 'node', 'github', 'stackoverflow', 'dev.to'],
      business: ['business', 'marketing', 'finance', 'startup', 'entrepreneur', 'sales', 'management', 'strategy', 'linkedin'],
      tutorial: ['tutorial', 'guide', 'how-to', 'learn', 'course', 'lesson', 'walkthrough', 'step-by-step'],
      news: ['news', 'article', 'blog', 'opinion', 'analysis', 'update', 'announcement'],
      research: ['research', 'study', 'paper', 'academic', 'journal', 'thesis', 'analysis', 'data'],
      design: ['design', 'ui', 'ux', 'css', 'figma', 'adobe', 'creative', 'visual', 'art'],
      tools: ['tool', 'utility', 'software', 'app', 'service', 'platform', 'extension'],
      personal: ['personal', 'diary', 'journal', 'thoughts', 'reflection', 'life', 'experience'],
      reference: ['reference', 'documentation', 'manual', 'spec', 'api', 'docs', 'wiki'],
    };
  }

  /**
   * Generate filename from metadata and settings
   * @param {Object} metadata - Content metadata
   * @param {Object} settings - Settings object with naming patterns
   * @returns {string} - Generated filename
   */
  generateFilename(metadata, settings = {}) {
    const SharedUtils = getSharedUtils();
    if (SharedUtils?.generateFilename) {
      try {
        return SharedUtils.generateFilename(metadata, settings);
      } catch (error) {
        console.warn('SharedUtils.generateFilename failed, using fallback:', error);
      }
    }

    return this._fallbackGenerateFilename(metadata, settings);
  }

  _fallbackGenerateFilename(metadata, settings = {}) {
    // Support both filenamePattern and fileNamingPattern for backward compatibility
    if (settings.filenamePattern || settings.fileNamingPattern) {
      const pattern = settings.filenamePattern || settings.fileNamingPattern;
      let filename = pattern
        .replace('{date}', metadata?.date || new Date().toISOString().split('T')[0])
        .replace('{domain}', this.sanitizeDomain(metadata?.domain))
        .replace('{title}', this.sanitizeTitle(metadata?.title));
      
      if (!filename.endsWith('.md')) {
        filename += '.md';
      }
      return filename;
    }

    const date = metadata?.date || new Date().toISOString().split('T')[0];
    const domain = this.sanitizeDomain(metadata?.domain);
    const title = this.sanitizeTitle(metadata?.title);
    return `${date}-${domain}-${title}.md`;
  }

  sanitizeDomain(domain) {
    const SharedUtils = getSharedUtils();
    return SharedUtils?.sanitizeDomain(domain) || this._fallbackSanitizeDomain(domain);
  }

  _fallbackSanitizeDomain(domain) {
    if (!domain) return 'unknown';
    
    return domain
      .replace(/^(https?:\/\/)?(www\.)?/, '') // Remove protocol and www
      .replace(/\/.*$/, '') // Remove path
      .replace(/[^\w.-]/g, '') // Remove invalid characters
      .toLowerCase()
      .substring(0, 20); // Limit length
  }

  sanitizeTitle(title) {
    const SharedUtils = getSharedUtils();
    return SharedUtils?.sanitizeTitle(title) || this._fallbackSanitizeTitle(title);
  }

  _fallbackSanitizeTitle(title) {
    if (!title) return 'untitled';
    
    return title
      .toLowerCase()
      .replace(/[^\w\s-]/g, '') // Remove special characters except spaces and hyphens
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/-+/g, '-') // Replace multiple hyphens with single
      .substring(0, 50); // Limit length
  }

  determineFolderFromUrl(url, metadata = {}) {
    if (!url) return 'unsorted';
    
    try {
      const urlObj = new URL(url);
      const domain = urlObj.hostname.toLowerCase();
      const path = urlObj.pathname.toLowerCase();
      
      // Check domain-based mapping
      for (const [folder, keywords] of Object.entries(this.folderMapping)) {
        if (keywords.some(keyword => domain.includes(keyword) || path.includes(keyword))) {
          return folder;
        }
      }
      
      // Check content-based mapping if metadata provided
      const text = `${metadata.title || ''} ${metadata.content || ''}`.toLowerCase();
      for (const [folder, keywords] of Object.entries(this.folderMapping)) {
        if (keywords.some(keyword => text.includes(keyword))) {
          return folder;
        }
      }
    } catch (error) {
      console.warn('Error parsing URL for folder determination:', error);
    }
    
    return 'unsorted';
  }

  createFrontmatter(metadata, pageData = {}) {
    const frontmatterData = {
      title: metadata?.title || 'Untitled',
      url: pageData?.url || metadata?.url || '',
      domain: metadata?.domain || '',
      date: metadata?.date || new Date().toISOString().split('T')[0],
      tags: metadata?.tags || [],
      folder: metadata?.folder || 'unsorted'
    };

    // Add optional fields if they exist
    if (metadata?.keywords && metadata?.keywords.length > 0) {
      frontmatterData.keywords = metadata.keywords;
    }
    
    if (metadata?.wordCount) {
      frontmatterData.wordCount = metadata.wordCount;
    }
    
    if (metadata?.readingTime) {
      frontmatterData.readingTime = metadata.readingTime;
    }

    // Convert to YAML, escaping special characters in strings
    let yaml = '---\n';
    for (const [key, value] of Object.entries(frontmatterData)) {
      if (Array.isArray(value)) {
        if (value.length > 0) {
          yaml += `${key}:\n`;
          value.forEach(item => {
            const escapedItem = typeof item === 'string' ? 
              item.replace(/"/g, '\\"').replace(/\n/g, '\\n') : item;
            yaml += `  - "${escapedItem}"\n`;
          });
        } else {
          yaml += `${key}: []\n`;
        }
      } else {
        const escapedValue = typeof value === 'string' ? 
          value.replace(/"/g, '\\"').replace(/\n/g, '\\n') : value;
        yaml += `${key}: "${escapedValue}"\n`;
      }
    }
    yaml += '---\n';
    
    return yaml;
  }

  extractTags(content, metadata = {}) {
    const tags = new Set();
    
    // Add explicit tags if provided
    if (metadata.tags && Array.isArray(metadata.tags)) {
      metadata.tags.forEach(tag => tags.add(tag.toLowerCase()));
    }
    
    // Add domain-based tag
    if (metadata.domain) {
      tags.add(metadata.domain.toLowerCase());
    }
    
    // Extract tags from content
    const text = `${metadata.title || ''} ${content || ''}`.toLowerCase();
    
    // Technology keywords
    const techKeywords = ['javascript', 'python', 'react', 'node', 'css', 'html', 'api', 'database'];
    techKeywords.forEach(keyword => {
      if (text.includes(keyword)) {
        tags.add(keyword);
      }
    });
    
    // Content type keywords
    const contentKeywords = ['tutorial', 'guide', 'review', 'news', 'analysis'];
    contentKeywords.forEach(keyword => {
      if (text.includes(keyword)) {
        tags.add(keyword);
      }
    });
    
    return Array.from(tags).slice(0, 10); // Limit to 10 tags
  }

  /**
   * Classify content into appropriate folder
   * @param {Object} metadata - Content metadata
   * @returns {string} - Folder name
   */
  classifyContent(metadata) {
    if (!metadata) return 'unsorted';
    
    // Check explicit tags first
    if (metadata.tags && Array.isArray(metadata.tags)) {
      for (const tag of metadata.tags) {
        for (const [folder, keywords] of Object.entries(this.folderMapping)) {
          if (keywords.includes(tag.toLowerCase())) {
            return folder;
          }
        }
      }
    }
    
    // Check content-based classification
    const text = `${metadata.title || ''} ${metadata.content || ''} ${metadata.domain || ''}`.toLowerCase();
    
    for (const [folder, keywords] of Object.entries(this.folderMapping)) {
      for (const keyword of keywords) {
        if (text.includes(keyword)) {
          return folder;
        }
      }
    }
    
    return 'unsorted';
  }

  /**
   * Generate metadata for page content
   * @param {Object} pageContent - Page content object
   * @param {Object} settings - Settings object
   * @returns {Object} - Generated metadata
   */
  generateMetadata(pageContent, settings = {}) {
    if (!pageContent) {
      return {
        title: 'Untitled',
        url: '',
        domain: 'unknown',
        date: new Date().toISOString().split('T')[0],
        tags: [],
        folder: 'unsorted',
        wordCount: 0,
        readingTime: '0 min'
      };
    }

    const content = pageContent.textContent || pageContent.content || '';
    const title = pageContent.title || 'Untitled';
    const url = pageContent.url || '';
    const domain = this.sanitizeDomain(pageContent.domain || this._extractDomainFromUrl(url));
    
    // Calculate word count and reading time
    const words = content.split(/\s+/).filter(word => word.length > 0);
    const wordCount = words.length;
    const readingTime = Math.max(1, Math.ceil(wordCount / 200)); // 200 words per minute
    
    const tags = this.extractTags(content, { title, domain, tags: pageContent.tags });
    
    const metadata = {
      title,
      url,
      domain,
      date: new Date().toISOString().split('T')[0],
      tags,
      wordCount,
      readingTime: `${readingTime} min`,
      content: content.substring(0, 500) // Store first 500 chars for classification
    };
    
    metadata.folder = this.classifyContent(metadata);
    
    return metadata;
  }

  _extractDomainFromUrl(url) {
    if (!url) return 'unknown';
    try {
      return new URL(url).hostname;
    } catch {
      return 'unknown';
    }
  }

  /**
   * Create processed content with frontmatter and markdown
   * @param {Object} pageContent - Page content object
   * @param {Object} settings - Settings object
   * @returns {Object} - Processed content with metadata, frontmatter, and content
   */
  createProcessedContent(pageContent, settings = {}) {
    if (!pageContent) {
      return {
        metadata: this.generateMetadata(null, settings),
        frontmatter: '---\ntitle: "Untitled"\n---\n',
        content: '',
        filename: 'untitled.md',
        folder: 'unsorted',
        markdown: '---\ntitle: "Untitled"\n---\n',
        images: [],
        links: []
      };
    }

    const metadata = this.generateMetadata(pageContent, settings);
    const frontmatter = this.createFrontmatter(metadata, pageContent);
    const folder = this.classifyContent(metadata);
    const filename = this.generateFilename(metadata, settings);
    const content = pageContent.markdown || pageContent.textContent || '';
    
    // Extract images and links if available
    const images = pageContent.images || [];
    const links = pageContent.links || [];
    
    let fullContent = frontmatter + '\n' + content;
    
    // Add images to markdown if present
    if (images.length > 0) {
      fullContent += '\n\n## Images\n\n';
      images.forEach(img => {
        fullContent += `![${img.alt || 'Image'}](${img.src})\n\n`;
      });
    }
    
    // Add links to markdown if present  
    if (links.length > 0) {
      fullContent += '\n\n## Links\n\n';
      links.forEach(link => {
        fullContent += `[${link.text || 'Link'}](${link.href})\n\n`;
      });
    }

    return {
      metadata,
      frontmatter,
      content,
      filename,
      folder,
      fullContent,
      path: `${folder}/${filename}`,
      markdown: fullContent, // For backward compatibility
      images,
      links
    };
  }

  /**
   * Organize multiple files into folder structure
   * @param {Array} contents - Array of content objects
   * @returns {Object} - Organization structure with folders and files
   */
  organizeFiles(contents) {
    if (!Array.isArray(contents)) {
      return { folders: {}, totalFiles: 0 };
    }

    const organized = {
      folders: {},
      totalFiles: 0
    };

    contents.forEach(content => {
      let processed;
      
      // Handle both raw content and pre-processed content
      if (content.metadata && content.folder) {
        processed = content;
      } else {
        processed = this.createProcessedContent(content);
      }

      const folder = processed.folder || 'unsorted';
      
      if (!organized.folders[folder]) {
        organized.folders[folder] = [];
      }
      
      organized.folders[folder].push(processed);
      organized.totalFiles++;
    });

    return organized;
  }

  ensureUniqueFilenames(contents) {
    if (!Array.isArray(contents)) {
      return [];
    }

    const usedFilenames = new Set();
    
    return contents.map(content => {
      let filename = content.filename;
      let counter = 1;
      
      while (usedFilenames.has(filename)) {
        const baseName = filename.replace(/\.md$/, '');
        filename = `${baseName}-${counter}.md`;
        counter++;
      }
      
      usedFilenames.add(filename);
      
      return {
        ...content,
        filename,
        path: `${content.folder}/${filename}`
      };
    });
  }

  /**
   * Generate full file path for content
   * @param {Object} metadata - Content metadata
   * @param {Object} settings - Settings object
   * @returns {string} - Full file path
   */
  generateFilePath(metadata, settings = {}) {
    if (!metadata) {
      return 'documents/unsorted/untitled.md';
    }

    const folder = this.classifyContent(metadata);
    const filename = this.generateFilename(metadata, settings);
    
    // Handle root folder (empty folder) case
    if (!folder || folder === '') {
      return `documents/${filename}`;
    }
    
    return `documents/${folder}/${filename}`;
  }

  /**
   * Generate path for image files
   * @param {string} imageName - Image filename
   * @param {Date|string} date - Date for organization
   * @returns {string} - Image file path
   */
  generateImagePath(imageName, date = null) {
    if (!imageName) {
      return 'images/untitled.jpg';
    }

    const now = date ? new Date(date) : new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    
    const sanitizedName = imageName.replace(/[^\w\-_.]/g, '-').replace(/--+/g, '-');
    
    return `images/${year}/${month}/${sanitizedName}`;
  }

  validateFilename(filename) {
    const SharedUtils = getSharedUtils();
    return SharedUtils?.validateFilename(filename) || this._fallbackValidateFilename(filename);
  }

  _fallbackValidateFilename(filename) {
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
      errors,
    };
  }

  getFileExtension(filename) {
    const SharedUtils = getSharedUtils();
    return SharedUtils?.getFileExtension(filename) || this._fallbackGetFileExtension(filename);
  }

  _fallbackGetFileExtension(filename) {
    if (!filename) return '';
    const lastDot = filename.lastIndexOf('.');
    return lastDot !== -1 ? filename.slice(lastDot) : '';
  }

  isMarkdownFile(filename) {
    return this.getFileExtension(filename) === '.md';
  }

  generateUniqueFilename(baseFilename, existingFiles = []) {
    const SharedUtils = getSharedUtils();
    return SharedUtils?.generateUniqueFilename(baseFilename, existingFiles) || 
           this._fallbackGenerateUniqueFilename(baseFilename, existingFiles);
  }

  _fallbackGenerateUniqueFilename(baseFilename, existingFiles = []) {
    if (!existingFiles.includes(baseFilename)) {
      return baseFilename;
    }

    const baseName = baseFilename.replace(/\.md$/, '');
    let counter = 1;
    let newFilename;

    do {
      newFilename = `${baseName}-${counter}.md`;
      counter++;
    } while (existingFiles.includes(newFilename));

    return newFilename;
  }

  getDateFromFilename(filename) {
    const SharedUtils = getSharedUtils();
    return SharedUtils?.getDateFromFilename(filename) || this._fallbackGetDateFromFilename(filename);
  }

  _fallbackGetDateFromFilename(filename) {
    const dateMatch = filename.match(/(\d{4}-\d{2}-\d{2})/);
    return dateMatch ? dateMatch[1] : null;
  }

  getTopLevelFolders() {
    return Object.keys(this.folderMapping);
  }

  suggestFolder(content, metadata = {}) {
    if (!content && !metadata) {
      return 'unsorted';
    }

    const combinedMetadata = {
      ...metadata,
      content: content || metadata.content || ''
    };

    return this.classifyContent(combinedMetadata);
  }
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FileManager;
} else if (typeof window !== 'undefined') {
  window.FileManager = FileManager;
} else if (typeof self !== 'undefined') {
  self.FileManager = FileManager;
}
