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
  let mockDocument;  beforeEach(() => {
    const ContentExtractorClass = require('../../src/utils/content-extractor.js');
    extractor = new ContentExtractorClass();
    
    // Use the global document mock from setup.js
    mockDocument = global.document;
    mockDocument.title = 'Test Page Title';
    mockDocument.URL = 'https://example.com/test-page';
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
      const mockElement = global.createMockElement('div');
      mockElement.innerHTML = '<p>Clean content</p>';
      mockElement.textContent = 'Clean content';
      
      // Mock querySelectorAll to return removable elements
      const removableEl1 = global.createMockElement('script');
      const removableEl2 = global.createMockElement('style');
      mockElement.querySelectorAll.mockReturnValue([removableEl1, removableEl2]);

      const cleaned = extractor.cleanContent(mockElement);

      expect(mockElement.querySelectorAll).toHaveBeenCalledWith(
        expect.stringContaining('script')
      );
      expect(cleaned).toBe(mockElement);
    });

    test('should preserve important elements', () => {
      const importantElement = global.createMockElement('div');
      const regularElement = global.createMockElement('div');
      
      const mockElement = global.createMockElement('div');
      mockElement.innerHTML = '<p>Content with important info</p>';
      mockElement.textContent = 'Content with important info';
      
      // Mock querySelectorAll to return different elements for different calls
      mockElement.querySelectorAll
        .mockReturnValueOnce([importantElement, regularElement]) // unwanted elements
        .mockReturnValueOnce([importantElement]); // preserve elements

      const cleaned = extractor.cleanContent(mockElement);

      expect(importantElement.remove).not.toHaveBeenCalled();
      expect(regularElement.remove).toHaveBeenCalled();
    });

    test('should clean HTML attributes', () => {
      const elementWithAttrs = global.createMockElement('div');
      
      // Mock attributes 
      elementWithAttrs.getAttribute.mockImplementation((attr) => 'test-value');
      elementWithAttrs.hasAttribute.mockImplementation(() => true);
      elementWithAttrs.attributes = [
        { name: 'onclick' },
        { name: 'style' },
        { name: 'class' },
        { name: 'id' }
      ];

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
      const mockImg1 = global.createMockElement('img');
      mockImg1.src = 'https://example.com/image1.jpg';
      mockImg1.alt = 'Test image 1';
      mockImg1.getAttribute.mockImplementation((attr) => 
        attr === 'src' ? 'https://example.com/image1.jpg' : 'Test image 1'
      );

      const mockImg2 = global.createMockElement('img');
      mockImg2.src = 'https://example.com/image2.png';
      mockImg2.alt = 'Test image 2';
      mockImg2.getAttribute.mockImplementation((attr) => 
        attr === 'src' ? 'https://example.com/image2.png' : 'Test image 2'
      );

      const mockImages = [mockImg1, mockImg2];

      const mockElement = global.createMockElement('div');
      mockElement.innerHTML = '<p>Content with images</p>';
      mockElement.textContent = 'Content with images';
      mockElement.querySelectorAll.mockReturnValue(mockImages);

      const images = extractor.extractImages(mockElement);

      expect(images).toHaveLength(2);
      expect(images[0]).toHaveProperty('src', 'https://example.com/image1.jpg');
      expect(images[0]).toHaveProperty('alt', 'Test image 1');
    });

    test('should filter out small and decorative images', () => {
      const iconImg = global.createMockElement('img');
      iconImg.src = 'https://example.com/icon.png';
      iconImg.alt = '';
      iconImg.width = 16;
      iconImg.height = 16;
      iconImg.getAttribute.mockImplementation((attr) => {
        if (attr === 'src') return 'https://example.com/icon.png';
        if (attr === 'width') return '16';
        if (attr === 'height') return '16';
        return '';
      });

      const contentImg = global.createMockElement('img');
      contentImg.src = 'https://example.com/content-image.jpg';
      contentImg.alt = 'Content image';
      contentImg.width = 400;
      contentImg.height = 300;
      contentImg.getAttribute.mockImplementation((attr) => {
        if (attr === 'src') return 'https://example.com/content-image.jpg';
        if (attr === 'alt') return 'Content image';
        if (attr === 'width') return '400';
        if (attr === 'height') return '300';
        return '';
      });

      const mockImages = [iconImg, contentImg];

      const mockElement = global.createMockElement('div');
      mockElement.innerHTML = '<p>Content with images</p>';
      mockElement.textContent = 'Content with images';
      mockElement.querySelectorAll.mockReturnValue(mockImages);

      const images = extractor.extractImages(mockElement);

      expect(images).toHaveLength(1);
      expect(images[0].src).toBe('https://example.com/content-image.jpg');
    });

    test('should handle relative image URLs', () => {
      const relativeImg = global.createMockElement('img');
      relativeImg.src = '/images/relative-image.jpg';
      relativeImg.alt = 'Relative image';
      relativeImg.getAttribute.mockImplementation((attr) => 
        attr === 'src' ? '/images/relative-image.jpg' : 'Relative image'
      );

      const mockImages = [relativeImg];

      const mockElement = global.createMockElement('div');
      mockElement.innerHTML = '<p>Content with relative image</p>';
      mockElement.textContent = 'Content with relative image';
      mockElement.querySelectorAll.mockReturnValue(mockImages);

      mockDocument.URL = 'https://example.com/article';
      const images = extractor.extractImages(mockElement, mockDocument.URL);

      expect(images[0].src).toBe('https://example.com/images/relative-image.jpg');
    });
  });
  describe('Link Processing', () => {
    test('should extract and process links', () => {
      const link1 = global.createMockElement('a');
      link1.href = 'https://example.com/link1';
      link1.textContent = 'External Link';
      link1.getAttribute.mockReturnValue('https://example.com/link1');

      const link2 = global.createMockElement('a');
      link2.href = '/internal-page';
      link2.textContent = 'Internal Link';
      link2.getAttribute.mockReturnValue('/internal-page');

      const mockLinks = [link1, link2];

      const mockElement = global.createMockElement('div');
      mockElement.innerHTML = '<p>Content with links</p>';
      mockElement.textContent = 'Content with links';
      mockElement.querySelectorAll.mockReturnValue(mockLinks);

      const links = extractor.extractLinks(mockElement, 'https://example.com');

      expect(links).toHaveLength(2);
      expect(links[0]).toHaveProperty('href', 'https://example.com/link1');
      expect(links[1]).toHaveProperty('href', 'https://example.com/internal-page');
    });

    test('should classify internal vs external links', () => {
      const internalLink = global.createMockElement('a');
      internalLink.href = 'https://example.com/internal';
      internalLink.textContent = 'Internal Link';
      internalLink.getAttribute.mockReturnValue('https://example.com/internal');

      const externalLink = global.createMockElement('a');
      externalLink.href = 'https://external.com/page';
      externalLink.textContent = 'External Link';
      externalLink.getAttribute.mockReturnValue('https://external.com/page');

      const mockLinks = [internalLink, externalLink];

      const mockElement = global.createMockElement('div');
      mockElement.innerHTML = '<p>Content with links</p>';
      mockElement.textContent = 'Content with links';
      mockElement.querySelectorAll.mockReturnValue(mockLinks);

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
    });    test('should analyze content quality', () => {
      const highQualityContent = global.createMockElement('div');
      highQualityContent.textContent = 'This is a high quality article with substantial content. '.repeat(100);
      
      // Mock headings for structure analysis
      const heading1 = global.createMockElement('h1');
      heading1.textContent = 'Heading 1';
      const heading2 = global.createMockElement('h2');
      heading2.textContent = 'Heading 2';
      
      highQualityContent.querySelector.mockReturnValue(heading1); // For checking if element has headings
      highQualityContent.querySelectorAll.mockReturnValue([heading1, heading2]);

      const analysis = extractor.analyzeContentQuality(highQualityContent);

      expect(analysis).toHaveProperty('wordCount');
      expect(analysis).toHaveProperty('hasStructure');
      expect(analysis).toHaveProperty('qualityScore');
      expect(analysis.qualityScore).toBeGreaterThan(0);
    });
  });
  describe('Error Handling', () => {
    test('should handle malformed HTML gracefully', () => {
      const malformedDocument = Object.assign({}, mockDocument);
      malformedDocument.querySelector = jest.fn(() => {
        throw new Error('DOM parsing error');
      });

      const result = extractor.extractPageContent(malformedDocument);

      expect(result).toHaveProperty('content');
      expect(result).toHaveProperty('error');
      expect(result.error).toContain('DOM parsing error');
    });

    test('should handle missing document properties', () => {
      const incompleteDocument = Object.assign({}, mockDocument);
      incompleteDocument.body = null;
      incompleteDocument.title = null;
      incompleteDocument.URL = null;

      const result = extractor.extractPageContent(incompleteDocument);

      expect(result).toHaveProperty('title');
      expect(result).toHaveProperty('url');
      expect(result.title).toBeTruthy(); // Should have fallback
      expect(result.url).toBeTruthy(); // Should have fallback
    });

    test('should handle extraction timeouts', async () => {
      const slowDocument = Object.assign({}, mockDocument);
      slowDocument.querySelector = jest.fn(() => {
        // Simulate slow DOM operation
        return new Promise(resolve => setTimeout(resolve, 5000));
      });

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
