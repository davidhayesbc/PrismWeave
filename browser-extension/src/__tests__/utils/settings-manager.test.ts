import { SettingsManager } from '../../utils/settings-manager';
import { cleanupTest, createTestSettings, mockChromeAPIs } from '../test-helpers';

describe('SettingsManager - Load/Save Operations', () => {
  let manager: SettingsManager;
  let chrome: any;

  beforeEach(() => {
    chrome = mockChromeAPIs();
    (global as any).chrome = chrome; // Ensure chrome is globally available
    manager = new SettingsManager();
  });

  afterEach(() => {
    cleanupTest();
  });
  test('A.1.1 Verify all schema fields have default values', async () => {
    const defaults = await manager.getDefaults();
    const expectedDefaults = createTestSettings();

    expect(defaults).toMatchObject(expectedDefaults);
    Object.keys(expectedDefaults).forEach(key => {
      expect(defaults).toHaveProperty(key, (expectedDefaults as any)[key]);
    });
  });

  test('A.1.2 Test loading when storage is empty', async () => {
    chrome.storage.sync.get.mockImplementation((keys: any, callback: any) => {
      callback({});
    });

    const settings = await manager.getSettings();
    expect(settings).toEqual({});
    expect(chrome.storage.sync.get).toHaveBeenCalledWith(
      ['prismWeaveSettings'],
      expect.any(Function)
    );
  });

  test('A.1.3 Verify schema validation on load', async () => {
    chrome.storage.sync.get.mockImplementation((keys: any, callback: any) => {
      callback({
        prismWeaveSettings: {
          githubToken: 12345, // should be string
          githubRepo: 'invalid repo format', // should match pattern
          defaultFolder: 'not-a-valid-folder', // not in options
          autoCommit: 'yes', // should be boolean
        },
      });
    });

    const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();

    const settings = await manager.getSettings();
    expect(settings).toEqual({
      githubToken: 12345,
      githubRepo: 'invalid repo format',
      defaultFolder: 'not-a-valid-folder',
      autoCommit: 'yes',
    });
    expect(consoleWarnSpy).toHaveBeenCalledWith(
      'SettingsManager: Settings validation failed:',
      expect.arrayContaining([
        expect.stringContaining('Invalid type for githubToken'),
        expect.stringContaining('Invalid format for githubRepo'),
        expect.stringContaining('Invalid value for defaultFolder'),
        expect.stringContaining('Invalid type for autoCommit'),
      ])
    );
    consoleWarnSpy.mockRestore();
  });
  test('A.2.2 Test saving valid settings', async () => {
    chrome.storage.sync.get.mockImplementation((keys: any, callback: any) => {
      callback({}); // Return empty settings for current state
    });
    chrome.storage.sync.set.mockImplementation((data: any, callback: any) => {
      callback();
    });

    const testSettings = createTestSettings({
      autoCommit: false,
      defaultFolder: 'tech',
      captureImages: false,
    });

    const result = await manager.updateSettings(testSettings);
    expect(result).toBe(true);
    expect(chrome.storage.sync.set).toHaveBeenCalledWith(
      { prismWeaveSettings: expect.objectContaining(testSettings) },
      expect.any(Function)
    );
  });

  test('A.3.1 Validate settings with correct types', () => {
    const validSettings = createTestSettings({
      autoCommit: true,
      defaultFolder: 'tech',
      githubRepo: 'owner/repo',
    });

    const validation = manager.validateSettings(validSettings);
    expect(validation.isValid).toBe(true);
    expect(validation.errors).toEqual([]);
  });

  test('A.3.2 Validate settings with incorrect types', () => {
    const invalidSettings = {
      autoCommit: 'yes', // should be boolean
      githubRepo: 'invalid-format', // should match pattern
    };

    const validation = manager.validateSettings(invalidSettings as any);
    expect(validation.isValid).toBe(false);
    expect(validation.errors.length).toBeGreaterThan(0);
  });

  test('A.4.1 Handle storage errors gracefully', async () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

    chrome.runtime.lastError = { message: 'Storage quota exceeded' };
    chrome.storage.sync.get.mockImplementation((keys: any, callback: any) => {
      callback({});
    });

    const settings = await manager.getSettings();
    expect(settings).toEqual({});

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'SettingsManager: Error getting settings:',
      expect.any(Error)
    );

    consoleErrorSpy.mockRestore();
  });

  test('A.4.3 Reset settings to defaults', async () => {
    chrome.storage.sync.set.mockImplementation((data: any, callback: any) => {
      callback();
    });

    const result = await manager.resetSettings();
    expect(result).toBe(true);

    const defaults = await manager.getDefaults();
    expect(chrome.storage.sync.set).toHaveBeenCalledWith(
      { prismWeaveSettings: defaults },
      expect.any(Function)
    );
  });
  test('A.5.1 Export settings (sanitized)', async () => {
    chrome.storage.sync.get.mockImplementation((keys: any, callback: any) => {
      callback({
        prismWeaveSettings: createTestSettings({
          githubToken: 'secret-token',
          autoCommit: true,
          defaultFolder: 'tech',
        }),
      });
    });

    const exported = await manager.exportSettings();
    const parsed = JSON.parse(exported);

    expect(parsed.githubToken).toBe('[REDACTED]');
    expect(parsed.autoCommit).toBe(true);
    expect(parsed.defaultFolder).toBe('tech');
  });

  test('A.6.1 Import settings successfully', async () => {
    chrome.storage.sync.get.mockImplementation((keys: any, callback: any) => {
      callback({}); // Return empty settings for current state
    });
    chrome.storage.sync.set.mockImplementation((data: any, callback: any) => {
      callback();
    });

    const importData = JSON.stringify(
      createTestSettings({
        autoCommit: false,
        defaultFolder: 'business',
      })
    );

    const result = await manager.importSettings(importData);
    expect(result).toBe(true);
  });

  test('A.6.3 Import invalid JSON fails gracefully', async () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

    const invalidJson = '{ invalid json }';

    const result = await manager.importSettings(invalidJson);
    expect(result).toBe(false);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'SettingsManager: Error importing settings:',
      expect.any(SyntaxError)
    );

    consoleErrorSpy.mockRestore();
  });
});
