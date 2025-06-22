// PrismWeave Docker Blog Content Analysis Script
// Run this in the browser console on the Docker blog page to analyze content structure

(function () {
  'use strict';

  console.log('🐳 PrismWeave Docker Blog Content Analysis Starting...');
  console.log('📍 URL:', window.location.href);
  console.log('📄 Title:', document.title);

  // Test all common content selectors
  const selectors = [
    'article',
    'main',
    '[role="main"]',
    '.content',
    '.post-content',
    '.entry-content',
    '.article-content',
    '.article-body',
    '.post-body',
    '.entry-body',
    '.content-body',
    '.main-content',
    '.article-text',
    '.story-body',
    '.article-wrapper',
    '.post-text',
    '.content-area',
    '.entry-text',
    '.blog-content',
    '.prose',
    '.rich-text',
    // Potential Docker-specific selectors
    '[class*="content"]',
    '[class*="article"]',
    '[class*="post"]',
    '[class*="blog"]',
    '[id*="content"]',
    '[id*="article"]',
    '[id*="post"]',
  ];

  console.log('🔍 Testing selectors...');

  let bestSelector = null;
  let bestElement = null;
  let bestScore = 0;

  selectors.forEach(selector => {
    try {
      const elements = document.querySelectorAll(selector);
      console.log(`📋 Selector "${selector}": ${elements.length} elements`);

      elements.forEach((element, index) => {
        const textContent = element.textContent?.trim() || '';
        const innerHTML = element.innerHTML || '';
        const textLength = textContent.length;
        const htmlLength = innerHTML.length;
        const ratio = textLength / htmlLength;

        const paragraphs = element.querySelectorAll('p').length;
        const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6').length;
        const links = element.querySelectorAll('a').length;

        // Calculate a content score
        let score = 0;
        score += Math.min(textLength / 10, 500); // Base score from text length
        score += paragraphs * 25; // Bonus for paragraphs
        score += headings * 30; // Bonus for headings
        if (links > paragraphs * 2) score -= links * 10; // Penalty for too many links

        console.log(`  📄 Element ${index + 1}:`, {
          textLength,
          htmlLength,
          ratio: ratio.toFixed(3),
          paragraphs,
          headings,
          links,
          score: Math.round(score),
          tagName: element.tagName,
          className:
            element.className.substring(0, 50) + (element.className.length > 50 ? '...' : ''),
          id: element.id,
        });

        if (score > bestScore && textLength > 1000) {
          bestScore = score;
          bestElement = element;
          bestSelector = selector;
        }
      });
    } catch (error) {
      console.warn(`❌ Error with selector "${selector}":`, error.message);
    }
  });

  console.log('🏆 Best content element found:');
  if (bestElement) {
    console.log('  📋 Selector:', bestSelector);
    console.log('  🏅 Score:', Math.round(bestScore));
    console.log('  📏 Text length:', bestElement.textContent?.length || 0);
    console.log('  🏷️ Tag:', bestElement.tagName);
    console.log('  🎨 Class:', bestElement.className);
    console.log('  🆔 ID:', bestElement.id);
    console.log('  📄 Element:', bestElement);

    // Test content extraction
    console.log('🧪 Testing content extraction...');
    const cloned = bestElement.cloneNode(true);

    // Remove unwanted elements
    const unwanted = cloned.querySelectorAll(
      'script, style, noscript, .ad, .ads, .banner, nav, header, footer, aside, .sidebar, .social-share, .share-buttons'
    );
    console.log('🗑️ Removing', unwanted.length, 'unwanted elements');
    unwanted.forEach(el => el.remove());

    const finalContent = cloned.innerHTML;
    const finalText = cloned.textContent?.trim() || '';

    console.log('✅ Final extracted content:');
    console.log('  📏 HTML length:', finalContent.length);
    console.log('  📝 Text length:', finalText.length);
    console.log('  📊 Word count:', finalText.split(/\s+/).filter(w => w.length > 0).length);

    // Show a preview of the content
    const preview = finalText.substring(0, 200) + (finalText.length > 200 ? '...' : '');
    console.log('  👁️ Preview:', preview);

    // Store results globally for further inspection
    window.prismweaveDebug = {
      bestElement,
      bestSelector,
      bestScore,
      finalContent,
      finalText,
      extractedHtml: finalContent,
    };

    console.log('💾 Results stored in window.prismweaveDebug for inspection');
  } else {
    console.log('❌ No suitable content element found');
  }

  console.log('🏁 Analysis complete!');
})();
