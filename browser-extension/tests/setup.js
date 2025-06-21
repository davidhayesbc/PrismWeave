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

// Mock SharedUtils for ContentExtractor and other modules
global.SharedUtils = {
  sanitizeText: jest.fn((text) => text ? text.trim() : ''),
  extractDomain: jest.fn((url) => {
    try {
      return new URL(url).hostname;
    } catch {
      return 'unknown';
    }
  }),
  estimateReadingTime: jest.fn((text) => {
    if (!text) return 0;
    return Math.ceil(text.split(' ').length / 200);
  }),
  sanitizeForFilename: jest.fn((text, maxLength = 50) => {
    if (!text) return 'untitled';
    return text
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
      .substring(0, maxLength);
  }),
  sanitizeDomain: jest.fn((domain) => {
    if (!domain) return 'unknown';
    return domain
      .toLowerCase()
      .replace(/^www\./, '')
      .replace(/[^a-z0-9.-]/g, '');
  }),
  isValidUrl: jest.fn((url) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }),
  resolveUrl: jest.fn((url, baseUrl = '') => {
    try {
      return new URL(url, baseUrl || 'https://example.com').href;
    } catch {
      return url;
    }
  }),
  isValidImageUrl: jest.fn((url) => {
    const imageExtensions = /\.(jpg|jpeg|png|gif|svg|webp|bmp)(\?.*)?$/i;
    return imageExtensions.test(url) || url.includes('image') || url.includes('img');
  }),
  truncateText: jest.fn((text, maxLength = 100) => {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }),
  delay: jest.fn((ms) => Promise.resolve()),
  formatBytes: jest.fn((bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }),
  validateSettings: jest.fn((settings) => ({ isValid: true, errors: [] })),
  logError: jest.fn()
};

// Make SharedUtils available in both window and self contexts
if (typeof window !== 'undefined') {
  window.SharedUtils = global.SharedUtils;
}
if (typeof self !== 'undefined') {
  self.SharedUtils = global.SharedUtils;
}

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
global.window = {
  ...global,
  document: global.document,
  location: {
    href: 'https://example.com/test-page',
    hostname: 'example.com',
    pathname: '/test-page',
    search: '',
    hash: ''
  },
  addEventListener: jest.fn(),
  removeEventListener: jest.fn()
};

// Mock ContentExtractor class
class MockContentExtractor {
  constructor() {
    this.readabilitySelectors = ['article', 'main', '.content'];
    this.unwantedSelectors = ['script', 'style', 'nav'];
  }

  extractPageContent = jest.fn().mockImplementation((document) => ({
    title: document?.title || 'Test Page Title',
    content: 'This is test content for the article.',
    markdown: '# Test Page Title\n\nThis is test content for the article.',
    url: document?.URL || 'https://example.com/test-page',
    domain: 'example.com',
    timestamp: new Date().toISOString(),
    wordCount: 10,
    readingTime: 1,
    quality: 8,
    images: [],
    links: [],
    textContent: 'This is test content for the article.'
  }));

  extractPageContentWithTimeout = jest.fn().mockImplementation(async (document, timeoutMs = 5000) => {
    return this.extractPageContent(document);
  });

  cleanContent = jest.fn().mockImplementation((html) => html);
  extractText = jest.fn().mockImplementation((element) => element?.textContent || '');
  calculateReadingTime = jest.fn().mockImplementation(() => 1);
  analyzeQuality = jest.fn().mockImplementation(() => 8);
  analyzePageStructure = jest.fn().mockImplementation((document) => ({
    hasMainContent: true,
    contentSections: 3,
    quality: 8,
    readabilityScore: 7.5
  }));
}

global.window.ContentExtractor = MockContentExtractor;
global.ContentExtractor = MockContentExtractor;

// Mock PrismWeaveContent class for content script tests
class MockPrismWeaveContent {
  constructor() {
    this.contentExtractor = new MockContentExtractor();
    this.captureIndicator = {
      style: { display: 'none' },
      textContent: '',
      remove: jest.fn()
    };
  }

  captureCurrentPage = jest.fn().mockImplementation(async () => ({
    success: true,
    content: this.contentExtractor.extractPageContent(global.document)
  }));

