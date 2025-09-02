// Centralized settings management with consistent schema and validation

import { createLogger } from './logger';
const logger = createLogger('SettingsManager');

import { ISettings } from '../types/types';

// Type definitions for service worker compatibility
interface ISettingsManagerStorageData {
  [key: string]: unknown;
}

type SettingsManagerStorageKeys = string | string[] | Record<string, unknown> | null;
type SettingsManagerStorageResult<T = Record<string, unknown>> = Promise<T>;

interface ISettingDefinition {
  type: 'string' | 'boolean' | 'number' | 'array';
  default: string | boolean | number | string[];
  required: boolean;
  sensitive: boolean;
  description: string;
  pattern?: RegExp;
  options?: string[];
  requires?: string[];
  min?: number;
  max?: number;
}

interface ISettingsSchema {
  [key: string]: ISettingDefinition;
}

class SettingsManager {
  private readonly STORAGE_KEY: string = 'prismWeaveSettings';
  private readonly schema: ISettingsSchema;

  constructor() {
    this.schema = this.getSettingsSchema();
  }
  private getSettingsSchema(): ISettingsSchema {
    return {
      // Repository Configuration
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
        sensitive: false,
        pattern: /^[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+$/,
        description: 'GitHub repository in format owner/repo',
      },

      // File Organization
      defaultFolder: {
        type: 'string',
        default: 'unsorted',
        required: true,
        sensitive: false,
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
        sensitive: false,
        description: 'Custom folder name when defaultFolder is "custom"',
      },
      fileNamingPattern: {
        type: 'string',
        default: 'YYYY-MM-DD-domain-title',
        required: true,
        sensitive: false,
        options: [
          'YYYY-MM-DD-domain-title',
          'YYYY-MM-DD-title',
          'domain-YYYY-MM-DD-title',
          'title-YYYY-MM-DD',
        ],
        description: 'Template for generated filenames',
      },

      // Automation Settings
      autoCommit: {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: true,
        description: 'Automatically commit captured files to Git',
      },

      // Content Processing
      captureImages: {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: true,
        description: 'Download and save images from captured pages',
      },
      removeAds: {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: true,
        description: 'Remove advertisements and promotional content',
      },
      removeNavigation: {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: true,
        description: 'Remove navigation menus and site headers/footers',
      },
      customSelectors: {
        type: 'string',
        default: '',
        required: false,
        sensitive: false,
        description: 'Custom CSS selectors for elements to remove during capture',
      },

      // Git & Repository Settings
      commitMessageTemplate: {
        type: 'string',
        required: false,
        sensitive: false,
        default: 'Add: {domain} - {title}',
        description: 'Template for git commit messages',
      },

      // Debugging Settings
      debugMode: {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: false,
        description: 'Enable detailed logging and debug information',
      },

      // UI Preferences
      showNotifications: {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: true,
        description: 'Show completion notifications',
      },
      enableKeyboardShortcuts: {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: true,
        description: 'Enable keyboard shortcuts for capture',
      },

      // Bookmarklet Settings
      'bookmarklet.enabled': {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: false,
        description: 'Enable bookmarklet functionality',
      },
      'bookmarklet.customDomain': {
        type: 'string',
        default: '',
        required: false,
        sensitive: false,
        pattern: /^https?:\/\/[a-zA-Z0-9.-]+(?:\:[0-9]+)?(?:\/.*)?$/,
        description: 'Custom domain for bookmarklet endpoint (optional)',
      },
      'bookmarklet.includeImages': {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: true,
        description: 'Include images in bookmarklet captures',
      },
      'bookmarklet.includeLinks': {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: true,
        description: 'Include links in bookmarklet captures',
      },
      'bookmarklet.cleanAds': {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: true,
        description: 'Remove advertisements in bookmarklet captures',
      },
      'bookmarklet.customSelectors': {
        type: 'array',
        default: [],
        required: false,
        sensitive: false,
        description: 'Custom CSS selectors to include in bookmarklet captures',
      },
      'bookmarklet.excludeSelectors': {
        type: 'array',
        default: ['nav', 'header', 'footer', '.advertisement', '.ad'],
        required: false,
        sensitive: false,
        description: 'CSS selectors to exclude from bookmarklet captures',
      },
      'bookmarklet.autoInstall': {
        type: 'boolean',
        required: false,
        sensitive: false,
        default: false,
        description: 'Automatically update bookmarklet when settings change',
      },
      'bookmarklet.version': {
        type: 'string',
        default: '1.0.0',
        required: false,
        sensitive: false,
        pattern: /^\d+\.\d+\.\d+$/,
        description: 'Bookmarklet version for tracking updates',
      },
    };
  }

