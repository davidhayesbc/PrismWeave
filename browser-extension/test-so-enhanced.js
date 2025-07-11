// Improved Stack Overflow blog extraction test
// Run this in browser console on stackoverflow.blog pages

console.log('🔍 Testing Enhanced Stack Overflow Blog Extractor...');

if (!window.location.href.includes('stackoverflow.blog')) {
  console.error('❌ This test should be run on a stackoverflow.blog page');
  console.log('Navigate to: https://stackoverflow.blog/2025/06/30/reliability-for-unreliable-llms');
} else {
  console.log('✅ Detected Stack Overflow blog page');

  // Test the actual DOM structure this page uses
  console.log('\n🔍 Analyzing Stack Overflow blog DOM structure...');

  // Check what content containers exist
  const contentContainers = [
    'article',
    'main',
    '[role="main"]',
    '.content',
    '.post-content',
    '.entry-content',
    '.article-body',
  ];

  contentContainers.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    console.log(`📦 ${selector}: ${elements.length} element(s)`);
    if (elements.length > 0) {
      const firstEl = elements[0];
      const textLength = firstEl.textContent?.length || 0;
      const childCount = firstEl.children.length;
      console.log(`   First element: ${textLength} chars, ${childCount} children`);
    }
  });

  // Check section structure (h2, h3 sections)
  const headers = document.querySelectorAll('h1, h2, h3');
  console.log(`\n📝 Found ${headers.length} headers:`);
  headers.forEach((header, index) => {
    if (index < 8) {
      // Show first 8 headers
      const level = header.tagName;
      const text = header.textContent?.substring(0, 50) || '';
      console.log(`   ${level}: "${text}${text.length === 50 ? '...' : ''}"`);
    }
  });

  // Test paragraph structure
  const paragraphs = document.querySelectorAll('p');
  console.log(`\n📄 Found ${paragraphs.length} paragraph elements`);

  let substantialParagraphs = 0;
  paragraphs.forEach((p, index) => {
    const text = p.textContent?.trim() || '';
    if (text.length > 30) {
      substantialParagraphs++;
      if (index < 5) {
        console.log(`   P${index + 1}: "${text.substring(0, 80)}..."`);
      }
    }
  });
  console.log(`✅ ${substantialParagraphs} substantial paragraphs found`);

  // Test if our extractor logic would work
  console.log('\n🧪 Testing extractor logic...');

  // Simulate article content extraction
  const articles = document.querySelectorAll('article');
  if (articles.length > 0) {
    const article = articles[0];
    const clone = article.cloneNode(true);

    // Remove unwanted elements (simulate our cleaner)
    const unwantedSelectors = [
      'nav',
      'header',
      'footer',
      'aside',
      '.nav',
      '.navigation',
      '.menu',
      '.sidebar',
      '.promo',
      '.promotion',
      '.advertisement',
      '.ad',
      '.social',
      '.share',
      '.sharing',
      '.comments',
      '.comment-form',
      '.related',
      '.related-posts',
      'script',
      'style',
      'noscript',
      '[class*="teams"]',
      '[class*="talent"]',
      '[class*="hiring"]',
      '[class*="subscribe"]',
      '[class*="newsletter"]',
      '[class*="products"]',
    ];

    unwantedSelectors.forEach(selector => {
      try {
        const elements = clone.querySelectorAll(selector);
        elements.forEach(el => el.remove());
        if (elements.length > 0) {
          console.log(`   🗑️ Removed ${elements.length} ${selector} elements`);
        }
      } catch (e) {
        // Invalid selector, skip
      }
    });

    const cleanedHtml = clone.innerHTML;
    const cleanedText = clone.textContent?.trim() || '';

    console.log(`📊 After cleaning: ${cleanedText.length} chars, ${cleanedHtml.length} HTML chars`);

    // Count remaining paragraphs
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = cleanedHtml;
    const remainingPs = tempDiv.querySelectorAll('p');
    console.log(`📄 Remaining paragraphs after cleaning: ${remainingPs.length}`);

    // Test markdown conversion if TurndownService is available
    if (typeof TurndownService !== 'undefined') {
      console.log('\n🔄 Testing markdown conversion...');
      const turndownService = new TurndownService({
        headingStyle: 'atx',
        bulletListMarker: '-',
        codeBlockStyle: 'fenced',
      });

      try {
        const markdown = turndownService.turndown(cleanedHtml);
        const paragraphBreaks = (markdown.match(/\n\n/g) || []).length;
        console.log(`📝 Markdown: ${markdown.length} chars, ${paragraphBreaks} paragraph breaks`);

        if (paragraphBreaks >= 3) {
          console.log('✅ Good paragraph structure in markdown!');
        } else {
          console.warn('⚠️ Few paragraph breaks detected');
        }

        // Show a sample
        console.log('📖 Markdown sample (first 400 chars):');
        console.log(markdown.substring(0, 400) + '...');
      } catch (error) {
        console.error('❌ Markdown conversion failed:', error);
      }
    } else {
      console.log('📦 TurndownService not available - load it to test conversion');
    }
  }

  // Test promotional content detection
  console.log('\n🚨 Testing promotional content detection...');
  const bodyText = document.body.textContent?.toLowerCase() || '';
  const promoIndicators = [
    'stack overflow for teams',
    'hire top talent',
    'subscribe to',
    'newsletter',
    'products',
    'pricing',
  ];

  const foundPromo = promoIndicators.filter(indicator => bodyText.includes(indicator));
  console.log(`🔍 Found promotional terms: ${foundPromo.join(', ')}`);

  // Final test instructions
  console.log('\n🎯 Next steps for testing:');
  console.log('1. Load the PrismWeave extension');
  console.log('2. Press Ctrl+Alt+S to capture this page');
  console.log('3. Check the captured markdown for:');
  console.log('   ✅ Proper headers (## sections)');
  console.log('   ✅ Paragraph breaks between content');
  console.log('   ✅ No promotional "teams" content');
  console.log('   ✅ Clean, readable structure');
}

console.log('\n✨ Enhanced test completed');