  highlightMainContent = jest.fn();
  
  showCaptureIndicator = jest.fn().mockImplementation(() => {
    this.captureIndicator.style.display = 'block';
  });

  hideCaptureIndicator = jest.fn().mockImplementation(() => {
    this.captureIndicator.style.display = 'none';
  });

  updateCaptureProgress = jest.fn().mockImplementation((percentage, message) => {
    this.captureIndicator.textContent = `${percentage}% - ${message}`;
  });

  analyzePageStructure = jest.fn().mockImplementation(async () => {
    return this.contentExtractor.analyzePageStructure(global.document);
  });
}

global.window.PrismWeaveContent = MockPrismWeaveContent;
global.PrismWeaveContent = MockPrismWeaveContent;

// Mock document object with proper Jest mocks
const createMockElement = (options = {}) => ({
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  style: { display: 'none', ...options.style },
  textContent: options.textContent || '',
  innerHTML: options.innerHTML || '',
  value: options.value || '',
  disabled: false,
  className: options.className || '',
  id: options.id || '',
  tagName: options.tagName || 'DIV',
  setAttribute: jest.fn(),
  getAttribute: jest.fn().mockReturnValue(null),
  removeAttribute: jest.fn(),
  hasAttribute: jest.fn(() => false),
  appendChild: jest.fn(),
  removeChild: jest.fn(),
  remove: jest.fn(),
  click: jest.fn(),
  focus: jest.fn(),
  blur: jest.fn(),
  cloneNode: jest.fn().mockImplementation((deep) => createMockElement(options)),
  querySelector: jest.fn(),
  querySelectorAll: jest.fn(() => []),
  children: [],
  childNodes: [],
  innerText: options.innerText || options.textContent || '',
  offsetWidth: options.offsetWidth || 100,
  offsetHeight: options.offsetHeight || 100,
  ...options
});

// Create a configurable document mock that extends existing jsdom document
const createMockDocument = () => {
  // Use existing document from jsdom if available, otherwise create mock
  const mockDoc = global.document || {};
  
  // Override methods with jest mocks
  mockDoc.getElementById = jest.fn().mockImplementation((id) => createMockElement({ id }));
  mockDoc.querySelector = jest.fn().mockImplementation(() => createMockElement());
  mockDoc.querySelectorAll = jest.fn(() => []);
  mockDoc.createElement = jest.fn().mockImplementation((tagName) => createMockElement({ tagName: tagName.toUpperCase() }));
  mockDoc.addEventListener = jest.fn();
  mockDoc.removeEventListener = jest.fn();
  
  // Create a mock body if it doesn't exist
  if (!mockDoc.body) {
    mockDoc.body = createMockElement({
      tagName: 'BODY',
      innerHTML: '<div>Test content</div>',
      textContent: 'Test content',
      cloneNode: jest.fn(() => createMockElement({
        tagName: 'BODY',
        querySelectorAll: jest.fn(() => []),
        querySelector: jest.fn(),
        appendChild: jest.fn(),
        removeChild: jest.fn()
      }))
    });
  }

  // Set title and URL properties safely - try to use defineProperty, fallback to direct assignment
  try {
    Object.defineProperty(mockDoc, 'title', {
      value: 'Test Page Title',
      writable: true,
      configurable: true
    });
  } catch (e) {
    mockDoc.title = 'Test Page Title';
  }
  
  try {
    Object.defineProperty(mockDoc, 'URL', {
      value: 'https://example.com/test-page',
      writable: true,
      configurable: true
    });
  } catch (e) {
    mockDoc.URL = 'https://example.com/test-page';
  }

  // Handle location property carefully - jsdom might have made it non-configurable
  try {
    Object.defineProperty(mockDoc, 'location', {
      value: {
        href: 'https://example.com/test-page',
        hostname: 'example.com',
        pathname: '/test-page',
        search: '',
        hash: ''
      },
      writable: true,
      configurable: true
    });
  } catch (e) {
    // If we can't redefine, try to modify existing location
    if (mockDoc.location) {
      try {
        mockDoc.location.href = 'https://example.com/test-page';
        mockDoc.location.hostname = 'example.com';
        mockDoc.location.pathname = '/test-page';
        mockDoc.location.search = '';
        mockDoc.location.hash = '';
      } catch (locationError) {
        // Create a completely new location object if modification fails
        mockDoc.location = {
          href: 'https://example.com/test-page',
          hostname: 'example.com',
          pathname: '/test-page',
          search: '',
          hash: ''
        };
      }
    } else {
      mockDoc.location = {
        href: 'https://example.com/test-page',
        hostname: 'example.com',
        pathname: '/test-page',
        search: '',
        hash: ''
      };
    }
  }

  return mockDoc;
};

