/**
 * Debug Anthropic Content Extraction - Real Page Test
 *
 * This script helps diagnose why the Anthropic extraction is capturing
 * figure captions and footnotes instead of the main article content.
 *
 * To use:
 * 1. Navigate to: https://www.anthropic.com/research/project-vend-1?utm_source=tldrwebdev
 * 2. Open browser console (F12)
 * 3. Paste and run this script
 * 4. Review what selectors are finding
 */

console.log('🔍 Debugging Anthropic Content Extraction Issues...');
console.log('===================================================');

// Test the exact same selectors our extension uses
function debugAnthropicSelectors() {
  console.log('🎯 Testing Anthropic-specific selectors...');

  const anthropicSelectors = [
    // Primary research content containers
    'main article',
    'article',
    'main',
    '[role="main"]',

    // Research-specific containers
    '.research-content',
    '.article-content',
    '.post-content',
    '.blog-content',
    '.content',
    '.main-content',

    // Next.js/React patterns (Anthropic uses Next.js)
    '#__next main',
    '[data-reactroot] main',
    '#__next article',
    '[data-reactroot] article',

    // Data attributes and components
    '[data-testid="article"]',
    '[data-testid="content"]',
    '[data-testid="research-content"]',
    '[data-component="article"]',
    '[data-component="research"]',

    // Container patterns
    '.container main',
    '.wrapper main',
    '.layout main',
    '.page-container main',
    '.content-container',
    '.article-container',
    '.research-container',

    // Fallback class-based selectors
    '[class*="research"]',
    '[class*="article"]',
    '[class*="content"]',
    '[class*="post"]',
  ];

  const results = [];

  for (const selector of anthropicSelectors) {
    try {
      const element = document.querySelector(selector);
      if (element) {
        const text = element.textContent?.trim() || '';
        const textPreview = text.substring(0, 200) + '...';

        results.push({
          selector,
          found: true,
          contentLength: text.length,
          tagName: element.tagName,
          className: element.className,
          textPreview,
          element: element,
        });

        console.log(`✅ Found: ${selector}`);
        console.log(`   Length: ${text.length} chars`);
        console.log(`   Tag: ${element.tagName}`);
        console.log(`   Classes: ${element.className}`);
        console.log(`   Preview: ${textPreview}`);
        console.log('   ---');
      }
    } catch (error) {
      console.warn(`❌ Invalid selector: ${selector}`, error);
    }
  }

  return results;
}

// Check what content we would actually extract
function testContentExtraction() {
  console.log('\n🎯 Testing actual content extraction logic...');

  // This mirrors our extension's logic
  const foundElements = debugAnthropicSelectors();

  if (foundElements.length === 0) {
    console.log('❌ No elements found with any selector');
    return null;
  }

  // Find the first valid element (like our extension does)
  for (const result of foundElements) {
    if (isValidAnthropicContent(result.element)) {
      console.log(`🎯 Would extract content from: ${result.selector}`);
      console.log(`📏 Content length: ${result.contentLength}`);
      console.log(`📄 Text preview: ${result.textPreview}`);

      // Show what specific content would be extracted
      const extractedText = result.element.textContent?.trim() || '';

      // Check if this contains the actual article content
      const hasMainContent = extractedText.toLowerCase().includes('project vend');
      const hasIntroduction = extractedText
        .toLowerCase()
        .includes('why did you have an llm run a small business');
      const hasPerformanceReview = extractedText
        .toLowerCase()
        .includes("claude's performance review");

      console.log(`\n📊 Content Analysis:`);
      console.log(`   Contains "project vend": ${hasMainContent}`);
      console.log(`   Contains introduction: ${hasIntroduction}`);
      console.log(`   Contains performance review: ${hasPerformanceReview}`);

      if (!hasMainContent && !hasIntroduction && !hasPerformanceReview) {
        console.log('🚨 WARNING: This element does NOT contain the main article content!');
        console.log('   It likely contains sidebar, footer, or metadata only.');
      } else {
        console.log('✅ This element appears to contain the main article content.');
      }

      return result.element;
    }
  }

  console.log('❌ No valid content elements found');
  return null;
}

// The validation function from our extension
function isValidAnthropicContent(element) {
  const text = element.textContent?.trim() || '';
  const className = element.className.toLowerCase();

  // Must have substantial content (research articles are typically long)
  if (text.length < 500) return false;

  // Should have good structure
  const paragraphs = element.querySelectorAll('p').length;
  const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6').length;

  if (paragraphs < 2 && headings < 1) return false;

  // Avoid pure navigation or promotional content
  const navTerms = ['navigation', 'nav', 'menu', 'footer', 'header', 'sidebar'];
  const isNavContent = navTerms.some(term => className.includes(term));

  if (isNavContent && paragraphs < 5) return false;

  return true;
}

