// PrismWeave File Management
// Utilities for file naming, organization, and metadata handling

// SharedUtils will be available globally after importScripts loads shared-utils.js
function getSharedUtils() {
  const globalScope = typeof window !== 'undefined' ? window : self;
  return globalScope.SharedUtils || null;
}

class FileManager {
  constructor() {
    this.folderMapping = {
      tech: [
        'technology',
        'programming',
        'software',
        'development',
        'coding',
        'github',
        'stackoverflow',
      ],
      business: ['business', 'finance', 'marketing', 'startup', 'entrepreneur', 'economy'],
      research: ['research', 'academic', 'paper', 'study', 'science', 'journal'],
      news: ['news', 'breaking', 'current', 'politics', 'world'],
      tutorial: ['tutorial', 'howto', 'guide', 'learn', 'course', 'training'],
      reference: ['documentation', 'docs', 'reference', 'api', 'manual'],
      blog: ['blog', 'personal', 'opinion', 'thoughts', 'medium'],
      social: ['twitter', 'facebook', 'linkedin', 'social', 'reddit'],
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
    const SharedUtils = getSharedUtils();
    return SharedUtils?.sanitizeDomain(domain) || this._fallbackSanitizeDomain(domain);
  }

  _fallbackSanitizeDomain(domain) {
    if (!domain) return 'unknown';

    // Remove common TLDs and subdomains, replace dots with hyphens
    let sanitized = domain
      .toLowerCase()
      .replace(/^www\./, '')  // Remove www.
      .replace(/\.(com|org|net|co\.uk|io|dev|app)$/, '')  // Remove common TLDs
      .replace(/\./g, '-')  // Replace dots with hyphens
      .replace(/[^a-z0-9-]/g, '')  // Keep only alphanumeric and hyphens
      .substring(0, 20); // Limit length
    
    return sanitized;
  }

  sanitizeTitle(title) {
    const SharedUtils = getSharedUtils();
    return SharedUtils?.sanitizeForFilename(title) || this._fallbackSanitizeTitle(title);
  }

  _fallbackSanitizeTitle(title) {
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
        if (
          keywords.some(
            keyword =>
              domain.includes(keyword) ||
              pathname.includes(keyword) ||
              title.includes(keyword) ||
              description.includes(keyword)
          )
        ) {
          return folder;
        }
      }

      // Check specific domain patterns
      if (domain.includes('github.com')) return 'tech';
      if (domain.includes('stackoverflow.com')) return 'tech';
      if (domain.includes('medium.com')) return 'blog';
      if (domain.includes('news') || domain.includes('cnn') || domain.includes('bbc'))
        return 'news';
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
      quality_score: pageData.quality?.score || 0,
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
    const SharedUtils = getSharedUtils();
    return SharedUtils?.escapeYaml(str) || this._fallbackEscapeYaml(str);
  }

  _fallbackEscapeYaml(str) {
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
      const keywordsArray = Array.isArray(metadata.keywords) 
        ? metadata.keywords 
        : metadata.keywords.split(',');
      
      keywordsArray.forEach(keyword => {
        const clean = (keyword || '').toString().trim().toLowerCase();
        if (clean.length > 2) tags.add(clean);
      });
    }

    // Extract from title and description
    const text = `${metadata.title || ''} ${metadata.description || ''}`.toLowerCase();
    const commonTags = [
      'javascript',
      'python',
      'react',
      'node',
      'api',
      'tutorial',
      'guide',
      'technology',
      'programming',
      'development',
      'business',
      'marketing',
      'startup',
      'ai',
      'machine learning',
      'data science',
      'web development',
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
    const match = filename.match(/\.([a-zA-Z0-9]+)$/);
    return match ? match[1].toLowerCase() : '';
  }

  isMarkdownFile(filename) {
    const SharedUtils = getSharedUtils();
    return SharedUtils?.isMarkdownFile(filename) || this.getFileExtension(filename) === 'md';
  }

  generateUniqueFilename(baseFilename, existingFiles = []) {
    const SharedUtils = getSharedUtils();
    return (
      SharedUtils?.generateUniqueFilename(baseFilename, existingFiles) ||
      this._fallbackGenerateUniqueFilename(baseFilename, existingFiles)
    );
  }

  _fallbackGenerateUniqueFilename(baseFilename, existingFiles = []) {
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
    const SharedUtils = getSharedUtils();
    return (
      SharedUtils?.getDateFromFilename(filename) || this._fallbackGetDateFromFilename(filename)
    );
  }

