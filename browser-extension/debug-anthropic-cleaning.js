/**
 * Debug Anthropic Content Cleaning Process
 *
 * This script tests the content cleaning pipeline to see why only
 * figure captions and footnotes are being preserved while the main
 * article content is being removed.
 *
 * To use:
 * 1. Navigate to: https://www.anthropic.com/research/project-vend-1?utm_source=tldrwebdev
 * 2. Open browser console (F12)
 * 3. Paste and run this script
 * 4. Compare before/after cleaning results
 */

console.log('🧹 Debugging Anthropic Content Cleaning Process...');
console.log('====================================================');

// Get the main article element (we know this works from previous diagnostic)
function getMainArticleElement() {
  const selectors = ['main article', 'article', 'main'];

  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      console.log(`✅ Found main content with selector: ${selector}`);
      console.log(`📏 Original content length: ${element.textContent?.length || 0} chars`);
      return element;
    }
  }

  return null;
}

// Simulate the content cleaning rules that our extension uses
function simulateContentCleaning(element) {
  console.log('\n🧹 Simulating content cleaning process...');

  const cloned = element.cloneNode(true);

  // Track what gets removed
  const removedElements = [];

  // Rule 1: Scripts and styles
  const scriptsAndStyles = cloned.querySelectorAll('script, style, noscript');
  console.log(`📝 Found ${scriptsAndStyles.length} script/style elements to remove`);
  scriptsAndStyles.forEach(el => {
    removedElements.push({
      rule: 'scripts-and-styles',
      element: el.tagName,
      content: el.textContent?.substring(0, 50),
    });
    el.remove();
  });

  // Rule 2: Advertisements
  const adSelectors = [
    '.ad',
    '.ads',
    '.advertisement',
    '.banner',
    '[id*="ad"]',
    '[class*="ad"]',
    '[id*="advertisement"]',
    '[class*="advertisement"]',
    '.google-ad',
    '.sponsored-content',
    '.promo',
  ];
  const adElements = cloned.querySelectorAll(adSelectors.join(','));
  console.log(`📝 Found ${adElements.length} advertisement elements to remove`);
  adElements.forEach(el => {
    removedElements.push({
      rule: 'advertisements',
      element: el.tagName,
      className: el.className,
      content: el.textContent?.substring(0, 50),
    });
    el.remove();
  });

  // Rule 3: Navigation
  const navSelectors = [
    'nav',
    'header:not(.article-header):not(.post-header)',
    'footer:not(.article-footer):not(.post-footer)',
    '.navigation',
    '.nav',
    '.menu',
    '.navbar',
    '.breadcrumb',
    '.pagination',
  ];
  const navElements = cloned.querySelectorAll(navSelectors.join(','));
  console.log(`📝 Found ${navElements.length} navigation elements to remove`);
  navElements.forEach(el => {
    removedElements.push({
      rule: 'navigation',
      element: el.tagName,
      className: el.className,
      content: el.textContent?.substring(0, 50),
    });
    el.remove();
  });

  // Rule 4: Social and widgets
  const socialSelectors = [
    '.social-share',
    '.share-buttons',
    '.social-links',
    '.newsletter-signup',
    '.subscription-box',
    '.comments-section',
    '.widget',
    '.sidebar',
  ];
  const socialElements = cloned.querySelectorAll(socialSelectors.join(','));
  console.log(`📝 Found ${socialElements.length} social/widget elements to remove`);
  socialElements.forEach(el => {
    removedElements.push({
      rule: 'social-and-widgets',
      element: el.tagName,
      className: el.className,
      content: el.textContent?.substring(0, 50),
    });
    el.remove();
  });

  // Rule 5: Metadata and tags
  const metaSelectors = [
    '.author-bio',
    '.author-card',
    '.tag-list',
    '.category-list',
    '.metadata',
    '.post-meta',
    '.article-meta',
  ];
  const metaElements = cloned.querySelectorAll(metaSelectors.join(','));
  console.log(`📝 Found ${metaElements.length} metadata elements to remove`);
  metaElements.forEach(el => {
    removedElements.push({
      rule: 'metadata-and-tags',
      element: el.tagName,
      className: el.className,
      content: el.textContent?.substring(0, 50),
    });
    el.remove();
  });

  // Test ad content removal by text
  console.log('\n🔍 Testing ad content removal by text...');
  const adKeywords = [
    'advertisement',
    'sponsored',
    'promoted',
    'ads by',
    'google ads',
    'affiliate',
    'partner content',
    'paid promotion',
    'shop now',
    'buy now',
    'subscribe now',
  ];

  const suspiciousElements = cloned.querySelectorAll('div, span, section, aside');
  let removedByText = 0;

  suspiciousElements.forEach(el => {
    const text = el.textContent?.toLowerCase() || '';
    const className = el.className?.toLowerCase() || '';
    const id = el.id?.toLowerCase() || '';
    const combinedText = `${text} ${id} ${className}`.toLowerCase();

    const hasAdKeyword = adKeywords.some(keyword => combinedText.includes(keyword));
    if (hasAdKeyword) {
      removedElements.push({
        rule: 'ad-text-removal',
        element: el.tagName,
        className: el.className,
        content: el.textContent?.substring(0, 100),
      });
      el.remove();
      removedByText++;
    }
  });
  console.log(`📝 Removed ${removedByText} elements by ad text detection`);

  // Remove empty elements
  console.log('\n🗑️ Removing empty elements...');
  const allElements = cloned.querySelectorAll('*');
  let removedEmpty = 0;

  for (let i = allElements.length - 1; i >= 0; i--) {
    const el = allElements[i];
    const text = el.textContent?.trim() || '';
    const hasVisibleChildren = el.querySelector('img, video, audio, canvas, svg, iframe');

    if (text.length === 0 && !hasVisibleChildren) {
      removedEmpty++;
      el.remove();
    }
  }
  console.log(`📝 Removed ${removedEmpty} empty elements`);

  console.log(`\n📊 Total removed elements: ${removedElements.length}`);
  console.log(`📏 Content length after cleaning: ${cloned.textContent?.length || 0} chars`);

  return { cleanedElement: cloned, removedElements };
}

