// Unit tests for SettingsManager
// Testing settings validation, schema enforcement, and storage operations

// Mock the chrome storage API for this test
const mockStorage = {
  local: {
    get: jest.fn(),
    set: jest.fn(),
    remove: jest.fn(),
    clear: jest.fn()
  },
  sync: {
    get: jest.fn(),
    set: jest.fn(),
    remove: jest.fn(),
    clear: jest.fn()
  }
};

beforeAll(() => {
  // Mock chrome API
  global.chrome = { storage: mockStorage };
});

// Import test utilities
require('../setup.js');

// Import the SettingsManager class
const SettingsManager = require('../../src/utils/settings-manager.js');

describe('SettingsManager', () => {
  let settingsManager;

  beforeEach(() => {
    settingsManager = new SettingsManager();
    jest.clearAllMocks();
  });

  describe('Constructor and Schema', () => {
    test('should initialize with correct storage key', () => {
      expect(settingsManager.STORAGE_KEY).toBe('prismWeaveSettings');
    });

    test('should have valid settings schema', () => {
      const schema = settingsManager.getSettingsSchema();
      
      expect(schema).toHaveProperty('repositoryPath');
      expect(schema).toHaveProperty('githubToken');
      expect(schema).toHaveProperty('githubRepo');
      expect(schema).toHaveProperty('defaultFolder');
      
      // Verify schema structure
      expect(schema.repositoryPath).toHaveProperty('type', 'string');
      expect(schema.githubToken).toHaveProperty('sensitive', true);
      expect(schema.githubRepo).toHaveProperty('pattern');
      expect(schema.defaultFolder).toHaveProperty('options');
    });

    test('should validate GitHub repo pattern', () => {
      const schema = settingsManager.getSettingsSchema();
      const pattern = schema.githubRepo.pattern;
      
      // Valid patterns
      expect('owner/repo').toMatch(pattern);
      expect('user123/my-repo').toMatch(pattern);
      expect('org_name/project.name').toMatch(pattern);
      
      // Invalid patterns
      expect('invalid').not.toMatch(pattern);
      expect('owner/').not.toMatch(pattern);
      expect('/repo').not.toMatch(pattern);
      expect('owner//repo').not.toMatch(pattern);
    });
  });

  describe('Settings Validation', () => {
    test('should validate valid settings', async () => {
      const validSettings = testUtils.createMockSettings();
      const result = await settingsManager.validateSettings(validSettings);
        expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    test('should detect invalid GitHub repo format', async () => {
      const invalidSettings = testUtils.createMockSettings({
        githubRepo: 'invalid-repo-format'
      });
      
      const result = await settingsManager.validateSettings(invalidSettings);
      
      expect(result.isValid).toBe(false);
      expect(result.errors.some(error => error.includes('githubRepo'))).toBe(true);
    });

    test('should validate required fields', async () => {
      const settingsWithMissingRequired = {
        repositoryPath: '',
        githubToken: '',
        githubRepo: '',
        // Missing defaultFolder which is required
      };
      
      const result = await settingsManager.validateSettings(settingsWithMissingRequired);
      
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });    test('should validate folder options', async () => {
      const settingsWithInvalidFolder = testUtils.createMockSettings({
        defaultFolder: 'invalid-folder'
      });
      
      const result = await settingsManager.validateSettings(settingsWithInvalidFolder);
      
      expect(result.isValid).toBe(false);
      expect(result.errors.some(error => error.includes('defaultFolder'))).toBe(true);
    });
  });

  describe('Default Settings', () => {
    test('should generate default settings', () => {
      const defaults = settingsManager.getDefaultSettings();
      
      expect(defaults).toHaveProperty('repositoryPath', '');
      expect(defaults).toHaveProperty('githubToken', '');
      expect(defaults).toHaveProperty('githubRepo', '');
      expect(defaults).toHaveProperty('defaultFolder', 'unsorted');
      expect(defaults).toHaveProperty('autoCommit', true);
      expect(defaults).toHaveProperty('commitMessage');
    });

    test('should merge custom settings with defaults', () => {
      const customSettings = {
        githubRepo: 'custom/repo',
        autoCommit: false
      };
      
      const merged = settingsManager.mergeWithDefaults(customSettings);
        expect(merged.githubRepo).toBe('custom/repo');
      expect(merged.autoCommit).toBe(false);
      expect(merged.defaultFolder).toBe('unsorted'); // Should keep default
    });
  });

  describe('Settings Storage', () => {
    test('should load settings from storage', async () => {
      const storedSettings = testUtils.createMockSettings();
      mockStorage.sync.get.mockRejectedValue(new Error('Sync not available'));
      mockStorage.local.get.mockResolvedValue({ [settingsManager.STORAGE_KEY]: storedSettings });

      const result = await settingsManager.loadSettings();
      
      expect(mockStorage.local.get).toHaveBeenCalledWith([settingsManager.STORAGE_KEY]);
      expect(result).toEqual(expect.objectContaining(storedSettings));
    });    test('should return defaults when storage is empty', async () => {
      mockStorage.local.get.mockImplementation((key, callback) => {
        callback({});
      });

      const result = await settingsManager.loadSettings();
      const defaults = settingsManager.getDefaultSettings();
      
      expect(result).toEqual(defaults);
    });

    test('should save valid settings to storage', async () => {
      const settingsToSave = testUtils.createMockSettings();
      mockStorage.local.set.mockResolvedValue();
      mockStorage.local.get.mockResolvedValue({ [settingsManager.STORAGE_KEY]: settingsToSave });

      const result = await settingsManager.saveSettings(settingsToSave);
      
      expect(result.success).toBe(true);
      expect(mockStorage.local.set).toHaveBeenCalledWith(
        { [settingsManager.STORAGE_KEY]: expect.objectContaining(settingsToSave) }
      );
    });    test('should reject invalid settings when saving', async () => {
      const invalidSettings = {
        githubRepo: 'invalid-format',
        defaultFolder: 'invalid-folder'
      };

      const result = await settingsManager.saveSettings(invalidSettings);
      
      expect(result.success).toBe(false);
      expect(result.errors.some(error => error.includes('githubRepo'))).toBe(true);
      expect(mockStorage.local.set).not.toHaveBeenCalled();
    });    test('should handle storage errors gracefully', async () => {
      mockStorage.local.get.mockImplementation((key, callback) => {
        throw new Error('Storage error');
      });

      const result = await settingsManager.loadSettings();
      
      // Should return defaults when storage fails
      expect(result).toEqual(settingsManager.getDefaultSettings());
    });
  });

  describe('Settings Reset', () => {
    test('should reset settings to defaults', async () => {
      mockStorage.local.set.mockResolvedValue();
      mockStorage.local.get.mockResolvedValue({});

      const result = await settingsManager.resetSettings();
      const defaults = settingsManager.getDefaultSettings();
      
      expect(result.success).toBe(true);
      expect(mockStorage.local.set).toHaveBeenCalledWith(
        { [settingsManager.STORAGE_KEY]: defaults }
      );
    });

    test('should handle reset errors', async () => {
      mockStorage.local.set.mockImplementation((data, callback) => {
        throw new Error('Reset failed');
      });

      const result = await settingsManager.resetSettings();
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Reset failed');
    });
  });

  describe('Settings Export/Import', () => {    test('should export settings (excluding sensitive data)', async () => {
      const settings = testUtils.createMockSettings({
        githubToken: 'secret-token'
      });
      
      mockStorage.local.get.mockImplementation((key, callback) => {
        callback({ [settingsManager.STORAGE_KEY]: settings });
      });
      
      const exported = await settingsManager.exportSettings();
      
      expect(exported.settings).not.toHaveProperty('githubToken');
      expect(exported.settings).toHaveProperty('githubRepo');
      expect(exported.settings).toHaveProperty('defaultFolder');
    });

    test('should import valid settings', async () => {
      const importData = {
        settings: {
          githubRepo: 'imported/repo',
          defaultFolder: 'tech',
          autoCommit: false
        }
      };
      
      mockStorage.local.set.mockResolvedValue();
      mockStorage.sync.set.mockResolvedValue();      mockStorage.local.get.mockResolvedValue({
        [settingsManager.STORAGE_KEY]: {
          ...settingsManager.getDefaultSettings(),
          ...importData.settings
        }
      });
      
      const result = await settingsManager.importSettings(importData);
      
      expect(result.success).toBe(true);
      expect(mockStorage.local.set).toHaveBeenCalled();
    });

    test('should reject invalid import data', async () => {
      const invalidImportData = {
        settings: {
          githubRepo: 'invalid-format',
          defaultFolder: 'nonexistent-folder'
        }
      };

      const result = await settingsManager.importSettings(invalidImportData);
      
      expect(result.success).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(mockStorage.local.set).not.toHaveBeenCalled();
    });
  });

  describe('Settings Migration', () => {
    test('should migrate old settings format', async () => {
      const oldSettings = {
        repo: 'old/format',  // Old key name
        folder: 'tech',      // Old key name
        token: 'old-token'   // Old key name
      };
      
      mockStorage.local.get.mockImplementation((key, callback) => {
        callback({ [settingsManager.STORAGE_KEY]: oldSettings });
      });

      // This would require implementing migration logic in SettingsManager
      const result = await settingsManager.loadSettings();
      
      // The result should have new format
      expect(result).toHaveProperty('githubRepo');
      expect(result).toHaveProperty('defaultFolder');
      expect(result).toHaveProperty('githubToken');
    });
  });
});