  _fallbackGetDateFromFilename(filename) {
    const dateMatch = filename.match(/(\d{4}-\d{2}-\d{2})/);
    return dateMatch ? new Date(dateMatch[1]) : null;
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

  /**
   * Suggest a folder based on content and metadata
   * @param {string} textContent - The text content of the page
   * @param {Object} metadata - Page metadata
   * @returns {string} - Suggested folder name
   */
  suggestFolder(textContent, metadata = {}) {
    // Use the existing folder determination logic
    return this.determineFolderFromUrl(metadata.url || '', metadata);
  }

  /**
   * Classify content into appropriate folder based on metadata and content
   * @param {Object} metadata - Page metadata including title, description, keywords, tags
   * @returns {string} - Folder classification
   */
  classifyContent(metadata) {
    if (!metadata) return 'unsorted';

    // Check URL-based classification first
    if (metadata.url) {
      const urlFolder = this.determineFolderFromUrl(metadata.url, metadata);
      if (urlFolder !== 'unsorted') {
        return urlFolder;
      }
    }

    // Check tags for direct matches
    if (metadata.tags && Array.isArray(metadata.tags)) {
      for (const tag of metadata.tags) {
        const tagLower = tag.toLowerCase();
        for (const [folder, keywords] of Object.entries(this.folderMapping)) {
          if (keywords.includes(tagLower)) {
            return folder;
          }
        }
      }
    }

    // Check title and description
    const text = `${metadata.title || ''} ${metadata.description || ''}`.toLowerCase();
    for (const [folder, keywords] of Object.entries(this.folderMapping)) {
      if (keywords.some(keyword => text.includes(keyword))) {
        return folder;
      }
    }

    // Check keywords
    if (metadata.keywords && Array.isArray(metadata.keywords)) {
      for (const keyword of metadata.keywords) {
        const keywordLower = keyword.toLowerCase();
        for (const [folder, keywords] of Object.entries(this.folderMapping)) {
          if (keywords.some(k => keywordLower.includes(k) || k.includes(keywordLower))) {
            return folder;
          }
        }
      }
    }

    return 'unsorted';
  }

  /**
   * Generate metadata from page content
   * @param {Object} pageContent - Page content object with url, title, textContent, etc.
   * @param {Object} settings - Settings object
   * @returns {Object} - Generated metadata
   */
  generateMetadata(pageContent, settings = {}) {
    if (!pageContent) {
      return {
        title: 'Untitled',
        url: '',
        domain: '',
        timestamp: new Date().toISOString(),
        tags: [],
        description: '',
        summary: ''
      };
    }

    const metadata = {
      title: pageContent.title || 'Untitled',
      url: pageContent.url || '',
      domain: pageContent.url ? this.sanitizeDomain(new URL(pageContent.url).hostname) : '',
      timestamp: new Date().toISOString(),
      description: pageContent.description || '',
      author: pageContent.author || '',
      keywords: pageContent.keywords || [],
      tags: this.generateTags({ 
        title: pageContent.title, 
        description: pageContent.description,
        keywords: pageContent.keywords 
      }, pageContent),
      summary: this.generateSummary(pageContent),
      wordCount: pageContent.textContent ? pageContent.textContent.split(/\s+/).length : 0,
      readingTime: pageContent.textContent ? Math.ceil(pageContent.textContent.split(/\s+/).length / 200) : 0
    };

    // Add custom metadata from settings
    if (settings.customMetadata) {
      Object.assign(metadata, settings.customMetadata);
    }

    return metadata;
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
        folder: 'unsorted'
      };
    }

    const metadata = this.generateMetadata(pageContent, settings);
    const frontmatter = this.createFrontmatter(metadata, pageContent);
    const folder = this.classifyContent(metadata);
    const filename = this.generateFilename(metadata, settings);

    return {
      metadata,
      frontmatter,
      content: pageContent.markdown || pageContent.textContent || '',
      filename,
      folder,
      fullContent: frontmatter + '\n' + (pageContent.markdown || pageContent.textContent || ''),
      path: `${folder}/${filename}`
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

    const organization = {
      folders: {},
      totalFiles: contents.length,
      byFolder: {}
    };

    contents.forEach(content => {
      const processed = typeof content === 'object' && content.folder 
        ? content 
        : this.createProcessedContent(content);
      
      const folder = processed.folder || 'unsorted';
      
      if (!organization.folders[folder]) {
        organization.folders[folder] = [];
        organization.byFolder[folder] = 0;
      }
      
      organization.folders[folder].push(processed);
      organization.byFolder[folder]++;
    });

    return organization;
  }

