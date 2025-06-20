// PrismWeave Settings Manager
// Centralized settings management with consistent schema and validation

class SettingsManager {
  constructor() {
    this.STORAGE_KEY = 'prismWeaveSettings';
    this.schema = this.getSettingsSchema();
  }

  getSettingsSchema() {
    return {
      // Repository Configuration
      repositoryPath: {
        type: 'string',
        default: '',
        required: false,
        description: 'Local or remote repository path',
      },
      githubToken: {
        type: 'string',
        default: '',
        required: false,
        sensitive: true,
        description: 'GitHub personal access token',
      },
      githubRepo: {
        type: 'string',
        default: '',
        required: false,
        pattern: /^[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+$/,
        description: 'GitHub repository in format owner/repo',
      },

      // File Organization
      defaultFolder: {
        type: 'string',
        default: 'unsorted',
        required: true,
        options: [
          'tech',
          'business',
          'research',
          'news',
          'tutorial',
          'reference',
          'blog',
          'social',
          'unsorted',
          'custom',
        ],
        description: 'Default folder for captured documents',
      },
      customFolder: {
        type: 'string',
        default: '',
        required: false,
        description: 'Custom folder name when defaultFolder is "custom"',
      },
      fileNamingPattern: {
        type: 'string',
        default: 'YYYY-MM-DD-domain-title',
        required: true,
        options: [
          'YYYY-MM-DD-domain-title',
          'YYYY-MM-DD-title',
          'domain-YYYY-MM-DD-title',
          'title-YYYY-MM-DD',
          'custom',
        ],
        description: 'Template for generated filenames',
      },
      customNamingPattern: {
        type: 'string',
        default: '',
        required: false,
        description: 'Custom naming pattern when fileNamingPattern is "custom"',
      },

      // Automation Settings
      autoCommit: {
        type: 'boolean',
        default: true,
        description: 'Automatically commit captured files to Git',
      },
      autoPush: {
        type: 'boolean',
        default: false,
        description: 'Automatically push commits to remote repository',
        requires: ['githubToken', 'githubRepo'],
      },

      // Content Processing
      captureImages: {
        type: 'boolean',
        default: true,
        description: 'Download and save images from captured pages',
      },
      removeAds: {
        type: 'boolean',
        default: true,
        description: 'Remove advertisements and promotional content',
      },
      removeNavigation: {
        type: 'boolean',
        default: true,
        description: 'Remove navigation and menu elements',
      },
      preserveLinks: {
        type: 'boolean',
        default: true,
        description: 'Preserve all links in markdown output',
      },
      customSelectors: {
        type: 'string',
        default: '',
        required: false,
        description: 'Comma-separated CSS selectors for elements to remove',
      },

      // Git Configuration
      commitMessage: {
        type: 'string',
        default: 'Add captured content: {title}',
        required: true,
        description: 'Simple commit message template',
      },
      commitMessageTemplate: {
        type: 'string',
        default: 'Add: {domain} - {title}',
        required: false,
        description: 'Advanced template for Git commit messages',
      },

      // User Experience
      enableKeyboardShortcuts: {
        type: 'boolean',
        default: true,
        description: 'Enable keyboard shortcuts for quick capture',
      },
      showNotifications: {
        type: 'boolean',
        default: true,
        description: 'Show browser notifications for capture events',
      },
      autoClosePopup: {
        type: 'boolean',
        default: true,
        description: 'Automatically close popup after successful capture',
      },

      // Advanced Options
      maxImageSize: {
        type: 'number',
        default: 5242880, // 5MB
        min: 1048576, // 1MB
        max: 52428800, // 50MB
        description: 'Maximum image file size to download (bytes)',
      },
      captureTimeout: {
        type: 'number',
        default: 30000, // 30 seconds
        min: 5000,
        max: 120000,
        description: 'Timeout for capture operations (milliseconds)',
      },
    };
  }

  getDefaultSettings() {
    const defaults = {};
    Object.entries(this.schema).forEach(([key, config]) => {
      defaults[key] = config.default;
    });
    return defaults;
  }

  async loadSettings() {
    try {
      console.log('SettingsManager: loadSettings called');
      
      // Try sync first, fallback to local
      let result;
      try {
        result = await chrome.storage.sync.get([this.STORAGE_KEY]);
        console.log('SettingsManager: sync storage result:', result);
      } catch (syncError) {
        console.warn('SettingsManager: sync storage failed, trying local:', syncError);
        result = await chrome.storage.local.get([this.STORAGE_KEY]);
        console.log('SettingsManager: local storage result:', result);
      }
      
      const savedSettings = result[this.STORAGE_KEY] || {};
      console.log('SettingsManager: savedSettings from storage:', savedSettings);

      // Merge with defaults and validate
      const settings = this.mergeWithDefaults(savedSettings);
      console.log('SettingsManager: merged with defaults:', settings);
      
      const validation = this.validateSettings(settings);
      const validated = validation.isValid ? validation.validated : this.getDefaultSettings();
      console.log('SettingsManager: final validated settings:', validated);

      return validated;
    } catch (error) {
      console.error('Failed to load settings:', error);
      return this.getDefaultSettings();
    }
  }

  async saveSettings(settings) {
    try {
      console.log('SettingsManager: saveSettings called with:', settings);
      
      // Validate before saving
      const validation = this.validateSettings(settings);
      console.log('SettingsManager: validation result:', validation);

      if (!validation.isValid) {
        return { 
          success: false, 
          errors: validation.errors 
        };
      }

      // Save to both sync and local for reliability during development
      const data = { [this.STORAGE_KEY]: validation.validated };
      
      try {
        await chrome.storage.sync.set(data);
        console.log('SettingsManager: settings saved to sync storage');
      } catch (syncError) {
        console.warn('SettingsManager: sync storage failed, using local:', syncError);
      }
      
      await chrome.storage.local.set(data);
      console.log('SettingsManager: settings saved to local storage');
      
      // Verify what was actually saved
      const verification = await chrome.storage.local.get([this.STORAGE_KEY]);
      console.log('SettingsManager: verification read from local storage:', verification);

      return { success: true, settings: validation.validated };
    } catch (error) {
      console.error('Failed to save settings:', error);
      return { success: false, error: error.message };
    }
  }

  mergeWithDefaults(userSettings) {
    const defaults = this.getDefaultSettings();
    const merged = { ...defaults };

    // Only merge keys that exist in schema
    Object.keys(this.schema).forEach(key => {
      if (userSettings.hasOwnProperty(key)) {
        merged[key] = userSettings[key];
      }
    });

    return merged;
  }

  validateSettings(settings) {
    const validated = { ...settings };
    const errors = [];

    Object.entries(this.schema).forEach(([key, config]) => {
      const value = validated[key];

      // Type validation
      if (config.type === 'boolean' && typeof value !== 'boolean') {
        validated[key] = config.default;
        errors.push(`Invalid type for ${key}, using default`);
      } else if (config.type === 'string' && typeof value !== 'string') {
        validated[key] = config.default;
        errors.push(`Invalid type for ${key}, using default`);
      } else if (config.type === 'number' && typeof value !== 'number') {
        validated[key] = config.default;
        errors.push(`Invalid type for ${key}, using default`);
      }

      // Required field validation
      if (config.required && (!value || value === '')) {
        errors.push(`Required field ${key} is missing`);
      }

      // Pattern validation
      if (config.pattern && value && !config.pattern.test(value)) {
        errors.push(`Field ${key} does not match required pattern`);
      }

      // Options validation
      if (config.options && value && !config.options.includes(value)) {
        validated[key] = config.default;
        errors.push(`Invalid option for ${key}, using default`);
      }

      // Range validation for numbers
      if (config.type === 'number' && typeof value === 'number') {
        if (config.min !== undefined && value < config.min) {
          validated[key] = config.min;
          errors.push(`Value for ${key} below minimum, adjusted`);
        }
        if (config.max !== undefined && value > config.max) {
          validated[key] = config.max;
          errors.push(`Value for ${key} above maximum, adjusted`);
        }
      }
    });

    // Cross-field validation
    if (validated.autoPush) {
      if (!validated.githubToken) {
        errors.push('GitHub token required for auto-push');
      }
      if (!validated.githubRepo) {
        errors.push('GitHub repository required for auto-push');
      }
    }

    if (validated.defaultFolder === 'custom' && !validated.customFolder) {
      errors.push('Custom folder name required when using custom folder');
    }

    if (validated.fileNamingPattern === 'custom' && !validated.customNamingPattern) {
      errors.push('Custom naming pattern required when using custom pattern');
    }

    if (errors.length > 0) {
      console.warn('Settings validation errors:', errors);
    }

    return {
      isValid: errors.length === 0,
      errors: errors,
      validated: validated
    };
  }

  async resetSettings() {
    const defaults = this.getDefaultSettings();
    return await this.saveSettings(defaults);
  }

  async exportSettings(settings = null) {
    // Load current settings if none provided
    if (!settings) {
      settings = await this.loadSettings();
    }
    
    // Remove sensitive data for export
    const exportData = { ...settings };
    Object.entries(this.schema).forEach(([key, config]) => {
      if (config.sensitive) {
        delete exportData[key];
      }
    });

    return {
      version: '1.0',
      exported: new Date().toISOString(),
      settings: exportData,
    };
  }

  async importSettings(importData) {
    try {
      // Validate import data format
      const validation = this.validateImportData(importData);
      if (!validation.isValid) {
        return {
          success: false,
          errors: validation.errors
        };
      }

      // Merge imported settings with defaults to get complete settings
      const completeSettings = this.mergeWithDefaults(importData.settings);
      
      // Save the complete settings
      const saveResult = await this.saveSettings(completeSettings);
      return saveResult;
    } catch (error) {
      return {
        success: false,
        errors: [error.message]
      };
    }
  }

  validateImportData(importData) {
    if (!importData || typeof importData !== 'object') {
      throw new Error('Invalid import data format');
    }

    if (!importData.settings) {
      throw new Error('No settings found in import data');
    }

    // For import, we only validate that the provided fields are valid types/values
    // We don't require all fields to be present (will be merged with defaults)
    const errors = [];
    const settings = importData.settings;

    Object.entries(settings).forEach(([key, value]) => {
      const config = this.schema[key];
      if (!config) {
        errors.push(`Unknown setting: ${key}`);
        return;
      }

      // Type validation for provided values
      if (config.type === 'boolean' && typeof value !== 'boolean') {
        errors.push(`Invalid type for ${key}, expected boolean`);
      } else if (config.type === 'string' && typeof value !== 'string') {
        errors.push(`Invalid type for ${key}, expected string`);
      } else if (config.type === 'number' && typeof value !== 'number') {
        errors.push(`Invalid type for ${key}, expected number`);
      }

      // Pattern validation for strings
      if (config.pattern && value && typeof value === 'string' && !config.pattern.test(value)) {
        errors.push(`Field ${key} does not match required pattern`);
      }

      // Options validation
      if (config.options && !config.options.includes(value)) {
        errors.push(`Field ${key} must be one of: ${config.options.join(', ')}`);
      }
    });

    return {
      isValid: errors.length === 0,
      errors: errors,
      validated: settings
    };
  }

  getFieldInfo(fieldName) {
    return this.schema[fieldName] || null;
  }

  getAllFieldInfo() {
    return this.schema;
  }

  // Utility methods for UI
  getSelectOptions(fieldName) {
    const field = this.schema[fieldName];
    return field?.options || [];
  }

  isFieldRequired(fieldName) {
    const field = this.schema[fieldName];
    return field?.required || false;
  }

  getFieldDescription(fieldName) {
    const field = this.schema[fieldName];
    return field?.description || '';
  }

  // Migration support for future schema changes
  migrateSettings(settings, fromVersion = '1.0', toVersion = '1.0') {
    // Future: Handle settings migration between versions
    return settings;
  }
}

// Export for different contexts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SettingsManager;
}

// Export for both browser extension and Node.js/test environments
if (typeof window !== 'undefined') {
  window.SettingsManager = SettingsManager;
} else if (typeof self !== 'undefined') {
  self.SettingsManager = SettingsManager;
}

// ES6 module export for tests
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SettingsManager;
}