// Analyze what content remains after cleaning
function analyzeRemainingContent(cleanedElement) {
  console.log('\n🔍 Analyzing remaining content...');

  const text = cleanedElement.textContent?.trim() || '';
  const textLength = text.length;

  // Check what types of elements remain
  const remainingElements = {
    paragraphs: cleanedElement.querySelectorAll('p').length,
    headings: cleanedElement.querySelectorAll('h1, h2, h3, h4, h5, h6').length,
    lists: cleanedElement.querySelectorAll('ul, ol').length,
    figures: cleanedElement.querySelectorAll('figure, figcaption').length,
    divs: cleanedElement.querySelectorAll('div').length,
    spans: cleanedElement.querySelectorAll('span').length,
  };

  console.log('📊 Remaining elements:', remainingElements);

  // Check for key article content
  const hasMainContent = text.toLowerCase().includes('project vend');
  const hasIntroduction = text
    .toLowerCase()
    .includes('why did you have an llm run a small business');
  const hasPerformanceReview = text.toLowerCase().includes("claude's performance review");
  const hasFigures =
    text.toLowerCase().includes('figure 1') || text.toLowerCase().includes('figure 2');
  const hasFootnotes = text.toLowerCase().includes('footnotes') || text.match(/\d+\.\s*[""]/);

  console.log('\n📝 Content analysis:');
  console.log(`   Text length: ${textLength} chars`);
  console.log(`   Contains main article content: ${hasMainContent}`);
  console.log(`   Contains introduction: ${hasIntroduction}`);
  console.log(`   Contains performance review: ${hasPerformanceReview}`);
  console.log(`   Contains figures: ${hasFigures}`);
  console.log(`   Contains footnotes: ${hasFootnotes}`);

  if (hasFigures && hasFootnotes && !hasMainContent) {
    console.log('🚨 WARNING: Only figures and footnotes remain - main content was removed!');
  }

  return {
    textLength,
    hasMainContent,
    hasIntroduction,
    hasPerformanceReview,
    hasFigures,
    hasFootnotes,
    remainingElements,
  };
}

