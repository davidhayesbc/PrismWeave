// Test script for enhanced Substack content extraction
// This script tests the improved Substack content selectors and extraction logic

console.log('🧪 Testing Enhanced Substack Content Extraction');

// Test URL from the user's report
const testUrl = 'https://worksonmymachine.substack.com/p/mcp-an-accidentally-universal-plugin';

console.log('📄 Test URL:', testUrl);
console.log('🔍 Testing enhanced selectors...');

// Enhanced Substack selectors to test
const enhancedSubstackSelectors = [
  // Primary 2025 Substack content selectors
  '.available-content',
  '.available-content .body',
  '.available-content .body.markup',
  '.available-content .markup',
  '.post-content .available-content',
  '.post .available-content',
  '.post-header + .available-content',
  '.body.markup',
  '.markup',
  '.post-body',
  '.post-content',
  'article .available-content',
  'article .body.markup',
  'article .markup',
  'article .post-content',
  '[data-testid="post-content"]',
  '[data-testid="available-content"]',
  '[data-testid="post-body"]',
  '[data-component="post-content"]',
  // Fallback patterns
  '[class*="available-content"]',
  '[class*="post-content"]',
  '[class*="body"][class*="markup"]',
  '.post .body',
  '.publication-content',
  '.newsletter-content',
  'main .available-content',
  'main .post-content',
  'main .markup',
  '[role="main"] .available-content',
  '[role="main"] .markup',
];

// Function to test selectors on a page
function testSubstackSelectors() {
  console.log('🎯 Testing selectors on current page...');
  
  const results = [];
  
  enhancedSubstackSelectors.forEach((selector, index) => {
    try {
      const elements = document.querySelectorAll(selector);
      if (elements.length > 0) {
        const element = elements[0];
        const textLength = element.textContent?.trim().length || 0;
        const hasSubstantialContent = textLength > 500;
        
        results.push({
          index: index + 1,
          selector,
          found: elements.length,
          textLength,
          hasSubstantialContent,
          className: element.className,
          preview: element.textContent?.trim().substring(0, 100) + '...'
        });
        
        console.log(`✅ ${index + 1}. ${selector}`, {
          found: elements.length,
          textLength,
          substantial: hasSubstantialContent,
          className: element.className
        });
      }
    } catch (error) {
      console.log(`❌ ${index + 1}. ${selector} - Invalid selector:`, error.message);
    }
  });
  
  // Find the best candidates
  const substantialContent = results.filter(r => r.hasSubstantialContent);
  
  console.log('\n🏆 Best content candidates:');
  substantialContent
    .sort((a, b) => b.textLength - a.textLength)
    .slice(0, 5)
    .forEach((result, i) => {
      console.log(`${i + 1}. ${result.selector}`, {
        textLength: result.textLength,
        className: result.className,
        preview: result.preview
      });
    });
  
  return substantialContent;
}

// Function to score elements like the enhanced ContentExtractor
function scoreSubstackElement(element) {
  let score = 0;
  const text = element.textContent?.trim() || '';
  const className = element.className.toLowerCase();
  
  // Base score from text length
  score += Math.min(text.length / 20, 300);
  
  // Bonus for content-related classes
  const contentBonuses = [
    { term: 'available-content', bonus: 200 },
    { term: 'markup', bonus: 150 },
    { term: 'post-content', bonus: 120 },
    { term: 'body', bonus: 100 },
    { term: 'article', bonus: 80 },
    { term: 'content', bonus: 60 },
  ];
  
  contentBonuses.forEach(({ term, bonus }) => {
    if (className.includes(term)) {
      score += bonus;
    }
  });
  
  // Penalty for navigation terms
  const navPenalties = [
    'nav', 'menu', 'header', 'footer', 'sidebar', 'subscribe',
    'related', 'recommendation', 'comment', 'share'
  ];
  
  navPenalties.forEach(term => {
    if (className.includes(term)) {
      score -= 100;
    }
  });
  
  // Bonus for paragraph structure
  const paragraphs = element.querySelectorAll('p').length;
  score += paragraphs * 15;
  
  // Bonus for headings
  const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6').length;
  score += headings * 25;
  
  return Math.max(0, score);
}

// Test the scoring algorithm
function testContentScoring() {
  console.log('\n🎯 Testing content scoring algorithm...');
  
  const allContentElements = document.querySelectorAll('div, section, article, main');
  const scored = Array.from(allContentElements)
    .map(el => ({
      element: el,
      score: scoreSubstackElement(el),
      textLength: el.textContent?.trim().length || 0,
      className: el.className,
      tagName: el.tagName.toLowerCase()
    }))
    .filter(item => item.score > 50 && item.textLength > 200)
    .sort((a, b) => b.score - a.score)
    .slice(0, 10);
  
  console.log('🏆 Top scored elements:');
  scored.forEach((item, i) => {
    console.log(`${i + 1}. Score: ${item.score}`, {
      tagName: item.tagName,
      className: item.className,
      textLength: item.textLength,
      preview: item.element.textContent?.trim().substring(0, 80) + '...'
    });
  });
  
  return scored;
}

// Instructions for manual testing
console.log(`
📋 Manual Testing Instructions:

1. Navigate to: ${testUrl}
2. Open browser DevTools (F12)
3. Copy and paste this entire script into the console
4. Run: testSubstackSelectors()
5. Run: testContentScoring()
6. Compare results with current extraction quality

🔍 What to look for:
- Selectors that find substantial content (>500 chars)
- High scoring elements that contain the main article
- Elements with "available-content", "markup", or "post-content" classes
- Avoid elements with navigation/promotional content

🚀 Testing Enhanced Extraction:
The enhanced extraction should now:
- Better identify Substack's .available-content containers
- Score content based on Substack-specific patterns
- Handle complex nested structures better
- Prefer markup containers over navigation elements
`);

// Export functions for manual testing
window.testSubstackSelectors = testSubstackSelectors;
window.testContentScoring = testContentScoring;
window.scoreSubstackElement = scoreSubstackElement;

console.log('✅ Test script loaded! Run testSubstackSelectors() and testContentScoring() in the console.');
