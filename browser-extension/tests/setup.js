// Test setup for PrismWeave Browser Extension
// Mocks and global test utilities

// Mock Chrome APIs
global.chrome = {
  runtime: {
    onInstalled: {
      addListener: jest.fn()
    },
    onMessage: {
      addListener: jest.fn()
    },
    sendMessage: jest.fn((message, callback) => {
      if (callback) callback({ success: true });
      return Promise.resolve({ success: true });
    }),
    onStartup: {
      addListener: jest.fn()
    },
    getManifest: jest.fn(() => ({
      version: '1.0.0',
      name: 'PrismWeave Test'
    }))
  },
  storage: {
    local: {
      get: jest.fn((keys, callback) => {
        const result = {};
        if (typeof keys === 'string') {
          result[keys] = null;
        } else if (Array.isArray(keys)) {
          keys.forEach(key => result[key] = null);
        }
        if (callback) callback(result);
        return Promise.resolve(result);
      }),
      set: jest.fn((data, callback) => {
        if (callback) callback();
        return Promise.resolve();
      }),
      remove: jest.fn((keys, callback) => {
        if (callback) callback();
        return Promise.resolve();
      }),
      clear: jest.fn((callback) => {
        if (callback) callback();
        return Promise.resolve();
      })
    },
    sync: {
      get: jest.fn((keys, callback) => {
        const result = {};
        if (typeof keys === 'string') {
          result[keys] = null;
        } else if (Array.isArray(keys)) {
          keys.forEach(key => result[key] = null);
        }
        if (callback) callback(result);
        return Promise.resolve(result);
      }),
      set: jest.fn((data, callback) => {
        if (callback) callback();
        return Promise.resolve();
      })
    }
  },
  tabs: {
    query: jest.fn((queryInfo, callback) => {
      const tabs = [{
        id: 1,
        url: 'https://example.com/test-page',
        title: 'Test Page Title',
        active: true,
        windowId: 1
      }];
      if (callback) callback(tabs);
      return Promise.resolve(tabs);
    }),
    get: jest.fn((tabId, callback) => {
      const tab = {
        id: tabId,
        url: 'https://example.com/test-page',
        title: 'Test Page Title',
        active: true,
        windowId: 1
      };
      if (callback) callback(tab);
      return Promise.resolve(tab);
    }),
    executeScript: jest.fn((tabId, details, callback) => {
      if (callback) callback(['script executed']);
      return Promise.resolve(['script executed']);
    }),
    insertCSS: jest.fn((tabId, details, callback) => {
      if (callback) callback();
      return Promise.resolve();
    })
  },
  action: {
    onClicked: {
      addListener: jest.fn()
    },
    setBadgeText: jest.fn(),
    setBadgeBackgroundColor: jest.fn()
  },  scripting: {
    executeScript: jest.fn((injection) => {
      return Promise.resolve([{ result: 'script executed' }]);
    }),
    insertCSS: jest.fn((injection) => {
      return Promise.resolve();
    })
  },
  downloads: {
    download: jest.fn((options, callback) => {
      if (callback) callback(1);
      return Promise.resolve(1);
    })
  },
  permissions: {
    contains: jest.fn((permissions, callback) => {
      if (callback) callback(true);
      return Promise.resolve(true);
    }),
    request: jest.fn((permissions, callback) => {
      if (callback) callback(true);
      return Promise.resolve(true);
    })
  }
};

// Mock fetch for GitHub API calls
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ message: 'Success' }),
    text: () => Promise.resolve('Success'),
    headers: {
      get: jest.fn(() => 'application/json')
    }
  })
);

// Mock console methods for cleaner test output
const originalConsole = { ...console };
global.console = {
  ...originalConsole,
  log: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  debug: jest.fn(),
  group: jest.fn(),
  groupEnd: jest.fn()
};

// Mock importScripts for service worker testing
global.importScripts = jest.fn();

// Mock self for service worker context
global.self = {
  PrismWeaveLogger: {
    createLogger: jest.fn(() => ({
      debug: jest.fn(),
      info: jest.fn(),
      warn: jest.fn(),
      error: jest.fn(),
      group: jest.fn(),
      groupEnd: jest.fn()
    }))
  }
};

// Mock window object for content scripts  
global.window = global;

