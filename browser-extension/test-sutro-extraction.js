/**
 * Test script to validate sutro.sh content extraction
 * Run with: node test-sutro-extraction.js
 */

const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

// Mock logger for testing
const logger = {
  debug: (...args) => console.log('[DEBUG]', ...args),
  info: (...args) => console.log('[INFO]', ...args),
  warn: (...args) => console.warn('[WARN]', ...args),
  error: (...args) => console.error('[ERROR]', ...args),
};

// Load and compile TypeScript content selector strategies
// For this test, we'll use a simplified version
const contentSelectorStrategies = `
// Simplified version of our strategies for testing
global.ModernBlogStrategy = class ModernBlogStrategy {
  isApplicable(url, document) {
    return url.includes('sutro.sh') || 
           url.includes('/blog/') || 
           !!document.querySelector('.prose, [class*="prose"], .blog-content, .post-content, main article');
  }

  getSelectors() {
    return [{
      name: 'Modern Blog Primary',
      selectors: [
        'main article',
        'article',
        'main .prose',
        '.prose',
        'main [role="main"]',
        '.blog-content',
        '.post-content',
        '.entry-content',
        'main .content',
        '.content'
      ]
    }];
  }
}

global.GeneralContentStrategy = class GeneralContentStrategy {
  isApplicable() { return true; }
  
  getSelectors() {
    return [{
      name: 'General Content',
      selectors: [
        'article',
        'main',
        '[role="main"]',
        '.content',
        '#content',
        '.post',
        '.entry'
      ]
    }];
  }
}

global.ContentSelectorManager = class ContentSelectorManager {
  constructor() {
    this.strategies = [
      new global.ModernBlogStrategy(),
      new global.GeneralContentStrategy()
    ];
  }

  findContentElement(url, document) {
    const selectorGroups = this.getSelectorsForContent(url, document);
    let bestElement = null;
    let bestScore = 0;

    for (const group of selectorGroups) {
      for (const selector of group.selectors) {
        try {
          const elements = document.querySelectorAll(selector);
          for (const element of Array.from(elements)) {
            if (this.isValidContentElement(element)) {
              const score = this.scoreContentElement(element, url);
              if (score > bestScore) {
                bestScore = score;
                bestElement = element;
                console.log(\`New best element: \${selector} (score: \${score})\`);
              }
            }
          }
        } catch (error) {
          console.warn('Invalid selector:', selector);
        }
      }
    }

    return bestElement;
  }

  getSelectorsForContent(url, document) {
    for (const strategy of this.strategies) {
      if (strategy.isApplicable(url, document)) {
        return strategy.getSelectors();
      }
    }
    return new global.GeneralContentStrategy().getSelectors();
  }

  isValidContentElement(element) {
    const text = element.textContent?.trim() || '';
    if (text.length < 100) return false;
    
    const paragraphs = element.querySelectorAll('p').length;
    const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6').length;
    return paragraphs >= 1 || headings >= 1;
  }

  scoreContentElement(element, url) {
    let score = 0;
    const text = element.textContent?.trim() || '';
    const className = element.className.toLowerCase();
    const tagName = element.tagName.toLowerCase();

    // Word count score
    const wordCount = text.split(/\\s+/).filter(Boolean).length;
    score += Math.min(wordCount / 5, 500);

    // Structure bonuses
    const paragraphs = element.querySelectorAll('p').length;
    const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6').length;
    score += paragraphs * 20;
    score += headings * 30;

    // Semantic HTML bonuses
    if (tagName === 'article') score += 200;
    if (tagName === 'main') score += 150;

    // Modern blog patterns
    if (className.includes('prose')) score += 150;
    if (className.includes('max-w-')) score += 80; // Tailwind
    if (className.includes('mx-auto')) score += 60;

    // Content indicators
    const contentTerms = ['content', 'article', 'post', 'entry', 'main', 'body'];
    contentTerms.forEach(term => {
      if (className.includes(term)) score += 80;
    });

    return Math.max(0, score);
  }
}
`;

