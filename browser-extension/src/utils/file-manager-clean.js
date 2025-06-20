// File Manager utility for PrismWeave
// Handles file naming, organization, and metadata processing

// Helper function to get SharedUtils in different contexts
function getSharedUtils() {
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
      tech: [
        'technology', 'programming', 'development', 'software', 'coding', 'javascript', 'python',
        'react', 'node', 'api', 'web development', 'mobile development', 'ai', 'machine learning',
        'data science', 'algorithm', 'framework', 'library', 'database', 'cloud'
      ],
      business: [
        'business', 'startup', 'entrepreneurship', 'marketing', 'sales', 'finance', 'strategy',
        'management', 'leadership', 'productivity', 'growth', 'revenue', 'customer', 'market'
      ],
      tutorial: [
        'tutorial', 'guide', 'how-to', 'learn', 'course', 'lesson', 'training', 'education',
        'walkthrough', 'step-by-step', 'beginner', 'advanced'
      ],
      research: [
        'research', 'study', 'analysis', 'academic', 'paper', 'journal', 'science', 'experiment',
        'methodology', 'findings', 'data', 'statistics'
      ],
      news: [
        'news', 'article', 'blog', 'press', 'release', 'announcement', 'update', 'report'
      ]
    };
  }

  generateFilename(metadata, settings = {}) {
    const SharedUtils = getSharedUtils();
    if (SharedUtils?.generateFilename) {
      return SharedUtils.generateFilename(metadata, settings);
    }

    // Fallback implementation
    const timestamp = metadata.timestamp ? new Date(metadata.timestamp) : new Date();
    const dateStr = timestamp.toISOString().split('T')[0]; // YYYY-MM-DD
    
    const domain = this.sanitizeDomain(metadata.domain);
    const title = this.sanitizeTitle(metadata.title);

    let filename;
    if (settings.filenamePattern) {
      filename = settings.filenamePattern
        .replace('{date}', dateStr)
        .replace('{domain}', domain)
        .replace('{title}', title);
    } else {
      filename = `${dateStr}-${domain}-${title}`;
    }

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
    return SharedUtils?.sanitizeTitle(title) || this._fallbackSanitizeTitle(title);
  }

  _fallbackSanitizeTitle(title) {
    if (!title) return 'untitled';

    return title
      .toLowerCase()
      .replace(/[^\w\s-]/g, '') // Remove special characters except spaces and hyphens
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/-+/g, '-') // Replace multiple hyphens with single
      .replace(/^-|-$/g, '') // Remove leading/trailing hyphens
      .substring(0, 50); // Limit length
  }

  determineFolderFromUrl(url, metadata = {}) {
    if (!url) return 'unsorted';

    try {
      const urlObj = new URL(url);
      const domain = urlObj.hostname.toLowerCase();
      const path = urlObj.pathname.toLowerCase();

      // Check domain-based folder mapping
      for (const [folder, keywords] of Object.entries(this.folderMapping)) {
        if (keywords.some(keyword => domain.includes(keyword) || path.includes(keyword))) {
          return folder;
        }
      }

      // Check title and description for classification
      const text = `${metadata.title || ''} ${metadata.description || ''}`.toLowerCase();
      for (const [folder, keywords] of Object.entries(this.folderMapping)) {
        if (keywords.some(keyword => text.includes(keyword))) {
          return folder;
        }
      }
    } catch (error) {
      // Invalid URL, fallback to content analysis
    }

    return 'unsorted';
  }

  createFrontmatter(metadata, pageData = {}) {
    const data = {
      title: metadata.title || 'Untitled',
      url: metadata.url || '',
      domain: metadata.domain || '',
      created: metadata.timestamp || new Date().toISOString(),
      tags: this.generateTags(metadata, pageData),
      description: metadata.description || '',
      author: metadata.author || '',
      summary: this.generateSummary(pageData)
    };

    // Add additional metadata if available
    if (metadata.keywords && metadata.keywords.length > 0) {
      data.keywords = metadata.keywords;
    }

    if (metadata.readingTime) {
      data.readingTime = metadata.readingTime;
    }

    if (metadata.wordCount) {
      data.wordCount = metadata.wordCount;
    }

    return this.formatFrontmatter(data);
  }

  formatFrontmatter(data) {
    let frontmatter = '---\n';
    for (const [key, value] of Object.entries(data)) {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          if (value.length > 0) {
            frontmatter += `${key}:\n`;
            value.forEach(item => {
              frontmatter += `  - ${this.escapeYaml(item)}\n`;
            });
          }
        } else {
          frontmatter += `${key}: ${this.escapeYaml(value)}\n`;
        }
      }
    }
    frontmatter += '---\n';
    return frontmatter;
  }

  escapeYaml(str) {
    const SharedUtils = getSharedUtils();
    return SharedUtils?.escapeYaml(str) || this._fallbackEscapeYaml(str);
  }

  _fallbackEscapeYaml(str) {
    if (typeof str !== 'string') return str;
    return str.includes(':') || str.includes('"') || str.includes("'") ? `"${str.replace(/"/g, '\\"')}"` : str;
  }

  generateTags(metadata, pageData = {}) {
    const tags = new Set();

    // Extract from domain
    const domain = metadata.domain || metadata.url;
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
        summary: '',
        folder: 'unsorted',
        captureSettings: settings
      };
    }

    let domain = '';
    try {
      if (pageContent.url && pageContent.url.startsWith('http')) {
        domain = this.sanitizeDomain(new URL(pageContent.url).hostname);
      }
    } catch (error) {
      domain = 'unknown';
    }

    const metadata = {
      title: pageContent.title || 'Untitled',
      url: pageContent.url || '',
      domain,
      timestamp: new Date().toISOString(),
      description: pageContent.description || '',
      author: pageContent.author || '',
      keywords: pageContent.keywords || [],
      tags: this.generateTags({ 
        title: pageContent.title, 
        description: pageContent.description,
        keywords: pageContent.keywords,
        domain
      }, pageContent),
      summary: this.generateSummary(pageContent),
      wordCount: pageContent.textContent ? pageContent.textContent.split(/\s+/).filter(w => w.length > 0).length : 0,
      readingTime: pageContent.textContent ? Math.ceil(pageContent.textContent.split(/\s+/).filter(w => w.length > 0).length / 200) : 0,
      folder: this.classifyContent({
        title: pageContent.title,
        description: pageContent.description,
        url: pageContent.url,
        keywords: pageContent.keywords
      }),
      captureSettings: settings
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
}

// For use in service worker context
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FileManager;
}

// For browser extension context
if (typeof window !== 'undefined') {
  window.FileManager = FileManager;
}
