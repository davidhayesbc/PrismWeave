// Centralized settings management with consistent schema and validation
// Updated to use shared core with dependency injection

import { createLogger } from './logger';
const logger = createLogger('SettingsManager');

import { ChromeStorageProvider } from '../shared/adapters/chrome-adapters.js';
import { SettingsManager as SharedSettingsManager } from '../shared/core/settings-manager.js';
import { ISettings } from '../types/index';

// Create settings manager instance with Chrome storage provider
const storageProvider = new ChromeStorageProvider();
const sharedManager = new SharedSettingsManager(storageProvider, logger);

/**
 * Legacy settings manager that delegates to shared implementation
 * Maintains backward compatibility while using new shared core
 */
class SettingsManager {
  async getSettings(): Promise<Partial<ISettings>> {
    return sharedManager.getSettings();
  }

  async getDefaults(): Promise<Partial<ISettings>> {
    return sharedManager.getDefaults();
  }

  async getSettingsWithDefaults(): Promise<Partial<ISettings>> {
    return sharedManager.getSettingsWithDefaults();
  }

  async updateSettings(updates: Partial<ISettings>): Promise<boolean> {
    return sharedManager.updateSettings(updates);
  }

  async resetSettings(): Promise<boolean> {
    return sharedManager.resetSettings();
  }

  validateSettings(settings: Partial<ISettings>): { isValid: boolean; errors: string[] } {
    return sharedManager.validateSettings(settings);
  }

  async checkRequiredDependencies(settings: Partial<ISettings>): Promise<string[]> {
    return sharedManager.checkRequiredDependencies(settings);
  }

  getSettingDefinition(key: string) {
    return sharedManager.getSettingDefinition(key);
  }

  getAllSettingDefinitions() {
    return sharedManager.getAllSettingDefinitions();
  }

  async exportSettings(): Promise<string> {
    return sharedManager.exportSettings();
  }

  async importSettings(jsonString: string): Promise<boolean> {
    return sharedManager.importSettings(jsonString);
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
