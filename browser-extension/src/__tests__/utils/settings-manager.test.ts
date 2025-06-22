import { SettingsManager } from '../../utils/settings-manager';

// Minimal chrome namespace/type declarations for Jest test environment
declare namespace chrome {
  namespace runtime {
    interface LastError {
      message: string;
    }
  }
}

// Mock Chrome APIs for testing
(global as any).chrome = {
  storage: {
    sync: {
      get: jest.fn(),
      set: jest.fn(),
    },
  },
  runtime: {
    lastError: undefined as chrome.runtime.LastError | undefined,
  },
};

describe('SettingsManager - Load/Save Operations', () => {
  let manager: SettingsManager;

  beforeEach(() => {
    manager = new SettingsManager();
    jest.clearAllMocks();
    (global as any).chrome.runtime.lastError = undefined;
  });
  test('A.1.1 Verify all schema fields have default values', async () => {
    // Test that all schema fields have proper default values
    const defaults = await manager.getDefaults();

    // List of expected default keys and values (functional settings only)
    const expectedDefaults = {
      githubToken: '',
      githubRepo: '',
      defaultFolder: 'unsorted',
      customFolder: '',
      fileNamingPattern: 'YYYY-MM-DD-domain-title',
      autoCommit: true,
      captureImages: true,
      removeAds: true,
      removeNavigation: true,
      customSelectors: '',
      commitMessageTemplate: 'Add: {domain} - {title}',
      debugMode: false,
      showNotifications: true,
      enableKeyboardShortcuts: true,
    };

    expect(defaults).toMatchObject(expectedDefaults);
    // All keys present
    Object.keys(expectedDefaults).forEach(key => {
      expect(defaults).toHaveProperty(key, (expectedDefaults as any)[key]);
    });
  });

  test('A.1.2 Test loading when storage is empty', async () => {
    // Mock storage to return empty object
    ((global as any).chrome.storage.sync.get as jest.Mock).mockImplementation((keys, callback) => {
      callback({});
    });

    const settings = await manager.getSettings();
    expect(settings).toEqual({});
    expect((global as any).chrome.storage.sync.get).toHaveBeenCalledWith(
      ['prismWeaveSettings'],
      expect.any(Function)
    );
  });
  // Not in TESTING_PLAN.md, assigned A.2.2 (Test fallback to local storage) or next available if not matching plan
  test('A.2.2 Test saving valid settings', async () => {
    // Mock storage set to succeed
    ((global as any).chrome.storage.sync.set as jest.Mock).mockImplementation((data, callback) => {
      callback();
    });

    const testSettings = {
      autoCommit: false,
      defaultFolder: 'tech',
      captureImages: false,
    };

    const result = await manager.updateSettings(testSettings);
    expect(result).toBe(true);
    expect((global as any).chrome.storage.sync.set).toHaveBeenCalledWith(
      { prismWeaveSettings: expect.objectContaining(testSettings) },
      expect.any(Function)
    );
  });
  test('A.3.1 Validate settings with correct types', () => {
    const validSettings = {
      autoCommit: true,
      defaultFolder: 'tech',
      githubRepo: 'owner/repo',
    };

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
  test('A.4.3 Reset settings to defaults', async () => {
    // Mock storage set to succeed
    ((global as any).chrome.storage.sync.set as jest.Mock).mockImplementation((data, callback) => {
      callback();
    });

    const result = await manager.resetSettings();
    expect(result).toBe(true);

    const defaults = await manager.getDefaults();
    expect((global as any).chrome.storage.sync.set).toHaveBeenCalledWith(
      { prismWeaveSettings: defaults },
      expect.any(Function)
    );
  });
  test('A.4.1 Handle storage errors gracefully', async () => {
    // Suppress expected console.error output during this test
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

    // Mock storage to fail
    (global as any).chrome.runtime.lastError = { message: 'Storage quota exceeded' };
    ((global as any).chrome.storage.sync.get as jest.Mock).mockImplementation((keys, callback) => {
      callback({});
    });

    const settings = await manager.getSettings();
    expect(settings).toEqual({});

    // Verify that console.error was called as expected
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'SettingsManager: Error getting settings:',
      expect.any(Error)
    );

    // Restore console.error
    consoleErrorSpy.mockRestore();
  });
  test('A.5.1 Export settings (sanitized)', async () => {
    // Mock storage to return settings with sensitive data
    ((global as any).chrome.storage.sync.get as jest.Mock).mockImplementation((keys, callback) => {
      callback({
        prismWeaveSettings: {
          githubToken: 'secret-token',
          autoCommit: true,
          defaultFolder: 'tech',
        },
      });
    });

    const exported = await manager.exportSettings();
    const parsed = JSON.parse(exported);

    expect(parsed.githubToken).toBe('[REDACTED]');
    expect(parsed.autoCommit).toBe(true);
    expect(parsed.defaultFolder).toBe('tech');
  });
  test('A.6.1 Import settings successfully', async () => {
    // Mock storage set to succeed
    ((global as any).chrome.storage.sync.set as jest.Mock).mockImplementation((data, callback) => {
      callback();
    });

    const importData = JSON.stringify({
      autoCommit: false,
      defaultFolder: 'business',
    });

    const result = await manager.importSettings(importData);
    expect(result).toBe(true);
  });
  test('A.6.3 Import invalid JSON fails gracefully', async () => {
    // Suppress expected console.error output during this test
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

    const invalidJson = '{ invalid json }';

    const result = await manager.importSettings(invalidJson);
    expect(result).toBe(false);

    // Verify that console.error was called as expected
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'SettingsManager: Error importing settings:',
      expect.any(SyntaxError)
    );

    // Restore console.error
    consoleErrorSpy.mockRestore();
  });
});