  async getSettings(): Promise<Partial<ISettings>> {
    try {
      const result = await this.getFromStorage<Record<string, Partial<ISettings>>>([
        this.STORAGE_KEY,
      ]);
      const rawSettings = result[this.STORAGE_KEY] || {};
      // Validate settings against schema - just log errors, don't block
      const validationResult = this.validateSettings(rawSettings);
      if (!validationResult.isValid) {
        logger.warn('Settings validation failed:', validationResult.errors);
      }

      return rawSettings;
    } catch (error) {
      logger.error('Error getting settings:', error);
      return {};
    }
  }

  async getDefaults(): Promise<Partial<ISettings>> {
    const defaults: Partial<ISettings> = {};

    Object.entries(this.schema).forEach(([key, definition]) => {
      (defaults as any)[key] = definition.default;
    });

    return defaults;
  }

  async getSettingsWithDefaults(): Promise<Partial<ISettings>> {
    try {
      const [current, defaults] = await Promise.all([this.getSettings(), this.getDefaults()]);

      return { ...defaults, ...current };
    } catch (error) {
      logger.error('Error getting settings with defaults:', error);
      return await this.getDefaults();
    }
  }

  async updateSettings(updates: Partial<ISettings>): Promise<boolean> {
    try {
      const validationResult = this.validateSettings(updates);
      if (!validationResult.isValid) {
        logger.error('Validation failed:', validationResult.errors);
        return false;
      }

      const current = await this.getSettings();
      const updated = { ...current, ...updates };

      await this.setToStorage({ [this.STORAGE_KEY]: updated });
      return true;
    } catch (error) {
      logger.error('Error updating settings:', error);
      return false;
    }
  }

  async resetSettings(): Promise<boolean> {
    try {
      const defaults = await this.getDefaults();
      await this.setToStorage({ [this.STORAGE_KEY]: defaults });
      return true;
    } catch (error) {
      logger.error('Error resetting settings:', error);
      return false;
    }
  }
  validateSettings(settings: Partial<ISettings>): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    Object.entries(settings).forEach(([key, value]) => {
      const definition = this.schema[key];
      if (!definition) {
        errors.push(`Unknown setting: ${key}`);
        return;
      }

      // Type validation with proper array handling
      const isValidType = this.validateType(value, definition.type);
      if (!isValidType) {
        errors.push(
          `Invalid type for ${key}: expected ${definition.type}, got ${this.getActualType(value)}`
        );
        return;
      }

      // Pattern validation
      if (
        definition.pattern &&
        typeof value === 'string' &&
        value !== '' &&
        !definition.pattern.test(value)
      ) {
        errors.push(`Invalid format for ${key}: does not match required pattern`);
      }

      // Options validation
      if (definition.options && value !== '' && !definition.options.includes(value as string)) {
        errors.push(`Invalid value for ${key}: must be one of ${definition.options.join(', ')}`);
      }

      // Range validation for numbers
      if (definition.type === 'number' && typeof value === 'number') {
        if (definition.min !== undefined && value < definition.min) {
          errors.push(`Value for ${key} is below minimum: ${definition.min}`);
        }
        if (definition.max !== undefined && value > definition.max) {
          errors.push(`Value for ${key} is above maximum: ${definition.max}`);
        }
      }
    });