// Don't override global.document immediately - let jsdom set it up first
// We'll apply our mocks in beforeEach

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

// Setup and cleanup functions
beforeEach(() => {
  // Apply document mocks before each test
  if (!global.document.__prismweave_mocked) {
    const mockedDoc = createMockDocument();
    // Copy mocked methods to existing document
    Object.assign(global.document, mockedDoc);
    global.document.__prismweave_mocked = true;
  }
});

// Clean up after each test and reset document
afterEach(() => {
  jest.clearAllMocks();
  fetch.mockClear();
  
  // Reset document properties to defaults safely
  try {
    global.document.title = 'Test Page Title';
  } catch (e) {
    // Ignore if property is non-writable
  }
  
  try {
    global.document.URL = 'https://example.com/test-page';
  } catch (e) {
    // Ignore if property is non-writable
  }

  // Reset location properties safely
  if (global.document.location) {
    try {
      global.document.location.href = 'https://example.com/test-page';
      global.document.location.hostname = 'example.com';
      global.document.location.pathname = '/test-page';
      global.document.location.search = '';
      global.document.location.hash = '';
    } catch (e) {
      // If we can't modify, create new location object
      try {
        global.document.location = {
          href: 'https://example.com/test-page',
          hostname: 'example.com',
          pathname: '/test-page',
          search: '',
          hash: ''
        };
      } catch (e2) {
        // Ignore if we can't set location at all
      }
    }
  }
  
  // Reset document mocks if they exist
  if (global.document.getElementById && global.document.getElementById.mockClear) {
    global.document.getElementById.mockClear();
  }
  if (global.document.querySelector && global.document.querySelector.mockClear) {
    global.document.querySelector.mockClear();
  }
  if (global.document.querySelectorAll && global.document.querySelectorAll.mockClear) {
    global.document.querySelectorAll.mockClear();
  }
  if (global.document.createElement && global.document.createElement.mockClear) {
    global.document.createElement.mockClear();
  }
  if (global.document.addEventListener && global.document.addEventListener.mockClear) {
    global.document.addEventListener.mockClear();
  }
  if (global.document.removeEventListener && global.document.removeEventListener.mockClear) {
    global.document.removeEventListener.mockClear();
  }
    // Reset ContentExtractor mocks
  if (global.window.ContentExtractor) {
    const mockInstance = new global.window.ContentExtractor();
    mockInstance.extractPageContent.mockClear();
    mockInstance.extractPageContentWithTimeout.mockClear();
    mockInstance.cleanContent.mockClear();
    mockInstance.extractText.mockClear();
    mockInstance.calculateReadingTime.mockClear();
    mockInstance.analyzeQuality.mockClear();
    mockInstance.analyzePageStructure.mockClear();
  }

  // Reset PrismWeaveContent mocks
  if (global.window.PrismWeaveContent) {
    const mockInstance = new global.window.PrismWeaveContent();
    mockInstance.captureCurrentPage.mockClear();
    mockInstance.highlightMainContent.mockClear();
    mockInstance.showCaptureIndicator.mockClear();
    mockInstance.hideCaptureIndicator.mockClear();
    mockInstance.updateCaptureProgress.mockClear();
    mockInstance.analyzePageStructure.mockClear();
  }
});

// Provide a helper function to reset document for tests
global.resetDocument = () => {
  const mockedDoc = createMockDocument();
  Object.assign(global.document, mockedDoc);
  global.document.__prismweave_mocked = true;
};