// Create a sample sutro.sh-like HTML structure
const sampleSutroHTML = `
<!DOCTYPE html>
<html>
<head>
  <title>The End of Moore's Law for AI: Gemini Flash Offers a Warning - Sutro</title>
</head>
<body>
  <header>
    <nav>Navigation here</nav>
  </header>
  
  <main class="max-w-4xl mx-auto px-4">
    <article class="prose prose-lg max-w-none">
      <header class="mb-8">
        <h1 class="text-4xl font-bold mb-4">The End of Moore's Law for AI: Gemini Flash Offers a Warning</h1>
        <div class="text-gray-600 mb-4">
          <time datetime="2024-07-13">July 13, 2024</time>
        </div>
      </header>
      
      <div class="article-content">
        <p class="text-lg leading-relaxed">
          As we stand at the precipice of a new era in artificial intelligence, 
          Google's Gemini Flash model serves as both a beacon of innovation and 
          a harbinger of challenges to come. The intersection of Moore's Law with 
          AI development presents fascinating questions about the future of 
          computational progress.
        </p>
        
        <p>
          For decades, Moore's Law has been the guiding principle of technological 
          advancement, predicting that the number of transistors on a microchip 
          doubles approximately every two years. This exponential growth has 
          powered the digital revolution, enabling everything from smartphones 
          to supercomputers.
        </p>
        
        <h2 class="text-2xl font-semibold mt-8 mb-4">The AI Computing Challenge</h2>
        
        <p>
          However, as we push the boundaries of artificial intelligence, we're 
          encountering new computational demands that strain the limits of 
          traditional silicon-based processing. AI models like GPT-4, Claude, 
          and Google's Gemini require unprecedented amounts of computational 
          power for both training and inference.
        </p>
        
        <p>
          Gemini Flash, Google's latest offering, represents an attempt to 
          balance performance with efficiency. But it also highlights a 
          fundamental tension in AI development: the growing gap between 
          our computational needs and our hardware capabilities.
        </p>
        
        <h3 class="text-xl font-medium mt-6 mb-3">Key Implications</h3>
        
        <ul class="list-disc pl-6 space-y-2">
          <li>Energy consumption concerns in AI training</li>
          <li>The need for specialized AI hardware</li>
          <li>Economic implications of computational limits</li>
          <li>Potential shift toward more efficient algorithms</li>
        </ul>
        
        <p>
          As we look toward the future, it's clear that the relationship between 
          hardware advancement and AI capability will define the next chapter 
          of technological progress. Companies like Google, with their Gemini 
          Flash model, are showing us both the possibilities and the constraints 
          of our current technological moment.
        </p>
        
        <blockquote class="border-l-4 border-blue-500 pl-4 italic text-gray-700 my-6">
          "The future of AI isn't just about building smarter models—it's about 
          building smarter, more efficient models that can work within the 
          physical constraints of our universe."
        </blockquote>
        
        <p>
          Whether we're truly approaching the end of Moore's Law for AI or simply 
          entering a new phase of innovation remains to be seen. What's certain 
          is that models like Gemini Flash are pushing us to reconsider our 
          assumptions about computational growth and forcing us to think more 
          creatively about the future of artificial intelligence.
        </p>
      </div>
    </article>
  </main>
  
  <aside class="sidebar">
    <div class="related-posts">
      <h3>Related Articles</h3>
      <a href="/other-post">Other Post</a>
    </div>
  </aside>
  
  <footer>
    <p>Footer content</p>
  </footer>
</body>
</html>
`;

async function testSutroExtraction() {
  console.log('Testing sutro.sh content extraction...\n');

  // Create JSDOM instance
  const dom = new JSDOM(sampleSutroHTML, {
    url: 'https://sutro.sh/blog/the-end-of-moore-s-law-for-ai-gemini-flash-offers-a-warning?utm_source=tldrai',
  });

  const { document, window } = dom.window;
  global.document = document;
  global.window = window;

  // Evaluate our content selector strategies
  eval(contentSelectorStrategies);

  // Test content extraction
  const manager = new ContentSelectorManager();
  const url =
    'https://sutro.sh/blog/the-end-of-moore-s-law-for-ai-gemini-flash-offers-a-warning?utm_source=tldrai';

  console.log('URL:', url);
  console.log('Document title:', document.title);
  console.log();

  // Test strategy selection
  const modernBlogStrategy = new global.ModernBlogStrategy();
  const isApplicable = modernBlogStrategy.isApplicable(url, document);
  console.log('ModernBlogStrategy applicable:', isApplicable);
  console.log();

  // Test content element finding
  const contentElement = manager.findContentElement(url, document);

  if (contentElement) {
    console.log('✅ Content extraction successful!');
    console.log(
      'Selected element:',
      contentElement.tagName +
        (contentElement.className ? '.' + contentElement.className.split(' ').join('.') : '')
    );
    console.log('Content preview:', contentElement.textContent.substring(0, 200) + '...');
    console.log('Word count:', contentElement.textContent.split(/\s+/).filter(Boolean).length);
    console.log('Paragraphs found:', contentElement.querySelectorAll('p').length);
    console.log(
      'Headings found:',
      contentElement.querySelectorAll('h1, h2, h3, h4, h5, h6').length
    );
  } else {
    console.log('❌ Content extraction failed!');
    console.log('No suitable content element found.');
  }

  console.log('\n=== Test Complete ===');
}

// Run the test
testSutroExtraction().catch(console.error);