// Mock document object with proper Jest mocks
global.document = {
  getElementById: jest.fn().mockImplementation((id) => ({
    addEventListener: jest.fn(),
    style: { display: 'none' },
    textContent: '',
    value: '',
    disabled: false,
    className: '',
    id: id,
    setAttribute: jest.fn(),
    getAttribute: jest.fn(),
    removeAttribute: jest.fn(),
    hasAttribute: jest.fn(() => false),
    appendChild: jest.fn(),
    removeChild: jest.fn(),
    click: jest.fn(),
    focus: jest.fn(),
    blur: jest.fn()
  })),
  querySelector: jest.fn().mockImplementation(() => ({
    style: {},
    textContent: '',
    appendChild: jest.fn(),
    removeChild: jest.fn(),
    addEventListener: jest.fn(),
    remove: jest.fn()
  })),
  querySelectorAll: jest.fn(() => []),
  createElement: jest.fn(() => ({
    style: {},
    appendChild: jest.fn(),
    removeChild: jest.fn(),
    addEventListener: jest.fn(),
    remove: jest.fn(),
    getAttribute: jest.fn(),
    setAttribute: jest.fn(),
    hasAttribute: jest.fn(() => false),
    removeAttribute: jest.fn(),
    cloneNode: jest.fn(),
    textContent: '',
    id: '',
    className: ''
  })),
  body: {
    appendChild: jest.fn(),
    removeChild: jest.fn(),
    cloneNode: jest.fn(() => ({
      querySelectorAll: jest.fn(() => []),
      querySelector: jest.fn(),
      appendChild: jest.fn(),
      removeChild: jest.fn()
    })),
    innerHTML: '<div>Test content</div>',
    textContent: 'Test content'
  },
  title: 'Test Page Title',
  URL: 'https://example.com/test-page'
};

// Test utilities
global.testUtils = {
  // Create mock settings
  createMockSettings: (overrides = {}) => ({
    repositoryPath: 'owner/repo',
    githubToken: 'test-token',
    githubRepo: 'owner/repo',
    defaultFolder: 'unsorted',
    fileNamingPattern: 'YYYY-MM-DD-domain-title',
    customFolder: '',
    customNamingPattern: '',
    autoCommit: true,
    autoPush: false,
    commitMessage: 'Add captured content: {title}',
    commitMessageTemplate: 'Add: {domain} - {title}',
    enableKeyboardShortcuts: true,
    showNotifications: true,
    autoClosePopup: true,
    captureImages: true,
    maxImageSize: 5242880,
    captureTimeout: 30000,
    removeAds: true,
    removeNavigation: true,
    preserveLinks: true,
    customSelectors: '',
    ...overrides
  }),

  // Create mock tab
  createMockTab: (overrides = {}) => ({
    id: 1,
    url: 'https://example.com/test-page',
    title: 'Test Page Title',
    active: true,
    windowId: 1,
    ...overrides
  }),
  // Create mock page content
  createMockContent: (overrides = {}) => ({
    title: 'Test Article Title',
    content: 'This is test content for the article.',
    markdown: '# Test Article Title\n\nThis is test content for the article.',
    url: 'https://example.com/test-page',
    domain: 'example.com',
    timestamp: new Date().toISOString(),
    wordCount: 10,
    readingTime: 1,
    quality: 8,
    images: [],
    links: [],
    textContent: 'This is test content for the article.',
    ...overrides
  }),

  // Create mock processed content
  createMockProcessedContent: (overrides = {}) => ({
    metadata: {
      title: 'Test Article Title',
      url: 'https://example.com/test-page',
      domain: 'example.com',
      timestamp: new Date().toISOString(),
      folder: 'unsorted',
      tags: ['test'],
      wordCount: 100,
      readingTime: 1
    },
    filename: '2025-06-19-example-test-article-title.md',
    markdown: '# Test Article Title\n\nThis is test content.',
    ...overrides
  }),

  // Wait for async operations
  waitFor: (ms = 100) => new Promise(resolve => setTimeout(resolve, ms)),

  // Mock GitHub API responses
  mockGitHubAPI: {
    success: () => ({
      ok: true,
      status: 200,
      json: () => Promise.resolve({
        name: 'test-repo',
        full_name: 'owner/repo',
        permissions: { push: true }
      })
    }),
    error: (status = 404, message = 'Not Found') => ({
      ok: false,
      status,
      json: () => Promise.resolve({ message })
    })
  }
};

// Setup DOM environment
// Note: jsdom is provided by jest-environment-jsdom, no need for jsdom-global

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
  fetch.mockClear();
});
