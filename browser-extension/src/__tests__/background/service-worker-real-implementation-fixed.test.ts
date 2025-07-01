// Real Implementation Testing for Service Worker
// This file tests the actual service worker implementation via code execution

import { jest } from '@jest/globals';
import {
  cleanupTest,
  executeServiceWorkerCode,
  mockFetch,
  mockGetURL,
  setupChromeEnvironment,
} from '../test-helpers';

describe('X. ServiceWorker - Real Implementation Testing (Simplified)', () => {
  let chromeMock: any;
  let serviceWorkerAPI: any;

  beforeEach(async () => {
    // Set up Chrome environment with working storage
    chromeMock = setupChromeEnvironment();

    // Reset mocks
    mockFetch.mockReset();
    mockGetURL.mockReset();

    // Execute service worker code and get API
    serviceWorkerAPI = executeServiceWorkerCode(chrome);

    // Wait for initialization
    await new Promise(resolve => setTimeout(resolve, 10));
  });

  afterEach(() => {
    cleanupTest();
    jest.clearAllMocks();
  });

  describe('X.1 Settings Management', () => {
    test('X.1.1 - Should return default settings when storage is empty', async () => {
      const message = { type: 'GET_SETTINGS', timestamp: Date.now() };
      const result = await serviceWorkerAPI.handleMessage(message, {});

      // Verify it returns the actual default settings structure
      expect(result).toEqual({
        githubToken: '',
        githubRepo: '',
        autoCommit: true,
        defaultFolder: 'auto',
        customFolder: '',
        fileNamingPattern: 'YYYY-MM-DD-domain-title',
        captureImages: true,
        removeAds: true,
        removeNavigation: true,
        customSelectors: '',
        commitMessageTemplate: 'Add: {domain} - {title}',
        debugMode: false,
        showNotifications: true,
        enableKeyboardShortcuts: true,
      });
    });

    test('SW.2 - Should update settings properly', async () => {
      // Update some settings
      const updateMessage = {
        type: 'UPDATE_SETTINGS',
        data: {
          githubToken: 'test-token',
          debugMode: true,
        },
        timestamp: Date.now(),
      };

      const updateResult = await serviceWorkerAPI.handleMessage(updateMessage, {});
      expect(updateResult).toEqual({ success: true });

      // Verify settings were updated
      const getMessage = { type: 'GET_SETTINGS', timestamp: Date.now() };
      const getResult = await serviceWorkerAPI.handleMessage(getMessage, {});

      expect(getResult.githubToken).toBe('test-token');
      expect(getResult.debugMode).toBe(true);
      expect(getResult.autoCommit).toBe(true); // Default preserved
    });

    test('SW.3 - Should validate settings correctly', async () => {
      // Test validation with empty settings (invalid)
      const validateMessage = { type: 'VALIDATE_SETTINGS', timestamp: Date.now() };
      const invalidResult = await serviceWorkerAPI.handleMessage(validateMessage, {});

      expect(invalidResult).toEqual({
        valid: false,
        errors: ['GitHub token is required', 'GitHub repository is required'],
      });

      // Update with valid settings
      await serviceWorkerAPI.handleMessage(
        {
          type: 'UPDATE_SETTINGS',
          data: {
            githubToken: 'ghp_validtoken123',
            githubRepo: 'user/repository',
          },
        },
        {}
      );

      // Test validation with valid settings
      const validResult = await serviceWorkerAPI.handleMessage(validateMessage, {});
      expect(validResult).toEqual({
        valid: true,
        errors: [],
      });
    });

    test('SW.4 - Should reject invalid UPDATE_SETTINGS data', async () => {
      // Test cases that should fail validation
      const invalidMessages = [
        { type: 'UPDATE_SETTINGS' }, // No data
        { type: 'UPDATE_SETTINGS', data: null },
        { type: 'UPDATE_SETTINGS', data: 'string' },
        { type: 'UPDATE_SETTINGS', data: 123 },
      ];

      for (const invalidMessage of invalidMessages) {
        await expect(serviceWorkerAPI.handleMessage(invalidMessage, {})).rejects.toThrow(
          'Invalid settings data provided'
        );
      }
    });
  });

  describe('GitHub Connection Testing', () => {
    test('SW.5 - Should fail GitHub connection test with empty settings', async () => {
      const message = { type: 'TEST_CONNECTION', timestamp: Date.now() };
      const result = await serviceWorkerAPI.handleMessage(message, {});

      expect(result).toEqual({
        success: false,
        status: 'failed',
        error: 'GitHub token and repository are required',
        timestamp: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/),
      });
    });

    test('SW.6 - Should test GitHub connection with valid settings', async () => {
      // Set up valid settings first
      await serviceWorkerAPI.handleMessage(
        {
          type: 'UPDATE_SETTINGS',
          data: {
            githubToken: 'ghp_validtoken123',
            githubRepo: 'testuser/testrepo',
          },
        },
        {}
      );

      // Mock successful GitHub API responses
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () =>
            Promise.resolve({
              login: 'testuser',
              type: 'User',
            }),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () =>
            Promise.resolve({
              full_name: 'testuser/testrepo',
              private: false,
              permissions: { admin: true, push: true, pull: true },
            }),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([]),
        } as Response);

      const message = { type: 'TEST_CONNECTION', timestamp: Date.now() };
      const result = await serviceWorkerAPI.handleMessage(message, {});

      expect(result).toEqual({
        success: true,
        status: 'connected',
        message: 'GitHub connection test successful',
        details: {
          user: 'testuser',
          userType: 'User',
          repository: 'testuser/testrepo',
          repositoryPrivate: false,
          hasWriteAccess: true,
          permissions: { admin: true, push: true, pull: true },
        },
        timestamp: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/),
      });

      // Verify GitHub API calls were made
      expect(mockFetch).toHaveBeenCalledTimes(3);
    });

    test('SW.7 - Should handle GitHub API authentication errors', async () => {
      // Set up settings with invalid token
      await serviceWorkerAPI.handleMessage(
        {
          type: 'UPDATE_SETTINGS',
          data: {
            githubToken: 'invalid_token',
            githubRepo: 'testuser/testrepo',
          },
        },
        {}
      );

      // Mock 401 Unauthorized response
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ message: 'Bad credentials' }),
      } as Response);

      const message = { type: 'TEST_CONNECTION', timestamp: Date.now() };
      const result = await serviceWorkerAPI.handleMessage(message, {});

      expect(result).toEqual({
        success: false,
        status: 'failed',
        error: 'Invalid GitHub token (401)',
        timestamp: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/),
      });
    });
  });

  describe('Library and Status Operations', () => {
    test('SW.8 - Should fetch TurndownService library successfully', async () => {
      const libraryContent =
        '// TurndownService library content\nvar TurndownService = function() {};';

      mockGetURL.mockReturnValue('chrome-extension://test-id/libs/turndown.min.js');
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(libraryContent),
      } as Response);

      const message = { type: 'GET_TURNDOWN_LIBRARY', timestamp: Date.now() };
      const result = await serviceWorkerAPI.handleMessage(message, {});

      expect(result).toEqual({
        success: true,
        content: libraryContent,
        timestamp: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/),
      });
    });

    test('SW.9 - Should return extension status', async () => {
      const message = { type: 'GET_STATUS', timestamp: Date.now() };
      const result = await serviceWorkerAPI.handleMessage(message, {});

      expect(result).toEqual({
        initialized: true,
        version: '1.0.0',
        timestamp: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/),
      });
    });

    test('SW.10 - Should handle TEST message', async () => {
      const message = { type: 'TEST', timestamp: Date.now() };
      const result = await serviceWorkerAPI.handleMessage(message, {});

      expect(result).toEqual({
        message: 'Service worker is working',
        timestamp: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/),
        version: '1.0.0',
      });
    });
  });

  describe('Error Handling', () => {
    test('SW.11 - Should handle invalid message formats', async () => {
      const invalidMessages = [null, undefined, {}, { data: 'no type field' }, { type: 123 }];

      for (const invalidMessage of invalidMessages) {
        await expect(serviceWorkerAPI.handleMessage(invalidMessage, {})).rejects.toThrow(
          'Invalid message format'
        );
      }
    });

    test('SW.12 - Should handle unknown message types', async () => {
      const unknownMessage = { type: 'UNKNOWN_TYPE', timestamp: Date.now() };

      await expect(serviceWorkerAPI.handleMessage(unknownMessage, {})).rejects.toThrow(
        'Unknown message type: UNKNOWN_TYPE'
      );
    });

    test('SW.13 - Should handle empty message type', async () => {
      const emptyTypeMessage = { type: '', timestamp: Date.now() };

      await expect(serviceWorkerAPI.handleMessage(emptyTypeMessage, {})).rejects.toThrow(
        'Unknown message type: '
      );
    });
  });

  describe('Performance and Concurrency', () => {
    test('SW.14 - Should handle concurrent requests', async () => {
      const messages = [
        { type: 'GET_SETTINGS' },
        { type: 'GET_STATUS' },
        { type: 'VALIDATE_SETTINGS' },
      ];

      const results = await Promise.all(
        messages.map(msg => serviceWorkerAPI.handleMessage(msg, {}))
      );

      expect(results).toHaveLength(3);
      expect(results[0]).toHaveProperty('githubToken', '');
      expect(results[1]).toHaveProperty('initialized', true);
      expect(results[2]).toHaveProperty('valid', false);
    });

    test('SW.15 - Should maintain state consistency', async () => {
      // Initial state
      const initial = await serviceWorkerAPI.handleMessage({ type: 'GET_SETTINGS' }, {});
      expect(initial.debugMode).toBe(false);

      // Update state
      await serviceWorkerAPI.handleMessage(
        {
          type: 'UPDATE_SETTINGS',
          data: { debugMode: true },
        },
        {}
      );

      // Verify state change
      const updated = await serviceWorkerAPI.handleMessage({ type: 'GET_SETTINGS' }, {});
      expect(updated.debugMode).toBe(true);
    });
  });
});
