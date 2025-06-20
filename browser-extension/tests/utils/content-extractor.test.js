// Unit tests for ContentExtractor
// Testing HTML parsing, content cleaning, and extraction logic

beforeAll(() => {
  // Mock SharedUtils for ContentExtractor
  global.SharedUtils = {
    sanitizeText: (text) => text.trim(),
    extractDomain: (url) => new URL(url).hostname,
    estimateReadingTime: (text) => Math.ceil(text.split(' ').length / 200)
  };
});

describe('ContentExtractor', () => {
  let extractor;
  let mockDocument;

  beforeEach(() => {
    const ContentExtractorClass = require('../../src/utils/content-extractor.js');
    extractor = new ContentExtractorClass();
    
    // Create a more sophisticated mock document
    mockDocument = {
      documentElement: {
        innerHTML: '',
        textContent: '',
        cloneNode: jest.fn(() => mockDocument.documentElement)
      },
      body: {
        innerHTML: '',
        textContent: '',
        cloneNode: jest.fn(() => mockDocument.body)
      },
      createElement: jest.fn((tagName) => ({
        tagName: tagName.toUpperCase(),
        innerHTML: '',
        textContent: '',
        style: {},
        classList: {
          add: jest.fn(),
          remove: jest.fn(),
          contains: jest.fn(() => false),
          value: ''
        },
        setAttribute: jest.fn(),
        getAttribute: jest.fn(() => null),
        removeAttribute: jest.fn(),
        appendChild: jest.fn(),
        removeChild: jest.fn(),
        remove: jest.fn(),
        querySelector: jest.fn(() => null),
        querySelectorAll: jest.fn(() => []),
        parentNode: null,
        childNodes: [],
        children: []
      })),
      querySelector: jest.fn(() => null),
      querySelectorAll: jest.fn(() => []),
      getElementById: jest.fn(() => null),
      title: 'Test Page Title',
      URL: 'https://example.com/test-page'
    };
  });

  describe('Constructor and Selectors', () => {
    test('should initialize with readability selectors', () => {
      expect(extractor.readabilitySelectors).toContain('article');
      expect(extractor.readabilitySelectors).toContain('main');
      expect(extractor.readabilitySelectors).toContain('.content');
    });

    test('should initialize with unwanted selectors', () => {
      expect(extractor.unwantedSelectors).toContain('script');
      expect(extractor.unwantedSelectors).toContain('style');
      expect(extractor.unwantedSelectors).toContain('.ad');
      expect(extractor.unwantedSelectors).toContain('.advertisement');
    });

    test('should initialize with preserve selectors', () => {
      expect(extractor.preserveSelectors).toContain('.article-comments');
      expect(extractor.preserveSelectors).toContain('.author-bio');
    });
  });

  describe('Content Extraction', () => {
    test('should extract basic page content', () => {
      // Setup mock document with basic content
      mockDocument.body.innerHTML = '<div class="content"><h1>Test Title</h1><p>Test content</p></div>';
      mockDocument.querySelector.mockReturnValue({
        innerHTML: '<h1>Test Title</h1><p>Test content</p>',
        textContent: 'Test Title Test content',
        querySelectorAll: jest.fn(() => [])
      });

      const result = extractor.extractPageContent(mockDocument);

      expect(result).toHaveProperty('title');
      expect(result).toHaveProperty('content');
      expect(result).toHaveProperty('url');
      expect(result).toHaveProperty('timestamp');
    });

    test('should prefer article content over generic content', () => {
      const articleContent = {
        innerHTML: '<h1>Article Title</h1><p>Article content</p>',
        textContent: 'Article Title Article content',
        querySelectorAll: jest.fn(() => [])
      };
      
      const genericContent = {
        innerHTML: '<h1>Generic Title</h1><p>Generic content</p>',
        textContent: 'Generic Title Generic content',
        querySelectorAll: jest.fn(() => [])
      };

      mockDocument.querySelector
        .mockReturnValueOnce(articleContent) // First call for article
        .mockReturnValueOnce(genericContent); // Second call for fallback

      const result = extractor.extractPageContent(mockDocument);

      expect(result.content).toContain('Article content');
    });

    test('should handle documents without main content', () => {
      mockDocument.querySelector.mockReturnValue(null);
      mockDocument.body.textContent = 'Fallback body content';

      const result = extractor.extractPageContent(mockDocument);

      expect(result).toHaveProperty('content');
      expect(result.content).toContain('Fallback body content');
    });

    test('should extract metadata from document', () => {
      mockDocument.title = 'Test Article Title';
      mockDocument.URL = 'https://example.com/test-article';
      
      const result = extractor.extractPageContent(mockDocument);

      expect(result.title).toBe('Test Article Title');
      expect(result.url).toBe('https://example.com/test-article');
      expect(result.domain).toBe('example.com');
    });
  });

  describe('Content Cleaning', () => {
    test('should remove unwanted elements', () => {
      const mockElement = {
        querySelectorAll: jest.fn(() => [
          { remove: jest.fn() },
          { remove: jest.fn() }
        ]),
        innerHTML: '<p>Clean content</p>',
        textContent: 'Clean content'
      };

      const cleaned = extractor.cleanContent(mockElement);

      expect(mockElement.querySelectorAll).toHaveBeenCalledWith(
        expect.stringContaining('script')
      );
      expect(cleaned).toBe(mockElement);
    });

    test('should preserve important elements', () => {
      const importantElement = { remove: jest.fn() };
      const regularElement = { remove: jest.fn() };
      
      const mockElement = {
        querySelectorAll: jest.fn()
          .mockReturnValueOnce([importantElement, regularElement]) // unwanted elements
          .mockReturnValueOnce([importantElement]), // preserve elements
        innerHTML: '<p>Content with important info</p>',
        textContent: 'Content with important info'
      };

      const cleaned = extractor.cleanContent(mockElement);

      expect(importantElement.remove).not.toHaveBeenCalled();
      expect(regularElement.remove).toHaveBeenCalled();
    });

    test('should clean HTML attributes', () => {
      const elementWithAttrs = {
        removeAttribute: jest.fn(),
        setAttribute: jest.fn(),
        getAttribute: jest.fn(() => 'test-value'),
        hasAttribute: jest.fn(() => true),
        attributes: [
          { name: 'onclick' },
          { name: 'style' },
          { name: 'class' },
          { name: 'id' }
        ]
      };

      extractor.cleanAttributes(elementWithAttrs);

      expect(elementWithAttrs.removeAttribute).toHaveBeenCalledWith('onclick');
      expect(elementWithAttrs.removeAttribute).toHaveBeenCalledWith('style');
      // class and id should be preserved
      expect(elementWithAttrs.removeAttribute).not.toHaveBeenCalledWith('class');
      expect(elementWithAttrs.removeAttribute).not.toHaveBeenCalledWith('id');
    });
  });

  describe('Image Processing', () => {
    test('should extract and process images', () => {
      const mockImages = [
        {
          src: 'https://example.com/image1.jpg',
          alt: 'Test image 1',
          getAttribute: jest.fn((attr) => attr === 'src' ? 'https://example.com/image1.jpg' : 'Test image 1'),
          hasAttribute: jest.fn(() => true)
        },
        {
          src: 'https://example.com/image2.png',
          alt: 'Test image 2',
          getAttribute: jest.fn((attr) => attr === 'src' ? 'https://example.com/image2.png' : 'Test image 2'),
          hasAttribute: jest.fn(() => true)
        }
      ];

      const mockElement = {
        querySelectorAll: jest.fn(() => mockImages),
        innerHTML: '<p>Content with images</p>',
        textContent: 'Content with images'
      };

      const images = extractor.extractImages(mockElement);

      expect(images).toHaveLength(2);
      expect(images[0]).toHaveProperty('src', 'https://example.com/image1.jpg');
      expect(images[0]).toHaveProperty('alt', 'Test image 1');
    });

    test('should filter out small and decorative images', () => {
      const mockImages = [
        {
          src: 'https://example.com/icon.png',
          alt: '',
          width: 16,
          height: 16,
          getAttribute: jest.fn((attr) => {
            if (attr === 'src') return 'https://example.com/icon.png';
            if (attr === 'width') return '16';
            if (attr === 'height') return '16';
            return '';
          }),
          hasAttribute: jest.fn(() => true)
        },
        {
          src: 'https://example.com/content-image.jpg',
          alt: 'Content image',
          width: 400,
          height: 300,
          getAttribute: jest.fn((attr) => {
            if (attr === 'src') return 'https://example.com/content-image.jpg';
            if (attr === 'alt') return 'Content image';
            if (attr === 'width') return '400';
            if (attr === 'height') return '300';
            return '';
          }),
          hasAttribute: jest.fn(() => true)
        }
      ];

      const mockElement = {
        querySelectorAll: jest.fn(() => mockImages),
        innerHTML: '<p>Content with images</p>',
        textContent: 'Content with images'
      };

      const images = extractor.extractImages(mockElement);

      expect(images).toHaveLength(1);
      expect(images[0].src).toBe('https://example.com/content-image.jpg');
    });

    test('should handle relative image URLs', () => {
      const mockImages = [
        {
          src: '/images/relative-image.jpg',
          alt: 'Relative image',
          getAttribute: jest.fn((attr) => 
            attr === 'src' ? '/images/relative-image.jpg' : 'Relative image'
          ),
          hasAttribute: jest.fn(() => true)
        }
      ];

      const mockElement = {
        querySelectorAll: jest.fn(() => mockImages),
        innerHTML: '<p>Content with relative image</p>',
        textContent: 'Content with relative image'
      };

      mockDocument.URL = 'https://example.com/article';
      const images = extractor.extractImages(mockElement, mockDocument.URL);

      expect(images[0].src).toBe('https://example.com/images/relative-image.jpg');
    });
  });

  describe('Link Processing', () => {
    test('should extract and process links', () => {
      const mockLinks = [
        {
          href: 'https://example.com/link1',
          textContent: 'External Link',
          getAttribute: jest.fn(() => 'https://example.com/link1')
        },
        {
          href: '/internal-page',
          textContent: 'Internal Link',
          getAttribute: jest.fn(() => '/internal-page')
        }
      ];

      const mockElement = {
        querySelectorAll: jest.fn(() => mockLinks),
        innerHTML: '<p>Content with links</p>',
        textContent: 'Content with links'
      };

      const links = extractor.extractLinks(mockElement, 'https://example.com');

      expect(links).toHaveLength(2);
      expect(links[0]).toHaveProperty('href', 'https://example.com/link1');
      expect(links[1]).toHaveProperty('href', 'https://example.com/internal-page');
    });

    test('should classify internal vs external links', () => {
      const mockLinks = [
        {
          href: 'https://example.com/internal',
          textContent: 'Internal Link',
          getAttribute: jest.fn(() => 'https://example.com/internal')
        },
        {
          href: 'https://external.com/page',
          textContent: 'External Link',
          getAttribute: jest.fn(() => 'https://external.com/page')
        }
      ];

      const mockElement = {
        querySelectorAll: jest.fn(() => mockLinks),
        innerHTML: '<p>Content with links</p>',
        textContent: 'Content with links'
      };

      const links = extractor.extractLinks(mockElement, 'https://example.com');

      expect(links[0]).toHaveProperty('isExternal', false);
      expect(links[1]).toHaveProperty('isExternal', true);
    });
  });

  describe('Content Analysis', () => {
    test('should calculate reading time', () => {
      const content = 'This is a test article with enough words to calculate reading time. '.repeat(50);
      
      const readingTime = extractor.calculateReadingTime(content);

      expect(readingTime).toBeGreaterThan(0);
      expect(typeof readingTime).toBe('number');
    });

    test('should count words accurately', () => {
      const content = 'This is a test with exactly ten words in it.';
      
      const wordCount = extractor.countWords(content);

      expect(wordCount).toBe(10);
    });

    test('should handle empty content', () => {
      const wordCount = extractor.countWords('');
      const readingTime = extractor.calculateReadingTime('');

      expect(wordCount).toBe(0);
      expect(readingTime).toBe(0);
    });

    test('should analyze content quality', () => {
      const highQualityContent = {
        textContent: 'This is a high quality article with substantial content. '.repeat(100),
        querySelectorAll: jest.fn(() => [
          { textContent: 'Heading 1' },
          { textContent: 'Heading 2' }
        ])
      };

      const analysis = extractor.analyzeContentQuality(highQualityContent);

      expect(analysis).toHaveProperty('wordCount');
      expect(analysis).toHaveProperty('hasStructure');
      expect(analysis).toHaveProperty('qualityScore');
      expect(analysis.qualityScore).toBeGreaterThan(0);
    });
  });

  describe('Error Handling', () => {
    test('should handle malformed HTML gracefully', () => {
      const malformedDocument = {
        ...mockDocument,
        querySelector: jest.fn(() => {
          throw new Error('DOM parsing error');
        })
      };

      const result = extractor.extractPageContent(malformedDocument);

      expect(result).toHaveProperty('content');
      expect(result).toHaveProperty('error');
      expect(result.error).toContain('DOM parsing error');
    });

    test('should handle missing document properties', () => {
      const incompleteDocument = {
        body: null,
        title: null,
        URL: null
      };

      const result = extractor.extractPageContent(incompleteDocument);

      expect(result).toHaveProperty('title');
      expect(result).toHaveProperty('url');
      expect(result.title).toBeTruthy(); // Should have fallback
      expect(result.url).toBeTruthy(); // Should have fallback
    });

    test('should handle extraction timeouts', async () => {
      const slowDocument = {
        ...mockDocument,
        querySelector: jest.fn(() => {
          // Simulate slow DOM operation
          return new Promise(resolve => setTimeout(resolve, 5000));
        })
      };

      const result = await extractor.extractPageContentWithTimeout(slowDocument, 1000);

      expect(result).toHaveProperty('error');
      expect(result.error).toContain('timeout');
    });
  });

  describe('Content Validation', () => {
    test('should validate extracted content structure', () => {
      const validContent = {
        title: 'Valid Title',
        content: 'Valid content with enough text',
        url: 'https://example.com',
        timestamp: new Date().toISOString()
      };

      const isValid = extractor.validateExtractedContent(validContent);

      expect(isValid).toBe(true);
    });

    test('should reject content with missing required fields', () => {
      const invalidContent = {
        title: '',
        content: '',
        url: 'https://example.com'
        // Missing timestamp
      };

      const isValid = extractor.validateExtractedContent(invalidContent);

      expect(isValid).toBe(false);
    });

    test('should reject content that is too short', () => {
      const shortContent = {
        title: 'Title',
        content: 'Short',
        url: 'https://example.com',
        timestamp: new Date().toISOString()
      };

      const isValid = extractor.validateExtractedContent(shortContent);

      expect(isValid).toBe(false);
    });
  });
});