  /**
   * Ensure all filenames in a collection are unique
   * @param {Array} contents - Array of content objects with filename property
   * @returns {Array} - Contents with unique filenames
   */
  ensureUniqueFilenames(contents) {
    if (!Array.isArray(contents)) {
      return [];
    }

    const usedFilenames = new Set();
    const processedContents = [];

    contents.forEach(content => {
      let filename = content.filename || 'untitled.md';
      
      // Generate unique filename if needed
      if (usedFilenames.has(filename)) {
        const extension = this.getFileExtension(filename);
        const nameWithoutExt = filename.substring(0, filename.length - extension.length - 1);
        let counter = 1;
        
        do {
          filename = `${nameWithoutExt}-${counter}.${extension}`;
          counter++;
        } while (usedFilenames.has(filename));
      }
      
      usedFilenames.add(filename);
      
      processedContents.push({
        ...content,
        filename,
        originalFilename: content.filename
      });
    });

    return processedContents;
  }

  /**
   * Generate full file path for content
   * @param {Object} metadata - Content metadata
   * @param {Object} settings - Settings object
   * @returns {string} - Full file path
   */
  generateFilePath(metadata, settings = {}) {
    if (!metadata) {
      return 'unsorted/untitled.md';
    }

    const folder = this.classifyContent(metadata);
    const filename = this.generateFilename(metadata, settings);
    return `${folder}/${filename}`;
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

    const dateObj = date ? new Date(date) : new Date();
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    
    // Sanitize image name
    const sanitizedName = imageName.replace(/[^\w\-_.]/g, '-').replace(/--+/g, '-');
    
    return `images/${year}/${month}/${sanitizedName}`;
  }

  /**
   * Suggest a folder based on content and metadata
   * @param {string} textContent - The text content of the page
   * @param {Object} metadata - Page metadata
   * @returns {string} - Suggested folder name
   */
  suggestFolder(textContent, metadata = {}) {
    // Use the existing folder determination logic
    return this.determineFolderFromUrl(metadata.url || '', metadata);
  }

  /**
   * Classify content into appropriate folder based on metadata and content
   * @param {Object} metadata - Page metadata including title, description, keywords, tags
   * @returns {string} - Folder classification
   */
  classifyContent(metadata) {
    if (!metadata) return 'unsorted';

    // Check URL-based classification first
    if (metadata.url) {
      const urlFolder = this.determineFolderFromUrl(metadata.url, metadata);
      if (urlFolder !== 'unsorted') {
        return urlFolder;
      }
    }

    // Check tags for direct matches
    if (metadata.tags && Array.isArray(metadata.tags)) {
      for (const tag of metadata.tags) {
        const tagLower = tag.toLowerCase();
        for (const [folder, keywords] of Object.entries(this.folderMapping)) {
          if (keywords.includes(tagLower)) {
            return folder;
          }
        }
      }
    }

    // Check title and description
    const text = `${metadata.title || ''} ${metadata.description || ''}`.toLowerCase();
    for (const [folder, keywords] of Object.entries(this.folderMapping)) {
      if (keywords.some(keyword => text.includes(keyword))) {
        return folder;
      }
    }

    // Check keywords
    if (metadata.keywords && Array.isArray(metadata.keywords)) {
      for (const keyword of metadata.keywords) {
        const keywordLower = keyword.toLowerCase();
        for (const [folder, keywords] of Object.entries(this.folderMapping)) {
          if (keywords.some(k => keywordLower.includes(k) || k.includes(keywordLower))) {
            return folder;
          }
        }
      }
    }

    return 'unsorted';
  }

