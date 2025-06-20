// Additional test utilities for PrismWeave Browser Extension
// Specialized mocks and helpers for complex testing scenarios

const testUtilsExtended = {
  // Mock complex GitHub API responses
  createGitHubAPIResponses: {
    // Repository information
    repository: (overrides = {}) => ({
      id: 123456,
      name: 'repo',
      full_name: 'owner/repo',
      private: false,
      permissions: {
        admin: true,
        push: true,
        pull: true
      },
      default_branch: 'main',
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-06-19T10:00:00Z',
      ...overrides
    }),

    // User information
    user: (overrides = {}) => ({
      id: 12345,
      login: 'testuser',
      name: 'Test User',
      email: 'test@example.com',
      avatar_url: 'https://github.com/images/avatar.png',
      ...overrides
    }),

    // File content response
    fileContent: (content, overrides = {}) => ({
      name: 'test-file.md',
      path: 'documents/test-file.md',
      sha: 'abc123def456',
      size: content.length,
      url: 'https://api.github.com/repos/owner/repo/contents/documents/test-file.md',
      html_url: 'https://github.com/owner/repo/blob/main/documents/test-file.md',
      git_url: 'https://api.github.com/repos/owner/repo/git/blobs/abc123def456',
      download_url: 'https://raw.githubusercontent.com/owner/repo/main/documents/test-file.md',
      type: 'file',
      content: Buffer.from(content).toString('base64'),
      encoding: 'base64',
      ...overrides
    }),

    // Create/update file response
    fileOperation: (action = 'created', overrides = {}) => ({
      content: {
        name: 'test-file.md',
        path: 'documents/test-file.md',
        sha: 'new123sha456',
        size: 1024,
        url: 'https://api.github.com/repos/owner/repo/contents/documents/test-file.md',
        html_url: 'https://github.com/owner/repo/blob/main/documents/test-file.md',
        git_url: 'https://api.github.com/repos/owner/repo/git/blobs/new123sha456',
        download_url: 'https://raw.githubusercontent.com/owner/repo/main/documents/test-file.md',
        type: 'file'
      },
      commit: {
        sha: 'commit123sha456',
        author: {
          name: 'Test User',
          email: 'test@example.com',
          date: new Date().toISOString()
        },
        committer: {
          name: 'Test User',
          email: 'test@example.com',
          date: new Date().toISOString()
        },
        message: 'Add captured content: Test Article',
        tree: {
          sha: 'tree123sha456',
          url: 'https://api.github.com/repos/owner/repo/git/trees/tree123sha456'
        },
        url: 'https://api.github.com/repos/owner/repo/git/commits/commit123sha456',
        verification: {
          verified: false,
          reason: 'unsigned',
          signature: null,
          payload: null
        }
      },
      ...overrides
    }),

    // Rate limit response
    rateLimit: (remaining = 0) => ({
      message: 'API rate limit exceeded',
      documentation_url: 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'
    }),

    // Error responses
    errors: {
      unauthorized: () => ({
        message: 'Bad credentials',
        documentation_url: 'https://docs.github.com/rest'
      }),
      notFound: () => ({
        message: 'Not Found',
        documentation_url: 'https://docs.github.com/rest'
      }),
      forbidden: () => ({
        message: 'Repository access blocked',
        documentation_url: 'https://docs.github.com/rest'
      })
    }
  },

  // Mock complex page content
  createComplexPageContent: (options = {}) => {
    const {
      type = 'article',
      imageCount = 3,
      linkCount = 5,
      hasVideo = false,
      hasCodeBlocks = false,
      language = 'en'
    } = options;

    const images = Array(imageCount).fill(null).map((_, i) => ({
      src: `https://example.com/image${i + 1}.jpg`,
      alt: `Test image ${i + 1}`,
      width: 800,
      height: 600,
      caption: `Caption for image ${i + 1}`
    }));

    const links = Array(linkCount).fill(null).map((_, i) => ({
      href: `https://example.com/link${i + 1}`,
      text: `Link ${i + 1}`,
      isExternal: i % 2 === 0,
      title: `Title for link ${i + 1}`
    }));

    let content = `This is a test ${type} with comprehensive content for testing purposes. `;
    content += 'It contains multiple paragraphs, formatting, and various elements. ';
    content += 'The content is designed to test the extraction and processing capabilities. ';

    if (hasCodeBlocks) {
      content += '\n\n```javascript\nconst test = "code block";\nconsole.log(test);\n```\n\n';
    }

    if (hasVideo) {
      content += 'This article also contains embedded video content. ';
    }

    return {
      title: `Test ${type.charAt(0).toUpperCase() + type.slice(1)} Title`,
      content,
      url: `https://example.com/test-${type}`,
      domain: 'example.com',
      timestamp: new Date().toISOString(),
      images,
      links,
      metadata: {
        type,
        language,
        hasVideo,
        hasCodeBlocks,
        author: 'Test Author',
        publishDate: '2025-06-19',
        tags: ['test', type, 'example']
      },
      wordCount: content.split(' ').length,
      readingTime: Math.ceil(content.split(' ').length / 200),
      quality: {
        score: 85,
        hasStructure: true,
        hasImages: imageCount > 0,
        hasLinks: linkCount > 0
      }
    };
  },

  // Mock browser tabs with various states
  createMockTabs: {
    // Standard web page
    webPage: (overrides = {}) => ({
      id: 1,
      windowId: 1,
      index: 0,
      url: 'https://example.com/article',
      title: 'Test Article Title',
      active: true,
      pinned: false,
      highlighted: false,
      incognito: false,
      status: 'complete',
      ...overrides
    }),

    // Chrome internal page
    chromePage: (overrides = {}) => ({
      id: 2,
      windowId: 1,
      index: 1,
      url: 'chrome://settings/',
      title: 'Chrome Settings',
      active: false,
      pinned: false,
      highlighted: false,
      incognito: false,
      status: 'complete',
      ...overrides
    }),

    // Extension page
    extensionPage: (overrides = {}) => ({
      id: 3,
      windowId: 1,
      index: 2,
      url: 'chrome-extension://abcdef123456/popup.html',
      title: 'Extension Popup',
      active: false,
      pinned: false,
      highlighted: false,
      incognito: false,
      status: 'complete',
      ...overrides
    }),

    // Loading page
    loadingPage: (overrides = {}) => ({
      id: 4,
      windowId: 1,
      index: 3,
      url: 'https://example.com/loading',
      title: 'Loading...',
      active: false,
      pinned: false,
      highlighted: false,
      incognito: false,
      status: 'loading',
      ...overrides
    })
  },

  // Mock Chrome runtime scenarios
  mockChromeRuntimeScenarios: {
    // Normal operation
    normal: () => {
      chrome.runtime.lastError = null;
      chrome.runtime.sendMessage.mockImplementation((message, callback) => {
        if (callback) callback({ success: true });
        return Promise.resolve({ success: true });
      });
    },

    // Extension context invalidated
    invalidated: () => {
      chrome.runtime.lastError = { message: 'Extension context invalidated' };
      chrome.runtime.sendMessage.mockImplementation((message, callback) => {
        if (callback) callback({ success: false, error: 'Extension context invalidated' });
        return Promise.reject(new Error('Extension context invalidated'));
      });
    },

    // Message passing failure
    messageFailure: () => {
      chrome.runtime.lastError = { message: 'Could not establish connection' };
      chrome.runtime.sendMessage.mockImplementation((message, callback) => {
        if (callback) callback({ success: false, error: 'Could not establish connection' });
        return Promise.reject(new Error('Could not establish connection'));
      });
    },

    // Permission denied
    permissionDenied: () => {
      chrome.runtime.lastError = { message: 'Permission denied' };
      chrome.permissions.contains.mockImplementation((permissions, callback) => {
        callback(false);
      });
    }
  },

  // Mock network scenarios for fetch
  mockNetworkScenarios: {
    // Successful responses
    success: (data = { message: 'Success' }) => {
      fetch.mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: () => Promise.resolve(data),
        text: () => Promise.resolve(JSON.stringify(data)),
        headers: {
          get: (header) => {
            if (header === 'content-type') return 'application/json';
            if (header === 'x-ratelimit-remaining') return '4999';
            return null;
          }
        }
      });
    },

    // Network error
    networkError: () => {
      fetch.mockRejectedValue(new Error('Network error'));
    },

    // Timeout
    timeout: () => {
      fetch.mockImplementation(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      );
    },

    // Rate limiting
    rateLimited: () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 429,
        statusText: 'Too Many Requests',
        json: () => Promise.resolve({
          message: 'API rate limit exceeded',
          documentation_url: 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'
        }),
        headers: {
          get: (header) => {
            if (header === 'x-ratelimit-remaining') return '0';
            if (header === 'x-ratelimit-reset') return String(Date.now() + 3600000);
            return null;
          }
        }
      });
    },

    // Server error
    serverError: () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({
          message: 'Internal server error',
          error: 'Something went wrong'
        })
      });
    }
  },

  // Performance testing utilities
  performanceUtils: {
    // Measure execution time
    measureTime: async (fn) => {
      const start = performance.now();
      const result = await fn();
      const end = performance.now();
      return {
        result,
        duration: end - start
      };
    },

    // Create large content for testing
    createLargeContent: (sizeKB = 100) => {
      const baseText = 'This is a test sentence with approximately ten words. ';
      const wordsPerKB = Math.ceil(1024 / (baseText.length / baseText.split(' ').length));
      const repetitions = Math.ceil((sizeKB * wordsPerKB) / baseText.split(' ').length);
      
      return {
        title: 'Large Content Test Article',
        content: baseText.repeat(repetitions),
        url: 'https://example.com/large-content',
        domain: 'example.com',
        timestamp: new Date().toISOString()
      };
    },

    // Memory usage tracker
    trackMemory: () => {
      if (typeof performance !== 'undefined' && performance.memory) {
        return {
          used: performance.memory.usedJSHeapSize,
          total: performance.memory.totalJSHeapSize,
          limit: performance.memory.jsHeapSizeLimit
        };
      }
      return null;
    }
  },

  // Test data generators
  generators: {
    // Random string
    randomString: (length = 10) => {
      return Math.random().toString(36).substring(2, length + 2);
    },

    // Random URL
    randomUrl: (domain = 'example.com') => {
      const path = testUtilsExtended.generators.randomString(8);
      return `https://${domain}/${path}`;
    },

    // Random GitHub repo
    randomRepo: () => {
      const owner = testUtilsExtended.generators.randomString(6);
      const repo = testUtilsExtended.generators.randomString(8);
      return `${owner}/${repo}`;
    },

    // Random settings
    randomSettings: () => ({
      repositoryPath: testUtilsExtended.generators.randomRepo(),
      githubToken: 'ghp_' + testUtilsExtended.generators.randomString(32),
      githubRepo: testUtilsExtended.generators.randomRepo(),
      defaultFolder: ['tech', 'business', 'research', 'tutorial'][Math.floor(Math.random() * 4)],
      autoCommit: Math.random() > 0.5,
      fileNamingPattern: 'YYYY-MM-DD-domain-title'
    })
  },

  // Async testing helpers
  asyncHelpers: {
    // Wait for condition
    waitForCondition: async (condition, timeout = 5000, interval = 100) => {
      const start = Date.now();
      while (Date.now() - start < timeout) {
        if (await condition()) {
          return true;
        }
        await new Promise(resolve => setTimeout(resolve, interval));
      }
      throw new Error(`Condition not met within ${timeout}ms`);
    },

    // Wait for multiple promises with timeout
    waitForAll: async (promises, timeout = 10000) => {
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Timeout')), timeout)
      );
      
      return Promise.race([
        Promise.all(promises),
        timeoutPromise
      ]);
    },

    // Retry operation
    retry: async (operation, maxAttempts = 3, delay = 1000) => {
      let lastError;
      
      for (let i = 0; i < maxAttempts; i++) {
        try {
          return await operation();
        } catch (error) {
          lastError = error;
          if (i < maxAttempts - 1) {
            await new Promise(resolve => setTimeout(resolve, delay));
          }
        }
      }
      
      throw lastError;
    }
  }
};

// Export for use in tests
if (typeof module !== 'undefined' && module.exports) {
  module.exports = testUtilsExtended;
} else if (typeof global !== 'undefined') {
  global.testUtilsExtended = testUtilsExtended;
}
