// Test script for Anthropic content extraction validation
// Run this in the browser console on https://www.anthropic.com/research/project-vend-1

console.log('🧪 Testing Anthropic Content Extraction...');

// Simulate the content extraction logic
function testAnthropicExtraction() {
  console.log('📊 Starting Anthropic content extraction test...');

  // Test the selector strategy first
  const anthropicSelectors = [
    'main article',
    'article',
    'main',
    '[role="main"]',
    '.research-content',
    '.article-content',
    '.post-content',
    '.blog-content',
    '.content',
    '.main-content',
    '#__next main',
    '[data-reactroot] main',
    '#__next article',
    '[data-reactroot] article',
    '[data-testid="article"]',
    '[data-testid="content"]',
    '[data-testid="research-content"]',
    '[data-component="article"]',
    '[data-component="research"]',
    '.container main',
    '.wrapper main',
    '.layout main',
    '.page-container main',
    '.content-container',
    '.article-container',
    '.research-container',
    '[class*="research"]',
    '[class*="article"]',
    '[class*="content"]',
    '[class*="post"]',
  ];

  console.log('🔍 Testing Anthropic-specific selectors...');
  let foundElement = null;
  let usedSelector = null;

  for (const selector of anthropicSelectors) {
    try {
      const element = document.querySelector(selector);
      if (element && isValidAnthropicContent(element)) {
        foundElement = element;
        usedSelector = selector;
        console.log(`✅ Found content with selector: ${selector}`);
        break;
      }
    } catch (error) {
      console.warn(`❌ Invalid selector: ${selector}`, error);
    }
  }

  if (!foundElement) {
    console.log('🔧 No direct selector match, trying structure analysis...');
    foundElement = findAnthropicContentByStructure();
    usedSelector = 'structure-analysis';
  }

  if (foundElement) {
    console.log('🎉 Content extraction successful!');
    console.log('📝 Method used:', usedSelector);
    console.log('📏 Content length:', foundElement.textContent?.length || 0);
    console.log('🏷️ Element tag:', foundElement.tagName);
    console.log('📄 Classes:', foundElement.className);
    console.log('🧪 Element preview:', foundElement.textContent?.substring(0, 200) + '...');

    // Test markdown conversion potential
    const paragraphs = foundElement.querySelectorAll('p').length;
    const headings = foundElement.querySelectorAll('h1, h2, h3, h4, h5, h6').length;
    const links = foundElement.querySelectorAll('a').length;
    const images = foundElement.querySelectorAll('img').length;

    console.log('📊 Content structure analysis:');
    console.log(`   Paragraphs: ${paragraphs}`);
    console.log(`   Headings: ${headings}`);
    console.log(`   Links: ${links}`);
    console.log(`   Images: ${images}`);

    // Test research content quality
    const text = foundElement.textContent?.toLowerCase() || '';
    const researchTerms = [
      'research',
      'study',
      'experiment',
      'project',
      'analysis',
      'claude',
      'anthropic',
    ];
    const foundTerms = researchTerms.filter(term => text.includes(term));
    console.log('🔬 Research terms found:', foundTerms);

    return {
      success: true,
      element: foundElement,
      selector: usedSelector,
      contentLength: foundElement.textContent?.length || 0,
      structure: { paragraphs, headings, links, images },
      researchTerms: foundTerms,
    };
  } else {
    console.log('❌ No suitable content found');
    return { success: false };
  }
}

// Helper function to validate content
function isValidAnthropicContent(element) {
  const text = element.textContent?.trim() || '';
  const className = element.className.toLowerCase();

  // Must have substantial content
  if (text.length < 500) return false;

  // Should have good structure
  const paragraphs = element.querySelectorAll('p').length;
  const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6').length;

  if (paragraphs < 2 && headings < 1) return false;

  // Avoid pure navigation content
  const navTerms = ['navigation', 'nav', 'menu', 'footer', 'header', 'sidebar'];
  const isNavContent = navTerms.some(term => className.includes(term));

  if (isNavContent && paragraphs < 5) return false;

  return true;
}

// Structure analysis fallback
function findAnthropicContentByStructure() {
  const candidates = Array.from(document.querySelectorAll('div, section, article, main'))
    .filter(el => {
      const text = el.textContent?.trim() || '';
      const className = el.className.toLowerCase();

      // Must have substantial text content
      if (text.length < 2000) return false;

      // Look for research article structure
      const paragraphs = el.querySelectorAll('p').length;
      const headings = el.querySelectorAll('h1, h2, h3, h4, h5, h6').length;

      // Should have substantial structure
      if (paragraphs < 5 && headings < 3) return false;

      // Prefer elements with content-related classes
      const contentTerms = ['content', 'research', 'article', 'post', 'main', 'body'];
      const hasContentClass = contentTerms.some(term => className.includes(term));

      // Exclude promotional areas
      const excludeTerms = [
        'nav',
        'menu',
        'header',
        'footer',
        'sidebar',
        'newsletter',
        'subscribe',
      ];
      const hasExcludeClass = excludeTerms.some(term => className.includes(term));

      if (hasExcludeClass && !hasContentClass) return false;

      // Check for research content
      const researchIndicators = [
        'research',
        'study',
        'experiment',
        'analysis',
        'project',
        'claude',
        'anthropic',
      ];
      const hasResearchContent = researchIndicators.some(indicator =>
        text.toLowerCase().includes(indicator)
      );

      return hasContentClass || hasResearchContent;
    })
    .sort((a, b) => {
      // Score by content quality
      const scoreA = scoreAnthropicElement(a);
      const scoreB = scoreAnthropicElement(b);
      return scoreB - scoreA;
    });

  return candidates.length > 0 ? candidates[0] : null;
}

// Scoring function for elements
function scoreAnthropicElement(element) {
  let score = 0;
  const text = element.textContent?.trim() || '';
  const className = element.className.toLowerCase();

  // Base score from text length
  score += Math.min(text.length / 15, 400);

  // Bonus for content-related classes
  const contentBonuses = [
    { term: 'research', bonus: 250 },
    { term: 'article', bonus: 200 },
    { term: 'content', bonus: 150 },
    { term: 'main', bonus: 120 },
    { term: 'post', bonus: 100 },
  ];

  contentBonuses.forEach(({ term, bonus }) => {
    if (className.includes(term)) score += bonus;
  });

  // Semantic element bonus
  if (element.tagName === 'MAIN' || element.tagName === 'ARTICLE') {
    score += 200;
  }

  // Structure bonuses
  score += element.querySelectorAll('p').length * 20;
  score += element.querySelectorAll('h1, h2, h3, h4, h5, h6').length * 30;

  return Math.max(0, score);
}

// Run the test
const result = testAnthropicExtraction();

if (result.success) {
  console.log('🎯 Test Summary:');
  console.log('✅ Anthropic content extraction: SUCCESS');
  console.log(`📏 Content length: ${result.contentLength} characters`);
  console.log(`🔧 Method: ${result.selector}`);
  console.log(
    `📊 Structure: ${result.structure.paragraphs}p, ${result.structure.headings}h, ${result.structure.links}links`
  );
  console.log(`🔬 Research terms: ${result.researchTerms.join(', ')}`);
} else {
  console.log('❌ Test Summary: Anthropic content extraction failed');
}

console.log('🧪 Test completed! Check the results above.');
