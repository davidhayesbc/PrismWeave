// Jest setup file to ensure proper initialization

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