    return { isValid: errors.length === 0, errors };
  }

  private validateType(value: unknown, expectedType: string): boolean {
    switch (expectedType) {
      case 'array':
        return Array.isArray(value);
      case 'string':
        return typeof value === 'string';
      case 'boolean':
        return typeof value === 'boolean';
      case 'number':
        return typeof value === 'number';
      default:
        return false;
    }
  }

  private getActualType(value: unknown): string {
    if (Array.isArray(value)) return 'array';
    if (value === null) return 'null';
    return typeof value;
  }

  async checkRequiredDependencies(settings: Partial<ISettings>): Promise<string[]> {
    const missingDependencies: string[] = [];

    Object.entries(settings).forEach(([key, value]) => {
      const definition = this.schema[key];
      if (definition?.requires && value) {
        definition.requires.forEach(required => {
          if (!settings[required as keyof ISettings]) {
            missingDependencies.push(`${key} requires ${required} to be set`);
          }
        });
      }
    });

    return missingDependencies;
  }

  getSettingDefinition(key: string): ISettingDefinition | null {
    return this.schema[key] || null;
  }

  getAllSettingDefinitions(): ISettingsSchema {
    return { ...this.schema };
  }

  async exportSettings(): Promise<string> {
    try {
      const settings = await this.getSettings();
      const sanitized = this.sanitizeForExport(settings);
      return JSON.stringify(sanitized, null, 2);
    } catch (error) {
      logger.error('Error exporting settings:', error);
      throw error;
    }
  }

  async importSettings(jsonString: string): Promise<boolean> {
    try {
      const imported = JSON.parse(jsonString) as Partial<ISettings>;
      return await this.updateSettings(imported);
    } catch (error) {
      logger.error('Error importing settings:', error);
      return false;
    }
  }

  private sanitizeForExport(settings: Partial<ISettings>): Partial<ISettings> {
    const sanitized = { ...settings };

    Object.entries(this.schema).forEach(([key, definition]) => {
      if (definition.sensitive && sanitized[key as keyof ISettings]) {
        (sanitized as any)[key] = '[REDACTED]';
      }
    });

    return sanitized;
  }
  private async getFromStorage<T = ISettingsManagerStorageData>(
    keys: SettingsManagerStorageKeys
  ): SettingsManagerStorageResult<T> {
    // Access chrome API - check multiple contexts for compatibility
    const chromeAPI =
      (typeof chrome !== 'undefined' ? chrome : undefined) ||
      (typeof globalThis !== 'undefined' && (globalThis as any).chrome) ||
      (typeof self !== 'undefined' && (self as any).chrome) ||
      (typeof global !== 'undefined' && (global as any).chrome);

    if (!chromeAPI || !chromeAPI.storage) {
      throw new Error('Chrome storage API not available');
    }

    return new Promise<T>((resolve, reject) => {
      chromeAPI.storage.sync.get(keys as any, (result: T) => {
        if (chromeAPI.runtime.lastError) {
          reject(new Error(chromeAPI.runtime.lastError.message));
        } else {
          resolve(result);
        }
      });
    });
  }

  private async setToStorage(data: ISettingsManagerStorageData): Promise<void> {
    // Access chrome API - check multiple contexts for compatibility
    const chromeAPI =
      (typeof chrome !== 'undefined' ? chrome : undefined) ||
      (typeof globalThis !== 'undefined' && (globalThis as any).chrome) ||
      (typeof self !== 'undefined' && (self as any).chrome) ||
      (typeof global !== 'undefined' && (global as any).chrome);

    if (!chromeAPI || !chromeAPI.storage) {
      throw new Error('Chrome storage API not available');
    }

    return new Promise<void>((resolve, reject) => {
      chromeAPI.storage.sync.set(data, () => {
        if (chromeAPI.runtime.lastError) {
          reject(new Error(chromeAPI.runtime.lastError.message));
        } else {
          resolve();
        }
      });
    });
  }
}

// Export for ES6 modules
export { SettingsManager };

// Make available globally for service worker importScripts compatibility
if (typeof globalThis !== 'undefined') {
  (globalThis as any).SettingsManager = SettingsManager;
} else if (typeof self !== 'undefined') {
  (self as any).SettingsManager = SettingsManager;
}
