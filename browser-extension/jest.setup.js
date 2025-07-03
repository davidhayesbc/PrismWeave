// Jest setup file to ensure proper initialization

// Add polyfills for Node.js environment
global.TextEncoder = require('util').TextEncoder;
global.TextDecoder = require('util').TextDecoder;

// Set test environment flag to reduce console output
process.env.NODE_ENV = 'test';

// Test logging configuration
// Set TEST_DEBUG=true to enable debug logging during test development
// Set TEST_LOG_LEVEL=DEBUG|INFO|WARN|ERROR to control verbosity
if (process.env.TEST_DEBUG === 'true') {
  console.log('🧪 Test debug mode enabled');
  process.env.TEST_LOG_LEVEL = process.env.TEST_LOG_LEVEL || 'DEBUG';
} else {
  // Suppress test logger output in normal test runs
  process.env.TEST_LOG_LEVEL = process.env.TEST_LOG_LEVEL || 'ERROR';
}

// Set up proper global environment for browser extension tests
global.chrome = {
  storage: {
    sync: {
      get: jest.fn(),
      set: jest.fn(),
    },
    local: {
      get: jest.fn(),
      set: jest.fn(),
    },
  },
  runtime: {
    getManifest: jest.fn(() => ({ version: '1.0.0' })),
    sendMessage: jest.fn(),
    onMessage: {
      addListener: jest.fn(),
    },
  },
  tabs: {
    query: jest.fn(),
    sendMessage: jest.fn(),
  },
};

// Ensure window and globalThis are available
if (typeof window === 'undefined') {
  global.window = {};
}

if (typeof globalThis === 'undefined') {
  global.globalThis = global;
}

// Suppress console output in tests unless debug mode is enabled
if (process.env.TEST_DEBUG !== 'true') {
  // Store original console methods
  const originalConsole = {
    log: console.log,
    info: console.info,
    warn: console.warn,
    error: console.error,
    debug: console.debug,
  };

  // Override console methods to filter test noise
  console.log = (...args) => {
    // Allow specific test-related logs
    const message = args[0];
    if (
      typeof message === 'string' &&
      (message.includes('[TEST-') ||
        message.includes('🧪') ||
        message.includes('✅') ||
        message.includes('❌'))
    ) {
      originalConsole.log(...args);
    }
    // Suppress other console.log in tests
  };

  console.info = (...args) => {
    const message = args[0];
    if (typeof message === 'string' && message.includes('[TEST-')) {
      originalConsole.info(...args);
    }
  };

  // Always show warnings and errors
  console.warn = originalConsole.warn;
  console.error = originalConsole.error;
  console.debug = originalConsole.debug;

  // Restore original console in afterAll if needed
  global.__originalConsole = originalConsole;
}
