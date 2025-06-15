// PrismWeave Shared Utilities
// Common helper functions used across multiple modules

class SharedUtils {
  // URL validation and manipulation
  static isValidUrl(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  static resolveUrl(url, baseUrl = '') {
    try {
      if (typeof window !== 'undefined' && window.location) {
        return new URL(url, baseUrl || window.location.href).href;
      }
      return new URL(url, baseUrl).href;
    } catch {
      return url;
    }
  }

  static isValidImageUrl(url) {
    const imageExtensions = /\.(jpg|jpeg|png|gif|svg|webp|bmp)(\?.*)?$/i;
    return imageExtensions.test(url) || url.includes('image') || url.includes('img');
  }

  // Text processing utilities
  static sanitizeForFilename(text, maxLength = 50) {
    if (!text) return 'untitled';
    
    return text
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/-+/g, '-') // Replace multiple hyphens with single
      .replace(/^-|-$/g, '') // Remove leading/trailing hyphens
      .substring(0, maxLength); // Limit length
  }

  static sanitizeDomain(domain) {
    if (!domain) return 'unknown';
    
    return domain
      .toLowerCase()
      .replace(/^www\./, '') // Remove www.
      .replace(/[^a-z0-9.-]/g, '') // Keep only alphanumeric, dots, and hyphens
      .substring(0, 20); // Limit length
  }

  // YAML utilities
  static escapeYaml(str) {
    if (typeof str !== 'string') return str;
    return str.replace(/"/g, '\\"').replace(/\n/g, '\\n');
  }

  static formatYamlValue(value) {
    if (value === null || value === undefined) return null;
    
    if (Array.isArray(value)) {
      if (value.length === 0) return '[]';
      return value;
    }
    
    if (typeof value === 'string') {
      return `"${this.escapeYaml(value)}"`;
    }
    
    return value;
  }

  // Date utilities
  static formatDateForFilename(date = new Date()) {
    const d = new Date(date);
    return d.getFullYear() + '-' + 
           (d.getMonth() + 1).toString().padStart(2, '0') + '-' +
           d.getDate().toString().padStart(2, '0');
  }

  static getDateFromFilename(filename) {
    const dateMatch = filename.match(/(\d{4}-\d{2}-\d{2})/);
    return dateMatch ? new Date(dateMatch[1]) : null;
  }

  // File utilities
  static getFileExtension(filename) {
    const match = filename.match(/\.([a-zA-Z0-9]+)$/);
    return match ? match[1].toLowerCase() : '';
  }

  static isMarkdownFile(filename) {
    return this.getFileExtension(filename) === 'md';
  }

  static generateUniqueFilename(baseFilename, existingFiles = []) {
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

  static validateFilename(filename) {
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

  // Content quality assessment utilities
  static calculateReadabilityScore(text, paragraphs, headings) {
    const wordCount = this.countWords(text);
    const avgWordsPerParagraph = paragraphs > 0 ? wordCount / paragraphs : 0;
    
    let score = 0;
    
    // Word count scoring
    if (wordCount >= 300) score += 30;
    else if (wordCount >= 100) score += 20;
    else if (wordCount >= 50) score += 10;
    
    // Structure scoring
    if (paragraphs >= 3) score += 20;
    if (headings >= 2) score += 15;
    
    // Readability scoring
    if (avgWordsPerParagraph >= 20 && avgWordsPerParagraph <= 100) {
      score += 15;
    }
    
    return Math.min(score, 100);
  }

  static countWords(text) {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  }

  // Browser context detection
  static isServiceWorkerContext() {
    return typeof importScripts === 'function' && typeof window === 'undefined';
  }

  static isBrowserContext() {
    return typeof window !== 'undefined';
  }

  // Error handling utilities
  static createError(message, code = 'GENERAL_ERROR', details = {}) {
    const error = new Error(message);
    error.code = code;
    error.details = details;
    return error;
  }

  static logError(error, context = '') {
    const timestamp = new Date().toISOString();
    console.error(`[PrismWeave${context ? ' ' + context : ''}] ${timestamp}:`, error);
  }
}

// Export for different contexts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SharedUtils;
}

if (typeof window !== 'undefined') {
  window.SharedUtils = SharedUtils;
}