// Check page structure to understand what we're working with
function analyzePageStructure() {
  console.log('\n🏗️ Analyzing page structure...');

  // Look for main content areas
  const mainElements = document.querySelectorAll('main, article, [role="main"]');
  console.log(`📊 Found ${mainElements.length} main content elements:`);

  mainElements.forEach((el, index) => {
    const text = el.textContent?.trim() || '';
    console.log(`   ${index + 1}. ${el.tagName} (${text.length} chars) - Classes: ${el.className}`);
  });

  // Look for Next.js structure
  const nextRoot = document.querySelector('#__next');
  if (nextRoot) {
    console.log('\n⚛️ Next.js structure detected:');
    console.log(`   #__next contains ${nextRoot.children.length} direct children`);

    const nextMain = nextRoot.querySelector('main');
    if (nextMain) {
      console.log(
        `   Main element found in Next.js root: ${nextMain.textContent?.length || 0} chars`
      );
    }
  }

  // Look for obvious article content
  const articleText = document.body.textContent?.toLowerCase() || '';
  const hasProjectVend = articleText.includes('project vend');
  const hasClaudeShop = articleText.includes('claude run a small shop');

  console.log(`\n🔍 Content detection:`);
  console.log(`   Page contains "project vend": ${hasProjectVend}`);
  console.log(`   Page contains "claude run a small shop": ${hasClaudeShop}`);

  if (!hasProjectVend || !hasClaudeShop) {
    console.log('🚨 WARNING: Expected content not found in page text!');
    console.log('   The page might not have loaded properly or the content is dynamically loaded.');
  }
}

// Find what element actually contains the article content
function findActualArticleContent() {
  console.log('\n🔎 Searching for actual article content...');

  // Look for elements that contain key phrases from the article
  const keyPhrases = [
    'project vend',
    'claude run a small shop',
    'why did you have an llm run a small business',
    "claude's performance review",
    'andon labs',
  ];

  const allElements = document.querySelectorAll('*');
  const candidateElements = [];

  for (const element of allElements) {
    const text = element.textContent?.toLowerCase() || '';
    const matchedPhrases = keyPhrases.filter(phrase => text.includes(phrase));

    if (matchedPhrases.length >= 2) {
      candidateElements.push({
        element,
        matchedPhrases,
        textLength: text.length,
        tagName: element.tagName,
        className: element.className,
        selector: getElementSelector(element),
      });
    }
  }

  // Sort by most matched phrases and text length
  candidateElements.sort((a, b) => {
    if (b.matchedPhrases.length !== a.matchedPhrases.length) {
      return b.matchedPhrases.length - a.matchedPhrases.length;
    }
    return b.textLength - a.textLength;
  });

  console.log(`📊 Found ${candidateElements.length} elements with article content:`);

  candidateElements.slice(0, 5).forEach((candidate, index) => {
    console.log(`   ${index + 1}. ${candidate.tagName}.${candidate.className}`);
    console.log(`      Selector: ${candidate.selector}`);
    console.log(`      Matched phrases: ${candidate.matchedPhrases.join(', ')}`);
    console.log(`      Text length: ${candidate.textLength} chars`);
    console.log('      ---');
  });

  return candidateElements;
}

// Helper to generate CSS selector for an element
function getElementSelector(element) {
  if (element.id) {
    return `#${element.id}`;
  }

  if (element.className) {
    const classes = element.className
      .split(' ')
      .filter(c => c)
      .slice(0, 2);
    if (classes.length > 0) {
      return `${element.tagName.toLowerCase()}.${classes.join('.')}`;
    }
  }

  return element.tagName.toLowerCase();
}

// Run all diagnostic tests
console.log('🚀 Starting diagnostic tests...\n');

analyzePageStructure();
const selectorResults = debugAnthropicSelectors();
const extractedElement = testContentExtraction();
const actualContent = findActualArticleContent();

console.log('\n📋 DIAGNOSTIC SUMMARY');
console.log('===================');
console.log(`🔍 Selectors found elements: ${selectorResults.length > 0}`);
console.log(`✅ Valid content extracted: ${extractedElement !== null}`);
console.log(`🎯 Actual article content found: ${actualContent.length > 0}`);

if (extractedElement && actualContent.length > 0) {
  const isCorrectElement = actualContent.some(candidate => candidate.element === extractedElement);
  console.log(`🎯 Extracted correct element: ${isCorrectElement}`);

  if (!isCorrectElement) {
    console.log('\n🔧 RECOMMENDATION:');
    console.log('The extraction is finding content, but not the main article.');
    console.log('Consider using these selectors instead:');
    actualContent.slice(0, 3).forEach((candidate, index) => {
      console.log(`   ${index + 1}. ${candidate.selector}`);
    });
  }
} else if (actualContent.length > 0) {
  console.log('\n🔧 RECOMMENDATION:');
  console.log('Article content exists but our selectors are not finding it.');
  console.log('Consider adding these selectors:');
  actualContent.slice(0, 3).forEach((candidate, index) => {
    console.log(`   ${index + 1}. ${candidate.selector}`);
  });
}

console.log('\n✨ Diagnostic completed!');
