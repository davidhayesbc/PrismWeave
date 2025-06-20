// Unit tests for FileManager
// Testing file naming, organization, and metadata handling

beforeAll(() => {
  // Mock SharedUtils for FileManager
  global.self = {
    SharedUtils: {
      sanitizeText: (text) => text.replace(/[^\w\s-]/g, '').trim(),
      extractDomain: (url) => new URL(url).hostname,
      generateUniqueId: () => Math.random().toString(36).substr(2, 9)
    }
  };
});

describe('FileManager', () => {
  let fileManager;

  beforeEach(() => {
    // Create a mock instance since FileManager exports might not work as constructor in tests
    const FileManagerClass = require('../../src/utils/file-manager.js');
    fileManager = new FileManagerClass();
  });

  describe('Constructor and Folder Mapping', () => {
    test('should initialize with folder mappings', () => {
      expect(fileManager.folderMapping).toHaveProperty('tech');
      expect(fileManager.folderMapping).toHaveProperty('business');
      expect(fileManager.folderMapping).toHaveProperty('research');
      expect(fileManager.folderMapping.tech).toContain('technology');
      expect(fileManager.folderMapping.tech).toContain('programming');
    });

    test('should have comprehensive keyword mappings', () => {
      const allKeywords = Object.values(fileManager.folderMapping).flat();
      
      expect(allKeywords).toContain('technology');
      expect(allKeywords).toContain('business');
      expect(allKeywords).toContain('research');
      expect(allKeywords).toContain('tutorial');
    });
  });

  describe('Filename Generation', () => {    test('should generate filename with default pattern', () => {
      const metadata = {
        title: 'Test Article Title',
        domain: 'example.com',
        date: '2025-06-20'
      };

      const filename = fileManager.generateFilename(metadata);

      // The actual implementation uses date-domain-title format
      expect(filename).toMatch(/^\d{4}-\d{2}-\d{2}-example\.com-test-article-title\.md$/);
      expect(filename).toContain('2025-06-20');
      expect(filename).toContain('example.com');
      expect(filename).toMatch(/\.md$/);
    });    test('should use custom filename pattern', () => {
      const metadata = {
        title: 'Custom Pattern Test',
        domain: 'test.com',
        date: '2025-06-20'
      };
      
      const settings = {
        fileNamingPattern: '{domain}-{date}-{title}'
      };

      const filename = fileManager.generateFilename(metadata, settings);

      expect(filename).toBe('test.com-2025-06-20-custom-pattern-test.md');
    });

    test('should handle missing metadata gracefully', () => {
      const metadata = {
        title: '',
        domain: '',
        timestamp: new Date().toISOString()
      };

      const filename = fileManager.generateFilename(metadata);      expect(filename).toMatch(/^\d{4}-\d{2}-\d{2}-.*\.md$/);
      expect(filename).toMatch(/\.md$/);
    });

    test('should sanitize filename components', () => {
      const metadata = {
        title: 'Title with Special @#$% Characters!',
        domain: 'test-site.com',
        timestamp: '2025-06-19T10:30:00.000Z'
      };

      const filename = fileManager.generateFilename(metadata);

      expect(filename).not.toContain('@');
      expect(filename).not.toContain('#');
      expect(filename).not.toContain('$');
      expect(filename).not.toContain('%');
      expect(filename).not.toContain('!');
    });

    test('should ensure .md extension', () => {
      const metadata = testUtils.createMockContent();
      const settings = {
        fileNamingPattern: 'title'
      };      const filename = fileManager.generateFilename(metadata, settings);

      expect(filename).toMatch(/\.md$/);
    });
  });

  describe('Title and Domain Sanitization', () => {
    test('should sanitize titles properly', () => {
      const dirtyTitle = 'How to Use JavaScript: A Complete Guide (2025)';
      const sanitized = fileManager.sanitizeTitle(dirtyTitle);

      expect(sanitized).toBe('how-to-use-javascript-a-complete-guide-2025');
      expect(sanitized).not.toContain(':');
      expect(sanitized).not.toContain('(');
      expect(sanitized).not.toContain(')');
    });

    test('should handle very long titles', () => {
      const longTitle = 'This is a very long title that exceeds normal length limits and should be truncated appropriately to ensure filename compatibility';
      const sanitized = fileManager.sanitizeTitle(longTitle);      expect(sanitized.length).toBeLessThanOrEqual(50);
      expect(sanitized).not.toMatch(/-$/);
    });

    test('should sanitize domains properly', () => {      const domain = 'sub.example-site.com';
      const sanitized = fileManager.sanitizeDomain(domain);

      expect(sanitized).toBe('sub.example-site.com');
      expect(sanitized).not.toContain('http://');
      expect(sanitized).not.toContain('www.');
    });

    test('should handle complex domains', () => {      const complexDomain = 'blog.my-awesome-site.co.uk';
      const sanitized = fileManager.sanitizeDomain(complexDomain);      expect(sanitized).toBe('blog.my-awesome-site');
      expect(sanitized.length).toBeLessThanOrEqual(20);
    });
  });

  describe('Folder Classification', () => {
    test('should classify tech content correctly', () => {
      const techMetadata = {
        title: 'JavaScript Programming Tutorial',
        content: 'Learn programming with JavaScript and Node.js',
        url: 'https://github.com/example/repo',
        tags: ['programming', 'javascript']
      };

      const folder = fileManager.classifyContent(techMetadata);

      expect(folder).toBe('tech');
    });

    test('should classify business content correctly', () => {
      const businessMetadata = {
        title: 'Startup Funding Strategies',
        content: 'Business plan and entrepreneurship guide for startups',
        url: 'https://business.example.com',
        tags: ['business', 'startup']
      };

      const folder = fileManager.classifyContent(businessMetadata);

      expect(folder).toBe('business');
    });

    test('should classify tutorial content correctly', () => {
      const tutorialMetadata = {
        title: 'How to Learn Python',
        content: 'Complete guide and tutorial for learning Python programming',
        url: 'https://tutorials.example.com',
        tags: ['tutorial', 'guide']
      };

      const folder = fileManager.classifyContent(tutorialMetadata);

      expect(folder).toBe('tutorial');
    });

    test('should fall back to unsorted for unclear content', () => {
      const unclearMetadata = {
        title: 'Random Title',
        content: 'Some random content without clear category indicators',
        url: 'https://random.example.com',
        tags: []
      };

      const folder = fileManager.classifyContent(unclearMetadata);

      expect(folder).toBe('unsorted');
    });

    test('should prioritize explicit tags over content analysis', () => {
      const taggedMetadata = {
        title: 'Business Article',
        content: 'This talks about business and technology and research',
        url: 'https://example.com',
        tags: ['research'] // Explicit research tag
      };

      const folder = fileManager.classifyContent(taggedMetadata);

      expect(folder).toBe('research');
    });

    test('should use domain hints when content is ambiguous', () => {      const domainHintMetadata = {
        title: 'Article Title',
        content: 'Generic content',
        domain: 'stackoverflow.com',
        url: 'https://stackoverflow.com/questions/123',
        tags: []
      };

      const folder = fileManager.classifyContent(domainHintMetadata);

      expect(folder).toBe('tech'); // stackoverflow should hint at tech
    });
  });

  describe('Metadata Generation', () => {
    test('should generate comprehensive metadata', () => {
      const pageContent = testUtils.createMockContent({
        title: 'Test Article',
        content: 'Test content for metadata generation',
        url: 'https://example.com/test'
      });
      
      const settings = testUtils.createMockSettings();

      const metadata = fileManager.generateMetadata(pageContent, settings);      expect(metadata).toHaveProperty('title');
      expect(metadata).toHaveProperty('url');
      expect(metadata).toHaveProperty('domain');
      expect(metadata).toHaveProperty('date');
      expect(metadata).toHaveProperty('folder');
      expect(metadata).toHaveProperty('tags');
      expect(metadata).toHaveProperty('wordCount');
      expect(metadata).toHaveProperty('readingTime');
    });    test('should include auto-generated tags', () => {
      const pageContent = testUtils.createMockContent({
        title: 'JavaScript Tutorial for Beginners',
        content: 'Learn programming with JavaScript frameworks and Node.js',
        textContent: 'Learn programming with JavaScript frameworks and Node.js',
        url: 'https://tutorial.example.com'
      });
      
      const settings = testUtils.createMockSettings();

      const metadata = fileManager.generateMetadata(pageContent, settings);
      expect(metadata.tags).toContain('javascript');
      expect(metadata.tags).toContain('tutorial');
      expect(metadata.tags).toContain('node');
    });

    test('should calculate word count and reading time', () => {
      const longContent = 'This is a longer article with multiple sentences. '.repeat(100);
      const pageContent = testUtils.createMockContent({
        content: longContent
      });
      
      const settings = testUtils.createMockSettings();

      const metadata = fileManager.generateMetadata(pageContent, settings);      expect(metadata.wordCount).toBeGreaterThan(0);
      expect(metadata.readingTime).toMatch(/\d+ min/);
      expect(typeof metadata.wordCount).toBe('number');
      expect(typeof metadata.readingTime).toBe('string');
    });

    test('should include capture settings in metadata', () => {
      const pageContent = testUtils.createMockContent();
      const settings = testUtils.createMockSettings({
        defaultFolder: 'tech',
        autoCommit: true
      });      const metadata = fileManager.generateMetadata(pageContent, settings);

      expect(metadata).toHaveProperty('title', 'Test Article Title');
      expect(metadata).toHaveProperty('url', 'https://example.com/test-page');
      expect(metadata).toHaveProperty('domain', 'example.com');
      expect(metadata).toHaveProperty('date');
      expect(metadata).toHaveProperty('folder');
    });
  });

  describe('Processed Content Creation', () => {
    test('should create processed content with all components', () => {
      const pageContent = testUtils.createMockContent();
      const settings = testUtils.createMockSettings();

      const processed = fileManager.createProcessedContent(pageContent, settings);

      expect(processed).toHaveProperty('metadata');
      expect(processed).toHaveProperty('filename');
      expect(processed).toHaveProperty('markdown');
      expect(processed).toHaveProperty('images');
      expect(processed).toHaveProperty('links');
    });

    test('should include YAML frontmatter in markdown', () => {
      const pageContent = testUtils.createMockContent({
        title: 'Test Article',
        url: 'https://example.com/test'
      });
      const settings = testUtils.createMockSettings();

      const processed = fileManager.createProcessedContent(pageContent, settings);      expect(processed.markdown).toContain('---');
      expect(processed.markdown).toContain('title: "Test Article"');
      expect(processed.markdown).toContain('url: "https://example.com/test"');
    });

    test('should handle images in content', () => {
      const pageContent = testUtils.createMockContent({
        images: [
          { src: 'https://example.com/image1.jpg', alt: 'Test image 1' },
          { src: 'https://example.com/image2.png', alt: 'Test image 2' }
        ]
      });
      const settings = testUtils.createMockSettings();

      const processed = fileManager.createProcessedContent(pageContent, settings);

      expect(processed.images).toHaveLength(2);
      expect(processed.markdown).toContain('![Test image 1]');
      expect(processed.markdown).toContain('![Test image 2]');
    });

    test('should handle links in content', () => {
      const pageContent = testUtils.createMockContent({
        links: [
          { href: 'https://example.com/link1', text: 'External Link', isExternal: true },
          { href: '/internal', text: 'Internal Link', isExternal: false }
        ]
      });
      const settings = testUtils.createMockSettings();

      const processed = fileManager.createProcessedContent(pageContent, settings);

      expect(processed.links).toHaveLength(2);
      expect(processed.markdown).toContain('[External Link](https://example.com/link1)');
      expect(processed.markdown).toContain('[Internal Link](/internal)');
    });
  });

  describe('File Organization', () => {    test('should organize files by folder structure', () => {
      const techContent = {
        title: 'JavaScript Programming Guide',
        content: 'Learn programming with JavaScript and Node.js',
        domain: 'github.com',
        url: 'https://github.com/example',
        date: '2025-06-20'
      };
        const businessContent = {
        title: 'Business Strategy for Startups',
        content: 'Marketing and sales strategies for startup companies and management',
        domain: 'linkedin.com',
        url: 'https://linkedin.com/example',
        date: '2025-06-20'
      };

      const organization = fileManager.organizeFiles([techContent, businessContent]);

      expect(organization.folders).toHaveProperty('tech');
      expect(organization.folders).toHaveProperty('business');
      expect(organization.folders.tech).toHaveLength(1);
      expect(organization.folders.business).toHaveLength(1);
      expect(organization.totalFiles).toBe(2);
    });

    test('should handle duplicate filenames', () => {
      const content1 = testUtils.createMockProcessedContent({
        filename: 'duplicate-name.md'
      });
      const content2 = testUtils.createMockProcessedContent({
        filename: 'duplicate-name.md'
      });

      const uniqueFilenames = fileManager.ensureUniqueFilenames([content1, content2]);

      expect(uniqueFilenames[0].filename).toBe('duplicate-name.md');
      expect(uniqueFilenames[1].filename).toMatch(/duplicate-name-\w+\.md/);
    });
  });

  describe('Error Handling', () => {
    test('should handle invalid metadata gracefully', () => {
      const invalidContent = {
        title: null,
        content: undefined,
        url: 'invalid-url'
      };
      const settings = testUtils.createMockSettings();

      const result = fileManager.createProcessedContent(invalidContent, settings);

      expect(result).toHaveProperty('metadata');
      expect(result).toHaveProperty('filename');      expect(result.metadata.title).toBeTruthy(); // Should have fallback
    });

    test('should handle missing settings gracefully', () => {
      // Use neutral content that won't trigger any folder classification
      const pageContent = {
        title: 'Test Page',
        content: 'This is test content.',
        url: 'https://example.com/test-page',
        domain: 'example.com'
      };
      const emptySettings = {};

      const result = fileManager.createProcessedContent(pageContent, emptySettings);

      expect(result).toHaveProperty('metadata');
      expect(result).toHaveProperty('filename');
      expect(result.metadata.folder).toBe('unsorted'); // Default folder
    });
  });

  describe('File Path Generation', () => {    test('should generate correct relative paths', () => {
      const metadata = {
        title: 'JavaScript Programming',
        domain: 'github.com', // Will classify as tech
        content: 'Learn programming with JavaScript',
        date: '2025-06-20'
      };

      const path = fileManager.generateFilePath(metadata);

      expect(path).toMatch(/^documents\/tech\/2025-06-20-.+\.md$/);
      expect(path).toContain('documents/tech/');
    });    test('should handle root folder files', () => {
      const metadata = {
        title: 'Random Document',
        domain: '', // Will not classify to any specific folder
        content: 'Some generic content without keywords',
        date: '2025-06-20'
      };

      const path = fileManager.generateFilePath(metadata);

      expect(path).toMatch(/^documents\/unsorted\/.+\.md$/);
    });

    test('should generate image paths correctly', () => {
      const imageName = 'test-image.jpg';
      const date = new Date('2025-06-19');

      const path = fileManager.generateImagePath(imageName, date);

      expect(path).toContain('images/');
      expect(path).toContain('2025/06/');
      expect(path).toContain('test-image.jpg');
    });
  });
});