  /**
   * Generate metadata from page content
   * @param {Object} pageContent - Page content object with url, title, textContent, etc.
   * @param {Object} settings - Settings object
   * @returns {Object} - Generated metadata
   */
  generateMetadata(pageContent, settings = {}) {
    if (!pageContent) {
      return {
        title: 'Untitled',
        url: '',
        domain: '',
        timestamp: new Date().toISOString(),
        tags: [],
        description: '',
        summary: ''
      };
    }

    const metadata = {
      title: pageContent.title || 'Untitled',
      url: pageContent.url || '',
      domain: pageContent.url ? this.sanitizeDomain(new URL(pageContent.url).hostname) : '',
      timestamp: new Date().toISOString(),
      description: pageContent.description || '',
      author: pageContent.author || '',
      keywords: pageContent.keywords || [],
      tags: this.generateTags({ 
        title: pageContent.title, 
        description: pageContent.description,
        keywords: pageContent.keywords 
      }, pageContent),
      summary: this.generateSummary(pageContent),
      wordCount: pageContent.textContent ? pageContent.textContent.split(/\s+/).length : 0,
      readingTime: pageContent.textContent ? Math.ceil(pageContent.textContent.split(/\s+/).length / 200) : 0
    };

    // Add custom metadata from settings
    if (settings.customMetadata) {
      Object.assign(metadata, settings.customMetadata);
    }

    return metadata;
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
        folder: 'unsorted'
      };
    }

    const metadata = this.generateMetadata(pageContent, settings);
    const frontmatter = this.createFrontmatter(metadata, pageContent);
    const folder = this.classifyContent(metadata);
    const filename = this.generateFilename(metadata, settings);

    return {
      metadata,
      frontmatter,
      content: pageContent.markdown || pageContent.textContent || '',
      filename,
      folder,
      fullContent: frontmatter + '\n' + (pageContent.markdown || pageContent.textContent || ''),
      path: `${folder}/${filename}`
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

    const organization = {
      folders: {},
      totalFiles: contents.length,
      byFolder: {}
    };

    contents.forEach(content => {
      const processed = typeof content === 'object' && content.folder 
        ? content 
        : this.createProcessedContent(content);
      
      const folder = processed.folder || 'unsorted';
      
      if (!organization.folders[folder]) {
        organization.folders[folder] = [];
        organization.byFolder[folder] = 0;
      }
      
      organization.folders[folder].push(processed);
      organization.byFolder[folder]++;
    });

    return organization;
  }

  /**
   * Ensure all filenames in a collection are unique
   * @param {Array} contents - Array of content objects with filename property
   * @returns {Array} - Contents with unique filenames
   */
  ensureUniqueFilenames(contents) {
    if (!Array.isArray(contents)) {
      return [];
    }

    const usedFilenames = new Set();
    const processedContents = [];

    contents.forEach(content => {
      let filename = content.filename || 'untitled.md';
      
      // Generate unique filename if needed
      if (usedFilenames.has(filename)) {
        const extension = this.getFileExtension(filename);
        const nameWithoutExt = filename.substring(0, filename.length - extension.length - 1);
        let counter = 1;
        
        do {
          filename = `${nameWithoutExt}-${counter}.${extension}`;
          counter++;
        } while (usedFilenames.has(filename));
      }
      
      usedFilenames.add(filename);
      
      processedContents.push({
        ...content,
        filename,
        originalFilename: content.filename
      });
    });

    return processedContents;
  }

  /**
   * Generate full file path for content
   * @param {Object} metadata - Content metadata
   * @param {Object} settings - Settings object
   * @returns {string} - Full file path
   */
  generateFilePath(metadata, settings = {}) {
    if (!metadata) {
      return 'unsorted/untitled.md';
    }

    const folder = this.classifyContent(metadata);
    const filename = this.generateFilename(metadata, settings);
    return `${folder}/${filename}`;
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

    const dateObj = date ? new Date(date) : new Date();
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    
    // Sanitize image name
    const sanitizedName = imageName.replace(/[^\w\-_.]/g, '-').replace(/--+/g, '-');
    
    return `images/${year}/${month}/${sanitizedName}`;
  }

  /**
   * Suggest a folder based on content and metadata
   * @param {string} textContent - The text content of the page
   * @param {Object} metadata - Page metadata
   * @returns {string} - Suggested folder name
   */
  suggestFolder(textContent, metadata = {}) {
    // Use the existing folder determination logic
    return this.determineFolderFromUrl(metadata.url || '', metadata);
  }

  /**
   * Classify content into appropriate folder based on metadata and content
   * @param {Object} metadata - Page metadata including title, description, keywords, tags
   * @returns {string} - Folder classification
   */
  classifyContent(metadata) {
    if (!metadata) return 'unsorted';

    // Check URL-based classification first
    if (metadata.url) {
      const urlFolder = this.determineFolderFromUrl(metadata.url, metadata);
      if (urlFolder !== 'unsorted') {
        return urlFolder;
      }
    }

    // Check tags for direct matches
    if (metadata.tags && Array.isArray(metadata.tags)) {
      for (const tag of metadata.tags) {
        const tagLower = tag.toLowerCase();
        for (const [folder, keywords] of Object.entries(this.folderMapping)) {
          if (keywords.includes(tagLower)) {
            return folder;
          }
        }
      }
    }

    // Check title and description
    const text = `${metadata.title || ''} ${metadata.description || ''}`.toLowerCase();
    for (const [folder, keywords] of Object.entries(this.folderMapping)) {
      if (keywords.some(keyword => text.includes(keyword))) {
        return folder;
      }
    }

    // Check keywords
    if (metadata.keywords && Array.isArray(metadata.keywords)) {
      for (const keyword of metadata.keywords) {
        const keywordLower = keyword.toLowerCase();
        for (const [folder, keywords] of Object.entries(this.folderMapping)) {
          if (keywords.some(k => keywordLower.includes(k) || k.includes(keywordLower))) {
            return folder;
          }
        }
      }
    }

    return 'unsorted';
  }

  /**
   * Generate metadata from page content
   * @param {Object} pageContent - Page content object with url, title, textContent, etc.
   * @param {Object} settings - Settings object
   * @returns {Object} - Generated metadata
   */
  generateMetadata(pageContent, settings = {}) {
    if (!pageContent) {
      return {
        title: 'Untitled',
        url: '',
        domain: '',
        timestamp: new Date().toISOString(),
        tags: [],
        description: '',
        summary: ''
      };
    }

    const metadata = {
      title: pageContent.title || 'Untitled',
      url: pageContent.url || '',
      domain: pageContent.url ? this.sanitizeDomain(new URL(pageContent.url).hostname) : '',
      timestamp: new Date().toISOString(),
      description: pageContent.description || '',
      author: pageContent.author || '',
      keywords: pageContent.keywords || [],
      tags: this.generateTags({ 
        title: pageContent.title, 
        description: pageContent.description,
        keywords: pageContent.keywords 
      }, pageContent),
      summary: this.generateSummary(pageContent),
      wordCount: pageContent.textContent ? pageContent.textContent.split(/\s+/).length : 0,
      readingTime: pageContent.textContent ? Math.ceil(pageContent.textContent.split(/\s+/).length / 200) : 0
    };

    // Add custom metadata from settings
    if (settings.customMetadata) {
      Object.assign(metadata, settings.customMetadata);
    }

    return metadata;
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
        folder: 'unsorted'
      };
    }

    const metadata = this.generateMetadata(pageContent, settings);
    const frontmatter = this.createFrontmatter(metadata, pageContent);
    const folder = this.classifyContent(metadata);
    const filename = this.generateFilename(metadata, settings);

    return {
      metadata,
      frontmatter,
      content: pageContent.markdown || pageContent.textContent || '',
      filename,
      folder,
      fullContent: frontmatter + '\n' + (pageContent.markdown || pageContent.textContent || ''),
      path: `${folder}/${filename}`
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

    const organization = {
      folders: {},
      totalFiles: contents.length,
      byFolder: {}
    };

    contents.forEach(content => {
      const processed = typeof content === 'object' && content.folder 
        ? content 
        : this.createProcessedContent(content);
      
      const folder = processed.folder || 'unsorted';
      
      if (!organization.folders[folder]) {
        organization.folders[folder] = [];
        organization.byFolder[folder] = 0;
      }
      
      organization.folders[folder].push(processed);
      organization.byFolder[folder]++;
    });

    return organization;
  }

  /**
   * Ensure all filenames in a collection are unique
   * @param {Array} contents - Array of content objects with filename property
   * @returns {Array} - Contents with unique filenames
   */
  ensureUniqueFilenames(contents) {
    if (!Array.isArray(contents)) {
      return [];
    }

    const usedFilenames = new Set();
    const processedContents = [];

    contents.forEach(content => {
      let filename = content.filename || 'untitled.md';
      
      // Generate unique filename if needed
      if (usedFilenames.has(filename)) {
        const extension = this.getFileExtension(filename);
        const nameWithoutExt = filename.substring(0, filename.length - extension.length - 1);
        let counter = 1;
        
        do {
          filename = `${nameWithoutExt}-${counter}.${extension}`;
          counter++;
        } while (usedFilenames.has(filename));
      }
      
      usedFilenames.add(filename);
      
      processedContents.push({
        ...content,
        filename,
        originalFilename: content.filename
      });
    });

    return processedContents;
  }

  /**
   * Generate full file path for content
   * @param {Object} metadata - Content metadata
   * @param {Object} settings - Settings object
   * @returns {string} - Full file path
   */
  generateFilePath(metadata, settings = {}) {
    if (!metadata) {
      return 'unsorted/untitled.md';
    }

    const folder = this.classifyContent(metadata);
    const filename = this.generateFilename(metadata, settings);
    return `${folder}/${filename}`;
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

    const dateObj = date ? new Date(date) : new Date();
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    
    // Sanitize image name
    const sanitizedName = imageName.replace(/[^\w\-_.]/g, '-').replace(/--+/g, '-');
    
    return `images/${year}/${month}/${sanitizedName}`;
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