// Check what specific elements contain the main content
function findMainContentElements(originalElement) {
  console.log('\n🎯 Analyzing which elements contain main article content...');

  const keyPhrases = [
    'why did you have an llm run a small business',
    'claude manage an automated store',
    'we learned a lot from this experiment',
    'claude performed surprisingly well',
    'project vend demonstrates',
  ];

  const allElements = originalElement.querySelectorAll('*');
  const contentElements = [];

  allElements.forEach(el => {
    const text = el.textContent?.toLowerCase() || '';
    const matchedPhrases = keyPhrases.filter(phrase => text.includes(phrase));

    if (matchedPhrases.length > 0) {
      contentElements.push({
        element: el,
        tagName: el.tagName,
        className: el.className,
        id: el.id,
        matchedPhrases,
        textLength: text.length,
        selector: getElementSelector(el),
      });
    }
  });

  // Sort by most matched phrases and content length
  contentElements.sort((a, b) => {
    if (b.matchedPhrases.length !== a.matchedPhrases.length) {
      return b.matchedPhrases.length - a.matchedPhrases.length;
    }
    return b.textLength - a.textLength;
  });

  console.log(`📊 Found ${contentElements.length} elements with main content:`);
  contentElements.slice(0, 5).forEach((item, index) => {
    console.log(`   ${index + 1}. ${item.tagName}.${item.className || 'no-class'}`);
    console.log(`      Selector: ${item.selector}`);
    console.log(`      Matched phrases: ${item.matchedPhrases.length}`);
    console.log(`      Text length: ${item.textLength} chars`);
    console.log('      ---');
  });

  return contentElements;
}

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

// Main diagnostic process
console.log('🚀 Starting content cleaning diagnostic...\n');

const originalElement = getMainArticleElement();
if (!originalElement) {
  console.log('❌ Could not find main article element');
} else {
  // Analyze original content structure
  const mainContentElements = findMainContentElements(originalElement);

  // Simulate cleaning process
  const { cleanedElement, removedElements } = simulateContentCleaning(originalElement);

  // Analyze what remains
  const remainingAnalysis = analyzeRemainingContent(cleanedElement);

  // Final summary
  console.log('\n📋 CLEANING DIAGNOSTIC SUMMARY');
  console.log('===============================');
  console.log(`🔍 Original content: ${originalElement.textContent?.length || 0} chars`);
  console.log(`🧹 After cleaning: ${remainingAnalysis.textLength} chars`);
  console.log(
    `📉 Content reduction: ${((1 - remainingAnalysis.textLength / (originalElement.textContent?.length || 1)) * 100).toFixed(1)}%`
  );
  console.log(`🎯 Main content preserved: ${remainingAnalysis.hasMainContent}`);
  console.log(`🏷️ Total elements removed: ${removedElements.length}`);

  if (!remainingAnalysis.hasMainContent) {
    console.log('\n🔧 PROBLEM IDENTIFIED:');
    console.log('The content cleaning process is removing the main article content!');
    console.log('This explains why only figure captions and footnotes remain.');

    console.log('\n💡 LIKELY CAUSES:');
    console.log('1. Main content elements have classes that match cleaning rules');
    console.log('2. Content structure is being misidentified as navigation/metadata');
    console.log('3. Empty element removal is too aggressive');

    // Show which elements were removed that might contain main content
    const suspiciousRemovals = removedElements.filter(
      item =>
        item.content &&
        item.content.length > 100 &&
        (item.content.includes('claude') ||
          item.content.includes('project') ||
          item.content.includes('vend'))
    );

    if (suspiciousRemovals.length > 0) {
      console.log('\n🚨 SUSPICIOUS REMOVALS (might contain main content):');
      suspiciousRemovals.forEach(item => {
        console.log(`   Rule: ${item.rule}`);
        console.log(`   Element: ${item.element}.${item.className || 'no-class'}`);
        console.log(`   Content: "${item.content}..."`);
        console.log('   ---');
      });
    }
  }
}

console.log('\n✨ Content cleaning diagnostic completed!');
