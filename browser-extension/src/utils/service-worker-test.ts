// Test script to verify Chrome API access in service worker context
// This simulates the service worker environment to test our fix
// NOTE: This file is a candidate for removal in Phase 4.1 (Dead Code Removal)

import { createLogger } from './logger';

const logger = createLogger('ServiceWorkerTest');

/**
 * Test Chrome API access patterns in service worker context
 * This test verifies that our fixes work correctly
 */
async function testServiceWorkerChromeAccess(): Promise<void> {
  logger.info('Testing Chrome API access in service worker context...');

  // Simulate service worker environment (no window, no global)
  const originalWindow = (globalThis as any).window;
  const originalGlobal = (globalThis as any).global;

  try {
    // Remove window and global to simulate service worker
    delete (globalThis as any).window;
    delete (globalThis as any).global;

    // Make sure chrome is available (simulated)
    (globalThis as any).chrome = {
      storage: {
        sync: {
          get: (keys: any, callback: any) => {
            logger.debug('Mock chrome.storage.sync.get called');
            callback({ test: 'value' });
          },
          set: (data: any, callback: any) => {
            logger.debug('Mock chrome.storage.sync.set called');
            callback();
          },
        },
      },
      runtime: {
        lastError: null,
      },
    };

    // Test settings manager in this context
    const { SettingsManager } = await import('./settings-manager.js');
    const settingsManager = new SettingsManager();

    logger.info('Testing getSettings...');
    const settings = await settingsManager.getSettings();
    logger.info('✓ getSettings succeeded');

    logger.info('Testing updateSettings...');
    await settingsManager.updateSettings({ githubToken: 'test-token', githubRepo: 'test/repo' });
    logger.info('✓ updateSettings succeeded');

    logger.info('✅ All Chrome API access tests passed!');
  } catch (error) {
    logger.error('❌ Chrome API access test failed:', error);
    throw error;
  } finally {
    // Restore original globals
    if (originalWindow !== undefined) {
      (globalThis as any).window = originalWindow;
    }
    if (originalGlobal !== undefined) {
      (globalThis as any).global = originalGlobal;
    }
  }
}

// Export for use in tests or manual execution
export { testServiceWorkerChromeAccess };

// Auto-run if this file is executed directly
if (require.main === module) {
  testServiceWorkerChromeAccess()
    .then(() => {
      logger.info('Service worker Chrome API test completed successfully');
      process.exit(0);
    })
    .catch(error => {
      logger.error('Service worker Chrome API test failed:', error);
      process.exit(1);
    });
}
